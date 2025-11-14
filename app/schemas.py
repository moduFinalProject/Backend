from dataclasses import Field
from datetime import date, datetime
from typing import Optional

import re
from typing import Annotated, List, Optional
from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field, StringConstraints, field_validator
from datetime import date

# ===== 유틸리티 =====
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




class UserCreate(BaseModel):
    email: str = Field(max_length=100)
    name : str = Field(max_length=50)
    address : Optional[str] = Field(None, max_length=100)
    birth_date : date
    gender : str = Field(max_length=10)
    provider : Optional[str] = Field(None, max_length=50)
    provider_id : Optional[str] = Field(None, max_length=50)
    phone : Optional[str] = Field(None, max_length=20)
    user_type : str = "1"
    military_service : str

    @field_validator('email', 'name', 'address', 'gender', 'provider', 'provider_id', 'phone')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v
    



class AuthCode(BaseModel):
    code : str
    

class UserResponse(BaseModel):
    uniqe_id : str
    email : str
    name: str
    address: str
    phone: Optional[str] = None
    birthdate : date
    gender : str
    gender_detail : str
    provider : Optional[str] = None
    provider_id : Optional[str] = None
    user_type: str
    user_type_detail: str
    is_sanction : bool
    created_at : datetime
    updated_at : datetime
    last_accessed : datetime



class UserInfo(BaseModel):

    email : str
    name: str
    address: str
    phone: Optional[str] = None
    birthdate : date
    gender : str
    gender_detail : str
    
    model_config = ConfigDict(from_attributes=True)
    
    
class ExperienceCreate(BaseModel):
    job_title : str = Field(max_length=20)
    department: str = Field(max_length=20)
    position : Optional[str] = Field(None, max_length=20)
    job_description : Optional[str] = Field(None, max_length=1000)
    employment_status : bool
    start_date : date
    end_date: Optional[date] = None

    @field_validator('job_title', 'department', 'position', 'job_description')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class EducationCreate(BaseModel):
    organ : str = Field(max_length=20)
    department : str = Field(max_length=20)
    degree_level : Optional[str] = Field(None, max_length=10)
    score : Optional[str] = Field(None, max_length=10)
    start_date : date
    end_date: Optional[date] = None

    @field_validator('organ', 'department', 'degree_level', 'score')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class ProjectCreate(BaseModel):
    title : str = Field(max_length=20)
    start_date : date
    end_date: Optional[date] = None
    description : Optional[str] = Field(None, max_length=500)

    @field_validator('title', 'description')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class ActivityCreate(BaseModel):
    title : str = Field(max_length=20)
    start_date : date
    end_date: Optional[date] = None
    description : Optional[str] = Field(None, max_length=500)

    @field_validator('title', 'description')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v
    
class QualificationCreate(BaseModel):
    title : str = Field(max_length=20)
    acquisition_date : date
    score : Optional[str] = Field(None, max_length=10)
    organ : Optional[str] = Field(None, max_length=20)

    @field_validator('title', 'score', 'organ')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class TechnologyStackCreate(BaseModel):
    title: str = Field(min_length=1, max_length=20)

    @field_validator('title')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v




class ExperienceResponse(BaseModel):
    job_title : str
    department: str
    position : Optional[str] = None
    job_description : Optional[str] = None
    employment_status : bool
    start_date : date
    end_date: Optional[date] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    

class EducationResponse(BaseModel):
    organ : str
    department : str
    degree_level : Optional[str] = None
    degree_level_detail : Optional[str] = None
    score : Optional[str] = None
    start_date : date
    end_date: Optional[date] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    

class ProjectResponse(BaseModel):
    title : str
    start_date : date
    end_date: Optional[date] = None
    description : Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    

class ActivityResponse(BaseModel):
    title : str
    start_date : date
    end_date: Optional[date] = None
    description : Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
    
class QualificationResponse(BaseModel):
    title : str
    acquisition_date : date
    score : Optional[str] = None
    organ : Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)



class TechnologyStackResponse(BaseModel):
    title : str

    model_config = ConfigDict(from_attributes=True)




