"""
Main UI module for Telegram Video Uploader PyQt5 version.
"""
import sys
import os
import logging
import configparser
import traceback
import time
import tempfile
import math
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtGui import QPainter, QColor, QPen, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal

# Import the utilities for main tab
from utils.main_tab import (
    refresh_video_list, 
    scan_folder_for_videos,
    select_all_videos,
    deselect_all_videos,
    select_unuploaded_videos,
    upload_selected_videos,
    upload_single_video,
    display_video_frames,
    display_video_info,
    display_error_message,
    clear_video_preview,
    clear_video_frames,
    update_video_preview_ui
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MainUI")

class LoadingOverlay(QtWidgets.QWidget):
    """Loading overlay với animation hiệu ứng tốt hơn"""
    
    def __init__(self, parent=None):
        super(LoadingOverlay, self).__init__(parent)
        
        # Làm cho overlay bán trong suốt với màu nền đẹp
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 150);
            border-radius: 10px;
        """)
        
        # Tạo layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Tạo container cho spinner và label
        self.container = QtWidgets.QWidget()
        self.container.setFixedSize(400, 200)
        self.container.setStyleSheet("""
            background-color: rgba(255, 255, 255, 90%);
            border-radius: 10px;
            border: 1px solid #3498DB;
        """)
        
        # Layout cho container
        container_layout = QtWidgets.QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Tạo label cho spinner
        self.spinner_label = QtWidgets.QLabel()
        self.spinner_label.setAlignment(QtCore.Qt.AlignCenter)
        self.spinner_label.setFixedSize(50, 50)
        self.spinner_label.setStyleSheet("background-color: transparent;")
        
        # Tạo spinner animation
        self.spinner_movie = QtGui.QMovie()
        self.spinner_movie.setFileName(self.get_spinner_path())
        self.spinner_movie.setScaledSize(QtCore.QSize(50, 50))
        self.spinner_label.setMovie(self.spinner_movie)
        
        # Tạo label cho message
        self.message_label = QtWidgets.QLabel("Đang tải...")
        self.message_label.setAlignment(QtCore.Qt.AlignCenter)
        self.message_label.setStyleSheet("""
            color: #333333;
            font-size: 16px;
            font-weight: bold;
            background-color: transparent;
        """)
        self.message_label.setWordWrap(True)
        
        # Thêm các widget vào container
        container_layout.addWidget(self.spinner_label, alignment=QtCore.Qt.AlignCenter)
        container_layout.addWidget(self.message_label, alignment=QtCore.Qt.AlignCenter)
        
        # Thêm container vào layout chính
        self.layout.addWidget(self.container, alignment=QtCore.Qt.AlignCenter)
        
        # Ẩn mặc định
        self.hide()
        
        # Timer để cập nhật spinner khi không có file
        self.dots_count = 0
        self.dots_timer = None

    def get_spinner_path(self):
        """Tạo hoặc tìm spinner GIF ở thư mục tạm"""
        try:
            # Sử dụng spinner có sẵn nếu có
            import os
            import tempfile
            import math
            import numpy as np
            
            # Kiểm tra thư mục tạm cho spinner
            temp_dir = os.path.join(tempfile.gettempdir(), "telegram_uploader")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            spinner_path = os.path.join(temp_dir, "spinner.gif")
            
            # Kiểm tra nếu spinner đã tồn tại
            if os.path.exists(spinner_path):
                return spinner_path
            
            # Tạo spinner đơn giản bằng PyQt
            from PyQt5.QtCore import Qt, QSize
            from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QImage
            
            # Tạo spinner GIF giả lập đơn giản
            size = 40
            frames = 8
            images = []
            
            for i in range(frames):
                # Tạo QImage mới cho mỗi frame
                img = QImage(size, size, QImage.Format_ARGB32)
                img.fill(Qt.transparent)
                
                # Tạo painter và vẽ spinner
                painter = QPainter(img)
                painter.setRenderHint(QPainter.Antialiasing)
                
                # Tính toán các thông số cho spinner
                center = size / 2
                radius = size / 2 - 5
                start_angle = i * (360 / frames) * 16  # QPainter sử dụng 1/16 độ
                
                # Vẽ đường tròn nền mờ
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(200, 200, 200, 50)))
                painter.drawEllipse(5, 5, size - 10, size - 10)
                
                # Vẽ phần spinner quay
                gradient_colors = [(33, 150, 243, 50), (33, 150, 243, 255)]
                for j in range(5):  # 5 chấm gradient
                    angle = start_angle - j * 30 * 16
                    x = center + radius * 0.8 * math.cos(math.radians(angle / 16))
                    y = center + radius * 0.8 * math.sin(math.radians(angle / 16))
                    
                    alpha = 255 - j * 40  # Giảm dần độ mờ
                    color = QColor(33, 150, 243, max(50, alpha))
                    
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QBrush(color))
                    painter.drawEllipse(int(x - 5 + j), int(y - 5 + j), 10 - j, 10 - j)
                
                painter.end()
                images.append(img)
            
            # Lưu spinner thành GIF
            import imageio
            
            # Chuyển đổi QImage sang numpy array
            numpy_images = []
            for img in images:
                buffer = img.bits().asstring(img.width() * img.height() * 4)
                numpy_img = np.frombuffer(buffer, dtype=np.uint8).reshape((img.height(), img.width(), 4))
                numpy_img = numpy_img[:, :, [2, 1, 0, 3]]  # BGRA to RGBA
                numpy_images.append(numpy_img)
            
            # Lưu thành GIF
            imageio.mimsave(spinner_path, numpy_images, duration=0.1, loop=0)
            
            return spinner_path
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo spinner: {str(e)}")
            # Trả về None để sử dụng hiệu ứng chấm thay thế
            return None
    
    def set_message(self, message):
        """Thiết lập thông báo hiển thị"""
        self.message_label.setText(message)
    
    def show_spinner(self, show=True):
        """Hiển thị hoặc ẩn spinner"""
        if show:
            # Hiển thị spinner nếu có file
            if self.spinner_movie.fileName():
                self.spinner_movie.start()
                self.spinner_label.show()
            else:
                # Sử dụng hiệu ứng chấm nếu không có file
                if self.dots_timer is None:
                    self.dots_timer = self.startTimer(500)  # Cập nhật mỗi 0.5 giây
                self.spinner_label.setText("⏳")
                self.spinner_label.setStyleSheet("font-size: 24px; color: #3498DB;")
                self.spinner_label.show()
        else:
            # Dừng spinner
            if self.spinner_movie.fileName():
                self.spinner_movie.stop()
            
            # Dừng timer hiệu ứng chấm
            if self.dots_timer is not None:
                self.killTimer(self.dots_timer)
                self.dots_timer = None
            
            self.spinner_label.hide()
    
    def timerEvent(self, event):
        """Xử lý sự kiện timer cho hiệu ứng chấm"""
        if self.dots_timer is not None and event.timerId() == self.dots_timer:
            self.dots_count = (self.dots_count + 1) % 4
            dots = "." * self.dots_count
            
            # Thay đổi biểu tượng spinner
            if self.dots_count % 2 == 0:
                self.spinner_label.setText("⏳")
            else:
                self.spinner_label.setText("⌛")
    
    def showEvent(self, event):
        """Xử lý sự kiện hiện overlay"""
        # Bắt đầu spinner nếu có
        self.show_spinner(True)
        super(LoadingOverlay, self).showEvent(event)
    
    def hideEvent(self, event):
        """Xử lý sự kiện ẩn overlay"""
        # Dừng spinner
        self.show_spinner(False)
        super(LoadingOverlay, self).hideEvent(event)
    
    def resizeEvent(self, event):
        """Xử lý sự kiện thay đổi kích thước"""
        # Cập nhật kích thước cho container
        self.container.setFixedSize(min(self.width() - 40, 400), 200)
        super(LoadingOverlay, self).resizeEvent(event)

class PlayButton(QtWidgets.QPushButton):
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

class MainUI(QtWidgets.QMainWindow):
    """Main UI class that loads components directly from .ui files"""

    def __init__(self, app_instance=None):
        super(MainUI, self).__init__()

        # Store reference to the main application (if provided)
        self.app = app_instance

        # Data storage for videos
        self.all_videos = []  # Stores all video information
        self.videos = {}      # Maps video names to paths
        self.selected_video = None  # Currently selected video
        self.frame_paths = []  # Paths to video frames
        self.current_page = 1  # Current pagination page
        self.selected_video_count = 0  # Number of selected videos
        self.selected_videos_size = 0  # Total size of selected videos

        # Khởi tạo pagination manager
        self.pagination_manager = None

        # Set window properties
        self.setWindowTitle("Telegram Video Uploader")
        self.resize(1200, 800)

        # Set window to maximize on startup
        self.showMaximized()

        # Apply global stylesheet
        self.apply_global_stylesheet()

        # Create main widget and layout
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self.central_widget)
        self.loading_overlay.resize(self.central_widget.size())

        try:
            # Log module information
            logger.info(f"Module path: {__file__}")
            logger.info(f"PyQt5 imported: {QtWidgets.__file__}")
            
            # Load UI components from .ui files
            self.load_ui_components()

            # Connect signals
            self.connect_signals()
            
            # Update cursor properties
            self.update_cursor_properties()

            # Initialize video list
            self.initialize_folder()

            logger.info("Main UI initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing UI: {str(e)}")
            logger.error(traceback.format_exc())
            QtWidgets.QMessageBox.critical(self, "Error", f"Error initializing UI: {str(e)}")
    
    def update_video_preview_ui(self):
        """
        Cập nhật UI video_preview để thêm ScrollArea cho thông tin video
        """
        if not hasattr(self, 'video_preview'):
            return
            
        try:
            # Tìm info panel hiện tại
            info_panel = self.video_preview.findChild(QtWidgets.QWidget, "infoPanel")
            if not info_panel:
                logger.error("Không tìm thấy info panel")
                return
            
            # Lấy form layout hiện tại của info panel
            form_layout = info_panel.layout()
            if not form_layout or not isinstance(form_layout, QtWidgets.QFormLayout):
                logger.error("Form layout không hợp lệ")
                return
            
            # Tạo ScrollArea mới
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setObjectName("infoScrollArea")
            scroll_area.setWidgetResizable(True)
            scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
            scroll_area.setStyleSheet("""
                QScrollArea {
                    background-color: transparent;
                    border: none;
                }
                
                QScrollBar:vertical {
                    border: none;
                    background: #F1F5F9;
                    width: 8px;
                    border-radius: 4px;
                }
                
                QScrollBar::handle:vertical {
                    background: #CBD5E1;
                    min-height: 20px;
                    border-radius: 4px;
                }
                
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)
            
            # Tạo widget mới cho nội dung
            content_widget = QtWidgets.QWidget()
            content_widget.setObjectName("infoContent")
            
            # Chuyển layout từ info panel sang content widget
            new_form_layout = QtWidgets.QFormLayout(content_widget)
            new_form_layout.setHorizontalSpacing(30)
            new_form_layout.setVerticalSpacing(15)
            new_form_layout.setContentsMargins(15, 15, 15, 15)
            
            # Tạo các label mới với nội dung giới hạn chiều rộng
            fields = [
                ('fileNameLabel', 'fileNameValueLabel'), 
                ('durationLabel', 'durationValueLabel'),
                ('resolutionLabel', 'resolutionValueLabel'),
                ('sizeLabel', 'sizeValueLabel'),
                ('statusLabel', 'statusValueLabel'),
                ('codecLabel', 'codecValueLabel')
            ]
            
            for label_name, value_name in fields:
                label = info_panel.findChild(QtWidgets.QLabel, label_name)
                value = info_panel.findChild(QtWidgets.QLabel, value_name)
                
                if label and value:
                    # Tạo bản sao của label
                    new_label = QtWidgets.QLabel(label.text())
                    new_label.setObjectName(label_name)
                    new_label.setProperty("class", "infoLabel")
                    
                    # Tạo bản sao của value label với giới hạn chiều rộng
                    new_value = QtWidgets.QLabel(value.text())
                    new_value.setObjectName(value_name)
                    new_value.setProperty("class", "valueLabel")
                    new_value.setWordWrap(True)  # Cho phép ngắt dòng
                    new_value.setMaximumWidth(250)  # Giới hạn chiều rộng tối đa
                    
                    # Thiết lập tooltip cho hiển thị đầy đủ nội dung
                    if value.text():
                        new_value.setToolTip(value.text())
                    
                    # Áp dụng stylesheet tương ứng
                    if value_name == "statusValueLabel" and value.styleSheet():
                        new_value.setStyleSheet(value.styleSheet())
                    
                    # Thêm vào layout mới
                    new_form_layout.addRow(new_label, new_value)
            
            # Đặt widget nội dung vào scroll area
            scroll_area.setWidget(content_widget)
            
            # Xóa widget info panel cũ và thay bằng scroll area
            parent_layout = info_panel.parentWidget().layout()
            parent_index = parent_layout.indexOf(info_panel)
            
            # Xóa widget cũ khỏi layout
            parent_layout.removeWidget(info_panel)
            info_panel.setParent(None)
            
            # Thêm scroll area vào vị trí cũ
            parent_layout.insertWidget(parent_index, scroll_area)
            
            # Lưu tham chiếu mới
            self.info_scroll_area = scroll_area
            self.info_content = content_widget
            
            logger.info("Đã cập nhật thành công UI thông tin video với ScrollArea")
            
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật UI thông tin video: {str(e)}")
            logger.error(traceback.format_exc())
    
    def _update_pagination_ui(self, total_pages):
        """
        Cập nhật UI phân trang với cách tiếp cận đáng tin cậy hơn
        
        Args:
            total_pages: Tổng số trang
        """
        try:
            # Tìm pagination frame
            pagination_frame = self.video_list.findChild(QtWidgets.QFrame, "paginationFrame")
            if not pagination_frame:
                logger.error("Không tìm thấy pagination frame")
                return
                
            # Khởi tạo pagination manager nếu chưa tồn tại
            if not self.pagination_manager:
                from utils.pagination_utils import PaginationManager
                self.pagination_manager = PaginationManager(self)
                
                # Tạo các nút phân trang trong pagination frame
                self.pagination_manager.create_page_buttons(pagination_frame, total_pages)
                
                # Thiết lập các nút điều hướng
                setup_success = self.pagination_manager.setup_pagination(
                    pagination_frame=pagination_frame,
                    first_button=self.first_page_button,
                    prev_button=self.prev_page_button,
                    next_button=self.next_page_button,
                    last_button=self.last_page_button,
                    on_page_change=self.handle_page_change
                )
                
                if not setup_success:
                    logger.error("Không thể thiết lập pagination manager")
                    return
                
                logger.info("Đã khởi tạo pagination manager thành công")
            
            # Cập nhật pagination với trang hiện tại và tổng số trang
            self.pagination_manager.update_pagination(self.current_page, total_pages)
            
        except Exception as e:
            logger.error(f"Lỗi cập nhật UI phân trang: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

    def handle_page_change(self, new_page):
        """
        Xử lý khi có thay đổi trang từ pagination manager
        
        Args:
            new_page: Trang mới đã chọn
        """
        if self.current_page != new_page:
            self.current_page = new_page
            self.update_video_list_ui()

    def initialize_sort_dropdown(self):
        """
        Thiết lập dropdown sắp xếp video với tùy chọn mặc định
        """
        if not hasattr(self, 'sort_combo_box'):
            return
        
        try:
            # Xóa tất cả mục hiện tại
            self.sort_combo_box.clear()
            
            # Thêm các tùy chọn sắp xếp
            sort_options = [
                "Sắp xếp theo tên (A-Z)",  # Mặc định
                "Sắp xếp theo tên (Z-A)",
                "Kích thước (lớn → nhỏ)",
                "Kích thước (nhỏ → lớn)",
                "Thời lượng video (dài → ngắn)",
                "Thời lượng video (ngắn → dài)",
                "Ngày tạo (mới → cũ)",
                "Ngày tạo (cũ → mới)",
                "Trạng thái"
            ]
            
            for option in sort_options:
                self.sort_combo_box.addItem(option)
            
            # Thiết lập tùy chọn mặc định (A-Z)
            self.sort_combo_box.setCurrentIndex(0)
            
            # Kết nối sự kiện thay đổi
            self.sort_combo_box.currentIndexChanged.connect(self.sort_videos)
            
            # Áp dụng sắp xếp mặc định
            self.sort_videos(0)
            
            logger.info("Đã thiết lập dropdown sắp xếp thành công")
        except Exception as e:
            logger.error(f"Lỗi khi thiết lập dropdown sắp xếp: {str(e)}")
            logger.error(traceback.format_exc())

    def apply_global_stylesheet(self):
        """Apply global stylesheet to maintain the beautiful design"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #F9FAFB;
                font-family: Arial;
            }

            QPushButton {
                border-radius: 4px;
            }

            QLineEdit {
                padding: 8px;
            }

            QScrollArea {
                border: none;
                background-color: transparent;
            }

            QScrollBar:vertical {
                border: none;
                background: #F1F5F9;
                width: 8px;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical {
                background: #CBD5E1;
                min-height: 20px;
                border-radius: 4px;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar:horizontal {
                border: none;
                background: #F1F5F9;
                height: 8px;
                border-radius: 4px;
            }

            QScrollBar::handle:horizontal {
                background: #CBD5E1;
                min-width: 20px;
                border-radius: 4px;
            }

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            QToolTip {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #343434;
                border-radius: 4px;
                padding: 4px;
            }
        """)

    def load_ui_components(self):
        """Load all UI components from .ui files and assemble them"""
        # Main scroll area to enable scrolling for the whole content
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        # Container for all components
        self.scroll_content = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(0)  # Set to 0 to remove all spacing between components

        # Load header
        self.header = self.load_header()
        self.main_layout.addWidget(self.header)

        # Add 20px spacing after header
        spacer_after_header = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addItem(spacer_after_header)

        # Group folder selection and sub-tabs without spacing
        folder_tabs_container = QtWidgets.QWidget()
        folder_tabs_layout = QtWidgets.QVBoxLayout(folder_tabs_container)
        folder_tabs_layout.setContentsMargins(0, 0, 0, 0)
        folder_tabs_layout.setSpacing(0)  # No spacing between these components

        # Load folder selection and add to the group
        self.folder_selection = self.load_folder_selection()
        folder_tabs_layout.addWidget(self.folder_selection)

        # Load sub-tabs and add to the group
        self.sub_tabs = self.load_sub_tabs()
        folder_tabs_layout.addWidget(self.sub_tabs)

        # Add the grouped container to main layout
        self.scroll_layout.addWidget(folder_tabs_container)

        # Add spacing after the folder+tabs group
        spacer = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.scroll_layout.addItem(spacer)

        # Load video list and preview in a horizontal layout
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QHBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 0, 30, 0)

        self.video_list = self.load_video_list()
        content_layout.addWidget(self.video_list, 7)  # 70% width

        self.video_preview = self.load_video_preview()
        content_layout.addWidget(self.video_preview, 3)  # 30% width

        self.scroll_layout.addWidget(content_widget)

        # Load video frames with proper height
        self.video_frames = self.load_video_frames()
        self.scroll_layout.addWidget(self.video_frames)

        # Set scroll content and add to main layout
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        # Load action bar (always at bottom, not in scroll area)
        self.action_bar = self.load_action_bar()
        self.main_layout.addWidget(self.action_bar)

    def load_header(self):
        """Load header component from .ui file"""
        ui_path = os.path.join(self.get_ui_dir(), "header.ui")

        # Fix UI file before loading
        fixed_ui_path = self.fix_ui_file(ui_path)

        # Create widget and load UI
        header_widget = QtWidgets.QWidget()
        try:
            uic.loadUi(fixed_ui_path, header_widget)
            logger.info("Header UI loaded successfully")

            # Set up tab button group to handle exclusive selection
            tab_button_group = QtWidgets.QButtonGroup(header_widget)
            
            # Find all tab buttons
            tab_buttons = header_widget.findChildren(QtWidgets.QPushButton)
            
            # Add buttons to group and set initial state
            for i, button in enumerate(tab_buttons):
                tab_button_group.addButton(button, i)
                # Set first button as checked by default
                if i == 0:
                    button.setChecked(True)
            
            # Store button group
            self.header_tab_group = tab_button_group

            return header_widget
        except Exception as e:
            logger.error(f"Failed to load header UI: {str(e)}")
            # Fallback to a basic header if loading fails
            return self.create_fallback_header()

    def load_folder_selection(self):
        """Load folder selection component from .ui file"""
        ui_path = os.path.join(self.get_ui_dir(), "folder_selection.ui")

        # Fix UI file before loading
        fixed_ui_path = self.fix_ui_file(ui_path)

        # Create widget and load UI
        folder_widget = QtWidgets.QWidget()
        try:
            uic.loadUi(fixed_ui_path, folder_widget)
            logger.info("Folder selection UI loaded successfully")

            # Remove bottom margin to fit with sub-tabs
            folder_widget.setContentsMargins(30, 10, 30, 0)

            # Store reference to important controls
            self.folder_path_edit = folder_widget.findChild(QtWidgets.QLineEdit, "directoryLineEdit")
            self.browse_button = folder_widget.findChild(QtWidgets.QPushButton, "browseButton")
            self.refresh_button = folder_widget.findChild(QtWidgets.QPushButton, "refreshButton")
            self.recent_folders_combo = folder_widget.findChild(QtWidgets.QComboBox, "recentFoldersComboBox")
            self.folder_stats_label = folder_widget.findChild(QtWidgets.QLabel, "folderStatsLabel")
            
            # Clear mock data in recent folders combo
            self.recent_folders_combo.clear()
            self.recent_folders_combo.addItem("Thư mục gần đây")
            
            # Add tooltip to recent folders dropdown
            self.recent_folders_combo.setToolTip("Chọn thư mục từ danh sách thư mục gần đây")
            
            # Clear folder stats
            if self.folder_stats_label:
                self.folder_stats_label.setText("Tổng dung lượng: 0 B | 0 videos")

            return folder_widget
        except Exception as e:
            logger.error(f"Failed to load folder selection UI: {str(e)}")
            # Fallback to a basic folder selection if loading fails
            return self.create_fallback_folder_selection()

    def load_sub_tabs(self):
        """Load sub-tabs component from .ui file"""
        ui_path = os.path.join(self.get_ui_dir(), "sub_tabs.ui")

        # Fix UI file before loading
        fixed_ui_path = self.fix_ui_file(ui_path)

        # Create widget and load UI
        tabs_widget = QtWidgets.QWidget()
        try:
            uic.loadUi(fixed_ui_path, tabs_widget)
            logger.info("Sub-tabs UI loaded successfully")

            # Set up tab button group to handle exclusive selection
            tab_button_group = QtWidgets.QButtonGroup(tabs_widget)
            
            # Find all tab buttons
            tab_buttons = tabs_widget.findChildren(QtWidgets.QPushButton)
            
            # Add buttons to group and set cursor
            for i, button in enumerate(tab_buttons):
                tab_button_group.addButton(button, i)
                button.setEnabled(True)  # Ensure all buttons are enabled
            
            # Store button group
            self.subtab_group = tab_button_group

            # Remove top margin to fit with folder selection
            tabs_widget.setContentsMargins(30, 0, 30, 10)

            return tabs_widget
        except Exception as e:
            logger.error(f"Failed to load sub-tabs UI: {str(e)}")
            # Fallback to basic sub-tabs if loading fails
            return self.create_fallback_sub_tabs()

    def load_video_list(self):
        """Load video list component from .ui file"""
        ui_path = os.path.join(self.get_ui_dir(), "video_list.ui")

        # Fix UI file before loading
        fixed_ui_path = self.fix_ui_file(ui_path)

        # Create widget and load UI
        list_widget = QtWidgets.QWidget()
        try:
            uic.loadUi(fixed_ui_path, list_widget)
            logger.info("Video list UI loaded successfully")
            
            # Clear mock data from video list
            for i in range(1, 11):
                videoItem = list_widget.findChild(QtWidgets.QFrame, f"videoItem{i}")
                label = list_widget.findChild(QtWidgets.QLabel, f"label{i}")
                status = list_widget.findChild(QtWidgets.QLabel, f"status{i}")
                checkbox = list_widget.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
                
                if videoItem:
                    videoItem.setVisible(False)  # Hide all rows initially
                
                if label:
                    label.setText("")  # Clear label text
                
                if status:
                    status.setText("")  # Clear status
                
                if checkbox:
                    checkbox.setChecked(False)  # Uncheck all checkboxes
                
                # Make entire row clickable to toggle checkbox and select video
                if videoItem:
                    videoItem.mousePressEvent = lambda event, idx=i: self.on_video_row_clicked(idx)

            # Clear pagination info
            pagination_info = list_widget.findChild(QtWidgets.QLabel, "paginationInfoLabel")
            if pagination_info:
                pagination_info.setText("Hiển thị 0-0 trên tổng 0 videos")

            # Store references to controls
            self.duplicate_check_box = list_widget.findChild(QtWidgets.QCheckBox, "duplicateCheckBox")
            self.history_check_box = list_widget.findChild(QtWidgets.QCheckBox, "historyCheckBox")
            self.search_line_edit = list_widget.findChild(QtWidgets.QLineEdit, "searchLineEdit")
            self.sort_combo_box = list_widget.findChild(QtWidgets.QComboBox, "sortComboBox")
            self.pagination_info_label = list_widget.findChild(QtWidgets.QLabel, "paginationInfoLabel")
            
            # Get pagination buttons and đặt các nút phân trang cố định về None vì đã loại bỏ khỏi UI
            self.page1_button = None
            self.page2_button = None
            self.next_page_button = list_widget.findChild(QtWidgets.QPushButton, "nextPageButton")
            self.prev_page_button = list_widget.findChild(QtWidgets.QPushButton, "prevPageButton")
            self.first_page_button = list_widget.findChild(QtWidgets.QPushButton, "firstPageButton")
            self.last_page_button = list_widget.findChild(QtWidgets.QPushButton, "lastPageButton")

            # Add shadow effect
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QtGui.QColor(0, 0, 0, 30))
            shadow.setOffset(0, 2)
            list_widget.setGraphicsEffect(shadow)

            # Add bottom margin to prevent shadow clipping
            list_widget.setContentsMargins(
                list_widget.contentsMargins().left(),
                list_widget.contentsMargins().top(),
                list_widget.contentsMargins().right(),
                list_widget.contentsMargins().bottom() + 15
            )

            return list_widget
        except Exception as e:
            logger.error(f"Failed to load video list UI: {str(e)}")
            # Fallback to a basic video list if loading fails
            return self.create_fallback_video_list()
    def load_video_preview(self):
        """Load video preview component from .ui file"""
        ui_path = os.path.join(self.get_ui_dir(), "video_preview.ui")

        # Fix UI file before loading
        fixed_ui_path = self.fix_ui_file(ui_path)

        # Create widget and load UI
        preview_widget = QtWidgets.QWidget()
        try:
            uic.loadUi(fixed_ui_path, preview_widget)
            logger.info("Video preview UI loaded successfully")
            
            # Clear mock data
            for field in ['fileNameValueLabel', 'durationValueLabel', 'resolutionValueLabel', 
                        'sizeValueLabel', 'statusValueLabel', 'codecValueLabel']:
                label = preview_widget.findChild(QtWidgets.QLabel, field)
                if label:
                    label.setText("")

            # Add custom SVG play button
            play_button_container = preview_widget.findChild(QtWidgets.QWidget, "playButtonContainer")
            if play_button_container:
                layout = QtWidgets.QVBoxLayout(play_button_container)
                layout.setContentsMargins(0, 0, 0, 0)
                
                # Create and add the custom play button
                self.play_button = PlayButton(play_button_container)
                layout.addWidget(self.play_button)
                
                # Connect click handler
                self.play_button.clicked.connect(self.view_video)

            # Add shadow effect
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QtGui.QColor(0, 0, 0, 30))
            shadow.setOffset(0, 2)
            preview_widget.setGraphicsEffect(shadow)

            # Store reference to important controls
            self.view_button = preview_widget.findChild(QtWidgets.QPushButton, "viewVideoButton")
            self.upload_this_button = preview_widget.findChild(QtWidgets.QPushButton, "uploadThisVideoButton")

            return preview_widget
        except Exception as e:
            logger.error(f"Failed to load video preview UI: {str(e)}")
            logger.error(traceback.format_exc())
            # Fallback to a basic video preview if loading fails
            return self.create_fallback_video_preview()

    def load_video_frames(self):
        """Load video frames component from .ui file"""
        ui_path = os.path.join(self.get_ui_dir(), "video_frames.ui")

        # Fix UI file before loading
        fixed_ui_path = self.fix_ui_file(ui_path)

        # Create widget and load UI
        frames_widget = QtWidgets.QWidget()
        try:
            uic.loadUi(fixed_ui_path, frames_widget)
            logger.info("Video frames UI loaded successfully")

            # Add padding to scroll area for proper scrolling
            frames_scroll_area = frames_widget.findChild(QtWidgets.QScrollArea, "framesScrollArea")
            if frames_scroll_area:
                frames_scroll_area.setStyleSheet("""
                    QScrollArea {
                        padding: 15px;
                        border: none;
                    }
                    
                    QScrollArea > QWidget > QWidget {
                        padding: 15px;
                    }
                """)

            # Prepare frame widgets for easy access and clear any existing content
            for i in range(1, 6):  # 5 frame containers
                frame_widget = frames_widget.findChild(QtWidgets.QFrame, f"frame{i}")
                if frame_widget:
                    # Clear existing content and setup layout
                    if frame_widget.layout():
                        while frame_widget.layout().count():
                            item = frame_widget.layout().takeAt(0)
                            widget = item.widget()
                            if widget:
                                widget.deleteLater()
                    else:
                        layout = QtWidgets.QVBoxLayout(frame_widget)
                        layout.setContentsMargins(0, 0, 0, 0)
                        layout.setAlignment(QtCore.Qt.AlignCenter)

            # Add shadow effect
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QtGui.QColor(0, 0, 0, 30))
            shadow.setOffset(0, 2)
            frames_widget.setGraphicsEffect(shadow)

            return frames_widget
        except Exception as e:
            logger.error(f"Failed to load video frames UI: {str(e)}")
            # Fallback to a basic video frames if loading fails
            return self.create_fallback_video_frames()

    def load_action_bar(self):
        """Load action bar component from .ui file"""
        ui_path = os.path.join(self.get_ui_dir(), "action_bar.ui")

        # Fix UI file before loading
        fixed_ui_path = self.fix_ui_file(ui_path)

        # Create widget and load UI
        action_bar_widget = QtWidgets.QWidget()
        try:
            uic.loadUi(fixed_ui_path, action_bar_widget)
            logger.info("Action bar UI loaded successfully")

            # Make it look nice
            action_bar_widget.setContentsMargins(30, 5, 30, 10)

            # Store reference to important controls
            self.select_all_button = action_bar_widget.findChild(QtWidgets.QPushButton, "selectAllButton")
            self.deselect_all_button = action_bar_widget.findChild(QtWidgets.QPushButton, "deselectAllButton")
            self.select_unuploaded_button = action_bar_widget.findChild(QtWidgets.QPushButton, "selectUnuploadedButton")
            self.upload_button = action_bar_widget.findChild(QtWidgets.QPushButton, "uploadButton")
            self.selection_label = action_bar_widget.findChild(QtWidgets.QLabel, "selectionLabel")
            
            # Clear mock data
            if self.selection_label:
                self.selection_label.setText("Đã chọn: 0 video | Tổng dung lượng: 0 B")

            # Add shadow effect
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QtGui.QColor(0, 0, 0, 30))
            shadow.setOffset(0, 2)
            action_bar_widget.setGraphicsEffect(shadow)

            return action_bar_widget
        except Exception as e:
            logger.error(f"Failed to load action bar UI: {str(e)}")
            # Fallback to a basic action bar if loading fails
            return self.create_fallback_action_bar()

    # Helper methods
    def get_ui_dir(self):
        """Get the directory containing UI files"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "qt_designer", "main_tab")

    def fix_ui_file(self, ui_path):
        """Fix UI file compatibility issues with PyQt5"""
        # Check if file exists
        if not os.path.exists(ui_path):
            logger.error(f"UI file not found: {ui_path}")
            return ui_path

        try:
            with open(ui_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix orientation attributes
            content = content.replace('Qt::Orientation::Horizontal', 'Horizontal')
            content = content.replace('Qt::Orientation::Vertical', 'Vertical')
            
            # Fix property="cursor" issues
            content = content.replace('property="cursor"', 'property="cursorShape"')
            
            # Fix alignment property for buttons
            content = content.replace('property="alignment"', 'property="alignmentProperty"')

            # Create a temporary file with fixed content
            import tempfile
            temp = tempfile.NamedTemporaryFile(delete=False, suffix='.ui')
            temp_path = temp.name

            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Fixed UI file {ui_path} -> {temp_path}")
            return temp_path
        except Exception as e:
            logger.error(f"Error fixing UI file {ui_path}: {str(e)}")
            return ui_path

    def update_cursor_properties(self):
        """Update cursor properties for all interactive elements"""
        # List of widgets that should have pointing hand cursor
        if hasattr(self, 'browse_button') and self.browse_button:
            self.browse_button.setCursor(QtCore.Qt.PointingHandCursor)
        
        if hasattr(self, 'refresh_button') and self.refresh_button:
            self.refresh_button.setCursor(QtCore.Qt.PointingHandCursor)
        
        if hasattr(self, 'view_button') and self.view_button:
            self.view_button.setCursor(QtCore.Qt.PointingHandCursor)
        
        if hasattr(self, 'play_button') and self.play_button:
            self.play_button.setCursor(QtCore.Qt.PointingHandCursor)
        
        if hasattr(self, 'upload_this_button') and self.upload_this_button:
            self.upload_this_button.setCursor(QtCore.Qt.PointingHandCursor)
        
        if hasattr(self, 'select_all_button') and self.select_all_button:
            self.select_all_button.setCursor(QtCore.Qt.PointingHandCursor)
        
        if hasattr(self, 'deselect_all_button') and self.deselect_all_button:
            self.deselect_all_button.setCursor(QtCore.Qt.PointingHandCursor)
        
        if hasattr(self, 'select_unuploaded_button') and self.select_unuploaded_button:
            self.select_unuploaded_button.setCursor(QtCore.Qt.PointingHandCursor)
        
        if hasattr(self, 'upload_button') and self.upload_button:
            self.upload_button.setCursor(QtCore.Qt.PointingHandCursor)
        
        # Handle video rows
        if hasattr(self, 'video_list'):
            for i in range(1, 11):
                videoItem = self.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
                if videoItem:
                    videoItem.setCursor(QtCore.Qt.PointingHandCursor)
        
        # Handle video frames
        if hasattr(self, 'video_frames'):
            for i in range(1, 6):
                frame = self.video_frames.findChild(QtWidgets.QFrame, f"frame{i}")
                if frame:
                    frame.setCursor(QtCore.Qt.PointingHandCursor)
                    
        # Handle pagination buttons - Loại bỏ kiểm tra các nút không còn tồn tại
        if hasattr(self, 'next_page_button') and self.next_page_button:
            self.next_page_button.setCursor(QtCore.Qt.PointingHandCursor)
        if hasattr(self, 'prev_page_button') and self.prev_page_button:
            self.prev_page_button.setCursor(QtCore.Qt.PointingHandCursor)
        if hasattr(self, 'first_page_button') and self.first_page_button:
            self.first_page_button.setCursor(QtCore.Qt.PointingHandCursor)
        if hasattr(self, 'last_page_button') and self.last_page_button:
            self.last_page_button.setCursor(QtCore.Qt.PointingHandCursor)
            
        # Handle tab buttons
        if hasattr(self, 'header_tab_group'):
            for button in self.header_tab_group.buttons():
                button.setCursor(QtCore.Qt.PointingHandCursor)
                
        if hasattr(self, 'subtab_group'):
            for button in self.subtab_group.buttons():
                button.setCursor(QtCore.Qt.PointingHandCursor)

    def on_video_row_clicked(self, idx):
        """Handle click on a video row"""
        # Toggle checkbox
        checkbox = self.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{idx}")
        if checkbox:
            checkbox.setChecked(not checkbox.isChecked())
            logger.info(f"Toggled checkbox {idx}: {checkbox.isChecked()}")
            
            # Update selection count
            self.update_selection_count()
        
        # Get video name
        label = self.video_list.findChild(QtWidgets.QLabel, f"label{idx}")
        if label:
            video_name = label.text()
            self.selected_video = video_name
            logger.info(f"Selected video: {video_name}")
            
            # Display video information
            self.display_selected_video()

    def update_selection_count(self):
        """Update the selection count in the action bar"""
        if not hasattr(self, 'selection_label'):
            return
            
        # Reset counters
        self.selected_video_count = 0
        self.selected_videos_size = 0
        
        # Count selected videos
        for i in range(1, 11):  # Assuming up to 10 videos displayed at once
            checkbox = self.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
            row = self.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
            
            # Only count if checkbox exists, is checked, and row is visible
            if checkbox and row and checkbox.isChecked() and row.isVisible():
                self.selected_video_count += 1
                
                # Find video info in all_videos
                label = self.video_list.findChild(QtWidgets.QLabel, f"label{i}")
                if label:
                    video_name = label.text()
                    for video in self.all_videos:
                        if video.get("name") == video_name:
                            self.selected_videos_size += video.get("file_size_bytes", 0)
                            break
        
        # Format total size
        size_str = self.format_file_size(self.selected_videos_size)
        
        # Update label
        self.selection_label.setText(f"Đã chọn: {self.selected_video_count} video | Tổng dung lượng: {size_str}")

    def format_file_size(self, size_in_bytes):
        """Format file size in bytes to human-readable string"""
        if size_in_bytes < 1024:
            return f"{size_in_bytes} B"
        elif size_in_bytes < 1024 * 1024:
            return f"{size_in_bytes / 1024:.1f} KB"
        elif size_in_bytes < 1024 * 1024 * 1024:
            return f"{size_in_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} GB"

    def display_selected_video(self):
        """Display information about the selected video"""
        if not self.selected_video:
            return
        
        # Find video path
        video_path = None
        for video in self.all_videos:
            if video.get("name") == self.selected_video:
                video_path = video.get("path")
                break
        
        if not video_path or not os.path.exists(video_path):
            logger.error(f"Video file not found: {self.selected_video}")
            return
        
        # Display video info in the preview
        display_video_info(self, video_path)
        
        # Display video frames
        display_video_frames(self, video_path)

    # Fallback UI creation methods
    def create_fallback_header(self):
        widget = QtWidgets.QWidget()
        widget.setObjectName("Header")
        widget.setMinimumHeight(70)
        widget.setMaximumHeight(70)
        
        layout = QtWidgets.QHBoxLayout(widget)
        
        logo = QtWidgets.QLabel("HENLLADEV")
        logo.setStyleSheet("font-size: 28px; font-weight: bold; color: #3498DB;")
        layout.addWidget(logo)
        
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addItem(spacer)
        
        return widget
    
    def create_fallback_folder_selection(self):
        widget = QtWidgets.QWidget()
        widget.setObjectName("FolderSelection")
        
        layout = QtWidgets.QHBoxLayout(widget)
        
        label = QtWidgets.QLabel("Thư mục chứa video")
        layout.addWidget(label)
        
        self.folder_path_edit = QtWidgets.QLineEdit()
        layout.addWidget(self.folder_path_edit)
        
        self.browse_button = QtWidgets.QPushButton("Duyệt")
        layout.addWidget(self.browse_button)
        
        return widget
    
    def create_fallback_sub_tabs(self):
        widget = QtWidgets.QWidget()
        widget.setObjectName("SubTabs")
        
        layout = QtWidgets.QHBoxLayout(widget)
        
        tab1 = QtWidgets.QPushButton("Tải lên thủ công")
        tab1.setObjectName("activeTab")
        layout.addWidget(tab1)
        
        tab2 = QtWidgets.QPushButton("Tự động tải lên")
        tab2.setObjectName("inactiveTab")
        layout.addWidget(tab2)
        
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addItem(spacer)
        
        return widget
    
    def create_fallback_video_list(self):
        widget = QtWidgets.QWidget()
        widget.setObjectName("VideoList")
        
        layout = QtWidgets.QVBoxLayout(widget)
        
        title = QtWidgets.QLabel("Danh sách video")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        # Would add more elements here in a real implementation
        
        return widget
    
    def create_fallback_video_preview(self):
        widget = QtWidgets.QWidget()
        widget.setObjectName("VideoPreview")
        
        layout = QtWidgets.QVBoxLayout(widget)
        
        title = QtWidgets.QLabel("Xem trước video")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        # Create a preview frame
        preview_frame = QtWidgets.QFrame()
        preview_frame.setMinimumHeight(250)
        preview_frame.setStyleSheet("background-color: #F2F6FC; border-radius: 8px;")
        frame_layout = QtWidgets.QVBoxLayout(preview_frame)
        
        # Add custom play button
        self.play_button = PlayButton()
        frame_layout.addWidget(self.play_button, 0, Qt.AlignCenter)
        
        layout.addWidget(preview_frame)
        
        # Add buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.view_button = QtWidgets.QPushButton("Xem video")
        self.view_button.setMinimumHeight(45)
        self.upload_this_button = QtWidgets.QPushButton("Tải lên video này")
        self.upload_this_button.setMinimumHeight(45)
        
        button_layout.addWidget(self.view_button)
        button_layout.addWidget(self.upload_this_button)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def create_fallback_video_frames(self):
        widget = QtWidgets.QWidget()
        widget.setObjectName("VideoFrames")
        
        layout = QtWidgets.QVBoxLayout(widget)
        
        title = QtWidgets.QLabel("Các khung hình từ video")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        # Would add more elements here in a real implementation
        
        return widget
    
    def create_fallback_action_bar(self):
        widget = QtWidgets.QWidget()
        widget.setObjectName("ActionBar")
        
        layout = QtWidgets.QHBoxLayout(widget)
        
        self.select_all_button = QtWidgets.QPushButton("Chọn tất cả")
        layout.addWidget(self.select_all_button)
        
        self.deselect_all_button = QtWidgets.QPushButton("Bỏ chọn tất cả")
        layout.addWidget(self.deselect_all_button)
        
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addItem(spacer)
        
        self.upload_button = QtWidgets.QPushButton("Tải lên")
        layout.addWidget(self.upload_button)
        
        return widget

    def connect_signals(self):
        """Connect signals to slots"""
        try:
            # Connect folder selection browse button if found
            if hasattr(self, 'browse_button') and self.browse_button:
                self.browse_button.clicked.connect(self.browse_folder)

            # Connect refresh button
            if hasattr(self, 'refresh_button') and self.refresh_button:
                self.refresh_button.clicked.connect(self.refresh_folder)

            # Connect view buttons
            if hasattr(self, 'view_button') and self.view_button:
                self.view_button.clicked.connect(self.view_video)

            if hasattr(self, 'play_button') and self.play_button:
                self.play_button.clicked.connect(self.view_video)

            # Connect upload buttons
            if hasattr(self, 'upload_this_button') and self.upload_this_button:
                self.upload_this_button.clicked.connect(self.upload_current_video)

            if hasattr(self, 'upload_button') and self.upload_button:
                self.upload_button.clicked.connect(self.upload_selected_videos)

            # Connect selection buttons
            if hasattr(self, 'select_all_button') and self.select_all_button:
                self.select_all_button.clicked.connect(self.select_all_videos)

            if hasattr(self, 'deselect_all_button') and self.deselect_all_button:
                self.deselect_all_button.clicked.connect(self.deselect_all_videos)

            if hasattr(self, 'select_unuploaded_button') and self.select_unuploaded_button:
                self.select_unuploaded_button.clicked.connect(self.select_unuploaded_videos)
                
            # Connect header tab buttons
            if hasattr(self, 'header_tab_group') and self.header_tab_group:
                self.header_tab_group.buttonClicked.connect(self.header_tab_clicked)
                
            # Connect sub-tab buttons
            if hasattr(self, 'subtab_group') and self.subtab_group:
                self.subtab_group.buttonClicked.connect(self.subtab_clicked)
            
            # Connect check boxes for video filtering
            if hasattr(self, 'duplicate_check_box') and self.duplicate_check_box:
                self.duplicate_check_box.stateChanged.connect(self.refresh_folder)
                
            if hasattr(self, 'history_check_box') and self.history_check_box:
                self.history_check_box.stateChanged.connect(self.refresh_folder)
                
            # Connect recent folders combo box
            if hasattr(self, 'recent_folders_combo') and self.recent_folders_combo:
                self.recent_folders_combo.currentIndexChanged.connect(self.load_recent_folder)
                
            # Connect search line edit
            if hasattr(self, 'search_line_edit') and self.search_line_edit:
                self.search_line_edit.textChanged.connect(self.filter_videos)
                
            # Connect sort combo box
            if hasattr(self, 'sort_combo_box') and self.sort_combo_box:
                self.sort_combo_box.currentIndexChanged.connect(self.sort_videos)
                
            # Connect pagination buttons - loại bỏ các nút trang cố định và chỉ kết nối các nút điều hướng
            if hasattr(self, 'next_page_button') and self.next_page_button:
                self.next_page_button.clicked.connect(self.next_page)
            if hasattr(self, 'prev_page_button') and self.prev_page_button:
                self.prev_page_button.clicked.connect(self.prev_page)
            if hasattr(self, 'first_page_button') and self.first_page_button:
                self.first_page_button.clicked.connect(lambda: self.go_to_page(1))
            if hasattr(self, 'last_page_button') and self.last_page_button:
                self.last_page_button.clicked.connect(self.last_page)
                
            logger.info("All signals connected successfully")
        except Exception as e:
            logger.error(f"Error connecting signals: {str(e)}")
            logger.error(traceback.format_exc())
    def header_tab_clicked(self, button):
        """Handle header tab button clicks"""
        # Set clicked button as checked, others as unchecked
        for btn in self.header_tab_group.buttons():
            btn.setChecked(btn == button)
        
        # Get the index of the clicked button
        index = self.header_tab_group.id(button)
        
        # Log the click
        logger.info(f"Header tab {index} clicked: {button.text()}")
        
        # Handle different tabs
        if index == 0:  # Upload tab
            # Already on this tab, do nothing
            pass
        else:
            # For other tabs, show development message
            QtWidgets.QMessageBox.information(
                self, 
                "Chức năng đang phát triển", 
                f"Chức năng '{button.text()}' đang được phát triển và sẽ có sẵn trong phiên bản tiếp theo."
            )
            
            # Reset to upload tab
            for btn in self.header_tab_group.buttons():
                if self.header_tab_group.id(btn) == 0:
                    btn.setChecked(True)
                else:
                    btn.setChecked(False)

    def subtab_clicked(self, button):
        """Handle sub-tab button clicks"""
        # Set clicked button as checked, others as unchecked
        for btn in self.subtab_group.buttons():
            if btn.objectName() == "activeTab":
                btn.setObjectName("inactiveTab")
                btn.setStyleSheet("")  # Remove any custom style
        
        # Set the clicked button as active
        button.setObjectName("activeTab")
        button.setStyleSheet("""
            color: #3498DB;
            border-bottom: 3px solid #3498DB;
            background-color: #EBF5FB;
            font-weight: bold;
        """)
        
        # Get the index of the clicked button
        index = self.subtab_group.id(button)
        
        # Log the click
        logger.info(f"Sub-tab clicked: {button.text()}")
        
        # Handle different sub-tabs
        if index == 0:  # Manual upload
            # Already on this tab, do nothing
            pass
        else:
            # For other sub-tabs, show development message
            QtWidgets.QMessageBox.information(
                self, 
                "Chức năng đang phát triển", 
                f"Chức năng '{button.text()}' đang được phát triển và sẽ có sẵn trong phiên bản tiếp theo."
            )
            
            # Reset to manual upload tab
            for btn in self.subtab_group.buttons():
                if self.subtab_group.id(btn) == 0:
                    btn.setObjectName("activeTab")
                    btn.setStyleSheet("""
                        color: #3498DB;
                        border-bottom: 3px solid #3498DB;
                        background-color: #EBF5FB;
                        font-weight: bold;
                    """)
                else:
                    btn.setObjectName("inactiveTab")
                    btn.setStyleSheet("")

    # Event handler methods
    def initialize_folder(self):
        """Initialize folder from saved settings"""
        # Load recent folders from config
        self.load_recent_folders_from_config()
        
        # Try to get folder from app config
        folder_path = ""
        if hasattr(self, 'app') and hasattr(self.app, 'config'):
            # Check if config is a ConfigParser object or a dictionary
            if hasattr(self.app.config, 'get') and callable(self.app.config.get):
                try:
                    # Check if it's ConfigParser object
                    if hasattr(self.app.config, 'has_section') and self.app.config.has_section('SETTINGS'):
                        folder_path = self.app.config.get('SETTINGS', 'video_folder')
                    # Otherwise treat as dictionary
                    elif isinstance(self.app.config, dict) and 'SETTINGS' in self.app.config:
                        settings = self.app.config.get('SETTINGS', {})
                        if isinstance(settings, dict):
                            folder_path = settings.get('video_folder', '')
                except Exception as e:
                    logger.error(f"Error getting folder path from config: {str(e)}")
        
        # Set folder path and refresh
        if folder_path and os.path.exists(folder_path) and os.path.isdir(folder_path):
            self.folder_path_edit.setText(folder_path)
            self.refresh_folder()

    def load_recent_folders_from_config(self):
        """Load recent folders from config"""
        if not hasattr(self, 'recent_folders_combo'):
            return
                
        # Clear existing items except the first one (header)
        while self.recent_folders_combo.count() > 1:
            self.recent_folders_combo.removeItem(1)
        
        # Try to get recent folders from config
        try:
            if hasattr(self, 'app') and hasattr(self.app, 'config'):
                # Check if config is ConfigParser or dictionary
                if hasattr(self.app.config, 'has_section') and callable(self.app.config.has_section):
                    # ConfigParser approach
                    if self.app.config.has_section('RECENT_FOLDERS'):
                        # Load each folder from config
                        for i in range(10):  # Load up to 10 recent folders
                            key = f"folder_{i}"
                            try:
                                if self.app.config.has_option('RECENT_FOLDERS', key):
                                    folder = self.app.config.get('RECENT_FOLDERS', key)
                                    if folder and os.path.exists(folder):
                                        self.recent_folders_combo.addItem(folder)
                            except Exception as e:
                                logger.error(f"Error loading folder {i} from config: {str(e)}")
                
                # Dictionary approach
                elif isinstance(self.app.config, dict) and 'RECENT_FOLDERS' in self.app.config:
                    recent_folders = self.app.config.get('RECENT_FOLDERS', {})
                    if isinstance(recent_folders, dict):
                        # Load each folder from config
                        for i in range(10):  # Load up to 10 recent folders
                            key = f"folder_{i}"
                            if key in recent_folders:
                                folder = recent_folders.get(key)
                                if folder and os.path.exists(folder):
                                    self.recent_folders_combo.addItem(folder)
                
                # If no RECENT_FOLDERS section exists yet and config_manager is available
                elif hasattr(self.app, 'config_manager'):
                    if isinstance(self.app.config, dict):
                        self.app.config['RECENT_FOLDERS'] = {}
                        self.app.config_manager.save_config(self.app.config)
            
            # Direct approach in case app or app.config is not available
            else:
                # Try to load directly from config.ini file
                config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.ini')
                if os.path.exists(config_path):
                    import configparser
                    config = configparser.ConfigParser()
                    config.read(config_path, encoding='utf-8')
                    
                    if 'RECENT_FOLDERS' in config:
                        for i in range(10):
                            key = f"folder_{i}"
                            if config.has_option('RECENT_FOLDERS', key):
                                folder = config.get('RECENT_FOLDERS', key)
                                if folder and os.path.exists(folder):
                                    self.recent_folders_combo.addItem(folder)
        except Exception as e:
            logger.error(f"Error loading recent folders from config: {str(e)}")

    def save_recent_folders_to_config(self):
        """Save recent folders to config"""
        if not hasattr(self, 'recent_folders_combo'):
            return
                
        # Try to save to app.config if available
        try:
            if hasattr(self, 'app') and hasattr(self.app, 'config'):
                # Check if app.config is ConfigParser or dictionary
                if hasattr(self.app.config, 'has_section') and callable(self.app.config.has_section):
                    # ConfigParser approach
                    if not self.app.config.has_section('RECENT_FOLDERS'):
                        self.app.config.add_section('RECENT_FOLDERS')
                    
                    # Clear existing entries
                    for option in self.app.config.options('RECENT_FOLDERS'):
                        if option.startswith('folder_'):
                            self.app.config.remove_option('RECENT_FOLDERS', option)
                    
                    # Save current folders - QUAN TRỌNG: bắt đầu từ 0 để đúng với định dạng folder_0, folder_1,... 
                    folder_count = 0
                    for i in range(1, min(self.recent_folders_combo.count(), 11)):
                        # Lấy đường dẫn đầy đủ từ userData, nếu không có thì lấy từ text
                        folder = self.recent_folders_combo.itemData(i, Qt.UserRole)
                        if not folder:  # Nếu không có userData
                            folder = self.recent_folders_combo.itemText(i)
                            
                        # Kiểm tra đường dẫn hợp lệ trước khi lưu
                        if folder and os.path.isdir(folder):
                            self.app.config.set('RECENT_FOLDERS', f"folder_{folder_count}", os.path.normpath(folder))
                            folder_count += 1
                    
                    # Save config if config_manager available
                    if hasattr(self.app, 'config_manager'):
                        self.app.config_manager.save_config(self.app.config)
                
                # Dictionary approach
                elif isinstance(self.app.config, dict):
                    # Create RECENT_FOLDERS section if it doesn't exist
                    if 'RECENT_FOLDERS' not in self.app.config:
                        self.app.config['RECENT_FOLDERS'] = {}
                    elif not isinstance(self.app.config['RECENT_FOLDERS'], dict):
                        self.app.config['RECENT_FOLDERS'] = {}
                    
                    # Clear existing entries
                    for key in list(self.app.config['RECENT_FOLDERS'].keys()):
                        if key.startswith('folder_'):
                            del self.app.config['RECENT_FOLDERS'][key]
                    
                    # Save current folders - QUAN TRỌNG: bắt đầu từ 0 để đúng với định dạng folder_0, folder_1,...
                    folder_count = 0
                    for i in range(1, min(self.recent_folders_combo.count(), 11)):
                        # Lấy đường dẫn đầy đủ từ userData, nếu không có thì lấy từ text
                        folder = self.recent_folders_combo.itemData(i, Qt.UserRole)
                        if not folder:  # Nếu không có userData
                            folder = self.recent_folders_combo.itemText(i)
                            
                        # Kiểm tra đường dẫn hợp lệ trước khi lưu
                        if folder and os.path.isdir(folder):
                            self.app.config['RECENT_FOLDERS'][f"folder_{folder_count}"] = os.path.normpath(folder)
                            folder_count += 1
                    
                    # Save config
                    if hasattr(self.app, 'config_manager'):
                        self.app.config_manager.save_config(self.app.config)
            
            # Direct approach in case app or app.config is not available
            else:
                # Try to save directly to config.ini file
                config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.ini')
                import configparser
                config = configparser.ConfigParser()
                
                # Load existing config if available
                if os.path.exists(config_path):
                    config.read(config_path, encoding='utf-8')
                
                # Create RECENT_FOLDERS section if it doesn't exist
                if 'RECENT_FOLDERS' not in config:
                    config['RECENT_FOLDERS'] = {}
                
                # Clear existing entries
                for key in list(config['RECENT_FOLDERS'].keys()):
                    if key.startswith('folder_'):
                        del config['RECENT_FOLDERS'][key]
                
                # Save current folders
                for i in range(1, min(self.recent_folders_combo.count(), 11)):
                    # Lấy đường dẫn đầy đủ từ userData, nếu không có thì lấy từ text
                    folder = self.recent_folders_combo.itemData(i, Qt.UserRole)
                    if not folder:  # Nếu không có userData
                        folder = self.recent_folders_combo.itemText(i)
                    config['RECENT_FOLDERS'][f"folder_{i-1}"] = folder
                
                # Write to file
                with open(config_path, 'w', encoding='utf-8') as f:
                    config.write(f)
                    
        except Exception as e:
            logger.error(f"Error saving recent folders to config file: {str(e)}")
            logger.error(traceback.format_exc())

    def browse_folder(self):
        """Open file dialog to browse for folder"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Chọn thư mục chứa video", "",
            QtWidgets.QFileDialog.ShowDirsOnly
        )

        if folder:
            self.folder_path_edit.setText(folder)
            logger.info(f"Selected folder: {folder}")
            
            # Refresh video list
            self.refresh_folder()
            
            # Save to recent folders
            self.add_to_recent_folders(folder)
            
            # Save to app config
            if hasattr(self, 'app') and hasattr(self.app, 'config') and hasattr(self.app, 'config_manager'):
                try:
                    # Check if config is ConfigParser or dictionary
                    if hasattr(self.app.config, 'has_section') and callable(self.app.config.has_section):
                        # ConfigParser approach
                        if not self.app.config.has_section('SETTINGS'):
                            self.app.config.add_section('SETTINGS')
                        self.app.config.set('SETTINGS', 'video_folder', folder)
                    else:
                        # Dictionary approach
                        if 'SETTINGS' not in self.app.config:
                            self.app.config['SETTINGS'] = {}
                        self.app.config['SETTINGS']['video_folder'] = folder
                    
                    # Save config
                    self.app.config_manager.save_config(self.app.config)
                except Exception as e:
                    logger.error(f"Error saving folder to config: {str(e)}")

    def add_to_recent_folders(self, folder_path):
        """Add folder to recent folders dropdown - IMPROVED"""
        if not hasattr(self, 'recent_folders_combo'):
            logger.error("recent_folders_combo không tồn tại")
            return
            
        # Đảm bảo đường dẫn đầy đủ - chuẩn hóa đường dẫn để tránh các phiên bản khác nhau của cùng đường dẫn
        folder_path = os.path.normpath(os.path.abspath(folder_path))
        
        # Kiểm tra xem thư mục có tồn tại
        if not os.path.isdir(folder_path):
            logger.warning(f"Thư mục không tồn tại hoặc không phải thư mục: {folder_path}")
            return
            
        # Tạm thời ngắt kết nối tín hiệu để tránh kích hoạt đệ quy
        try:
            self.recent_folders_combo.blockSignals(True)  # Cách tốt hơn để tạm ngắt tín hiệu
        except Exception as e:
            logger.error(f"Lỗi khi blockSignals: {str(e)}")
            
        # Kiểm tra xem thư mục đã có trong danh sách chưa
        found_index = -1
        for i in range(1, self.recent_folders_combo.count()):
            item_path = self.recent_folders_combo.itemData(i, Qt.UserRole)
            if not item_path:  # Nếu không có userData, sử dụng text hiển thị
                item_path = self.recent_folders_combo.itemText(i)
                
            # Chuẩn hóa đường dẫn để so sánh chính xác
            if item_path and os.path.normpath(item_path) == folder_path:
                found_index = i
                break
                
        # Nếu đã tìm thấy, xóa nó (sẽ được thêm vào đầu danh sách)
        if found_index != -1:
            self.recent_folders_combo.removeItem(found_index)
            
        # Thêm vào đầu danh sách (ngay sau tiêu đề)
        self.recent_folders_combo.insertItem(1, folder_path)
        self.recent_folders_combo.setItemData(1, folder_path, Qt.UserRole)  # Lưu đường dẫn đầy đủ vào user data
        
        # Giới hạn số lượng thư mục gần đây đến 5 để tránh quá nhiều
        while self.recent_folders_combo.count() > 6:  # 1 tiêu đề + 5 thư mục
            self.recent_folders_combo.removeItem(self.recent_folders_combo.count() - 1)
        
        # Lưu cấu hình
        # Lưu vào config
        self.save_recent_folders_to_config()
        
    def truncate_path(self, path, max_length=30):
        """Cắt ngắn đường dẫn nếu quá dài để hiển thị"""
        if len(path) > max_length:
            return path[:max_length-3] + "..."
        return path

    def load_recent_folder(self, index):
        """Load folder from recent folders combo box"""
        # Không thực hiện hành động nếu người dùng chọn tiêu đề
        if index <= 0:  # Tiêu đề "Thư mục gần đây"
            return
            
        try:
            # Lấy đường dẫn đầy đủ từ userData (nếu có) hoặc từ text
            folder = self.recent_folders_combo.itemData(index, Qt.UserRole)
            if not folder:  # Nếu không có userData, sử dụng text hiển thị
                folder = self.recent_folders_combo.itemText(index)
                
            # Kiểm tra xem thư mục có tồn tại không
            if not os.path.exists(folder):
                # Hiển thị cảnh báo và xóa thư mục không tồn tại khỏi dropdown
                result = QtWidgets.QMessageBox.warning(
                    self, 
                    "Lỗi", 
                    f"Thư mục không tồn tại hoặc không hợp lệ:\n{folder}", 
                    QtWidgets.QMessageBox.Ok
                )
                
                # Xóa thư mục không hợp lệ khỏi dropdown và config
                self.recent_folders_combo.removeItem(index)
                self.save_recent_folders_to_config()
                
                # Đặt lại dropdown về item đầu tiên ("Đường dẫn gần đây")
                self.recent_folders_combo.setCurrentIndex(0)
                return
                
            # Hiển thị tooltip đầy đủ đường dẫn
            self.recent_folders_combo.setToolTip(folder)
            
            # Clear existing previews first
            clear_video_preview(self)
            
            # Set folder path in the edit box
            self.folder_path_edit.setText(folder)
            
            # QUAN TRỌNG: Ngắt kết nối tạm thời để tránh gọi đệ quy khi setCurrentIndex
            self.recent_folders_combo.currentIndexChanged.disconnect(self.load_recent_folder)
            
            # Lưu combobox index hiện tại để khôi phục sau
            current_index = index
            
            # Kết nối lại sau khi hoàn thành
            self.recent_folders_combo.currentIndexChanged.connect(self.load_recent_folder)
        except Exception as e:
            logger.error(f"Lỗi khi tải thư mục gần đây: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Show loading overlay
            self.loading_overlay.show()
            QtWidgets.QApplication.processEvents()
            
            # Set active item with ellipsis if needed
            display_text = self.truncate_path(folder)
            
            # Lưu đường dẫn đầy đủ vào userData
            self.recent_folders_combo.setItemData(index, folder, Qt.UserRole)
            
            # Giữ folder đã chọn hiển thị trong dropdown
            self.recent_folders_combo.setItemText(index, display_text)
            
            # Refresh folder asynchronously
            QtCore.QTimer.singleShot(100, self.refresh_folder_with_loading)

    def count_video_files(self, folder_path):
        """
        Đếm số lượng file video trong thư mục
        
        Args:
            folder_path: Đường dẫn thư mục
            
        Returns:
            int: Số lượng file video
        """
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.webm', '.m4v', '.flv', '.wmv']
        count = 0
        
        try:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in video_extensions:
                        count += 1
        except Exception as e:
            logger.error(f"Lỗi khi đếm file video: {str(e)}")
        
        return count

    def check_ffmpeg_installed(self):
        """
        Kiểm tra xem FFmpeg có được cài đặt không
        
        Returns:
            bool: True nếu FFmpeg được cài đặt, ngược lại False
        """
        try:
            # Thử chạy lệnh ffmpeg -version
            import subprocess
            result = subprocess.run(
                ["ffmpeg", "-version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    def refresh_folder(self):
        """Refresh danh sách video từ thư mục hiện tại - CẢI TIẾN"""
        folder_path = self.folder_path_edit.text()
        if not folder_path:
            return
                
        # Xóa thông tin video và frame hiện tại
        clear_video_preview(self)
        clear_video_frames(self)
        
        # Reset selected video
        self.selected_video = None
        
        # Reset phân trang về trang đầu tiên
        self.current_page = 1
        
        # Reset pagination manager nếu tồn tại
        if self.pagination_manager:
            self.pagination_manager.reset()
        
        # Hiển thị overlay loading
        self.show_loading_overlay("Đang quét thư mục video...", show_spinner=True)
        
        # Sử dụng QTimer để tránh đóng băng UI
        QtCore.QTimer.singleShot(100, self.refresh_folder_with_loading)

    def show_loading_overlay(self, message="Đang tải...", show_spinner=True):
        """
        Hiển thị overlay loading với hiệu ứng nâng cao
        
        Args:
            message: Thông báo hiển thị
            show_spinner: Có hiển thị spinner hay không
        """
        # Đảm bảo overlay đã được tạo
        if not hasattr(self, 'loading_overlay') or not self.loading_overlay:
            self.loading_overlay = LoadingOverlay(self.central_widget)
        
        # Cập nhật kích thước
        self.loading_overlay.resize(self.central_widget.size())
        
        # Thiết lập thông báo
        self.loading_overlay.set_message(message)
        
        # Bật/tắt spinner
        self.loading_overlay.show_spinner(show_spinner)
        
        # Hiển thị overlay
        self.loading_overlay.show()
        
        # Cập nhật UI ngay lập tức
        QtWidgets.QApplication.processEvents()

    def debug_video_list_issue(self):
        """
        Hàm để kiểm tra và debug vấn đề chỉ hiển thị 1 video trong danh sách.
        Gọi hàm này trước khi gọi update_video_list_ui().
        """
        try:
            # Kiểm tra số lượng video trong all_videos
            logger.info(f"Tổng số video trong all_videos: {len(self.all_videos)}")
            
            # Kiểm tra trạng thái hiển thị của các hàng video
            visible_rows = 0
            for i in range(1, 11):
                row = self.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
                if row and row.isVisible():
                    visible_rows += 1
            logger.info(f"Số hàng đang hiển thị: {visible_rows}")
            
            # Kiểm tra các video item có tồn tại không
            missing_items = []
            for i in range(1, 11):
                row = self.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
                if not row:
                    missing_items.append(i)
            
            if missing_items:
                logger.error(f"Thiếu các videoItem: {missing_items}")
            else:
                logger.info("Tất cả videoItem đều tồn tại")
            
            # Kiểm tra phân trang
            items_per_page = 10
            total_pages = max(1, (len(self.all_videos) + items_per_page - 1) // items_per_page)
            logger.info(f"Trang hiện tại: {self.current_page}, Tổng số trang: {total_pages}")
            
            # Kiểm tra chỉ số bắt đầu và kết thúc
            start_idx = (self.current_page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(self.all_videos))
            logger.info(f"Chỉ số bắt đầu: {start_idx}, Chỉ số kết thúc: {end_idx}")
            
            # Kiểm tra xem các hàng có được cập nhật đúng không
            for i in range(1, 11):
                if i <= end_idx - start_idx:
                    row = self.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
                    label = self.video_list.findChild(QtWidgets.QLabel, f"label{i}")
                    
                    if row and label:
                        video_idx = start_idx + i - 1
                        if video_idx < len(self.all_videos):
                            video = self.all_videos[video_idx]
                            logger.info(f"Hàng {i}: Dự kiến hiển thị video '{video['name']}'")
                            logger.info(f"Hàng {i} thực tế: {label.text()}, Hiển thị: {row.isVisible()}")
            
            # Đảm bảo cập nhật trạng thái hiển thị của tất cả các hàng
            for i in range(1, 11):
                row = self.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
                if row:
                    if i <= end_idx - start_idx:
                        row.setVisible(True)
                        logger.info(f"Đặt hàng {i} thành hiển thị")
                    else:
                        row.setVisible(False)
                        logger.info(f"Đặt hàng {i} thành ẩn")
        
        except Exception as e:
            logger.error(f"Lỗi khi debug video list: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

    def refresh_folder_with_loading(self):
        """Làm mới thư mục với hiệu ứng loading - CẢI TIẾN"""
        self.update_video_list_ui()
        self.debug_video_list_issue()
        try:
            # Đặt con trỏ wait
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            
            folder_path = self.folder_path_edit.text()
            
            # Hiển thị đang quét video
            self.loading_overlay.set_message(f"Đang quét video trong thư mục...\n{folder_path}")
            QtWidgets.QApplication.processEvents()
            
            # Đếm số file trong thư mục 
            video_count = self.count_video_files(folder_path)
            
            # Hiển thị số lượng video đã tìm thấy
            self.loading_overlay.set_message(f"Đã tìm thấy {video_count} video.\nĐang phân tích...")
            QtWidgets.QApplication.processEvents()
            
            # Nếu có nhiều file, xử lý từng batch
            if video_count > 100:
                # Tạo progress dialog
                progress_dialog = QtWidgets.QProgressDialog(
                    f"Đang quét {video_count} video trong thư mục...", 
                    "Hủy", 0, 100, self
                )
                progress_dialog.setWindowTitle("Đang tải danh sách video")
                progress_dialog.setWindowModality(Qt.WindowModal)
                progress_dialog.show()
                
                # Sử dụng hàm tiện ích để làm mới danh sách video với báo cáo tiến trình
                self.all_videos = []
                
                # Xử lý file theo batch
                total_files = 0
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        ext = os.path.splitext(file)[1].lower()
                        if ext in ['.mp4', '.avi', '.mkv', '.mov', '.webm', '.m4v', '.flv', '.wmv']:
                            total_files += 1
                
                processed_files = 0
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        ext = os.path.splitext(file)[1].lower()
                        if ext in ['.mp4', '.avi', '.mkv', '.mov', '.webm', '.m4v', '.flv', '.wmv']:
                            file_path = os.path.join(root, file)
                            video_info = {
                                "name": file,
                                "path": file_path,
                                "status": "new",
                                "file_size_bytes": os.path.getsize(file_path)
                            }
                            self.all_videos.append(video_info)
                            
                            processed_files += 1
                            progress = int((processed_files / total_files) * 100)
                            progress_dialog.setValue(progress)
                            
                            # Cập nhật loading overlay
                            self.loading_overlay.set_message(f"Đã quét {processed_files}/{total_files} video...")
                            QtWidgets.QApplication.processEvents()
                            
                            if progress_dialog.wasCanceled():
                                break
                        
                        if progress_dialog.wasCanceled():
                            break
                    
                    if progress_dialog.wasCanceled():
                        break
                
                progress_dialog.close()
            else:
                # Sử dụng hàm tiện ích để làm mới danh sách video
                self.all_videos = refresh_video_list(self, folder_path)
            
            # Kiểm tra nếu có FFmpeg để hiển thị frames
            has_ffmpeg = self.check_ffmpeg_installed()
            if not has_ffmpeg:
                self.loading_overlay.set_message("Đang hoàn tất... (FFmpeg không có sẵn, không thể trích xuất khung hình)")
                QtWidgets.QApplication.processEvents()
                time.sleep(1)  # Cho phép người dùng đọc thông báo
            
            # Cập nhật từ điển video
            self.videos = {}
            for video in self.all_videos:
                self.videos[video["name"]] = video["path"]
            
            # Reset bộ đếm lựa chọn
            self.selected_video_count = 0
            self.selected_videos_size = 0
            
            # Cập nhật UI
            self.update_video_list_ui()
            
            # Lưu thư mục vào danh sách gần đây
            self.add_to_recent_folders(folder_path)
            
        except Exception as e:
            logger.error(f"Lỗi khi làm mới thư mục: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Hiển thị thông báo lỗi
            QtWidgets.QMessageBox.critical(self, "Lỗi", f"Không thể quét thư mục: {str(e)}")
        finally:
            # Khôi phục con trỏ và ẩn loading overlay
            QtWidgets.QApplication.restoreOverrideCursor()
            self.loading_overlay.hide()
            

    def update_video_list_ui(self):
        """Update video list UI with current videos"""
        if not hasattr(self, 'video_list'):
            return
        
        try:
            # Calculate pagination
            items_per_page = 10
            total_pages = max(1, (len(self.all_videos) + items_per_page - 1) // items_per_page)
            
            # Ensure current page is valid
            self.current_page = min(max(1, self.current_page), max(1, total_pages))
            
            # Calculate start and end indices for current page
            start_idx = (self.current_page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(self.all_videos))
            
            # Get videos for current page
            current_videos = self.all_videos[start_idx:end_idx]
            display_count = len(current_videos)
            
            # Debug log
            logger.info(f"Hiển thị {display_count} video từ vị trí {start_idx} đến {end_idx}")
            logger.info(f"Tổng số video: {len(self.all_videos)}")
            
            # Đảm bảo tất cả các hàng được xử lý (ẩn/hiện, cập nhật nội dung)
            for i in range(1, 11):
                # Get widgets
                row = self.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
                label = self.video_list.findChild(QtWidgets.QLabel, f"label{i}")
                status = self.video_list.findChild(QtWidgets.QLabel, f"status{i}")
                checkbox = self.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
                
                # Kiểm tra xem tất cả các widget cần thiết đã được tìm thấy chưa
                if row is None or label is None or status is None or checkbox is None:
                    logger.warning(f"Không tìm thấy đủ các widget cho hàng {i}")
                    continue
                    
                # Xử lý hiển thị hoặc ẩn các hàng
                if i <= display_count:
                    # Hiển thị hàng
                    row.setVisible(True)
                    
                    # Lấy thông tin video và cập nhật nội dung
                    video_idx = i - 1
                    if video_idx < len(current_videos):
                        video = current_videos[video_idx]
                        
                        # Cập nhật tên
                        label.setText(video.get("name", ""))
                        
                        # Cập nhật trạng thái
                        status_text = "Mới"
                        status_class = "statusNew"
                        
                        if video.get("status") == "uploaded":
                            status_text = "Đã tải"
                            status_class = "statusUploaded"
                        elif video.get("status") == "duplicate":
                            status_text = "Trùng"
                            status_class = "statusDuplicate"
                        
                        status.setText(status_text)
                        status.setProperty("class", status_class)
                        
                        # Cập nhật style
                        status.style().unpolish(status)
                        status.style().polish(status)
                        
                        # Đặt trạng thái checkbox
                        checkbox.setChecked(video.get("status") == "new")
                        
                        logger.debug(f"Hiển thị video {i}: {video.get('name')}, Trạng thái: {status_text}")
                    else:
                        logger.warning(f"Chỉ số video không hợp lệ: {video_idx} >= {len(current_videos)}")
                else:
                    # Ẩn hàng
                    row.setVisible(False)
                    
                    # Xóa nội dung hiện tại
                    label.setText("")
                    status.setText("")
                    checkbox.setChecked(False)
                    
                    logger.debug(f"Ẩn hàng {i}")
            
            # Update pagination info
            if hasattr(self, 'pagination_info_label'):
                duplicate_count = sum(1 for v in self.all_videos if v.get("status") == "duplicate")
                uploaded_count = sum(1 for v in self.all_videos if v.get("status") == "uploaded")
                
                if len(self.all_videos) > 0:
                    self.pagination_info_label.setText(
                        f"Hiển thị {start_idx+1}-{end_idx} trên tổng {len(self.all_videos)} videos, "
                        f"có {duplicate_count} video trùng, có {uploaded_count} đã tải lên"
                    )
                else:
                    self.pagination_info_label.setText("Không có video nào trong thư mục này")
            
            # Update pagination UI with improved approach
            self._update_pagination_ui(total_pages)
            
            # Update selection count
            self.update_selection_count()
            
            # Update folder stats
            if hasattr(self, 'folder_stats_label'):
                total_size = sum(video.get("file_size_bytes", 0) for video in self.all_videos)
                size_str = self.format_file_size(total_size)
                self.folder_stats_label.setText(f"Tổng dung lượng: {size_str} | {len(self.all_videos)} videos")
        
        except Exception as e:
            logger.error(f"Lỗi trong update_video_list_ui: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    def go_to_page(self, page):
        """Go to specific page"""
        items_per_page = 10
        total_pages = (len(self.all_videos) + items_per_page - 1) // items_per_page
        
        # Ràng buộc page trong phạm vi hợp lệ
        page = max(1, min(page, total_pages))
        
        if self.current_page != page:
            self.current_page = page
            self.update_video_list_ui()

    def next_page(self):
        """Go to next page"""
        items_per_page = 10
        total_pages = (len(self.all_videos) + items_per_page - 1) // items_per_page
        
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_video_list_ui()

    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_video_list_ui()

    def last_page(self):
        """Go to last page"""
        items_per_page = 10
        total_pages = (len(self.all_videos) + items_per_page - 1) // items_per_page
        
        if self.current_page != total_pages:
            self.current_page = total_pages
            self.update_video_list_ui()

    def filter_videos(self, text):
        """Filter videos by name"""
        if not text:
            # If no filter, show all videos
            self.update_video_list_ui()
            return
        
        # Filter videos by name (case insensitive)
        text = text.lower()
        filtered_videos = [v for v in self.all_videos if text in v["name"].lower()]
        
        # Replace all_videos temporarily for UI update
        saved_videos = self.all_videos
        self.all_videos = filtered_videos
        self.current_page = 1  # Reset to first page
        self.update_video_list_ui()
        self.all_videos = saved_videos

    def sort_videos(self, index):
        """
        Sắp xếp video theo tiêu chí đã chọn - ĐÃ CẢI TIẾN
        
        Args:
            index: Chỉ số tùy chọn sắp xếp trong dropdown
        """
        if not hasattr(self, 'all_videos') or not self.all_videos:
            return
        
        try:
            logger.info(f"Sắp xếp videos theo tùy chọn: {index}")
            
            # Lấy text option từ combobox nếu có
            sort_text = self.sort_combo_box.currentText() if hasattr(self, 'sort_combo_box') else ""
            
            # Sắp xếp dựa trên tùy chọn
            if index == 0 or "tên (A-Z)" in sort_text:  # Tên (A-Z)
                self.all_videos.sort(key=lambda v: v.get("name", "").lower())
            elif index == 1 or "tên (Z-A)" in sort_text:  # Tên (Z-A)
                self.all_videos.sort(key=lambda v: v.get("name", "").lower(), reverse=True)
            elif index == 2 or "lớn → nhỏ" in sort_text:  # Kích thước (lớn → nhỏ)
                self.all_videos.sort(key=lambda v: v.get("file_size_bytes", 0), reverse=True)
            elif index == 3 or "nhỏ → lớn" in sort_text:  # Kích thước (nhỏ → lớn)
                self.all_videos.sort(key=lambda v: v.get("file_size_bytes", 0))
            elif index == 4 or "dài → ngắn" in sort_text:  # Thời lượng (dài → ngắn)
                self.all_videos.sort(key=lambda v: v.get("duration", 0), reverse=True)
            elif index == 5 or "ngắn → dài" in sort_text:  # Thời lượng (ngắn → dài)
                self.all_videos.sort(key=lambda v: v.get("duration", 0))
            elif index == 6 or "mới → cũ" in sort_text:  # Ngày tạo (mới → cũ)
                # Sử dụng os.path.getctime để lấy thời gian tạo file
                self.all_videos.sort(
                    key=lambda v: os.path.getctime(v.get("path", "")) if os.path.exists(v.get("path", "")) else 0, 
                    reverse=True
                )
            elif index == 7 or "cũ → mới" in sort_text:  # Ngày tạo (cũ → mới)
                self.all_videos.sort(
                    key=lambda v: os.path.getctime(v.get("path", "")) if os.path.exists(v.get("path", "")) else 0
                )
            elif index == 8 or "Trạng thái" in sort_text:  # Trạng thái
                # Sắp xếp theo trạng thái (uploaded, duplicate, new)
                status_order = {"uploaded": 0, "duplicate": 1, "new": 2}
                self.all_videos.sort(key=lambda v: status_order.get(v.get("status", "new"), 3))
            
            # Reset về trang đầu tiên
            self.current_page = 1
            
            # Cập nhật UI
            self.update_video_list_ui()
            
            logger.info(f"Đã sắp xếp {len(self.all_videos)} videos")
        except Exception as e:
            logger.error(f"Lỗi khi sắp xếp videos: {str(e)}")
            logger.error(traceback.format_exc())

    def view_video(self):
        """Open the currently selected video in a media player"""
        if not self.selected_video:
            return
        
        # Find video path
        video_path = None
        for video in self.all_videos:
            if video.get("name") == self.selected_video:
                video_path = video.get("path")
                break
        
        if not video_path or not os.path.exists(video_path):
            logger.error(f"Video file not found: {self.selected_video}")
            return
        
        # Open video with default player
        import subprocess
        import platform
        
        system = platform.system()
        
        try:
            if system == "Windows":
                os.startfile(video_path)
            elif system == "Darwin":  # macOS
                subprocess.call(["open", video_path])
            else:  # Linux
                subprocess.call(["xdg-open", video_path])
                
            logger.info(f"Opened video: {video_path}")
        except Exception as e:
            logger.error(f"Error opening video: {str(e)}")
            QtWidgets.QMessageBox.warning(self, "Lỗi", f"Không thể mở video: {str(e)}")

    def upload_current_video(self):
        """Upload the currently selected video"""
        if not self.selected_video:
            QtWidgets.QMessageBox.information(self, "Thông báo", "Vui lòng chọn một video!")
            return
        
        # Find video path
        video_path = None
        for video in self.all_videos:
            if video.get("name") == self.selected_video:
                video_path = video.get("path")
                break
        
        if not video_path or not os.path.exists(video_path):
            logger.error(f"Video file not found: {self.selected_video}")
            return
        
        # Use utility function to upload
        upload_single_video(self, self.selected_video, video_path)

    def select_all_videos(self):
        """Select all videos in the list"""
        select_all_videos(self)
        self.update_selection_count()

    def deselect_all_videos(self):
        """Deselect all videos in the list"""
        deselect_all_videos(self)
        self.update_selection_count()

    def select_unuploaded_videos(self):
        """Select only videos that haven't been uploaded"""
        select_unuploaded_videos(self)
        self.update_selection_count()

    def upload_selected_videos(self):
        """Upload all selected videos"""
        upload_selected_videos(self)
        
        # Refresh folder after upload
        self.refresh_folder()

    def resizeEvent(self, event):
        """Handle resize event to update loading overlay size"""
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.resize(self.central_widget.size())
        super(MainUI, self).resizeEvent(event)

# Run the application if executed directly
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec_())