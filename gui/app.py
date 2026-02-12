"""
Main application window for LECTOR-NCF GUI - Redesigned
"""
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui.screens import DashboardScreen, EditorScreen, ExporterScreen
from gui.utils.styles import GLOBAL_STYLES
from gui.utils.icon_helper import IconHelper
from gui.utils.theme import COLORS


class LectorNCFApp(QMainWindow):
    """Main application window - Redesigned with modern theme"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LECTOR-NCF - Gestión de Facturas OCR")
        
        # Set window icon
        try:
            icon = IconHelper.get_icon('ocr', COLORS['PRIMARY'], 48)
            self.setWindowIcon(icon)
        except:
            pass  # Icon might not be available yet
        
        # Set minimum size and default size
        self.setMinimumSize(1200, 700)
        self.resize(1400, 900)
        
        # Apply global stylesheet
        self.setStyleSheet(GLOBAL_STYLES)
        
        # Stacked widget for navigation
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create screens
        self.dashboard = DashboardScreen()
        self.editor = EditorScreen()
        self.exporter = ExporterScreen()
        
        # Add to stack
        self.stacked_widget.addWidget(self.dashboard)
        self.stacked_widget.addWidget(self.editor)
        self.stacked_widget.addWidget(self.exporter)
        
        # Connect signals
        self.dashboard.factura_selected.connect(self.open_editor)
        self.dashboard.export_requested.connect(self.open_exporter)
        self.editor.back_requested.connect(self.show_dashboard)
        self.exporter.back_requested.connect(self.show_dashboard)
        
        # Show dashboard
        self.show_dashboard()
    
    def show_dashboard(self):
        """Show dashboard screen"""
        self.stacked_widget.setCurrentWidget(self.dashboard)
        self.dashboard.refresh_data()
    
    def open_editor(self, empresa_id: str, factura_id: str):
        """
        Open editor screen
        
        Args:
            empresa_id: Empresa document ID
            factura_id: Factura document ID
        """
        self.editor.load_factura(empresa_id, factura_id)
        self.stacked_widget.setCurrentWidget(self.editor)
    
    def open_exporter(self, empresa_id: str):
        """
        Open exporter screen
        
        Args:
            empresa_id: Empresa document ID
        """
        self.exporter.load_empresa(empresa_id)
        self.stacked_widget.setCurrentWidget(self.exporter)
