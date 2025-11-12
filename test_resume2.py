import httpx
import asyncio
import json
from app.security import create_access_token

async def test_resume_creation():
    # Generate a fresh token for user unique_id
    # Note: Using 'sub' claim as expected by security.py
    token = create_access_token({"sub": "test_user_001"})
    print(f"Generated token: {token}")

    async with httpx.AsyncClient() as client:
        data = {
            "resume_type": "1",
            "title": "테스트 이력서",
            "name": "홍길동",
            "email": "test@example.com",
            "gender": "1",
            "address": "서울",
            "phone": "01012345678",
            "military_service": "1",
            "birth_date": "1990-01-01",
            "self_introduction": "안녕하세요",
            "technology_stacks": [],
            "experiences": [],
            "educations": [],
            "projects": [],
            "activities": [],
            "qualifications": []
        }

        files = {
            "data": (None, json.dumps(data))
        }

        response = await client.post(
            "http://localhost:8000/resumes/",
            headers={"Authorization": f"Bearer {token}"},
            files=files,
            follow_redirects=True
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:3000]}")

asyncio.run(test_resume_creation())
