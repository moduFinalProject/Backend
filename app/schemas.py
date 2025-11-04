from pydantic import BaseModel, Field
from typing import List


class JobPosting(BaseModel):
    """
    채용 공고 텍스트를 담는 요청 스키마
    """
    job_text: str = Field(..., description="분석할 채용 공고의 전체 텍스트")

class StudyRecommendation(BaseModel):
    """
    추천되는 하나의 학습 항목을 위한 스키마
    """
    topic: str = Field(..., description="추천 학습 주제 또는 기술명")
    reasoning: str = Field(..., description="해당 주제를 학습해야 하는 이유 (공고 기반)")

class RecommendationResponse(BaseModel):
    """
    AI 분석 결과를 구조화된 JSON 형태로 담는 최종 응답 스키마
    """
    role_summary: str = Field(..., description="공고에서 추출된 핵심 역할 요약")
    recommended_items: List[StudyRecommendation] = Field(..., description="추천 학습 항목 목록")

    class Config:
        # FastAPI에서 ORM 객체와 호환되도록 설정 (여기서는 JSON 응답 직렬화에 사용)
        from_attributes = True