from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import date, datetime
from models import Experience, Activity, Education, Project, Qualification

from app.routers.resumes import ResumeCreate, ResumeResponse, ResumeUpdate 
from app.models import ResumeDB, ExperienceDB, ActivityDB, EducationDB, ProjectDB, QualificationDB, TechnologyStackDB 
from app.database import get_db

class ResumeCreate(BaseModel):
    """이력서 생성 (POST 요청용)"""
    # 1. 기본 정보 (필수)
    name: str
    email: str
    phone_number: str

    # 2. 공고 URL (선택)
    job_post_url: Optional[HttpUrl] = None

    # 3. 주요 섹션 (목록 형태로 정의, 기본값: 빈 리스트)
    experiences: List[Experience] = [] # 경력 (Experience)
    activities: List[Activity] = [] # 활동 (Activity)
    educations: List[Education] = []
    projects: List[Project] = []
    qualifications: List[Qualification] = []

    # 4. 기술 스택 (필수 목록)
    tech_stack_summary: List[str]


class ResumeUpdate(BaseModel):
    """이력서 수정 (PUT/PATCH 요청용)"""
    # 모든 필드는 Optional로 설정하여 부분 업데이트를 허용
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None

    job_post_url: Optional[HttpUrl] = None

    # 목록형 데이터는 보통 전체를 덮어쓰거나, 별도의 중첩 API로 관리 (여기서는 덮어쓰기로 가정)
    experiences: Optional[List[Experience]] = None
    activities: Optional[List[Activity]] = None
    educations: Optional[List[Education]] = None
    projects: Optional[List[Project]] = None
    qualifications: Optional[List[Qualification]] = None

    tech_stack_summary: Optional[List[str]] = None


class ResumeResponse(BaseModel):
    """이력서 응답 (GET 요청 및 생성 후 반환용)"""
    
    resume_id: int 
    created_at: datetime
    updated_at: datetime
    
    # ResumeCreate의 모든 필드 포함
    name: str
    email: str
    phone_number: str
    job_post_url: Optional[HttpUrl] = None
    
    experiences: List[Experience]
    activities: List[Activity]
    educations: List[Education]
    projects: List[Project]
    qualifications: List[Qualification]
    tech_stack_summary: List[str]
    
    # Pydantic V2 설정 (class Config 대신 model_config 사용)
    model_config = {
        # DB 객체에서 Pydantic 모델로 변환 허용 (ORM 모드 활성화)
        "from_attributes": True,
        # 필드명이 아닌 속성 이름(예: DB column 이름)으로 값 할당을 허용
        "populate_by_name": True 
    }

