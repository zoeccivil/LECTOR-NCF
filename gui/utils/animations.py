"""
Animation helper utility for GUI transitions and effects
"""
from PyQt6.QtCore import (QPropertyAnimation, QEasingCurve, QAbstractAnimation,
                          QPoint, QRect, QSequentialAnimationGroup, QParallelAnimationGroup)
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect


class AnimationHelper:
    """Helper class for creating smooth animations"""
    
    @staticmethod
    def fade_in(widget: QWidget, duration: int = 300, start_opacity: float = 0.0, end_opacity: float = 1.0):
        """
        Create fade in animation for a widget
        
        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            start_opacity: Starting opacity (0.0 to 1.0)
            end_opacity: Ending opacity (0.0 to 1.0)
            
        Returns:
            QPropertyAnimation object
        """
        # Create opacity effect if not exists
        if not widget.graphicsEffect():
            effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(effect)
        else:
            effect = widget.graphicsEffect()
        
        # Create animation
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(start_opacity)
        animation.setEndValue(end_opacity)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        return animation
    
    @staticmethod
    def fade_out(widget: QWidget, duration: int = 300, start_opacity: float = 1.0, end_opacity: float = 0.0):
        """
        Create fade out animation for a widget
        
        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            start_opacity: Starting opacity (0.0 to 1.0)
            end_opacity: Ending opacity (0.0 to 1.0)
            
        Returns:
            QPropertyAnimation object
        """
        return AnimationHelper.fade_in(widget, duration, start_opacity, end_opacity)
    
    @staticmethod
    def slide_in(widget: QWidget, direction: str = 'left', duration: int = 300, distance: int = 50):
        """
        Create slide in animation for a widget
        
        Args:
            widget: Widget to animate
            direction: Slide direction ('left', 'right', 'top', 'bottom')
            duration: Animation duration in milliseconds
            distance: Distance to slide in pixels
            
        Returns:
            QPropertyAnimation object
        """
        # Get current position
        current_pos = widget.pos()
        
        # Calculate start position based on direction
        if direction == 'left':
            start_pos = QPoint(current_pos.x() - distance, current_pos.y())
        elif direction == 'right':
            start_pos = QPoint(current_pos.x() + distance, current_pos.y())
        elif direction == 'top':
            start_pos = QPoint(current_pos.x(), current_pos.y() - distance)
        elif direction == 'bottom':
            start_pos = QPoint(current_pos.x(), current_pos.y() + distance)
        else:
            start_pos = current_pos
        
        # Create animation
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(current_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        return animation
    
    @staticmethod
    def slide_fade_in(widget: QWidget, direction: str = 'left', duration: int = 300, distance: int = 50):
        """
        Create combined slide + fade in animation
        
        Args:
            widget: Widget to animate
            direction: Slide direction ('left', 'right', 'top', 'bottom')
            duration: Animation duration in milliseconds
            distance: Distance to slide in pixels
            
        Returns:
            QParallelAnimationGroup object
        """
        # Create animation group
        group = QParallelAnimationGroup()
        
        # Add slide animation
        slide_anim = AnimationHelper.slide_in(widget, direction, duration, distance)
        group.addAnimation(slide_anim)
        
        # Add fade animation
        fade_anim = AnimationHelper.fade_in(widget, duration)
        group.addAnimation(fade_anim)
        
        return group
    
    @staticmethod
    def scale_animation(widget: QWidget, start_scale: float = 0.95, end_scale: float = 1.0, duration: int = 150):
        """
        Create scale animation for a widget
        
        Args:
            widget: Widget to animate
            start_scale: Starting scale factor
            end_scale: Ending scale factor
            duration: Animation duration in milliseconds
            
        Returns:
            QPropertyAnimation object
        """
        # Get widget geometry
        geometry = widget.geometry()
        center = geometry.center()
        
        # Calculate start and end geometry
        start_width = int(geometry.width() * start_scale)
        start_height = int(geometry.height() * start_scale)
        start_x = center.x() - start_width // 2
        start_y = center.y() - start_height // 2
        
        end_width = int(geometry.width() * end_scale)
        end_height = int(geometry.height() * end_scale)
        end_x = center.x() - end_width // 2
        end_y = center.y() - end_height // 2
        
        start_rect = QRect(start_x, start_y, start_width, start_height)
        end_rect = QRect(end_x, end_y, end_width, end_height)
        
        # Create animation
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        return animation
    
    @staticmethod
    def hover_scale(scale: float = 1.05):
        """
        Get hover scale factor for hover effects
        
        Args:
            scale: Scale factor for hover state
            
        Returns:
            Float scale factor
        """
        return scale
