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
from gui.widgets.components import SearchBox, IconButton, EmptyState
from gui.utils import FirebaseWorkerPool
from gui.utils.icon_helper import IconHelper
from gui.utils.theme import COLORS, FONTS, SPACING, RADIUS
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
        content.setStyleSheet(f"background-color: {COLORS['GRAY_50']};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(SPACING['XL'], SPACING['XL'], 
                                         SPACING['XL'], SPACING['XL'])
        content_layout.setSpacing(SPACING['LG'])
        
        # Header with title and tabs
        header = self._create_header()
        content_layout.addWidget(header)
        
        # Tab widget for different states
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: transparent;
            }}
            QTabBar::tab {{
                background-color: transparent;
                color: {COLORS['GRAY_700']};
                padding: {SPACING['MD']}px {SPACING['XL']}px;
                border: none;
                border-bottom: 3px solid transparent;
                font-size: {FONTS['SIZE_BODY']};
                font-weight: {FONTS['WEIGHT_MEDIUM']};
                margin-right: {SPACING['SM']}px;
            }}
            QTabBar::tab:selected {{
                color: {COLORS['PRIMARY']};
                border-bottom: 3px solid {COLORS['PRIMARY']};
                font-weight: {FONTS['WEIGHT_SEMIBOLD']};
            }}
            QTabBar::tab:hover {{
                color: {COLORS['PRIMARY_DARK']};
                background-color: {COLORS['GRAY_100']};
            }}
        """)
        
        # Create tabs
        self.tab_todas = self._create_table_tab()
        self.tab_pendientes = self._create_table_tab()
        self.tab_revisadas = self._create_table_tab()
        self.tab_exportadas = self._create_table_tab()
        
        # Set tab icons
        self.tabs.addTab(self.tab_todas, "📋 Todas")
        self.tabs.addTab(self.tab_pendientes, "⏱️ Pendientes")
        self.tabs.addTab(self.tab_revisadas, "✓ Revisadas")
        self.tabs.addTab(self.tab_exportadas, "📤 Exportadas")
        
        # Connect tab change
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
        content_layout.addWidget(self.tabs)
        
        main_layout.addWidget(content)
    
    def _create_header(self) -> QWidget:
        """Create header with title, search, and export button"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING['LG'])
        
        # Title
        title = QLabel("Facturas OCR")
        title.setStyleSheet(f"""
            font-size: {FONTS['SIZE_HEADING']};
            font-weight: {FONTS['WEIGHT_BOLD']};
            color: {COLORS['GRAY_900']};
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search box
        self.search_box = SearchBox(placeholder="Buscar por NCF, RNC...")
        self.search_box.search_changed.connect(self._on_search)
        header_layout.addWidget(self.search_box)
        
        # Refresh button
        refresh_btn = IconButton('refresh', '', 'Actualizar datos', COLORS['GRAY_700'], 20)
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        # Export button
        export_btn = QPushButton()
        export_btn.setText("  Exportar")
        export_btn.setIcon(IconHelper.get_icon('export', COLORS['WHITE'], 20))
        export_btn.setIconSize(QSize(20, 20))
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['PRIMARY']};
                color: {COLORS['WHITE']};
                border: none;
                border-radius: {RADIUS['MEDIUM']};
                padding: {SPACING['MD']}px {SPACING['XL']}px;
                font-size: {FONTS['SIZE_BODY']};
                font-weight: {FONTS['WEIGHT_SEMIBOLD']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['PRIMARY_DARK']};
            }}
        """)
        export_btn.clicked.connect(self._on_export_clicked)
        header_layout.addWidget(export_btn)
        
        return header
    
    def _create_table_tab(self) -> QWidget:
        """Create a tab containing a factura table"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, SPACING['LG'], 0, 0)
        
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
        
        # Use OCR invoices collection
        self.worker_pool.execute(
            lambda: firebase_handler.get_ocr_facturas_by_empresa(self.current_empresa_id, estado),
            on_success=self._on_facturas_loaded,
            on_error=self._on_error
        )
    
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
            # Search in NCF (column 1) and RNC (column 2)
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
            
            table.setRowHidden(row, not show)
    
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
            # Use OCR invoice delete method
            self.worker_pool.execute(
                lambda: firebase_handler.delete_ocr_factura(factura_id),
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
    
    def _on_error(self, error: Exception):
        """Handle errors"""
        QMessageBox.critical(self, "Error", f"Error: {str(error)}")

        
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
            lambda: firebase_handler.get_facturas_by_empresa(empresa_id),
            on_success=self._on_facturas_loaded,
            on_error=self._on_error
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
                lambda: firebase_handler.delete_factura(empresa_id, factura_id),
                on_success=lambda success: self._on_delete_complete(success),
                on_error=self._on_error
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
