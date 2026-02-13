"""
Factura table widget - Redesigned with row numbering and better styling
"""
from PyQt6.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton, QWidget, QHBoxLayout, QLabel)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QColor, QFont
from typing import List, Dict


class FacturaTable(QTableWidget):
    """Table widget for displaying facturas with modern design"""
    
    factura_double_clicked = pyqtSignal(str, str)  # empresa_id, factura_id
    factura_edit_clicked = pyqtSignal(str, str)
    factura_delete_clicked = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_empresa_id = None
        self.facturas_data = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize table UI"""
        # Set column count
        self.setColumnCount(8)
        
        # Set headers
        headers = ['#', 'NCF', 'RNC', 'RAZÓN SOCIAL', 'FECHA', 'TOTAL', 'ESTADO', 'ACCIONES']
        self.setHorizontalHeaderLabels(headers)
        
        # Configure table
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        
        # ✅ Set row height to 48px (ajustado para centrar mejor)
        self.verticalHeader().setDefaultSectionSize(48)
        
        # Configure headers
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # #
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # NCF
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # RNC
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Razón Social
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Fecha
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Total
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Estado
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)  # Acciones
        
        # Set column widths
        self.setColumnWidth(0, 60)   # # (número)
        self.setColumnWidth(6, 130)  # Estado (aumentado para badges)
        self.setColumnWidth(7, 90)   # Acciones (ajustado para 2 botones)
        
        # Apply styles
        self.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                gridline-color: #F3F4F6;
            }
            
            QTableWidget::item {
                padding: 8px 12px;
                color: #111827;
                font-size: 13px;
                border-bottom: 1px solid #F3F4F6;
            }
            
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E40AF;
            }
            
            QTableWidget::item:hover {
                background-color: #F9FAFB;
            }
            
            QHeaderView::section {
                background-color: #F9FAFB;
                color: #374151;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                font-weight: 600;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            QTableWidget::item:alternate {
                background-color: #FAFAFA;
            }
        """)
        
        # Connect double click
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
    
    def set_facturas(self, empresa_id: str, facturas: List[Dict]):
        """Set facturas data and populate table"""
        self.current_empresa_id = empresa_id
        self.facturas_data = facturas
        self._populate_table()
    
    def _populate_table(self):
        """Populate table with facturas data"""
        self.setRowCount(0)
        
        for idx, factura in enumerate(self.facturas_data):
            row = self.rowCount()
            self.insertRow(row)
            
            # Column 0: Row number
            num_item = QTableWidgetItem(str(idx + 1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num_item.setForeground(QColor('#6B7280'))
            font = num_item.font()
            font.setWeight(QFont.Weight.Bold)
            num_item.setFont(font)
            self.setItem(row, 0, num_item)
            
            # Column 1: NCF
            ncf_item = QTableWidgetItem(factura.get('ncf', ''))
            ncf_item.setForeground(QColor('#2563EB'))
            font_ncf = ncf_item.font()
            font_ncf.setWeight(QFont.Weight.Medium)
            ncf_item.setFont(font_ncf)
            self.setItem(row, 1, ncf_item)
            
            # Column 2: RNC
            rnc_item = QTableWidgetItem(factura.get('rnc', ''))
            rnc_item.setForeground(QColor('#111827'))
            self.setItem(row, 2, rnc_item)
            
            # Column 3: Razón Social
            razon_item = QTableWidgetItem(factura.get('razon_social', ''))
            razon_item.setForeground(QColor('#111827'))
            self.setItem(row, 3, razon_item)
            
            # Column 4: Fecha
            fecha_item = QTableWidgetItem(factura.get('fecha_emision', ''))
            fecha_item.setForeground(QColor('#111827'))
            self.setItem(row, 4, fecha_item)
            
            # Column 5: Total
            total = factura.get('total', 0)
            moneda = factura.get('moneda', 'DOP')
            total_str = f"{moneda} {total:,.2f}" if total else ''
            total_item = QTableWidgetItem(total_str)
            total_item.setForeground(QColor('#111827'))
            font_total = total_item.font()
            font_total.setWeight(QFont.Weight.Bold)
            total_item.setFont(font_total)
            self.setItem(row, 5, total_item)
            
            # Column 6: Estado badge
            estado_widget = self._create_estado_badge(factura.get('estado', 'pendiente'))
            self.setCellWidget(row, 6, estado_widget)
            
            # Column 7: Action buttons
            actions_widget = self._create_action_buttons(factura)
            self.setCellWidget(row, 7, actions_widget)
    
    def _create_estado_badge(self, estado: str) -> QWidget:
        """Create estado badge widget - centered and compact"""
        # ✅ Widget container con altura fija
        widget = QWidget()
        widget.setFixedHeight(48)  # Altura de la fila
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Badge label
        badge = QLabel()
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # ✅ Configure badge based on estado - más compacto
        if estado == 'pendiente':
            badge.setText('⏱ Pendiente')
            badge.setStyleSheet("""
                background-color: #FEF3C7;
                color: #92400E;
                padding: 6px 10px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 600;
            """)
        elif estado == 'revisada':
            badge.setText('✓ Revisada')
            badge.setStyleSheet("""
                background-color: #D1FAE5;
                color: #065F46;
                padding: 6px 10px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 600;
            """)
        elif estado == 'exportada':
            badge.setText('📤 Exportada')
            badge.setStyleSheet("""
                background-color: #E5E7EB;
                color: #374151;
                padding: 6px 10px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 600;
            """)
        else:
            badge.setText(estado.capitalize())
            badge.setStyleSheet("""
                background-color: #F3F4F6;
                color: #6B7280;
                padding: 6px 10px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 600;
            """)
        
        layout.addWidget(badge)
        return widget
    
    def _create_action_buttons(self, factura: Dict) -> QWidget:
        """Create action buttons widget - centered and compact"""
        # ✅ Widget container con altura fija
        widget = QWidget()
        widget.setFixedHeight(48)  # Altura de la fila
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # ✅ Edit button - más pequeño y centrado
        btn_edit = QPushButton()
        btn_edit.setText('✏️')
        btn_edit.setToolTip('Editar factura')
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setFixedSize(30, 30)
        btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #DBEAFE;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #BFDBFE;
            }
            QPushButton:pressed {
                background-color: #93C5FD;
            }
        """)
        btn_edit.clicked.connect(
            lambda: self.factura_edit_clicked.emit(self.current_empresa_id, factura['id'])
        )
        layout.addWidget(btn_edit)
        
        # ✅ Delete button - más pequeño y centrado
        btn_delete = QPushButton()
        btn_delete.setText('🗑️')
        btn_delete.setToolTip('Eliminar factura')
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.setFixedSize(30, 30)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #FEE2E2;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #FECACA;
            }
            QPushButton:pressed {
                background-color: #FCA5A5;
            }
        """)
        btn_delete.clicked.connect(
            lambda: self.factura_delete_clicked.emit(self.current_empresa_id, factura['id'])
        )
        layout.addWidget(btn_delete)
        
        return widget
    
    def _on_item_double_clicked(self, item: QTableWidgetItem):
        """Handle item double click"""
        if not self.current_empresa_id:
            return
        
        row = item.row()
        if row < len(self.facturas_data):
            factura = self.facturas_data[row]
            self.factura_double_clicked.emit(self.current_empresa_id, factura['id'])
    
    def filter_by_status(self, status: str):
        """Filter table by status"""
        for row in range(self.rowCount()):
            if row < len(self.facturas_data):
                factura = self.facturas_data[row]
                estado = factura.get('estado', 'pendiente')
                
                if status == 'all':
                    self.setRowHidden(row, False)
                elif status == 'pending':
                    self.setRowHidden(row, estado != 'pendiente')
                elif status == 'reviewed':
                    self.setRowHidden(row, estado != 'revisada')
    
    def filter_by_text(self, text: str):
        """Filter table by search text"""
        search_text = text.lower()
        
        for row in range(self.rowCount()):
            if row < len(self.facturas_data):
                factura = self.facturas_data[row]
                
                # Search in NCF, RNC, and Razón Social
                ncf = factura.get('ncf', '').lower()
                rnc = factura.get('rnc', '').lower()
                razon = factura.get('razon_social', '').lower()
                
                match = (search_text in ncf or 
                        search_text in rnc or 
                        search_text in razon)
                
                self.setRowHidden(row, not match and len(search_text) > 0)
    
    def clear_table(self):
        """Clear all table data"""
        self.setRowCount(0)
        self.facturas_data = []
        self.current_empresa_id = None