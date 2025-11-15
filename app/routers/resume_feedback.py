from fastapi import APIRouter

from app.schemas import ResumeCreate, ResumeFeedbackAI
from app.util.ai import resume_standard_feedback


router = APIRouter(prefix="/resume_feedbacks", tags=["Resume_Feedback"])


@router.post('/stantard', response_model=ResumeFeedbackAI)
async def resume_feedback(resume:ResumeCreate):
    result = resume_standard_feedback(resume)
    
    return result