from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import and_, delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import (
    Activity,
    Education,
    Experience,
    Project,
    Qualification,
    Resume,
    TechnologyStack,
    User,
)
from app.models import File as FileModel
from app.resume_util import get_resume_response
from app.schemas import ResumeCreate, ResumeListResponse, ResumeResponse, ResumeUpdate
from app.security import get_current_user
from app.storage_util import (
    delete_from_storage,
    generate_presigned_url,
    generate_unique_filename,
    upload_to_image,
    validate_image_file,
)



router = APIRouter(prefix="/resumes", tags=["resumes"])


router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.get("/", response_model=List[ResumeListResponse])
async def get_all_resumes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """현재 사용자의 모든 이력서 목록 조회"""
    result = await db.execute(
        select(Resume).where(Resume.user_id == current_user.user_id)
    )
    resumes = result.scalars().all()
    return resumes


# ============ 기존 엔드포인트 (디버깅 중) ============
# @router.get("/{resume_id}", response_model=ResumeResponse)
# async def get_resume(
#     resume_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """특정 이력서 상세 조회"""
#
#     try:
#         resume = await db.get(Resume, resume_id)
#
#         if resume is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 이력서 입니다.",
#             )
#
#         if resume.user_id != current_user.user_id:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 접근입니다."
#             )
#
#         result = get_resume_response(db=db, resume_id=resume_id)
#
#         image_url = await generate_presigned_url(result.image_key)
#
#         db_resume= ResumeResponse.model_validate(result).model_dump()
#
#         db_resume['image_url'] = image_url
#
#         return db_resume
#
#     except Exception as e:
#         print(f"error : {str(e)}")
#         await db.rollback()
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이력서 수정에 실패했습니다.")


# ============ 디버깅 코드가 추가된 새로운 엔드포인트 ============
@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """특정 이력서 상세 조회 (디버깅 버전)"""

    try:
        print(f"[DEBUG] 요청된 resume_id: {resume_id}")
        print(f"[DEBUG] 현재 사용자 ID: {current_user.user_id}")

        resume = await db.get(Resume, resume_id)
        print(f"[DEBUG] DB에서 조회한 resume: {resume}")

        if resume is None:
            print(f"[DEBUG] resume_id {resume_id}를 찾을 수 없습니다.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 이력서 입니다.",
            )

        if resume.user_id != current_user.user_id:
            print(f"[DEBUG] 접근 권한 없음. resume.user_id: {resume.user_id}, current_user.user_id: {current_user.user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 접근입니다."
            )

        print(f"[DEBUG] get_resume_response 함수 호출 중...")
        result = await get_resume_response(db=db, resume_id=resume_id)
        print(f"[DEBUG] get_resume_response 결과: {result}")

        if result.image_key:
            print(f"[DEBUG] image_key 존재: {result.image_key}")
            image_url = await generate_presigned_url(result.image_key)
            print(f"[DEBUG] presigned_url 생성됨: {image_url}")
        else:
            print(f"[DEBUG] image_key가 None 또는 empty")
            image_url = None

        print(f"[DEBUG] ResumeResponse.model_validate 호출 중...")
        db_resume = ResumeResponse.model_validate(result).model_dump()
        print(f"[DEBUG] model_validate 성공")

        db_resume['image_url'] = image_url
        print(f"[DEBUG] 최종 응답 준비 완료")

        return db_resume

    except HTTPException as http_exc:
        print(f"[DEBUG] HTTPException 발생: {http_exc.detail}")
        await db.rollback()
        raise
    except Exception as e:
        print(f"[ERROR] 예상치 못한 오류 발생")
        print(f"[ERROR] 에러 타입: {type(e).__name__}")
        print(f"[ERROR] 에러 메시지: {str(e)}")
        import traceback
        print(f"[ERROR] 스택 트레이스:\n{traceback.format_exc()}")
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이력서 조회에 실패했습니다.")



@router.post("", response_model=ResumeResponse)
async def create_resumes(
    data: str = Form(...),
    photo: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """일반 이력서 생성"""

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

        for technology_stack in resume_data.technology_stacks:
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
        
        resume_info = await get_resume_response(db=db, resume_id=new_resume.resume_id)
        
        image_url = await generate_presigned_url(resume_info.image_key) if resume_info.image_key else None
        
        resume_response = ResumeResponse.model_validate(resume_info).model_dump()
        
        resume_response['image_url'] = image_url
        
        return resume_response
    
    
    except Exception as e:

        await db.rollback()
        print(f"error: {str(e)}")
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
        image_key =resume_info.image_key
        
        if photo:
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
                    file_key=upload_image.get("temp_key")
                )
            )
            
            image_url = await generate_presigned_url(upload_image.get("temp_key"))
        else :
            image_url = await generate_presigned_url(image_key)
            
            
        await db.commit()
        

        resume_response = ResumeResponse.model_validate(resume_info).model_dump()
        
        resume_response['image_url'] = image_url
        
        return resume_response
        

    except Exception as e:
        print(f"error : {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이력서 수정에 실패했습니다.")



@router.patch('/{resume_id}')
async def deactivate_resume(resume_id: int, db: AsyncSession = Depends(get_db), current_user : User = Depends(get_current_user)):
    '''이력서를 비활성화(삭제) 하는 엔드포인트'''
    
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
        print(f"error : {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이력서 삭제에 실패 했습니다.")

