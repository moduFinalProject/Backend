from .base import BaseConfig

class ProductionConfig(BaseConfig):
    
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
    port: int = 0
    
    domain: str = ''
    email: str = ''
    
    redis_host: str = ''
    redis_port: int = 0
    
    aws_access_key_id: str = ''
    aws_secret_access_key: str = ''
    aws_bucket_name: str = ''
    aws_endpoint_url: str = ''

    db_pool_size: int = 20
    db_max_overflow: int = 30
    db_pool_timeout: int = 30
    db_command_timeout: int = 60
    
    google_client_key: str = ''
    google_client_secret: str = ''
    
    front_end_domain: str = ''
    
    class Config:
        env_file = ".env.production"
        extra = "ignore"

