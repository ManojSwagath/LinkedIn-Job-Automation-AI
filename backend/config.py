"""
Configuration management using Pydantic Settings.
Loads environment variables and provides type-safe configuration.
"""
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "AutoAgentHire"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = Field(default=8000, validation_alias="PORT")  # Support both API_PORT and PORT (for Render)
    API_RELOAD: bool = True
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str
    SYNC_DATABASE_URL: Optional[str] = None
    
    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_BUCKET_NAME: str = "resumes"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Vector Database
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_PERSIST_DIRECTORY: str = "./vector_db/data"
    
    # Pinecone (alternative)
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: Optional[str] = None
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_MAX_TOKENS: int = 4000
    OPENAI_TEMPERATURE: float = 0.7
    
    # Anthropic (alternative)
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # CrewAI
    CREWAI_TELEMETRY: bool = False
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    
    LINKEDIN_OAUTH_CLIENT_ID: Optional[str] = None
    LINKEDIN_OAUTH_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_OAUTH_REDIRECT_URI: Optional[str] = None
    
    # Web Automation
    SELENIUM_HEADLESS: bool = True
    SELENIUM_IMPLICIT_WAIT: int = 10
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_TIMEOUT: int = 30000
    
    # Proxy
    USE_PROXY: bool = False
    PROXY_URL: Optional[str] = None
    
    # Email
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: Optional[str] = None
    NOTIFICATION_EMAIL: Optional[str] = None
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Job Search
    MAX_JOBS_PER_SEARCH: int = 100
    SEARCH_DELAY_SECONDS: int = 2
    MAX_APPLICATIONS_PER_DAY: int = 10
    
    # Feature Flags
    ENABLE_AUTO_APPLY: bool = False
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    ENABLE_DAILY_REPORTS: bool = True
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Encryption
    ENCRYPTION_KEY: Optional[str] = None
    
    # Frontend
    STREAMLIT_PORT: int = 8501
    REACT_APP_API_URL: str = "http://localhost:8000"

    # CORS - stored as comma-separated string in .env, parsed to list
    # Include both localhost and 127.0.0.1 for dev servers (Vite often runs on 127.0.0.1).
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://127.0.0.1:8080,http://localhost:8501"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string to list."""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_RESUME_EXTENSIONS: str = "pdf,docx,txt"
    FILE_STORAGE_TYPE: str = "local"  # local, supabase, s3
    
    # AWS S3 (optional)
    AWS_S3_BUCKET_NAME: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse ALLOWED_RESUME_EXTENSIONS string to list."""
        if isinstance(self.ALLOWED_RESUME_EXTENSIONS, list):
            return self.ALLOWED_RESUME_EXTENSIONS
        return [ext.strip() for ext in self.ALLOWED_RESUME_EXTENSIONS.split(",") if ext.strip()]

    # Optional fields present in .env but not strictly required
    LLAMA_MODEL_PATH: Optional[str] = None
    LINKEDIN_EMAIL: Optional[str] = None
    LINKEDIN_PASSWORD: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # Logging
    LOG_FILE_PATH: str = "data/logs/app.log"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "30 days"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        # Ignore extra environment variables that are not declared on the model
        extra = "ignore"


# Global settings instance
try:
    settings = Settings()  # type: ignore[call-arg]
except Exception as e:
    # If environment parsing/validation fails (common during local dev),
    # fall back to a minimal, safe Settings object constructed from
    # environment variables or sensible defaults so the app can start.
    import os
    print("Warning: Settings validation failed, falling back to minimal defaults:", e)
    settings = Settings.model_construct(  # Use model_construct instead of construct
        APP_NAME=os.environ.get("APP_NAME", "AutoAgentHire"),
        APP_ENV=os.environ.get("APP_ENV", "development"),
        DEBUG=os.environ.get("DEBUG", "True") in ["True", "true", "1"],
        LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"),
        API_HOST=os.environ.get("API_HOST", "0.0.0.0"),
        API_PORT=int(os.environ.get("API_PORT", 8000)),
        API_RELOAD=False,
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret"),
        DATABASE_URL=os.environ.get("DATABASE_URL", "sqlite:///./data/autoagenthire.db"),
        OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY", "test-key"),
        CORS_ORIGINS=os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://localhost:8501"),
        ALLOWED_RESUME_EXTENSIONS=os.environ.get("ALLOWED_RESUME_EXTENSIONS", "pdf,docx,txt"),
    )
