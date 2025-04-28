"""
Module xử lý giao diện xác thực OTP của Telethon.
"""
import os
import sys
import time
import logging
import configparser
import traceback
from enum import Enum
from datetime import datetime, timedelta

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

logger = logging.getLogger(__name__)

class OTPState(Enum):
    """Trạng thái của modal OTP"""
    LOADING = 1
    VERIFICATION = 2
    EXPIRED = 3

class OTPModal(QtWidgets.QDialog):
    """
    Modal xác thực OTP của Telethon
    """
    # Tín hiệu khi OTP được xác thực
    otpVerified = pyqtSignal(bool)
    
    def __init__(self, parent=None, api_id=None, api_hash=None, phone=None, timeout=300):
        """
        Khởi tạo modal xác thực OTP
        
        Args:
            parent: Parent widget
            api_id (str): Telethon API ID
            api_hash (str): Telethon API Hash
            phone (str): Số điện thoại đã đăng ký với Telegram
            timeout (int): Thời gian timeout của OTP, tính bằng giây
        """
        super().__init__(parent)
        self.parent = parent
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.timeout = timeout
        
        # Client Telethon
        self.client = None
        
        # Thời gian hết hạn
        self.expire_time = None
        
        # Trạng thái hiện tại
        self.current_state = OTPState.LOADING
        
        # Số lần yêu cầu OTP
        self.otp_count = 0
        self.max_otp_count = 3
        
        # Lưu thời gian yêu cầu OTP gần nhất
        self.last_otp_request_time = None
        
        # Đường dẫn lưu số lần request OTP
        self.otp_count_file = self._get_otp_count_file()
        
        # Lấy số lần request OTP và thời gian request gần nhất
        self._load_otp_count()
        
        # Setup UI
        self._setup_ui()
        
        # Setup timer
        self._setup_timer()
        
        # Start OTP flow
        self._start_otp_flow()
    
    def _get_otp_count_file(self):
        """Lấy đường dẫn đến file lưu số lần request OTP"""
        # Lấy đường dẫn đến thư mục dữ liệu
        app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(app_root, "data")
        
        # Tạo thư mục data nếu chưa tồn tại
        os.makedirs(data_dir, exist_ok=True)
        
        # Đường dẫn đến file lưu số lần request OTP
        return os.path.join(data_dir, "otp_count.cfg")
    
    def _load_otp_count(self):
        """Lấy số lần request OTP và thời gian request gần nhất"""
        try:
            if os.path.exists(self.otp_count_file):
                config = configparser.ConfigParser()
                with open(self.otp_count_file, "r", encoding="utf-8") as f:
                    config.read_file(f)
                
                if "OTP" in config:
                    if "count" in config["OTP"]:
                        self.otp_count = int(config["OTP"]["count"])
                    
                    if "last_request_time" in config["OTP"]:
                        last_time_str = config["OTP"]["last_request_time"]
                        try:
                            self.last_otp_request_time = datetime.fromisoformat(last_time_str)
                            
                            # Nếu thời gian yêu cầu gần nhất đã quá 24h, reset số lần request
                            if datetime.now() - self.last_otp_request_time > timedelta(days=1):
                                self.otp_count = 0
                                self.last_otp_request_time = None
                        except ValueError:
                            self.last_otp_request_time = None
        except Exception as e:
            logger.error(f"Lỗi khi đọc file lưu số lần request OTP: {str(e)}")
            logger.error(traceback.format_exc())
    
    def _save_otp_count(self):
        """Lưu số lần request OTP và thời gian request gần nhất"""
        try:
            config = configparser.ConfigParser()
            config["OTP"] = {
                "count": str(self.otp_count),
                "last_request_time": self.last_otp_request_time.isoformat() if self.last_otp_request_time else ""
            }
            
            with open(self.otp_count_file, "w", encoding="utf-8") as f:
                config.write(f)
        except Exception as e:
            logger.error(f"Lỗi khi lưu file số lần request OTP: {str(e)}")
            logger.error(traceback.format_exc())
    
    def _setup_ui(self):
        """Thiết lập UI cho modal OTP"""
        self.setWindowTitle("Xác thực Telethon")
        self.setMinimumSize(500, 460)
        self.setMaximumSize(500, 460)
        self.setModal(True)
        
        # Layout chính
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Widget stacked chứa các trạng thái khác nhau
        self.stacked_widget = QtWidgets.QStackedWidget()
        
        # Tạo widgets cho các trạng thái
        self.loading_widget = self._create_loading_widget()
        self.verification_widget = self._create_verification_widget()
        self.expired_widget = self._create_expired_widget()
        
        # Thêm các widgets vào stacked widget
        self.stacked_widget.addWidget(self.loading_widget)
        self.stacked_widget.addWidget(self.verification_widget)
        self.stacked_widget.addWidget(self.expired_widget)
        
        # Thêm stacked widget vào layout chính
        self.main_layout.addWidget(self.stacked_widget)
        
        # Thiết lập stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                font-family: Arial;
            }
            
            QLabel.titleLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1E293B;
                background-color: transparent;
                font-family: Arial;
            }
            
            QLabel.messageLabel {
                font-size: 16px;
                font-weight: bold;
                color: #3498DB;
                font-family: Arial;
            }
            
            QLabel.errorMessageLabel {
                font-size: 16px;
                font-weight: bold;
                color: #E53E3E;
                font-family: Arial;
            }
            
            QLabel.infoLabel {
                font-size: 14px;
                color: #64748B;
                font-family: Arial;
            }
            
            QLineEdit {
                border: 1px solid #E4E7EB;
                border-radius: 6px;
                padding: 10px 15px;
                background-color: #FFFFFF;
                font-size: 16px;
                color: #1E293B;
                font-family: Arial;
                height: 50px;
            }
            
            QLineEdit.otpDigit {
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                background-color: #F9FAFB;
                font-size: 24px;
                font-weight: bold;
                color: #1E293B;
                text-align: center;
                font-family: Arial;
            }
            
            QLineEdit.errorOtpDigit {
                border: 1px solid #FC8181;
                border-radius: 6px;
                background-color: #FFF5F5;
                font-size: 24px;
                font-weight: bold;
                color: #E53E3E;
                text-align: center;
                font-family: Arial;
            }
            
            QPushButton.primaryButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 16px;
                font-weight: bold;
                font-family: Arial;
            }
            
            QPushButton.primaryButton:hover {
                background-color: #2980B9;
            }
            
            QPushButton.secondaryButton {
                background-color: #EBF5FB;
                color: #3498DB;
                border: 1px solid #BFDBFE;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 16px;
                font-family: Arial;
            }
            
            QPushButton.secondaryButton:hover {
                background-color: #D1E6FA;
            }
            
            QPushButton.disabledButton {
                background-color: #CBD5E1;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 16px;
                font-weight: bold;
                font-family: Arial;
            }
            
            QFrame.statusInfo {
                background-color: #EBF8FF;
                border: 1px solid #BEE3F8;
                border-radius: 4px;
                font-family: Arial;
            }
            
            QFrame.statusError {
                background-color: #FFF5F5;
                border: 1px solid #FED7D7;
                border-radius: 4px;
                font-family: Arial;
            }
            
            QLabel.timerLabel {
                background-color: transparent;
                color: #3498DB;
                font-weight: bold;
                font-size: 16px;
                font-family: Arial;
            }
            
            QLabel.errorTimerLabel {
                background-color: transparent;
                color: #E53E3E;
                font-weight: bold;
                font-size: 16px;
                font-family: Arial;
            }
            
            QProgressBar {
                border: none;
                background-color: #E2E8F0;
                height: 8px;
                border-radius: 4px;
            }
            
            QProgressBar::chunk {
                background-color: #3498DB;
                border-radius: 4px;
            }
        """)
        
        # Ban đầu hiển thị widget loading
        self.stacked_widget.setCurrentIndex(OTPState.LOADING.value - 1)
    
    def _create_loading_widget(self):
        """Tạo widget cho trạng thái đang tải"""
        widget = QtWidgets.QWidget()
        
        # Layout chính
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header_widget = QtWidgets.QWidget()
        header_widget.setMinimumHeight(60)
        header_widget.setMaximumHeight(60)
        header_widget.setStyleSheet("background-color: #F9FAFB;")
        
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        title_label = QtWidgets.QLabel("Xác thực Telethon")
        title_label.setProperty("class", "titleLabel")
        
        header_layout.addWidget(title_label)
        
        # Content
        content_widget = QtWidgets.QWidget()
        
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 20, 30, 20)
        content_layout.setSpacing(20)
        
        # Message layout
        message_layout = QtWidgets.QHBoxLayout()
        message_layout.setSpacing(15)
        
        loading_icon_label = QtWidgets.QLabel("⏳")
        loading_icon_label.setMinimumSize(30, 30)
        loading_icon_label.setMaximumSize(30, 30)
        loading_icon_label.setStyleSheet("""
            background-color: #3498DB;
            color: white;
            border-radius: 15px;
            font-size: 14px;
            font-weight: bold;
        """)
        loading_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        message_label = QtWidgets.QLabel("Đang gửi mã xác thực đến Telegram của bạn...")
        message_label.setProperty("class", "messageLabel")
        
        message_layout.addWidget(loading_icon_label)
        message_layout.addWidget(message_label)
        
        # Phone layout
        phone_layout = QtWidgets.QVBoxLayout()
        phone_layout.setSpacing(10)
        
        phone_label = QtWidgets.QLabel("Số điện thoại:")
        phone_label.setProperty("class", "infoLabel")
        
        self.loading_phone_line_edit = QtWidgets.QLineEdit()
        self.loading_phone_line_edit.setReadOnly(True)
        self.loading_phone_line_edit.setStyleSheet("background-color: #F9FAFB;")
        self.loading_phone_line_edit.setText(self.phone if self.phone else "")
        
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.loading_phone_line_edit)
        
        # Progress bar
        self.loading_progress_bar = QtWidgets.QProgressBar()
        self.loading_progress_bar.setMinimum(0)
        self.loading_progress_bar.setMaximum(0)  # Indeterminate
        self.loading_progress_bar.setValue(-1)
        self.loading_progress_bar.setTextVisible(False)
        
        # Instruction label
        instruction_label = QtWidgets.QLabel("Vui lòng đợi trong khi chúng tôi gửi mã xác thực đến tài khoản Telegram của bạn.")
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setWordWrap(True)
        instruction_label.setStyleSheet("font-size: 15px; color: #1E293B; margin-top: 10px;")
        
        # Note label
        note_label = QtWidgets.QLabel("Quá trình này thường mất vài giây. Sau khi nhận được mã OTP, vui lòng nhập vào màn hình tiếp theo để hoàn tất xác thực.")
        note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note_label.setWordWrap(True)
        note_label.setStyleSheet("font-size: 12px; color: #64748B;")
        
        # Spacer
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        
        # Thêm các thành phần vào content layout
        content_layout.addLayout(message_layout)
        content_layout.addLayout(phone_layout)
        content_layout.addWidget(self.loading_progress_bar)
        content_layout.addWidget(instruction_label)
        content_layout.addWidget(note_label)
        content_layout.addItem(spacer)
        
        # Footer
        footer_widget = QtWidgets.QWidget()
        footer_widget.setMinimumHeight(60)
        footer_widget.setMaximumHeight(60)
        footer_widget.setStyleSheet("background-color: #F9FAFB;")
        
        footer_layout = QtWidgets.QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(30, 10, 30, 10)
        
        # Nút hủy
        cancel_button = QtWidgets.QPushButton("Hủy")
        cancel_button.setMinimumSize(120, 0)
        cancel_button.setMaximumSize(120, 16777215)
        cancel_button.setProperty("class", "secondaryButton")
        
        # Nút xác thực (disabled)
        self.loading_verify_button = QtWidgets.QPushButton("Đang xử lý...")
        self.loading_verify_button.setMinimumSize(120, 0)
        self.loading_verify_button.setMaximumSize(120, 16777215)
        self.loading_verify_button.setEnabled(False)
        self.loading_verify_button.setProperty("class", "disabledButton")
        
        # Spacer
        footer_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        
        # Thêm các thành phần vào footer layout
        footer_layout.addWidget(cancel_button)
        footer_layout.addItem(footer_spacer)
        footer_layout.addWidget(self.loading_verify_button)
        
        # Kết nối các sự kiện
        cancel_button.clicked.connect(self.reject)
        
        # Thêm các widget vào layout chính
        layout.addWidget(header_widget)
        layout.addWidget(content_widget)
        layout.addWidget(footer_widget)
        
        return widget
    
    def _create_verification_widget(self):
        """Tạo widget cho trạng thái nhập mã OTP"""
        widget = QtWidgets.QWidget()
        
        # Layout chính
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header_widget = QtWidgets.QWidget()
        header_widget.setMinimumHeight(60)
        header_widget.setMaximumHeight(60)
        header_widget.setStyleSheet("background-color: #F9FAFB;")
        
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        title_label = QtWidgets.QLabel("Xác thực Telethon")
        title_label.setProperty("class", "titleLabel")
        
        header_layout.addWidget(title_label)
        
        # Content
        content_widget = QtWidgets.QWidget()
        
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 20, 30, 20)
        content_layout.setSpacing(20)
        
        # Message layout
        message_layout = QtWidgets.QHBoxLayout()
        message_layout.setSpacing(15)
        
        icon_label = QtWidgets.QLabel("✉")
        icon_label.setMinimumSize(40, 40)
        icon_label.setMaximumSize(40, 40)
        icon_label.setStyleSheet("""
            background-color: #3498DB;
            color: white;
            border-radius: 20px;
            font-size: 16px;
            font-weight: bold;
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        message_label = QtWidgets.QLabel("Mã OTP đã được gửi đến ứng dụng Telegram của bạn")
        message_label.setProperty("class", "messageLabel")
        
        message_layout.addWidget(icon_label)
        message_layout.addWidget(message_label)
        
        # Phone layout
        phone_layout = QtWidgets.QVBoxLayout()
        phone_layout.setSpacing(10)
        
        phone_label = QtWidgets.QLabel("Số điện thoại:")
        phone_label.setProperty("class", "infoLabel")
        
        self.verification_phone_line_edit = QtWidgets.QLineEdit()
        self.verification_phone_line_edit.setReadOnly(True)
        self.verification_phone_line_edit.setStyleSheet("background-color: #F9FAFB;")
        self.verification_phone_line_edit.setText(self.phone if self.phone else "")
        
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.verification_phone_line_edit)
        
        # OTP layout
        otp_layout = QtWidgets.QVBoxLayout()
        otp_layout.setSpacing(10)
        
        otp_label = QtWidgets.QLabel("Nhập mã xác thực (6 chữ số):")
        otp_label.setProperty("class", "infoLabel")
        
        otp_digits_layout = QtWidgets.QHBoxLayout()
        otp_digits_layout.setSpacing(10)
        
        # Các ô nhập OTP
        self.otp_digits = []
        for i in range(6):
            digit = QtWidgets.QLineEdit()
            digit.setMinimumSize(62, 62)
            digit.setMaximumSize(62, 62)
            digit.setProperty("class", "otpDigit")
            digit.setMaxLength(1)
            digit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            digit.textChanged.connect(lambda text, idx=i: self._on_otp_digit_changed(text, idx))
            otp_digits_layout.addWidget(digit)
            self.otp_digits.append(digit)
        
        # Timer frame
        self.timer_frame = QtWidgets.QFrame()
        self.timer_frame.setMinimumHeight(36)
        self.timer_frame.setMaximumHeight(36)
        self.timer_frame.setProperty("class", "statusInfo")
        
        timer_layout = QtWidgets.QHBoxLayout(self.timer_frame)
        timer_layout.setContentsMargins(10, 0, 10, 0)
        
        timer_icon_label = QtWidgets.QLabel("⏱")
        timer_icon_label.setMinimumSize(24, 24)
        timer_icon_label.setMaximumSize(24, 24)
        timer_icon_label.setStyleSheet("""
            background-color: #3498DB;
            color: white;
            border-radius: 12px;
            font-size: 14px;
            font-weight: bold;
        """)
        timer_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        timer_label = QtWidgets.QLabel("Mã có hiệu lực trong:")
        timer_label.setProperty("class", "timerLabel")
        
        timer_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        
        self.time_left_label = QtWidgets.QLabel("05:00")
        self.time_left_label.setProperty("class", "timerLabel")
        self.time_left_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
        
        timer_layout.addWidget(timer_icon_label)
        timer_layout.addWidget(timer_label)
        timer_layout.addItem(timer_spacer)
        timer_layout.addWidget(self.time_left_label)
        
        # Note label
        note_label = QtWidgets.QLabel("Mã xác thực có hiệu lực trong 5 phút. Nếu chưa nhận được mã, vui lòng kiểm tra Telegram hoặc lấy mã khác.")
        note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note_label.setWordWrap(True)
        note_label.setStyleSheet("font-size: 13px; color: #64748B;")
        
        # Spacer
        spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        
        # Thêm các thành phần vào content layout
        otp_layout.addWidget(otp_label)
        otp_layout.addLayout(otp_digits_layout)
        
        content_layout.addLayout(message_layout)
        content_layout.addLayout(phone_layout)
        content_layout.addLayout(otp_layout)
        content_layout.addWidget(self.timer_frame)
        content_layout.addWidget(note_label)
        content_layout.addItem(spacer)
        
        # Footer
        footer_widget = QtWidgets.QWidget()
        footer_widget.setMinimumHeight(70)
        footer_widget.setMaximumHeight(70)
        footer_widget.setStyleSheet("background-color: #F9FAFB;")
        
        footer_layout = QtWidgets.QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(30, 10, 30, 10)
        
        # Nút hủy
        cancel_button = QtWidgets.QPushButton("Hủy")
        cancel_button.setMinimumSize(120, 0)
        cancel_button.setMaximumSize(120, 16777215)
        cancel_button.setProperty("class", "secondaryButton")
        
        # Nút xác thực
        self.verify_button = QtWidgets.QPushButton("Xác thực")
        self.verify_button.setMinimumSize(120, 0)
        self.verify_button.setMaximumSize(120, 16777215)
        self.verify_button.setProperty("class", "primaryButton")
        self.verify_button.setEnabled(False)
        
        # Spacer
        footer_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        
        # Thêm các thành phần vào footer layout
        footer_layout.addWidget(cancel_button)
        footer_layout.addItem(footer_spacer)
        footer_layout.addWidget(self.verify_button)
        
        # Kết nối các sự kiện
        cancel_button.clicked.connect(self.reject)
        self.verify_button.clicked.connect(self._verify_otp)
        
        # Thêm các widget vào layout chính
        layout.addWidget(header_widget)
        layout.addWidget(content_widget)
        layout.addWidget(footer_widget)
        
        return widget
    
    def _create_expired_widget(self):
        """Tạo widget cho trạng thái OTP hết hạn"""
        widget = QtWidgets.QWidget()
        
        # Layout chính
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header_widget = QtWidgets.QWidget()
        header_widget.setMinimumHeight(60)
        header_widget.setMaximumHeight(60)
        header_widget.setStyleSheet("background-color: #F9FAFB;")
        
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        title_label = QtWidgets.QLabel("Xác thực Telethon")
        title_label.setProperty("class", "titleLabel")
        
        header_layout.addWidget(title_label)
        
        # Content
        content_widget = QtWidgets.QWidget()
        
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 20, 30, 20)
        content_layout.setSpacing(20)
        
        # Message layout
        message_layout = QtWidgets.QHBoxLayout()
        message_layout.setSpacing(15)
        
        icon_label = QtWidgets.QLabel("!")
        icon_label.setMinimumSize(40, 40)
        icon_label.setMaximumSize(40, 40)
        icon_label.setStyleSheet("""
            background-color: #E53E3E;
            color: white;
            border-radius: 20px;
            font-size: 16px;
            font-weight: bold;
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        message_label = QtWidgets.QLabel("Mã OTP đã hết hạn hoặc không hợp lệ")
        message_label.setProperty("class", "errorMessageLabel")
        
        message_layout.addWidget(icon_label)
        message_layout.addWidget(message_label)
        
        # Phone layout
        phone_layout = QtWidgets.QVBoxLayout()
        phone_layout.setSpacing(10)
        
        phone_label = QtWidgets.QLabel("Số điện thoại:")
        phone_label.setProperty("class", "infoLabel")
        
        self.expired_phone_line_edit = QtWidgets.QLineEdit()
        self.expired_phone_line_edit.setReadOnly(True)
        self.expired_phone_line_edit.setStyleSheet("background-color: #F9FAFB;")
        self.expired_phone_line_edit.setText(self.phone if self.phone else "")
        
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.expired_phone_line_edit)
        
        # OTP layout
        otp_layout = QtWidgets.QVBoxLayout()
        otp_layout.setSpacing(10)
        
        otp_label = QtWidgets.QLabel("Nhập mã xác thực (6 chữ số):")
        otp_label.setProperty("class", "infoLabel")
        
        otp_digits_layout = QtWidgets.QHBoxLayout()
        otp_digits_layout.setSpacing(10)
        
        # Các ô nhập OTP (không cho phép chỉnh sửa)
        self.expired_otp_digits = []
        for i in range(6):
            digit = QtWidgets.QLineEdit()
            digit.setMinimumSize(0, 0)
            digit.setMaximumSize(16777215, 16777215)
            digit.setProperty("class", "errorOtpDigit")
            digit.setReadOnly(True)
            digit.setMaxLength(1)
            digit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            otp_digits_layout.addWidget(digit)
            self.expired_otp_digits.append(digit)
        
        # Timer frame
        self.expired_timer_frame = QtWidgets.QFrame()
        self.expired_timer_frame.setMinimumHeight(36)
        self.expired_timer_frame.setMaximumHeight(36)
        self.expired_timer_frame.setProperty("class", "statusError")
        
        timer_layout = QtWidgets.QHBoxLayout(self.expired_timer_frame)
        timer_layout.setContentsMargins(10, 0, 10, 0)
        
        timer_icon_label = QtWidgets.QLabel("⏱")
        timer_icon_label.setMinimumSize(24, 24)
        timer_icon_label.setMaximumSize(24, 24)
        timer_icon_label.setStyleSheet("""
            background-color: #E53E3E;
            color: white;
            border-radius: 12px;
            font-size: 14px;
            font-weight: bold;
        """)
        timer_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        timer_label = QtWidgets.QLabel("Mã đã hết hạn")
        timer_label.setProperty("class", "errorTimerLabel")
        
        timer_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        
        time_left_label = QtWidgets.QLabel("00:00")
        time_left_label.setProperty("class", "errorTimerLabel")
        time_left_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
        
        timer_layout.addWidget(timer_icon_label)
        timer_layout.addWidget(timer_label)
        timer_layout.addItem(timer_spacer)
        timer_layout.addWidget(time_left_label)
        
        # Note label
        self.expired_note_label = QtWidgets.QLabel("Vui lòng nhấn \"Lấy lại mã\" để nhận mã xác thực mới")
        self.expired_note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.expired_note_label.setWordWrap(True)
        self.expired_note_label.setStyleSheet("font-size: 13px; color: #64748B;")
        
        # Spacer
        spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        
        # Thêm các thành phần vào content layout
        otp_layout.addWidget(otp_label)
        otp_layout.addLayout(otp_digits_layout)
        
        content_layout.addLayout(message_layout)
        content_layout.addLayout(phone_layout)
        content_layout.addLayout(otp_layout)
        content_layout.addWidget(self.expired_timer_frame)
        content_layout.addWidget(self.expired_note_label)
        content_layout.addItem(spacer)
        
        # Footer
        footer_widget = QtWidgets.QWidget()
        footer_widget.setMinimumHeight(70)
        footer_widget.setMaximumHeight(70)
        footer_widget.setStyleSheet("background-color: #F9FAFB;")
        
        footer_layout = QtWidgets.QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(30, 10, 30, 10)
        
        # Nút hủy
        cancel_button = QtWidgets.QPushButton("Hủy")
        cancel_button.setMinimumSize(120, 0)
        cancel_button.setMaximumSize(120, 16777215)
        cancel_button.setProperty("class", "secondaryButton")
        
        # Nút lấy lại mã
        self.get_new_code_button = QtWidgets.QPushButton("Lấy lại mã")
        self.get_new_code_button.setMinimumSize(120, 0)
        self.get_new_code_button.setMaximumSize(120, 16777215)
        self.get_new_code_button.setProperty("class", "primaryButton")
        
        # Spacer
        footer_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        
        # Thêm các thành phần vào footer layout
        footer_layout.addWidget(cancel_button)
        footer_layout.addItem(footer_spacer)
        footer_layout.addWidget(self.get_new_code_button)
        
        # Kết nối các sự kiện
        cancel_button.clicked.connect(self.reject)
        self.get_new_code_button.clicked.connect(self._get_new_otp)
        
        # Thêm các widget vào layout chính
        layout.addWidget(header_widget)
        layout.addWidget(content_widget)
        layout.addWidget(footer_widget)
        
        return widget
    
    def _setup_timer(self):
        """Thiết lập timer cho việc đếm thời gian hết hạn"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer)
        self.timer.setInterval(1000)  # Cập nhật mỗi giây
    
    def _start_timer(self):
        """Bắt đầu đếm thời gian hết hạn"""
        # Thiết lập thời gian hết hạn
        self.expire_time = datetime.now() + timedelta(seconds=self.timeout)
        
        # Cập nhật timer
        self._update_timer()
        
        # Bắt đầu timer
        self.timer.start()
    
    def _update_timer(self):
        """Cập nhật hiển thị thời gian hết hạn"""
        if self.expire_time is None:
            return
        
        now = datetime.now()
        time_left = self.expire_time - now
        
        if time_left.total_seconds() <= 0:
            # OTP đã hết hạn
            self.timer.stop()
            self._on_otp_expired()
            return
        
        # Tính toán phút và giây còn lại
        minutes = int(time_left.total_seconds() // 60)
        seconds = int(time_left.total_seconds() % 60)
        
        # Cập nhật label hiển thị thời gian
        self.time_left_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def _start_otp_flow(self):
        """Bắt đầu quy trình xác thực OTP"""
        # Kiểm tra số lần yêu cầu OTP trong ngày
        if self.otp_count >= self.max_otp_count:
            # Nếu đã yêu cầu quá 3 lần trong 24h, hiển thị thông báo
            self._show_otp_limit_message()
            return
        
        # Tạo client Telethon và yêu cầu OTP
        try:
            from telethon import TelegramClient
            import telethon.errors as telethon_errors
            
            # Flag để theo dõi trạng thái yêu cầu OTP
            self.is_requesting_otp = True
            
            # Tạo client Telethon trong một thread riêng
            self.thread = QtCore.QThread()
            self.worker = OTPWorker(self.api_id, self.api_hash, self.phone)
            self.worker.moveToThread(self.thread)
            
            # Kết nối các tín hiệu
            self.thread.started.connect(self.worker.request_otp)
            self.worker.error.connect(self._on_otp_error)
            self.worker.otp_sent.connect(self._on_otp_sent)
            self.worker.verification_done.connect(self._on_verification_done)
            
            # Bắt đầu thread
            self.thread.start()
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo client Telethon: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Hiển thị thông báo lỗi
            self._show_message_box(
                "Lỗi",
                f"Không thể khởi tạo client Telethon: {str(e)}",
                QtWidgets.QMessageBox.Icon.Critical
            )
            
            # Đóng dialog
            self.reject()
    
    def _show_otp_limit_message(self):
        """Hiển thị thông báo đã yêu cầu OTP quá giới hạn"""
        # Chuyển sang widget OTP hết hạn
        self.stacked_widget.setCurrentIndex(OTPState.EXPIRED.value - 1)
        
        # Cập nhật trạng thái
        self.current_state = OTPState.EXPIRED
        
        # Cập nhật nút và nhãn
        self.get_new_code_button.setText("Đã quá giới hạn")
        self.get_new_code_button.setEnabled(False)
        self.get_new_code_button.setProperty("class", "disabledButton")
        self.get_new_code_button.setStyleSheet("""
            background-color: #CBD5E1;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 15px;
            font-size: 16px;
            font-weight: bold;
            font-family: Arial;
        """)
        
        # Tính thời gian còn lại đến lần reset tiếp theo
        if self.last_otp_request_time:
            next_reset_time = self.last_otp_request_time + timedelta(days=1)
            time_left = next_reset_time - datetime.now()
            
            hours = int(time_left.total_seconds() // 3600)
            minutes = int((time_left.total_seconds() % 3600) // 60)
            
            reset_msg = f"Bạn đã thực hiện quá {self.max_otp_count} lần trong 24h. Vui lòng thử lại sau {hours} giờ {minutes} phút."
        else:
            reset_msg = f"Bạn đã thực hiện quá {self.max_otp_count} lần trong 24h. Vui lòng thử lại sau 24 giờ."
        
        self.expired_note_label.setText(reset_msg)
    
    def _on_otp_sent(self, phone_code_hash, otp_timeout):
        """Xử lý khi OTP đã được gửi"""
        # Lưu phone_code_hash để sử dụng khi xác thực
        self.phone_code_hash = phone_code_hash
        
        # Cập nhật timeout nếu server trả về giá trị khác
        if otp_timeout and otp_timeout > 0:
            self.timeout = otp_timeout
        
        # Cập nhật số lần yêu cầu OTP
        self.otp_count += 1
        self.last_otp_request_time = datetime.now()
        self._save_otp_count()
        
        # Chuyển sang widget nhập OTP
        self.stacked_widget.setCurrentIndex(OTPState.VERIFICATION.value - 1)
        
        # Cập nhật trạng thái
        self.current_state = OTPState.VERIFICATION
        
        # Focus vào ô nhập OTP đầu tiên
        if self.otp_digits and len(self.otp_digits) > 0:
            self.otp_digits[0].setFocus()
        
        # Bắt đầu đếm thời gian
        self._start_timer()
    
    def _on_otp_error(self, error_message):
        """Xử lý khi có lỗi trong quá trình yêu cầu OTP"""
        logger.error(f"Lỗi khi yêu cầu OTP: {error_message}")
        
        # Hiển thị thông báo lỗi
        self._show_message_box(
            "Lỗi",
            f"Không thể gửi mã xác thực: {error_message}",
            QtWidgets.QMessageBox.Icon.Critical
        )
        
        # Đóng dialog
        self.reject()
    
    def _on_verification_done(self, success, error_message=None):
        """Xử lý khi xác thực OTP hoàn tất"""
        if success:
            # Phát tín hiệu xác thực thành công
            self.otpVerified.emit(True)
            
            # Hiển thị thông báo thành công
            self._show_message_box(
                "Thành công",
                "Xác thực Telethon API thành công!",
                QtWidgets.QMessageBox.Icon.Information
            )
            
            # Đóng dialog với kết quả thành công
            self.accept()
        else:
            # Hiển thị thông báo lỗi
            self._show_message_box(
                "Lỗi",
                f"Xác thực thất bại: {error_message}",
                QtWidgets.QMessageBox.Icon.Critical
            )
            
            # Đánh dấu OTP hết hạn hoặc không hợp lệ
            self._on_otp_expired()
    
    def _on_otp_digit_changed(self, text, index):
        """Xử lý khi người dùng nhập các chữ số OTP"""
        # Chỉ cho phép nhập số
        if text and not text.isdigit():
            self.otp_digits[index].setText("")
            return
        
        # Chuyển focus sang ô tiếp theo nếu có nhập giá trị
        if text and index < len(self.otp_digits) - 1:
            self.otp_digits[index + 1].setFocus()
        
        # Kiểm tra nếu đã nhập đủ 6 số
        self._check_otp_complete()
    
    def _check_otp_complete(self):
        """Kiểm tra xem người dùng đã nhập đủ 6 chữ số OTP chưa"""
        otp_complete = True
        for digit in self.otp_digits:
            if not digit.text():
                otp_complete = False
                break
        
        # Enable/disable nút xác thực
        self.verify_button.setEnabled(otp_complete)
    
    def _verify_otp(self):
        """Xác thực mã OTP"""
        # Lấy mã OTP từ các ô nhập
        otp_code = ""
        for digit in self.otp_digits:
            otp_code += digit.text()
        
        # Kiểm tra độ dài
        if len(otp_code) != 6:
            self._show_message_box(
                "Lỗi",
                "Vui lòng nhập đủ 6 chữ số OTP",
                QtWidgets.QMessageBox.Icon.Warning
            )
            return
        
        # Thiết lập UI đang xác thực
        self.verify_button.setEnabled(False)
        self.verify_button.setText("Đang xác thực...")
        
        # Yêu cầu worker xác thực OTP
        self.worker.verify_otp(otp_code, self.phone_code_hash)
    
    def _on_otp_expired(self):
        """Xử lý khi OTP hết hạn"""
        # Chuyển sang widget OTP hết hạn
        self.stacked_widget.setCurrentIndex(OTPState.EXPIRED.value - 1)
        
        # Cập nhật trạng thái
        self.current_state = OTPState.EXPIRED
        
        # Sao chép OTP đã nhập sang widget hết hạn
        otp = "".join([digit.text() for digit in self.otp_digits])
        for i, digit in enumerate(otp):
            if i < len(self.expired_otp_digits):
                self.expired_otp_digits[i].setText(digit)
        
        # Disable nút lấy lại mã nếu đã yêu cầu quá số lần cho phép
        if self.otp_count >= self.max_otp_count:
            self._show_otp_limit_message()
    
    def _get_new_otp(self):
        """Lấy mã OTP mới"""
        # Kiểm tra số lần yêu cầu OTP trong ngày
        if self.otp_count >= self.max_otp_count:
            # Nếu đã yêu cầu quá 3 lần trong 24h, hiển thị thông báo
            self._show_otp_limit_message()
            return
        
        # Chuyển về màn hình loading
        self.stacked_widget.setCurrentIndex(OTPState.LOADING.value - 1)
        
        # Cập nhật trạng thái
        self.current_state = OTPState.LOADING
        
        # Yêu cầu OTP mới
        try:
            # Thử kết nối lại với Telethon và yêu cầu OTP mới
            if hasattr(self, 'worker') and self.worker:
                self.worker.request_otp()
            else:
                # Nếu chưa có worker, khởi tạo lại quy trình OTP
                self._start_otp_flow()
        except Exception as e:
            logger.error(f"Lỗi khi yêu cầu OTP mới: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Hiển thị thông báo lỗi
            self._show_message_box(
                "Lỗi",
                f"Không thể yêu cầu mã xác thực mới: {str(e)}",
                QtWidgets.QMessageBox.Icon.Critical
            )
            
            # Đóng dialog
            self.reject()
    
    def _show_message_box(self, title, message, icon=QtWidgets.QMessageBox.Icon.Information):
        """Hiển thị hộp thoại thông báo"""
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg_box.exec()
    
    def closeEvent(self, event):
        """Xử lý khi người dùng đóng dialog"""
        # Dừng timer nếu đang chạy
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        
        # Dừng thread nếu đang chạy
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait(3000)  # Đợi tối đa 3 giây
        
        # Chấp nhận sự kiện đóng
        event.accept()
    
    def reject(self):
        """Xử lý khi người dùng hủy dialog"""
        # Dừng timer nếu đang chạy
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        
        # Dừng thread nếu đang chạy
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait(3000)  # Đợi tối đa 3 giây
        
        # Phát tín hiệu xác thực thất bại
        self.otpVerified.emit(False)
        
        # Đóng dialog
        super().reject()


class OTPWorker(QtCore.QObject):
    """
    Worker thread để xử lý các tác vụ Telethon
    """
    # Tín hiệu khi OTP được gửi
    otp_sent = pyqtSignal(str, int)
    # Tín hiệu khi có lỗi
    error = pyqtSignal(str)
    # Tín hiệu khi xác thực hoàn tất
    verification_done = pyqtSignal(bool, str)
    
    def __init__(self, api_id, api_hash, phone):
        """
        Khởi tạo worker
        
        Args:
            api_id (str): Telethon API ID
            api_hash (str): Telethon API Hash
            phone (str): Số điện thoại đã đăng ký với Telegram
        """
        super().__init__()
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        
        # Flag để dừng thread
        self.running = True
        
        # Client Telethon
        self.client = None
    
    def stop(self):
        """Dừng worker"""
        self.running = False
        
        # Đóng client nếu đang kết nối
        if self.client is not None:
            try:
                self.client.disconnect()
            except:
                pass
    
    def request_otp(self):
        """Yêu cầu mã OTP"""
        if not self.running:
            return
        
        try:
            from telethon import TelegramClient
            import telethon.errors as telethon_errors
            
            # Khởi tạo client
            self.client = TelegramClient(
                None,  # Không lưu session
                int(self.api_id),
                self.api_hash
            )
            
            # Kết nối đến Telegram
            self.client.connect()
            
            # Yêu cầu mã xác thực
            if not self.running:
                return
                
            try:
                # Yêu cầu mã OTP
                result = self.client.send_code_request(self.phone)
                
                # Lấy phone_code_hash và timeout
                phone_code_hash = result.phone_code_hash
                otp_timeout = result.timeout
                
                # Phát tín hiệu OTP đã được gửi
                self.otp_sent.emit(phone_code_hash, otp_timeout)
            except telethon_errors.PhoneNumberBannedError:
                self.error.emit("Số điện thoại đã bị cấm bởi Telegram")
            except telethon_errors.PhoneNumberInvalidError:
                self.error.emit("Số điện thoại không hợp lệ")
            except telethon_errors.FloodWaitError as e:
                self.error.emit(f"Vui lòng đợi {e.seconds} giây trước khi thử lại")
            except Exception as e:
                self.error.emit(str(e))
        except ImportError:
            self.error.emit("Thư viện Telethon chưa được cài đặt")
        except Exception as e:
            self.error.emit(str(e))
    
    def verify_otp(self, otp_code, phone_code_hash):
        """
        Xác thực mã OTP
        
        Args:
            otp_code (str): Mã OTP
            phone_code_hash (str): Hash code từ yêu cầu OTP
        """
        if not self.running or self.client is None:
            return
        
        try:
            from telethon import TelegramClient
            import telethon.errors as telethon_errors
            
            # Xác thực mã OTP
            try:
                # Đăng nhập với mã OTP
                self.client.sign_in(
                    self.phone,
                    otp_code,
                    phone_code_hash=phone_code_hash
                )
                
                # Kiểm tra xem đã đăng nhập thành công hay chưa
                me = self.client.get_me()
                
                if me:
                    # Đăng nhập thành công
                    self.verification_done.emit(True, "")
                else:
                    # Đăng nhập thất bại
                    self.verification_done.emit(False, "Không thể xác thực tài khoản")
            except telethon_errors.PhoneCodeInvalidError:
                self.verification_done.emit(False, "Mã xác thực không hợp lệ")
            except telethon_errors.PhoneCodeExpiredError:
                self.verification_done.emit(False, "Mã xác thực đã hết hạn")
            except telethon_errors.SessionPasswordNeededError:
                self.verification_done.emit(True, "")  # Two-factor auth enabled but we consider it verified
            except telethon_errors.FloodWaitError as e:
                self.verification_done.emit(False, f"Vui lòng đợi {e.seconds} giây trước khi thử lại")
            except Exception as e:
                self.verification_done.emit(False, str(e))
        except Exception as e:
            self.verification_done.emit(False, str(e))