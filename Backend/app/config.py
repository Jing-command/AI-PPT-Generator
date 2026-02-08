"""
AI PPT Generator - Backend Configuration
配置文件管理，支持环境变量
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用配置类
    从环境变量读取，带有默认值
    """
    
    # 应用信息
    APP_NAME: str = "AI PPT Generator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://pptuser:pptpass@localhost:5432/pptdb"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 密码加密
    PASSWORD_BCRYPT_ROUNDS: int = 12
    
    # 文件存储
    STORAGE_TYPE: str = "local"  # local, s3, oss
    STORAGE_LOCAL_PATH: str = "./storage"
    STORAGE_MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 限流配置
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # AI 配置
    DEFAULT_AI_PROVIDER: str = "openai"
    AI_REQUEST_TIMEOUT: int = 60
    AI_MAX_RETRIES: int = 3
    
    # 任务队列
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # 日志
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json, text
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例
    使用 lru_cache 确保只加载一次
    """
    return Settings()


# 全局配置实例
settings = get_settings()
