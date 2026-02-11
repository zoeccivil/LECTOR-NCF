"""
Image viewer widget with zoom and pan capabilities
"""
from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, QWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QLabel)
from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QTransform
from PIL import Image
import requests
from io import BytesIO


class ImageViewer(QWidget):
    """Image viewer with zoom, pan, and rotation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_pixmap = None
        self.rotation_angle = 0
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        toolbar = QWidget()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet("background-color: #333333; border-bottom: 2px solid #212121;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 10, 10, 10)
        
        # Zoom in button
        self.zoom_in_btn = QPushButton("🔍+")
        self.zoom_in_btn.setFixedSize(40, 30)
        self.zoom_in_btn.setToolTip("Zoom In")
        self.zoom_in_btn.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar_layout.addWidget(self.zoom_in_btn)
        
        # Zoom out button
        self.zoom_out_btn = QPushButton("🔍-")
        self.zoom_out_btn.setFixedSize(40, 30)
        self.zoom_out_btn.setToolTip("Zoom Out")
        self.zoom_out_btn.setStyleSheet(self.zoom_in_btn.styleSheet())
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar_layout.addWidget(self.zoom_out_btn)
        
        # Rotate button
        self.rotate_btn = QPushButton("⟲")
        self.rotate_btn.setFixedSize(40, 30)
        self.rotate_btn.setToolTip("Rotate 90°")
        self.rotate_btn.setStyleSheet(self.zoom_in_btn.styleSheet())
        self.rotate_btn.clicked.connect(self.rotate_image)
        toolbar_layout.addWidget(self.rotate_btn)
        
        # Reset button
        self.reset_btn = QPushButton("⟳ Reset")
        self.reset_btn.setFixedSize(70, 30)
        self.reset_btn.setToolTip("Reset View")
        self.reset_btn.setStyleSheet(self.zoom_in_btn.styleSheet())
        self.reset_btn.clicked.connect(self.reset_view)
        toolbar_layout.addWidget(self.reset_btn)
        
        # Zoom indicator
        self.zoom_label = QLabel("100%")
        self.zoom_label.setStyleSheet("color: white; font-size: 12px; padding: 0 10px;")
        toolbar_layout.addWidget(self.zoom_label)
        
        toolbar_layout.addStretch()
        
        layout.addWidget(toolbar)
        
        # Graphics view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("background-color: #333333; border: none;")
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setRenderHint(self.view.renderHints())
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        # Enable mouse wheel zoom
        self.view.wheelEvent = self._wheel_event
        
        layout.addWidget(self.view)
    
    def load_image_from_url(self, url: str):
        """
        Load image from URL
        
        Args:
            url: Image URL
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Load with PIL
            image = Image.open(BytesIO(response.content))
            
            # Convert to QPixmap
            image_data = image.convert("RGB")
            width, height = image_data.size
            bytes_data = image_data.tobytes("raw", "RGB")
            
            qimage = QImage(bytes_data, width, height, width * 3, 
                          QImage.Format.Format_RGB888)
            self.current_pixmap = QPixmap.fromImage(qimage)
            
            self._display_image()
            
        except Exception as e:
            print(f"Error loading image: {e}")
            self.show_placeholder("Error cargando imagen")
    
    def load_image_from_path(self, path: str):
        """
        Load image from file path
        
        Args:
            path: Local file path
        """
        try:
            self.current_pixmap = QPixmap(path)
            self._display_image()
        except Exception as e:
            print(f"Error loading image: {e}")
            self.show_placeholder("Error cargando imagen")
    
    def _display_image(self):
        """Display the current pixmap in the scene"""
        if self.current_pixmap:
            self.scene.clear()
            self.rotation_angle = 0
            self.scene.addPixmap(self.current_pixmap)
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self._update_zoom_label()
    
    def show_placeholder(self, message: str = "Sin imagen"):
        """Show placeholder text when no image is loaded"""
        self.scene.clear()
        text = self.scene.addText(message)
        text.setDefaultTextColor(Qt.GlobalColor.white)
        font = text.font()
        font.setPointSize(16)
        text.setFont(font)
    
    def zoom_in(self):
        """Zoom in by 10%"""
        self.view.scale(1.1, 1.1)
        self._update_zoom_label()
    
    def zoom_out(self):
        """Zoom out by 10%"""
        self.view.scale(0.9, 0.9)
        self._update_zoom_label()
    
    def rotate_image(self):
        """Rotate image 90 degrees clockwise"""
        if self.current_pixmap:
            self.rotation_angle = (self.rotation_angle + 90) % 360
            transform = QTransform().rotate(90)
            self.current_pixmap = self.current_pixmap.transformed(transform)
            self.scene.clear()
            self.scene.addPixmap(self.current_pixmap)
    
    def reset_view(self):
        """Reset zoom and rotation"""
        if self.current_pixmap:
            self.view.resetTransform()
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self._update_zoom_label()
    
    def _wheel_event(self, event):
        """Handle mouse wheel for zooming"""
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def _update_zoom_label(self):
        """Update zoom percentage label"""
        transform = self.view.transform()
        zoom_level = transform.m11() * 100  # Get scale factor
        self.zoom_label.setText(f"{zoom_level:.0f}%")
