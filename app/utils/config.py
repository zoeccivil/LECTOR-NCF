"""
Configuration management for LECTOR-NCF application
"""
from pydantic_settings import BaseSettings
from typing import Optional
import json
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from config.json and environment variables"""
    
    # Google Cloud Vision
    google_application_credentials: Optional[str] = None
    google_cloud_project_id: Optional[str] = None
    
    # Firebase
    firebase_credentials_path: Optional[str] = None
    firebase_project_id: Optional[str] = None
    firebase_database_url: Optional[str] = None
    firebase_storage_bucket: Optional[str] = None
    
    # Twilio WhatsApp
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_whatsapp_number: str = "whatsapp:+14155238886"
    twilio_webhook_url: Optional[str] = None
    
    # Export Configuration
    export_format: str = "both"  # csv, json, or both
    csv_delimiter: str = ","
    timezone: str = "America/Santo_Domingo"
    
    # Application Configuration
    debug: bool = False
    log_level: str = "INFO"
    max_image_size_mb: int = 10
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        """Initialize settings and load from config.json"""
        super().__init__(**kwargs)
        self._load_from_config_json()
    
    def _load_from_config_json(self):
        """Load configuration from config.json file or environment variables"""
        import os
        
        # ✅ Prioridad 1: Variables de entorno (para Render)
        env_firebase_creds = os.environ.get('FIREBASE_CREDENTIALS_PATH')
        env_google_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        env_firebase_db = os.environ.get('FIREBASE_DATABASE_URL')
        env_twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        env_twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
        env_twilio_number = os.environ.get('TWILIO_WHATSAPP_NUMBER')
        
        if env_firebase_creds:
            self.firebase_credentials_path = env_firebase_creds
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
        
        # Si ya hay valores de variables de entorno, no leer config.json
        if env_firebase_creds and env_google_creds:
            return
        
        # ✅ Prioridad 2: config.json (para desarrollo local)
        config_path = Path("config.json")
        
        if not config_path.exists():
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Cargar desde config.json si no hay env vars
            firebase = config.get('firebase', {})
            if firebase and not env_firebase_creds:
                self.firebase_credentials_path = firebase.get('credentials_path')
                self.firebase_project_id = firebase.get('project_id')
                self.firebase_database_url = firebase.get('database_url')
                self.firebase_storage_bucket = firebase.get('storage_bucket')
            
            google_cloud = config.get('google_cloud', {})
            gc_creds = google_cloud.get('credentials_path')
            
            if gc_creds and not env_google_creds:
                self.google_application_credentials = gc_creds
            elif self.firebase_credentials_path and not env_google_creds:
                self.google_application_credentials = self.firebase_credentials_path
            
            twilio = config.get('twilio', {})
            if twilio and not env_twilio_sid:
                self.twilio_account_sid = twilio.get('account_sid')
                self.twilio_auth_token = twilio.get('auth_token')
                if twilio.get('whatsapp_number'):
                    self.twilio_whatsapp_number = twilio.get('whatsapp_number')
            
        except Exception as e:
            print(f"[CONFIG] Warning: Could not load config.json: {e}")


# Global settings instance
settings = Settings()