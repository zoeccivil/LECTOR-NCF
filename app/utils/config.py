"""
Configuration settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Settings:
    def __init__(self):
        # Firebase
        self.firebase_credentials = os.environ.get(
            "FIREBASE_CREDENTIALS",
            "credentials/firebase-credentials.json"
        )
        self.firebase_database_url = os.environ.get(
            "FIREBASE_DATABASE_URL",
            "https://facot-app-default-rtdb.firebaseio.com/"
        )
        
        # Google Cloud Vision
        self.google_credentials = os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS",
            "credentials/google-vision-credentials.json"
        )
        
        # Twilio
        self.twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.twilio_whatsapp_number = os.environ.get(
            "TWILIO_WHATSAPP_NUMBER",
            "whatsapp:+14155238886"
        )
        
        # Green-API
        self.greenapi_instance_id = os.environ.get("GREENAPI_INSTANCE_ID")
        self.greenapi_token = os.environ.get("GREENAPI_TOKEN")
        
        # WhatsApp Mode
        self.whatsapp_mode = os.environ.get("WHATSAPP_MODE", "dual")
        
        # Server
        self.port = int(os.environ.get("PORT", 8000))
        self.debug = os.environ.get("DEBUG", "False").lower() == "true"


settings = Settings()