"""
QSS Global Stylesheet for LECTOR-NCF GUI - Modern Minimalist Design
"""
from gui.utils.theme import COLORS, FONTS, SPACING, RADIUS, SHADOWS

GLOBAL_STYLES = f"""
/* Main Window */
QMainWindow {{
    background-color: {COLORS['GRAY_100']};
    font-family: {FONTS['FAMILY']};
}}

/* Primary Button */
QPushButton {{
    border: none;
    padding: {SPACING['SM']}px {SPACING['LG']}px;
    border-radius: {RADIUS['MEDIUM']};
    font-weight: {FONTS['WEIGHT_SEMIBOLD']};
    font-size: {FONTS['SIZE_BODY']};
    font-family: {FONTS['FAMILY']};
}}

QPushButton[class="primary"] {{
    background-color: {COLORS['PRIMARY']};
    color: {COLORS['WHITE']};
}}

QPushButton[class="primary"]:hover {{
    background-color: {COLORS['PRIMARY_DARK']};
}}

QPushButton[class="primary"]:pressed {{
    background-color: {COLORS['PRIMARY_DARK']};
}}

/* Success Button */
QPushButton[class="success"] {{
    background-color: {COLORS['SUCCESS']};
    color: {COLORS['WHITE']};
}}

QPushButton[class="success"]:hover {{
    background-color: #059669;
}}

/* Warning Button */
QPushButton[class="warning"] {{
    background-color: {COLORS['WARNING']};
    color: {COLORS['WHITE']};
}}

QPushButton[class="warning"]:hover {{
    background-color: #D97706;
}}

/* Error Button */
QPushButton[class="error"] {{
    background-color: {COLORS['ERROR']};
    color: {COLORS['WHITE']};
}}

QPushButton[class="error"]:hover {{
    background-color: #DC2626;
}}

/* Outline Button */
QPushButton[class="outline"] {{
    background-color: transparent;
    border: 1px solid {COLORS['GRAY_300']};
    color: {COLORS['GRAY_900']};
}}

QPushButton[class="outline"]:hover {{
    background-color: {COLORS['GRAY_100']};
}}

/* Input Fields */
QLineEdit, QDoubleSpinBox, QDateEdit, QSpinBox, QComboBox {{
    border: 1px solid {COLORS['GRAY_300']};
    padding: {SPACING['SM']}px {SPACING['MD']}px;
    border-radius: {RADIUS['MEDIUM']};
    font-size: {FONTS['SIZE_BODY']};
    font-family: {FONTS['FAMILY']};
    background-color: {COLORS['WHITE']};
    color: {COLORS['GRAY_900']};
}}

QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1px solid {COLORS['PRIMARY']};
    outline: none;
}}

/* Table Widget */
QTableWidget {{
    gridline-color: {COLORS['GRAY_200']};
    selection-background-color: {COLORS['PRIMARY_LIGHT']};
    selection-color: {COLORS['PRIMARY_DARK']};
    border: 1px solid {COLORS['GRAY_200']};
    border-radius: {RADIUS['MEDIUM']};
    background-color: {COLORS['WHITE']};
}}

QTableWidget::item {{
    padding: {SPACING['MD']}px;
    border-bottom: 1px solid {COLORS['GRAY_100']};
}}

QTableWidget::item:hover {{
    background-color: {COLORS['GRAY_100']};
}}

QTableWidget::item:selected {{
    background-color: {COLORS['PRIMARY_LIGHT']};
    color: {COLORS['PRIMARY_DARK']};
}}

QTableWidget::item:alternate {{
    background-color: {COLORS['GRAY_50']};
}}

QTableWidget QHeaderView::section {{
    background-color: {COLORS['WHITE']};
    padding: {SPACING['MD']}px;
    border: none;
    border-bottom: 2px solid {COLORS['GRAY_200']};
    font-weight: {FONTS['WEIGHT_SEMIBOLD']};
    color: {COLORS['GRAY_700']};
    text-align: left;
    font-size: {FONTS['SIZE_CAPTION']};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* List Widget */
QListWidget {{
    background: {COLORS['WHITE']};
    border: none;
    border-radius: {RADIUS['MEDIUM']};
}}

QListWidget::item {{
    padding: {SPACING['MD']}px;
    border-radius: {RADIUS['SMALL']};
    margin: 2px;
}}

QListWidget::item:selected {{
    background-color: {COLORS['PRIMARY_LIGHT']};
    color: {COLORS['PRIMARY_DARK']};
    font-weight: {FONTS['WEIGHT_SEMIBOLD']};
}}

QListWidget::item:hover {{
    background-color: {COLORS['GRAY_100']};
}}

/* Labels */
QLabel {{
    color: {COLORS['GRAY_900']};
    font-size: {FONTS['SIZE_BODY']};
    font-family: {FONTS['FAMILY']};
}}

QLabel[class="title"] {{
    font-size: {FONTS['SIZE_HEADING']};
    font-weight: {FONTS['WEIGHT_BOLD']};
    color: {COLORS['GRAY_900']};
}}

QLabel[class="subtitle"] {{
    font-size: {FONTS['SIZE_SUBTITLE']};
    font-weight: {FONTS['WEIGHT_SEMIBOLD']};
    color: {COLORS['GRAY_900']};
}}

QLabel[class="caption"] {{
    font-size: {FONTS['SIZE_CAPTION']};
    color: {COLORS['GRAY_700']};
}}

/* Scroll Area */
QScrollArea {{
    border: none;
    background-color: {COLORS['WHITE']};
}}

QScrollBar:vertical {{
    border: none;
    background: {COLORS['GRAY_100']};
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['GRAY_300']};
    border-radius: 5px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['GRAY_700']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    border: none;
    background: {COLORS['GRAY_100']};
    height: 10px;
    margin: 0px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background: {COLORS['GRAY_300']};
    border-radius: 5px;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {COLORS['GRAY_700']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* Splitter */
QSplitter::handle {{
    background-color: {COLORS['GRAY_200']};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

/* Status Bar */
QStatusBar {{
    background-color: {COLORS['WHITE']};
    color: {COLORS['GRAY_700']};
    border-top: 1px solid {COLORS['GRAY_200']};
}}

/* Progress Bar */
QProgressBar {{
    border: 1px solid {COLORS['GRAY_200']};
    border-radius: {RADIUS['MEDIUM']};
    text-align: center;
    background-color: {COLORS['GRAY_100']};
}}

QProgressBar::chunk {{
    background-color: {COLORS['PRIMARY']};
    border-radius: {RADIUS['SMALL']};
}}

/* Group Box */
QGroupBox {{
    border: 1px solid {COLORS['GRAY_200']};
    border-radius: {RADIUS['MEDIUM']};
    margin-top: 10px;
    padding-top: 10px;
    background-color: {COLORS['WHITE']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: {COLORS['GRAY_900']};
    font-weight: {FONTS['WEIGHT_SEMIBOLD']};
}}

/* Check Box */
QCheckBox {{
    spacing: {SPACING['SM']}px;
    color: {COLORS['GRAY_900']};
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {COLORS['GRAY_300']};
    border-radius: 3px;
    background-color: {COLORS['WHITE']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['PRIMARY']};
    border-color: {COLORS['PRIMARY']};
}}

/* Radio Button */
QRadioButton {{
    spacing: {SPACING['SM']}px;
    color: {COLORS['GRAY_900']};
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {COLORS['GRAY_300']};
    border-radius: 9px;
    background-color: {COLORS['WHITE']};
}}

QRadioButton::indicator:checked {{
    background-color: {COLORS['PRIMARY']};
    border-color: {COLORS['PRIMARY']};
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid {COLORS['GRAY_200']};
    border-radius: {RADIUS['MEDIUM']};
    background-color: {COLORS['WHITE']};
    top: -1px;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['GRAY_700']};
    padding: {SPACING['SM']}px {SPACING['LG']}px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: {FONTS['SIZE_BODY']};
    font-weight: {FONTS['WEIGHT_MEDIUM']};
    margin-right: {SPACING['SM']}px;
}}

QTabBar::tab:selected {{
    color: {COLORS['PRIMARY']};
    border-bottom: 2px solid {COLORS['PRIMARY']};
    font-weight: {FONTS['WEIGHT_SEMIBOLD']};
}}

QTabBar::tab:hover {{
    color: {COLORS['PRIMARY_DARK']};
    background-color: {COLORS['GRAY_50']};
}}
"""

# Color constants for programmatic use (deprecated - use theme.py instead)
COLORS = {
    'primary_blue': '#2563EB',
    'primary_dark': '#1E40AF',
    'primary_light': '#DBEAFE',
    'success': '#10B981',
    'warning': '#F59E0B',
    'error': '#EF4444',
    'pending': '#F59E0B',
    'exported': '#374151',
    'text_primary': '#111827',
    'text_secondary': '#374151',
    'bg_white': '#FFFFFF',
    'bg_alt': '#F3F4F6',
    'border': '#E5E7EB',
}
