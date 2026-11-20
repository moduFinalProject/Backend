import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.models import Conversation, Interview, JobPosting, User
from app.schema.interview_schemas import ChatRequest, ChatResponse, StartChatResponse
from app.schema.schemas import JobPostingResponse, ResumeResponse
from app.security import get_current_user
from app.service.interview_service import create_chain_with_history
from app.service.resume_service import get_resume_response


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/start/{resume_id}/{posting_id}", response_model=StartChatResponse)
async def start_interview(
    resume_id: int,
    posting_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """모의 면접 시작 엔드 포인트"""

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
        resume_response = ResumeResponse.model_validate(resume)
        resume_dict = resume_response.model_dump()

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

        interview = Interview(
            user_id=current_user.user_id,
            resume_id=resume_id,
            posting_id=posting_id,
            status="1",
        )

        db.add(interview)
        await db.flush()
        await db.refresh(interview)

        session_id = f"interview_{interview.interview_id}"

        chain = create_chain_with_history()

        response = await chain.ainvoke(
            {
                "company": posting.get("company"),
                "posting": posting,
                "resume": resume,
                "input": "면접을 시작하겠습니다. 첫 질문을 해주세요",
            },
            config={"configurable": {"session_id": session_id}},
        )

        first_question = response.content

        qa = Conversation(
            interview_id=interview.interview_id, question=first_question, sequence=1
        )

        db.add(qa)
        await db.commit()

        result = {
            "interview_id": interview.interview_id,
            "first_question": first_question,
            "message": "면접이 시작되었습니다.",
        }

        return result

    except Exception as e:
        await db.rollback()
        logger.error(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="인터뷰 실행에 실패했습니다.",
        )


@router.post("/chat/{interview_id}", response_model=ChatResponse)
async def interview_conversation(
    interview_id: int,
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """면접 진행 엔드포인트"""

    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="면접을 찾을 수 없습니다"
        )

    if interview.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="진행 중인 면접이 아닙니다"
        )
        
    