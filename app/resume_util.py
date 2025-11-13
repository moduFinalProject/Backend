from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload, contains_eager
from app.models import Code, Resume, File


async def get_resume_response(db: AsyncSession, resume_id: int):
    """이력서 상세 조회용 함수 - ResumeResponse 형태의 딕셔너리 반환"""

    ResumetypeCode = aliased(Code)
    GenderCode = aliased(Code)
    MilitaryServiceCode = aliased(Code)
    ImageFile = aliased(File)

    stmt = (
        select(
            Resume,
            GenderCode.code_detail.label("gender_detail"),
            ResumetypeCode.code_detail.label("resume_type_detail"),
            MilitaryServiceCode.code_detail.label("military_service_detail"),
            ImageFile.file_key.label("image_key"),
        )
        .outerjoin(
            GenderCode,
            (GenderCode.division == "gender") & (GenderCode.detail_id == Resume.gender),
        )
        .outerjoin(
            ResumetypeCode,
            (ResumetypeCode.division == "resume_type")
            & (ResumetypeCode.detail_id == Resume.resume_type),
        )
        .outerjoin(
            MilitaryServiceCode,
            (MilitaryServiceCode.division == "military")
            & (MilitaryServiceCode.detail_id == Resume.military_service),
        )
        .outerjoin(
            ImageFile,
            (ImageFile.fileable_id == Resume.resume_id)
            & (ImageFile.fileable_table == "resumes")
            & (ImageFile.purpose == "resume_image"),
        )
        .outerjoin(Resume.experiences)
        .outerjoin(Resume.educations)
        .outerjoin(Resume.projects)
        .outerjoin(Resume.activities)
        .outerjoin(Resume.technology_stacks)
        .outerjoin(Resume.qualifications)
        .options(
            contains_eager(Resume.experiences),
            contains_eager(Resume.educations),
            contains_eager(Resume.projects),
            contains_eager(Resume.activities),
            contains_eager(Resume.technology_stacks),
            contains_eager(Resume.qualifications),
        )
        .where(and_(Resume.resume_id == resume_id, Resume.is_active == True))
    )

    result = await db.execute(stmt)
    row = result.unique().first()

    if row is None:
        return None

    # 튜플에서 각 요소 추출
    resume, gender_detail, resume_type_detail, military_service_detail, image_key = row

    # ResumeResponse 형태의 딕셔너리로 변환
    resume_dict = {
        "resume_id": resume.resume_id,
        "title": resume.title,
        "name": resume.name,
        "email": resume.email,
        "gender": resume.gender,
        "gender_detail": gender_detail,
        "address": resume.address,
        "phone": resume.phone,
        "military_service": resume.military_service,
        "military_service_detail": military_service_detail,
        "birth_date": resume.birth_date,
        "self_introduction": resume.self_introduction,
        "experiences": resume.experiences,
        "educations": resume.educations,
        "projects": resume.projects,
        "activities": resume.activities,
        "technology_stacks": resume.technology_stacks,
        "qualifications": resume.qualifications,
        "resume_type": resume.resume_type,
        "resume_type_detail": resume_type_detail,
        "created_at": resume.created_at,
        "updated_at": resume.updated_at,
        "image_key": image_key,  # presigned_url 생성에 필요
    }

    return resume_dict
