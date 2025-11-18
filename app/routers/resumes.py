from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import json
import logging
import traceback
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import and_, delete, desc, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.models import (
    Activity,
    Code,
    Education,
    Experience,
    JobPosting,
    Project,
    Qualification,
    Resume,
    TechnologyStack,
    User,
)
from app.models.models import File as FileModel
from app.service.resume_service import get_resume_response
from app.schema.schemas import (
    ResumeCreate,
    ResumeListResponse,
    ResumeResponse,
    ResumeUpdate,
)
from app.security import get_current_user
from app.storage_util.storage_util import (
    delete_from_storage,
    generate_presigned_url,
    generate_unique_filename,
    upload_to_image,
    validate_image_file,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.get("/", response_model=List[ResumeListResponse])
async def get_all_resumes(
    title: Optional[str] = None,
    page: int = 1,
    page_size: int = 6,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """현재 사용자의 모든 이력서 목록 조회(검색)"""

    offset = (page - 1) * page_size

    title = title.strip() if title else None

    if not title:
        result = await db.execute(
            select(
                Resume.resume_id,
                Resume.title,
                Resume.created_at,
                Resume.resume_type,
                Code.code_detail.label("resume_type_detail"),
                JobPosting.url,
                JobPosting.end_date,
            )
            .outerjoin(
                Code,
                (Code.division == "resume_type")
                & (Code.detail_id == Resume.resume_type),
            )
            .outerjoin(
                JobPosting,
                (JobPosting.posting_id == Resume.posting_id)
                & (JobPosting.is_active == True),
            )
            .where(
                and_(Resume.user_id == current_user.user_id, Resume.is_active == True)
            )
            .order_by(desc(Resume.created_at))
            .offset(offset)
            .limit(page_size)
        )

    else:
        result = await db.execute(
            select(
                Resume.resume_id,
                Resume.title,
                Resume.created_at,
                Resume.resume_type,
                Code.code_detail.label("resume_type_detail"),
                JobPosting.url,
                JobPosting.end_date,
            )
            .outerjoin(
                Code,
                (Code.division == "resume_type")
                & (Code.detail_id == Resume.resume_type),
            )
            .outerjoin(
                JobPosting,
                (JobPosting.posting_id == Resume.posting_id)
                & (JobPosting.is_active == True),
            )
            .where(
                and_(
                    Resume.user_id == current_user.user_id,
                    Resume.is_active == True,
                    Resume.title.ilike(f"%{title}%"),
                )
            )
            .order_by(desc(Resume.created_at))
            .offset(offset)
            .limit(page_size)
        )

    rows = result.all()
    return [row._asdict() for row in rows]


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """특정 이력서 상세 조회"""

    try:
        resume = await db.get(Resume, resume_id)

        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 이력서 입니다.",
            )

        if resume.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 접근입니다."
            )

        result = await get_resume_response(db=db, resume_id=resume_id)

        image_url = await generate_presigned_url(result.get("image_key"))

        db_resume = ResumeResponse.model_validate(result).model_dump()

        db_resume["image_url"] = image_url

        return db_resume

    except Exception as e:
        logger.error(f"error : {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이력서 조회에 실패했습니다.",
        )


