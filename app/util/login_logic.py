import secrets
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
from app.models import Code, User
from sqlalchemy.orm import aliased


async def get_user_by_id(db: AsyncSession, user_id: str):
    GenderCode = aliased(Code)
    UsertypeCode = aliased(Code)

    stmt = (
        select(
            User,
            GenderCode.code_detail.label("gender_detail"),
            UsertypeCode.code_detail.label("user_type_detail"),
        )
        .outerjoin(
            GenderCode,
            (GenderCode.division == "gender") & (GenderCode.detail_id == User.gender),
        )
        .outerjoin(
            UsertypeCode,
            (UsertypeCode.division == "user_type")
            & (UsertypeCode.detail_id == User.user_type),
        )
        .where(User.unique_id == user_id, User.is_activate == True)
    )

    user = await db.execute(stmt)

    user = user.first()

    return user


async def get_user_by_email(db: AsyncSession, email: str):

    stmt = select(User).where(User.email == email, User.is_activate == True)

    user = await db.execute(stmt)

    user = user.scalar_one_or_none()

    return user


async def get_user_by_provider(db: AsyncSession, provieder: str, provider_id: str):

    stmt = select(User).where(
        User.provider == provieder, User.provider_id == provider_id, User.is_activate == True
    )

    user = await db.execute(stmt)

    user = user.scalar_one_or_none()

    return user


def generate_unique_user_id():
    return secrets.token_urlsafe(16)


async def create_user(
    db: AsyncSession,
    email: str,
    name: str,
    birth_date: date,
    gender: str,
    address: Optional[str] = None,
    provider: Optional[str] = None,
    provider_id: Optional[str] = None,
    phone: Optional[str] = None,
    user_type: Optional[str] = None,
    military_service: Optional[str] = None
):
    unique_id = generate_unique_user_id()

    new_user = User(
        unique_id=unique_id,
        email=email,
        name=name,
        address=address,
        birth_date=birth_date,
        gender=gender,
        provider=provider,
        provider_id=provider_id,
        phone=phone,
        user_type=user_type,
        military_service = military_service
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


# async def update_login(db: AsyncSession, user_id: str):
#     user = await get_user_by_id(db, user_id)

#     if user:
#         user.last_accessed = datetime.utcnow()
#         await db.commit()
#     return None
