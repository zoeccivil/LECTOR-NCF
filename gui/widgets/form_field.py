"""
Form field widget with OCR confidence indicator
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen


class ConfidenceIndicator(QWidget):
    """Circular confidence indicator widget"""
    
    def __init__(self, confidence: float = 0.0, parent=None):
        super().__init__(parent)
        self.confidence = confidence
        self.setFixedSize(20, 20)
        self.setToolTip(f"Confianza OCR: {confidence*100:.1f}%")
    
    def set_confidence(self, confidence: float):
        """Update confidence value and refresh display"""
        self.confidence = confidence
        self.setToolTip(f"Confianza OCR: {confidence*100:.1f}%")
        self.update()
    
    def paintEvent(self, event):
        """Draw confidence circle"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Determine color based on confidence
        if self.confidence > 0.9:
            color = QColor("#4CAF50")  # Green
        elif self.confidence > 0.7:
            color = QColor("#FFC107")  # Yellow
        else:
            color = QColor("#F44336")  # Red
        
        painter.setBrush(color)
        painter.setPen(QPen(color.darker(120), 1))
        painter.drawEllipse(2, 2, 16, 16)


class FormField(QWidget):
    """Form field with label and OCR confidence indicator"""
    
    def __init__(self, label_text: str, confidence: float = 0.0, 
                 field_type: str = "text", parent=None):
        """
        Initialize form field
        
        Args:
            label_text: Label text for the field
            confidence: OCR confidence score (0.0 to 1.0)
            field_type: Type of field ('text', 'number', 'date')
            parent: Parent widget
        """
        super().__init__(parent)
        self.field_type = field_type
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QLabel(label_text)
        self.label.setMinimumWidth(120)
        layout.addWidget(self.label)
        
        # Input field
        self.input = QLineEdit()
        layout.addWidget(self.input, 1)
        
        # Confidence indicator
        self.indicator = ConfidenceIndicator(confidence)
        layout.addWidget(self.indicator)
    
    def set_value(self, value: str):
        """Set the field value"""
        self.input.setText(str(value) if value else "")
    
    def get_value(self) -> str:
        """Get the field value"""
        return self.input.text()
    
    def set_confidence(self, confidence: float):
        """Update confidence indicator"""
        self.indicator.set_confidence(confidence)
