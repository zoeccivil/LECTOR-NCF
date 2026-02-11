"""
Dashboard screen - Main screen with empresa list and factura table
"""
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, 
                             QPushButton, QButtonGroup, QRadioButton, QMessageBox,
                             QLabel, QFrame)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gui.widgets import EmpresaList, FacturaTable
from gui.utils import FirebaseWorkerPool
from app.firebase_handler import firebase_handler


class DashboardScreen(QWidget):
    """Main dashboard screen"""
    
    factura_selected = pyqtSignal(str, str)  # empresa_id, factura_id
    export_requested = pyqtSignal(str)       # empresa_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_empresa_id = None
        self.current_facturas = []
        self.worker_pool = FirebaseWorkerPool()
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components"""
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left sidebar (250px fixed)
        self.empresa_list = EmpresaList()
        self.empresa_list.setFixedWidth(250)
        self.empresa_list.empresa_selected.connect(self._on_empresa_selected)
        main_layout.addWidget(self.empresa_list)
        
        # Right content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(16)
        
        # Header
        header = QLabel("Facturas")
        header.setProperty("class", "title")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #212121;")
        content_layout.addWidget(header)
        
        # Filter bar
        filter_bar = self._create_filter_bar()
        content_layout.addWidget(filter_bar)
        
        # Factura table
        self.factura_table = FacturaTable()
        self.factura_table.factura_double_clicked.connect(self.factura_selected.emit)
        self.factura_table.factura_edit_clicked.connect(self.factura_selected.emit)
        self.factura_table.factura_delete_clicked.connect(self._on_delete_factura)
        content_layout.addWidget(self.factura_table)
        
        main_layout.addWidget(content)
    
    def _create_filter_bar(self) -> QWidget:
        """Create filter bar with buttons and search"""
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(12)
        
        # Status filter buttons
        self.filter_group = QButtonGroup()
        
        btn_todas = QRadioButton("Todas")
        btn_todas.setChecked(True)
        btn_todas.toggled.connect(lambda: self._apply_filter("todas"))
        self.filter_group.addButton(btn_todas)
        filter_layout.addWidget(btn_todas)
        
        btn_pendientes = QRadioButton("Pendientes")
        btn_pendientes.toggled.connect(lambda: self._apply_filter("pendientes"))
        self.filter_group.addButton(btn_pendientes)
        filter_layout.addWidget(btn_pendientes)
        
        btn_revisadas = QRadioButton("Revisadas")
        btn_revisadas.toggled.connect(lambda: self._apply_filter("revisadas"))
        self.filter_group.addButton(btn_revisadas)
        filter_layout.addWidget(btn_revisadas)
        
        filter_layout.addSpacing(20)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Buscar por NCF...")
        self.search_box.setMaximumWidth(250)
        self.search_box.textChanged.connect(self._on_search)
        filter_layout.addWidget(self.search_box)
        
        filter_layout.addStretch()
        
        # Export button
        export_btn = QPushButton("📤 Exportar")
        export_btn.setProperty("class", "primary")
        export_btn.setFixedHeight(36)
        export_btn.clicked.connect(self._on_export_clicked)
        filter_layout.addWidget(export_btn)
        
        return filter_widget
    
    def refresh_data(self):
        """Refresh empresas and facturas data"""
        self.worker_pool.execute(
            firebase_handler.get_empresas,
            on_success=self._on_empresas_loaded,
            on_error=self._on_error
        )
    
    def _on_empresas_loaded(self, empresas: list):
        """Handle empresas data loaded"""
        self.empresa_list.set_empresas(empresas)
        
        # Auto-select first empresa if available
        if empresas and not self.current_empresa_id:
            first_empresa_id = empresas[0].get('id')
            if first_empresa_id:
                self._load_facturas(first_empresa_id)
    
    def _on_empresa_selected(self, empresa_id: str):
        """Handle empresa selection"""
        self._load_facturas(empresa_id)
    
    def _load_facturas(self, empresa_id: str):
        """Load facturas for selected empresa"""
        self.current_empresa_id = empresa_id
        self.worker_pool.execute(
            firebase_handler.get_facturas_by_empresa,
            on_success=self._on_facturas_loaded,
            on_error=self._on_error,
            empresa_id
        )
    
    def _on_facturas_loaded(self, facturas: list):
        """Handle facturas data loaded"""
        self.current_facturas = facturas
        if self.current_empresa_id:
            self.factura_table.set_facturas(self.current_empresa_id, facturas)
    
    def _apply_filter(self, status: str):
        """Apply status filter to table"""
        self.factura_table.filter_by_status(status)
    
    def _on_search(self, text: str):
        """Handle search text change"""
        search_text = text.lower()
        for row in range(self.factura_table.rowCount()):
            ncf_item = self.factura_table.item(row, 0)
            if ncf_item:
                ncf = ncf_item.text().lower()
                show = search_text in ncf
                self.factura_table.setRowHidden(row, not show)
    
    def _on_export_clicked(self):
        """Handle export button click"""
        if self.current_empresa_id:
            self.export_requested.emit(self.current_empresa_id)
        else:
            QMessageBox.warning(self, "Advertencia", 
                              "Seleccione una empresa primero")
    
    def _on_delete_factura(self, empresa_id: str, factura_id: str):
        """Handle factura delete request"""
        reply = QMessageBox.question(
            self, 
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar esta factura?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.worker_pool.execute(
                firebase_handler.delete_factura,
                on_success=lambda success: self._on_delete_complete(success),
                on_error=self._on_error,
                empresa_id,
                factura_id
            )
    
    def _on_delete_complete(self, success: bool):
        """Handle delete completion"""
        if success:
            QMessageBox.information(self, "Éxito", "Factura eliminada correctamente")
            # Refresh facturas
            if self.current_empresa_id:
                self._load_facturas(self.current_empresa_id)
        else:
            QMessageBox.warning(self, "Error", "No se pudo eliminar la factura")
    
    def _on_error(self, error_msg: str):
        """Handle error"""
        QMessageBox.critical(self, "Error", f"Error: {error_msg}")
