from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List

from app.database import get_db
from app.schemas import ResumeUpdate, ResumeResponse, ResumeListResponse
from app.security import get_current_user
from app.models import Resume


router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.get("/", response_model=List[ResumeListResponse])
async def get_all_resumes(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """현재 사용자의 모든 이력서 목록 조회"""
    result = await db.execute(
        select(Resume).where(Resume.user_id == current_user_id)
    )
    resumes = result.scalars().all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """특정 이력서 상세 조회"""
    result = await db.execute(
        select(Resume).where(
            Resume.resume_id == resume_id,
            Resume.user_id == current_user_id
        )
    )
    db_resume = result.scalar_one_or_none()
    
    if db_resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found"
        )
    return db_resume