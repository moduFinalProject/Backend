from dataclasses import Field
from datetime import date, datetime
from typing import Literal, Optional

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
    unique_id : str
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



# class UserModel(BaseModel):

#     email : str
#     name: str
#     address: str
#     phone: Optional[str] = None
#     birthdate : date
#     gender : str
#     gender_detail : str
    
#     model_config = ConfigDict(from_attributes=True)
    
    
class ExperienceCreate(BaseModel):
    job_title : str = Field(max_length=20, description="직책/직무명")
    department: str = Field(max_length=20, description="부서명")
    position : Optional[str] = Field(None, max_length=20, description="직급")
    job_description : Optional[str] = Field(None, max_length=1000, description="업무 설명")
    employment_status : bool = Field(description="현재 재직 여부")
    start_date : date = Field(description="시작일")
    end_date: Optional[date] = Field(None, description="종료일")

    @field_validator('job_title', 'department', 'position', 'job_description')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class EducationCreate(BaseModel):
    organ : str = Field(max_length=20, description="학교/기관명")
    department : str = Field(max_length=20, description="학과/전공")
    degree_level : Literal['1','2','3','4','5'] = Field(description="학위 1:고졸, 2:전문학사, 3:학사, 4:석사, 5:박사")
    score : Optional[str] = Field(None, max_length=10, description="학점/성적")
    start_date : date = Field(description="입학일")
    end_date: Optional[date] = Field(None, description="졸업일")

    @field_validator('organ', 'department', 'degree_level', 'score')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class ProjectCreate(BaseModel):
    title : str = Field(max_length=20, description="프로젝트명")
    start_date : date = Field(description="시작일")
    end_date: Optional[date] = Field(None, description="종료일")
    description : Optional[str] = Field(None, max_length=500)

    @field_validator('title', 'description')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class ActivityCreate(BaseModel):
    title : str = Field(max_length=20, description="활동명")
    start_date : date = Field(description="시작일")
    end_date: Optional[date] = Field(None, description="종료일")
    description : Optional[str] = Field(None, max_length=500)

    @field_validator('title', 'description')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v
    
class QualificationCreate(BaseModel):
    title : str = Field(max_length=20, description="자격증명")
    acquisition_date : date = Field(description="취득일")
    score : Optional[str] = Field(None, max_length=10, description="점수/등급")
    organ : Optional[str] = Field(None, max_length=20, description="발급 기관")

    @field_validator('title', 'score', 'organ')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class TechnologyStackCreate(BaseModel):
    title: str = Field(min_length=1, max_length=20, description="기술스택명")

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
    resume_type : str = Field(max_length=10, description="이력서 유형")
    title: str = Field(min_length=2, max_length=30, description="이력서 제목")
    name: TrimmedStr = Field(max_length=50, description="이름")
    email: EmailStr = Field(max_length=50, description="이메일")
    gender: Literal['1','2'] = Field(description="성별, 1: 남자, 2: 여자")
    address: Optional[str] = Field(default=None, max_length=50, description="주소")
    phone: TrimmedStr = Field(max_length=50, description="연락처")
    military_service : Literal['1','2','3','4','5','6'] = Field(description="병역사항, 1: 면제, 2:군필, 3:미필, 4:공익, 5:병역특례, 6:해당없음")
    birth_date : Optional[date] = Field(None, description="생년월일")
    self_introduction: Optional[str] = Field(default=None, description="자기소개")
    technology_stacks: Optional[List[TechnologyStackCreate]] = Field(default_factory=list, description="기술스택 목록")


    experiences: Optional[List[ExperienceCreate]] = Field(default_factory=list, description="경력 목록")
    educations: Optional[List[EducationCreate]] = Field(default_factory=list, description="학력 목록")
    projects: Optional[List[ProjectCreate]] = Field(default_factory=list, description="프로젝트 목록")
    activities: Optional[List[ActivityCreate]] = Field(default_factory=list, description="활동 목록")
    qualifications: Optional[List[QualificationCreate]] = Field(default_factory=list, description="자격증 목록")

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
    military_service : str
    
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
    last_accessed: Optional[datetime] = None
    
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



class FeedbackContentAI(BaseModel):
    
    feedback_devision : Literal['1','2','3'] = Field(description="피드백 분류 1:잘된부분, 2:개선 사항, 3: 추가 권장사항")
    feedback_result : str = Field(description='피드백 내용')
    
    model_config = ConfigDict(from_attributes=True)
    
class ResumeFeedbackAI(BaseModel):

    parent_content : str = Field(description="이전 이력서 내용 정리(md 형식의 text)")
    matching_rate : int = Field(ge=0, le=100, description="이력서와 공고 적합도(매칭률), 단위: 백분위")
    feedback_contents : List[FeedbackContentAI] = Field(description="피드백 리스트")
    
    model_config = ConfigDict(from_attributes=True)


class DashboardResumeItem(BaseModel):
    """대시보드 최근 이력서 정보"""
    resume_id: int
    title: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardActivityItem(BaseModel):
    """대시보드 활동 로그 정보"""
    action_type: str
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardResponse(BaseModel):
    """대시보드 전체 응답"""
    total_resumes: int
    this_week_resumes: int
    this_week_ai_feedback: int
    total_job_postings: int
    this_week_job_postings: int
    recent_resumes: List[DashboardResumeItem]
    recent_activities: List[DashboardActivityItem]

    model_config = ConfigDict(from_attributes=True)


class FeedbackContentResponse(BaseModel):
    
    feedback_devision : str
    feedback_result : str
    feedback_devision_detail: str
    
    model_config = ConfigDict(from_attributes=True)


class ResumeFeedbackResponse(BaseModel):
    
    parent_content : str
    matching_rate : int
    feedback_contents : List[FeedbackContentResponse]
    
    model_config = ConfigDict(from_attributes=True)
