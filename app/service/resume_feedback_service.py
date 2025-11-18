from fastapi import HTTPException, status
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import and_, select
from app.config.settings import settings
from app.models.models import (
    Activity,
    Education,
    Experience,
    File,
    JobPosting,
    Project,
    Qualification,
    Resume,
    ResumeFeedback,
    Code,
    TechnologyStack,
)
from app.schema.schemas import (
    FeedbackContentAI,
    ResumeCreate,
    ResumeFeedbackAI,
    ResumeFeedbackResponse,
    ResumeResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload

from app.service.resume_service import get_resume_response
from app.storage_util.storage_util import (
    copy_image,
    generate_presigned_url,
    generate_unique_filename,
)


llm = ChatOpenAI(
    api_key=settings.openai_api_key,
    model=settings.ai_model,
    temperature=settings.temperature,
)


async def resume_standard_feedback(resume: dict) -> ResumeFeedbackAI:
    """일반 이력서 첨삭"""

    prompt = ChatPromptTemplate(
        [
            (
                "system",
                """당신은 전직 한 회사의 인사과 팀장이자 이력서 첨삭 전문가 입니다. 이력서 정보를 받고 회사에 취업할 수 있도록 이력서를 피드백 해주세요, 
                단 사실에 근거해야 합니다. 
                매칭률은 0으로 출력하시오.
                parent_content는 이력서의 내용을 입력받은 이력서의 내용을 마크다운 형식의 text로 빠지는 부분 없이 매우 구체적으로 정리하세요.
                특히 기술스택, 경력, 학력, 자격, 프로젝트, 활동 의 내용을 빠지지 않게 작성하세요.
                피드백 내용은 구체적으로 적어주세요
                feedback_devision은 반드시 다음을 준수하세요 1:잘된 부분, 2:필수 수정 사항,3:개선 제안 사항, 4: 추가 권장사항""",
            ),
            ("user", "{resume}"),
        ]
    )

    chain = prompt | llm.with_structured_output(ResumeFeedbackAI)

    result = chain.invoke({"resume": resume})

    return result


async def resume_feedback_with_posting(resume: dict, posting: dict) -> ResumeFeedbackAI:
    """공고별 이력서 첨삭"""

    prompt = ChatPromptTemplate(
        [
            (
                "system",
                """당신은 전직 {company} 회사의 인사과 팀장이자 이력서 첨삭 전문가 입니다. 이력서와 공고 정보를 받고 해당 회사에 취업할 수 있도록 이력서를 피드백 해주세요,
         단 사실에 근거해야 합니다.
         parent_content는 입력받은 이력서의 내용을 마크다운 형식의 text로 빠지는 부분 없이 매우 구체적으로 정리하세요.
         특히 기술스택, 경력, 학력, 자격, 프로젝트, 활동 의 내용을 빠지지 않게 작성하세요
         피드백 내용은 구체적으로 적어주세요,
         feedback_devision은 반드시 다음을 준수하세요 1:잘된 부분, 2:필수 수정 사항,3:개선 제안 사항, 4: 추가 권장사항""",
            ),
            ("user", "{resume}, {posting}"),
        ]
    )

    chain = prompt | llm.with_structured_output(ResumeFeedbackAI)

    result = chain.invoke(
        {"company": posting.get("company"), "resume": resume, "posting": posting}
    )

    return result


async def get_resume_feedback(
    feedback_id: int, db: AsyncSession
) -> ResumeFeedbackResponse:
    """피드백정보 불러오는 함수 - ResumeFeedbackResponse 형태로 반환"""

    data_stmt = (
        select(ResumeFeedback)
        .options(joinedload(ResumeFeedback.feedback_contents))
        .where(ResumeFeedback.feedback_id == feedback_id)
    )

    feedback = await db.execute(data_stmt)
    feedback = feedback.unique().scalar_one_or_none()

    if feedback is None:
        return None
    
    

    feedback_divisions = [
        content.feedback_devision
        for content in feedback.feedback_contents
        if content.feedback_devision
    ]

    feedback_code_map = {}
    if feedback_divisions:
        code_stmt = select(Code).where(
            and_(
                Code.division == "feedback_division",
                Code.detail_id.in_(feedback_divisions),
            )
        )
        code_result = await db.execute(code_stmt)
        codes = code_result.scalars().all()
        feedback_code_map = {code.detail_id: code.code_detail for code in codes}

    for content in feedback.feedback_contents:
        content.feedback_devision_detail = feedback_code_map.get(
            content.feedback_devision
        )
    

    result = ResumeFeedbackResponse.from_orm(feedback)

    return result


async def create_resume_by_feedback(resume: dict, feedback: dict) -> ResumeCreate:
    """일반 첨삭 이력서 생성"""

    prompt = ChatPromptTemplate(
        [
            (
                "system",
                "당신은 전직 한 회사의 인사과 팀장이자 이력서 첨삭 전문가 입니다. 이력서와 피드백 정보를 받고 피드백내용에 기반하여 이력서를 수정해 주세요,특히 자기소개서 부분을 이력서에 가장 잘 어울리게 첨삭 해주세요. , 단 사실에 근거해야 합니다.resume_type은 문자열'3'으로 적용시키세요,",
            ),
            ("user", "{resume},{feedback}"),
        ]
    )

    chain = prompt | llm.with_structured_output(ResumeCreate)

    result = chain.invoke({"resume": resume, "feedback": feedback})

    return result


async def create_posting_resume_by_feedback(
    resume: dict, feedback: dict, posting: dict
) -> ResumeCreate:
    """공고별 첨삭 이력서 생성"""

    prompt = ChatPromptTemplate(
        [
            (
                "system",
                "당신은 전직 {company} 회사의 인사과 팀장이자 이력서 첨삭 전문가 입니다. 이력서와 피드백 정보, 공고 정보를 받고 피드백내용에 기반하여 이력서를 수정해 주세요, 특히 자기소개서 부분을 이력서에 가장 잘 어울리게 첨삭 해주세요. , 단 사실에 근거해야 합니다.resume_type은 문자열'2'로 적용시키세요",
            ),
            ("user", "{resume},{feedback}, {posting}"),
        ]
    )

    chain = prompt | llm.with_structured_output(ResumeCreate)

    result = chain.invoke(
        {
            "company": posting.get("company"),
            "resume": resume,
            "feedback": feedback,
            "posting": posting,
        }
    )

    return result


async def create_resume_with_feedback(
    result: ResumeCreate, db: AsyncSession, user_id: int, parent_resume_id: int
) -> ResumeResponse:
    """피드백을 기반으로 생성된 이력서를 저장 후 출력하는 함수"""

    new_resume = Resume(
        user_id=user_id,
        resume_type=result.resume_type,
        title=result.title,
        name=result.name,
        email=result.email,
        gender=result.gender,
        address=result.address,
        phone=result.phone,
        military_service=result.military_service,
        birth_date=result.birth_date,
        self_introduction=result.self_introduction,
    )
    db.add(new_resume)
    await db.flush()
    await db.refresh(new_resume)

    for technology_stack in result.technology_stacks:
        new_tech = TechnologyStack(
            resume_id=new_resume.resume_id, title=technology_stack.title
        )
        db.add(new_tech)

    for experience in result.experiences:
        new_experience = Experience(
            resume_id=new_resume.resume_id, **experience.model_dump()
        )
        db.add(new_experience)

    for education in result.educations:
        new_education = Education(
            resume_id=new_resume.resume_id, **education.model_dump()
        )
        db.add(new_education)

    for project in result.projects:
        new_project = Project(resume_id=new_resume.resume_id, **project.model_dump())
        db.add(new_project)

    for activity in result.activities:
        new_activity = Activity(resume_id=new_resume.resume_id, **activity.model_dump())
        db.add(new_activity)

    for qualification in result.qualifications:
        new_qualification = Qualification(
            resume_id=new_resume.resume_id, **qualification.model_dump()
        )
        db.add(new_qualification)

    image_file = await db.execute(
        select(File).where(
            and_(File.fileable_id == parent_resume_id, File.purpose == "resume_image")
        )
    )
    image_file = image_file.scalar_one_or_none()

    if image_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="파일을 찾을 수 없습니다."
        )

    new_image = await copy_image(
        key=image_file.file_key, real_format=image_file.filetype
    )

    new_file = File(
        fileable_id=new_resume.resume_id,
        user_id=user_id,
        filetype=image_file.filetype,
        fileable_table="resumes",
        org_file_name=image_file.org_file_name,
        mod_file_name=new_image.get("unique_filename"),
        file_key=new_image.get("new_image_key"),
        purpose="resume_image",
    )

    db.add(new_file)

    await db.commit()

    resume_info = await get_resume_response(db=db, resume_id=new_resume.resume_id)

    image_key = resume_info.get("image_key") if resume_info else None
    image_url = await generate_presigned_url(image_key) if image_key else None

    resume_info["image_url"] = image_url

    resume_response = ResumeResponse.model_validate(resume_info).model_dump()

    return resume_response
