"""
API Configuration

Loads configuration from environment variables with validation.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = Field(default="AgenticAI", env="APP_NAME")
    APP_ENV: str = Field(default="development", env="APP_ENV")
    APP_DEBUG: bool = Field(default=True, env="APP_DEBUG")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    APP_HOST: str = Field(default="0.0.0.0", env="APP_HOST")
    APP_PORT: int = Field(default=8000, env="APP_PORT")
    
    # API
    API_PREFIX: str = Field(default="/api/v1", env="API_PREFIX")
    API_RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="API_RATE_LIMIT_PER_MINUTE")
    
    # Security
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(default="jwt-secret-key-change-in-production", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="API_CORS_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://agenticai:password@localhost:5432/agenticai_db",
        env="DATABASE_URL"
    )
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    SENTRY_DSN: str = Field(default="", env="SENTRY_DSN")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    
    # LLM Providers
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = Field(default="", env="ANTHROPIC_API_KEY")
    
    # Vector DB
    VECTOR_DB_PROVIDER: str = Field(default="chroma", env="VECTOR_DB_PROVIDER")
    
    # Feature Flags
    FEATURE_LLM_AGENTS: bool = Field(default=True, env="FEATURE_LLM_AGENTS")
    FEATURE_VECTOR_MEMORY: bool = Field(default=True, env="FEATURE_VECTOR_MEMORY")
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from comma-separated string."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
