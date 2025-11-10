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

    @field_validator('email', 'name', 'address', 'gender', 'provider', 'provider_id', 'phone')
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v
    



class AuthCode(BaseModel):
    code : str
    


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
    title: Optional[str] = Field(default="내 이력서", max_length=30)
    name: TrimmedStr = Field(max_length=50)
    email: EmailStr = Field(max_length=50)
    gender: str
    address: Optional[str] = Field(default=None, max_length=50)
    phone: TrimmedStr = Field(max_length=50)
    military_service : Optional[str] = Field(None, max_length=10)
    birth_date : Optional[date] = None
    self_introduction: Optional[str] = Field(default=None)
    technology_stacks: Optional[List[str]] = Field(default_factory=list)


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
    gender : str
    address: Optional[str] = Field(None, max_length=50)
    phone: Optional[TrimmedStr] = Field(None, max_length=50)
    military_service : Optional[str] = Field(None, max_length=10)
    birth_date : Optional[date] = None
    self_introduction: Optional[str] = None
    technology_stacks: Optional[List[str]] = Field(default_factory=list)


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
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)



class UserResponse(BaseModel):
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
    
    model_config = ConfigDict(from_attributes=True)



