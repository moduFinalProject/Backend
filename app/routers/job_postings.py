from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models import User, JobPosting as DBJobPosting
from app.schemas import JobPosting, JobPostingCreate, JobPostingUpdate
from app.security import get_current_user

import app.posting_util as crud  # app/job_postings.py 파일 (CRUD 로직)


router = APIRouter(prefix="/job-postings", tags=["Job Postings"])


@router.post("/", response_model=JobPosting, status_code=status.HTTP_201_CREATED)
async def create_job_posting_endpoint(
    job_posting: JobPostingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """새 채용 공고를 생성하고 DB에 저장합니다."""
    try:
        db_job = await crud.create_job_posting(
            db=db, 
            job_posting=job_posting, 
            user_id=current_user.user_id
        )
        return db_job
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"공고 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{page}/{page_size}", response_model=List[JobPosting])
async def read_all_job_postings_endpoint(page : int= 1, page_size : int= 6,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """모든 채용 공고 목록을 조회합니다."""
    try:
        job_postings = await crud.get_job_postings(db=db,user_id=current_user.user_id, page = page, page_size = page_size)
        return job_postings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"공고 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{posting_id}", response_model=JobPosting)
async def read_job_posting_endpoint(
    posting_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """특정 ID의 채용 공고를 조회합니다."""
    try:
        db_job = await db.get(DBJobPosting, posting_id)

        if db_job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 공고입니다."
            )

        if db_job.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="잘못된 접근입니다."
            )

        return db_job

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"공고 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/{posting_id}", response_model=JobPosting)
async def update_job_posting_endpoint(
    posting_id: int,
    job_posting_update: JobPostingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """특정 ID의 채용 공고를 수정합니다."""
    try:
        job_posting = await db.get(DBJobPosting, posting_id)

        if job_posting is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 공고입니다."
            )

        if job_posting.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="잘못된 접근입니다."
            )

        # 업데이트할 필드들
        for field in [
            "url",
            "title",
            "company",
            "content",
            "qualification",
            "prefer",
            "end_date",
            "memo",
        ]:
            setattr(job_posting, field, getattr(job_posting_update, field))

        job_posting.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(job_posting)

        return job_posting

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"공고 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.patch("/{posting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_posting_endpoint(
    posting_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """특정 ID의 채용 공고를 삭제합니다 (소프트 삭제)."""
    try:
        job_posting = await db.get(DBJobPosting, posting_id)

        if job_posting is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 공고입니다."
            )

        if job_posting.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="잘못된 접근입니다."
            )

        # 소프트 삭제: is_activate을 False로 설정
        job_posting.is_activate = False

        await db.commit()

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"공고 삭제 중 오류가 발생했습니다: {str(e)}"
        )