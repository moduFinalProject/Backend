"""게스트(체험) 계정 생성, 샘플 데이터 입력, 만료된 게스트 정리."""
import io
import logging
import secrets
from datetime import date, datetime, timedelta, timezone

from botocore.exceptions import ClientError
from PIL import Image, ImageDraw
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.models.models import (
    Activity,
    Conversation,
    Education,
    Experience,
    FeedbackContent,
    File as FileModel,
    Interview,
    InterviewFeedback,
    JobPosting,
    Project,
    Qualification,
    Resume,
    ResumeFeedback,
    StudyGuide,
    StudyItem,
    StudyKeyword,
    TechnologyStack,
    User,
)
from app.service.login_service import create_user
from app.storage_util import storage_util

logger = logging.getLogger(__name__)

GUEST_PROVIDER = "guest"
GUEST_EMAIL_DOMAIN = "gaechwi.demo"
GUEST_TTL_HOURS = 24  # 이 시간이 지난 게스트 계정은 삭제
MAX_GUESTS = 100  # 동시에 존재할 수 있는 게스트 계정 수 (남용 방지)
PLACEHOLDER_KEY = f"{settings.image}/guest-sample.png"


class GuestLimitExceeded(Exception):
    pass


# ---------------------------------------------------------------------------
# 기본 프로필 이미지
# ---------------------------------------------------------------------------
def _make_placeholder_png() -> bytes:
    img = Image.new("RGB", (300, 400), (226, 232, 240))
    draw = ImageDraw.Draw(img)
    draw.ellipse((100, 90, 200, 190), fill=(148, 163, 184))
    draw.ellipse((40, 220, 260, 460), fill=(148, 163, 184))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def _ensure_placeholder_image() -> None:
    """기본 이미지가 버킷에 없으면 만들어서 올린다."""
    client = storage_util.s3_client
    try:
        client.head_object(Bucket=settings.aws_bucket_name, Key=PLACEHOLDER_KEY)
    except ClientError as e:
        code = str(e.response.get("Error", {}).get("Code"))
        if code not in ("404", "NoSuchKey", "NotFound"):
            raise
        client.upload_fileobj(
            io.BytesIO(_make_placeholder_png()),
            settings.aws_bucket_name,
            PLACEHOLDER_KEY,
            ExtraArgs={"ContentType": "image/png"},
        )


async def _attach_photo(db: AsyncSession, user: User, resume: Resume) -> None:
    """기본 이미지를 복사해서 이력서에 연결한다. 실패해도 게스트 생성은 계속한다."""
    try:
        _ensure_placeholder_image()
        copied = await storage_util.copy_image(PLACEHOLDER_KEY, "png")
        db.add(
            FileModel(
                fileable_id=resume.resume_id,
                user_id=user.user_id,
                filetype="png",
                fileable_table="resumes",
                org_file_name="sample.png",
                mod_file_name=copied["unique_filename"],
                file_key=copied["new_image_key"],
                purpose="resume_image",
            )
        )
    except Exception as e:  # 버킷 설정 문제 등
        logger.warning(f"게스트 샘플 사진 연결 실패: {e}")


