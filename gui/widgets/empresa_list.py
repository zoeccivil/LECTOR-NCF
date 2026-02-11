"""
Empresa list widget (sidebar)
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                             QListWidgetItem, QHBoxLayout)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


class EmpresaListItem(QWidget):
    """Custom widget for empresa list item with badge"""
    
    def __init__(self, empresa_data: dict, parent=None):
        super().__init__(parent)
        self.empresa_data = empresa_data
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Empresa name
        name_label = QLabel(empresa_data.get('nombre', 'Sin Nombre'))
        name_label.setStyleSheet("color: #212121; font-weight: 600;")
        layout.addWidget(name_label, 1)
        
        # Badge with count
        total = empresa_data.get('total_facturas', 0)
        badge = QLabel(str(total))
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedSize(30, 20)
        badge.setStyleSheet("""
            background-color: #1976D2;
            color: white;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 600;
        """)
        layout.addWidget(badge)


class EmpresaList(QWidget):
    """Sidebar widget with empresa list"""
    
    empresa_selected = pyqtSignal(str)  # Emits empresa_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.empresas = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #1976D2;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("LECTOR-NCF")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Gestión de Facturas")
        subtitle.setStyleSheet("color: #E3F2FD; font-size: 12px;")
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # List section header
        list_header = QLabel("EMPRESAS")
        list_header.setStyleSheet("""
            padding: 12px 16px;
            color: #757575;
            font-size: 11px;
            font-weight: 600;
            background-color: #F8F9FA;
        """)
        layout.addWidget(list_header)
        
        # Empresa list
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: white;
            }
            QListWidget::item {
                border-bottom: 1px solid #F0F0F0;
            }
        """)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)
    
    def set_empresas(self, empresas: list):
        """
        Populate list with empresas
        
        Args:
            empresas: List of empresa dictionaries
        """
        self.empresas = empresas
        self.list_widget.clear()
        
        for empresa in empresas:
            item = QListWidgetItem(self.list_widget)
            widget = EmpresaListItem(empresa)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
    
    def _on_item_clicked(self, item):
        """Handle item click"""
        index = self.list_widget.row(item)
        if 0 <= index < len(self.empresas):
            empresa_id = self.empresas[index].get('id')
            if empresa_id:
                self.empresa_selected.emit(empresa_id)
