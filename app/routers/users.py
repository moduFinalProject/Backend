import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.models import JobPosting, Resume, User
from app.models.models import User, JobPosting, Resume
from app.schema.schemas import UserInfo, UserProfileResponse, UserProfileUpdate
from app.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/userinfo", response_model=UserInfo)
async def get_current_userinfo(current_user: User = Depends(get_current_user)
):
  '''현재 유저정보 반환'''
  
  return current_user  



@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """현재 로그인한 사용자의 프로필 조회"""

    try:
        return {
            "name": current_user.name,
            "email": current_user.email,
            "phone": getattr(current_user, 'phone', None),
            "address": getattr(current_user, 'address', None),
            "birth_date": getattr(current_user, 'birth_date', None),
            "gender": getattr(current_user, 'gender', None),
            "created_at": current_user.created_at,
            "last_accessed": getattr(current_user, 'last_accessed', None)
        }
    except Exception as e:
        logger.error(f"프로필 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로필 조회 실패: {str(e)}"
        )
    
    



@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    profile_update: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """프로필 수정 (이름, 이메일, 연락처, 주소)"""
    try:
        update_data = profile_update.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(current_user, key, value)
        
        await db.commit()
        await db.refresh(current_user)
        
        return {
            "name": current_user.name,   
            "email": current_user.email,
            "phone": current_user.phone,
            "address": current_user.address,
            "birth_date": current_user.birth_date,
            "gender": current_user.gender,
            "created_at": current_user.created_at,
            "last_accessed": current_user.last_accessed
        }
        
    except Exception as e:
       
        await db.rollback() 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로필 수정 중 오류가 발생했습니다: {str(e)}"
        )






@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """계정 및 소유 데이터 비활성화"""
    try:
        user_id = current_user.user_id

        current_user.is_active = False

        await db.execute(
            update(JobPosting)
            .where(JobPosting.user_id == user_id)
            .values(is_active=False)
        )

        await db.execute(
            update(Resume)
            .where(Resume.user_id == user_id)
            .values(is_active=False)
        )


        await db.commit()

        return
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정 비활성화 중 오류가 발생했습니다: {str(e)}"
        )