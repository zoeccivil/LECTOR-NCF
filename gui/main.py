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
from gui.utils.styles import GLOBAL_STYLES


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
