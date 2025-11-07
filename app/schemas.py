import datetime
import re
from typing import Annotated, List, Optional
from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field, StringConstraints, field_validator
from datetime import date

# ===== 기존 유틸리티 함수들 =====
def strip_string(a: str):
    if isinstance(a, str):
        return a.strip()
    return a

def normalize_str(a: str):
    if isinstance(a, str):
        a = a.strip()
        return re.sub(r'\s+',' ',a)
    return a

Username = Annotated[
    str, StringConstraints(max_length=20, min_length=2, pattern=r"^[A-Za-z가-힣0-9_]+$")
]
TrimmedStr = Annotated[str, BeforeValidator(strip_string)]
Normalizedstr = Annotated[str, BeforeValidator(normalize_str)]


# ===== 인증 관련 =====
class Login(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str):
        password = password.strip()
        if not password:
            raise ValueError("비밀 번호를 입력해 주세요")
        return password


class UserCreate(BaseModel):
    username: Username
    email: EmailStr
    password: str
    password_test: str
    bio: Optional[str] = Field(default=None, max_length=500)

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str):
        if " " in password:
            raise ValueError("공백은 포함할 수 없습니다.")
        if len(password) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다.")
        if not any(c.isalpha() for c in password):
            raise ValueError("영문을 포함해야 합니다.")
        if not any(c.isdigit() for c in password):
            raise ValueError("숫자를 포함해야 합니다.")
        if not any(c in "!@#$%^&*" for c in password):
            raise ValueError("특수문자를 포함해야 합니다.")
        return password


# ===== JWT 인증 관련 추가 =====
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=50)
    phone: Optional[str] = None
    user_type: str = Field(default="job_seeker")  # job_seeker or employer

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    phone: Optional[str] = None
    user_type: str
    
    model_config = ConfigDict(from_attributes=True)


# ===== 채용공고 스키마 =====
class JobPostingCreate(BaseModel):
    company_name: TrimmedStr = Field(min_length=1, max_length=100)
    title: TrimmedStr = Field(min_length=1, max_length=200)
    description: str = Field(min_length=10)
    requirements: Optional[str] = None
    preferred_qualifications: Optional[str] = None
    responsibilities: Optional[str] = None
    
    salary_min: Optional[int] = Field(default=None, ge=0)
    salary_max: Optional[int] = Field(default=None, ge=0)
    salary_type: Optional[str] = Field(default="연봉")
    location: TrimmedStr = Field(min_length=1, max_length=100)
    employment_type: str = Field(default="정규직")
    experience_level: Optional[str] = None
    education_level: Optional[str] = None
    
    tech_stack: Optional[str] = None
    job_category: Optional[str] = None
    deadline: Optional[datetime.datetime] = None


class JobPostingUpdate(BaseModel):
    title: Optional[TrimmedStr] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    preferred_qualifications: Optional[str] = None
    responsibilities: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_type: Optional[str] = None
    location: Optional[TrimmedStr] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    education_level: Optional[str] = None
    tech_stack: Optional[str] = None
    job_category: Optional[str] = None
    deadline: Optional[datetime.datetime] = None
    is_active: Optional[bool] = None


class JobPostingResponse(BaseModel):
    id: int
    user_id: int
    company_name: str
    title: str
    description: str
    requirements: Optional[str] = None
    preferred_qualifications: Optional[str] = None
    responsibilities: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_type: Optional[str] = None
    location: str
    employment_type: str
    experience_level: Optional[str] = None
    education_level: Optional[str] = None
    tech_stack: Optional[str] = None
    job_category: Optional[str] = None
    deadline: Optional[datetime.datetime] = None
    is_active: bool
    views: int
    application_count: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)


# ===== 이력서 관련 상세 스키마 =====

