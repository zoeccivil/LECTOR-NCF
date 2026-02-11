"""
Configuration management for LECTOR-NCF application
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Google Cloud Vision
    google_application_credentials: str = "credentials/google-cloud-vision.json"
    google_cloud_project_id: Optional[str] = None
    
    # Twilio WhatsApp
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_whatsapp_number: str = "whatsapp:+14155238886"
    twilio_webhook_url: Optional[str] = None
    
    # Export Configuration
    export_format: str = "both"  # csv, json, or both
    csv_delimiter: str = ","
    timezone: str = "America/Santo_Domingo"
    
    # Firebase (Optional)
    firebase_credentials: Optional[str] = None
    firebase_database_url: Optional[str] = None
    
    # Application Configuration
    debug: bool = False
    log_level: str = "INFO"
    max_image_size_mb: int = 10
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
