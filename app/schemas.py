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

class ExperienceItem(BaseModel):
    company: str = Field(max_length=100)
    position: str = Field(max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None

class EducationItem(BaseModel):
    school: str = Field(max_length=100)
    major: str = Field(max_length=100)
    degree: Optional[str] = None
    gpa: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ProjectItem(BaseModel):
    name: str = Field(max_length=200)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class CertificationItem(BaseModel):
    name: str = Field(max_length=100)
    issuer: str = Field(max_length=100)
    issue_date: Optional[date] = None

class ActivityItem(BaseModel):
    name: str = Field(max_length=200)
    organization: Optional[str] = Field(default=None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None


# ===== 이력서 스키마 =====
class ResumeCreate(BaseModel):
    name: TrimmedStr = Field(max_length=100)
    email: EmailStr
    phone: TrimmedStr = Field(max_length=20)
    address: Optional[str] = Field(default=None, max_length=200)
    introduction: Optional[str] = Field(default=None, max_length=2000)
    
    experiences: Optional[List[ExperienceItem]] = Field(default_factory=list)
    educations: Optional[List[EducationItem]] = Field(default_factory=list)
    projects: Optional[List[ProjectItem]] = Field(default_factory=list)
    activities: Optional[List[ActivityItem]] = Field(default_factory=list)
    skills: Optional[List[str]] = Field(default_factory=list)
    certifications: Optional[List[CertificationItem]] = Field(default_factory=list)
    
    title: Optional[str] = Field(default="내 이력서", max_length=100)

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
    title: Optional[str] = None


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
    
    experiences: Optional[List[ExperienceItem]] = Field(default_factory=list)
    educations: Optional[List[EducationItem]] = Field(default_factory=list)
    projects: Optional[List[ProjectItem]] = Field(default_factory=list)
    activities: Optional[List[ActivityItem]] = Field(default_factory=list)
    skills: Optional[List[str]] = Field(default_factory=list)
    certifications: Optional[List[CertificationItem]] = Field(default_factory=list)
    
    file_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ResumeListResponse(BaseModel):
    id: int
    title: str
    name: str
    is_default: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
