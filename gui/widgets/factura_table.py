"""
Factura table widget
"""
from PyQt6.QtWidgets import (QTableWidget, QTableWidgetItem, QPushButton, 
                             QWidget, QHBoxLayout, QLabel)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor


class StatusBadge(QLabel):
    """Status badge widget"""
    
    def __init__(self, status: str, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(24)
        self.set_status(status)
    
    def set_status(self, status: str):
        """Set badge status and styling"""
        if status == "exportada":
            self.setText("Exportada")
            self.setStyleSheet("""
                background-color: #9E9E9E;
                color: white;
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            """)
        elif status == "revisada":
            self.setText("Revisada")
            self.setStyleSheet("""
                background-color: #4CAF50;
                color: white;
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            """)
        else:  # pendiente
            self.setText("Pendiente")
            self.setStyleSheet("""
                background-color: #FFC107;
                color: #212121;
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            """)


class ActionButtons(QWidget):
    """Action buttons widget for table row"""
    
    edit_clicked = pyqtSignal()
    delete_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Edit button
        self.edit_btn = QPushButton("✏️")
        self.edit_btn.setFixedSize(32, 28)
        self.edit_btn.setToolTip("Editar factura")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #E3F2FD;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #BBDEFB;
            }
        """)
        self.edit_btn.clicked.connect(self.edit_clicked.emit)
        layout.addWidget(self.edit_btn)
        
        # Delete button
        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setFixedSize(32, 28)
        self.delete_btn.setToolTip("Eliminar factura")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFEBEE;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FFCDD2;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_clicked.emit)
        layout.addWidget(self.delete_btn)
        
        layout.addStretch()


class FacturaTable(QTableWidget):
    """Table widget for displaying facturas"""
    
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
        # Setup columns
        headers = ["NCF", "RNC", "Razón Social", "Fecha", "Total", "Estado", "Acciones"]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # Column widths
        self.setColumnWidth(0, 140)  # NCF
        self.setColumnWidth(1, 120)  # RNC
        self.setColumnWidth(2, 250)  # Razón Social
        self.setColumnWidth(3, 100)  # Fecha
        self.setColumnWidth(4, 120)  # Total
        self.setColumnWidth(5, 100)  # Estado
        self.setColumnWidth(6, 120)  # Acciones
        
        # Table settings
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        
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
            # NCF
            ncf_item = QTableWidgetItem(factura.get('ncf', ''))
            ncf_item.setFlags(ncf_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 0, ncf_item)
            
            # RNC
            rnc_item = QTableWidgetItem(factura.get('rnc', ''))
            rnc_item.setFlags(rnc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 1, rnc_item)
            
            # Razón Social
            razon_item = QTableWidgetItem(factura.get('razon_social', ''))
            razon_item.setFlags(razon_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 2, razon_item)
            
            # Fecha
            fecha_item = QTableWidgetItem(factura.get('fecha_emision', ''))
            fecha_item.setFlags(fecha_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 3, fecha_item)
            
            # Total
            total = factura.get('total', 0) or 0
            total_item = QTableWidgetItem(f"DOP {total:,.2f}")
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 4, total_item)
            
            # Status badge
            status = self._get_status(factura)
            badge = StatusBadge(status)
            self.setCellWidget(row, 5, badge)
            
            # Action buttons
            actions = ActionButtons()
            actions.edit_clicked.connect(
                lambda _, r=row: self._on_edit_clicked(r)
            )
            actions.delete_clicked.connect(
                lambda _, r=row: self._on_delete_clicked(r)
            )
            self.setCellWidget(row, 6, actions)
    
    def _get_status(self, factura: dict) -> str:
        """Determine factura status"""
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
            status: 'todas', 'pendientes', or 'revisadas'
        """
        for row in range(self.rowCount()):
            if status == 'todas':
                self.setRowHidden(row, False)
            else:
                factura = self.facturas[row]
                factura_status = self._get_status(factura)
                
                if status == 'pendientes':
                    show = factura_status == 'pendiente'
                elif status == 'revisadas':
                    show = factura_status in ['revisada', 'exportada']
                else:
                    show = True
                
                self.setRowHidden(row, not show)
