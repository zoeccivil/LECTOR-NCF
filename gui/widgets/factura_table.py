"""
Factura table widget - Redesigned
"""
from PyQt6.QtWidgets import (QTableWidget, QTableWidgetItem, QPushButton, 
                             QWidget, QHBoxLayout, QLabel)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QColor
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gui.utils.icon_helper import IconHelper
from gui.utils.theme import COLORS, FONTS, SPACING, RADIUS
from gui.widgets.components import StatusBadge


class ActionButtons(QWidget):
    """Action buttons widget for table row with SVG icons"""
    
    edit_clicked = pyqtSignal()
    delete_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING['XS'], SPACING['XS'], SPACING['XS'], SPACING['XS'])
        layout.setSpacing(SPACING['XS'])
        
        # Edit button with SVG icon
        self.edit_btn = QPushButton()
        self.edit_btn.setIcon(IconHelper.get_icon('edit', COLORS['PRIMARY'], 16))
        self.edit_btn.setIconSize(QSize(16, 16))
        self.edit_btn.setFixedSize(32, 32)
        self.edit_btn.setToolTip("Editar factura")
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['PRIMARY_LIGHT']};
                border: none;
                border-radius: {RADIUS['SMALL']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['PRIMARY']};
            }}
        """)
        self.edit_btn.clicked.connect(self.edit_clicked.emit)
        layout.addWidget(self.edit_btn)
        
        # Delete button with SVG icon
        self.delete_btn = QPushButton()
        self.delete_btn.setIcon(IconHelper.get_icon('delete', COLORS['ERROR'], 16))
        self.delete_btn.setIconSize(QSize(16, 16))
        self.delete_btn.setFixedSize(32, 32)
        self.delete_btn.setToolTip("Eliminar factura")
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FEE2E2;
                border: none;
                border-radius: {RADIUS['SMALL']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['ERROR']};
            }}
        """)
        self.delete_btn.clicked.connect(self.delete_clicked.emit)
        layout.addWidget(self.delete_btn)
        
        layout.addStretch()


