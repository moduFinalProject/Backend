"""
Database 설정 - Async(앱용) + Sync(Alembic용)
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

# ==================== Async 엔진 (FastAPI 앱용) ====================
async_engine = create_async_engine(
    settings.database_url,  # postgresql+asyncpg://...
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    echo=settings.debug,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ==================== Sync 엔진 (Alembic용) ====================
# asyncpg를 psycopg2로 변경한 URL
sync_database_url = settings.database_url.replace(
    "postgresql+asyncpg://",
    "postgresql://"
)

sync_engine = create_engine(
    sync_database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    echo=settings.debug,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)


# ==================== Base ====================
Base = declarative_base()


# ==================== 의존성 ====================
# FastAPI에서 사용할 Async 세션
async def get_db():
    """
    FastAPI 의존성으로 사용할 Async DB 세션
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Seed 스크립트에서 사용할 Sync 세션
def get_sync_db():
    """
    Seed 스크립트나 동기 코드에서 사용할 Sync DB 세션
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()