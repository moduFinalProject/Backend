from typing import List
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.models import (
    Activity,
    Education,
    Experience,
    FeedbackContent,
    JobPosting,
    Project,
    Qualification,
    Resume,
    ResumeFeedback,
    TechnologyStack,
    User,
)
from app.schema.schemas import (
    JobPostingCreate,
    JobPostingResponse,
    ResumeCreate,
    ResumeFeedbackAI,
    ResumeFeedbackListResponse,
    ResumeFeedbackResponse,
    ResumeResponse,
)
from app.security import get_current_user
from app.service.resume_feedback_service import (
    create_posting_resume_by_feedback,
    create_resume_by_feedback,
    create_resume_with_feedback,
    get_resume_feedback,
    resume_feedback_with_posting,
    resume_standard_feedback,
)
from app.service.resume_service import get_resume_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume_feedbacks", tags=["Resume_Feedback"])


@router.post("/stantard/{resume_id}", response_model=ResumeFeedbackResponse)
async def resume_feedback(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """일반 이력서 첨삭 엔드 포인트"""

    try:
        resume = await get_resume_response(resume_id=resume_id, db=db)
        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 이력서 입니다.",
            )

        if resume.get("user_id") != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 접근입니다."
            )

        result = await resume_standard_feedback(resume)

        new_feedback = ResumeFeedback(
            resume_id=resume.get("resume_id"),
            user_id=current_user.user_id,
            parent_content=result.parent_content,
            matching_rate=result.matching_rate,
        )
        db.add(new_feedback)
        await db.flush()
        await db.refresh(new_feedback)

        for content in result.feedback_contents:
            new_feedback_content = FeedbackContent(
                feedback_id=new_feedback.feedback_id,
                feedback_devision=content.feedback_devision,
                feedback_result=content.feedback_result,
            )
            db.add(new_feedback_content)

        await db.commit()

        feedback = await get_resume_feedback(
            db=db, feedback_id=new_feedback.feedback_id
        )

        return feedback

    except Exception as e:
        await db.rollback()
        logger.error(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="피드백 생성에 실패했습니다.",
        )


@router.post("/posting/{resume_id}/{posting_id}", response_model=ResumeFeedbackResponse)
async def resume_feedback_with_jobposting(
    resume_id: int,
    posting_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """공고별 이력서 첨삭 엔드포인트"""

    try:
        resume = await get_resume_response(resume_id=resume_id, db=db)
        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 이력서 입니다.",
            )

        if resume.get("user_id") != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="잘못된 접근입니다."
            )

        posting = await db.get(JobPosting, posting_id)

        if posting is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 공고입니다.",
            )

        if posting.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="잘못된 접근입니다."
            )

        posting = JobPostingResponse.from_orm(posting).model_dump()

        result = await resume_feedback_with_posting(resume=resume, posting=posting)

        new_feedback = ResumeFeedback(
            resume_id=resume.get("resume_id"),
            posting_id=posting_id,
            user_id=current_user.user_id,
            parent_content=result.parent_content,
            matching_rate=result.matching_rate,
        )
        db.add(new_feedback)
        await db.flush()
        await db.refresh(new_feedback)

        for content in result.feedback_contents:
            new_feedback_content = FeedbackContent(
                feedback_id=new_feedback.feedback_id,
                feedback_devision=content.feedback_devision,
                feedback_result=content.feedback_result,
            )
            db.add(new_feedback_content)

        await db.commit()

        feedback = await get_resume_feedback(
            db=db, feedback_id=new_feedback.feedback_id
        )

        return feedback

    except Exception as e:
        await db.rollback()
        logger.error(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="피드백 생성에 실패했습니다.",
        )


