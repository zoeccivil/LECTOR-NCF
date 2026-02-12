"""
Entry point for LECTOR-NCF GUI application - Redesigned
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui.app import LectorNCFApp
<<<<<<< Updated upstream
from gui.utils.styles import GLOBAL_STYLES
=======
from gui.utils import GLOBAL_STYLES
from gui.utils.config_manager import config_manager

from gui.utils.config_manager import config_manager
import os

def apply_config_to_env():
    """Aplica config.json a variables de entorno (para compatibilidad)."""
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config_manager.get_firebase_credentials_path()
    os.environ["FIREBASE_DATABASE_URL"] = config_manager.get_firebase_database_url()
    # Esto es opcional, solo si algún módulo legacy lee env vars


def check_and_load_config():
    """Check if configuration exists and load it"""
    if not config_manager.is_configured():
        from gui.dialogs.config_dialog import ConfigDialog
        
        app_temp = QApplication.instance() or QApplication(sys.argv)
        
        # Show first-time configuration dialog
        dialog = ConfigDialog(None, first_time=True)
        
        if dialog.exec() != ConfigDialog.DialogCode.Accepted:
            QMessageBox.critical(
                None, 
                "Error", 
                "Configuración requerida para ejecutar la aplicación."
            )
            sys.exit(0)
        
        # Reload config after saving
        config_manager.config = config_manager._load_config()
    
    # Set environment variables for Firebase and Google Cloud
    firebase_creds = config_manager.get_firebase_credentials_path()
    if firebase_creds and os.path.exists(firebase_creds):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = firebase_creds
    
    firebase_db_url = config_manager.get_firebase_database_url()
    if firebase_db_url:
        os.environ["FIREBASE_DATABASE_URL"] = firebase_db_url
>>>>>>> Stashed changes


def main():
    """Main entry point"""
    # High DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("LECTOR-NCF")
    app.setApplicationDisplayName("LECTOR-NCF - Gestión de Facturas OCR")
    
    # Set default font (Inter if available, fallback to system font)
    try:
        font = QFont("Inter", 13)
        app.setFont(font)
    except:
        pass  # Use system font if Inter is not available
    
    # Apply global stylesheet
    app.setStyleSheet(GLOBAL_STYLES)
    
    # Create and show main window
    window = LectorNCFApp()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
