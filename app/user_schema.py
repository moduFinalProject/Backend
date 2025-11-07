from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime


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
    
    model_config = ConfigDict(from_attributes=True)



class UserCreate(BaseModel):
    email: str
    name : str
    address : Optional[str] = None
    birth_date : date
    gender : str
    provider : Optional[str] = None
    provider_id : Optional[str] = None
    phone : Optional[str] = None
    user_type : str = 1