"""
Module for the initial configuration modal that appears when no Telegram configuration exists.
"""
import os
import sys
import logging
import json
import time
import configparser
from datetime import datetime, timedelta
from pathlib import Path

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal

# Import các module cần thiết
try:
    from ..utils.ffmpeg_manager import FFmpegManager
except ImportError:
    from utils.ffmpeg_manager import FFmpegManager

logger = logging.getLogger("ConfigModal")

class ConfigTab(QtWidgets.QWidget):
    """
    Tab cấu hình cơ bản cho modal
    """
    connectionChecked = pyqtSignal(bool, str)
    
    def __init__(self, parent=None):
        super(ConfigTab, self).__init__(parent)
    
    def check_connection(self):
        """
        Hàm ảo để kiểm tra kết nối, được ghi đè bởi các tab con
        """
        pass

class TelegramBotTab(ConfigTab):
    """
    Tab cấu hình Telegram Bot API
    """
    def __init__(self, parent=None):
        super(TelegramBotTab, self).__init__(parent)
        
        # Thiết lập giao diện
        layout = QtWidgets.QVBoxLayout(self)
        
        # Trường nhập Bot Token
        token_group = QtWidgets.QGroupBox("Token Telegram Bot")
        token_layout = QtWidgets.QVBoxLayout()
        token_label = QtWidgets.QLabel("Token Bot - (Tìm trong @BotFather)")
        self.token_input = QtWidgets.QLineEdit()
        self.token_input.setPlaceholderText("Nhập token bot (vd: 1234567890:ABCDEF...")
        
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_input)
        token_group.setLayout(token_layout)
        
        # Trường nhập Chat ID
        chat_group = QtWidgets.QGroupBox("Chat ID")
        chat_layout = QtWidgets.QVBoxLayout()
        chat_label = QtWidgets.QLabel("Chat ID - (Có định dạng: -100xxxxxxxxxx)")
        self.chat_id_input = QtWidgets.QLineEdit()
        self.chat_id_input.setPlaceholderText("Nhập chat ID (vd: -1001234567890)")
        
        chat_layout.addWidget(chat_label)
        chat_layout.addWidget(self.chat_id_input)
        chat_group.setLayout(chat_layout)
        
        # Nút kiểm tra kết nối
        self.check_button = QtWidgets.QPushButton("Kiểm tra kết nối")
        self.check_button.clicked.connect(self.check_connection)
        
        # Kết quả kiểm tra
        self.result_label = QtWidgets.QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        
        # Thêm các widget vào layout chính
        layout.addWidget(token_group)
        layout.addWidget(chat_group)
        layout.addWidget(self.check_button)
        layout.addWidget(self.result_label)
        layout.addStretch()
        
        # Biến lưu trạng thái kết nối
        self.is_connected = False
    
    def check_connection(self):
        """
        Kiểm tra kết nối đến Telegram Bot API
        """
        # Lấy thông tin từ các trường nhập
        token = self.token_input.text().strip()
        chat_id = self.chat_id_input.text().strip()
        
        if not token or not chat_id:
            self.result_label.setText("Vui lòng nhập đầy đủ token và chat ID")
            self.result_label.setStyleSheet("color: red;")
            self.connectionChecked.emit(False, "Vui lòng nhập đầy đủ token và chat ID")
            return
        
        # Thay đổi trạng thái nút
        self.check_button.setEnabled(False)
        self.check_button.setText("Đang kiểm tra...")
        
        # Tạo tiến trình riêng để kiểm tra
        self.check_thread = CheckTelegramBotThread(token, chat_id)
        self.check_thread.resultReady.connect(self.on_check_complete)
        self.check_thread.start()
    
    def on_check_complete(self, success, message):
        """
        Xử lý kết quả kiểm tra kết nối
        
        Args:
            success (bool): Kết nối thành công hay không
            message (str): Thông báo kết quả
        """
        # Cập nhật giao diện
        self.check_button.setEnabled(True)
        self.check_button.setText("Kiểm tra kết nối")
        
        if success:
            self.result_label.setText("Kết nối thành công!")
            self.result_label.setStyleSheet("color: green; font-weight: bold;")
            self.is_connected = True
        else:
            self.result_label.setText(f"Lỗi: {message}")
            self.result_label.setStyleSheet("color: red;")
            self.is_connected = False
        
        # Phát tín hiệu kết quả
        self.connectionChecked.emit(success, message)
    
    def get_config(self):
        """
        Lấy thông tin cấu hình hiện tại
        
        Returns:
            dict: Thông tin cấu hình
        """
        return {
            "bot_token": self.token_input.text().strip(),
            "chat_id": self.chat_id_input.text().strip()
        }

