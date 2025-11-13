from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User
from app.schemas import UserInfo
from app.security import get_current_user


router = APIRouter(prefix="/user", tags=["User"])


@router.get("/userinfo", response_model=UserInfo)
async def get_current_userinfo(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
  '''현재 유저정보 반환'''
  
  return current_user  
