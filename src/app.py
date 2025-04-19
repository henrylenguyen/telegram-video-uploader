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

# Import PyQt5
from PyQt5 import QtWidgets, QtCore

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

# Import UI modules
from ui.splash_screen import show_splash_screen, SplashScreen
from ui.main_tab.main_ui import MainUI

# Import core modules
from core.config_manager import ConfigManager
from core.telegram_connector import TelegramConnector

# Import utilities
from utils.video_analyzer import VideoAnalyzer
from utils.upload_history import UploadHistory
from utils.ffmpeg_manager import FFmpegManager

class TelegramUploaderApp:
    """
    Main application for uploading videos to Telegram.
    """
    def __init__(self):
        """
        Initialize the application.
        """
        self.qt_app = None
        self.main_window = None
        self.is_uploading = False
        self.splash_screen = None
        
        # Khởi tạo ứng dụng Qt trước khi tiếp tục
        self.qt_app = QtWidgets.QApplication(sys.argv)
        
        # Set up components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize core components"""
        logger.info("Initializing application components")
        
        # Initialize configuration
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # Initialize FFmpeg manager
        self.ffmpeg_manager = FFmpegManager()
        
        # Initialize video analyzer
        self.video_analyzer = VideoAnalyzer()
        
        # Initialize upload history
        history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload_history.json')
        self.upload_history = UploadHistory(history_file)
        
        # Initialize task queue
        self.task_queue = Queue()
        
        # Initialize Telegram connection
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
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            
            if reply == QtWidgets.QMessageBox.No:
                event.ignore()
                return
        
        # Save configuration
        self.config_manager.save_config(self.config)
        
        # Disconnect APIs
        if hasattr(self, 'telegram_api'):
            self.telegram_api.disconnect()
        
        if hasattr(self, 'telethon_uploader'):
            self.telethon_uploader.disconnect()
        
        # Accept close event
        event.accept()
    
    def _on_splash_screen_canceled(self):
        """Xử lý khi splash screen bị hủy"""
        logger.info("Splash screen canceled by user, exiting application")
        # Thoát ứng dụng
        self.qt_app.quit()
    
    def run(self):
        """Run the application"""
        try:
            # Hiển thị splash screen trước
            self.splash_screen = show_splash_screen(self.qt_app, self.ffmpeg_manager)
            
            # Kết nối tín hiệu finished từ splash screen để thiết lập và hiển thị cửa sổ chính
            self.splash_screen.finished.connect(self._on_splash_screen_finished)
            
            # Kết nối tín hiệu hủy
            if hasattr(self.splash_screen, 'canceled'):
                self.splash_screen.canceled.connect(self._on_splash_screen_canceled)
            
            # Run Qt application
            return self.qt_app.exec_()
        except Exception as e:
            logger.error(f"Error running application: {e}")
            logger.error(traceback.format_exc())
            return 1
            
    def _on_splash_screen_finished(self, telegram_configured):
        """Xử lý sự kiện khi splash screen hoàn thành"""
        try:
            # Thiết lập UI chính sau khi splash screen đã hoàn thành
            self._setup_ui()
            
            # Hiển thị cửa sổ chính
            self.main_window.show()
            
            logger.info("Main window shown after splash screen completed")
        except Exception as e:
            logger.error(f"Error showing main window: {e}")
            logger.error(traceback.format_exc())