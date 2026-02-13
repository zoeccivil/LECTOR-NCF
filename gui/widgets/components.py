"""
Reusable UI components for LECTOR-NCF GUI
"""
from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QHBoxLayout,
                             QVBoxLayout, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QColor, QFont, QPixmap
from gui.utils.icon_helper import IconHelper
from gui.utils.theme import COLORS, FONTS, SPACING, RADIUS, SHADOWS


class StatusBadge(QLabel):
    """Pill-style status badge component"""
    
    def __init__(self, status: str = 'pendiente', parent=None):
        super().__init__(parent)
        self.status = status
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(24)
        self.set_status(status)
    
    def set_status(self, status: str):
        """
        Set badge status and update styling
        
        Args:
            status: Status value ('pendiente', 'revisada', 'exportada')
        """
        self.status = status
        
        # Status configurations
        status_config = {
            'pendiente': {
                'text': '⏱️ Pendiente',
                'bg': COLORS['PENDING'],
                'fg': COLORS['GRAY_900']
            },
            'revisada': {
                'text': '✓ Revisada',
                'bg': COLORS['SUCCESS'],
                'fg': COLORS['WHITE']
            },
            'exportada': {
                'text': '📤 Exportada',
                'bg': COLORS['GRAY_700'],
                'fg': COLORS['WHITE']
            }
        }
        
        config = status_config.get(status, status_config['pendiente'])
        
        self.setText(config['text'])
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {config['bg']};
                color: {config['fg']};
                border-radius: {RADIUS['LARGE']};
                padding: 4px 12px;
                font-size: {FONTS['SIZE_CAPTION']};
                font-weight: {FONTS['WEIGHT_SEMIBOLD']};
            }}
        """)


class IconButton(QPushButton):
    """Button with SVG icon and hover effects"""
    
    def __init__(self, icon_name: str, text: str = "", tooltip: str = "", 
                 color: str = None, size: int = 24, parent=None):
        super().__init__(text, parent)
        
        self.icon_name = icon_name
        self.icon_size = size
        self.icon_color = color or COLORS['GRAY_700']
        self.hover_color = COLORS['PRIMARY']
        
        # Set icon
        self._update_icon(self.icon_color)
        
        # Set tooltip
        if tooltip:
            self.setToolTip(tooltip)
        
        # Set cursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Apply styling
        self._apply_style()
    
    def _update_icon(self, color: str):
        """Update icon with specified color"""
        icon = IconHelper.get_icon(self.icon_name, color, self.icon_size)
        self.setIcon(icon)
        self.setIconSize(QSize(self.icon_size, self.icon_size))
    
    def _apply_style(self):
        """Apply button styling"""
        self.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-color: transparent;
                padding: {SPACING['SM']}px;
                border-radius: {RADIUS['SMALL']};
                font-size: {FONTS['SIZE_BODY']};
                font-weight: {FONTS['WEIGHT_MEDIUM']};
                color: {COLORS['GRAY_700']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['GRAY_100']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['GRAY_200']};
            }}
        """)
    
    def enterEvent(self, event):
        """Handle mouse enter event"""
        self._update_icon(self.hover_color)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave event"""
        self._update_icon(self.icon_color)
        super().leaveEvent(event)


class SearchBox(QLineEdit):
    """Search input with icon and clear button"""
    
    search_changed = pyqtSignal(str)
    
    def __init__(self, placeholder: str = "Buscar...", parent=None):
        super().__init__(parent)
        
        self.setPlaceholderText(placeholder)
        
        # Set styling
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COLORS['GRAY_300']};
                border-radius: {RADIUS['MEDIUM']};
                padding: {SPACING['SM']}px {SPACING['LG']}px {SPACING['SM']}px 40px;
                font-size: {FONTS['SIZE_BODY']};
                background-color: {COLORS['WHITE']};
                color: {COLORS['GRAY_900']};
            }}
            QLineEdit:focus {{
                border-color: {COLORS['PRIMARY']};
                outline: none;
            }}
        """)
        
        # Add search icon (left side)
        self._add_search_icon()
        
        # Connect text changed signal
        self.textChanged.connect(self.search_changed.emit)
        
        # Set minimum width
        self.setMinimumWidth(250)
        self.setMaximumHeight(40)
    
    def _add_search_icon(self):
        """Add search icon to the left side"""
        # Create icon label
        icon_label = QLabel(self)
        icon_pixmap = IconHelper.get_pixmap('search', 20, COLORS['GRAY_700'])
        icon_label.setPixmap(icon_pixmap)
        icon_label.setStyleSheet("border: none; background: transparent;")
        icon_label.move(12, 10)
        icon_label.show()


