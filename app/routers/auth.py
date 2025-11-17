from datetime import datetime, timezone
import traceback
import logging
from fastapi import APIRouter, Depends, HTTPException, status
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.database import get_db
from app.util.login_logic import create_user, get_user_by_email, get_user_by_provider
from app.security import create_access_token
from app.schemas import AuthCode, UserCreate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])




@router.post("/google/localhost")
async def auth_google_localhost(code: AuthCode, db: AsyncSession = Depends(get_db)):
    """구글 간편 로그인 엔드포인트"""
    try:
        async with httpx.AsyncClient() as client:
            token_data_payload = {
                "code": code.code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": "http://localhost:5173/frontend/googleCallback",
                "grant_type": "authorization_code",
            }

            token_response = await client.post(
                settings.google_oauth_token_url,
                data=token_data_payload,
            )

            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"토큰 교환 실패: {token_response.text}",
                )

            token_data = token_response.json()
            access_token = token_data.get("access_token")

            # 4. 사용자 정보 요청
            user_info_response = await client.get(
                settings.google_oauth_userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if user_info_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"사용자 정보 불러오기 실패: {user_info_response.text}",
                )

            user_info = user_info_response.json()

        # 5. DB 조회
        user = await get_user_by_provider(db, "google", user_info["id"])

        if not user:
            user = await get_user_by_email(db, user_info["email"])

            if not user:
                return {
                    "is_new_user": True,
                    "user": {
                        "provider": "google",
                        "provider_id": user_info["id"],
                        "email": user_info["email"],
                        "name": user_info["name"],
                    },
                }

        # 6. JWT 생성
        jwt_token = create_access_token(data={"sub": user.unique_id})

        user.last_accessed = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(user)

        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": {"name": user.name, "email": user.email},
            "is_new_user": False,
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"예외 발생: {str(e)}")
        logger.error(f"스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"에러 상세: {str(e)}",
        )


@router.post("/google")
async def auth_google(code: AuthCode, db: AsyncSession = Depends(get_db)):
    """구글 간편 로그인 엔드포인트"""
    try:
        async with httpx.AsyncClient() as client:
            token_data_payload = {
                "code": code.code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": f"{settings.front_end_domain}/frontend/googleCallback",
                "grant_type": "authorization_code",
            }

            token_response = await client.post(
                settings.google_oauth_token_url,
                data=token_data_payload,
            )

            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"토큰 교환 실패: {token_response.text}",
                )

            token_data = token_response.json()
            access_token = token_data.get("access_token")

            # 4. 사용자 정보 요청
            user_info_response = await client.get(
                settings.google_oauth_userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if user_info_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"사용자 정보 불러오기 실패: {user_info_response.text}",
                )

            user_info = user_info_response.json()

        # 5. DB 조회
        user = await get_user_by_provider(db, "google", user_info["id"])

        if not user:
            user = await get_user_by_email(db, user_info["email"])

            if not user:
                return {
                    "is_new_user": True,
                    "user": {
                        "provider": "google",
                        "provider_id": user_info["id"],
                        "email": user_info["email"],
                        "name": user_info["name"],
                    },
                }

        # 6. JWT 생성
        jwt_token = create_access_token(data={"sub": user.unique_id})

        user.last_accessed = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(user)

        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": {"name": user.name, "email": user.email},
            "is_new_user": False,
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"예외 발생: {str(e)}")
        logger.error(f"스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"에러 상세: {str(e)}",
        )


@router.post("/signup")
async def signup(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """신규 사용자 로그인 엔드포인트"""
    
    try:
        user = await create_user(
            db=db,
            email=data.email,
            name=data.name,
            address=data.address,
            birth_date=data.birth_date,
            gender=data.gender,
            provider=data.provider,
            provider_id=data.provider_id,
            phone=data.phone,
            user_type=data.user_type,
            military_service = data.military_service
        )

        jwt_token = create_access_token(data={"sub": user.unique_id})
        
        user.last_accessed = datetime.utcnow()
        
        await db.commit()
        
        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": {"name": user.name, "email": user.email},
        }
    
    except Exception as e:
        await db.rollback()
        logger.error(f"예외 발생: {str(e)}")
        logger.error(f"스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"에러 상세: {str(e)}",
        )