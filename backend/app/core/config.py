from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API Configuration
    anthropic_api_key: str
    openai_api_key: str = ""
    
    # Database Configuration
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    
    # Application Settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AWS Configuration
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket_name: str = ""
    
    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # CORS Settings
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # File Upload Settings
    max_file_size_mb: int = 50
    allowed_image_types: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]
    allowed_document_types: List[str] = ["pdf", "docx", "txt"]
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        if isinstance(self.allowed_origins, str):
            return [origin.strip() for origin in self.allowed_origins.split(",")]
        return self.allowed_origins

settings = Settings()