# ---------------------------------------------------------------------------
# 샘플 데이터
# ---------------------------------------------------------------------------
async def _add_sample_data(db: AsyncSession, user: User) -> None:
    postings = [
        JobPosting(
            user_id=user.user_id,
            title="[샘플] 백엔드 개발자",
            company="네오테크",
            url="https://example.com/jobs/neotech-backend",
            qualification="Python 또는 Java 실무 경험 2년 이상, REST API 설계 및 RDBMS 활용 경험",
            prefer="FastAPI 또는 Spring 경험, Docker 및 클라우드 배포 경험, 테스트 코드 작성 경험",
            end_date=date(2026, 12, 31),
        ),
        JobPosting(
            user_id=user.user_id,
            title="[샘플] 프론트엔드 개발자",
            company="블루웨이브",
            url="https://example.com/jobs/bluewave-frontend",
            qualification="React 및 TypeScript 프로젝트 경험, 반응형 웹 구현 경험",
            prefer="상태관리 라이브러리 경험, 웹 접근성 및 성능 최적화 경험",
            end_date=date(2026, 12, 20),
        ),
        JobPosting(
            user_id=user.user_id,
            title="[샘플] 풀스택 개발자",
            company="스타트랩",
            url="https://example.com/jobs/startlab-fullstack",
            qualification="웹 서비스 개발 경험, 프론트와 백엔드 협업 경험",
            prefer="AI API 연동 경험, 소규모 팀 프로젝트 리딩 경험",
            end_date=date(2027, 1, 15),
        ),
    ]
    db.add_all(postings)
    await db.flush()

    common = dict(
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        address=user.address,
        gender=user.gender,
        phone=user.phone,
        military_service=user.military_service,
        birth_date=user.birth_date,
    )
    resume1 = Resume(
        title="[샘플] 개발자 기본 이력서",
        resume_type="1",
        self_introduction=(
            "문제를 끝까지 파고들어 원인을 찾는 것을 좋아하는 개발자입니다. "
            "팀 프로젝트에서 백엔드 API와 배포 환경을 맡아 서비스를 직접 운영해 본 경험이 있습니다. "
            "새로운 기술도 공식 문서를 읽고 작은 프로젝트로 검증하며 익힙니다."
        ),
        **common,
    )
    resume2 = Resume(
        posting_id=postings[0].posting_id,
        title="[샘플] 네오테크 지원용",
        resume_type="2",
        self_introduction=(
            "FastAPI와 PostgreSQL로 AI 기반 취업 준비 서비스를 개발하고 직접 배포까지 운영했습니다. "
            "API 설계, DB 마이그레이션, 컨테이너 배포 경험을 바탕으로 네오테크의 백엔드 팀에 기여하고 싶습니다."
        ),
        **common,
    )
    db.add_all([resume1, resume2])
    await db.flush()

    for resume in (resume1, resume2):
        db.add_all(
            [
                Education(
                    resume_id=resume.resume_id,
                    organ="한국대학교",
                    department="컴퓨터공학과",
                    degree_level="3",
                    score="3.8/4.5",
                    start_date=date(2019, 3, 1),
                    end_date=date(2025, 2, 28),
                ),
                Experience(
                    resume_id=resume.resume_id,
                    job_title="웹 개발 인턴",
                    department="개발팀",
                    position="인턴",
                    job_description="사내 관리자 페이지의 API 개발 및 DB 쿼리 최적화를 담당했습니다.",
                    employment_status=False,
                    start_date=date(2024, 7, 1),
                    end_date=date(2024, 12, 31),
                ),
                Project(
                    resume_id=resume.resume_id,
                    title="AI 기반 취업 준비 플랫폼",
                    start_date=date(2025, 9, 1),
                    end_date=date(2025, 11, 30),
                    description="FastAPI, PostgreSQL, React로 이력서 피드백과 모의면접 기능을 가진 서비스를 개발했습니다.",
                ),
                Project(
                    resume_id=resume.resume_id,
                    title="팀 일정 공유 웹앱",
                    start_date=date(2024, 3, 1),
                    end_date=date(2024, 6, 30),
                    description="React와 Node.js로 팀 일정 공유 및 알림 기능을 구현했습니다.",
                ),
                Activity(
                    resume_id=resume.resume_id,
                    title="교내 개발 동아리 운영진",
                    start_date=date(2022, 3, 1),
                    end_date=date(2023, 12, 31),
                    description="스터디를 기획하고 신입 부원 대상 Git 및 웹 기초 강의를 진행했습니다.",
                ),
                Qualification(
                    resume_id=resume.resume_id,
                    title="정보처리기사",
                    acquisition_date=date(2024, 8, 30),
                    organ="한국산업인력공단",
                ),
                Qualification(
                    resume_id=resume.resume_id,
                    title="OPIc IM2",
                    acquisition_date=date(2024, 5, 20),
                    score="IM2",
                    organ="ACTFL",
                ),
            ]
            + [
                TechnologyStack(resume_id=resume.resume_id, title=t)
                for t in ["Python", "FastAPI", "PostgreSQL", "Docker", "React", "TypeScript"]
            ]
        )
        await _attach_photo(db, user, resume)

    feedback = ResumeFeedback(
        resume_id=resume2.resume_id,
        user_id=user.user_id,
        posting_id=postings[0].posting_id,
        parent_content="네오테크 백엔드 개발자 공고 기준으로 이력서를 분석했습니다.",
        matching_rate=82,
    )
    db.add(feedback)
    await db.flush()
    db.add_all(
        [
            FeedbackContent(
                feedback_id=feedback.feedback_id,
                feedback_devision="1",
                feedback_result="FastAPI와 PostgreSQL 사용 경험이 공고의 우대사항과 정확히 일치하고, 직접 배포까지 운영한 점이 강점입니다.",
            ),
            FeedbackContent(
                feedback_id=feedback.feedback_id,
                feedback_devision="2",
                feedback_result="프로젝트 설명에 본인이 맡은 역할과 구체적인 성과 수치가 부족합니다. 응답 속도 개선 같은 지표를 추가해 보세요.",
            ),
            FeedbackContent(
                feedback_id=feedback.feedback_id,
                feedback_devision="3",
                feedback_result="자기소개서에 지원 동기를 한 문장 더 구체화하면 설득력이 높아집니다.",
            ),
            FeedbackContent(
                feedback_id=feedback.feedback_id,
                feedback_devision="4",
                feedback_result="테스트 코드 작성 경험이 있다면 프로젝트 항목에 함께 적어 두는 것을 권장합니다.",
            ),
        ]
    )

    interview = Interview(
        user_id=user.user_id,
        resume_id=resume2.resume_id,
        posting_id=postings[0].posting_id,
        total_score=78,
        status="2",  # 면접 상태 코드: 2 = 완료
    )
    db.add(interview)
    await db.flush()
    # conversations.created_at 컬럼이 timezone 없는 TIMESTAMP라 naive UTC로 넣음
    naive_now = datetime.now(timezone.utc).replace(tzinfo=None)
    db.add_all(
        [
            Conversation(
                interview_id=interview.interview_id,
                question="진행한 프로젝트에서 가장 어려웠던 기술적 문제와 해결 과정을 설명해 주세요.",
                answer="DB 마이그레이션 순서 충돌로 배포가 실패했고, 마이그레이션 이력을 분석해 해당 단계를 정리한 뒤 재배포했습니다.",
                feedback="문제 원인과 해결 과정이 명확합니다. 재발 방지책도 함께 언급하면 더 좋습니다.",
                sequence=1,
                created_at=naive_now,
            ),
            Conversation(
                interview_id=interview.interview_id,
                question="REST API를 설계할 때 중요하게 생각하는 기준은 무엇인가요?",
                answer="자원 중심의 일관된 URL, 적절한 상태 코드, 그리고 오류 응답 형식의 통일을 중요하게 생각합니다.",
                feedback="핵심은 잘 짚었습니다. 버전 관리나 인증 처리 기준도 덧붙여 보세요.",
                sequence=2,
                created_at=naive_now,
            ),
            InterviewFeedback(
                interview_id=interview.interview_id,
                status="1",
                content="질문의 의도에 맞게 상황과 해결 과정을 순서대로 설명했습니다.",
            ),
            InterviewFeedback(
                interview_id=interview.interview_id,
                status="2",
                content="성과를 수치로 제시하면 답변의 설득력이 높아집니다.",
            ),
            InterviewFeedback(
                interview_id=interview.interview_id,
                status="3",
                content="데이터베이스 인덱스와 트랜잭션 격리 수준을 더 학습해 보세요.",
            ),
        ]
    )

    guide = StudyGuide(
        user_id=user.user_id,
        posting_id=postings[0].posting_id,
        title="네오테크 백엔드 준비",
        description="네오테크 백엔드 개발자 공고에 맞춰 우선순위별로 학습할 내용을 정리했습니다.",
    )
    db.add(guide)
    await db.flush()

    items = [
        ("FastAPI", "FastAPI 의존성 주입과 비동기 처리", "Depends 구조와 async 엔드포인트의 동작 방식을 정리합니다.", 180, "1", ["Depends", "async"]),
        ("PostgreSQL", "인덱스와 쿼리 실행 계획", "EXPLAIN으로 쿼리를 분석하고 인덱스 설계 기준을 익힙니다.", 240, "1", ["인덱스", "EXPLAIN"]),
        ("Docker", "도커 컴포즈로 배포 환경 구성", "서비스 간 네트워크와 환경변수 관리 방법을 복습합니다.", 120, "2", ["Compose", "네트워크"]),
        ("테스트", "pytest로 API 테스트 작성", "TestClient를 사용한 엔드포인트 테스트를 작성해 봅니다.", 150, "3", ["pytest", "TestClient"]),
    ]
    for keyword, title, content, minutes, priority, keywords in items:
        item = StudyItem(
            guide_id=guide.guide_id,
            keyword=keyword,
            title=title,
            content=content,
            estimated_time=minutes,
            priority=priority,
        )
        db.add(item)
        await db.flush()
        db.add_all(
            [StudyKeyword(study_item_id=item.study_item_id, keyword=k) for k in keywords]
        )


