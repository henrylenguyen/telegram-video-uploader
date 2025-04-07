"""
PyQt5 Gallery Modal for displaying video frames
"""
import os
import sys
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                            QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea,
                            QFrame, QGridLayout, QSizePolicy, QMessageBox, QShortcut,
                            QFileDialog)
from PyQt5.QtGui import QPixmap, QIcon, QImage, QPalette, QColor, QCursor, QKeySequence
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QPoint

logger = logging.getLogger(__name__)

class ThumbnailWidget(QWidget):
    """Widget to display a thumbnail image with active state highlighting"""
    clicked = pyqtSignal(int)  # Signal to emit when thumbnail is clicked

    def __init__(self, image_path, index, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.index = index
        self.is_active = False
        
        # Set cursor to pointing hand
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Create frame for border
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setStyleSheet("border: 1px solid #e0e0e0; border-radius: 2px;")
        
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create image label
        self.image_label = QLabel()
        self.image_label.setFixedSize(140, 110)
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # Load image
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("Error loading")
        
        frame_layout.addWidget(self.image_label)
        layout.addWidget(self.frame)
        
        self.setLayout(layout)
    
    def set_active(self, active):
        """Set the active state of the thumbnail"""
        self.is_active = active
        if active:
            self.frame.setStyleSheet("border: 3px solid #4a7ebb; border-radius: 4px;")
        else:
            self.frame.setStyleSheet("border: 1px solid #e0e0e0; border-radius: 2px;")
    
    def mousePressEvent(self, event):
        """Handle mouse press event"""
        self.clicked.emit(self.index)
        super().mousePressEvent(event)
    
    def scrollToVisible(self):
        """Scroll to make this widget visible in the scroll area"""
        scrollarea = self.parent().parent()
        if hasattr(scrollarea, 'ensureVisible'):
            # Get the position of this widget relative to the scroll area's widget
            pos = self.mapTo(scrollarea.widget(), QPoint(0, 0))
            # Ensure it's visible
            scrollarea.ensureVisible(pos.x(), pos.y(), self.width(), self.height())


class GalleryModal(QMainWindow):
    """Modal window to display a gallery of images with navigation controls"""
    
    def __init__(self, image_paths, parent=None, initial_index=0):
        super().__init__(parent)
        
        self.image_paths = image_paths
        self.current_index = initial_index
        self.zoom_level = 1.0
        
        self.init_ui()
        
        # Apply fullscreen
        self.showMaximized()
        
        # Select initial image
        self.select_image(self.current_index)
    
    def init_ui(self):
        """Initialize the user interface"""
        # Set window properties
        self.setWindowTitle('Video Frames Gallery')
        self.setGeometry(50, 50, 1200, 800)
        self.setStyleSheet("background-color: white;")
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left panel (main image)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main image display
        main_image_container = QWidget()
        main_image_container.setStyleSheet("background-color: #000000;")
        main_image_layout = QHBoxLayout(main_image_container)
        
        # Previous button
        self.prev_button = QPushButton("<")
        self.prev_button.setFixedSize(60, 60)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(74, 126, 187, 0.8);
                color: white;
                border-radius: 30px;
                font-weight: bold;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: rgba(58, 110, 171, 1.0);
            }
        """)
        self.prev_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.prev_button.clicked.connect(self.prev_image)
        
        # Main image
        self.main_image = QLabel()
        self.main_image.setAlignment(Qt.AlignCenter)
        self.main_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Next button
        self.next_button = QPushButton(">")
        self.next_button.setFixedSize(60, 60)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(74, 126, 187, 0.8);
                color: white;
                border-radius: 30px;
                font-weight: bold;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: rgba(58, 110, 171, 1.0);
            }
        """)
        self.next_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.next_button.clicked.connect(self.next_image)
        
        main_image_layout.addWidget(self.prev_button)
        main_image_layout.addWidget(self.main_image, 1)
        main_image_layout.addWidget(self.next_button)
        
        # Controls container at bottom
        controls_container = QWidget()
        controls_container.setFixedHeight(50)
        controls_container.setStyleSheet("background-color: #f0f0f0; border-top: 1px solid #cccccc;")
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(10, 5, 10, 5)
        
        # Download button
        self.download_button = QPushButton("Tải xuống")
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #4a7ebb;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a6eab;
            }
        """)
        self.download_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.download_button.clicked.connect(self.download_image)
        
        # Image counter
        self.counter_label = QLabel()
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setStyleSheet("color: #333333; font-size: 14px; font-weight: bold;")
        
        # Zoom controls
        zoom_control_widget = QWidget()
        zoom_layout = QHBoxLayout(zoom_control_widget)
        zoom_layout.setContentsMargins(0, 0, 0, 0)
        zoom_layout.setSpacing(5)
        
        zoom_out_button = QPushButton("-")
        zoom_out_button.setFixedSize(30, 30)
        zoom_out_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #666666;
                border-radius: 15px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        zoom_out_button.setCursor(QCursor(Qt.PointingHandCursor))
        zoom_out_button.clicked.connect(self.zoom_out)
        
        zoom_in_button = QPushButton("+")
        zoom_in_button.setFixedSize(30, 30)
        zoom_in_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #666666;
                border-radius: 15px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        zoom_in_button.setCursor(QCursor(Qt.PointingHandCursor))
        zoom_in_button.clicked.connect(self.zoom_in)
        
        zoom_layout.addWidget(zoom_out_button)
        zoom_layout.addWidget(zoom_in_button)
        
        # Add widgets to controls layout (without the close button)
        controls_layout.addWidget(self.download_button)
        controls_layout.addStretch(1)
        controls_layout.addWidget(self.counter_label)
        controls_layout.addStretch(1)
        controls_layout.addWidget(zoom_control_widget)
        
        # Add main components to left layout
        left_layout.addWidget(main_image_container, 1)
        left_layout.addWidget(controls_container)
        
        # Right panel (thumbnails)
        right_panel = QWidget()
        right_panel.setFixedWidth(180)
        right_panel.setStyleSheet("background-color: #f8f8f8; border-left: 1px solid #cccccc;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Thumbnails label
        thumbnails_label = QLabel("Hình thu nhỏ")
        thumbnails_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333333;")
        thumbnails_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(thumbnails_label)
        
        # Thumbnails scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("border: none;")
        
        # Thumbnails container
        thumbnails_container = QWidget()
        self.thumbnails_layout = QVBoxLayout(thumbnails_container)
        self.thumbnails_layout.setAlignment(Qt.AlignTop)
        self.thumbnails_layout.setSpacing(10)
        self.thumbnails_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create thumbnails
        self.thumbnails = []
        for i, path in enumerate(self.image_paths):
            thumbnail = ThumbnailWidget(path, i)
            thumbnail.clicked.connect(self.select_image)
            self.thumbnails_layout.addWidget(thumbnail)
            self.thumbnails.append(thumbnail)
        
        scroll_area.setWidget(thumbnails_container)
        right_layout.addWidget(scroll_area)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 5)
        main_layout.addWidget(right_panel)
        
        # Set up keyboard shortcuts
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""
        # Left arrow - previous image
        self.prev_shortcut = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.prev_shortcut.activated.connect(self.prev_image)
        
        # Right arrow - next image
        self.next_shortcut = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.next_shortcut.activated.connect(self.next_image)
        
        # Plus - zoom in
        self.zoom_in_shortcut = QShortcut(QKeySequence(Qt.Key_Plus), self)
        self.zoom_in_shortcut.activated.connect(self.zoom_in)
        
        # Minus - zoom out
        self.zoom_out_shortcut = QShortcut(QKeySequence(Qt.Key_Minus), self)
        self.zoom_out_shortcut.activated.connect(self.zoom_out)
        
        # Escape - close
        self.close_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.close_shortcut.activated.connect(self.close)
    
    def select_image(self, index):
        """
        Select and display the image at the given index
        
        Args:
            index: Index of the image to display
        """
        if 0 <= index < len(self.image_paths):
            self.current_index = index
            
            # Update main image
            pixmap = QPixmap(self.image_paths[index])
            if not pixmap.isNull():
                # Calculate scaled size to fit the view while maintaining aspect ratio
                self.original_pixmap = pixmap
                self._update_main_image()
                
                # Update counter with zoom level
                self.counter_label.setText(f"{index + 1} / {len(self.image_paths)} (Zoom: {self.zoom_level:.2f}x)")
                
                # Update thumbnails
                for i, thumbnail in enumerate(self.thumbnails):
                    thumbnail.set_active(i == index)
                
                # Ensure selected thumbnail is visible
                selected_thumbnail = self.thumbnails[index]
                selected_thumbnail.scrollToVisible()
    
    def _update_main_image(self):
        """Update the main image with improved zoom handling"""
        if not hasattr(self, 'original_pixmap') or self.original_pixmap.isNull():
            return
            
        try:
            # Get the display size
            display_width = max(50, self.main_image.width() - 20)  # Ensure positive value
            display_height = max(50, self.main_image.height() - 20)
            
            # Get original size
            original_width = max(1, self.original_pixmap.width())  # Prevent division by zero
            original_height = max(1, self.original_pixmap.height())
            
            # Calculate the base scaling to fit in view
            width_ratio = display_width / original_width
            height_ratio = display_height / original_height
            base_scale = min(width_ratio, height_ratio)
            
            # Apply zoom level with safety check
            scale = base_scale * max(0.1, min(2.5, self.zoom_level))
            
            # Calculate new size with limits to prevent excessive memory usage
            new_width = min(10000, int(original_width * scale))
            new_height = min(10000, int(original_height * scale))
            
            # Create scaled pixmap with high quality transformation
            scaled_pixmap = self.original_pixmap.scaled(
                new_width, new_height, 
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            
            # Set the pixmap
            self.main_image.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Error updating image: {str(e)}")
    
    def resizeEvent(self, event):
        """Handle window resize event"""
        super().resizeEvent(event)
        self._update_main_image()
    
    def next_image(self):
        """Display the next image in the gallery"""
        next_idx = (self.current_index + 1) % len(self.image_paths)
        self.select_image(next_idx)
    
    def prev_image(self):
        """Display the previous image in the gallery"""
        prev_idx = (self.current_index - 1) % len(self.image_paths)
        self.select_image(prev_idx)
    
    def zoom_out(self):
        """Zoom out with strict limits and smaller increments"""
        # Hard stop at 0.5x zoom
        if self.zoom_level <= 0.5:
            return
        
        # Use smaller increments as zoom decreases
        if self.zoom_level > 2.0:
            # Faster zooming when highly zoomed in
            increment = 0.1
        elif self.zoom_level > 1.0:
            # Moderate decrements in normal range
            increment = 0.05
        else:
            # Very small decrements when already zoomed out
            increment = 0.025
        
        # Apply zoom with absolute bounds check
        self.zoom_level -= increment
        self.zoom_level = max(0.5, self.zoom_level)  # Double-check we don't go below min
        
        # Update counter and image
        self.counter_label.setText(f"{self.current_index + 1} / {len(self.image_paths)} (Zoom: {self.zoom_level:.2f}x)")
        self._update_main_image()
    
    def zoom_in(self):
        """Zoom in on the current image with strict limits and smaller increments"""
        # Use very strict zoom limits
        if self.zoom_level >= 2.5:
            # Hard stop at 2.5x zoom
            return
        
        # Use smaller increments as zoom increases
        if self.zoom_level < 1.0:
            # Faster zooming when zoomed out
            increment = 0.1
        elif self.zoom_level < 1.5:
            # Moderate increments in normal range
            increment = 0.05
        else:
            # Very small increments when already zoomed in
            increment = 0.025
        
        # Apply zoom with absolute bounds check
        self.zoom_level += increment
        self.zoom_level = min(2.5, self.zoom_level)  # Double-check we don't exceed max
        
        # Update counter and image
        self.counter_label.setText(f"{self.current_index + 1} / {len(self.image_paths)} (Zoom: {self.zoom_level:.2f}x)")
        self._update_main_image()
    
    
    def download_image(self):
        """Download the current image"""
        try:
            # Get the current image path
            source_path = self.image_paths[self.current_index]
            filename = os.path.basename(source_path)
            
            # Ask user for download location
            dest_path, _ = QFileDialog.getSaveFileName(
                self,
                "Lưu hình ảnh",
                filename,
                "Image files (*.png *.jpg *.jpeg)"
            )
            
            if dest_path:
                # Copy the file
                import shutil
                shutil.copy2(source_path, dest_path)
                QMessageBox.information(self, "Thành công", f"Đã lưu hình ảnh vào: {dest_path}")
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu hình ảnh: {str(e)}")


if __name__ == "__main__":
    # Read paths from file if provided as argument
    if len(sys.argv) > 1:
        path_file = sys.argv[1]
        
        if os.path.exists(path_file):
            try:
                with open(path_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # First line is initial index
                initial_index = 0
                try:
                    initial_index = int(lines[0].strip())
                except:
                    pass
                
                # Rest of lines are image paths
                image_paths = [line.strip() for line in lines[1:] if line.strip()]
                
                if image_paths:
                    # Create application and gallery
                    app = QApplication(sys.argv)
                    gallery = GalleryModal(image_paths, initial_index=initial_index)
                    gallery.show()
                    sys.exit(app.exec_())
            except Exception as e:
                print(f"Error opening gallery: {str(e)}")
                sys.exit(1)
    
    # If no file provided or error, show test gallery with dummy images
    print("No valid image paths file provided. Running test gallery.")
    
    # Create a test application
    app = QApplication(sys.argv)
    
    # Create test images
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_images")
    os.makedirs(temp_dir, exist_ok=True)
    
    test_images = []
    for i in range(5):
        # Create a QImage for testing
        image = QImage(800, 600, QImage.Format_RGB32)
        image.fill(QColor(50 + i * 40, 100, 150))
        
        # Save to a temporary file
        path = os.path.join(temp_dir, f"test_image_{i}.png")
        image.save(path)
        test_images.append(path)
    
    # Create and show the gallery
    gallery = GalleryModal(test_images)
    gallery.show()
    
    # Run the application
    sys.exit(app.exec_())