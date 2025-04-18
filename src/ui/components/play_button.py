"""
Custom play button component for the UI
"""
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QPainter, QColor, QPen, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QRectF

class PlayButton(QPushButton):
    """Custom play button with SVG-like triangle using QPainter"""
    
    def __init__(self, parent=None):
        super(PlayButton, self).__init__(parent)
        # Set size
        self.setFixedSize(70, 70)
        self.setCursor(Qt.PointingHandCursor)
        # No text
        self.setText("")
        # Default colors
        self.background_color = QColor("#3498DB")
        self.icon_color = QColor(255, 255, 255)
        # Update visuals
        self.update()
        
    def paintEvent(self, event):
        """Custom paint event to draw the play button"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw rounded background
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.background_color)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 25, 25)
        
        # Draw play triangle
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.icon_color)
        
        # Create a triangle polygon
        # Slightly offset to right to account for visual weight
        width = self.width()
        height = self.height()
        triangle_width = width * 0.4
        triangle_height = height * 0.4
        
        # Center the triangle within the button
        center_x = width / 2 + width * 0.03  # Slight right adjustment
        center_y = height / 2
        
        # Create triangle points
        triangle = QPolygonF()
        triangle.append(QPointF(center_x - triangle_width/2, center_y - triangle_height/2))
        triangle.append(QPointF(center_x + triangle_width/2, center_y))
        triangle.append(QPointF(center_x - triangle_width/2, center_y + triangle_height/2))
        
        # Draw the triangle
        painter.drawPolygon(triangle)
        
    def enterEvent(self, event):
        """Handle hover state"""
        self.background_color = QColor("#2980B9")
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle end of hover state"""
        self.background_color = QColor("#3498DB")
        self.update()
        super().leaveEvent(event)
