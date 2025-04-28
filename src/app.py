"""
Telegram Video Uploader Application
==================================

Main application to upload videos to Telegram with advanced features.
"""
import os
import sys
import logging
from queue import Queue
import traceback
import platform

# Kiểm tra phiên bản Python
python_version = platform.python_version_tuple()
python_version_float = float(f"{python_version[0]}.{python_version[1]}")

# Đã cập nhật: Import PyQt6 thay vì PyQt5
from PyQt6 import QtWidgets, QtCore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("telegram_uploader.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TelegramUploader")

# Thiết lập SSL sớm trước khi import Telethon
from utils.ssl_helper import setup_ssl

# Kiểm tra và thiết lập SSL (quan trọng cho Telethon trên Windows)
try:
    ssl_ready = setup_ssl()
    if ssl_ready:
        logger.info("SSL được cấu hình thành công")
    else:
        logger.warning("Không thể cấu hình SSL, Telethon có thể hoạt động chậm hơn")
except Exception as e:
    logger.error(f"Lỗi khi thiết lập SSL: {str(e)}")
    logger.error(traceback.format_exc())

# Import FFmpeg Manager
from utils.ffmpeg_manager import FFmpegManager

# Import UI modules
from ui.splash_screen import show_splash_screen, SplashScreen
from ui.main_tab.main_ui import MainUI

# Import core modules
from core.config_manager import ConfigManager
from utils.telegram.telegram_connector import TelegramConnector

# Import utilities
from utils.video_analyzer import VideoAnalyzer
from utils.upload_history import UploadHistory

# Import các module mới
from utils.disk_space_checker import DiskSpaceChecker
from utils.update_checker import UpdateChecker
from utils.performance_optimizer import PerformanceOptimizer

