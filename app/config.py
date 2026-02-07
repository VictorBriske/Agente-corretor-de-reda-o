"""
Configurações da aplicação
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Configurações gerais da aplicação"""
    
    # Ambiente
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Socratis"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:4200",  # Angular default port
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4200",  # Angular default port
        "http://127.0.0.1:8000"
    ]
    
    # Segurança
    SECRET_KEY: str = "seu-secret-key-aqui-mude-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LLM_PROVIDER: str = "openai" 
    LLM_MODEL: str = "gpt-4o"  
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4000
    
    # Database PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/info_aplicada"
    )
    
    # Limites por plano
    FREE_TIER_DAILY_LIMIT: int = 5
    PREMIUM_TIER_DAILY_LIMIT: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