# ===== 이력서 스키마 =====
class ResumeCreate(BaseModel):
    resume_type : str = Field(max_length=10)
    title: str = Field(min_length=2, max_length=30)
    name: TrimmedStr = Field(max_length=50)
    email: EmailStr = Field(max_length=50)
    gender: str
    address: Optional[str] = Field(default=None, max_length=50)
    phone: TrimmedStr = Field(max_length=50)
    military_service : Optional[str] = Field(None, max_length=10)
    birth_date : Optional[date] = None
    self_introduction: Optional[str] = Field(default=None)
    technology_stacks: Optional[List[TechnologyStackCreate]] = Field(default_factory=list)


    experiences: Optional[List[ExperienceCreate]] = Field(default_factory=list)
    educations: Optional[List[EducationCreate]] = Field(default_factory=list)
    projects: Optional[List[ProjectCreate]] = Field(default_factory=list)
    activities: Optional[List[ActivityCreate]] = Field(default_factory=list)
    qualifications: Optional[List[QualificationCreate]] = Field(default_factory=list)

    @field_validator('title', 'name', 'gender','address', 'phone', 'military_service', 'self_introduction')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class ResumeUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=30)
    name: Optional[TrimmedStr] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=50)
    gender : Optional[str] = Field(None, max_length=10)
    address: Optional[str] = Field(None, max_length=50)
    phone: Optional[TrimmedStr] = Field(None, max_length=50)
    military_service : Optional[str] = Field(None, max_length=10)
    birth_date : Optional[date] = None
    self_introduction: Optional[str] = None
    technology_stacks: Optional[List[TechnologyStackCreate]] = Field(default_factory=list)


    experiences: Optional[List[ExperienceCreate]] = Field(default_factory=list)
    educations: Optional[List[EducationCreate]] = Field(default_factory=list)
    projects: Optional[List[ProjectCreate]] = Field(default_factory=list)
    activities: Optional[List[ActivityCreate]] = Field(default_factory=list)
    qualifications: Optional[List[QualificationCreate]] = Field(default_factory=list)

    @field_validator('title', 'name', 'address', 'gender', 'phone', 'military_service', 'self_introduction')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class ResumeResponse(BaseModel):
    resume_id : int
    title: str
    name: str
    email: str
    gender : str
    gender_detail : str
    address: Optional[str] = None
    phone: str
    military_service : Optional[str] = None
    military_service_detail : Optional[str] = None
    birth_date : Optional[date] = None
    self_introduction: Optional[str] = None
    
    experiences: Optional[List[ExperienceResponse]] = Field(default_factory=list)
    educations: Optional[List[EducationResponse]] = Field(default_factory=list)
    projects: Optional[List[ProjectResponse]] = Field(default_factory=list)
    activities: Optional[List[ActivityResponse]] = Field(default_factory=list)
    technology_stacks: Optional[List[TechnologyStackResponse]] = Field(default_factory=list)
    qualifications: Optional[List[QualificationResponse]] = Field(default_factory=list)
    
    image_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    resume_type : str
    resume_type_detail: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ResumeListResponse(BaseModel):
    resume_id: int
    title: str
    created_at: datetime
    resume_type: str
    resume_type_detail : str

    model_config = ConfigDict(from_attributes=True)


# ===== pydantic 스키마 =====
class JobPostingBase(BaseModel):
    """채용 공고 생성 및 수정을 위한 공통 필드 (ERD 컬럼명 반영)"""

    url: Optional[str] = Field(None, max_length=1000, description="공고 URL")
    title: str = Field(..., max_length=30, description="제목")
    company: str = Field(..., max_length=30, description="회사명")
    qualification: str = Field(..., max_length=300, description="자격 요건")
    prefer: str = Field(..., max_length=300, description="우대 사항")
    end_date: Optional[date] = Field(None, description="공고 마감일")
    memo: Optional[str] = Field(None, max_length=500, description="메모")


class JobPostingCreate(JobPostingBase):
    pass


class JobPostingUpdate(BaseModel):
    """채용 공고 수정을 위한 스키마 (모든 필드는 선택 사항)"""

    url: Optional[str] = Field(None, max_length=1000, description="공고 URL")
    title: Optional[str] = Field(None, max_length=30, description="제목")
    company: Optional[str] = Field(None, max_length=30, description="회사명")
    qualification: Optional[str] = Field(None, max_length=300, description="자격 요건")
    prefer: Optional[str] = Field(None, max_length=300, description="우대 사항")
    end_date: Optional[date] = Field(None, description="공고 마감일")
    memo: Optional[str] = Field(None, max_length=500, description="메모")


class JobPostingResponse(JobPostingBase):
    """클라이언트에게 반환할 최종 데이터 스키마 (응답 모델)"""

    posting_id: int = Field(..., description="채용 공고 고유 ID")
    user_id: int = Field(..., description="공고를 작성한 사용자 ID (작성자)")
    created_at: datetime = Field(..., description="생성 시간")

    class Config:
        """SQLAlchemy ORM 모드 활성화"""
        from_attributes = True



class UserInfo(BaseModel):
    
    name : str
    email: str
    gender: str
    phone : str
    birth_date: date 
    address : str
    
    model_config = ConfigDict(from_attributes=True)



class UserProfileResponse(BaseModel):
    """프로필 조회 응답"""
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    created_at: datetime
    last_accessed: datetime
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """프로필 수정 요청"""
    name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=100)
    
    @field_validator('name', 'phone', 'address')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v



class FeedbackContentCreate(BaseModel):
    
    feedback_devision : str
    feedback_result : str



class ResumeFeedbackCreate(BaseModel):
    
    parent_content : str
    matching_rate : int = Field(max_digits=100)
    feedback : List[FeedbackContentCreate]
    