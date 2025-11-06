from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import date

# --- 서브 모델 정의 ---

class Career(BaseModel):
    """경력 정보"""
    # 필수 필드: 기본값 없음
    company_name: str
    job_title: str
    start_date: date

    # 선택 필드: 기본값 None
    end_date: Optional[date] = None  # 종료일 (재직 중이면 None)
    description: Optional[str] = None  # 담당 업무 및 성과

class Education(BaseModel):
    """학력 정보"""
    # 필수 필드
    school_name: str
    major: str
    degree: str  # 예: 학사, 석사, 고졸
    start_date: date
    end_date: date

class ExperienceActivity(BaseModel):
    """경험/활동 정보"""
    # 필수 필드
    title: str
    organization: str
    start_date: date

    # 선택 필드
    end_date: Optional[date] = None  # 종료일
    details: Optional[str] = None  # 주요 내용 및 기여도

class Project(BaseModel):
    """프로젝트 정보"""
    # 필수 필드
    project_name: str
    description: str
    start_date: date
    tech_stack: List[str]  # 사용 기술 스택 목록

    # 선택 필드
    end_date: Optional[date] = None  # 종료일
    role: Optional[str] = None  # 역할 및 기여도

class CertificationLanguage(BaseModel):
    """자격증 및 어학 정보"""
    # 필수 필드
    name: str
    issuer: str
    acquisition_date: date  # 취득일/시험일

    # 선택 필드
    score: Optional[str] = None  # 점수 또는 등급


# --- 메인 모델 정의: Resume ---

class Resume(BaseModel):
    """
    일반 이력서 메인 모델
    """
    # 1. 기본 정보 (필수 항목: 기본값 없음)
    name: str
    email: str
    phone_number: str

    # 2. 공고 URL (선택)
    job_post_url: Optional[HttpUrl] = None  # 지원 공고 URL (선택 사항)

    # 3. 주요 섹션 (목록 형태로 정의, 기본값: 빈 리스트)
    careers: List[Career] = []
    educations: List[Education] = []
    experiences_activities: List[ExperienceActivity] = []
    projects: List[Project] = []
    certifications_languages: List[CertificationLanguage] = []

    # 4. 기술 스택 (단일 목록)
    tech_stack_summary: List[str]