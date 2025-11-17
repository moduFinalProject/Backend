from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import DashboardResponse
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

        # 통계 조회
        stats_query = text("""
        WITH week_ago AS (
            SELECT NOW() - INTERVAL '7 days' AS week_start
        ),
        base_resumes AS (
            SELECT resume_id
            FROM resumes
            WHERE user_id = :user_id AND is_active = true
        ),
        base_feedbacks AS (
            SELECT feedback_id, created_at
            FROM resumefeedbacks
            WHERE user_id = :user_id
        ),
        base_jobpostings AS (
            SELECT posting_id, created_at
            FROM jobpostings
            WHERE user_id = :user_id AND is_active = true
        )
        SELECT
            (SELECT COUNT(*) FROM base_resumes) AS total_resumes,
            (SELECT COUNT(*) FROM base_resumes br JOIN resumes r ON br.resume_id = r.resume_id WHERE r.created_at >= (SELECT week_start FROM week_ago)) AS this_week_resumes,
            (SELECT COUNT(*) FROM base_feedbacks WHERE created_at >= (SELECT week_start FROM week_ago)) AS this_week_ai_feedback,
            (SELECT COUNT(*) FROM base_jobpostings) AS total_job_postings,
            (SELECT COUNT(*) FROM base_jobpostings WHERE created_at >= (SELECT week_start FROM week_ago)) AS this_week_job_postings
        """)

        stats_result = await db.execute(stats_query, {"user_id": user_id})
        stats_row = stats_result.first()

        # 최근 이력서 조회
        resumes_query = text("""
        SELECT resume_id, title, COALESCE(updated_at, created_at) AS updated_at
        FROM resumes
        WHERE user_id = :user_id AND is_active = true
        ORDER BY created_at DESC
        LIMIT 3
        """)

        resumes_result = await db.execute(resumes_query, {"user_id": user_id})
        recent_resumes = [
            {"resume_id": row.resume_id, "title": row.title, "updated_at": row.updated_at}
            for row in resumes_result.all()
        ]

        # 최근 활동 조회
        activities_query = text("""
        SELECT action_type, description, created_at
        FROM useractiviylogs
        WHERE user_id = :user_id AND action_type != 'login'
        ORDER BY created_at DESC
        LIMIT 3
        """)

        activities_result = await db.execute(activities_query, {"user_id": user_id})
        recent_activities = [
            {"action_type": row.action_type, "description": row.description, "created_at": row.created_at}
            for row in activities_result.all()
        ]

        return {
            "total_resumes": stats_row.total_resumes or 0,
            "this_week_resumes": stats_row.this_week_resumes or 0,
            "this_week_ai_feedback": stats_row.this_week_ai_feedback or 0,
            "total_job_postings": stats_row.total_job_postings or 0,
            "this_week_job_postings": stats_row.this_week_job_postings or 0,
            "recent_resumes": recent_resumes,
            "recent_activities": recent_activities,
        }

    except Exception as e:
        print(f"[ERROR] 대시보드 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대시보드 조회 실패: {str(e)}",
        )