# 경력 항목
class ExperienceItem(BaseModel):
    company: str = Field(max_length=100)
    position: str = Field(max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None


# 학력 항목
class EducationItem(BaseModel):
    school: str = Field(max_length=100)
    major: str = Field(max_length=100)
    degree: Optional[str] = None
    gpa: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


# 프로젝트 항목
class ProjectItem(BaseModel):
    name: str = Field(max_length=200)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


# 자격증 항목
class CertificationItem(BaseModel):
    name: str = Field(max_length=100)
    issuer: str = Field(max_length=100)
    issue_date: Optional[date] = None



# 포트폴리오 항목
class PortfolioItem(BaseModel):
    name: str = Field(max_length=200)
    description: Optional[str] = None
    file_url: Optional[str] = None
    link: Optional[str] = None


# 활동 항목 (새로 추가)
class ActivityItem(BaseModel):
    """경력/활동 항목"""
    name: str = Field(max_length=200)  # 활동명
    organization: Optional[str] = Field(default=None, max_length=100)  # 기관/단체
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None


# 이력서 생성 요청
class ResumeCreate(BaseModel):
    profile_image: Optional[str] = None
    
    # 기본 정보
    name: TrimmedStr = Field(max_length=100)
    email: EmailStr
    phone: TrimmedStr = Field(max_length=20)
    address: Optional[str] = Field(default=None, max_length=200)
    
    # 자기소개
    introduction: Optional[str] = Field(default=None, max_length=2000)
    
    # 경력
    experiences: Optional[List[ExperienceItem]] = Field(default_factory=list)
    
    # 학력
    educations: Optional[List[EducationItem]] = Field(default_factory=list)
    
    # 프로젝트
    projects: Optional[List[ProjectItem]] = Field(default_factory=list)
    
    # 경력/활동 (새로 추가)
    activities: Optional[List[ActivityItem]] = Field(default_factory=list)
    
    # 기술 스택
    skills: Optional[List[str]] = Field(default_factory=list)
    
    # 자격증 및 어학
    certifications: Optional[List[CertificationItem]] = Field(default_factory=list)
    
    # 포트폴리오
    portfolios: Optional[List[PortfolioItem]] = Field(default_factory=list)
    
    # 이력서 제목
    title: Optional[str] = Field(default="내 이력서", max_length=100)
    
    # 기본 이력서 설정
    is_default: bool = False


# 이력서 수정 요청
class ResumeUpdate(BaseModel):
    profile_image: Optional[str] = None
    name: Optional[TrimmedStr] = None
    email: Optional[EmailStr] = None
    phone: Optional[TrimmedStr] = None
    address: Optional[str] = None
    introduction: Optional[str] = None
    experiences: Optional[List[ExperienceItem]] = None
    educations: Optional[List[EducationItem]] = None
    projects: Optional[List[ProjectItem]] = None
    activities: Optional[List[ActivityItem]] = None
    skills: Optional[List[str]] = None
    certifications: Optional[List[CertificationItem]] = None
    portfolios: Optional[List[PortfolioItem]] = None
    title: Optional[str] = None
    is_default: Optional[bool] = None


# 이력서 응답
class ResumeResponse(BaseModel):
    id: int
    user_id: int
    
    title: str
    profile_image: Optional[str] = None
    name: str
    email: str
    phone: str
    address: Optional[str] = None
    
    introduction: Optional[str] = None
    experiences: Optional[str] = None  # JSON 문자열
    educations: Optional[str] = None
    projects: Optional[str] = None
    activities: Optional[str] = None  # JSON 문자열
    skills: Optional[str] = None
    certifications: Optional[str] = None
    languages: Optional[str] = None
    portfolios: Optional[str] = None
    
    file_url: Optional[str] = None
    
    ai_score: Optional[int] = None
    ai_feedback: Optional[str] = None
    
    is_default: bool
    
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)


# 이력서 간단 응답
class ResumeListResponse(BaseModel):
    id: int
    title: str
    name: str
    is_default: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)


# ===== 지원 스키마 =====
class ApplicationCreate(BaseModel):
    job_posting_id: int
    resume_id: int
    cover_letter: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    job_posting_id: int
    resume_id: int
    cover_letter: Optional[str] = None
    status: str
    ai_match_score: Optional[int] = None
    ai_analysis: Optional[str] = None
    applied_at: datetime.datetime
    reviewed_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)