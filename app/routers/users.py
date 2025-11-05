from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.security import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """현재 로그인한 사용자의 프로필 조회"""
    return current_user

@router.put("/me")
def update_my_profile(
    name: str = None,
    phone: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """프로필 수정"""
    if name:
        current_user.name = name
    if phone:
        current_user.phone = phone
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/me")
def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """회원 탈퇴"""
    db.delete(current_user)
    db.commit()
    return {"message": "회원 탈퇴가 완료되었습니다"}