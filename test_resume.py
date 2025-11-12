import httpx
import asyncio
import json

async def test_resume_creation():
    async with httpx.AsyncClient() as client:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMiIsImVtYWlsIjoiMDEwNTA1MDBAZ21haWwuY29tIiwibmFtZSI6Iko2TSIsImV4cCI6MTczMDAxMzA3OH0.H8yHMW01iH9wkBSN-jjHTCNxw3KqBjHRvvZ8zXBvYEg"

        data = {
            "resume_type": 1,
            "title": "테스트 이력서",
            "name": "홍길동",
            "email": "test@example.com",
            "gender": 1,
            "address": "서울",
            "phone": "01012345678",
            "military_service": 1,
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
        print(f"Response: {response.text[:2000]}")

asyncio.run(test_resume_creation())
