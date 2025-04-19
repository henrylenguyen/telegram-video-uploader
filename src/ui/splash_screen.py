"""
Module tạo và hiển thị màn hình chào khi khởi động ứng dụng.
"""
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtCore import Qt
import os
import sys
import logging
import time
import configparser
import traceback
import requests

logger = logging.getLogger("SplashScreen")

class SplashScreen(QtWidgets.QWidget):
    """
    Màn hình chào hiện đại với thanh cuộn và các indicator tròn
    """
    
    # Tín hiệu hoàn thành splash screen và trạng thái cấu hình
    finished = QtCore.pyqtSignal(bool)
    # Tín hiệu khi người dùng hủy
    canceled = QtCore.pyqtSignal()
    
    def __init__(self, parent=None, app=None):
        super(SplashScreen, self).__init__(parent, Qt.Window | Qt.FramelessWindowHint)
        
        # Lưu tham chiếu đến ứng dụng chính
        self.app = app
        
        # Khởi tạo các danh sách để lưu trữ các thành phần UI
        self.status_items = []
        self.indicator_labels = []
        self.status_labels = []
        
        # Trạng thái kết nối internet
        self.is_connected = True
        self.retry_count = 0
        self.max_retries = 3
        
        # Nạp giao diện từ file UI
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file = os.path.join(current_dir, "qt_designer", "splash_screen.ui")
        
        # Nếu không tìm thấy file UI, sử dụng đường dẫn khác
        if not os.path.exists(ui_file):
            ui_file = os.path.join(current_dir, "..", "ui", "qt_designer", "splash_screen.ui")
        
        # Nếu vẫn không tìm thấy, tạo giao diện trực tiếp
        if not os.path.exists(ui_file):
            self.setup_ui_manually()
        else:
            uic.loadUi(ui_file, self)
        
        # Căn giữa màn hình
        self.center_on_screen()
        
        # Tạo logo
        self.setup_logo()
        
        # Thiết lập các indicator trạng thái
        self.setup_indicators()
        
        # Thêm nút hủy
        self.add_cancel_button()
        
        # Thêm label hiển thị thông tin tốc độ mạng (mặc định ẩn)
        self.add_network_info_label()
        
        # Khởi tạo tiến trình
        self.current_step = 0
        self.total_steps = 8  # Tổng số bước
        
        # Thiết lập giá trị ban đầu cho thanh tiến trình
        self.progressBar.setValue(0)
        
        # Danh sách các bước setup
        self.setup_items = [
            "Kiểm tra cấu hình hệ thống",
            "Khởi tạo tài nguyên ứng dụng",
            "Chuẩn bị bộ phân tích video",
            "Kiểm tra kết nối",
            "Tải các thành phần giao diện",
            "Kiểm tra không gian lưu trữ",
            "Tìm kiếm cập nhật",
            "Tối ưu hóa hiệu suất"
        ]
        
        # Biến để theo dõi trạng thái cấu hình Telegram
        self.telegram_configured = False
        self.ffmpeg_manager = None
        
        # Timer cập nhật trạng thái tải FFmpeg
        self.ffmpeg_status_timer = QtCore.QTimer(self)
        self.ffmpeg_status_timer.timeout.connect(self.update_ffmpeg_download_status)
    
    def add_network_info_label(self):
        """Thêm label hiển thị thông tin tốc độ mạng"""
        self.networkInfoLabel = QtWidgets.QLabel("", self)
        self.networkInfoLabel.setStyleSheet("""
            font-family: Arial, sans-serif;
            font-size: 11px;
            color: #7f8c8d;
            background-color: transparent;
        """)
        
        # Thêm vào layout
        if hasattr(self, 'contentLayout'):
            self.contentLayout.addWidget(self.networkInfoLabel, 0, QtCore.Qt.AlignHCenter)
            self.networkInfoLabel.hide()  # Ẩn ban đầu
    
    def add_cancel_button(self):
        """Thêm nút hủy vào màn hình chào"""
        # Tạo nút Hủy
        self.cancelButton = QtWidgets.QPushButton("Hủy", self)
        self.cancelButton.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 15px;
                color: #555;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.cancelButton.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        
        # Thêm vào layout
        if hasattr(self, 'contentLayout'):
            # Tạo layout cho nút
            buttonLayout = QtWidgets.QHBoxLayout()
            buttonLayout.addStretch()
            buttonLayout.addWidget(self.cancelButton)
            
            # Thêm vào layout chính
            self.contentLayout.addLayout(buttonLayout)
        
        # Kết nối sự kiện
        self.cancelButton.clicked.connect(self.on_cancel_clicked)
    
    def on_cancel_clicked(self):
        """Xử lý khi người dùng nhấn nút Hủy"""
        # Hiển thị hộp thoại xác nhận
        reply = QtWidgets.QMessageBox.question(
            self, 
            "Xác nhận hủy",
            "Bạn có chắc muốn hủy cài đặt và thoát ứng dụng?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # Dừng các timer
            if hasattr(self, 'process_timer') and self.process_timer.isActive():
                self.process_timer.stop()
                
            if hasattr(self, 'ffmpeg_status_timer') and self.ffmpeg_status_timer.isActive():
                self.ffmpeg_status_timer.stop()
            
            # Phát tín hiệu hủy
            self.canceled.emit()
            
            # Đóng splash screen
            self.close()
            
            # Thoát ứng dụng
            QtCore.QCoreApplication.quit()
    
    def update_ffmpeg_download_status(self):
        """Cập nhật thông tin tải FFmpeg từ FFmpegManager"""
        if self.ffmpeg_manager and self.ffmpeg_manager.is_downloading:
            status_text = self.ffmpeg_manager.download_status
            
            # Cập nhật trạng thái
            self.update_status(status_text)
            
            # Cập nhật tiến trình dựa trên phần trăm tải FFmpeg
            progress = self.ffmpeg_manager.download_progress
            step_progress = int((2 / self.total_steps) * 100)
            total_progress = step_progress + int(progress / self.total_steps)
            self.update_progress(total_progress)
            
            # Hiển thị thông tin tốc độ mạng trong networkInfoLabel
            if hasattr(self, 'networkInfoLabel'):
                # Hiển thị label nếu đang ẩn
                if self.networkInfoLabel.isHidden():
                    self.networkInfoLabel.show()
                
                # Cập nhật thông tin mạng
                if hasattr(self.ffmpeg_manager, 'download_speed') and self.ffmpeg_manager.download_speed > 0:
                    info = f"Tốc độ mạng: {self._format_speed(self.ffmpeg_manager.download_speed)}"
                    if hasattr(self.ffmpeg_manager, 'estimated_time'):
                        info += f" | Thời gian còn lại: {self.ffmpeg_manager.estimated_time}"
                    
                    self.networkInfoLabel.setText(info)
                else:
                    self.networkInfoLabel.setText("Đang phân tích tốc độ mạng...")
        else:
            # Nếu không còn tải nữa, dừng timer
            self.ffmpeg_status_timer.stop()
            
            # Ẩn nhãn thông tin mạng
            if hasattr(self, 'networkInfoLabel'):
                self.networkInfoLabel.hide()
                
    def _format_speed(self, speed_bytes):
        """Định dạng tốc độ tải thành chuỗi dễ đọc"""
        if speed_bytes < 1024:
            return f"{speed_bytes:.1f} B/s"
        elif speed_bytes < 1024 * 1024:
            return f"{speed_bytes/1024:.1f} KB/s"
        else:
            return f"{speed_bytes/(1024*1024):.1f} MB/s"
    
    def center_on_screen(self):
        """Đặt cửa sổ vào giữa màn hình"""
        rect = QtWidgets.QApplication.desktop().availableGeometry()
        self.move((rect.width() - self.width()) // 2, (rect.height() - self.height()) // 2)
        
    def setup_ui_manually(self):
        """Thiết lập UI theo cách thủ công nếu không tìm thấy file UI"""
        # Thiết lập kích thước
        self.setObjectName("SplashScreen")
        self.resize(600, 400)
        self.setWindowTitle("Đang khởi động...")
        
        # Thiết lập stylesheet
        self.setStyleSheet("""
            QWidget#SplashScreen {
              background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8f9fa, stop:1 #e9ecef);
              border-radius: 15px;
            }
            
            QLabel#titleLabel {
              font-family: Arial, sans-serif;
              font-size: 24px;
              font-weight: bold;
              color: #2c3e50;
            }
            
            QLabel#statusLabel {
              font-family: Arial, sans-serif;
              font-size: 12px;
              color: #7f8c8d;
            }
            
            QScrollArea {
              background-color: transparent;
              border: none;
            }
            
            QWidget#scrollAreaContents {
              background-color: white;
              border-radius: 8px;
            }
            
            QScrollBar:vertical {
              background: #E2E8F0;
              width: 6px;
              border-radius: 3px;
              margin: 0px;
            }
            
            QScrollBar::handle:vertical {
              background: #CBD5E1;
              border-radius: 3px;
              min-height: 30px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
              height: 0px;
            }
            
            QProgressBar {
              background-color: #e0e0e0;
              border: none;
              height: 10px;
              border-radius: 5px;
              text-align: center;
            }
            
            QProgressBar::chunk {
              background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498DB, stop:1 #2ECC71);
              border-radius: 5px;
            }
            
            QLabel.statusItem {
              font-family: Arial, sans-serif;
              font-size: 14px;
              color: #2c3e50;
            }
            
            QLabel.statusItemPending {
              font-family: Arial, sans-serif;
              font-size: 14px;
              color: #7f8c8d;
            }
            
            QFrame.statusItemFrame {
              background-color: white;
            }

            QPushButton {
              background-color: #f0f0f0;
              border: 1px solid #ccc;
              border-radius: 4px;
              padding: 5px 15px;
              color: #555;
              font-weight: bold;
            }
            QPushButton:hover {
              background-color: #e0e0e0;
            }
            QPushButton:pressed {
              background-color: #d0d0d0;
            }
        """)
        
        # Tạo layout chính
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(30, 30, 30, 30)
        self.verticalLayout.setSpacing(15)
        
        # Layout logo
        self.logoLayout = QtWidgets.QVBoxLayout()
        self.logoLayout.setSpacing(15)
        
        # Logo
        self.logoLabel = QtWidgets.QLabel()
        self.logoLabel.setMinimumSize(70, 70)
        self.logoLabel.setMaximumSize(70, 70)
        self.logoLabel.setScaledContents(True)
        self.logoLayout.addWidget(self.logoLabel, 0, QtCore.Qt.AlignHCenter)
        
        # Tiêu đề
        self.titleLabel = QtWidgets.QLabel("Telegram Video Uploader")
        self.titleLabel.setObjectName("titleLabel")
        self.logoLayout.addWidget(self.titleLabel, 0, QtCore.Qt.AlignHCenter)
        
        self.verticalLayout.addLayout(self.logoLayout)
        
        # Layout nội dung
        self.contentLayout = QtWidgets.QVBoxLayout()
        self.contentLayout.setSpacing(20)
        
        # Khung cuộn trạng thái
        self.statusScrollArea = QtWidgets.QScrollArea()
        self.statusScrollArea.setObjectName("statusScrollArea")
        self.statusScrollArea.setMinimumHeight(150)
        self.statusScrollArea.setMaximumHeight(150)
        self.statusScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.statusScrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.statusScrollArea.setWidgetResizable(True)
        
        # Nội dung khung cuộn
        self.scrollAreaContents = QtWidgets.QWidget()
        self.scrollAreaContents.setObjectName("scrollAreaContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaContents)
        
        # Tạo các mục trạng thái
        for i, item_text in enumerate(self.setup_items):
            # Frame cho mục
            status_item = QtWidgets.QFrame()
            status_item.setObjectName(f"statusItem{i+1}")
            status_item.setFrameShape(QtWidgets.QFrame.StyledPanel)
            status_item.setFrameShadow(QtWidgets.QFrame.Raised)
            status_item.setProperty("class", "statusItemFrame")
            
            # Layout cho mục
            horizontalLayout = QtWidgets.QHBoxLayout(status_item)
            horizontalLayout.setContentsMargins(10, 5, 10, 5)
            
            # Indicator
            indicator = QtWidgets.QLabel()
            indicator.setObjectName(f"indicator{i+1}")
            indicator.setMinimumSize(20, 20)
            indicator.setMaximumSize(20, 20)
            horizontalLayout.addWidget(indicator)
            self.indicator_labels.append(indicator)
            
            # Label
            label = QtWidgets.QLabel(item_text)
            label.setObjectName(f"label{i+1}")
            if i < 3:
                label.setProperty("class", "statusItem")
            else:
                label.setProperty("class", "statusItemPending")
            horizontalLayout.addWidget(label)
            self.status_labels.append(label)
            
            # Thêm vào layout
            self.verticalLayout_2.addWidget(status_item)
            self.status_items.append(status_item)
        
        self.statusScrollArea.setWidget(self.scrollAreaContents)
        self.contentLayout.addWidget(self.statusScrollArea)
        
        # Thanh tiến trình
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setValue(0)
        self.contentLayout.addWidget(self.progressBar)
        
        # Nhãn trạng thái
        self.statusLabel = QtWidgets.QLabel("Đang chuẩn bị...")
        self.statusLabel.setObjectName("statusLabel")
        self.contentLayout.addWidget(self.statusLabel, 0, QtCore.Qt.AlignHCenter)
        
        # Nút hủy
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addStretch()
        
        self.cancelButton = QtWidgets.QPushButton("Hủy")
        self.cancelButton.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        buttonLayout.addWidget(self.cancelButton)
        
        self.contentLayout.addLayout(buttonLayout)
        self.verticalLayout.addLayout(self.contentLayout)
    
    def setup_logo(self):
        """Thiết lập logo ứng dụng"""
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png")
        
        if not os.path.exists(logo_path):
            # Thử đường dẫn khác
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo", "logo.png")
        
        if os.path.exists(logo_path):
            pixmap = QtGui.QPixmap(logo_path)
            self.logoLabel.setPixmap(pixmap)
        
    def setup_indicators(self):
        """Thiết lập các indicator trạng thái"""
        # Tạo hình ảnh cho các trạng thái
        size = QtCore.QSize(20, 20)
        
        # Pending circle (empty circle)
        pending_img = QtGui.QPixmap(size)
        pending_img.fill(Qt.transparent)
        painter = QtGui.QPainter(pending_img)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor("#CBD5E1"), 2))
        painter.setBrush(Qt.transparent)
        painter.drawEllipse(2, 2, 16, 16)
        painter.end()
        
        # Active circle (blue circle)
        active_img = QtGui.QPixmap(size)
        active_img.fill(Qt.transparent)
        painter = QtGui.QPainter(active_img)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QtGui.QColor("#3498DB"))
        painter.drawEllipse(2, 2, 16, 16)
        painter.end()
        
        # Success circle (green circle with checkmark)
        success_img = QtGui.QPixmap(size)
        success_img.fill(Qt.transparent)
        painter = QtGui.QPainter(success_img)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw green circle
        painter.setPen(Qt.NoPen)
        painter.setBrush(QtGui.QColor("#2ECC71"))
        painter.drawEllipse(2, 2, 16, 16)
        
        # Draw checkmark
        painter.setPen(QtGui.QPen(Qt.white, 2))
        painter.drawLine(6, 10, 9, 14)
        painter.drawLine(9, 14, 14, 6)
        painter.end()
        
        # Error circle (red circle with X)
        error_img = QtGui.QPixmap(size)
        error_img.fill(Qt.transparent)
        painter = QtGui.QPainter(error_img)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw red circle
        painter.setPen(Qt.NoPen)
        painter.setBrush(QtGui.QColor("#E74C3C"))
        painter.drawEllipse(2, 2, 16, 16)
        
        # Draw X
        painter.setPen(QtGui.QPen(Qt.white, 2))
        painter.drawLine(6, 6, 14, 14)
        painter.drawLine(6, 14, 14, 6)
        painter.end()
        
        # Lưu lại các pixmap
        self.indicator_images = {
            "pending": pending_img,
            "active": active_img,
            "success": success_img,
            "error": error_img
        }
        
        # Kiểm tra xem indicator_labels đã được khởi tạo và có phần tử chưa
        if not hasattr(self, 'indicator_labels') or len(self.indicator_labels) == 0:
            logger.warning("Không tìm thấy indicator_labels, có thể do UI không được tạo đúng cách")
            return
            
        # Thiết lập trạng thái ban đầu
        for i, indicator in enumerate(self.indicator_labels):
            if i == 0:
                indicator.setPixmap(self.indicator_images["active"])
            else:
                indicator.setPixmap(self.indicator_images["pending"])
    
    def update_indicator(self, index, status):
        """
        Cập nhật trạng thái indicator
        
        Args:
            index (int): Chỉ số của indicator (0-based)
            status (str): Trạng thái mới ('pending', 'active', 'success', 'error')
        """
        if 0 <= index < len(self.indicator_labels) and status in self.indicator_images:
            self.indicator_labels[index].setPixmap(self.indicator_images[status])
            
            # Cập nhật style của label
            if status == "pending":
                self.status_labels[index].setProperty("class", "statusItemPending")
            else:
                self.status_labels[index].setProperty("class", "statusItem")
                
            # Force style update
            self.status_labels[index].style().unpolish(self.status_labels[index])
            self.status_labels[index].style().polish(self.status_labels[index])
            
    def update_progress(self, value):
        """Cập nhật giá trị thanh tiến trình"""
        self.progressBar.setValue(value)
        
    def update_status(self, text):
        """Cập nhật text trạng thái hiện tại"""
        self.statusLabel.setText(text)
        
    def next_step(self):
        """Chuyển sang bước tiếp theo trong tiến trình cài đặt"""
        if self.current_step < self.total_steps:
            # Đánh dấu bước hiện tại là hoàn thành
            self.update_indicator(self.current_step, "success")
            
            # Tăng bước hiện tại
            self.current_step += 1
            
            # Cập nhật tiến trình
            progress_value = int((self.current_step / self.total_steps) * 100)
            self.update_progress(progress_value)
            
            # Nếu còn bước tiếp theo, đánh dấu là active
            if self.current_step < self.total_steps:
                self.update_indicator(self.current_step, "active")
                self.update_status(f"Đang {self.setup_items[self.current_step].lower()}...")
            else:
                # Đã hoàn thành tất cả các bước
                self.update_status("Đã hoàn tất cài đặt!")
                
                # Phát tín hiệu hoàn thành sau 1 giây
                QtCore.QTimer.singleShot(1000, lambda: self.finished.emit(self.telegram_configured))
                
    def mark_step_error(self, index, error_message=None):
        """Đánh dấu một bước bị lỗi"""
        if 0 <= index < self.total_steps:
            self.update_indicator(index, "error")
            
            if error_message:
                self.update_status(error_message)
                
    def start_setup_process(self, ffmpeg_manager=None):
        """
        Bắt đầu quy trình cài đặt
        
        Args:
            ffmpeg_manager: Đối tượng quản lý FFmpeg
        """
        self.ffmpeg_manager = ffmpeg_manager
        
        # Khởi tạo tiến trình với bước đầu tiên
        self.current_step = 0
        self.update_indicator(0, "active")
        self.update_status(f"Đang {self.setup_items[0].lower()}...")
        
        # Tạo timer để cập nhật các bước
        self.process_timer = QtCore.QTimer(self)
        self.process_timer.timeout.connect(self.process_next_step)
        self.process_timer.start(1000)  # 1 giây mỗi bước
        
    def process_next_step(self):
        """Xử lý bước tiếp theo trong tiến trình cài đặt"""
        # Nếu đã hoàn thành hoặc có lỗi, dừng timer
        if self.current_step >= self.total_steps:
            self.process_timer.stop()
            return
            
        # Xử lý logic cho từng bước
        if self.current_step == 0:  # Kiểm tra cấu hình hệ thống
            self.next_step()
            
        elif self.current_step == 1:  # Khởi tạo tài nguyên ứng dụng
            self.next_step()
            
        elif self.current_step == 2:  # Chuẩn bị bộ phân tích video
            if self.ffmpeg_manager:
                # Kiểm tra FFmpeg đã tải về chưa
                if self.ffmpeg_manager.is_available:
                    self.next_step()
                elif self.ffmpeg_manager.is_downloading:
                    # Khi bắt đầu tải FFmpeg, khởi động timer để cập nhật trạng thái
                    if not self.ffmpeg_status_timer.isActive():
                        self.ffmpeg_status_timer.start(500)  # Cập nhật mỗi 500ms
                else:
                    # Kiểm tra kết nối internet trước khi tải
                    if self.check_internet_connection():
                        # Bắt đầu tải
                        self.update_status("Đang tải FFmpeg...")
                        self.ffmpeg_manager.setup_ffmpeg()
                        
                        # Bắt đầu timer cập nhật trạng thái tải
                        if not self.ffmpeg_status_timer.isActive():
                            self.ffmpeg_status_timer.start(500)
                    else:
                        self.handle_connection_error("Đang tải FFmpeg...")
            else:
                # Không có ffmpeg_manager, bỏ qua
                self.next_step()
                
        elif self.current_step == 3:  # Kiểm tra kết nối
            # Kiểm tra kết nối internet
            if not self.check_internet_connection():
                self.handle_connection_error("Đang kiểm tra kết nối...")
                return
                
            # Kiểm tra cấu hình Telegram
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.ini")
            
            if os.path.exists(config_path):
                config = configparser.ConfigParser()
                config.read(config_path)
                
                # Kiểm tra nếu đã cấu hình Telegram Bot hoặc Telethon
                if config.has_section('TELEGRAM') and config.has_option('TELEGRAM', 'bot_token') and config.has_option('TELEGRAM', 'chat_id'):
                    bot_token = config.get('TELEGRAM', 'bot_token')
                    chat_id = config.get('TELEGRAM', 'chat_id')
                    
                    if bot_token and chat_id:
                        self.telegram_configured = True
                
                if config.has_section('TELETHON') and config.has_option('TELETHON', 'api_id') and config.has_option('TELETHON', 'api_hash'):
                    api_id = config.get('TELETHON', 'api_id')
                    api_hash = config.get('TELETHON', 'api_hash')
                    
                    if api_id and api_hash:
                        self.telegram_configured = True
                
            self.next_step()
                    
        elif self.current_step == 4:  # Tải các thành phần giao diện
            self.next_step()
            
        elif self.current_step == 5:  # Kiểm tra không gian lưu trữ
            self.next_step()
            
        elif self.current_step == 6:  # Tìm kiếm cập nhật
            # Kiểm tra kết nối internet
            if not self.check_internet_connection():
                self.handle_connection_error("Đang tìm kiếm cập nhật...")
                return
                
            self.next_step()
            
        elif self.current_step == 7:  # Tối ưu hóa hiệu suất
            self.next_step()

    def check_internet_connection(self):
        """Kiểm tra kết nối internet bằng cách truy cập Google"""
        try:
            requests.get("https://www.google.com", timeout=5)
            return True
        except requests.RequestException:
            return False
            
    def handle_connection_error(self, step_message):
        """Xử lý khi mất kết nối internet"""
        self.is_connected = False
        self.retry_count += 1
        
        if self.retry_count <= self.max_retries:
            # Cập nhật trạng thái
            self.update_status(f"Mất kết nối! Đang thử lại ({self.retry_count}/{self.max_retries})...")
            
            # Chờ 3 giây và thử lại
            QtCore.QTimer.singleShot(3000, lambda: self.retry_connection(step_message))
        else:
            # Hết số lần thử, hiển thị thông báo
            self.mark_step_error(self.current_step, "Không thể kết nối. Vui lòng kiểm tra kết nối mạng!")
            
            # Hiển thị hộp thoại thông báo
            QtWidgets.QMessageBox.warning(
                self,
                "Lỗi kết nối",
                "Không thể kết nối đến mạng sau nhiều lần thử lại.\nHãy kiểm tra kết nối và thử lại sau.",
                QtWidgets.QMessageBox.Ok
            )
    
    def retry_connection(self, step_message):
        """Thử kết nối lại và tiếp tục tiến trình nếu thành công"""
        if self.check_internet_connection():
            self.is_connected = True
            self.retry_count = 0
            self.update_status(step_message)
            # Tiếp tục tiến trình
            self.next_step()
        else:
            # Vẫn mất kết nối, xử lý lỗi
            self.handle_connection_error(step_message)

def show_splash_screen(app, ffmpeg_manager=None):
    """
    Hiển thị splash screen và xử lý tiến trình cài đặt ban đầu
    
    Args:
        app: Ứng dụng Qt
        ffmpeg_manager: Quản lý FFmpeg
        
    Returns:
        tuple: (splash_screen, telegram_configured)
    """
    try:
        splash = SplashScreen(app=app)
        splash.show()
        
        # Bắt đầu tiến trình cài đặt
        splash.start_setup_process(ffmpeg_manager)
        
        return splash
    except Exception as e:
        logger.error(f"Lỗi khi tạo splash screen: {str(e)}")
        logger.error(traceback.format_exc())
        # Tạo splash screen đơn giản hơn trong trường hợp lỗi
        simple_splash = QtWidgets.QSplashScreen(QtGui.QPixmap())
        simple_splash.show()
        QtCore.QTimer.singleShot(3000, simple_splash.close)
        return simple_splash

if __name__ == "__main__":
    # Test splash screen
    app = QtWidgets.QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    
    # Mô phỏng xử lý
    timer = QtCore.QTimer()
    timer.timeout.connect(splash.next_step)
    timer.start(300)
    
    sys.exit(app.exec_())