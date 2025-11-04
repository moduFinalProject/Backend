from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.security import get_current_user
from app.database import get_db
from app.models import User, Application, JobPosting, Resume
from app.schemas import ApplicationCreate, ApplicationResponse

router = APIRouter(prefix="/applications", tags=["applications"])

@router.get("/", response_model=List[ApplicationResponse])
def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """내 지원 내역 조회"""
    applications = db.query(Application)\
        .filter(Application.user_id == current_user.id)\
        .all()
    return applications

@router.post("/", response_model=ApplicationResponse)
def apply_to_job(
    application_data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """채용공고에 지원하기"""
    
    # 채용공고 존재 확인
    job_posting = db.query(JobPosting)\
        .filter(JobPosting.id == application_data.job_posting_id)\
        .first()
    if not job_posting:
        raise HTTPException(status_code=404, detail="채용공고를 찾을 수 없습니다")
    
    # 이력서 존재 및 본인 소유 확인
    resume = db.query(Resume)\
        .filter(Resume.id == application_data.resume_id)\
        .first()
    if not resume or resume.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다")
    
    # 중복 지원 확인
    existing = db.query(Application)\
        .filter(
            Application.user_id == current_user.id,
            Application.job_posting_id == application_data.job_posting_id
        )\
        .first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 지원한 공고입니다")
    
    # 지원 생성
    new_application = Application(
        user_id=current_user.id,
        job_posting_id=application_data.job_posting_id,
        resume_id=application_data.resume_id,
        cover_letter=application_data.cover_letter
    )
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    
    return new_application

@router.delete("/{application_id}")
def cancel_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """지원 취소"""
    application = db.query(Application)\
        .filter(Application.id == application_id)\
        .first()
    
    if not application:
        raise HTTPException(status_code=404, detail="지원 내역을 찾을 수 없습니다")
    
    if application.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    db.delete(application)
    db.commit()
    return {"message": "지원이 취소되었습니다"}