class StatsCard(QWidget):
    """Statistics card component"""
    
    def __init__(self, icon_name: str, value: str, label: str, 
                 color: str = None, parent=None):
        super().__init__(parent)
        
        self.icon_name = icon_name
        self.value_text = value
        self.label_text = label
        self.card_color = color or COLORS['PRIMARY']
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING['LG'], SPACING['LG'], 
                                SPACING['LG'], SPACING['LG'])
        layout.setSpacing(SPACING['MD'])
        
        # Icon
        icon_label = QLabel()
        icon_pixmap = IconHelper.get_pixmap(self.icon_name, 32, self.card_color)
        icon_label.setPixmap(icon_pixmap)
        layout.addWidget(icon_label)
        
        # Text content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        
        # Value
        value_label = QLabel(self.value_text)
        value_label.setStyleSheet(f"""
            font-size: {FONTS['SIZE_HEADING']};
            font-weight: {FONTS['WEIGHT_BOLD']};
            color: {COLORS['GRAY_900']};
        """)
        text_layout.addWidget(value_label)
        
        # Label
        label_label = QLabel(self.label_text)
        label_label.setStyleSheet(f"""
            font-size: {FONTS['SIZE_CAPTION']};
            color: {COLORS['GRAY_700']};
        """)
        text_layout.addWidget(label_label)
        
        layout.addLayout(text_layout, 1)
        
        # Apply card styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['WHITE']};
                border-radius: {RADIUS['MEDIUM']};
                border: 1px solid {COLORS['GRAY_200']};
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)
        
        # Set cursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def update_value(self, value: str):
        """Update the value displayed"""
        self.value_text = value
        # Find value label and update
        layout = self.layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if isinstance(item, QVBoxLayout):
                value_label = item.itemAt(0).widget()
                if isinstance(value_label, QLabel):
                    value_label.setText(value)


class EmptyState(QWidget):
    """Component for displaying empty states"""
    
    def __init__(self, icon_name: str, title: str, description: str = "",
                 action_text: str = "", parent=None):
        super().__init__(parent)
        
        self.icon_name = icon_name
        self.title_text = title
        self.description_text = description
        self.action_text = action_text
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(SPACING['LG'])
        
        # Icon (large)
        icon_label = QLabel()
        icon_pixmap = IconHelper.get_pixmap(self.icon_name, 64, COLORS['GRAY_300'])
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(self.title_text)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: {FONTS['SIZE_TITLE']};
            font-weight: {FONTS['WEIGHT_SEMIBOLD']};
            color: {COLORS['GRAY_900']};
        """)
        layout.addWidget(title_label)
        
        # Description (if provided)
        if self.description_text:
            desc_label = QLabel(self.description_text)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(f"""
                font-size: {FONTS['SIZE_BODY']};
                color: {COLORS['GRAY_700']};
                max-width: 400px;
            """)
            layout.addWidget(desc_label)
        
        # Action button (if provided)
        if self.action_text:
            action_button = QPushButton(self.action_text)
            action_button.setStyleSheet(f"""
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
            action_button.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(action_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Set minimum size
        self.setMinimumHeight(300)
