from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.security import get_current_user_optional
from app.database import get_db
from app.models import User, JobPosting
from app.schemas import JobPostingResponse

router = APIRouter(prefix="/job-postings", tags=["job-postings"])

@router.get("/", response_model=List[JobPostingResponse])
def get_job_postings(
    skip: int = 0,
    limit: int = 20,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """채용공고 목록 조회 (로그인 시 맞춤 추천)"""
    
    if current_user:
        # 로그인한 경우: 사용자 맞춤 추천 (예: AI 기반 매칭)
        # TODO: AI 매칭 로직 추가
        job_postings = db.query(JobPosting)\
            .filter(JobPosting.is_active == True)\
            .offset(skip)\
            .limit(limit)\
            .all()
        return job_postings
    else:
        # 비로그인: 일반 공고 목록
        job_postings = db.query(JobPosting)\
            .filter(JobPosting.is_active == True)\
            .offset(skip)\
            .limit(limit)\
            .all()
        return job_postings

@router.get("/{posting_id}", response_model=JobPostingResponse)
def get_job_posting(
    posting_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """특정 채용공고 상세 조회"""
    posting = db.query(JobPosting).filter(JobPosting.id == posting_id).first()
    
    if not posting:
        raise HTTPException(status_code=404, detail="채용공고를 찾을 수 없습니다")
    
    # 로그인한 경우 조회수 증가 등 추가 로직 가능
    if current_user:
        # TODO: 조회 기록 저장, 관심 공고 추천 등
        pass
    
    return posting