class TelegramUploaderApp:
    """
    Main application for uploading videos to Telegram.
    """
    def __init__(self):
        """
        Initialize the application.
        """
        self.app = None
        self.main_window = None
        self.is_uploading = False
        self.splash_screen = None
        
        # Khởi tạo ứng dụng Qt trước khi tiếp tục
        self.app = QtWidgets.QApplication(sys.argv)
        
        # Khởi tạo FFmpeg Manager
        self.ffmpeg_manager = FFmpegManager()
        
        # Set up components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize core components"""
        logger.info("Initializing application components")
        
        # Initialize configuration
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # Initialize video analyzer
        self.video_analyzer = VideoAnalyzer()
        
        # Initialize upload history
        app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(app_root, 'data')
        os.makedirs(data_dir, exist_ok=True)  # Đảm bảo thư mục data tồn tại
        history_file = os.path.join(data_dir, 'upload_history.json')
        self.upload_history = UploadHistory(history_file)
        
        # Initialize task queue
        self.task_queue = Queue()
        
        # Khởi tạo các module tiện ích mới
        self.disk_checker = DiskSpaceChecker()
        self.update_checker = UpdateChecker()
        self.performance_optimizer = PerformanceOptimizer()
        
        # Initialize Telegram connection - chỉ khởi tạo sau splash screen
        self.telegram_connector = None
        self.telegram_api = None
        self.telethon_uploader = None
    
    def _setup_telegram_connection(self):
        """Thiết lập kết nối Telegram sau khi splash screen hoàn tất"""
        # Khởi tạo Telegram Connector
        self.telegram_connector = TelegramConnector(self)
        self.telegram_api = self.telegram_connector.telegram_api
        self.telethon_uploader = self.telegram_connector.telethon_uploader
    
    def _setup_ui(self):
        """Set up application UI - only create the main window, don't show it yet"""
        try:
            # Tạo cửa sổ chính (không hiển thị)
            self._create_main_window()
            logger.info("UI setup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error setting up UI: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _create_main_window(self):
        """Create main application window"""
        self.main_window = QtWidgets.QMainWindow()
        
        # Thiết lập thuộc tính cửa sổ
        self.main_window.setWindowTitle("Telegram Video Uploader")
        self.main_window.resize(1200, 800)
        self.main_window.setMinimumSize(1024, 768)
        
        # Widget chính
        self.central_widget = QtWidgets.QWidget()
        self.main_window.setCentralWidget(self.central_widget)
        
        # Layout chính
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Tạo main tab trực tiếp
        self._setup_main_tab()
        
        # Kết nối sự kiện đóng cửa sổ
        self.main_window.closeEvent = self._on_close_event
    
    def _setup_main_tab(self):
        """Setup main tab"""
        # Khởi tạo MainUI
        self.main_tab = MainUI(app_instance=self)
        
        # Thêm trực tiếp vào layout chính
        self.main_layout.addWidget(self.main_tab)
    
    def _on_close_event(self, event):
        """Handle Qt window close event"""
        # Ask for confirmation if uploading
        if self.is_uploading:
            reply = QtWidgets.QMessageBox.question(
                self.main_window,
                "Xác nhận",
                "Đang tải video lên. Bạn có chắc muốn thoát?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No
            )
            
            if reply == QtWidgets.QMessageBox.StandardButton.No:
                event.ignore()
                return
        
        # Hỏi người dùng có muốn xóa xác thực OTP không
        if self.config.has_section('TELETHON') and self.config.has_option('TELETHON', 'otp_verified') and self.config.getboolean('TELETHON', 'otp_verified', fallback=False):
            reply = QtWidgets.QMessageBox.question(
                self.main_window,
                "Xác thực Telethon",
                "Bạn có muốn xóa xác thực Telethon API hiện tại không?\nNếu chọn 'Có', lần sau bạn sẽ cần xác thực lại mã OTP.",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No
            )
            
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                # Xóa xác thực
                self.config['TELETHON']['otp_verified'] = 'false'
                # Lưu cấu hình
                self.config_manager.save_config(self.config)
                logger.info("Đã xóa xác thực Telethon API")
        
        # Save configuration
        self.config_manager.save_config(self.config)
        
        # Disconnect APIs
        if hasattr(self, 'telegram_api') and self.telegram_api:
            self.telegram_api.disconnect()
        
        if hasattr(self, 'telethon_uploader') and self.telethon_uploader:
            self.telethon_uploader.disconnect()
        
        # Accept close event
        event.accept()
    
    def _on_splash_screen_canceled(self):
        """Xử lý khi splash screen bị hủy"""
        logger.info("Splash screen canceled by user, exiting application")
        # Thoát ứng dụng
        self.app.quit()
    
    def run(self):
        """
        Chạy ứng dụng và hiển thị giao diện người dùng
        """
        try:
            # Hiển thị splash screen
            self.splash_screen = show_splash_screen(self.app, self.ffmpeg_manager)
            
            # Kết nối tín hiệu finished từ splash screen để hiển thị cửa sổ chính
            self.splash_screen.finished.connect(self.on_splash_screen_finished)
            
            # Kết nối tín hiệu canceled từ splash screen để đóng ứng dụng
            self.splash_screen.canceled.connect(self._on_splash_screen_canceled)
            
            # QUAN TRỌNG: Không hiển thị main_window ở đây, sẽ hiển thị trong hàm on_splash_screen_finished
            # khi splash screen đã thực sự hoàn thành
            
            # Chạy vòng lặp sự kiện Qt
            return self.app.exec()
                
        except Exception as e:
            logging.error(f"Lỗi khi khởi chạy ứng dụng: {str(e)}")
            logging.error(traceback.format_exc())
            
            # Hiển thị dialog lỗi với Qt
            QtWidgets.QMessageBox.critical(None, "Lỗi khởi động", 
                                f"Không thể khởi động ứng dụng: {str(e)}\n\n"
                                f"Chi tiết: {traceback.format_exc()}")
            
            return 1
            
    def setup_ui(self):
        """Set up application UI - only create the main window, don't show it yet"""
        try:
            # Tạo cửa sổ chính (không hiển thị)
            self._create_main_window()
            logger.info("UI setup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error setting up UI: {e}")
            logger.error(traceback.format_exc())
            return False
            
    def on_splash_screen_finished(self, telegram_configured):
        """
        Xử lý khi splash screen hoàn thành
        
        Args:
            telegram_configured (bool): Cho biết có cấu hình Telegram không
        """
        try:
            # Lưu trạng thái cấu hình Telegram
            self.telegram_configured = telegram_configured
            
            # Thiết lập kết nối Telegram sau khi splash screen hoàn tất
            if telegram_configured:
                self._setup_telegram_connection()
            
            # Khởi tạo cửa sổ chính nếu chưa có
            if not hasattr(self, 'main_window') or self.main_window is None:
                self.setup_ui()
            
            # Đóng splash screen
            if hasattr(self, 'splash_screen') and self.splash_screen:
                # Tắt các timer trước khi đóng
                if hasattr(self.splash_screen, 'process_timer') and self.splash_screen.process_timer.isActive():
                    self.splash_screen.process_timer.stop()
                if hasattr(self.splash_screen, 'ffmpeg_status_timer') and self.splash_screen.ffmpeg_status_timer.isActive():
                    self.splash_screen.ffmpeg_status_timer.stop()
                
                # Đóng splash screen
                self.splash_screen.close()
                self.splash_screen = None
            
            # Hiển thị cửa sổ chính
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            
            # Đảm bảo cửa sổ chính được hiển thị
            # Xử lý sự kiện và cập nhật giao diện
            QtWidgets.QApplication.processEvents()
            
            # Kiểm tra nếu cần hiển thị dialog cấu hình Telegram
            if not self.telegram_configured:
                self.show_telegram_config_dialog()
            
            logging.info("Đã khởi động ứng dụng thành công với giao diện Qt")
        except Exception as e:
            logging.error(f"Lỗi trong hàm on_splash_screen_finished: {str(e)}")
            logging.error(traceback.format_exc())