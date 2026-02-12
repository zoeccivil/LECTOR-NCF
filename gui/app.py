"""
Main application window for LECTOR-NCF GUI
"""
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui.screens import DashboardScreen, EditorScreen, ExporterScreen


class LectorNCFApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LECTOR-NCF - Gestión de Facturas")
        
        # Create menu bar
        self._create_menu_bar()
        
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
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&Archivo")
        exit_action = file_menu.addAction("🚪 Salir")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # Configuration menu
        config_menu = menubar.addMenu("&Configuración")
        config_action = config_menu.addAction("⚙️ Configurar credenciales...")
        config_action.triggered.connect(self._open_config_dialog)
    
    def _open_config_dialog(self):
        """Open configuration dialog"""
        from gui.dialogs.config_dialog import ConfigDialog
        from PyQt6.QtWidgets import QDialog, QMessageBox
        
        dialog = ConfigDialog(self, first_time=False)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(
                self, 
                "Reinicio", 
                "La configuración ha sido guardada. La aplicación se cerrará.\n\n"
                "Por favor, reinicie la aplicación para aplicar los cambios."
            )
            self.close()
