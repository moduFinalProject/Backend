from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload, contains_eager
from app.models import Code, Resume, File


async def get_resume_response(db: AsyncSession, resume_id: int):
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
            (MilitaryServiceCode.division == "military_service")
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

    resume = await db.execute(stmt)

    resume = resume.unique().first()

    return resume
