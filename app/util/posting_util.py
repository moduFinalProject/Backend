from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select, update, delete
from typing import Optional, List

from app.models import JobPosting as DBJobPosting
from app.schemas import JobPostingCreate, JobPostingUpdate


async def create_job_posting(
    db: AsyncSession, job_posting: JobPostingCreate, user_id: int
) -> DBJobPosting:
    """새 채용 공고를 생성합니다. user_id는 인증 시스템에서 주입됩니다."""

    db_job = DBJobPosting(
        user_id=user_id, **job_posting.model_dump(exclude_unset=True, exclude_none=True)
    )

    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)

    return db_job


async def get_job_postings(
    db: AsyncSession,
    user_id: int,
    page_size: int = 6,
    page: int = 1,
    title: Optional[str] = None,
) -> List[DBJobPosting]:
    """모든 채용 공고 목록을 조회합니다."""

    offset = (page - 1) * page_size

    title = title.strip() if title else None

    search_condition = (
        [
            DBJobPosting.title.ilike(f"%{title}%"),
            DBJobPosting.user_id == user_id,
            DBJobPosting.is_active == True,
        ]
        if title
        else [DBJobPosting.user_id == user_id, DBJobPosting.is_active == True]
    )
    result = await db.execute(
        select(DBJobPosting)
        .where(*search_condition)
        .order_by(desc(DBJobPosting.created_at))
        .offset(offset)
        .limit(page_size)
    )
    return result.scalars().all()


async def get_job_posting(db: AsyncSession, posting_id: int) -> Optional[DBJobPosting]:
    """특정 채용 공고를 조회합니다."""

    result = await db.execute(
        select(DBJobPosting).where(
            DBJobPosting.posting_id == posting_id, DBJobPosting.is_active == True
        )
    )
    return result.scalar_one_or_none()


async def update_job_posting(
    db: AsyncSession, posting_id: int, job_posting_update: JobPostingUpdate
) -> Optional[DBJobPosting]:
    """특정 채용 공고를 수정합니다."""
    update_data = job_posting_update.model_dump(exclude_unset=True)

    if not update_data:
        return await get_job_posting(db, posting_id)

    stmt = (
        update(DBJobPosting)
        .where(DBJobPosting.posting_id == posting_id)
        .values(**update_data)
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(stmt)
    await db.commit()

    return await get_job_posting(db, posting_id)


async def delete_job_posting(db: AsyncSession, posting_id: int) -> bool:
    """특정 채용 공고를 삭제합니다."""
    stmt = (
        update(DBJobPosting)
        .where(DBJobPosting.posting_id == posting_id)
        .values(is_active=False)
        .execution_options(synchronize_session="fetch")
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
