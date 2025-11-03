import os
from .development import DevelopmentConfig
from .production import ProductionConfig

def get_settings():
    """환경에 따라 적절한 설정 객체 반환"""
    # 터미널에서 직접 설정한 환경변수 읽기
    env = os.getenv("ENV", "development")
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
    }
    
    config_class = config_map.get(env)
    if not config_class:
        raise ValueError(f"Unknown environment: {env}. Use 'development' or 'production'")
    
    return config_class()

# 전역 settings 객체
settings = get_settings()