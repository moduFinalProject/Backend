from .base import BaseConfig

class DevelopmentConfig(BaseConfig):
    
    debug: bool = False
    environment: str = ''
    
    openai_api_key: str = ''
    
    database_url: str = ''
    db_password: str = ''
    db_name: str = ''
    db_user: str = ''
    db_host: str = ''
    
    jwt_secret: str = ''
    
    host: str = ''
    port: int = ''
    
    domain: str = ''
    email: str = ''
    
    redis_host: str = ''
    redis_port: int = ''
    
    aws_access_key_id: str = ''
    aws_secret_access_key: str = ''
    aws_bucket_name: str = ''
    aws_endpoint_url: str = ''
    
    class Config:
        env_file = ".env"

