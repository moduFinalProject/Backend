from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.security import get_current_user
from app.database import get_db
from app.models import User, Resume
from app.schemas import ResumeCreate, ResumeResponse

router = APIRouter(prefix="/resumes", tags=["resumes"])

@router.get("/", response_model=List[ResumeResponse])
def get_my_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """내 이력서 목록 조회"""
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    return resumes

@router.post("/", response_model=ResumeResponse)
def create_resume(
    resume_data: ResumeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """이력서 생성"""
    new_resume = Resume(
        user_id=current_user.id,
        title=resume_data.title,
        content=resume_data.content
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    return new_resume

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 이력서 조회"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다")
    
    # 본인 확인
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    return resume

@router.put("/{resume_id}", response_model=ResumeResponse)
def update_resume(
    resume_id: int,
    resume_data: ResumeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """이력서 수정"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다")
    
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    resume.title = resume_data.title
    resume.content = resume_data.content
    
    db.commit()
    db.refresh(resume)
    return resume

@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """이력서 삭제 (본인만 가능)"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다")
    
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    db.delete(resume)
    db.commit()
    return {"message": "삭제되었습니다"}