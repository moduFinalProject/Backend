from fastapi import APIRouter, HTTPException, status
# 상대 경로 임포트를 사용하여 같은 패키지 내의 모듈을 참조
from ..schemas import JobPosting, RecommendationResponse
from ..ai import analyze_and_recommend

router = APIRouter(
    prefix="/study", # /api/v1/study 로 접근
    tags=["Study Guide"]
)

@router.post(
    "/recommend", 
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="채용 공고 분석 및 학습 항목 추천"
)
async def get_study_recommendation(job_posting: JobPosting):
    """
    채용 공고 텍스트를 입력받아 Gemini AI 모델을 통해 필요한 핵심 학습 항목을 추출하고 추천합니다.
    """
    if not job_posting.job_text or len(job_posting.job_text) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="채용 공고 텍스트는 최소 50자 이상이어야 합니다."
        )

    try:
        recommendation_result = await analyze_and_recommend(job_posting.job_text)
        
        if recommendation_result is None:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI 모델로부터 유효한 응답을 받지 못했습니다."
            )
            
        return recommendation_result

    except Exception as e:
        print(f"Recommendation Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"추천 서비스 처리 중 오류 발생: {e}"
        )