"""
LoadingOverlay component for the UI
"""
import logging
import os
import tempfile
import math
import numpy as np
import time
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve

logger = logging.getLogger(__name__)

class SpinnerWidget(QtWidgets.QWidget):
    """Custom spinner widget with animation"""
    
    def __init__(self, parent=None, size=50, color=QtGui.QColor("#3498DB")):
        super(SpinnerWidget, self).__init__(parent)
        self.setFixedSize(size, size)
        self.color = color
        self.angle = 0
        self.dots = 8
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(50)  # Update every 50ms
        self.setStyleSheet("background-color: transparent;")
    
    def rotate(self):
        """Rotate the spinner"""
        self.angle = (self.angle + 10) % 360
        self.update()
    
    def paintEvent(self, event):
        """Paint the spinner"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        center = self.width() / 2
        outer_radius = (self.width() - 10) / 2
        inner_radius = outer_radius * 0.6
        
        # Draw a light background circle
        background_color = QtGui.QColor(self.color)
        background_color.setAlpha(30)
        painter.setPen(Qt.NoPen)
        painter.setBrush(background_color)
        painter.drawEllipse(5, 5, self.width() - 10, self.height() - 10)
        
        # Draw dots with varying alpha
        for i in range(self.dots):
            dot_angle = self.angle - i * (360 / self.dots)
            alpha = 255 - (i * 255 / self.dots)
            
            dot_color = QtGui.QColor(self.color)
            dot_color.setAlpha(int(alpha))
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(dot_color)
            
            x = center + outer_radius * math.cos(math.radians(dot_angle))
            y = center + outer_radius * math.sin(math.radians(dot_angle))
            
            dot_size = 8 - (i * 4 / self.dots)
            painter.drawEllipse(x - dot_size/2, y - dot_size/2, dot_size, dot_size)
        
        painter.end()
    
    def start(self):
        """Start the animation"""
        if not self.timer.isActive():
            self.timer.start(50)
    
    def stop(self):
        """Stop the animation"""
        if self.timer.isActive():
            self.timer.stop()

class LoadingOverlay(QtWidgets.QWidget):
    """Loading overlay with improved animation effects"""
    
    def __init__(self, parent=None):
        super(LoadingOverlay, self).__init__(parent)
        
        # Make overlay semi-transparent with nice background
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 120);
            border-radius: 10px;
        """)
        
        # Create layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Create container for spinner and label
        self.container = QtWidgets.QWidget()
        self.container.setFixedSize(400, 200)
        self.container.setStyleSheet("""
            background-color: rgba(255, 255, 255, 95%);
            border-radius: 10px;
            border: 1px solid #3498DB;
        """)
        
        # Layout for container
        container_layout = QtWidgets.QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Create spinner widgets - both GIF and custom
        self.spinner_label = QtWidgets.QLabel()
        self.spinner_label.setAlignment(QtCore.Qt.AlignCenter)
        self.spinner_label.setFixedSize(60, 60)
        self.spinner_label.setStyleSheet("background-color: transparent;")
        
        # Create custom spinner widget
        self.custom_spinner = SpinnerWidget(size=60, color=QtGui.QColor("#3498DB"))
        self.custom_spinner.hide()
        
        # Create GIF spinner if available
        self.spinner_movie = QtGui.QMovie()
        spinner_path = self.get_spinner_path()
        if spinner_path:
            self.spinner_movie.setFileName(spinner_path)
            self.spinner_movie.setScaledSize(QtCore.QSize(60, 60))
            self.spinner_label.setMovie(self.spinner_movie)
            self.has_gif = True
        else:
            self.has_gif = False
        
        # Create message label
        self.message_label = QtWidgets.QLabel("Đang tải...")
        self.message_label.setAlignment(QtCore.Qt.AlignCenter)
        self.message_label.setStyleSheet("""
            color: #333333;
            font-size: 16px;
            font-weight: bold;
            background-color: transparent;
        """)
        self.message_label.setWordWrap(True)
        
        # Add widgets to container layout
        container_layout.addWidget(self.spinner_label, alignment=QtCore.Qt.AlignCenter)
        container_layout.addWidget(self.custom_spinner, alignment=QtCore.Qt.AlignCenter)
        container_layout.addWidget(self.message_label, alignment=QtCore.Qt.AlignCenter)
        
        # Add container to main layout
        self.layout.addWidget(self.container, alignment=QtCore.Qt.AlignCenter)
        
        # Add fade-in animation
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutCubic)
        
        # Hide by default
        self.hide()

    def get_spinner_path(self):
        """Attempt to locate or create a spinner GIF"""
        try:
            # Check temp directory for spinner
            temp_dir = os.path.join(tempfile.gettempdir(), "telegram_uploader")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            spinner_path = os.path.join(temp_dir, "spinner.gif")
            
            # Check if spinner exists
            if os.path.exists(spinner_path):
                return spinner_path
            
            # Check for a local spinner in resources
            local_spinner = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                          "..", "..", "resources", "spinner.gif")
            if os.path.exists(local_spinner):
                return local_spinner
                
            # We don't try to generate a GIF here anymore - we'll use the custom spinner
            return None
            
        except Exception as e:
            logger.error(f"Error locating spinner: {str(e)}")
            return None
    
    def set_message(self, message):
        """Set the message to display"""
        self.message_label.setText(message)
    
    def show_spinner(self, show=True):
        """Show or hide the spinner"""
        if show:
            if self.has_gif:
                # Use GIF spinner if available
                self.spinner_movie.start()
                self.spinner_label.show()
                self.custom_spinner.hide()
            else:
                # Use custom spinner widget
                self.spinner_label.hide()
                self.custom_spinner.show()
                self.custom_spinner.start()
        else:
            # Stop both spinners
            if self.has_gif:
                self.spinner_movie.stop()
            self.custom_spinner.stop()
            
            self.spinner_label.hide()
            self.custom_spinner.hide()
    
    def showEvent(self, event):
        """Handle show event"""
        # Start spinner
        self.show_spinner(True)
        
        # Play fade-in animation
        self.fade_anim.setDirection(QPropertyAnimation.Forward)
        self.fade_anim.start()
        
        super(LoadingOverlay, self).showEvent(event)
    
    def hideEvent(self, event):
        """Handle hide event"""
        # Stop spinner
        self.show_spinner(False)
        
        super(LoadingOverlay, self).hideEvent(event)
    
    def resizeEvent(self, event):
        """Handle resize event"""
        # Make sure container is properly sized and centered
        self.container.setFixedSize(min(self.width() - 40, 400), 200)
        super(LoadingOverlay, self).resizeEvent(event)