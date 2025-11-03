import os
from pydantic_settings import BaseSettings
from typing import Optional

class BaseConfig(BaseSettings):
    
    app_name: str = "gaechwi"
    jwt_algorithum: str = ''
    access_token_expire_minutes: int = ""
    aws_region: str = ''
 
    
    class Config:
        env_file_encoding = "utf-8"