# ---------------------------------------------------------------------------
# 공개 함수
# ---------------------------------------------------------------------------
async def cleanup_expired_guests(db: AsyncSession) -> int:
    """GUEST_TTL_HOURS가 지난 게스트 계정과 그 이미지 파일을 삭제한다."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=GUEST_TTL_HOURS)
    result = await db.execute(
        select(User.user_id).where(
            User.provider == GUEST_PROVIDER, User.created_at < cutoff
        )
    )
    user_ids = list(result.scalars().all())
    if not user_ids:
        return 0

    result = await db.execute(
        select(FileModel.file_key).where(FileModel.user_id.in_(user_ids))
    )
    for key in result.scalars().all():
        try:
            await storage_util.delete_from_storage(key)
        except Exception as e:
            logger.warning(f"게스트 파일 삭제 실패({key}): {e}")

    # 하위 데이터는 DB의 ON DELETE CASCADE로 함께 삭제된다.
    await db.execute(delete(User).where(User.user_id.in_(user_ids)))
    await db.commit()
    return len(user_ids)


async def create_guest_user(db: AsyncSession) -> User:
    """새 게스트 계정을 만들고 샘플 데이터를 채운다."""
    count = await db.scalar(
        select(func.count()).select_from(User).where(User.provider == GUEST_PROVIDER)
    )
    if (count or 0) >= MAX_GUESTS:
        raise GuestLimitExceeded()

    suffix = secrets.token_hex(4)
    user = await create_user(
        db=db,
        email=f"guest-{suffix}@{GUEST_EMAIL_DOMAIN}",
        name="게스트",
        birth_date=date(2000, 1, 1),
        gender="1",
        address="서울특별시",
        provider=GUEST_PROVIDER,
        provider_id=suffix,
        phone="010-0000-0000",
        user_type="1",
        military_service="6",
    )

    await _add_sample_data(db, user)
    await db.commit()
    await db.refresh(user)
    return user