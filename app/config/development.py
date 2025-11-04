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
    
    description : str = '''
    ## 🔧 개발 자료
    - [ERD 다이어그램](https://www.erdcloud.com/d/KNgfev2afc4PpbBiW)
    - [아키텍처 구조도](https://drive.google.com/file/d/1h4NaN3dCZtZamfisBrnLudJk-so3z94c/view?usp=sharing)
    '''
    
    class Config:
        env_file = ".env"