@router.post("/standard_resume/{feedback_id}", response_model=ResumeResponse)
async def apply_feedback(
    feedback_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """기본 피드백 이력서 적용 엔드 포인트"""

    try:
        feedback = await get_resume_feedback(feedback_id=feedback_id, db=db)
        resume = await get_resume_response(resume_id=feedback.resume_id, db=db)

        if feedback is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 피드백입니다.",
            )

        if feedback.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="잘못된 접근입니다."
            )

        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 이력서 입니다.",
            )

        if resume.get("user_id") != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="잘못된 접근입니다."
            )

        feedback = feedback.model_dump()

        result = await create_resume_by_feedback(resume=resume, feedback=feedback)

        new_resume = await create_resume_with_feedback(
            result=result,
            db=db,
            user_id=current_user.user_id,
            parent_resume_id=resume.get("resume_id"),
        )

        return new_resume

    except Exception as e:
        await db.rollback()
        logger.error(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이력서 생성에 실패했습니다.",
        )


@router.post("/posting_resume/{feedback_id}", response_model=ResumeResponse)
async def apply_feedback_with_posting(
    feedback_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """공고별 피드백 이력서 적용 엔드 포인트"""

    try:
        feedback = await get_resume_feedback(feedback_id=feedback_id, db=db)
        resume = await get_resume_response(resume_id=feedback.resume_id, db=db)
        posting = await db.get(JobPosting, feedback.posting_id)

        if feedback is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 피드백입니다.",
            )

        if feedback.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="잘못된 접근입니다."
            )

        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 이력서 입니다.",
            )

        if resume.get("user_id") != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 접근입니다."
            )

        if posting is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 공고입니다.",
            )

        if posting.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="잘못된 접근입니다."
            )

        posting = JobPostingResponse.from_orm(posting)
        posting = posting.model_dump()

        result = await create_posting_resume_by_feedback(
            resume=resume, feedback=feedback, posting=posting
        )

        new_resume = await create_resume_with_feedback(
            result=result,
            db=db,
            user_id=current_user.user_id,
            parent_resume_id=resume.get("resume_id"),
        )

        return new_resume

    except Exception as e:
        await db.rollback()
        logger.error(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이력서 생성에 실패했습니다.",
        )


@router.get("/", response_model=List[ResumeFeedbackListResponse])
async def get_resumefeedback_list(
    page: int = 1,
    page_size: int = 6,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """이력서 리스트를 가져오는 엔드포인트"""

    try:

        offset = (page - 1) * page_size

        data_stmt = (
            select(
                ResumeFeedback.matching_rate,
                func.count(FeedbackContent.feedbackcontent_id).label("content_count"),
                JobPosting.company,
                Resume.title,
                ResumeFeedback.feedback_id,
            )
            .outerjoin(
                FeedbackContent,
                (FeedbackContent.feedback_id == ResumeFeedback.feedback_id),
            )
            .outerjoin(
                JobPosting,
                (JobPosting.posting_id == ResumeFeedback.posting_id)
                & (JobPosting.is_active == True),
            )
            .outerjoin(
                Resume,
                (Resume.resume_id == ResumeFeedback.resume_id)
                & (Resume.is_active == True),
            )
            .where(ResumeFeedback.user_id == current_user.user_id)
            .group_by(
                ResumeFeedback.feedback_id,
                ResumeFeedback.matching_rate,
                JobPosting.company,
                Resume.title,
            )
            .offset(offset)
            .limit(page_size)
        )

        feedback_list = await db.execute(data_stmt)
        result = feedback_list.all()

        return [
            ResumeFeedbackListResponse(
                feedback_id = row.feedback_id,
                company=row.company,
                resume_title=row.title,
                content_count=row.content_count,
                matching_rate=row.matching_rate,
            )
            for row in result
        ]

    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이력서 조회에 실패했습니다.",
        )


@router.get("/content/{feedback_id}", response_model=ResumeFeedbackResponse)
async def get_resumefeedback(
    feedback_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """피드백 상세를 조회하는 엔드포인트"""

    feedback = await get_resume_feedback(db=db, feedback_id=feedback_id)

    if feedback is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 피드백입니다.",
        )

    if feedback.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="잘못된 접근입니다."
        )

    return feedback


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
    feedback_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    '''피드백 삭제 엔드 포인트'''
    
    try:
        feedback = await db.get(ResumeFeedback, feedback_id)
        
        if feedback is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 피드백입니다.",
            )

        if feedback.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="잘못된 접근입니다."
            )
        
        await db.delete(feedback)
        
        await db.commit()

    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="피드백 삭제에 실패했습니다.",
        )