"""
Configuración de la aplicación usando Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./business_security.db"
    
    # PostgreSQL components (alternativo)
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_DB: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App
    APP_NAME: str = "Business Security API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS - formato: separado por comas
    ALLOWED_ORIGINS: str = "http://localhost:4000,http://localhost:4200,http://localhost:8100,http://localhost:3000"
    
    # Login Security
    MAX_LOGIN_ATTEMPTS: int = 3
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convierte ALLOWED_ORIGINS de string a lista"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
