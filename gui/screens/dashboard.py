"""
Dashboard screen - Main screen with empresa list and factura table - Redesigned
"""
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, 
                             QPushButton, QTabWidget, QMessageBox,
                             QLabel, QFrame)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QIcon
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gui.widgets import EmpresaList, FacturaTable
from gui.utils import FirebaseWorkerPool
from app.firebase_handler import firebase_handler


class DashboardScreen(QWidget):
    """Main dashboard screen - Redesigned with tabs and modern UI"""
    
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
        
        # Left sidebar (220px fixed)
        self.empresa_list = EmpresaList()
        self.empresa_list.setFixedWidth(220)
        self.empresa_list.empresa_selected.connect(self._on_empresa_selected)
        main_layout.addWidget(self.empresa_list)
        
        # Right content area
        content = QWidget()
        content.setStyleSheet("background-color: #F9FAFB;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(24)
        
        # Header with title and tabs
        header = self._create_header()
        content_layout.addWidget(header)
        
        # Tab widget for different states
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: transparent;
            }
            QTabBar::tab {
                background-color: transparent;
                color: #6B7280;
                padding: 12px 24px;
                border: none;
                border-bottom: 3px solid transparent;
                font-size: 14px;
                font-weight: 500;
                margin-right: 8px;
            }
            QTabBar::tab:selected {
                color: #2563EB;
                border-bottom: 3px solid #2563EB;
                font-weight: 600;
            }
            QTabBar::tab:hover {
                color: #1E40AF;
                background-color: #F3F4F6;
                border-radius: 6px 6px 0 0;
            }
        """)
        
        # Create tabs with tables
        self.tab_todas = self._create_table_tab()
        self.tab_pendientes = self._create_table_tab()
        self.tab_revisadas = self._create_table_tab()
        self.tab_exportadas = self._create_table_tab()
        
        # Add tabs
        self.tabs.addTab(self.tab_todas, "📋 Todas")
        self.tabs.addTab(self.tab_pendientes, "⏱️ Pendientes")
        self.tabs.addTab(self.tab_revisadas, "✓ Revisadas")
        self.tabs.addTab(self.tab_exportadas, "📤 Exportadas")
        
        # Connect tab change
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
        content_layout.addWidget(self.tabs)
        
        main_layout.addWidget(content)
        
        # Load initial data
        self._load_empresas()
    
    def _create_header(self) -> QWidget:
        """Create header with title, search, and export button"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        
        # Title
        title = QLabel("Facturas OCR")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #111827;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Buscar por NCF, RNC o Razón Social...")
        self.search_box.setMinimumWidth(300)
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 10px 16px;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                background-color: #FFFFFF;
                font-size: 13px;
                color: #111827;
            }
            QLineEdit:focus {
                border: 2px solid #2563EB;
                outline: none;
            }
        """)
        self.search_box.textChanged.connect(self._on_search)
        header_layout.addWidget(self.search_box)
        
        # Refresh button (texto simple, no emoji)
        refresh_btn = QPushButton("↻")  # ← Carácter Unicode, no emoji
        refresh_btn.setToolTip("Actualizar datos")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                font-size: 20px;
                color: #374151;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F3F4F6;
                border-color: #9CA3AF;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        # Export button
        export_btn = QPushButton("📤 Exportar")
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
        """)
        export_btn.clicked.connect(self._on_export_clicked)
        header_layout.addWidget(export_btn)
        
        return header
    
    def _create_table_tab(self) -> QWidget:
        """Create a tab containing a factura table"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 16, 0, 0)
        
        # Create table
        table = FacturaTable()
        table.factura_double_clicked.connect(self.factura_selected.emit)
        table.factura_edit_clicked.connect(self.factura_selected.emit)
        table.factura_delete_clicked.connect(self._on_delete_factura)
        
        layout.addWidget(table)
        
        return tab
    
    def _get_active_table(self) -> FacturaTable:
        """Get the currently active table"""
        current_tab = self.tabs.currentWidget()
        if current_tab:
            # Find the FacturaTable in the tab
            for child in current_tab.findChildren(FacturaTable):
                return child
        return None
    
    def _on_tab_changed(self, index: int):
        """Handle tab change"""
        if self.current_empresa_id:
            self._load_facturas_for_tab(index)
    
    def _load_facturas_for_tab(self, tab_index: int):
        """Load facturas based on selected tab"""
        if not self.current_empresa_id:
            return
        
        # Map tab index to status filter
        status_map = {
            0: None,           # Todas
            1: 'pendiente',    # Pendientes
            2: 'revisada',     # Revisadas
            3: 'exportada'     # Exportadas
        }
        
        estado = status_map.get(tab_index)
        
        # Check if OCR method exists, otherwise use regular method
        if hasattr(firebase_handler, 'get_ocr_facturas_by_empresa'):
            # Use OCR invoices collection
            self.worker_pool.execute(
                lambda: firebase_handler.get_ocr_facturas_by_empresa(self.current_empresa_id, estado),
                on_success=self._on_facturas_loaded,
                on_error=self._on_error
            )
        else:
            # Fallback to regular invoices (filter by estado if available)
            self.worker_pool.execute(
                lambda: firebase_handler.get_facturas_by_empresa(self.current_empresa_id),
                on_success=lambda facturas: self._on_facturas_loaded_with_filter(facturas, estado),
                on_error=self._on_error
            )
    
    def _on_facturas_loaded_with_filter(self, facturas: list, estado: str):
        """Handle facturas loaded with manual filtering"""
        if estado:
            # Filter facturas by estado
            filtered = [f for f in facturas if f.get('estado') == estado]
            self._on_facturas_loaded(filtered)
        else:
            self._on_facturas_loaded(facturas)
    
    def _load_empresas(self):
        """Load empresas from Firebase"""
        self.worker_pool.execute(
            firebase_handler.get_empresas,
            on_success=self._on_empresas_loaded,
            on_error=self._on_error
        )
    
    def refresh_data(self):
        """Refresh empresas and facturas data"""
        self._load_empresas()
    
    def _on_empresas_loaded(self, empresas: list):
        """Handle empresas data loaded"""
        self.empresa_list.set_empresas(empresas)
        
        # Auto-select first empresa if available
        if empresas and not self.current_empresa_id:
            first_empresa_id = empresas[0].get('id')
            if first_empresa_id:
                self.current_empresa_id = first_empresa_id
                self._load_facturas_for_tab(self.tabs.currentIndex())
    
    def _on_empresa_selected(self, empresa_id: str):
        """Handle empresa selection"""
        self.current_empresa_id = empresa_id
        self._load_facturas_for_tab(self.tabs.currentIndex())
    
    def _on_facturas_loaded(self, facturas: list):
        """Handle facturas data loaded"""
        self.current_facturas = facturas
        
        # Update current tab's table
        table = self._get_active_table()
        if table and self.current_empresa_id:
            table.set_facturas(self.current_empresa_id, facturas)
    
    def _on_search(self, text: str):
        """Handle search text change"""
        table = self._get_active_table()
        if not table:
            return
        
        search_text = text.lower()
        for row in range(table.rowCount()):
            # Search in NCF (column 1), RNC (column 2), and Razón Social (column 3)
            ncf_item = table.item(row, 1)
            rnc_item = table.item(row, 2)
            razon_item = table.item(row, 3)
            
            show = False
            if ncf_item and search_text in ncf_item.text().lower():
                show = True
            elif rnc_item and search_text in rnc_item.text().lower():
                show = True
            elif razon_item and search_text in razon_item.text().lower():
                show = True
            
            # If search is empty, show all rows
            if not search_text:
                show = True
            
            table.setRowHidden(row, not show)
    
    def _on_export_clicked(self):
        """Handle export button click"""
        if self.current_empresa_id:
            # Verificar que haya facturas revisadas
            if hasattr(firebase_handler, 'get_ocr_facturas_by_empresa'):
                revisadas = firebase_handler.get_ocr_facturas_by_empresa(
                    self.current_empresa_id, 
                    estado='revisada'
                )
                
                if not revisadas:
                    QMessageBox.warning(
                        self,
                        "Sin facturas revisadas",
                        "No hay facturas revisadas para exportar en esta empresa.\n\n"
                        "Por favor, revisa las facturas pendientes primero."
                    )
                    return
            
            # Emitir señal con empresa_id
            self.export_requested.emit(self.current_empresa_id)
        else:
            QMessageBox.warning(
                self, 
                "Advertencia", 
                "Seleccione una empresa primero"
            )
    
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
            # Check if OCR delete method exists
            if hasattr(firebase_handler, 'delete_ocr_factura'):
                delete_method = lambda: firebase_handler.delete_ocr_factura(factura_id)
            else:
                delete_method = lambda: firebase_handler.delete_factura(empresa_id, factura_id)
            
            self.worker_pool.execute(
                delete_method,
                on_success=lambda success: self._on_delete_complete(success),
                on_error=self._on_error
            )
    
    def _on_delete_complete(self, success: bool):
        """Handle delete completion"""
        if success:
            QMessageBox.information(self, "Éxito", "Factura eliminada correctamente")
            # Refresh facturas
            if self.current_empresa_id:
                self._load_facturas_for_tab(self.tabs.currentIndex())
        else:
            QMessageBox.warning(self, "Error", "No se pudo eliminar la factura")
    
    def _on_error(self, error):
        """Handle error"""
        error_msg = str(error) if error else "Error desconocido"
        QMessageBox.critical(self, "Error", f"Error: {error_msg}")