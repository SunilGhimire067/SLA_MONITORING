from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ITSM Platform"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "mysql+aiomysql://itsm_user:itsm_password_123@localhost:3306/itsm_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "change-me-to-a-random-64-char-string-for-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:80", "http://localhost"]

    # Email (Phase 3)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    # Teams (Phase 3)
    TEAMS_WEBHOOK_URL: str = ""

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
