"""
QSS Global Stylesheet for LECTOR-NCF GUI
"""

GLOBAL_STYLES = """
/* Main Window */
QMainWindow {
    background-color: #F8F9FA;
}

/* Primary Button */
QPushButton {
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 14px;
    font-family: "Segoe UI", Roboto, sans-serif;
}

QPushButton[class="primary"] {
    background-color: #1976D2;
    color: white;
}

QPushButton[class="primary"]:hover {
    background-color: #1565C0;
}

QPushButton[class="primary"]:pressed {
    background-color: #0D47A1;
}

/* Success Button */
QPushButton[class="success"] {
    background-color: #4CAF50;
    color: white;
}

QPushButton[class="success"]:hover {
    background-color: #388E3C;
}

/* Warning Button */
QPushButton[class="warning"] {
    background-color: #FF9800;
    color: white;
}

QPushButton[class="warning"]:hover {
    background-color: #F57C00;
}

/* Error Button */
QPushButton[class="error"] {
    background-color: #F44336;
    color: white;
}

QPushButton[class="error"]:hover {
    background-color: #D32F2F;
}

/* Outline Button */
QPushButton[class="outline"] {
    background-color: transparent;
    border: 1px solid #E0E0E0;
    color: #212121;
}

QPushButton[class="outline"]:hover {
    background-color: #F8F9FA;
}

/* Input Fields */
QLineEdit, QDoubleSpinBox, QDateEdit, QSpinBox, QComboBox {
    border: 1px solid #BDBDBD;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 14px;
    font-family: "Segoe UI", Roboto, sans-serif;
    background-color: white;
}

QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #1976D2;
}

/* Table Widget */
QTableWidget {
    gridline-color: #E0E0E0;
    selection-background-color: #E3F2FD;
    selection-color: #1565C0;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    background-color: white;
}

QTableWidget::item {
    padding: 12px;
    border-bottom: 1px solid #F0F0F0;
}

QTableWidget::item:selected {
    background-color: #E3F2FD;
    color: #1565C0;
}

QTableWidget QHeaderView::section {
    background-color: #F8F9FA;
    padding: 12px;
    border: none;
    border-bottom: 2px solid #E0E0E0;
    font-weight: 600;
    color: #757575;
    text-align: left;
}

/* List Widget */
QListWidget {
    background: white;
    border: none;
    border-radius: 4px;
}

QListWidget::item {
    padding: 12px;
    border-radius: 6px;
    margin: 2px;
}

QListWidget::item:selected {
    background-color: #E3F2FD;
    color: #1565C0;
}

QListWidget::item:hover {
    background-color: #F8F9FA;
}

/* Labels */
QLabel {
    color: #212121;
    font-size: 14px;
    font-family: "Segoe UI", Roboto, sans-serif;
}

QLabel[class="title"] {
    font-size: 24px;
    font-weight: bold;
    color: #212121;
}

QLabel[class="subtitle"] {
    font-size: 16px;
    font-weight: 600;
    color: #212121;
}

QLabel[class="caption"] {
    font-size: 12px;
    color: #757575;
}

/* Scroll Area */
QScrollArea {
    border: none;
    background-color: white;
}

QScrollBar:vertical {
    border: none;
    background: #F8F9FA;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #BDBDBD;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #9E9E9E;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Splitter */
QSplitter::handle {
    background-color: #E0E0E0;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* Status Bar */
QStatusBar {
    background-color: #F8F9FA;
    color: #757575;
    border-top: 1px solid #E0E0E0;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    text-align: center;
    background-color: #F8F9FA;
}

QProgressBar::chunk {
    background-color: #1976D2;
    border-radius: 3px;
}

/* Group Box */
QGroupBox {
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 10px;
    background-color: white;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #212121;
    font-weight: 600;
}

/* Check Box */
QCheckBox {
    spacing: 8px;
    color: #212121;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #BDBDBD;
    border-radius: 3px;
    background-color: white;
}

QCheckBox::indicator:checked {
    background-color: #1976D2;
    border-color: #1976D2;
}

/* Radio Button */
QRadioButton {
    spacing: 8px;
    color: #212121;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #BDBDBD;
    border-radius: 9px;
    background-color: white;
}

QRadioButton::indicator:checked {
    background-color: #1976D2;
    border-color: #1976D2;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    background-color: white;
}

QTabBar::tab {
    background-color: #F8F9FA;
    color: #757575;
    padding: 8px 16px;
    border: 1px solid #E0E0E0;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: white;
    color: #1976D2;
    font-weight: 600;
}

QTabBar::tab:hover {
    background-color: #E3F2FD;
}
"""

# Color constants for programmatic use
COLORS = {
    'primary_blue': '#1976D2',
    'primary_dark': '#1565C0',
    'primary_light': '#E3F2FD',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'error': '#F44336',
    'pending': '#FFC107',
    'exported': '#9E9E9E',
    'text_primary': '#212121',
    'text_secondary': '#757575',
    'bg_white': '#FFFFFF',
    'bg_alt': '#F8F9FA',
    'border': '#E0E0E0',
}