# ============ 기존 엔드포인트 (디버깅 중) ============
# @router.post("", response_model=ResumeResponse)
# async def create_resumes(
#     data: str = Form(...),
#     photo: UploadFile = File(None),
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """일반 이력서 생성"""
#
#     try:
#         resume_data = ResumeCreate(**json.loads(data))
#
#         new_resume = Resume(
#             user_id=current_user.user_id,
#             resume_type=resume_data.resume_type,
#             title=resume_data.title,
#             name=resume_data.name,
#             email=resume_data.email,
#             gender=resume_data.gender,
#             address=resume_data.address,
#             phone=resume_data.phone,
#             military_service=resume_data.military_service,
#             birth_date=resume_data.birth_date,
#             self_introduction=resume_data.self_introduction,
#         )
#         db.add(new_resume)
#         await db.flush()
#         await db.refresh(new_resume)
#
#         for technology_stack in resume_data.technology_stacks:
#             new_tech = TechnologyStack(
#                 resume_id=new_resume.resume_id, title=technology_stack.title
#             )
#             db.add(new_tech)
#
#         for experience in resume_data.experiences:
#             new_experience = Experience(
#                 resume_id=new_resume.resume_id, **experience.model_dump()
#             )
#             db.add(new_experience)
#
#         for education in resume_data.educations:
#             new_education = Education(
#                 resume_id=new_resume.resume_id, **education.model_dump()
#             )
#             db.add(new_education)
#
#         for project in resume_data.projects:
#             new_project = Project(
#                 resume_id=new_resume.resume_id, **project.model_dump()
#             )
#             db.add(new_project)
#
#         for activity in resume_data.activities:
#             new_activity = Activity(
#                 resume_id=new_resume.resume_id, **activity.model_dump()
#             )
#             db.add(new_activity)
#
#         for qualification in resume_data.qualifications:
#             new_qualification = Qualification(
#                 resume_id=new_resume.resume_id, **qualification.model_dump()
#             )
#             db.add(new_qualification)
#
#         if photo:
#             validated: dict = await validate_image_file(photo)
#
#             upload_image = await upload_to_image(file=validated)
#
#             new_image_file = FileModel(
#                 fileable_id=new_resume.resume_id,
#                 user_id=current_user.user_id,
#                 filetype=validated.get("real_format"),
#                 fileable_table="resumes",
#                 org_file_name=validated.get("filename"),
#                 mod_file_name=upload_image.get("unique_filename"),
#                 file_key=upload_image.get("temp_key"),
#                 purpose="resume_image",
#             )
#             db.add(new_image_file)
#         await db.commit()
#
#         resume_info = await get_resume_response(db=db, resume_id=new_resume.resume_id)
#
#         image_key = resume_info.get("image_key") if resume_info else None
#         image_url = await generate_presigned_url(image_key) if image_key else None
#
#         resume_info["image_url"] = image_url
#
#         resume_response = ResumeResponse.model_validate(resume_info).model_dump()
#
#         return resume_response
#
#     except Exception as e:
#
#         await db.rollback()
#         print(f"error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="이력서 생성에 실패했습니다.",
#         )


