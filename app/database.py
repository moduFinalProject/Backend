from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.debug,
    pool_pre_ping = True,
    pool_size = settings.db_pool_size,
    max_overflow= settings.db_max_overflow,
    pool_timeout = settings.db_pool_timeout
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()