"""
Icon helper utility for loading and manipulating SVG icons
"""
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray, Qt
from pathlib import Path
import re


class IconHelper:
    """Helper class for loading and manipulating SVG icons"""
    
    ICONS_DIR = Path(__file__).parent.parent / "assets" / "icons"
    
    @staticmethod
    def get_icon(name: str, color: str = "#374151", size: int = 24) -> QIcon:
        """
        Get SVG icon with specified color
        
        Args:
            name: Icon name (without .svg extension)
            color: Hex color code for the icon
            size: Icon size in pixels
            
        Returns:
            QIcon object
        """
        pixmap = IconHelper.get_pixmap(name, size, color)
        return QIcon(pixmap)
    
    @staticmethod
    def get_pixmap(name: str, size: int = 24, color: str = "#374151") -> QPixmap:
        """
        Get SVG as pixmap with specified color
        
        Args:
            name: Icon name (without .svg extension)
            size: Icon size in pixels
            color: Hex color code for the icon
            
        Returns:
            QPixmap object
        """
        # Load SVG file
        svg_path = IconHelper.ICONS_DIR / f"{name}.svg"
        
        if not svg_path.exists():
            # Return empty pixmap if icon not found
            return QPixmap(size, size)
        
        # Read SVG content
        with open(svg_path, 'r') as f:
            svg_content = f.read()
        
        # Replace currentColor with the specified color
        svg_content = svg_content.replace('currentColor', color)
        
        # Create QSvgRenderer from modified content
        svg_bytes = QByteArray(svg_content.encode('utf-8'))
        renderer = QSvgRenderer(svg_bytes)
        
        # Create pixmap and render SVG onto it
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return pixmap
    
    @staticmethod
    def get_colored_pixmap(name: str, size: int, color: QColor) -> QPixmap:
        """
        Get SVG as pixmap with QColor
        
        Args:
            name: Icon name (without .svg extension)
            size: Icon size in pixels
            color: QColor object
            
        Returns:
            QPixmap object
        """
        hex_color = color.name()
        return IconHelper.get_pixmap(name, size, hex_color)
