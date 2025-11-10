import traceback
from fastapi import APIRouter, Depends, HTTPException, status
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.database import get_db
from app.login_logic import create_user, get_user_by_email, get_user_by_provider
from app.security import create_access_token
from app.user_schema import AuthCode, UserCreate, UserModel, UserResponse


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/google")
async def auth_google(code: AuthCode, db: AsyncSession = Depends(get_db)):
    '''구글 간편 로그인 엔드포인트'''
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                settings.google_oauth_token_url,
                data={
                    "code": code.code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": f"{settings.front_end_domain}/frontend/googleCallback",
                    "grant_type": "authorization_code",
                },
            )
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="토큰 교환 실패"
                )
            token_data = token_response.json()
            access_token = token_data.get("access_token")

            user_info_response = await client.get(
                settings.google_oauth_userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if user_info_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="사용자 정보 불러오기 실패",
                )

            user_info = user_info_response.json()

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
        jwt_token = create_access_token(data={"sub": user.unique_id})
        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": {"name": user.name, "email": user.email},
            "is_new_user": False,
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/signup")
async def signup(data: UserCreate, db: AsyncSession = Depends(get_db)):
    '''신규 사용자 로그인 엔드포인트'''
    user = create_user(
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
    )

    jwt_token = create_access_token(data={"sub": user.unique_id})

    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {"name": user.name, "email": user.email},
    }