class FacturaTable(QTableWidget):
    """Table widget for displaying facturas - Redesigned with numbering and modern UI"""
    
    factura_double_clicked = pyqtSignal(str, str)  # empresa_id, factura_id
    factura_edit_clicked = pyqtSignal(str, str)    # empresa_id, factura_id
    factura_delete_clicked = pyqtSignal(str, str)  # empresa_id, factura_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.facturas = []
        self.empresa_id = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize table UI"""
        # Setup columns with numbering column
        headers = ["#", "NCF", "RNC", "Razón Social", "Fecha", "Total", "Estado", "Acciones"]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # Column widths
        self.setColumnWidth(0, 50)   # #
        self.setColumnWidth(1, 140)  # NCF
        self.setColumnWidth(2, 120)  # RNC
        self.setColumnWidth(3, 220)  # Razón Social
        self.setColumnWidth(4, 100)  # Fecha
        self.setColumnWidth(5, 120)  # Total
        self.setColumnWidth(6, 120)  # Estado
        self.setColumnWidth(7, 100)  # Acciones
        
        # Table settings
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        
        # Set minimum row height
        self.verticalHeader().setDefaultSectionSize(48)
        
        # Apply custom styling
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['WHITE']};
                border: 1px solid {COLORS['GRAY_200']};
                border-radius: {RADIUS['MEDIUM']};
                gridline-color: {COLORS['GRAY_100']};
            }}
            QTableWidget::item {{
                padding: {SPACING['MD']}px;
                border-bottom: 1px solid {COLORS['GRAY_100']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['PRIMARY_LIGHT']};
                color: {COLORS['PRIMARY_DARK']};
            }}
            QTableWidget::item:hover {{
                background-color: {COLORS['GRAY_50']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['WHITE']};
                padding: {SPACING['MD']}px;
                border: none;
                border-bottom: 2px solid {COLORS['GRAY_200']};
                font-weight: {FONTS['WEIGHT_SEMIBOLD']};
                color: {COLORS['GRAY_700']};
                font-size: {FONTS['SIZE_CAPTION']};
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """)
        
        # Connect double click
        self.cellDoubleClicked.connect(self._on_double_click)
    
    def set_facturas(self, empresa_id: str, facturas: list):
        """
        Populate table with facturas
        
        Args:
            empresa_id: Empresa document ID
            facturas: List of factura dictionaries
        """
        self.empresa_id = empresa_id
        self.facturas = facturas
        self.setRowCount(len(facturas))
        
        for row, factura in enumerate(facturas):
            # Row number
            num_item = QTableWidgetItem(str(row + 1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num_item.setFlags(num_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            num_item.setForeground(QColor(COLORS['GRAY_700']))
            self.setItem(row, 0, num_item)
            
            # NCF
            ncf_item = QTableWidgetItem(factura.get('ncf', ''))
            ncf_item.setFlags(ncf_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 1, ncf_item)
            
            # RNC
            rnc_item = QTableWidgetItem(factura.get('rnc', ''))
            rnc_item.setFlags(rnc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 2, rnc_item)
            
            # Razón Social
            razon_item = QTableWidgetItem(factura.get('razon_social', ''))
            razon_item.setFlags(razon_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 3, razon_item)
            
            # Fecha
            fecha = factura.get('fecha_emision', '')
            # Try to format date if it's a datetime object
            if hasattr(fecha, 'strftime'):
                fecha = fecha.strftime('%d/%m/%Y')
            fecha_item = QTableWidgetItem(str(fecha))
            fecha_item.setFlags(fecha_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 4, fecha_item)
            
            # Total
            total = factura.get('total', 0) or 0
            total_item = QTableWidgetItem(f"RD$ {total:,.2f}")
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.setItem(row, 5, total_item)
            
            # Status badge using the new component
            status = self._get_status(factura)
            badge = StatusBadge(status)
            badge_container = QWidget()
            badge_layout = QHBoxLayout(badge_container)
            badge_layout.setContentsMargins(0, 0, 0, 0)
            badge_layout.addWidget(badge)
            badge_layout.addStretch()
            self.setCellWidget(row, 6, badge_container)
            
            # Action buttons
            actions = ActionButtons()
            actions.edit_clicked.connect(
                lambda _, r=row: self._on_edit_clicked(r)
            )
            actions.delete_clicked.connect(
                lambda _, r=row: self._on_delete_clicked(r)
            )
            self.setCellWidget(row, 7, actions)
    
    def _get_status(self, factura: dict) -> str:
        """Determine factura status"""
        # Check estado field first (new OCR invoices collection)
        if 'estado' in factura:
            return factura['estado']
        
        # Fall back to old logic for existing invoices
        if factura.get('exportada', False):
            return "exportada"
        elif factura.get('revisada', False):
            return "revisada"
        else:
            return "pendiente"
    
    def _on_double_click(self, row: int, column: int):
        """Handle row double click"""
        if 0 <= row < len(self.facturas):
            factura = self.facturas[row]
            self.factura_double_clicked.emit(self.empresa_id, factura.get('id'))
    
    def _on_edit_clicked(self, row: int):
        """Handle edit button click"""
        if 0 <= row < len(self.facturas):
            factura = self.facturas[row]
            self.factura_edit_clicked.emit(self.empresa_id, factura.get('id'))
    
    def _on_delete_clicked(self, row: int):
        """Handle delete button click"""
        if 0 <= row < len(self.facturas):
            factura = self.facturas[row]
            self.factura_delete_clicked.emit(self.empresa_id, factura.get('id'))
    
    def filter_by_status(self, status: str):
        """
        Filter table by status
        
        Args:
            status: 'todas', 'pendiente', 'revisada', or 'exportada'
        """
        for row in range(self.rowCount()):
            if status == 'todas':
                self.setRowHidden(row, False)
            else:
                factura = self.facturas[row]
                factura_status = self._get_status(factura)
                
                show = (factura_status == status)
                
                self.setRowHidden(row, not show)
