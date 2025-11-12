from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List


from app.database import get_db # DB 세션 의존성 함수
from app.models import User
from app.schemas import JobPosting, JobPostingCreate, JobPostingUpdate # Pydantic 스키마
from app.security import get_current_user
import app.posting_util as crud  # app/job_postings.py 파일 (CRUD 로직)

router = APIRouter(prefix="/job-postings", tags=["Job Postings"])

# ----------------------------------------------------------------------
## 1. CREATE (POST /job-postings/)
# ----------------------------------------------------------------------
@router.post("/", response_model=JobPosting, status_code=status.HTTP_201_CREATED)
async def create_job_posting_endpoint(
    job_posting: JobPostingCreate, 
    db: AsyncSession = Depends(get_db),
   
    current_user: User = Depends(get_current_user)
):
    """새 채용 공고를 생성하고 DB에 저장합니다."""
   
    db_job = await crud.create_job_posting(db=db, job_posting=job_posting, user_id=current_user.user_id)
    return db_job

# ----------------------------------------------------------------------
## 2. READ ALL (GET /job-postings/)
# ----------------------------------------------------------------------
@router.get("/", response_model=List[JobPosting])
async def read_all_job_postings_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """모든 채용 공고 목록을 조회합니다."""
    # CRUD 함수 호출: get_job_postings
    job_postings = await crud.get_job_postings(db=db)
    return job_postings

# ----------------------------------------------------------------------
## 3. READ SINGLE (GET /job-postings/{posting_id})
# ----------------------------------------------------------------------
@router.get("/{posting_id}", response_model=JobPosting)
async def read_job_posting_endpoint(
    posting_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """특정 ID의 채용 공고를 조회합니다."""
 
    db_job = await crud.get_job_posting(db=db, posting_id=posting_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail=f"Job Posting with ID {posting_id} not found")
    return db_job

# ----------------------------------------------------------------------
## 4. UPDATE (PUT /job-postings/{posting_id})
# ----------------------------------------------------------------------
@router.put("/{posting_id}", response_model=JobPosting)
async def update_job_posting_endpoint(
    posting_id: int,
    job_posting_update: JobPostingUpdate,
    db: AsyncSession = Depends(get_db),

):
    """특정 ID의 채용 공고를 수정합니다."""

    db_job = await crud.update_job_posting(db=db, posting_id=posting_id, job_posting_update=job_posting_update)
    if db_job is None:
        raise HTTPException(status_code=404, detail=f"Job Posting with ID {posting_id} not found")
    return db_job

# ----------------------------------------------------------------------
## 5. DELETE (DELETE /job-postings/{posting_id})
# ----------------------------------------------------------------------
@router.delete("/{posting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_posting_endpoint(
    posting_id: int,
    db: AsyncSession = Depends(get_db),
):
    """특정 ID의 채용 공고를 삭제합니다."""
    # CRUD 함수 호출: delete_job_posting
    success = await crud.delete_job_posting(db=db, posting_id=posting_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Job Posting with ID {posting_id} not found")
    
    
    return