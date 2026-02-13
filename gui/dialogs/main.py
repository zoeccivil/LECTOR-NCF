"""
Entry point for LECTOR-NCF GUI application.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt


def check_and_load_config():
    """
    Verifica si la configuración existe y es válida.
    Si no, muestra el diálogo de configuración.
    """
    from gui.utils.config_manager import config_manager
    
    if not config_manager.is_configured():
        # Mostrar diálogo de configuración
        from gui.dialogs.config_dialog import ConfigDialog
        
        # Crear QApplication temporal si no existe
        app_temp = QApplication.instance()
        if app_temp is None:
            app_temp = QApplication(sys.argv)
        
        # Mostrar diálogo
        dialog = ConfigDialog(None, first_time=True)
        result = dialog.exec()
        
        if result != ConfigDialog.DialogCode.Accepted:
            QMessageBox.critical(
                None,
                "Configuración requerida",
                "No se puede iniciar LECTOR-NCF sin configuración.\n\n"
                "La aplicación se cerrará."
            )
            sys.exit(0)
        
        # Reload config después de guardar
        config_manager.config = config_manager._load_config()
    
    # Aplicar configuración a variables de entorno (para compatibilidad con código legacy)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config_manager.get_firebase_credentials_path()
    os.environ["FIREBASE_DATABASE_URL"] = config_manager.get_firebase_database_url()
    
    print(f"[CONFIG] Firebase credentials: {config_manager.get_firebase_credentials_path()}")
    print(f"[CONFIG] Database URL: {config_manager.get_firebase_database_url()}")


def main():
    """Main entry point"""
    # Verificar configuración ANTES de crear la app principal
    check_and_load_config()
    
    # High DPI support
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    
    from gui.app import LectorNCFApp
    from gui.utils.styles import GLOBAL_STYLES
    
    app = QApplication(sys.argv)
    app.setApplicationName("LECTOR-NCF")
    app.setStyleSheet(GLOBAL_STYLES)
    
    window = LectorNCFApp()
    window.setMinimumSize(1280, 720)
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()