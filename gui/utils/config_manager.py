"""
Gestor de configuración para LECTOR-NCF.
Maneja la lectura/escritura del archivo config.json.
"""

import os
import json
from typing import Dict, Any
from datetime import datetime
from pathlib import Path


class ConfigManager:
    """
    Gestor centralizado de configuración.
    
    Maneja:
    - Lectura/escritura de config.json
    - Validación de credenciales
    - Valores por defecto
    """
    
    CONFIG_FILE = "config.json"
    
    DEFAULT_CONFIG = {
        "firebase": {
            "credentials_path": "",
            "project_id": "",
            "database_url": "https://facot-app-default-rtdb.firebaseio.com/",
            "storage_bucket": ""
        },
        "google_cloud": {
            "credentials_path": ""
        },
        "twilio": {
            "account_sid": "",
            "auth_token": "",
            "whatsapp_number": ""
        },
        "app": {
            "data_folder": "./data",
            "export_folder": "./data/exports",
            "temp_folder": "./data/temp"
        },
        "last_updated": ""
    }
    
    def __init__(self):
        self.config_path = Path(self.CONFIG_FILE)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde el archivo JSON."""
        if not self.config_path.exists():
            return self._deep_copy_config(self.DEFAULT_CONFIG)
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return self._merge_with_defaults(config)
        except Exception as e:
            print(f"[CONFIG] Error cargando config: {e}")
            return self._deep_copy_config(self.DEFAULT_CONFIG)
    
    def _deep_copy_config(self, config: Dict) -> Dict:
        """Copia profunda del diccionario de configuración."""
        import copy
        return copy.deepcopy(config)
    
    def _merge_with_defaults(self, config: Dict) -> Dict:
        """Mezcla config cargada con defaults para agregar campos nuevos."""
        merged = self._deep_copy_config(self.DEFAULT_CONFIG)
        for section, values in config.items():
            if section in merged and isinstance(values, dict):
                merged[section].update(values)
            else:
                merged[section] = values
        return merged
    
    def save(self) -> bool:
        """Guarda la configuración actual en el archivo JSON."""
        try:
            self.config["last_updated"] = datetime.now().isoformat()
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            print(f"[CONFIG] Configuración guardada en {self.config_path.absolute()}")
            return True
        except Exception as e:
            print(f"[CONFIG] Error guardando config: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Verifica si las configuraciones mínimas están completas."""
        firebase = self.config.get("firebase", {})
        
        cred_path = firebase.get("credentials_path", "")
        db_url = firebase.get("database_url", "")
        
        # Validar que existan los campos y el archivo
        if not cred_path or not db_url:
            return False
        
        return os.path.exists(cred_path)
    
    # Getters para Firebase
    def get_firebase_credentials_path(self) -> str:
        return self.config.get("firebase", {}).get("credentials_path", "")
    
    def get_firebase_database_url(self) -> str:
        return self.config.get("firebase", {}).get("database_url", "")
    
    def get_firebase_storage_bucket(self) -> str:
        return self.config.get("firebase", {}).get("storage_bucket", "")
    
    def get_firebase_project_id(self) -> str:
        return self.config.get("firebase", {}).get("project_id", "")
    
    # Getters para Google Cloud
    def get_google_cloud_credentials_path(self) -> str:
        gc_path = self.config.get("google_cloud", {}).get("credentials_path", "")
        # Si no hay credenciales de Google Cloud, usar las de Firebase
        if not gc_path:
            return self.get_firebase_credentials_path()
        return gc_path
    
    # Getters para Twilio
    def get_twilio_account_sid(self) -> str:
        return self.config.get("twilio", {}).get("account_sid", "")
    
    def get_twilio_auth_token(self) -> str:
        return self.config.get("twilio", {}).get("auth_token", "")
    
    def get_twilio_whatsapp_number(self) -> str:
        return self.config.get("twilio", {}).get("whatsapp_number", "")
    
    # Getters para App
    def get_data_folder(self) -> str:
        return self.config.get("app", {}).get("data_folder", "./data")
    
    def get_export_folder(self) -> str:
        return self.config.get("app", {}).get("export_folder", "./data/exports")
    
    def get_temp_folder(self) -> str:
        return self.config.get("app", {}).get("temp_folder", "./data/temp")
    
    # Setters
    def update_firebase_config(self, credentials_path: str, project_id: str, 
                              database_url: str, storage_bucket: str):
        """Actualiza configuración de Firebase."""
        self.config["firebase"]["credentials_path"] = credentials_path
        self.config["firebase"]["project_id"] = project_id
        self.config["firebase"]["database_url"] = database_url
        self.config["firebase"]["storage_bucket"] = storage_bucket
    
    def update_google_cloud_config(self, credentials_path: str):
        """Actualiza configuración de Google Cloud."""
        self.config["google_cloud"]["credentials_path"] = credentials_path
    
    def update_twilio_config(self, account_sid: str, auth_token: str, whatsapp_number: str):
        """Actualiza configuración de Twilio."""
        self.config["twilio"]["account_sid"] = account_sid
        self.config["twilio"]["auth_token"] = auth_token
        self.config["twilio"]["whatsapp_number"] = whatsapp_number
    
    def update_app_config(self, data_folder: str, export_folder: str, temp_folder: str):
        """Actualiza configuración de rutas de la app."""
        self.config["app"]["data_folder"] = data_folder
        self.config["app"]["export_folder"] = export_folder
        self.config["app"]["temp_folder"] = temp_folder


# Singleton global
config_manager = ConfigManager()