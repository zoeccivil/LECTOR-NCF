"""
Configuration management for LECTOR-NCF application
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


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
    firebase_credentials_path: Optional[str] = None
    
    # Application Configuration
    debug: bool = False
    log_level: str = "INFO"
    max_image_size_mb: int = 10
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def _load_from_config_json(self):
        """
        Load configuration from environment variables with priority over config.json
        This method is called after initialization to ensure environment variables take precedence
        """
        import os
        
        # Prioridad 1: Variables de entorno (para Render)
        env_firebase_creds = os.environ.get('FIREBASE_CREDENTIALS_PATH')
        env_google_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        env_firebase_db = os.environ.get('FIREBASE_DATABASE_URL')
        env_twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        env_twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
        env_twilio_number = os.environ.get('TWILIO_WHATSAPP_NUMBER')
        
        if env_firebase_creds:
            self.firebase_credentials_path = env_firebase_creds
            self.firebase_credentials = env_firebase_creds
        if env_google_creds:
            self.google_application_credentials = env_google_creds
        if env_firebase_db:
            self.firebase_database_url = env_firebase_db
        if env_twilio_sid:
            self.twilio_account_sid = env_twilio_sid
        if env_twilio_token:
            self.twilio_auth_token = env_twilio_token
        if env_twilio_number:
            self.twilio_whatsapp_number = env_twilio_number
        
        # Si hay valores de env vars, no leer config.json
        if env_firebase_creds and env_google_creds:
            return


# Global settings instance
settings = Settings()
# Load environment variables with priority
settings._load_from_config_json()