# ============ 디버깅 코드가 추가된 새로운 엔드포인트 ============
@router.post("", response_model=ResumeResponse)
async def create_resumes(
    data: str = Form(...),
    photo: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """일반 이력서 생성 (디버깅 버전)"""

    try:
        resume_data = ResumeCreate(**json.loads(data))

        new_resume = Resume(
            user_id=current_user.user_id,
            resume_type=resume_data.resume_type,
            title=resume_data.title,
            name=resume_data.name,
            email=resume_data.email,
            gender=resume_data.gender,
            address=resume_data.address,
            phone=resume_data.phone,
            military_service=resume_data.military_service,
            birth_date=resume_data.birth_date,
            self_introduction=resume_data.self_introduction,
        )
        db.add(new_resume)
        await db.flush()
        await db.refresh(new_resume)
        for idx, technology_stack in enumerate(resume_data.technology_stacks):
            new_tech = TechnologyStack(
                resume_id=new_resume.resume_id, title=technology_stack.title
            )
            db.add(new_tech)

        for experience in resume_data.experiences:
            new_experience = Experience(
                resume_id=new_resume.resume_id, **experience.model_dump()
            )
            db.add(new_experience)

        for education in resume_data.educations:
            new_education = Education(
                resume_id=new_resume.resume_id, **education.model_dump()
            )
            db.add(new_education)

        for project in resume_data.projects:
            new_project = Project(
                resume_id=new_resume.resume_id, **project.model_dump()
            )
            db.add(new_project)

        for activity in resume_data.activities:
            new_activity = Activity(
                resume_id=new_resume.resume_id, **activity.model_dump()
            )
            db.add(new_activity)

        for qualification in resume_data.qualifications:
            new_qualification = Qualification(
                resume_id=new_resume.resume_id, **qualification.model_dump()
            )
            db.add(new_qualification)

        if photo:
            validated: dict = await validate_image_file(photo)

            upload_image = await upload_to_image(file=validated)

            new_image_file = FileModel(
                fileable_id=new_resume.resume_id,
                user_id=current_user.user_id,
                filetype=validated.get("real_format"),
                fileable_table="resumes",
                org_file_name=validated.get("filename"),
                mod_file_name=upload_image.get("unique_filename"),
                file_key=upload_image.get("temp_key"),
                purpose="resume_image",
            )
            db.add(new_image_file)
        await db.commit()
        await db.commit()

        resume_info = await get_resume_response(db=db, resume_id=new_resume.resume_id)

        image_key = resume_info.get("image_key") if resume_info else None
        image_url = await generate_presigned_url(image_key) if image_key else None

        resume_info["image_url"] = image_url

        resume_response = ResumeResponse.model_validate(resume_info).model_dump()

        return resume_response

    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이력서 생성에 실패했습니다.",
        )


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: int,
    data: str = Form(...),
    photo: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """이력서 수정 엔드포인트"""

    try:
        resume = await db.get(Resume, resume_id)

        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 이력서 입니다.",
            )

        if resume.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 접근입니다."
            )

        resume_data = ResumeUpdate(**json.loads(data))

        for c in [
            "title",
            "name",
            "email",
            "gender",
            "address",
            "phone",
            "military_service",
            "birth_date",
            "self_introduction",
        ]:
            setattr(resume, c, getattr(resume_data, c))
        resume.updated_at = datetime.utcnow()

        tech_stmt = delete(TechnologyStack).where(
            TechnologyStack.resume_id == resume_id
        )
        experience_stmt = delete(Experience).where(Experience.resume_id == resume_id)
        education_stmt = delete(Education).where(Education.resume_id == resume_id)
        project_stmt = delete(Project).where(Project.resume_id == resume_id)
        activity_stmt = delete(Activity).where(Activity.resume_id == resume_id)
        qualification_stmt = delete(Qualification).where(
            Qualification.resume_id == resume_id
        )

        for i in [
            tech_stmt,
            experience_stmt,
            education_stmt,
            project_stmt,
            activity_stmt,
            qualification_stmt,
        ]:
            await db.execute(i)

        for technology_stack in resume_data.technology_stacks:
            new_tech = TechnologyStack(
                resume_id=resume_id, title=technology_stack.title
            )
            db.add(new_tech)

        for experience in resume_data.experiences:
            new_experience = Experience(resume_id=resume_id, **experience.model_dump())
            db.add(new_experience)

        for education in resume_data.educations:
            new_education = Education(resume_id=resume_id, **education.model_dump())
            db.add(new_education)

        for project in resume_data.projects:
            new_project = Project(resume_id=resume_id, **project.model_dump())
            db.add(new_project)

        for activity in resume_data.activities:
            new_activity = Activity(resume_id=resume_id, **activity.model_dump())
            db.add(new_activity)

        for qualification in resume_data.qualifications:
            new_qualification = Qualification(
                resume_id=resume_id, **qualification.model_dump()
            )
            db.add(new_qualification)

        resume_info = await get_resume_response(resume_id=resume_id, db=db)
        image_key = resume_info.get("image_key") if resume_info else None

        if photo:
            if image_key:
                await delete_from_storage(image_key)

            validated: dict = await validate_image_file(photo)

            upload_image = await upload_to_image(file=validated)

            await db.execute(
                update(FileModel)
                .where(
                    and_(
                        FileModel.fileable_id == resume_id,
                        FileModel.purpose == "resume_image",
                    )
                )
                .values(
                    filetype=validated.get("real_format"),
                    org_file_name=validated.get("filename"),
                    mod_file_name=upload_image.get("unique_filename"),
                    file_key=upload_image.get("temp_key"),
                )
            )

            image_url = await generate_presigned_url(upload_image.get("temp_key"))
        else:
            image_url = await generate_presigned_url(image_key) if image_key else None

        await db.commit()

        # image_url을 resume_info에 추가
        resume_info["image_url"] = image_url

        resume_response = ResumeResponse.model_validate(resume_info).model_dump()

        return resume_response

    except Exception as e:
        logger.error(f"error : {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이력서 수정에 실패했습니다.",
        )


@router.patch("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """이력서를 비활성화(삭제) 하는 엔드포인트"""

    try:
        resume = await db.get(Resume, resume_id)

        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 이력서 입니다.",
            )

        if resume.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 접근입니다."
            )

        resume.is_active = False

        await db.commit()

    except Exception as e:
        logger.error(f"error : {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이력서 삭제에 실패 했습니다.",
        )
