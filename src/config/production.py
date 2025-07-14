import os
from typing import Optional

class ProductionConfig:
    """Production configuration settings"""
    
    # Domain and URLs
    DOMAIN: str = os.getenv("DOMAIN", "localhost")
    API_BASE_URL: str = f"https://api.{DOMAIN}" if DOMAIN != "localhost" else "http://localhost:8000"
    FRONTEND_URL: str = f"https://{DOMAIN}" if DOMAIN != "localhost" else "http://localhost:8501"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/cinema_action.db")
    
    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "your-32-char-encryption-key")
    
    # RunPod Configuration
    RUNPOD_API_KEY: Optional[str] = os.getenv("RUNPOD_API_KEY")
    RUNPOD_ENDPOINT: Optional[str] = os.getenv("RUNPOD_ENDPOINT")
    
    # Payment Processing
    STRIPE_PUBLISHABLE_KEY: Optional[str] = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # File Storage
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "cinema-action-generated")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioaccess")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "miniosecret")
    
    # Feature Flags
    ENABLE_LORA_TRAINING: bool = os.getenv("ENABLE_LORA_TRAINING", "true").lower() == "true"
    ENABLE_VIDEO_GENERATION: bool = os.getenv("ENABLE_VIDEO_GENERATION", "true").lower() == "true"
    ENABLE_BATCH_PROCESSING: bool = os.getenv("ENABLE_BATCH_PROCESSING", "true").lower() == "true"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))
    RATE_LIMIT_GENERATIONS_PER_HOUR: int = int(os.getenv("RATE_LIMIT_GENERATIONS_PER_HOUR", "50"))
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
    ALLOWED_EXTENSIONS: set = {'.png', '.jpg', '.jpeg', '.gif', '.mp4', '.mov', '.avi'}
    
    # Email Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    # Analytics
    GOOGLE_ANALYTICS_ID: Optional[str] = os.getenv("GOOGLE_ANALYTICS_ID")
    POSTHOG_API_KEY: Optional[str] = os.getenv("POSTHOG_API_KEY")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # Production flags
    PRODUCTION: bool = os.getenv("PRODUCTION", "false").lower() == "true"
    DEBUG: bool = not PRODUCTION
    
    @classmethod
    def validate_config(cls):
        """Validate production configuration"""
        errors = []
        
        if cls.PRODUCTION:
            if not cls.RUNPOD_API_KEY:
                errors.append("RUNPOD_API_KEY is required in production")
            
            if not cls.RUNPOD_ENDPOINT:
                errors.append("RUNPOD_ENDPOINT is required in production")
            
            if not cls.STRIPE_SECRET_KEY:
                errors.append("STRIPE_SECRET_KEY is required for payments")
            
            if cls.JWT_SECRET == "your-secret-key-change-in-production":
                errors.append("JWT_SECRET must be changed in production")
            
            if not cls.DATABASE_URL.startswith("postgresql://"):
                errors.append("PostgreSQL database required in production")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True

# Initialize configuration
config = ProductionConfig()

# Validate on import if in production
if config.PRODUCTION:
    config.validate_config()