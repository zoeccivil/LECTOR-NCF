"""
Empresa list widget (sidebar) - Redesigned
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                             QListWidgetItem, QHBoxLayout, QGraphicsDropShadowEffect)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QFont, QColor
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gui.utils.icon_helper import IconHelper
from gui.utils.theme import COLORS, FONTS, SPACING, RADIUS


class EmpresaListItem(QWidget):
    """Custom widget for empresa list item with circular badge"""
    
    def __init__(self, empresa_data: dict, parent=None):
        super().__init__(parent)
        self.empresa_data = empresa_data
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING['LG'], SPACING['MD'], SPACING['LG'], SPACING['MD'])
        layout.setSpacing(SPACING['MD'])
        
        # Company icon
        icon_label = QLabel()
        icon_pixmap = IconHelper.get_pixmap('company', 20, COLORS['GRAY_700'])
        icon_label.setPixmap(icon_pixmap)
        layout.addWidget(icon_label)
        
        # Empresa name
        name_label = QLabel(self.empresa_data.get('nombre', 'Sin Nombre'))
        name_label.setStyleSheet(f"""
            color: {COLORS['GRAY_900']};
            font-weight: {FONTS['WEIGHT_SEMIBOLD']};
            font-size: {FONTS['SIZE_BODY']};
        """)
        layout.addWidget(name_label, 1)
        
        # Circular badge with count
        total = self.empresa_data.get('total_facturas', 0)
        if total > 0:
            badge = QLabel(str(total))
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFixedSize(24, 24)
            badge.setStyleSheet(f"""
                background-color: {COLORS['PRIMARY']};
                color: {COLORS['WHITE']};
                border-radius: 12px;
                font-size: {FONTS['SIZE_CAPTION']};
                font-weight: {FONTS['WEIGHT_BOLD']};
            """)
            layout.addWidget(badge)


class EmpresaList(QWidget):
    """Sidebar widget with empresa list - Redesigned"""
    
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
        
        # Header with logo
        header = QWidget()
        header.setFixedHeight(100)
        header.setStyleSheet(f"background-color: {COLORS['PRIMARY']};")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(SPACING['XL'], SPACING['XL'], SPACING['XL'], SPACING['XL'])
        header_layout.setSpacing(SPACING['XS'])
        
        # Logo icon
        logo_label = QLabel()
        logo_pixmap = IconHelper.get_pixmap('ocr', 32, COLORS['WHITE'])
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(logo_label)
        
        # Title
        title = QLabel("LECTOR-NCF")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            color: {COLORS['WHITE']};
            font-size: {FONTS['SIZE_TITLE']};
            font-weight: {FONTS['WEIGHT_BOLD']};
        """)
        header_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Facturas OCR")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"""
            color: {COLORS['PRIMARY_LIGHT']};
            font-size: {FONTS['SIZE_CAPTION']};
        """)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # List section header
        list_header = QLabel("🏢 EMPRESAS")
        list_header.setStyleSheet(f"""
            padding: {SPACING['MD']}px {SPACING['LG']}px;
            color: {COLORS['GRAY_700']};
            font-size: {FONTS['SIZE_CAPTION']};
            font-weight: {FONTS['WEIGHT_SEMIBOLD']};
            background-color: {COLORS['GRAY_50']};
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(list_header)
        
        # Empresa list
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                border: none;
                background-color: {COLORS['WHITE']};
                outline: none;
            }}
            QListWidget::item {{
                border-bottom: 1px solid {COLORS['GRAY_100']};
                padding: 0;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['PRIMARY_LIGHT']};
                border-left: 4px solid {COLORS['PRIMARY']};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['GRAY_100']};
                border-left: 4px solid {COLORS['PRIMARY']};
            }}
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
            item.setSizeHint(QSize(200, 48))  # Fixed height for consistent look
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
    
    def _on_item_clicked(self, item):
        """Handle item click"""
        index = self.list_widget.row(item)
        if 0 <= index < len(self.empresas):
            empresa_id = self.empresas[index].get('id')
            if empresa_id:
                self.empresa_selected.emit(empresa_id)
