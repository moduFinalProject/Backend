import asyncio
from app.database import async_engine
from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

async def create_test_user():
    async with AsyncSession(async_engine) as session:
        # Create a test user
        test_user = User(
            unique_id="test_user_001",
            email="test@example.com",
            name="Test User",
            user_type="1",  # Job seeker
            gender="1",  # Male
            phone="01012345678",
            birth_date=date(1990, 1, 1),
            is_activate=True
        )

        session.add(test_user)
        await session.commit()
        print(f"Test user created with unique_id: {test_user.unique_id}")

asyncio.run(create_test_user())
