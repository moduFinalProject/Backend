from .base import BaseConfig

class DevelopmentConfig(BaseConfig):
    
    debug: bool = True
    environment: str = ''
    
    openai_api_key: str = ''
    
    database_url: str = ''
    db_password: str = ''
    db_name: str = ''
    db_user: str = ''
    db_host: str = ''
    
    jwt_secret: str = ''
    
    host: str = ''
    port: int = 0
    
    domain: str = ''
    email: str = ''
    
    redis_host: str = ''
    redis_port: int = 0
    
    aws_access_key_id: str = ''
    aws_secret_access_key: str = ''
    aws_bucket_name: str = ''
    aws_endpoint_url: str = ''
    
    db_pool_size: int = 5
    db_max_overflow: int = 5
    db_pool_timeout: int = 30
    db_command_timeout: int = 60
    
    google_client_key: str = ''
    google_client_secret: str = ''
    
    front_end_domain: str = ''
    
    
    description : str = """

---

## 개발 자료 (DEV ONLY)

<div style="background: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px 0;">

<a href="https://www.erdcloud.com/d/KNgfev2afc4PpbBiW" target="_blank" style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px;">ERD</a>

<a href="https://drive.google.com/file/d/1h4NaN3dCZtZamfisBrnLudJk-so3z94c/view?usp=sharing" target="_blank" style="display: inline-block; padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px; margin: 5px;">아키텍쳐 구조도</a>

</div>
"""

    
    class Config:
        env_file = ".env"
        extra = "ignore"

