from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# --- 서브 엔티티 정의 (ERD 기반) ---

class Experience(BaseModel):
    """경력 정보 (Experience)"""
    company_name: str
    job_title: str
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None

class Activity(BaseModel):
    """활동 정보 (Activity)"""
    title: str
    organization: str
    start_date: date
    end_date: Optional[date] = None
    details: Optional[str] = None

class Education(BaseModel):
    """학력 정보 (Education)"""
    school_name: str
    major: str
    degree: str
    start_date: date
    end_date: date

class Project(BaseModel):
    """프로젝트 정보 (Project)"""
    project_name: str
    description: str
    start_date: date
    end_date: Optional[date] = None
    role: Optional[str] = None
    tech_stack: List[str]

class Qualification(BaseModel):
    """자격증 및 어학 정보 (Qualification)"""
    name: str
    issuer: str
    acquisition_date: date
    score: Optional[str] = None