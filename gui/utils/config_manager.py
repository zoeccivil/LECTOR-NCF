"""Gestor de configuración para LECTOR-NCF."""
import os
import json
from datetime import datetime
from pathlib import Path


class ConfigManager:
    CONFIG_FILE = "config.json"
    
    DEFAULT_CONFIG = {
        "firebase": {
            "credentials_path": "",
            "project_id": "",
            "database_url": "https://facot-app-default-rtdb.firebaseio.com/",
            "storage_bucket": ""
        },
        "google_cloud": {"credentials_path": ""},
        "twilio": {
            "account_sid": "",
            "auth_token": "",
            "whatsapp_number": ""
        },
        "app": {
            "data_folder": "./data",
            "export_folder": "./data/exports",
            "temp_folder": "./data/temp"
        }
    }
    
    def __init__(self):
        self.config_path = Path(self.CONFIG_FILE)
        self.config = self._load_config()
    
    def _load_config(self):
        if not self.config_path.exists():
            return self.DEFAULT_CONFIG.copy()
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self.DEFAULT_CONFIG.copy()
    
    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except:
            return False
    
    def is_configured(self):
        fb = self.config.get("firebase", {})
        return bool(fb.get("credentials_path")) and os.path.exists(fb.get("credentials_path", ""))
    
    def get_firebase_credentials_path(self):
        return self.config.get("firebase", {}).get("credentials_path", "")
    
    def get_firebase_database_url(self):
        return self.config.get("firebase", {}).get("database_url", "")


config_manager = ConfigManager()
