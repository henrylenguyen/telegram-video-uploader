"""
Module xử lý giao diện cấu hình Telegram và Telethon API.
"""
import os
import sys
import logging
import configparser
import traceback
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt, pyqtSignal

from .telegram_ui_otp_modal import OTPModal

logger = logging.getLogger(__name__)

class ConfigModal(QtWidgets.QDialog):
    """
    Modal cấu hình Telegram và Telethon API
    """
    # Tín hiệu khi cấu hình được lưu
    configSaved = pyqtSignal(bool)
    
    def __init__(self, parent=None, app=None, force_manual_ui=False):
        """
        Khởi tạo modal cấu hình
        
        Args:
            parent: Parent widget
            app: Đối tượng ứng dụng chính
            force_manual_ui (bool): Buộc tạo UI thủ công thay vì từ file UI
        """
        super().__init__(parent)
        self.app = app
        self.parent = parent
        
        # Trạng thái kết nối
        self.telegram_connected = False
        self.telethon_connected = False
        
        # Trạng thái wizard
        self.current_step = 1  # Bắt đầu với Telegram Bot API
        self.total_steps = 2
        
        # Trạng thái nút lưu
        self.bot_tab_completed = False
        self.telethon_tab_completed = False
        
        # Tạo UI
        self.setup_ui_manually() if force_manual_ui else self.load_ui_from_designer()
        
        # Kết nối các sự kiện
        self.connect_events()
        
        # Nạp cấu hình nếu có
        self.load_config()
        
        # Cập nhật UI dựa trên trạng thái ban đầu
        self.update_step_ui()
        self.update_save_button_state()
    
    def load_ui_from_designer(self):
        """Nạp UI từ file thiết kế"""
        self.setWindowTitle("Cấu hình Telegram")
        self.setMinimumSize(700, 600)
        self.setMaximumSize(800, 650)
        
        # Sử dụng stylesheet từ file ui_telethon_modal.py
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                font-family: Arial;
            }

            QTabWidget::pane {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                background-color: #FFFFFF;
                top: -1px;
                margin: 0px 20px;
            }

            QTabBar::tab {
                background-color: #FFFFFF;
                color: #64748B;
                padding: 12px 0px;
                font-size: 14px;
                border: none;
                width: 180px;
                font-family: Arial;
                margin-left: 0px; 
            }

            QTabBar::tab:first {
                margin-left: 20px; 
            }

            QTabBar::tab:selected {
                color: #3498DB;
                border-bottom: 3px solid #3498DB;
                background-color: #EBF5FB;
                font-weight: bold;
            }

            QTabBar::tab:hover:!selected {
                color: #3498DB;
                background-color: #F5F9FF;
            }

            QScrollArea {
                border: none;
                background-color: transparent;
            }

            QWidget#scrollContent {
                background-color: transparent;
            }

            QLabel.titleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1E293B;
                background-color: transparent;
                font-family: Arial;
            }

            QLabel.infoBox {
                background-color: #EBF5FB;
                color: #3498DB;
                border: 1px solid #BFDBFE;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                font-family: Arial;
                margin-bottom: 15px;
            }

            QLabel.fieldLabel {
                font-size: 14px;
                font-weight: bold;
                color: #1E293B;
                font-family: Arial;
            }

            QLabel.fieldHint {
                font-size: 13px;
                color: #64748B;
                font-family: Arial;
            }

            QLineEdit {
                border: 1px solid #E4E7EB;
                border-radius: 6px;
                padding: 15px;
                background-color: #FFFFFF;
                font-size: 14px;
                color: #1E293B;
                font-family: Arial;
            }

            QPushButton.primaryButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
                font-family: Arial;
                height: 36px;
            }

            QPushButton.primaryButton:hover {
                background-color: #2980B9;
            }

            QPushButton.secondaryButton {
                background-color: #EBF5FB;
                color: #3498DB;
                border: 1px solid #BFDBFE;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 14px;
                font-family: Arial;
                height: 36px;
            }

            QPushButton.secondaryButton:hover {
                background-color: #D1E6FA;
            }

            QPushButton.outlineButton {
                background-color: #FFFFFF;
                color: #64748B;
                border: 1px solid #E4E7EB;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 14px;
                font-family: Arial;
                height: 36px;
            }

            QLabel.statusSuccess {
                background-color: #F0FFF4;
                color: #2ECC71;
                border: 1px solid #C6F6D5;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                font-family: Arial;
                margin-top: 10px;
                margin-bottom: 10px;
            }

            QLabel.statusError {
                background-color: #FFF5F5;
                color: #E53E3E;
                border: 1px solid #FED7D7;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                font-family: Arial;
                margin-top: 10px;
                margin-bottom: 10px;
            }

            QLabel.statusWarning {
                background-color: #FFFBEB;
                color: #F59E0B;
                border: 1px solid #FEF3C7;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                font-family: Arial;
                margin-top: 10px;
                margin-bottom: 10px;
            }
        """)
        
        # ==== Layout chính ====
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # ==== Header ====
        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setMinimumHeight(50)
        self.header_widget.setMaximumHeight(50)
        self.header_widget.setStyleSheet("background-color: #F9FAFB;")
        
        self.header_layout = QtWidgets.QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(20, 10, 20, 10)
        
        self.title_label = QtWidgets.QLabel("Cấu hình Telegram")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B;")
        
        self.header_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.header_widget)
        
        # ==== Wizard ====
        self.wizard_widget = QtWidgets.QWidget()
        self.wizard_widget.setMinimumHeight(60)
        self.wizard_widget.setMaximumHeight(60)
        self.wizard_widget.setStyleSheet("background-color: #F9FAFB;")
        
        self.wizard_layout = QtWidgets.QHBoxLayout(self.wizard_widget)
        self.wizard_layout.setContentsMargins(20, 5, 20, 5)
        
        self.steps_layout = QtWidgets.QHBoxLayout()
        self.steps_layout.setSpacing(15)
        
        # Step 1
        self.step1_label = QtWidgets.QLabel("1")
        self.step1_label.setMinimumSize(32, 32)
        self.step1_label.setMaximumSize(32, 32)
        self.step1_label.setStyleSheet("""
            background-color: #3498DB;
            color: white;
            border-radius: 16px;
            font-size: 14px;
            font-weight: bold;
        """)
        self.step1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.step_text_label1 = QtWidgets.QLabel("Cấu hình Telegram Bot API")
        self.step_text_label1.setStyleSheet("""
            color: #3498DB;
            font-size: 14px;
            font-weight: bold;
        """)
        
        # Line giữa các step
        self.step_line = QtWidgets.QLabel()
        self.step_line.setMinimumSize(40, 1)
        self.step_line.setMaximumSize(40, 1)
        self.step_line.setStyleSheet("background-color: #CBD5E1;")
        
        # Step 2
        self.step2_label = QtWidgets.QLabel("2")
        self.step2_label.setMinimumSize(32, 32)
        self.step2_label.setMaximumSize(32, 32)
        self.step2_label.setStyleSheet("""
            background-color: #CBD5E1;
            color: white;
            border-radius: 16px;
            font-size: 14px;
            font-weight: bold;
        """)
        self.step2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.step_text_label2 = QtWidgets.QLabel("Cấu hình Telethon API")
        self.step_text_label2.setStyleSheet("""
            color: #64748B;
            font-size: 14px;
        """)
        
        # Thêm các item vào layout
        self.steps_layout.addWidget(self.step1_label)
        self.steps_layout.addWidget(self.step_text_label1)
        self.steps_layout.addWidget(self.step_line)
        self.steps_layout.addWidget(self.step2_label)
        self.steps_layout.addWidget(self.step_text_label2)
        self.steps_layout.addStretch()
        
        self.wizard_layout.addLayout(self.steps_layout)
        self.main_layout.addWidget(self.wizard_widget)
        
        # ==== Tab Widget ====
        self.config_tab_widget = QtWidgets.QTabWidget()
        self.config_tab_widget.setMinimumHeight(420)
        self.config_tab_widget.setMaximumHeight(420)
        
        # Tab Bot API
        self.bot_api_tab = QtWidgets.QWidget()
        self.bot_api_tab_layout = QtWidgets.QVBoxLayout(self.bot_api_tab)
        self.bot_api_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.bot_api_tab_layout.setSpacing(0)
        
        # Scroll Area cho Bot API
        self.bot_api_scroll_area = QtWidgets.QScrollArea()
        self.bot_api_scroll_area.setWidgetResizable(True)
        self.bot_api_scroll_area.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        
        self.bot_api_content = QtWidgets.QWidget()
        self.bot_api_content_layout = QtWidgets.QVBoxLayout(self.bot_api_content)
        self.bot_api_content_layout.setSpacing(15)
        self.bot_api_content_layout.setContentsMargins(20, 20, 20, 15)
        
        # Thêm nội dung của tab Bot API
        self.create_bot_api_tab_content()
        
        self.bot_api_scroll_area.setWidget(self.bot_api_content)
        self.bot_api_tab_layout.addWidget(self.bot_api_scroll_area)
        
        # Tab Telethon API
        self.telethon_api_tab = QtWidgets.QWidget()
        self.telethon_api_tab_layout = QtWidgets.QVBoxLayout(self.telethon_api_tab)
        self.telethon_api_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.telethon_api_tab_layout.setSpacing(0)
        
        # Scroll Area cho Telethon API
        self.telethon_api_scroll_area = QtWidgets.QScrollArea()
        self.telethon_api_scroll_area.setWidgetResizable(True)
        self.telethon_api_scroll_area.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        
        self.telethon_api_content = QtWidgets.QWidget()
        self.telethon_api_content_layout = QtWidgets.QVBoxLayout(self.telethon_api_content)
        self.telethon_api_content_layout.setSpacing(15)
        self.telethon_api_content_layout.setContentsMargins(20, 15, 20, 15)
        
        # Thêm nội dung của tab Telethon API
        self.create_telethon_api_tab_content()
        
        self.telethon_api_scroll_area.setWidget(self.telethon_api_content)
        self.telethon_api_tab_layout.addWidget(self.telethon_api_scroll_area)
        
        # Thêm các tab vào TabWidget
        self.config_tab_widget.addTab(self.bot_api_tab, "Telegram Bot API")
        self.config_tab_widget.addTab(self.telethon_api_tab, "Telethon API")
        
        # Kết nối sự kiện thay đổi tab
        self.config_tab_widget.currentChanged.connect(self.on_tab_changed)
        
        self.main_layout.addWidget(self.config_tab_widget)
        
        # ==== Footer ====
        self.footer_widget = QtWidgets.QWidget()
        self.footer_widget.setMinimumHeight(60)
        self.footer_widget.setMaximumHeight(60)
        self.footer_widget.setStyleSheet("background-color: #F9FAFB;")
        
        self.footer_layout = QtWidgets.QHBoxLayout(self.footer_widget)
        self.footer_layout.setContentsMargins(20, 10, 20, 10)
        self.footer_layout.setSpacing(15)
        
        self.draft_button = QtWidgets.QPushButton("Lưu dạng bản nháp")
        self.draft_button.setMinimumSize(150, 36)
        self.draft_button.setMaximumSize(150, 36)
        self.draft_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #64748B;
                border: 1px solid #E4E7EB;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background-color: #F5F9FF;
                color: #3498DB;
            }
        """)
        self.draft_button.setProperty("class", "outlineButton")
        
        self.save_button = QtWidgets.QPushButton("Lưu cài đặt")
        self.save_button.setMinimumSize(150, 36)
        self.save_button.setMaximumSize(150, 36)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #2980B9;
            }
            
            QPushButton:disabled {
                background-color: #CBD5E1;
                color: white;
            }
        """)
        self.save_button.setProperty("class", "primaryButton")
        self.save_button.setEnabled(False)
        
        self.footer_layout.addWidget(self.draft_button)
        self.footer_layout.addStretch()
        self.footer_layout.addWidget(self.save_button)
        
        self.main_layout.addWidget(self.footer_widget)
    
    def create_bot_api_tab_content(self):
        """Tạo nội dung của tab Bot API"""
        # Info Box
        self.bot_info_label = QtWidgets.QLabel("Để sử dụng ứng dụng, bạn cần cấu hình Telegram Bot API bằng cách tạo bot với @BotFather\nvà cung cấp token cùng với chat ID của nhóm nơi bạn muốn tải video lên.")
        self.bot_info_label.setMinimumHeight(60)
        self.bot_info_label.setMaximumHeight(60)
        self.bot_info_label.setStyleSheet("""
            background-color: #EBF5FB;
            color: #3498DB;
            border: 1px solid #BFDBFE;
            border-radius: 6px;
            padding: 8px;
            font-size: 13px;
        """)
        self.bot_info_label.setAlignment(Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.bot_info_label.setWordWrap(True)
        
        self.bot_api_content_layout.addWidget(self.bot_info_label)
        
        # Token Container
        self.token_container = QtWidgets.QWidget()
        self.token_layout = QtWidgets.QVBoxLayout(self.token_container)
        self.token_layout.setSpacing(5)
        self.token_layout.setContentsMargins(0, 0, 0, 0)
        
        # Token Header
        self.token_header_layout = QtWidgets.QHBoxLayout()
        
        self.token_label = QtWidgets.QLabel("Token Telegram")
        self.token_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E293B;")
        
        self.token_hint_label = QtWidgets.QLabel("(Tìm trong @BotFather)")
        self.token_hint_label.setStyleSheet("font-size: 13px; color: #64748B;")
        
        self.token_header_layout.addWidget(self.token_label)
        self.token_header_layout.addWidget(self.token_hint_label)
        self.token_header_layout.addStretch()
        
        self.token_layout.addLayout(self.token_header_layout)
        
        # Token Input
        self.token_line_edit = QtWidgets.QLineEdit()
        self.token_line_edit.setMinimumHeight(45)
        self.token_line_edit.setMaximumHeight(45)
        self.token_line_edit.setPlaceholderText("110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw")
        
        self.token_layout.addWidget(self.token_line_edit)
        
        self.bot_api_content_layout.addWidget(self.token_container)
        
        # Chat ID Container
        self.chat_id_container = QtWidgets.QWidget()
        self.chat_id_layout = QtWidgets.QVBoxLayout(self.chat_id_container)
        self.chat_id_layout.setSpacing(5)
        self.chat_id_layout.setContentsMargins(0, 0, 0, 0)
        
        # Chat ID Header
        self.chat_id_header_layout = QtWidgets.QHBoxLayout()
        
        self.chat_id_label = QtWidgets.QLabel("Chat ID")
        self.chat_id_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E293B;")
        
        self.chat_id_hint_label = QtWidgets.QLabel("(Có định dạng: -100xxxxxxxxx)")
        self.chat_id_hint_label.setStyleSheet("font-size: 13px; color: #64748B;")
        
        self.chat_id_header_layout.addWidget(self.chat_id_label)
        self.chat_id_header_layout.addWidget(self.chat_id_hint_label)
        self.chat_id_header_layout.addStretch()
        
        self.chat_id_layout.addLayout(self.chat_id_header_layout)
        
        # Chat ID Input
        self.chat_id_line_edit = QtWidgets.QLineEdit()
        self.chat_id_line_edit.setMinimumHeight(45)
        self.chat_id_line_edit.setMaximumHeight(45)
        self.chat_id_line_edit.setPlaceholderText("-1001234567890")
        
        self.chat_id_layout.addWidget(self.chat_id_line_edit)
        
        self.bot_api_content_layout.addWidget(self.chat_id_container)
        
        # Separator
        self.separator1 = QtWidgets.QFrame()
        self.separator1.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.separator1.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        
        self.bot_api_content_layout.addWidget(self.separator1)
        
        # Connection Status
        self.connection_status_label = QtWidgets.QLabel()
        self.connection_status_label.setMinimumHeight(40)
        self.connection_status_label.setMaximumHeight(40)
        self.connection_status_label.setProperty("class", "statusWarning")
        self.connection_status_label.setText("⚠ Chưa kết nối đến Telegram API")
        self.connection_status_label.setStyleSheet("""
            background-color: #FFFBEB;
            color: #F59E0B;
            border: 1px solid #FEF3C7;
            border-radius: 6px;
            padding: 8px;
            font-size: 13px;
        """)
        
        self.bot_api_content_layout.addWidget(self.connection_status_label)
        
        # Connection Check Button
        self.connection_check_layout = QtWidgets.QHBoxLayout()
        self.connection_check_layout.setSpacing(15)
        
        self.btn_check_connection = QtWidgets.QPushButton("Kiểm tra kết nối")
        self.btn_check_connection.setMinimumSize(150, 36)
        self.btn_check_connection.setMaximumHeight(36)
        self.btn_check_connection.setStyleSheet("""
            QPushButton {
                background-color: #EBF5FB;
                color: #3498DB;
                border: 1px solid #BFDBFE;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background-color: #D1E6FA;
            }
        """)
        self.btn_check_connection.setProperty("class", "secondaryButton")
        
        self.connection_check_layout.addWidget(self.btn_check_connection)
        self.connection_check_layout.addStretch()
        
        self.bot_api_content_layout.addLayout(self.connection_check_layout)
        
        # Spacer
        self.bot_api_content_layout.addStretch()
    
    def create_telethon_api_tab_content(self):
        """Tạo nội dung của tab Telethon API"""
        # Info Box
        self.telethon_info_label = QtWidgets.QLabel("Telethon API cho phép tải lên các file lớn hơn 50MB. Để sử dụng tính năng này,\nvui lòng đăng ký và nhập API ID, API Hash từ my.telegram.org.")
        self.telethon_info_label.setMinimumHeight(60)
        self.telethon_info_label.setMaximumHeight(60)
        self.telethon_info_label.setStyleSheet("""
            background-color: #EBF5FB;
            color: #3498DB;
            border: 1px solid #BFDBFE;
            border-radius: 6px;
            padding: 8px;
            font-size: 13px;
        """)
        self.telethon_info_label.setAlignment(Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.telethon_info_label.setWordWrap(True)
        
        self.telethon_api_content_layout.addWidget(self.telethon_info_label)
        
        # API ID Container
        self.api_id_container = QtWidgets.QWidget()
        self.api_id_layout = QtWidgets.QVBoxLayout(self.api_id_container)
        self.api_id_layout.setSpacing(5)
        self.api_id_layout.setContentsMargins(0, 0, 0, 0)
        
        # API ID Header
        self.api_id_header_layout = QtWidgets.QHBoxLayout()
        
        self.api_id_label = QtWidgets.QLabel("API ID")
        self.api_id_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E293B;")
        
        self.api_id_hint_label = QtWidgets.QLabel("(Có định dạng: 2xxxxxx)")
        self.api_id_hint_label.setStyleSheet("font-size: 13px; color: #64748B;")
        
        self.api_id_header_layout.addWidget(self.api_id_label)
        self.api_id_header_layout.addWidget(self.api_id_hint_label)
        self.api_id_header_layout.addStretch()
        
        self.api_id_layout.addLayout(self.api_id_header_layout)
        
        # API ID Input
        self.api_id_line_edit = QtWidgets.QLineEdit()
        self.api_id_line_edit.setMinimumHeight(45)
        self.api_id_line_edit.setMaximumHeight(45)
        self.api_id_line_edit.setPlaceholderText("Nhập API ID (ví dụ: 2xxxxxx)")
        
        self.api_id_layout.addWidget(self.api_id_line_edit)
        
        self.telethon_api_content_layout.addWidget(self.api_id_container)
        
        # API Hash Container
        self.api_hash_container = QtWidgets.QWidget()
        self.api_hash_layout = QtWidgets.QVBoxLayout(self.api_hash_container)
        self.api_hash_layout.setSpacing(5)
        self.api_hash_layout.setContentsMargins(0, 0, 0, 0)
        
        # API Hash Header
        self.api_hash_header_layout = QtWidgets.QHBoxLayout()
        
        self.api_hash_label = QtWidgets.QLabel("API Hash")
        self.api_hash_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E293B;")
        
        self.api_hash_hint_label = QtWidgets.QLabel("(Có định dạng: 7xxxxe)")
        self.api_hash_hint_label.setStyleSheet("font-size: 13px; color: #64748B;")
        
        self.api_hash_header_layout.addWidget(self.api_hash_label)
        self.api_hash_header_layout.addWidget(self.api_hash_hint_label)
        self.api_hash_header_layout.addStretch()
        
        self.api_hash_layout.addLayout(self.api_hash_header_layout)
        
        # API Hash Input with Toggle Button
        self.api_hash_input_layout = QtWidgets.QHBoxLayout()
        self.api_hash_input_layout.setSpacing(0)
        
        self.api_hash_line_edit = QtWidgets.QLineEdit()
        self.api_hash_line_edit.setMinimumHeight(45)
        self.api_hash_line_edit.setMaximumHeight(45)
        self.api_hash_line_edit.setPlaceholderText("Nhập API Hash (ví dụ: 7xxxxe)")
        self.api_hash_line_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.api_hash_line_edit.setStyleSheet("""
            border-top-right-radius: 0px;
            border-bottom-right-radius: 0px;
        """)
        
        self.toggle_password_button = QtWidgets.QPushButton("👁️")
        self.toggle_password_button.setMinimumSize(40, 45)
        self.toggle_password_button.setMaximumSize(40, 45)
        self.toggle_password_button.setStyleSheet("""
            background-color: #F1F5F9;
            border: 1px solid #E4E7EB;
            border-left: none;
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
            font-size: 18px;
            color: #64748B;
        """)
        
        self.api_hash_input_layout.addWidget(self.api_hash_line_edit)
        self.api_hash_input_layout.addWidget(self.toggle_password_button)
        
        self.api_hash_layout.addLayout(self.api_hash_input_layout)
        
        self.telethon_api_content_layout.addWidget(self.api_hash_container)
        
        # Phone Container
        self.phone_container = QtWidgets.QWidget()
        self.phone_layout = QtWidgets.QVBoxLayout(self.phone_container)
        self.phone_layout.setSpacing(5)
        self.phone_layout.setContentsMargins(0, 0, 0, 0)
        
        # Phone Header
        self.phone_header_layout = QtWidgets.QHBoxLayout()
        
        self.phone_label = QtWidgets.QLabel("Số điện thoại")
        self.phone_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E293B;")
        
        self.phone_hint_label = QtWidgets.QLabel("(Có định dạng: +84123456789)")
        self.phone_hint_label.setStyleSheet("font-size: 13px; color: #64748B;")
        
        self.phone_header_layout.addWidget(self.phone_label)
        self.phone_header_layout.addWidget(self.phone_hint_label)
        self.phone_header_layout.addStretch()
        
        self.phone_layout.addLayout(self.phone_header_layout)
        
        # Phone Input
        self.phone_line_edit = QtWidgets.QLineEdit()
        self.phone_line_edit.setMinimumHeight(45)
        self.phone_line_edit.setMaximumHeight(45)
        self.phone_line_edit.setPlaceholderText("+84123456789")
        
        self.phone_layout.addWidget(self.phone_line_edit)
        
        self.telethon_api_content_layout.addWidget(self.phone_container)
        
        # Separator
        self.separator2 = QtWidgets.QFrame()
        self.separator2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.separator2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        
        self.telethon_api_content_layout.addWidget(self.separator2)
        
        # OTP Status and Button
        self.otp_status_layout = QtWidgets.QHBoxLayout()
        self.otp_status_layout.setSpacing(10)
        
        self.otp_status_label = QtWidgets.QLabel("⚠ Chưa xác thực! Cần xác thực OTP")
        self.otp_status_label.setMinimumHeight(36)
        self.otp_status_label.setMaximumHeight(36)
        self.otp_status_label.setStyleSheet("""
            background-color: #FFF5F5;
            color: #E53E3E;
            border: 1px solid #FED7D7;
            border-radius: 6px;
            padding: 8px;
            font-size: 13px;
        """)
        
        self.get_otp_button = QtWidgets.QPushButton("Lấy mã xác thực")
        self.get_otp_button.setMinimumSize(150, 36)
        self.get_otp_button.setMaximumSize(150, 36)
        self.get_otp_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        self.get_otp_button.setProperty("class", "primaryButton")
        
        self.otp_status_layout.addWidget(self.otp_status_label)
        self.otp_status_layout.addWidget(self.get_otp_button)
        
        self.telethon_api_content_layout.addLayout(self.otp_status_layout)
        
        # API Help Link
        self.api_help_label = QtWidgets.QLabel("<a href=\"#\" style=\"color: #3498DB;\">Làm thế nào để lấy API ID và Hash?</a>")
        self.api_help_label.setStyleSheet("color: #3498DB; font-size: 13px; text-decoration: underline;")
        self.api_help_label.setTextFormat(Qt.TextFormat.RichText)
        self.api_help_label.setOpenExternalLinks(False)
        
        self.telethon_api_content_layout.addWidget(self.api_help_label)
        
        # Spacer
        self.telethon_api_content_layout.addStretch()
    
    def setup_ui_manually(self):
        """Thiết lập UI theo cách thủ công"""
        # Đây sẽ là phương thức dự phòng nếu không thể tải UI từ file
        # Trong trường hợp thực tế, bạn sẽ triển khai nội dung tương tự như load_ui_from_designer
        # Ở đây chỉ tạo một UI đơn giản
        pass
    
    def connect_events(self):
        """Kết nối các sự kiện của UI"""
        # Bot API tab
        self.btn_check_connection.clicked.connect(self.check_telegram_connection)
        self.token_line_edit.textChanged.connect(self.on_bot_api_input_changed)
        self.chat_id_line_edit.textChanged.connect(self.on_bot_api_input_changed)
        
        # Telethon API tab
        self.api_id_line_edit.textChanged.connect(self.on_telethon_api_input_changed)
        self.api_hash_line_edit.textChanged.connect(self.on_telethon_api_input_changed)
        self.phone_line_edit.textChanged.connect(self.on_telethon_api_input_changed)
        self.toggle_password_button.clicked.connect(self.toggle_api_hash_visibility)
        self.get_otp_button.clicked.connect(self.get_otp_verification)
        self.api_help_label.linkActivated.connect(self.show_api_help)
        
        # Footer
        self.draft_button.clicked.connect(self.save_as_draft)
        self.save_button.clicked.connect(self.save_config)
    
    def load_config(self):
        """Nạp cấu hình từ file"""
        try:
            # Lấy đường dẫn đến file cấu hình
            app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(app_root, "config.ini")
            
            if os.path.exists(config_path):
                config = configparser.ConfigParser()
                with open(config_path, 'r', encoding='utf-8') as f:
                    config.read_file(f)
                
                # Nạp cấu hình Bot API
                if 'TELEGRAM' in config:
                    if 'bot_token' in config['TELEGRAM']:
                        self.token_line_edit.setText(config['TELEGRAM']['bot_token'])
                    if 'chat_id' in config['TELEGRAM']:
                        self.chat_id_line_edit.setText(config['TELEGRAM']['chat_id'])
                
                # Nạp cấu hình Telethon API
                if 'TELETHON' in config:
                    if 'api_id' in config['TELETHON']:
                        self.api_id_line_edit.setText(config['TELETHON']['api_id'])
                    if 'api_hash' in config['TELETHON']:
                        self.api_hash_line_edit.setText(config['TELETHON']['api_hash'])
                    if 'phone' in config['TELETHON']:
                        self.phone_line_edit.setText(config['TELETHON']['phone'])
                    
                    # Kiểm tra trạng thái xác thực OTP
                    if 'otp_verified' in config['TELETHON'] and config.getboolean('TELETHON', 'otp_verified', fallback=False):
                        self.telethon_connected = True
                        self.update_otp_status(True)
        except Exception as e:
            logger.error(f"Lỗi khi đọc cấu hình: {str(e)}")
            logger.error(traceback.format_exc())
    
    def update_step_ui(self):
        """Cập nhật UI của wizard dựa trên bước hiện tại"""
        if self.current_step == 1:
            # Bước 1 - Telegram Bot API
            self.step1_label.setStyleSheet("""
                background-color: #3498DB;
                color: white;
                border-radius: 16px;
                font-size: 14px;
                font-weight: bold;
            """)
            self.step_text_label1.setStyleSheet("""
                color: #3498DB;
                font-size: 14px;
                font-weight: bold;
            """)
            
            self.step2_label.setStyleSheet("""
                background-color: #CBD5E1;
                color: white;
                border-radius: 16px;
                font-size: 14px;
                font-weight: bold;
            """)
            self.step_text_label2.setStyleSheet("""
                color: #64748B;
                font-size: 14px;
            """)
            
            # Chọn tab Bot API
            self.config_tab_widget.setCurrentIndex(0)
        else:
            # Bước 2 - Telethon API
            self.step1_label.setStyleSheet("""
                background-color: #2ECC71;
                color: white;
                border-radius: 16px;
                font-size: 14px;
                font-weight: bold;
            """)
            self.step_text_label1.setStyleSheet("""
                color: #2ECC71;
                font-size: 14px;
                font-weight: bold;
            """)
            
            self.step2_label.setStyleSheet("""
                background-color: #3498DB;
                color: white;
                border-radius: 16px;
                font-size: 14px;
                font-weight: bold;
            """)
            self.step_text_label2.setStyleSheet("""
                color: #3498DB;
                font-size: 14px;
                font-weight: bold;
            """)
            
            # Chọn tab Telethon API
            self.config_tab_widget.setCurrentIndex(1)
    
    def update_save_button_state(self):
        """Cập nhật trạng thái nút lưu dựa trên các trường dữ liệu"""
        if self.current_step == 1:
            # Bước 1 - Cần cả Bot Token và Chat ID đã được xác thực
            self.save_button.setEnabled(self.telegram_connected)
        else:
            # Bước 2 - Cần bước 1 đã hoàn thành và thông tin Telethon đã được nhập đầy đủ
            has_api_id = bool(self.api_id_line_edit.text().strip())
            has_api_hash = bool(self.api_hash_line_edit.text().strip())
            has_phone = bool(self.phone_line_edit.text().strip())
            
            # Nếu đã xác thực Telethon hoặc đã nhập đầy đủ thông tin
            self.save_button.setEnabled(
                self.telethon_connected or 
                (self.bot_tab_completed and has_api_id and has_api_hash and has_phone)
            )
    
    def update_otp_status(self, verified=False):
        """Cập nhật trạng thái xác thực OTP"""
        if verified:
            self.otp_status_label.setText("✓ Đã xác thực thành công!")
            self.otp_status_label.setStyleSheet("""
                background-color: #F0FFF4;
                color: #2ECC71;
                border: 1px solid #C6F6D5;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            """)
            self.get_otp_button.setEnabled(False)
            self.get_otp_button.setText("Đã xác thực")
            self.telethon_connected = True
        else:
            self.otp_status_label.setText("⚠ Chưa xác thực! Cần xác thực OTP")
            self.otp_status_label.setStyleSheet("""
                background-color: #FFF5F5;
                color: #E53E3E;
                border: 1px solid #FED7D7;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            """)
            self.get_otp_button.setEnabled(True)
            self.get_otp_button.setText("Lấy mã xác thực")
            self.telethon_connected = False
        
        self.update_save_button_state()
    
    def check_telegram_connection(self):
        """Kiểm tra kết nối với Telegram Bot API"""
        bot_token = self.token_line_edit.text().strip()
        chat_id = self.chat_id_line_edit.text().strip()
        
        if not bot_token:
            self.show_message_box("Lỗi", "Vui lòng nhập Bot Token", QtWidgets.QMessageBox.Icon.Warning)
            return
        
        if not chat_id:
            self.show_message_box("Lỗi", "Vui lòng nhập Chat ID", QtWidgets.QMessageBox.Icon.Warning)
            return
        
        # Thay đổi trạng thái UI
        self.btn_check_connection.setEnabled(False)
        self.btn_check_connection.setText("Đang kiểm tra...")
        QtCore.QCoreApplication.processEvents()
        
        try:
            # Import và sử dụng TelegramAPI
            from utils.telegram.telegram_api import TelegramAPI
            
            telegram_api = TelegramAPI()
            if telegram_api.connect(bot_token):
                # Kiểm tra kết nối chat
                bot_info = telegram_api.test_connection(chat_id, delete_after=60)
                
                if bot_info:
                    # Kết nối thành công
                    self.connection_status_label.setText(f"✓ Đã kết nối thành công! Kết nối tới bot @{bot_info.get('username', 'unknown')}")
                    self.connection_status_label.setStyleSheet("""
                        background-color: #F0FFF4;
                        color: #2ECC71;
                        border: 1px solid #C6F6D5;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: 13px;
                    """)
                    self.telegram_connected = True
                    self.bot_tab_completed = True
                    
                    # Cập nhật trạng thái nút lưu
                    self.update_save_button_state()
                    
                    # Sau khi kết nối thành công, tự động chuyển sang bước 2
                    QtCore.QTimer.singleShot(1000, self.go_to_step_2)
                else:
                    # Kết nối chat thất bại
                    self.connection_status_label.setText("✗ Không thể kết nối đến chat! Vui lòng kiểm tra Chat ID")
                    self.connection_status_label.setStyleSheet("""
                        background-color: #FFF5F5;
                        color: #E53E3E;
                        border: 1px solid #FED7D7;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: 13px;
                    """)
                    self.telegram_connected = False
            else:
                # Kết nối bot thất bại
                self.connection_status_label.setText("✗ Không thể kết nối với Bot! Vui lòng kiểm tra Bot Token")
                self.connection_status_label.setStyleSheet("""
                    background-color: #FFF5F5;
                    color: #E53E3E;
                    border: 1px solid #FED7D7;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 13px;
                """)
                self.telegram_connected = False
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra kết nối Telegram: {str(e)}")
            logger.error(traceback.format_exc())
            
            self.connection_status_label.setText(f"✗ Lỗi kết nối: {str(e)}")
            self.connection_status_label.setStyleSheet("""
                background-color: #FFF5F5;
                color: #E53E3E;
                border: 1px solid #FED7D7;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            """)
            self.telegram_connected = False
        
        # Khôi phục trạng thái UI
        self.btn_check_connection.setEnabled(True)
        self.btn_check_connection.setText("Kiểm tra kết nối")
        self.update_save_button_state()
    
    def go_to_step_2(self):
        """Chuyển sang bước 2 - Telethon API"""
        if self.current_step == 1 and self.telegram_connected:
            self.current_step = 2
            self.update_step_ui()
    
    def toggle_api_hash_visibility(self):
        """Hiển thị/ẩn API Hash"""
        if self.api_hash_line_edit.echoMode() == QtWidgets.QLineEdit.EchoMode.Password:
            self.api_hash_line_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            self.toggle_password_button.setText("🔒")
        else:
            self.api_hash_line_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.toggle_password_button.setText("👁️")
    
    def get_otp_verification(self):
        """Lấy mã xác thực OTP từ Telegram"""
        api_id = self.api_id_line_edit.text().strip()
        api_hash = self.api_hash_line_edit.text().strip()
        phone = self.phone_line_edit.text().strip()
        
        # Kiểm tra các trường dữ liệu
        if not api_id:
            self.show_message_box("Lỗi", "Vui lòng nhập API ID", QtWidgets.QMessageBox.Icon.Warning)
            return
        
        if not api_hash:
            self.show_message_box("Lỗi", "Vui lòng nhập API Hash", QtWidgets.QMessageBox.Icon.Warning)
            return
        
        if not phone:
            self.show_message_box("Lỗi", "Vui lòng nhập số điện thoại", QtWidgets.QMessageBox.Icon.Warning)
            return
        
        # Hiển thị modal OTP
        try:
            otp_modal = OTPModal(self, api_id=api_id, api_hash=api_hash, phone=phone)
            
            # Hiển thị modal
            result = otp_modal.exec()
            
            # Kiểm tra kết quả
            if result == QtWidgets.QDialog.DialogCode.Accepted:
                # Xác thực thành công
                self.update_otp_status(True)
            else:
                # Xác thực thất bại
                self.update_otp_status(False)
        except Exception as e:
            logger.error(f"Lỗi khi hiển thị modal OTP: {str(e)}")
            logger.error(traceback.format_exc())
            
            self.show_message_box(
                "Lỗi",
                f"Không thể hiển thị modal xác thực OTP: {str(e)}",
                QtWidgets.QMessageBox.Icon.Critical
            )
    
    def show_api_help(self):
        """Hiển thị hướng dẫn lấy API ID và Hash"""
        help_text = """
        <h3>Hướng dẫn lấy API ID và API Hash từ Telegram</h3>
        <ol>
            <li>Truy cập <a href="https://my.telegram.org">https://my.telegram.org</a> và đăng nhập.</li>
            <li>Nhấn vào "API development tools".</li>
            <li>Điền thông tin ứng dụng:
                <ul>
                    <li>App title: Telegram Video Uploader</li>
                    <li>Short name: TG_Video_Uploader</li>
                    <li>Platform: Desktop</li>
                    <li>Description: Ứng dụng tải video lên Telegram</li>
                </ul>
            </li>
            <li>Nhấn "Create Application".</li>
            <li>Sao chép API ID và API Hash vào các trường tương ứng.</li>
        </ol>
        <p>Lưu ý: API ID và API Hash là thông tin nhạy cảm, không nên chia sẻ với người khác.</p>
        """
        
        help_dialog = QtWidgets.QDialog(self)
        help_dialog.setWindowTitle("Hướng dẫn lấy API ID và Hash")
        help_dialog.setMinimumSize(500, 400)
        
        layout = QtWidgets.QVBoxLayout(help_dialog)
        
        text_browser = QtWidgets.QTextBrowser()
        text_browser.setHtml(help_text)
        text_browser.setOpenExternalLinks(True)
        
        close_button = QtWidgets.QPushButton("Đóng")
        close_button.clicked.connect(help_dialog.accept)
        
        layout.addWidget(text_browser)
        layout.addWidget(close_button, 0, Qt.AlignmentFlag.AlignHCenter)
        
        help_dialog.exec()
    
    def on_bot_api_input_changed(self):
        """Xử lý khi các trường dữ liệu Bot API thay đổi"""
        # Reset trạng thái kết nối
        if self.telegram_connected:
            self.telegram_connected = False
            self.update_save_button_state()
            
            # Cập nhật UI
            self.connection_status_label.setText("⚠ Thông tin đã thay đổi, vui lòng kiểm tra kết nối lại")
            self.connection_status_label.setStyleSheet("""
                background-color: #FFFBEB;
                color: #F59E0B;
                border: 1px solid #FEF3C7;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            """)
    
    def on_telethon_api_input_changed(self):
        """Xử lý khi các trường dữ liệu Telethon API thay đổi"""
        # Reset trạng thái xác thực OTP
        if self.telethon_connected:
            self.update_otp_status(False)
        
        self.update_save_button_state()
    
    def on_tab_changed(self, index):
        """Xử lý khi tab thay đổi"""
        self.current_step = index + 1
        self.update_step_ui()
        self.update_save_button_state()
    
    def save_as_draft(self):
        """Lưu cấu hình dưới dạng bản nháp"""
        # Hiển thị thông báo xác nhận
        reply = QtWidgets.QMessageBox.question(
            self,
            "Xác nhận lưu nháp",
            "Lưu nháp bạn sẽ phải cần xác thực lại khi thực hiện các chức năng sau này. Bạn có chắc muốn tiếp tục?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            # Lưu cấu hình
            self._save_config_to_file(as_draft=True)
            
            # Phát tín hiệu lưu thành công
            self.configSaved.emit(True)
            
            # Đóng dialog
            self.accept()
    
    def save_config(self):
        """Lưu cấu hình"""
        # Lưu cấu hình
        self._save_config_to_file()
        
        # Phát tín hiệu lưu thành công
        self.configSaved.emit(True)
        
        # Đóng dialog
        self.accept()
    
    def _save_config_to_file(self, as_draft=False):
        """
        Lưu cấu hình vào file
        
        Args:
            as_draft (bool): Lưu dưới dạng bản nháp
        """
        try:
            # Lấy đường dẫn đến file cấu hình
            app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(app_root, "config.ini")
            
            # Đọc cấu hình hiện tại
            config = configparser.ConfigParser()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config.read_file(f)
            
            # Đảm bảo các section tồn tại
            if 'TELEGRAM' not in config:
                config['TELEGRAM'] = {}
            if 'TELETHON' not in config:
                config['TELETHON'] = {}
            
            # Cập nhật cấu hình Bot API
            config['TELEGRAM']['bot_token'] = self.token_line_edit.text().strip()
            config['TELEGRAM']['chat_id'] = self.chat_id_line_edit.text().strip()
            config['TELEGRAM']['notification_chat_id'] = self.chat_id_line_edit.text().strip()
            
            # Cập nhật cấu hình Telethon API
            config['TELETHON']['api_id'] = self.api_id_line_edit.text().strip()
            config['TELETHON']['api_hash'] = self.api_hash_line_edit.text().strip()
            config['TELETHON']['phone'] = self.phone_line_edit.text().strip()
            
            # Cập nhật trạng thái xác thực OTP
            if as_draft:
                config['TELETHON']['otp_verified'] = 'false'
                config['TELETHON']['use_telethon'] = 'false'
            else:
                config['TELETHON']['otp_verified'] = 'true' if self.telethon_connected else 'false'
                config['TELETHON']['use_telethon'] = 'true' if self.telethon_connected else 'false'
            
            # Lưu cấu hình
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)
                
            logger.info("Đã lưu cấu hình Telegram thành công")
        except Exception as e:
            logger.error(f"Lỗi khi lưu cấu hình: {str(e)}")
            logger.error(traceback.format_exc())
            
            self.show_message_box(
                "Lỗi",
                f"Không thể lưu cấu hình: {str(e)}",
                QtWidgets.QMessageBox.Icon.Critical
            )
    
    def show_message_box(self, title, message, icon=QtWidgets.QMessageBox.Icon.Information):
        """Hiển thị hộp thoại thông báo"""
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg_box.exec()