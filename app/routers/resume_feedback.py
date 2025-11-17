from fastapi import APIRouter

from app.schemas import JobPostingCreate, ResumeCreate, ResumeFeedbackAI
from app.util.ai import resume_feedback_with_posting, resume_standard_feedback


router = APIRouter(prefix="/resume_feedbacks", tags=["Resume_Feedback"])


@router.post('/standard', response_model=ResumeFeedbackAI)
async def resume_feedback(resume:ResumeCreate):
    
    resume = resume.model_dump()
    
    result = await resume_standard_feedback(resume)
    
    return result

@router.post('/posting', response_model=ResumeFeedbackAI)
async def resume_feedback_with_jobposting(resume:ResumeCreate, posting: JobPostingCreate):
    
    resume = resume.model_dump()
    posting = posting.model_dump()
    result = await resume_feedback_with_posting(resume=resume, posting=posting)
    
    return result