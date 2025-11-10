import os
from pydantic_settings import BaseSettings
from typing import Optional

class BaseConfig(BaseSettings):
    
    app_name: str = "gaechwi"
    jwt_algorithm: str = ''
    access_token_expire_minutes: int = ""
    aws_region: str = ''
    
    google_oauth_token_url : str = 'https://oauth2.googleapis.com/token'
    google_oauth_userinfo_url : str = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    image_max_size : int = 5 * 1024 * 1024
 
    
    class Config:
        env_file_encoding = "utf-8"
