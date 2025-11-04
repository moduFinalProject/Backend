from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.security import get_current_user, get_current_user_optional
from app.database import get_db
from app.models import User
from app.schemas import SomeResponse, Resume

router = APIRouter()

# 1. 로그인 필수 엔드포인트
@router.get("/my-profile")
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 로그인한 사용자의 프로필 조회"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name
    }

# 2. 로그인 선택적 엔드포인트
@router.get("/job-postings")
def get_job_postings(
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """채용공고 목록 조회 (로그인 시 맞춤 추천)"""
    if current_user:
        # 로그인한 경우: 사용자 맞춤 추천
        return {"message": f"{current_user.email}님을 위한 맞춤 공고"}
    else:
        # 비로그인: 일반 공고 목록
        return {"message": "전체 공고 목록"}

# 3. 본인 확인이 필요한 엔드포인트
@router.delete("/resumes/{resume_id}")
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """이력서 삭제 (본인만 가능)"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다")
    
    # 본인 확인
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    db.delete(resume)
    db.commit()
    return {"message": "삭제되었습니다"}