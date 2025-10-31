from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User
from app.dependencies import user_id
from sqlalchemy import select


router = APIRouter()

@router.get("/users/me")
async def get_current_user_info(db: AsyncSession = Depends(get_db)):
    # 비동기 쿼리
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    return user


    return current_user


    # 만약 ID만 필요하다면:
    return current_user.id