from typing import Annotated, List
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def strip_string(a: str):
    if isinstance(a, str):
        return a.strip()
    return a


TrimmedStr = Annotated[str, BeforeValidator(strip_string)]


class ChatRequest(BaseModel):
    user_message: TrimmedStr


class ChatResponse(BaseModel):
    question: str

    model_config = ConfigDict(from_attributes=True)


class QAItem(BaseModel):

    question: str
    answer: str
    feedback: str

    model_config = ConfigDict(from_attributes=True)


class InterviewTotalFeedback(BaseModel):

    status: int
    status_detail: str
    content: str

    model_config = ConfigDict(from_attributes=True)


class EndInterviewResponse(BaseModel):

    interview_feedbacks: List[InterviewTotalFeedback]
    conversations: List[QAItem]

    model_config = ConfigDict(from_attributes=True)


class StartChatResponse(BaseModel):
    interview_id: int
    first_question: str = Field(min_length=10)