class TelethonTab(ConfigTab):
    """
    Tab cấu hình Telethon API
    """
    otpRequested = pyqtSignal(str, str, str)  # api_id, api_hash, phone
    
    def __init__(self, parent=None):
        super(TelethonTab, self).__init__(parent)
        
        # Thiết lập giao diện
        layout = QtWidgets.QVBoxLayout(self)
        
        # Trường nhập API ID
        api_id_group = QtWidgets.QGroupBox("API ID")
        api_id_layout = QtWidgets.QVBoxLayout(api_id_group)
        api_id_label = QtWidgets.QLabel("API ID - (Có định dạng: 2xxxxxx)")
        self.api_id_input = QtWidgets.QLineEdit()
        self.api_id_input.setPlaceholderText("Nhập API ID (vd: 1234567)")
        
        api_id_layout.addWidget(api_id_label)
        api_id_layout.addWidget(self.api_id_input)
        api_id_group.setLayout(api_id_layout)
        
        # Trường nhập API Hash
        api_hash_group = QtWidgets.QGroupBox("API Hash")
        api_hash_layout = QtWidgets.QVBoxLayout(api_hash_group)
        api_hash_label = QtWidgets.QLabel("API Hash - (Có định dạng: 7xxxxe)")
        self.api_hash_input = QtWidgets.QLineEdit()
        self.api_hash_input.setPlaceholderText("Nhập API Hash")
        
        api_hash_layout.addWidget(api_hash_label)
        api_hash_layout.addWidget(self.api_hash_input)
        api_hash_group.setLayout(api_hash_layout)
        
        # Trường nhập số điện thoại
        phone_group = QtWidgets.QGroupBox("Số điện thoại")
        phone_layout = QtWidgets.QVBoxLayout(phone_group)
        phone_label = QtWidgets.QLabel("Số điện thoại - (Có định dạng: +84123456789)")
        self.phone_input = QtWidgets.QLineEdit()
        self.phone_input.setPlaceholderText("Nhập số điện thoại (vd: +84123456789)")
        
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)
        phone_group.setLayout(phone_layout)
        
        # Nút lấy mã OTP
        self.otp_button = QtWidgets.QPushButton("Lấy mã xác thực")
        self.otp_button.clicked.connect(self.request_otp)
        
        # Kết quả kiểm tra
        self.result_label = QtWidgets.QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        
        # Link hướng dẫn
        help_label = QtWidgets.QLabel("<a href='https://my.telegram.org/apps'>Làm thế nào để lấy API ID và Hash?</a>")
        help_label.setOpenExternalLinks(True)
        help_label.setAlignment(Qt.AlignCenter)
        
        # Thêm các widget vào layout chính
        layout.addWidget(api_id_group)
        layout.addWidget(api_hash_group)
        layout.addWidget(phone_group)
        layout.addWidget(self.otp_button)
        layout.addWidget(self.result_label)
        layout.addWidget(help_label)
        layout.addStretch()
        
        # Biến lưu trạng thái kết nối
        self.is_connected = False
    
    def request_otp(self):
        """
        Gửi yêu cầu lấy mã OTP
        """
        # Lấy thông tin từ các trường nhập
        api_id = self.api_id_input.text().strip()
        api_hash = self.api_hash_input.text().strip()
        phone = self.phone_input.text().strip()
        
        if not api_id or not api_hash or not phone:
            self.result_label.setText("Vui lòng nhập đầy đủ API ID, API Hash và số điện thoại")
            self.result_label.setStyleSheet("color: red;")
            return
        
        # Kiểm tra định dạng API ID
        try:
            api_id = int(api_id)
        except ValueError:
            self.result_label.setText("API ID phải là số nguyên")
            self.result_label.setStyleSheet("color: red;")
            return
        
        # Phát tín hiệu yêu cầu OTP
        self.otpRequested.emit(str(api_id), api_hash, phone)
    
    def check_connection(self):
        """
        Kiểm tra kết nối Telethon API
        """
        # Sẽ được xử lý qua tiến trình OTP
        pass
    
    def get_config(self):
        """
        Lấy thông tin cấu hình hiện tại
        
        Returns:
            dict: Thông tin cấu hình
        """
        return {
            "api_id": self.api_id_input.text().strip(),
            "api_hash": self.api_hash_input.text().strip(),
            "phone": self.phone_input.text().strip()
        }

