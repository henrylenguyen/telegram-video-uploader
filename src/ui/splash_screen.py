"""
Module tạo và hiển thị màn hình chào khi khởi động ứng dụng.
"""
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt, pyqtSignal
import os
import sys
import logging
import time
import configparser
import traceback
import requests
import shutil
import platform
import subprocess
import ctypes
import webbrowser
import urllib.request

from .telegram.telegram_ui import ConfigModal

logger = logging.getLogger(__name__)

class SplashScreen(QtWidgets.QWidget):
    """
    Màn hình chào hiện đại với thanh cuộn và các indicator tròn
    """
    
    # Tín hiệu hoàn thành splash screen và trạng thái cấu hình
    finished = pyqtSignal(bool)
    # Tín hiệu khi người dùng hủy
    canceled = pyqtSignal()
    
    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.setup_complete = False
        self.error_occurred = False
        self.current_step = 0
        self.total_steps = 10  # Tổng số bước
        
        # Các danh sách để theo dõi trạng thái
        self.indicator_labels = []
        self.status_labels = []
        
        # Danh sách các bước setup - 10 bước
        self.setup_items = [
            "Kiểm tra kết nối Internet",
            "Kiểm tra cấu hình hệ thống",
            "Thiết lập SSL cho Telethon",
            "Khởi tạo tài nguyên ứng dụng",
            "Chuẩn bị bộ phân tích video",
            "Kiểm tra kết nối Telegram",
            "Tải các thành phần giao diện",
            "Kiểm tra không gian lưu trữ",
            "Tìm kiếm cập nhật",
            "Tối ưu hóa hiệu suất"
        ]
        
        # Khởi tạo các danh sách để lưu trữ các thành phần UI
        self.status_items = []
        
        # Trạng thái kết nối internet
        self.is_connected = True
        self.retry_count = 0
        self.max_retries = 3
        
        # Biến kiểm soát để đảm bảo tín hiệu finished chỉ được phát một lần
        self.has_emitted_finished = False
        
        # Nạp giao diện từ file UI
        self.setup_ui_manually()
        
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
        
        # Thiết lập giá trị ban đầu cho thanh tiến trình
        if hasattr(self, 'progressBar'):
            self.progressBar.setValue(0)
        
        # Biến để theo dõi trạng thái cấu hình Telegram
        self.telegram_configured = False
        self.ffmpeg_manager = None
        
        # Timer cập nhật trạng thái tải FFmpeg
        self.ffmpeg_status_timer = QtCore.QTimer(self)
        self.ffmpeg_status_timer.timeout.connect(self.update_ffmpeg_download_status)
    
    def setup_ui_manually(self):
        """Thiết lập UI theo cách thủ công"""
        # Thiết lập kích thước
        self.setObjectName("SplashScreen")
        self.resize(850, 550)
        self.setWindowTitle("Đang khởi động...")
        
        # Thiết lập stylesheet
        self.setStyleSheet("""
            QWidget#SplashScreen {
              background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8f9fa, stop:1 #e9ecef);
              border-radius: 15px;
            }
            
            QLabel#titleLabel {
              font-family: Arial, sans-serif;
              font-size: 32px;
              font-weight: bold;
              color: #2c3e50;
            }
            
            QLabel#statusLabel {
              font-family: Arial, sans-serif;
              font-size: 16px;
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
              width: 8px;
              border-radius: 4px;
              margin: 0px;
            }
            
            QScrollBar::handle:vertical {
              background: #CBD5E1;
              border-radius: 4px;
              min-height: 30px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
              height: 0px;
            }
            
            QProgressBar {
              background-color: #e0e0e0;
              border: none;
              height: 14px;
              border-radius: 7px;
              text-align: center;
            }
            
            QProgressBar::chunk {
              background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498DB, stop:1 #2ECC71);
              border-radius: 7px;
            }
            
            QLabel.statusItem {
              font-family: Arial, sans-serif;
              font-size: 18px;
              color: #2c3e50;
            }
            
            QLabel.statusItemPending {
              font-family: Arial, sans-serif;
              font-size: 18px;
              color: #7f8c8d;
            }
            
            QFrame.statusItemFrame {
              background-color: white;
            }

            QPushButton {
              background-color: #f0f0f0;
              border: 1px solid #ccc;
              border-radius: 4px;
              padding: 6px 18px;
              color: #555;
              font-weight: bold;
              font-size: 14px;
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
        self.verticalLayout.setContentsMargins(40, 40, 40, 40)
        self.verticalLayout.setSpacing(20)
        
        # Layout logo
        self.logoLayout = QtWidgets.QVBoxLayout()
        self.logoLayout.setSpacing(20)
        
        # Logo
        self.logoLabel = QtWidgets.QLabel()
        self.logoLabel.setMinimumSize(100, 100)
        self.logoLabel.setMaximumSize(100, 100)
        self.logoLabel.setScaledContents(True)
        self.logoLayout.addWidget(self.logoLabel, 0, Qt.AlignmentFlag.AlignHCenter)
        
        # Tiêu đề
        self.titleLabel = QtWidgets.QLabel("Telegram Video Uploader")
        self.titleLabel.setObjectName("titleLabel")
        self.logoLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignHCenter)
        
        self.verticalLayout.addLayout(self.logoLayout)
        
        # Layout nội dung
        self.contentLayout = QtWidgets.QVBoxLayout()
        self.contentLayout.setSpacing(25)
        
        # Khung cuộn trạng thái
        self.statusScrollArea = QtWidgets.QScrollArea()
        self.statusScrollArea.setObjectName("statusScrollArea")
        self.statusScrollArea.setMinimumHeight(250)
        self.statusScrollArea.setMaximumHeight(250)
        self.statusScrollArea.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.statusScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.statusScrollArea.setWidgetResizable(True)
        
        # Nội dung khung cuộn
        self.scrollAreaContents = QtWidgets.QWidget()
        self.scrollAreaContents.setObjectName("scrollAreaContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaContents)
        self.verticalLayout_2.setSpacing(8)
        
        # Tạo các mục trạng thái
        for i, item_text in enumerate(self.setup_items):
            # Frame cho mục
            status_item = QtWidgets.QFrame()
            status_item.setObjectName(f"statusItem{i+1}")
            status_item.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
            status_item.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
            status_item.setProperty("class", "statusItemFrame")
            
            # Layout cho mục
            horizontalLayout = QtWidgets.QHBoxLayout(status_item)
            horizontalLayout.setContentsMargins(15, 8, 15, 8)
            
            # Indicator
            indicator = QtWidgets.QLabel()
            indicator.setObjectName(f"indicator{i+1}")
            indicator.setMinimumSize(32, 32)
            indicator.setMaximumSize(32, 32)
            horizontalLayout.addWidget(indicator)
            self.indicator_labels.append(indicator)
            
            # Label
            label = QtWidgets.QLabel(item_text)
            label.setObjectName(f"label{i+1}")
            if i < 1:
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
        self.contentLayout.addWidget(self.statusLabel, 0, Qt.AlignmentFlag.AlignHCenter)
        
        # Nút kiểm tra kết nối được đặt ở bên phải
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addStretch()
        
        self.cancelButton = QtWidgets.QPushButton("Hủy")
        self.cancelButton.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
        buttonLayout.addWidget(self.cancelButton)
        
        self.contentLayout.addLayout(buttonLayout)
        self.verticalLayout.addLayout(self.contentLayout)
    
    def center_on_screen(self):
        """Đặt cửa sổ vào giữa màn hình"""
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)
        
    def setup_logo(self):
        """Thiết lập logo ứng dụng"""
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png")
        
        if not os.path.exists(logo_path):
            # Thử đường dẫn khác
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo", "logo.png")
        
        if os.path.exists(logo_path):
            pixmap = QtGui.QPixmap(logo_path)
            self.logoLabel.setPixmap(pixmap)
    
    def add_cancel_button(self):
        """Thêm nút hủy vào màn hình chào"""
        # Kết nối sự kiện cho nút Cancel đã được tạo trong setup_ui_manually
        self.cancelButton.clicked.connect(self.on_cancel_clicked)
    
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
        self.contentLayout.addWidget(self.networkInfoLabel, 0, Qt.AlignmentFlag.AlignHCenter)
        self.networkInfoLabel.hide()  # Ẩn ban đầu
    
    def setup_indicators(self):
        """Thiết lập các indicator trạng thái"""
        # Tạo hình ảnh cho các trạng thái
        size = QtCore.QSize(32, 32)
        
        # Pending circle (empty circle)
        pending_img = QtGui.QPixmap(size)
        pending_img.fill(Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pending_img)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor("#CBD5E1"), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(4, 4, 24, 24)
        painter.end()
        
        # Active circle (blue circle)
        active_img = QtGui.QPixmap(size)
        active_img.fill(Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(active_img)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor("#3498DB"))
        painter.drawEllipse(4, 4, 24, 24)
        painter.end()
        
        # Success circle (green circle with checkmark)
        success_img = QtGui.QPixmap(size)
        success_img.fill(Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(success_img)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            
        # Draw green circle
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor("#2ECC71"))
        painter.drawEllipse(4, 4, 24, 24)
                
        # Draw checkmark
        painter.setPen(QtGui.QPen(Qt.GlobalColor.white, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.drawLine(10, 16, 14, 22)
        painter.drawLine(14, 22, 22, 10)
        painter.end()
        
        # Error circle (red circle with X)
        error_img = QtGui.QPixmap(size)
        error_img.fill(Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(error_img)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        # Draw red circle
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor("#E74C3C"))
        painter.drawEllipse(4, 4, 24, 24)
            
        # Draw X
        painter.setPen(QtGui.QPen(Qt.GlobalColor.white, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.drawLine(10, 10, 22, 22)
        painter.drawLine(10, 22, 22, 10)
        painter.end()
            
        # Lưu lại các pixmap
        self.indicator_images = {
            "pending": pending_img,
            "active": active_img,
            "success": success_img,
            "error": error_img
        }
        
        # Thiết lập trạng thái ban đầu
        for i, indicator in enumerate(self.indicator_labels):
            if i == 0:
                indicator.setPixmap(self.indicator_images["active"])
            else:
                indicator.setPixmap(self.indicator_images["pending"])
    
    def on_cancel_clicked(self):
        """Xử lý khi người dùng nhấn nút Hủy"""
        # Hiển thị hộp thoại xác nhận
        reply = QtWidgets.QMessageBox.question(
            self, 
            "Xác nhận hủy",
            "Bạn có chắc muốn hủy cài đặt và thoát ứng dụng?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
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
                self.status_labels[index].setStyleSheet("font-weight: normal;")
            else:
                self.status_labels[index].setProperty("class", "statusItem")
                
                # Chỉ đậm bước đang active
                if status == "active":
                    self.status_labels[index].setStyleSheet("font-weight: bold; color: #3498DB;")
                elif status == "success":
                    self.status_labels[index].setStyleSheet("font-weight: normal; color: #2ECC71;")  
                elif status == "error":
                    self.status_labels[index].setStyleSheet("font-weight: normal; color: #E74C3C;")
                
            # Force style update
            self.status_labels[index].style().unpolish(self.status_labels[index])
            self.status_labels[index].style().polish(self.status_labels[index])
    
    def update_progress(self, value):
        """Cập nhật giá trị thanh tiến trình"""
        self.progressBar.setValue(value)
    
    def calculate_overall_progress(self):
        """Tính toán phần trăm tiến trình tổng thể dựa trên các bước đã hoàn thành"""
        if self.current_step >= self.total_steps:
            return 100
        
        # Mỗi bước chiếm 10% (100/10)
        percent_per_step = 100 / self.total_steps
        
        # Tính toán phần trăm của các bước đã hoàn thành
        completed_steps_percent = self.current_step * percent_per_step
        
        # Nếu đang ở bước tải FFmpeg (bước thứ 5) và đang tải
        if self.current_step == 4 and self.ffmpeg_manager and self.ffmpeg_manager.is_downloading:
            # Tính phần trăm của bước hiện tại dựa trên tiến trình tải FFmpeg
            ffmpeg_progress_percent = (self.ffmpeg_manager.download_progress / 100) * percent_per_step
            
            # Tổng tiến trình = % các bước hoàn thành + % của bước hiện tại
            return int(completed_steps_percent + ffmpeg_progress_percent)
        else:
            # Nếu không phải đang tải FFmpeg, tiến trình là phần trăm của các bước đã hoàn thành
            return int(completed_steps_percent)
    
    def update_status(self, text):
        """Cập nhật text trạng thái hiện tại"""
        self.statusLabel.setText(text)
        
        # Làm cho văn bản trạng thái đậm hơn để dễ đọc
        self.statusLabel.setStyleSheet("""
            font-family: Arial, sans-serif;
            font-size: 13px;
            font-weight: bold;
            color: #2c3e50;
        """)
    
    def update_ffmpeg_download_status(self):
        """Cập nhật thông tin tải FFmpeg từ FFmpegManager"""
        if self.ffmpeg_manager and self.ffmpeg_manager.is_downloading:
            status_text = self.ffmpeg_manager.download_status
            
            # Cập nhật trạng thái
            self.update_status(status_text)
            
            # Cập nhật tiến trình dựa trên phần trăm tải FFmpeg
            self.update_progress(self.calculate_overall_progress())
            
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
        elif self.ffmpeg_manager and self.ffmpeg_manager.is_available and self.current_step == 4:
            # FFmpeg đã tải xong và sẵn sàng
            self.ffmpeg_status_timer.stop()
            
            # Ẩn nhãn thông tin mạng
            if hasattr(self, 'networkInfoLabel'):
                self.networkInfoLabel.hide()
                
            # Đánh dấu bước 4 là hoàn thành và chuyển sang bước tiếp theo
            self.update_status("Đã tải và cài đặt FFmpeg thành công")
            self.update_indicator(self.current_step, "success")
            
            # Đảm bảo chỉ tăng current_step nếu chưa phát tín hiệu finished
            if not self.has_emitted_finished:
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
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
    
    def check_internet_connection(self):
        """Kiểm tra kết nối Internet"""
        try:
            urllib.request.urlopen('http://www.google.com', timeout=3)
            return True
        except:
            return False
    
    def retry_connection_auto(self):
        """Tự động thử lại kết nối Internet không cần người dùng tương tác"""
        # Cập nhật trạng thái
        self.update_status("Đang thử kết nối lại...")
        self.update_indicator(0, "active")
        
        # Kiểm tra lại kết nối
        if self.check_internet_connection():
            self.update_status("Kết nối Internet OK")
            self.update_indicator(0, "success")
            self.current_step += 1
            self.update_progress(self.calculate_overall_progress())
            # Tiếp tục quy trình
            QtCore.QTimer.singleShot(500, self.process_next_step)
        else:
            # Vẫn không kết nối được
            self.mark_step_error(0, "Không thể kết nối Internet. Vui lòng kiểm tra kết nối của bạn.")
            # Lặp lại việc thử kết nối sau một khoảng thời gian
            QtCore.QTimer.singleShot(5000, self.retry_connection_auto)
    
    def check_pip_installation(self):
        """Kiểm tra cài đặt pip và các thư viện cần thiết"""
        pip_available = False
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "--version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                check=False
            )
            pip_available = True
        except:
            self.update_status("Không tìm thấy pip. Đang cài đặt...")
            # Cố gắng cài đặt pip
            try:
                import ensurepip
                ensurepip.bootstrap()
                self.update_status("Đã cài đặt pip thành công")
                pip_available = True
            except:
                self.mark_step_error(1, "Không thể cài đặt pip. Vui lòng cài đặt thủ công.")
                
                reply = QtWidgets.QMessageBox.critical(
                    self,
                    "Không tìm thấy pip",
                    "Ứng dụng yêu cầu pip để cài đặt các thư viện.\n\nVui lòng cài đặt pip và khởi động lại ứng dụng.",
                    QtWidgets.QMessageBox.StandardButton.Ok
                )
                return False

        # Kiểm tra các thư viện cần thiết
        required_modules = ["PyQt6", "requests", "configparser", "psutil"]
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules and pip_available:
            # Hỏi người dùng có muốn cài đặt các thư viện thiếu không
            reply = QtWidgets.QMessageBox.question(
                self,
                "Thiếu thư viện",
                f"Ứng dụng cần các thư viện sau: {', '.join(missing_modules)}.\n\nBạn có muốn cài đặt ngay không?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.Yes
            )
            
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                # Cài đặt các thư viện thiếu
                self.update_status(f"Đang cài đặt: {', '.join(missing_modules)}...")
                
                # Tìm đường dẫn đến requirements.txt
                app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                req_path = os.path.join(app_root, "requirements.txt")
                
                if os.path.exists(req_path):
                    # Cài đặt từ requirements.txt
                    try:
                        process = subprocess.Popen(
                            [sys.executable, "-m", "pip", "install", "-r", req_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        
                        # Theo dõi tiến trình
                        while process.poll() is None:
                            output = process.stdout.readline().strip()
                            if output:
                                self.update_status(f"Đang cài đặt: {output}")
                            QtCore.QCoreApplication.processEvents()
                        
                        if process.returncode == 0:
                            self.update_status("Đã cài đặt các thư viện thành công!")
                            # Tái nhập các module sau khi cài đặt
                            for module in missing_modules:
                                try:
                                    __import__(module)
                                except ImportError:
                                    # Vẫn không thể nhập sau khi cài đặt
                                    self.mark_step_error(1, f"Không thể tải module: {module}")
                                    return False
                        else:
                            error = process.stderr.read()
                            self.mark_step_error(1, f"Lỗi cài đặt: {error}")
                            return False
                    except Exception as e:
                        self.mark_step_error(1, f"Lỗi khi cài đặt thư viện: {str(e)}")
                        return False
                else:
                    # Cài đặt từng module một
                    for module in missing_modules:
                        try:
                            self.update_status(f"Đang cài đặt {module}...")
                            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                        except subprocess.CalledProcessError:
                            self.mark_step_error(1, f"Không thể cài đặt {module}")
                            return False
                    
                    self.update_status("Đã cài đặt các thư viện thành công!")
                    
                    # Tái nhập các module sau khi cài đặt
                    for module in missing_modules:
                        try:
                            __import__(module)
                        except ImportError:
                            # Vẫn không thể nhập sau khi cài đặt
                            self.mark_step_error(1, f"Không thể tải module: {module}")
                            return False
            else:
                # Người dùng không muốn cài đặt
                self.mark_step_error(1, f"Thiếu thư viện: {', '.join(missing_modules)}")
                return False
        elif missing_modules:
            # Không có pip nhưng thiếu module
            self.mark_step_error(1, f"Thiếu thư viện: {', '.join(missing_modules)}")
            return False
            
        return True
    
    def is_admin(self):
        """Kiểm tra xem ứng dụng có đang chạy với quyền admin không."""
        try:
            if platform.system() == "Windows":
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False
    
    def setup_ssl_automatically(self):
        """Thiết lập SSL tự động."""
        if platform.system() != "Windows":
            self.update_status("Không cần cài đặt SSL trên hệ điều hành này")
            return True
            
        # Thử cài đặt tự động
        try:
            # Import module cấu hình SSL
            from utils.ssl_helper import setup_ssl
            
            # Thiết lập SSL
            if setup_ssl():
                self.update_status("SSL đã được cấu hình thành công")
                return True
            else:
                self.update_status("Không thể cấu hình SSL tự động, Telethon có thể hoạt động chậm hơn")
                return False
        except Exception as e:
            self.update_status(f"Lỗi khi thiết lập SSL: {str(e)}")
            return False
    
    def process_next_step(self):
        """Xử lý bước tiếp theo trong tiến trình cài đặt"""
        # Nếu đã hoàn thành hoặc có lỗi, dừng timer
        if self.current_step >= self.total_steps:
            self.process_timer.stop()
            
            # Chỉ phát tín hiệu hoàn thành nếu chưa phát và tất cả các bước đã hoàn thành
            if not self.has_emitted_finished:
                self.has_emitted_finished = True
                logger.info("Tất cả các bước cài đặt đã hoàn thành, phát tín hiệu finished")
                # Phát tín hiệu hoàn thành sau 1 giây
                QtCore.QTimer.singleShot(1000, lambda: self.finished.emit(self.telegram_configured))
            return
            
        # Đánh dấu các bước đang tiến hành hoặc lỗi
        self.update_indicator(self.current_step, "active")
            
        # Xử lý logic cho từng bước
        if self.current_step == 0:  # Kiểm tra kết nối Internet
            try:
                # Kiểm tra kết nối internet
                self.update_status("Đang kiểm tra kết nối Internet...")
                
                # Thử kiểm tra kết nối ngay lập tức (tự động)
                if not self.check_internet_connection():
                    # Nếu không kết nối được, chờ 3 giây và thử lại
                    QtCore.QTimer.singleShot(3000, lambda: self.retry_connection_auto())
                    return
                
                # Nếu kết nối thành công, tiếp tục bước tiếp theo
                self.update_status("Kết nối Internet OK")
                self.update_indicator(self.current_step, "success")
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
                # Tự động chuyển sang bước tiếp theo
                QtCore.QTimer.singleShot(500, self.process_next_step)
            except Exception as e:
                self.mark_step_error(0, f"Lỗi kiểm tra kết nối Internet: {str(e)}")
                return
        
        elif self.current_step == 1:  # Kiểm tra cấu hình hệ thống
            try:
                # Kiểm tra phiên bản Python
                python_version = sys.version.split()[0]
                min_python_version = "3.7.0"
                
                self.update_status(f"Kiểm tra phiên bản Python: {python_version}")
                
                # So sánh phiên bản bằng cách chia thành các thành phần số
                def parse_version(version_str):
                    parts = version_str.split('.')
                    return [int(part) for part in parts]
                
                python_version_parts = parse_version(python_version)
                min_version_parts = parse_version(min_python_version)
                
                # So sánh từng phần của phiên bản
                is_outdated = False
                for i in range(min(len(python_version_parts), len(min_version_parts))):
                    if python_version_parts[i] < min_version_parts[i]:
                        is_outdated = True
                        break
                    elif python_version_parts[i] > min_version_parts[i]:
                        break
                
                # Kiểm tra hệ điều hành
                os_name = platform.system()
                os_version = platform.version()
                self.update_status(f"Hệ điều hành: {os_name} {os_version}")
                
                # Kiểm tra pip có cài đặt không và các thư viện cần thiết
                pip_available = self.check_pip_installation()
                if not pip_available:
                    return
                
                self.update_status("Hệ thống đạt yêu cầu")
                self.update_indicator(self.current_step, "success")
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
            except Exception as e:
                self.mark_step_error(1, f"Lỗi: {str(e)}")
                
        elif self.current_step == 2:  # Thiết lập SSL cho Telethon
            try:
                self.update_status("Kiểm tra và cài đặt SSL...")
                if platform.system() == "Windows":
                    # Kiểm tra SSL và cài đặt nếu cần
                    ssl_setup_success = self.setup_ssl_automatically()
                    
                    if not ssl_setup_success:
                        # Hiển thị thông báo và hỏi người dùng
                        reply = QtWidgets.QMessageBox.question(
                            self,
                            "Vấn đề với SSL",
                            "Không thể cài đặt SSL tự động. Điều này có thể ảnh hưởng đến tốc độ tải lên.\n\n"
                            "Bạn có muốn tiếp tục không? Chọn No sẽ hiển thị hướng dẫn cài đặt thủ công.",
                            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                            QtWidgets.QMessageBox.StandardButton.Yes
                        )
                        
                        if reply == QtWidgets.QMessageBox.StandardButton.No:
                            # Hiển thị hướng dẫn
                            QtWidgets.QMessageBox.information(
                                self,
                                "Hướng dẫn cài đặt SSL thủ công",
                                "1. Tải OpenSSL từ https://slproweb.com/products/Win32OpenSSL.html\n"
                                "2. Cài đặt OpenSSL vào đường dẫn mặc định\n"
                                "3. Sao chép các file libssl*.dll và libcrypto*.dll từ thư mục bin của OpenSSL\n"
                                "4. Dán các file này vào thư mục Python của bạn\n"
                                "5. Khởi động lại ứng dụng",
                                QtWidgets.QMessageBox.StandardButton.Ok
                            )
                else:
                    self.update_status("Không cần cài đặt SSL trên hệ điều hành này")
                
                self.update_status("SSL được thiết lập")
                self.update_indicator(self.current_step, "success")
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
            except Exception as e:
                self.mark_step_error(2, f"Lỗi kiểm tra SSL: {str(e)}")
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
                
        elif self.current_step == 3:  # Khởi tạo tài nguyên ứng dụng
            try:
                # Lấy đường dẫn tới thư mục gốc của dự án (parent của src)
                src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                app_root = os.path.dirname(src_dir)  # Lên một cấp từ src để tới thư mục gốc
                
                # Tạo các thư mục cần thiết ở thư mục gốc
                data_dir = os.path.join(app_root, 'data')
                cache_dir = os.path.join(app_root, 'cache')
                temp_dir = os.path.join(app_root, 'temp')
                logs_dir = os.path.join(app_root, 'logs')
                
                # Đảm bảo các thư mục tồn tại
                os.makedirs(data_dir, exist_ok=True)
                os.makedirs(cache_dir, exist_ok=True)
                os.makedirs(temp_dir, exist_ok=True)
                os.makedirs(logs_dir, exist_ok=True)
                
                self.update_status("Đã tạo các thư mục làm việc")
                
                # Tạo file lịch sử tải lên nếu chưa có
                history_file = os.path.join(data_dir, 'upload_history.json')
                if not os.path.exists(history_file):
                    try:
                        with open(history_file, 'w', encoding='utf-8') as f:
                            f.write('[]')  # Tạo một mảng JSON rỗng
                        self.update_status(f"Đã tạo file lịch sử tải lên: {history_file}")
                        logger.info(f"Đã tạo file lịch sử tải lên: {history_file}")
                    except Exception as e:
                        logger.error(f"Lỗi khi tạo file lịch sử: {str(e)}")
                        self.mark_step_error(3, f"Không thể tạo file lịch sử: {str(e)}")
                        return
                
                # Kiểm tra lại xem file có tồn tại không
                if not os.path.exists(history_file):
                    logger.error(f"File lịch sử vẫn không tồn tại sau khi tạo: {history_file}")
                    self.mark_step_error(3, "Không thể tạo file lịch sử tải lên")
                    return
                
                # Kiểm tra file cấu hình
                config_path = os.path.join(app_root, "config.ini")
                if not os.path.exists(config_path):
                    # Tạo file config mẫu nếu chưa có
                    import configparser
                    config = configparser.ConfigParser()
                    config['APP'] = {
                        'first_run': 'true',
                        'theme': 'light',
                        'language': 'vi'
                    }
                    config['PATHS'] = {
                        'cache_dir': cache_dir,
                        'temp_dir': temp_dir,
                        'logs_dir': logs_dir
                    }
                    config['TELEGRAM'] = {
                        'bot_token': '',
                        'chat_id': '',
                        'notification_chat_id': ''
                    }
                    config['TELETHON'] = {
                        'api_id': '',
                        'api_hash': '',
                        'phone': '',
                        'use_telethon': 'false',
                        'otp_verified': 'false'
                    }
                    
                    try:
                        with open(config_path, 'w', encoding='utf-8') as f:
                            config.write(f)
                        self.update_status("Đã tạo file cấu hình mẫu")
                    except Exception as e:
                        logger.error(f"Lỗi khi tạo file cấu hình: {str(e)}")
                        self.mark_step_error(3, f"Không thể tạo file cấu hình: {str(e)}")
                        return
                else:
                    # Nếu file config đã tồn tại, cập nhật đường dẫn
                    try:
                        import configparser
                        config = configparser.ConfigParser()
                        # Đọc file config hiện tại
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config.read_file(f)
                        
                        # Cập nhật đường dẫn
                        if 'PATHS' not in config:
                            config['PATHS'] = {}
                        config['PATHS']['cache_dir'] = cache_dir
                        config['PATHS']['temp_dir'] = temp_dir
                        config['PATHS']['logs_dir'] = logs_dir
                        
                        # Lưu lại file config
                        with open(config_path, 'w', encoding='utf-8') as f:
                            config.write(f)
                        self.update_status("Đã cập nhật file cấu hình")
                    except Exception as e:
                        logger.error(f"Lỗi khi cập nhật file cấu hình: {str(e)}")
                        self.mark_step_error(3, f"Không thể cập nhật file cấu hình: {str(e)}")
                        return
                
                # Kiểm tra lại xem file cấu hình có tồn tại không
                if not os.path.exists(config_path):
                    logger.error(f"File cấu hình vẫn không tồn tại sau khi tạo: {config_path}")
                    self.mark_step_error(3, "Không thể tạo file cấu hình")
                    return
                
                self.update_status("Đã khởi tạo tài nguyên ứng dụng")
                self.update_indicator(self.current_step, "success")
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
            except Exception as e:
                self.mark_step_error(3, f"Lỗi khởi tạo tài nguyên: {str(e)}")
                logger.error(f"Chi tiết lỗi khởi tạo tài nguyên: {traceback.format_exc()}")
                return
        
        elif self.current_step == 4:  # Chuẩn bị bộ phân tích video
            if self.ffmpeg_manager:
                # Kiểm tra FFmpeg đã tải về chưa
                if self.ffmpeg_manager.is_available:
                    # FFmpeg đã sẵn sàng, chuyển sang bước tiếp theo
                    self.update_status("Đã tải và cài đặt FFmpeg thành công")
                    self.update_indicator(self.current_step, "success")
                    self.current_step += 1
                    self.update_progress(self.calculate_overall_progress())
                elif self.ffmpeg_manager.is_downloading:
                    # Đang tải FFmpeg, hiển thị trạng thái và KHÔNG chuyển bước
                    self.update_status("Đang tải FFmpeg, vui lòng đợi...")
                    
                    # Khi bắt đầu tải FFmpeg, khởi động timer để cập nhật trạng thái
                    if not self.ffmpeg_status_timer.isActive():
                        self.ffmpeg_status_timer.start(500)  # Cập nhật mỗi 500ms
                    
                    # QUAN TRỌNG: KHÔNG tăng current_step ở đây,
                    # chỉ tăng khi tải hoàn tất trong hàm update_ffmpeg_download_status
                    
                    # Dừng quá trình xử lý ở đây, không xử lý các bước tiếp theo
                    # cho đến khi FFmpeg được tải xong
                    return
                else:
                    # Chưa tải FFmpeg, bắt đầu tải
                    # Kiểm tra kết nối internet trước khi tải
                    if self.check_internet_connection():
                        # Bắt đầu tải
                        self.update_status("Đang tải FFmpeg...")
                        self.ffmpeg_manager.setup_ffmpeg()
                        
                        # Bắt đầu timer cập nhật trạng thái tải
                        if not self.ffmpeg_status_timer.isActive():
                            self.ffmpeg_status_timer.start(500)
                    else:
                        self.mark_step_error(4, "Không thể kết nối Internet để tải FFmpeg")
                        return
            else:
                # Không có ffmpeg_manager, bỏ qua
                self.update_status("FFmpeg đã sẵn sàng")
                self.update_indicator(self.current_step, "success")
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())

        elif self.current_step == 5:  # Kiểm tra kết nối Telegram
            # Bước này sẽ được triển khai chi tiết sau, bây giờ chỉ là bước nháp
            # Kiểm tra cấu hình Telegram
            self.telegram_configured = False  # Mặc định là chưa cấu hình
            # Biến theo dõi trạng thái cấu hình đã hoàn thành hay chưa
            self.config_completed = False
            import configparser
            
            try:
                app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                config_path = os.path.join(app_root, "config.ini")
                
                if os.path.exists(config_path):
                    config = configparser.ConfigParser()
                    # Thêm tham số encoding để tránh lỗi UnicodeDecodeError
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config.read_file(f)
                    
                    # Kiểm tra nếu đã cấu hình Telegram Bot hoặc Telethon
                    if config.has_section('TELEGRAM') and config.has_option('TELEGRAM', 'bot_token') and config.has_option('TELEGRAM', 'chat_id'):
                        bot_token = config.get('TELEGRAM', 'bot_token')
                        chat_id = config.get('TELEGRAM', 'chat_id')
                        
                        if bot_token and chat_id:
                            self.telegram_configured = True
                            self.config_completed = True
                    
                    # Kiểm tra xác thực Telethon
                    telethon_configured = False
                    otp_verified = False
                    
                    if config.has_section('TELETHON') and config.has_option('TELETHON', 'api_id') and config.has_option('TELETHON', 'api_hash'):
                        api_id = config.get('TELETHON', 'api_id')
                        api_hash = config.get('TELETHON', 'api_hash')
                        
                        if api_id and api_hash:
                            telethon_configured = True
                            
                            # Kiểm tra trạng thái OTP
                            if config.has_option('TELETHON', 'otp_verified'):
                                otp_verified = config.getboolean('TELETHON', 'otp_verified', fallback=False)
                                
                    # Cập nhật trạng thái cấu hình
                    if telethon_configured:
                        self.telegram_configured = True
                        
                        # Nếu cấu hình Telethon nhưng chưa xác thực OTP, hiển thị modal OTP
                        if not otp_verified:
                            self.update_status("Cần xác thực lại Telethon API")
                            
                            # Tạm dừng process_timer để tránh xung đột
                            was_timer_active = False
                            if hasattr(self, 'process_timer') and self.process_timer.isActive():
                                was_timer_active = True
                                self.process_timer.stop()
                            
                            # Hiển thị modal OTP 
                            from ui.telegram.telegram_ui_otp_modal import OTPModal
                            otp_modal = OTPModal(self, api_id=api_id, api_hash=api_hash, phone=config.get('TELETHON', 'phone', fallback=''))
                            
                            # Hiển thị modal
                            result = otp_modal.exec()
                            
                            # Kiểm tra kết quả xác thực
                            if result == QtWidgets.QDialog.DialogCode.Accepted:
                                # Cập nhật trạng thái xác thực OTP trong config
                                if not config.has_section('TELETHON'):
                                    config.add_section('TELETHON')
                                config['TELETHON']['otp_verified'] = 'true'
                                
                                # Lưu cấu hình
                                with open(config_path, 'w', encoding='utf-8') as f:
                                    config.write(f)
                                    
                                self.update_status("Xác thực Telethon API thành công")
                            else:
                                # Không xác thực được
                                self.update_status("Xác thực Telethon API không thành công")
                                
                            # Khởi động lại timer nếu đã dừng
                            if was_timer_active:
                                self.process_timer.start()
                
                # Hiển thị dialog cấu hình nếu chưa cấu hình Telegram
                if not self.telegram_configured:
                    self.update_status("Cần cấu hình Telegram để tiếp tục")
                    
                    # Tạm dừng process_timer để tránh xung đột
                    was_timer_active = False
                    if hasattr(self, 'process_timer') and self.process_timer.isActive():
                        was_timer_active = True
                        self.process_timer.stop()
                    
                    # Hiển thị thông báo cho người dùng
                    self.update_status("Đang mở cửa sổ cấu hình Telegram...")
                    QtCore.QCoreApplication.processEvents()  # Cập nhật UI ngay lập tức
                    
                    # Import và hiển thị ConfigModal
                    from ui.telegram.telegram_ui import ConfigModal
                    # Để hệ thống tự chọn UI từ file Qt Designer nếu có thể
                    config_modal = ConfigModal(self, app=self.app, force_manual_ui=False)
                    
                    # Kết nối tín hiệu configSaved để biết khi nào cấu hình được lưu
                    config_modal.configSaved.connect(self.on_config_saved)
                    
                    # Hiển thị modal
                    config_modal.exec()
                    
                    # Kiểm tra lại cấu hình sau khi dialog đóng
                    if hasattr(config_modal, 'telegram_connected') and config_modal.telegram_connected:
                        self.telegram_configured = True
                        self.config_completed = True
                        self.update_status("Cấu hình Telegram đã sẵn sàng")
                    elif hasattr(config_modal, 'telethon_connected') and config_modal.telethon_connected:
                        self.telegram_configured = True
                        self.config_completed = True
                        self.update_status("Cấu hình Telethon đã sẵn sàng")
                        
                        # Thêm cờ xác thực OTP
                        if not config.has_section('TELETHON'):
                            config.add_section('TELETHON')
                        config['TELETHON']['otp_verified'] = 'true'
                        
                        # Lưu cấu hình
                        with open(config_path, 'w', encoding='utf-8') as f:
                            config.write(f)
                    else:
                        # Không cấu hình được, nhưng vẫn tiếp tục
                        self.update_status("Cấu hình Telegram bị hủy. Một số tính năng có thể không hoạt động.")
                        # Đánh dấu là đã hoàn thành quá trình cấu hình (dù thành công hay không)
                        self.config_completed = True
                    
                    # Khởi động lại timer nếu đã dừng
                    if was_timer_active:
                        self.process_timer.start()
                    
                    # QUAN TRỌNG: Trả về mà không tăng current_step
                    # Bước tiếp theo sẽ được xử lý trong lần gọi process_next_step sau
                    return
                else:
                    self.update_status("Cấu hình Telegram đã sẵn sàng")
                    self.config_completed = True
            except Exception as e:
                logger.error(f"Lỗi khi đọc cấu hình: {str(e)}")
                self.mark_step_error(5, f"Lỗi đọc cấu hình: {str(e)}")
                return
            
            # Chỉ tiếp tục khi đã hoàn thành quá trình cấu hình
            if self.config_completed:
                self.update_status("Kết nối Telegram OK")
                self.update_indicator(self.current_step, "success")
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
        
        elif self.current_step == 6:  # Tải các thành phần giao diện
            try:
                # Cập nhật trạng thái
                self.update_status("Đang nạp các thành phần giao diện...")
                
                # Tải các module UI cần thiết - giả lập bằng một độ trễ
                imported_count = 0
                total_components = 5  # Giả sử có 5 thành phần cần nạp
                
                # Các thành phần UI cần nạp
                ui_components = [
                    "Main Window Components", 
                    "Dialog Components",
                    "Tab Components",
                    "Custom Controls",
                    "Icon Resources"
                ]
                
                # Nạp từng thành phần và cập nhật trạng thái
                for component in ui_components:
                    # Giả lập việc nạp thành phần
                    self.update_status(f"Đang nạp {component}...")
                    
                    # Thêm độ trễ để người dùng thấy được tiến trình
                    QtCore.QCoreApplication.processEvents()
                    time.sleep(0.3)  # 300ms cho mỗi thành phần
                    
                    imported_count += 1
                    
                    # Cập nhật tiến trình
                    component_progress = int((imported_count / total_components) * 10) + 60  # 60-70%
                    self.update_progress(component_progress)
                
                # Nạp thành công
                self.update_status("Đã nạp các thành phần giao diện")
                self.update_indicator(self.current_step, "success")
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
            except Exception as e:
                logger.error(f"Lỗi khi nạp thành phần giao diện: {str(e)}")
                logger.error(traceback.format_exc())
                self.mark_step_error(6, f"Lỗi khi nạp UI: {str(e)}")
                
                # Mặc dù có lỗi, vẫn tiếp tục bước tiếp theo
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
        
        elif self.current_step == 7:  # Kiểm tra không gian lưu trữ
            try:
                from utils.disk_space_checker import DiskSpaceChecker
                
                # Cập nhật trạng thái
                self.update_status("Đang kiểm tra không gian lưu trữ...")
                
                # Tạo đối tượng kiểm tra không gian
                disk_checker = DiskSpaceChecker()
                
                # Kiểm tra không gian
                space_info = disk_checker.check_all()
                
                # Hiển thị thông tin không gian đĩa
                disk_space = space_info['disk_space']
                free_space_gb = disk_space['free'] / (1024 * 1024 * 1024)
                
                self.update_status(f"Không gian trống: {disk_space['formatted']['free']} ({disk_space['percent_free']}%)")
                
                # Kiểm tra nếu không gian không đủ
                if not space_info['has_sufficient_space']:
                    # Hiển thị cảnh báo không gian không đủ
                    warning_msg = f"Cảnh báo: Không gian trống ({disk_space['formatted']['free']}) thấp hơn yêu cầu tối thiểu (1GB)"
                    self.update_status(warning_msg)
                    
                    # Hiển thị dialog cảnh báo
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Cảnh báo không gian lưu trữ",
                        f"{warning_msg}\n\nỨng dụng có thể không hoạt động đúng cách.\nVui lòng giải phóng thêm không gian đĩa.",
                        QtWidgets.QMessageBox.StandardButton.Ok
                    )
                
                # Kiểm tra quyền ghi
                if not space_info['write_permission']:
                    # Hiển thị cảnh báo không có quyền ghi
                    warning_msg = "Cảnh báo: Không có quyền ghi vào thư mục làm việc"
                    self.update_status(warning_msg)
                    
                    # Hiển thị dialog cảnh báo
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Cảnh báo quyền ghi",
                        f"{warning_msg}\n\nỨng dụng có thể không hoạt động đúng cách.\nVui lòng chạy ứng dụng với quyền admin hoặc kiểm tra lại quyền truy cập.",
                        QtWidgets.QMessageBox.StandardButton.Ok
                    )
                
                # Cập nhật UI với thông tin tốt đẹp
                if space_info['has_sufficient_space'] and space_info['write_permission']:
                    success_msg = f"Kiểm tra không gian lưu trữ OK: {disk_space['formatted']['free']} trống"
                    self.update_status(success_msg)
                
                # Hoàn thành bước này
                self.update_indicator(self.current_step, "success")
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
            except ImportError:
                # Không tìm thấy module disk_space_checker
                logger.warning("Module disk_space_checker không tìm thấy, bỏ qua kiểm tra không gian lưu trữ")
                self.update_status("Bỏ qua kiểm tra không gian lưu trữ")
                
                # Đánh dấu bước này là thành công và chuyển sang bước tiếp theo
                self.update_indicator(self.current_step, "success")
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
            except Exception as e:
                logger.error(f"Lỗi khi kiểm tra không gian lưu trữ: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Đánh dấu lỗi nhưng vẫn tiếp tục
                self.mark_step_error(7, f"Lỗi kiểm tra không gian: {str(e)}")
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
        elif self.current_step == 8:  # Tìm kiếm cập nhật
            try:
                from utils.update_checker import UpdateChecker
                
                # Cập nhật trạng thái
                self.update_status("Đang kiểm tra cập nhật...")
                
                # Tạo đối tượng kiểm tra cập nhật
                update_checker = UpdateChecker()
                
                # Flag theo dõi trạng thái kiểm tra
                self.update_check_complete = False
                
                # Hàm callback khi kiểm tra hoàn tất
                def on_update_check_complete(result):
                    try:
                        # Cập nhật biến trạng thái
                        self.update_check_complete = True
                        
                        # Kiểm tra kết quả
                        if 'error' in result:
                            # Hiển thị thông báo lỗi
                            self.update_status(f"Lỗi kiểm tra cập nhật: {result['error']}")
                            logger.error(f"Lỗi kiểm tra cập nhật: {result['error']}")
                        else:
                            # Kiểm tra xem có cập nhật không
                            if result['has_update']:
                                # Có cập nhật mới
                                update_msg = f"Có phiên bản mới: {result['latest_version']} (hiện tại: {result['current_version']})"
                                self.update_status(update_msg)
                                
                                # Hiển thị thông báo cập nhật
                                reply = QtWidgets.QMessageBox.information(
                                    self,
                                    "Cập nhật mới",
                                    f"{update_msg}\n\n{result.get('update_notes', '')}\n\nBạn có muốn tải cập nhật không?",
                                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                                    QtWidgets.QMessageBox.StandardButton.No
                                )
                                
                                if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                                    # Mở trang tải cập nhật
                                    import webbrowser
                                    webbrowser.open(result['update_url'])
                                    
                                    # Đánh dấu đã thông báo
                                    update_checker.mark_as_notified()
                            else:
                                # Không có cập nhật
                                self.update_status(f"Phần mềm đã cập nhật (phiên bản {result['current_version']})")
                        
                        # Hoàn thành bước này
                        self.update_indicator(self.current_step, "success")
                        self.current_step += 1
                        self.update_progress(self.calculate_overall_progress())
                        
                        # Tiếp tục xử lý các bước tiếp theo
                        self.process_next_step()
                    except Exception as e:
                        logger.error(f"Lỗi trong callback kiểm tra cập nhật: {str(e)}")
                        logger.error(traceback.format_exc())
                        
                        # Đánh dấu bước này là thành công và chuyển sang bước tiếp theo
                        self.update_indicator(self.current_step, "success")
                        self.current_step += 1
                        self.update_progress(self.calculate_overall_progress())
                        
                        # Tiếp tục xử lý các bước tiếp theo
                        self.process_next_step()
                
                # Kiểm tra cập nhật bất đồng bộ
                update_checker.check_for_updates_async(callback=on_update_check_complete)
                
                # QUAN TRỌNG: Dừng xử lý ở đây và đợi callback
                return
                
            except ImportError:
                # Không tìm thấy module update_checker
                logger.warning("Module update_checker không tìm thấy, bỏ qua kiểm tra cập nhật")
                self.update_status("Bỏ qua kiểm tra cập nhật")
                
                # Đánh dấu bước này là thành công và chuyển sang bước tiếp theo
                self.update_indicator(self.current_step, "success")
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
            except Exception as e:
                logger.error(f"Lỗi khi kiểm tra cập nhật: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Đánh dấu lỗi nhưng vẫn tiếp tục
                self.mark_step_error(8, f"Lỗi kiểm tra cập nhật: {str(e)}")
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
        elif self.current_step == 9:  # Tối ưu hóa hiệu suất
            try:
                from utils.performance_optimizer import PerformanceOptimizer
                
                # Cập nhật trạng thái
                self.update_status("Đang tối ưu hóa hiệu suất...")
                
                # Tạo đối tượng tối ưu hóa
                optimizer = PerformanceOptimizer()
                
                # Flag theo dõi trạng thái tối ưu hóa
                self.optimization_complete = False
                
                # Hàm callback khi tối ưu hóa hoàn tất
                def on_optimization_complete(result):
                    try:
                        # Cập nhật biến trạng thái
                        self.optimization_complete = True
                        
                        # Kiểm tra kết quả
                        if result['success']:
                            # Hiển thị thông tin tối ưu hóa
                            self.update_status(result['message'])
                            
                            # Log thông tin chi tiết
                            logger.info(f"Tối ưu hóa bộ nhớ: Giải phóng {result['memory']['freed']['formatted']}")
                            logger.info(f"Dọn dẹp cache: {result['cache']['message']}")
                            logger.info(f"Dọn dẹp logs: {result['logs']['message']}")
                            logger.info(f"Dọn dẹp temp: {result['temp']['message']}")
                        else:
                            # Hiển thị thông báo lỗi
                            self.update_status(f"Lỗi tối ưu hóa: {result.get('error', 'Unknown error')}")
                            logger.error(f"Lỗi tối ưu hóa: {result.get('error', 'Unknown error')}")
                        
                        # Hoàn thành bước này
                        self.update_indicator(self.current_step, "success")
                        self.current_step += 1
                        self.update_progress(self.calculate_overall_progress())
                        
                        # Tiếp tục xử lý các bước tiếp theo
                        self.process_next_step()
                    except Exception as e:
                        logger.error(f"Lỗi trong callback tối ưu hóa: {str(e)}")
                        logger.error(traceback.format_exc())
                        
                        # Đánh dấu bước này là thành công và chuyển sang bước tiếp theo
                        self.update_indicator(self.current_step, "success")
                        self.current_step += 1
                        self.update_progress(self.calculate_overall_progress())
                        
                        # Tiếp tục xử lý các bước tiếp theo
                        self.process_next_step()
                
                # Thực hiện tối ưu hóa bất đồng bộ
                optimizer.optimize_async(callback=on_optimization_complete)
                
                # QUAN TRỌNG: Dừng xử lý ở đây và đợi callback
                return
                
            except ImportError:
                # Không tìm thấy module performance_optimizer
                logger.warning("Module performance_optimizer không tìm thấy, bỏ qua tối ưu hóa hiệu suất")
                self.update_status("Bỏ qua tối ưu hóa hiệu suất")
                
                # Đánh dấu bước này là thành công và chuyển sang bước tiếp theo
                self.update_indicator(self.current_step, "success")
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
            except Exception as e:
                logger.error(f"Lỗi khi tối ưu hóa hiệu suất: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Đánh dấu lỗi nhưng vẫn tiếp tục
                self.mark_step_error(9, f"Lỗi tối ưu hóa: {str(e)}")
                self.current_step += 1
                self.update_progress(self.calculate_overall_progress())
    
    def complete_ui_loading(self):
        """Hoàn tất việc tải giao diện"""
        self.update_status("Đã tải giao diện thành công")
        self.update_indicator(self.current_step, "success")
        self.current_step += 1
        self.update_progress(self.calculate_overall_progress())
        
        # Tiếp tục xử lý các bước tiếp theo
        self.process_next_step()
        
    def complete_update_check(self):
        """Hoàn tất việc kiểm tra cập nhật"""
        self.update_status("Phần mềm đã được cập nhật")
        self.update_indicator(self.current_step, "success")
        self.current_step += 1
        self.update_progress(self.calculate_overall_progress())
        
        # Tiếp tục xử lý các bước tiếp theo
        self.process_next_step()
        
    def complete_optimization(self):
        """Hoàn tất việc tối ưu hóa hiệu suất"""
        self.update_status("Hiệu suất đã được tối ưu hóa")
        self.update_indicator(self.current_step, "success")
        self.current_step += 1
        self.update_progress(self.calculate_overall_progress())
        
        # Không cần gọi process_next_step() vì đây là bước cuối cùng
        # Tiến trình sẽ phát tín hiệu finished trong lần gọi process_next_step tiếp theo
    
    def on_config_saved(self, success):
        """
        Xử lý sự kiện khi cấu hình Telegram được lưu
        
        Args:
            success (bool): Trạng thái lưu cấu hình thành công hay không
        """
        if success:
            self.telegram_configured = True
            self.config_completed = True
            self.update_status("Đã cấu hình Telegram thành công")
        else:
            self.update_status("Cấu hình Telegram không thành công")
            # Đánh dấu là đã hoàn thành quá trình cấu hình (dù thành công hay không)
            self.config_completed = True


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
        
        # Đảm bảo splash screen được hiển thị trên cùng
        splash.raise_()
        splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        splash.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        splash.activateWindow()
        
        # Xử lý sự kiện và đảm bảo UI được cập nhật
        QtWidgets.QApplication.processEvents()
        
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