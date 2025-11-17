from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.models import User
from app.schema.schemas import DashboardResponse
from app.security import get_current_user


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """대시보드 정보 조회"""
    try:
        user_id = current_user.user_id

        query = text("""
        WITH week_ago AS (
            SELECT NOW() - INTERVAL '7 days' AS week_start
        ),
        base_resumes AS (
            SELECT resume_id, title, created_at, updated_at
            FROM resumes
            WHERE user_id = :user_id
              AND is_active = true
        ),
        base_feedbacks AS (
            SELECT feedback_id, resume_id, created_at
            FROM resumefeedbacks
            WHERE user_id = :user_id
        ),
        base_jobpostings AS (
            SELECT posting_id, created_at
            FROM jobpostings
            WHERE user_id = :user_id
              AND is_active = true
        ),
        stats AS (
            SELECT
                (SELECT COUNT(*) FROM base_resumes) AS total_resumes,
                (SELECT COUNT(*) FROM base_resumes WHERE created_at >= week_start) AS this_week_resumes,
                (SELECT COUNT(*) FROM base_feedbacks WHERE created_at >= week_start) AS this_week_ai_feedback,
                (SELECT COUNT(*) FROM base_jobpostings) AS total_job_postings,
                (SELECT COUNT(*) FROM base_jobpostings WHERE created_at >= week_start) AS this_week_job_postings
            FROM week_ago
        ),
        recent_resumes AS (
            SELECT
                resume_id,
                title,
                COALESCE(updated_at, created_at) AS updated_at
            FROM base_resumes
            ORDER BY created_at DESC
            LIMIT 3
        ),
        recent_activities AS (
            SELECT action_type, description, created_at
            FROM useractiviylogs
            WHERE user_id = :user_id AND action_type != 'login'
            ORDER BY created_at DESC
            LIMIT 3
        )
        SELECT JSON_BUILD_OBJECT(
            'stats', (SELECT ROW_TO_JSON(s) FROM stats s),
            'recent_resumes', COALESCE((SELECT JSON_AGG(ROW_TO_JSON(rr)) FROM recent_resumes rr), '[]'::json),
            'recent_activities', COALESCE((SELECT JSON_AGG(ROW_TO_JSON(ra)) FROM recent_activities ra), '[]'::json)
        ) AS result
        """)

        result = await db.execute(query, {"user_id": user_id})
        row = result.first()

        if not row or not row.result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="대시보드 데이터 조회 실패",
            )

        # JSON 결과 파싱 (이미 dict 형태로 자동 변환됨)
        data = row.result
        stats = data.get("stats", {})
        recent_resumes = data.get("recent_resumes", [])
        recent_activities = data.get("recent_activities", [])

        return {
            "total_resumes": stats.get("total_resumes") or 0,
            "this_week_resumes": stats.get("this_week_resumes") or 0,
            "this_week_ai_feedback": stats.get("this_week_ai_feedback") or 0,
            "total_job_postings": stats.get("total_job_postings") or 0,
            "this_week_job_postings": stats.get("this_week_job_postings") or 0,
            "recent_resumes": recent_resumes,
            "recent_activities": recent_activities,
        }

    except Exception as e:
        print(f"[ERROR] 대시보드 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대시보드 조회 실패: {str(e)}",
        )