class ConfigModal(QtWidgets.QDialog):
    """
    Modal đầu tiên để cấu hình Telegram Bot và Telethon
    """
    configSaved = pyqtSignal(bool)  # Phát tín hiệu khi cấu hình đã được lưu
    
    def __init__(self, parent=None, app=None):
        # Thay đổi cờ window để loại bỏ nút đóng
        super(ConfigModal, self).__init__(parent, Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # Loại bỏ khả năng đóng bằng Alt+F4
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.app = app
        self.setWindowTitle("Cấu hình Telegram")
        
        # Đường dẫn file UI
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file = os.path.join(current_dir, "qt_designer", "config_modal.ui")
        
        # Nếu không tìm thấy file UI, sử dụng đường dẫn khác
        if not os.path.exists(ui_file):
            ui_file = os.path.join(current_dir, "..", "ui", "qt_designer", "config_modal.ui")
        
        # Nếu vẫn không tìm thấy, tạo giao diện trực tiếp
        if not os.path.exists(ui_file):
            self.setup_ui_manually()
        else:
            uic.loadUi(ui_file, self)
            
            # Thiết lập các kết nối
            self.btnCheckTelegram = self.findChild(QtWidgets.QPushButton, "btnCheckTelegram")
            self.btnCheckTelethon = self.findChild(QtWidgets.QPushButton, "btnCheckTelethon")
            self.btnSaveDraft = self.findChild(QtWidgets.QPushButton, "btnSaveDraft")
            self.btnSave = self.findChild(QtWidgets.QPushButton, "btnSave")
            
            # Kết nối các sự kiện
            if self.btnCheckTelegram:
                self.btnCheckTelegram.clicked.connect(self.check_telegram_connection)
            
            if self.btnCheckTelethon:
                self.btnCheckTelethon.clicked.connect(self.request_telethon_code)
            
            if self.btnSaveDraft:
                self.btnSaveDraft.clicked.connect(self.save_draft)
            
            if self.btnSave:
                self.btnSave.clicked.connect(self.save_config)
                self.btnSave.setEnabled(False)
        
        # Biến trạng thái
        self.telegram_connected = False
        self.telethon_connected = False
        
        # Đặt kích thước và vị trí
        self.resize(600, 500)
        self.center_on_screen()
        
        # Tải cấu hình hiện có
        self.load_existing_config()
        
        # Cập nhật trạng thái UI
        self.update_ui_state()
        
        self.finished.connect(self.on_finish)
    
    def center_on_screen(self):
        """Đặt cửa sổ vào giữa màn hình"""
        screen = QtWidgets.QApplication.desktop().availableGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)
    
    def setup_ui_manually(self):
        """Thiết lập UI theo cách thủ công nếu không tìm thấy file UI"""
        # Thiết lập layout chính
        layout = QtWidgets.QVBoxLayout(self)
        
        # Tạo widget tab
        self.tabWidget = QtWidgets.QTabWidget()
        
        # Tab Telegram Bot API
        telegram_tab = QtWidgets.QWidget()
        telegram_layout = QtWidgets.QVBoxLayout(telegram_tab)
        
        # Nhóm Token
        token_group = QtWidgets.QGroupBox("Token Telegram Bot")
        token_layout = QtWidgets.QVBoxLayout(token_group)
        token_label = QtWidgets.QLabel("Token Bot - (Tìm trong @BotFather)")
        self.txtTelegramToken = QtWidgets.QLineEdit()
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.txtTelegramToken)
        
        # Nhóm Chat ID
        chat_group = QtWidgets.QGroupBox("Chat ID")
        chat_layout = QtWidgets.QVBoxLayout(chat_group)
        chat_label = QtWidgets.QLabel("Chat ID - (Có định dạng: -100xxxxxxxxxx)")
        self.txtChatId = QtWidgets.QLineEdit()
        chat_layout.addWidget(chat_label)
        layout.addWidget(self.txtChatId)
        
        # Nút kiểm tra kết nối Telegram
        self.btnCheckTelegram = QtWidgets.QPushButton("Kiểm tra kết nối")
        self.btnCheckTelegram.clicked.connect(self.check_telegram_connection)
        
        # Thêm các widget vào layout tab Telegram
        telegram_layout.addWidget(token_group)
        telegram_layout.addWidget(chat_group)
        telegram_layout.addWidget(self.btnCheckTelegram)
        telegram_layout.addStretch()
        
        # Tab Telethon API
        telethon_tab = QtWidgets.QWidget()
        telethon_layout = QtWidgets.QVBoxLayout(telethon_tab)
        
        # Nhóm API ID
        api_id_group = QtWidgets.QGroupBox("API ID")
        api_id_layout = QtWidgets.QVBoxLayout(api_id_group)
        api_id_label = QtWidgets.QLabel("API ID - (Có định dạng: 2xxxxxx)")
        self.txtApiId = QtWidgets.QLineEdit()
        api_id_layout.addWidget(api_id_label)
        api_id_layout.addWidget(self.txtApiId)
        
        # Nhóm API Hash
        api_hash_group = QtWidgets.QGroupBox("API Hash")
        api_hash_layout = QtWidgets.QVBoxLayout(api_hash_group)
        api_hash_label = QtWidgets.QLabel("API Hash - (Có định dạng: 7xxxxe)")
        self.txtApiHash = QtWidgets.QLineEdit()
        api_hash_layout.addWidget(api_hash_label)
        api_hash_layout.addWidget(self.txtApiHash)
        
        # Nhóm Phone
        phone_group = QtWidgets.QGroupBox("Số điện thoại")
        phone_layout = QtWidgets.QVBoxLayout(phone_group)
        phone_label = QtWidgets.QLabel("Số điện thoại - (Có định dạng: +84123456789)")
        self.txtPhone = QtWidgets.QLineEdit()
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.txtPhone)
        
        # Nút lấy mã xác thực Telethon
        self.btnCheckTelethon = QtWidgets.QPushButton("Lấy mã xác thực")
        self.btnCheckTelethon.clicked.connect(self.request_telethon_code)
        
        # Thêm các widget vào layout tab Telethon
        telethon_layout.addWidget(api_id_group)
        telethon_layout.addWidget(api_hash_group)
        telethon_layout.addWidget(phone_group)
        telethon_layout.addWidget(self.btnCheckTelethon)
        telethon_layout.addStretch()
        
        # Thêm các tab vào widget tab
        self.tabWidget.addTab(telegram_tab, "Telegram Bot API")
        self.tabWidget.addTab(telethon_tab, "Telethon API")
        
        # Thêm widget tab vào layout chính
        layout.addWidget(self.tabWidget)
        
        # Layout nút
        button_layout = QtWidgets.QHBoxLayout()
        
        # Nút lưu bản nháp
        self.btnSaveDraft = QtWidgets.QPushButton("Lưu dạng bản nháp")
        self.btnSaveDraft.clicked.connect(self.save_draft)
        button_layout.addWidget(self.btnSaveDraft)
        
        # Khoảng cách
        button_layout.addStretch()
        
        # Nút lưu cài đặt
        self.btnSave = QtWidgets.QPushButton("Lưu cài đặt")
        self.btnSave.clicked.connect(self.save_config)
        self.btnSave.setEnabled(False)
        button_layout.addWidget(self.btnSave)
        
        # Thêm layout nút vào layout chính
        layout.addLayout(button_layout)
    
    def load_existing_config(self):
        """Tải cấu hình hiện có từ file config.ini"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.ini")
        
        if os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.read(config_path)
            
            # Tải cấu hình Telegram Bot
            if config.has_section('TELEGRAM'):
                if config.has_option('TELEGRAM', 'bot_token'):
                    self.txtTelegramToken.setText(config.get('TELEGRAM', 'bot_token'))
                
                if config.has_option('TELEGRAM', 'chat_id'):
                    self.txtChatId.setText(config.get('TELEGRAM', 'chat_id'))
            
            # Tải cấu hình Telethon
            if config.has_section('TELETHON'):
                if config.has_option('TELETHON', 'api_id'):
                    self.txtApiId.setText(config.get('TELETHON', 'api_id'))
                
                if config.has_option('TELETHON', 'api_hash'):
                    self.txtApiHash.setText(config.get('TELETHON', 'api_hash'))
                
                if config.has_option('TELETHON', 'phone'):
                    self.txtPhone.setText(config.get('TELETHON', 'phone'))
    
    def update_ui_state(self):
        """Cập nhật trạng thái UI dựa trên trạng thái kết nối"""
        # Tab Telethon chỉ được kích hoạt khi đã kết nối Telegram Bot
        self.tabWidget.setTabEnabled(1, self.telegram_connected)
        
        # Cập nhật biểu tượng trạng thái cho các tab
        if self.telegram_connected:
            self.tabWidget.setTabIcon(0, self.get_status_icon(True))
        else:
            self.tabWidget.setTabIcon(0, self.get_status_icon(False))
        
        if self.telethon_connected:
            self.tabWidget.setTabIcon(1, self.get_status_icon(True))
        else:
            self.tabWidget.setTabIcon(1, self.get_status_icon(False))
        
        # Cập nhật trạng thái nút lưu
        self.btnSave.setEnabled(self.telegram_connected or self.telethon_connected)
    
    def get_status_icon(self, success):
        """
        Tạo biểu tượng trạng thái
        
        Args:
            success (bool): Trạng thái kết nối thành công
            
        Returns:
            QtGui.QIcon: Biểu tượng trạng thái
        """
        # Tạo pixmap 16x16
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        # Tạo painter
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        if success:
            # Vẽ dấu tích màu xanh
            painter.setPen(Qt.NoPen)
            painter.setBrush(QtGui.QColor("#2ECC71"))
            painter.drawEllipse(2, 2, 12, 12)
            
            painter.setPen(QtGui.QPen(Qt.white, 2))
            painter.drawLine(4, 8, 7, 11)
            painter.drawLine(7, 11, 12, 5)
        else:
            # Vẽ dấu X màu đỏ
            painter.setPen(Qt.NoPen)
            painter.setBrush(QtGui.QColor("#E74C3C"))
            painter.drawEllipse(2, 2, 12, 12)
            
            painter.setPen(QtGui.QPen(Qt.white, 2))
            painter.drawLine(5, 5, 11, 11)
            painter.drawLine(5, 11, 11, 5)
        
        painter.end()
        
        return QtGui.QIcon(pixmap)
    
    def check_telegram_connection(self):
        """Kiểm tra kết nối Telegram Bot"""
        token = self.txtTelegramToken.text().strip()
        chat_id = self.txtChatId.text().strip()
        
        if not token or not chat_id:
            QtWidgets.QMessageBox.warning(
                self,
                "Thiếu thông tin",
                "Vui lòng nhập đầy đủ token và chat ID"
            )
            return
        
        # Disable nút kiểm tra trong quá trình kiểm tra
        self.btnCheckTelegram.setEnabled(False)
        self.btnCheckTelegram.setText("Đang kiểm tra...")
        
        # Tạo thread kiểm tra kết nối
        self.telegram_check_thread = CheckTelegramThread(token, chat_id)
        self.telegram_check_thread.resultReady.connect(self.on_telegram_check_result)
        self.telegram_check_thread.start()
    
    def on_telegram_check_result(self, success, message):
        """
        Xử lý kết quả kiểm tra kết nối Telegram
        
        Args:
            success (bool): Kết nối thành công hay không
            message (str): Thông báo kết quả
        """
        # Khôi phục trạng thái nút
        self.btnCheckTelegram.setEnabled(True)
        self.btnCheckTelegram.setText("Kiểm tra kết nối")
        
        # Cập nhật trạng thái
        self.telegram_connected = success
        
        # Hiển thị kết quả
        if success:
            QtWidgets.QMessageBox.information(
                self,
                "Kết nối thành công",
                "Đã kết nối thành công đến Telegram Bot API!"
            )
        else:
            QtWidgets.QMessageBox.critical(
                self,
                "Lỗi kết nối",
                f"Không thể kết nối đến Telegram Bot API: {message}"
            )
        
        # Cập nhật UI
        self.update_ui_state()
    
    def request_telethon_code(self):
        """Yêu cầu mã xác thực Telethon"""
        api_id = self.txtApiId.text().strip()
        api_hash = self.txtApiHash.text().strip()
        phone = self.txtPhone.text().strip()
        
        if not api_id or not api_hash or not phone:
            QtWidgets.QMessageBox.warning(
                self,
                "Thiếu thông tin",
                "Vui lòng nhập đầy đủ API ID, API Hash và số điện thoại"
            )
            return
        
        # Kiểm tra định dạng API ID
        try:
            api_id = int(api_id)
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self,
                "Sai định dạng",
                "API ID phải là số nguyên"
            )
            return
        
        # Hiển thị modal OTP
        from src.ui.otp_modal import OTPModal
        otp_modal = OTPModal(self, api_id=str(api_id), api_hash=api_hash, phone=phone)
        result = otp_modal.exec_()
        
        if result == QtWidgets.QDialog.Accepted:
            # OTP xác thực thành công
            self.telethon_connected = True
            QtWidgets.QMessageBox.information(
                self,
                "Xác thực thành công",
                "Đã xác thực thành công với Telethon API!"
            )
            self.update_ui_state()
    
    def save_draft(self):
        """Lưu cấu hình dạng bản nháp"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.ini")
        
        # Kiểm tra xem file config đã tồn tại chưa
        config = configparser.ConfigParser()
        if os.path.exists(config_path):
            config.read(config_path)
        
        # Đảm bảo các section tồn tại
        if not config.has_section('TELEGRAM'):
            config.add_section('TELEGRAM')
        
        if not config.has_section('TELETHON'):
            config.add_section('TELETHON')
        
        # Lưu cấu hình Telegram Bot
        config.set('TELEGRAM', 'bot_token', self.txtTelegramToken.text().strip())
        config.set('TELEGRAM', 'chat_id', self.txtChatId.text().strip())
        
        # Lưu cấu hình Telethon
        config.set('TELETHON', 'api_id', self.txtApiId.text().strip())
        config.set('TELETHON', 'api_hash', self.txtApiHash.text().strip())
        config.set('TELETHON', 'phone', self.txtPhone.text().strip())
        
        # Lưu file config
        with open(config_path, 'w') as f:
            config.write(f)
        
        # Hiển thị thông báo
        QtWidgets.QMessageBox.information(
            self,
            "Lưu bản nháp",
            "Đã lưu cấu hình dạng bản nháp thành công."
        )
    
    def save_config(self):
        """Lưu cấu hình chính thức"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.ini")
        
        # Kiểm tra xem file config đã tồn tại chưa
        config = configparser.ConfigParser()
        if os.path.exists(config_path):
            config.read(config_path)
        
        # Đảm bảo các section tồn tại
        if not config.has_section('TELEGRAM'):
            config.add_section('TELEGRAM')
        
        if not config.has_section('TELETHON'):
            config.add_section('TELETHON')
        
        if not config.has_section('SETTINGS'):
            config.add_section('SETTINGS')
        
        # Lưu cấu hình Telegram Bot
        config.set('TELEGRAM', 'bot_token', self.txtTelegramToken.text().strip())
        config.set('TELEGRAM', 'chat_id', self.txtChatId.text().strip())
        
        # Lưu cấu hình Telethon
        config.set('TELETHON', 'api_id', self.txtApiId.text().strip())
        config.set('TELETHON', 'api_hash', self.txtApiHash.text().strip())
        config.set('TELETHON', 'phone', self.txtPhone.text().strip())
        
        # Nếu Telethon đã kết nối thành công, đánh dấu sử dụng Telethon
        if self.telethon_connected:
            config.set('TELETHON', 'use_telethon', 'true')
        else:
            config.set('TELETHON', 'use_telethon', 'false')
        
        # Lưu file config
        with open(config_path, 'w') as f:
            config.write(f)
        
        # Hiển thị thông báo
        QtWidgets.QMessageBox.information(
            self,
            "Lưu cấu hình",
            "Đã lưu cấu hình thành công."
        )
        
        # Phát tín hiệu cấu hình đã lưu
        self.configSaved.emit(True)
        
        # Đóng dialog
        self.accept()
    
    def closeEvent(self, event):
        """
        Xử lý khi người dùng đóng dialog
        
        Args:
            event: Sự kiện đóng
        """
        # Nếu chưa có cấu hình nào được kết nối thành công, hiển thị cảnh báo
        if not self.telegram_connected and not self.telethon_connected:
            reply = QtWidgets.QMessageBox.question(
                self, 
                "Xác nhận thoát", 
                "Bạn chưa cấu hình kết nối Telegram. Ứng dụng sẽ không hoạt động đầy đủ.\n\nBạn có chắc chắn muốn thoát?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            
            if reply == QtWidgets.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def on_finish(self):
        """Xử lý khi config modal hoàn tất"""
        # Kiểm tra xem có cấu hình nào được kết nối thành công không
        if not self.telegram_connected and not self.telethon_connected:
            QtWidgets.QMessageBox.warning(
                self,
                "Cấu hình chưa đầy đủ",
                "Bạn cần cấu hình kết nối Telegram và Telethon để sử dụng ứng dụng."
            )
            event.accept()
        else:
            event.accept()

class CheckTelegramThread(QtCore.QThread):
    """
    Thread kiểm tra kết nối Telegram Bot
    """
    resultReady = QtCore.pyqtSignal(bool, str)
    
    def __init__(self, token, chat_id):
        super(CheckTelegramThread, self).__init__()
        self.token = token
        self.chat_id = chat_id
    
    def run(self):
        """Kiểm tra kết nối Telegram Bot"""
        try:
            import requests
            
            # Kiểm tra token
            url = f"https://api.telegram.org/bot{self.token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                self.resultReady.emit(False, "Token không hợp lệ")
                return
            
            # Kiểm tra chat ID
            url = f"https://api.telegram.org/bot{self.token}/getChat?chat_id={self.chat_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                self.resultReady.emit(False, "Chat ID không hợp lệ")
                return
            
            # Thành công
            self.resultReady.emit(True, "")
        
        except Exception as e:
            self.resultReady.emit(False, str(e))

if __name__ == "__main__":
    # Test ConfigModal
    app = QtWidgets.QApplication(sys.argv)
    dialog = ConfigModal()
    dialog.show()
    sys.exit(app.exec_())