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
            "name":"김취업",
            "birth_date":"2025-12-31",
            "email":"email@email.com",
            "phone":"010-1111-2222",
            "gender":"2",
            "military_service":"1",
            "address":"서울시 강남구",
            "title":"이력서",
            "url":"",
            "photoUrl":"",
            "educations":[{"organ":"한국대학교","department":"컴퓨터공학과","degree_level":"3","score":"4.5점","start_date":"2025-01-01","end_date":"2025-10-01"}],
            "self_introduction":"",
            "experiences":[],
            "projects":[],
            "activities":[],
            "technology_stacks":[],
            "qualifications":[],
            "resume_type":"1"
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
