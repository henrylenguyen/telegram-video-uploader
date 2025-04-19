"""
Module xử lý modal xác thực OTP cho Telethon
"""
import os
import sys
import json
import logging
import time
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QTimer

logger = logging.getLogger("OTPModal")

class OTPVerificationState:
    """Các trạng thái của modal xác thực OTP"""
    LOADING = 0    # Đang tải/gửi mã OTP
    VERIFY = 1     # Đang nhập mã xác thực
    EXPIRED = 2    # Mã đã hết hạn

class OTPModal(QtWidgets.QDialog):
    """
    Modal xác thực OTP cho Telethon API
    """
    def __init__(self, parent=None, api_id=None, api_hash=None, phone=None):
        super(OTPModal, self).__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setWindowTitle("Xác thực Telethon")
        
        # Lưu thông tin xác thực
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        
        # Thông tin OTP
        self.phone_code_hash = None
        self.otp_timeout = 5 * 60  # 5 phút
        self.remaining_time = self.otp_timeout
        self.verification_success = False
        
        # Thông tin giới hạn yêu cầu OTP
        self.otp_reset_limit = 3  # Số lần được phép reset trong 24h
        self.cooldown_period = 60  # Thời gian chờ giữa các lần reset (giây)
        self.otp_requested_time = None
        self.is_cooldown = False
        
        # Trạng thái hiện tại
        self.current_state = OTPVerificationState.LOADING
        
        # Thiết lập UI
        self.setup_ui()
        
        # Bắt đầu quy trình xác thực
        self.start_verification()
    
    def setup_ui(self):
        """Thiết lập UI cho modal"""
        # Tạo layout chính
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Tạo widget stack để chứa các trạng thái UI khác nhau
        self.state_stack = QtWidgets.QStackedWidget()
        
        # Widget cho trạng thái đang tải
        self.loading_widget = self.create_loading_widget()
        self.state_stack.addWidget(self.loading_widget)
        
        # Widget cho trạng thái nhập OTP
        self.verification_widget = self.create_verification_widget()
        self.state_stack.addWidget(self.verification_widget)
        
        # Widget cho trạng thái OTP hết hạn
        self.expired_widget = self.create_expired_widget()
        self.state_stack.addWidget(self.expired_widget)
        
        # Thiết lập widget hiện tại
        self.state_stack.setCurrentIndex(self.current_state)
        
        # Thêm widget stack vào layout chính
        main_layout.addWidget(self.state_stack)
        
        # Đặt kích thước và vị trí
        self.resize(400, 350)
        self.center_on_screen()
    
    def create_loading_widget(self):
        """Tạo widget cho trạng thái đang tải"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        
        # Icon loading
        loading_label = QtWidgets.QLabel()
        loading_pixmap = self.create_loading_animation(32)
        loading_label.setPixmap(loading_pixmap)
        loading_label.setAlignment(Qt.AlignCenter)
        
        # Tiêu đề
        title_label = QtWidgets.QLabel("Đang gửi yêu cầu xác thực")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Mô tả
        desc_label = QtWidgets.QLabel("Vui lòng đợi trong khi chúng tôi gửi mã xác thực đến Telegram của bạn...")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        
        # Trạng thái
        self.loading_status = QtWidgets.QLabel("Đang kết nối đến Telegram API...")
        self.loading_status.setAlignment(Qt.AlignCenter)
        self.loading_status.setStyleSheet("color: #3498db;")
        
        # Thêm các widget vào layout
        layout.addStretch()
        layout.addWidget(loading_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(self.loading_status)
        layout.addStretch()
        
        return widget
    
    def create_verification_widget(self):
        """Tạo widget cho trạng thái nhập OTP"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        
        # Icon xác thực
        icon_label = QtWidgets.QLabel()
        icon_pixmap = QtGui.QPixmap(32, 32)
        icon_pixmap.fill(Qt.transparent)
        painter = QtGui.QPainter(icon_pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QtGui.QColor("#3498db"))
        painter.drawEllipse(2, 2, 28, 28)
        painter.setPen(QtGui.QPen(Qt.white, 2))
        painter.drawLine(10, 16, 15, 22)
        painter.drawLine(15, 22, 24, 10)
        painter.end()
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Tiêu đề
        title_label = QtWidgets.QLabel("Xác thực Telegram")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Mô tả
        desc_label = QtWidgets.QLabel("Mã OTP đã được gửi đến ứng dụng Telegram của bạn.\nVui lòng nhập mã vào ô bên dưới:")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        
        # Đồng hồ đếm ngược
        self.countdown_label = QtWidgets.QLabel("Mã có hiệu lực trong: 05:00")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("color: #3498db; font-weight: bold;")
        
        # Ô nhập OTP
        otp_layout = QtWidgets.QHBoxLayout()
        self.otp_digits = []
        
        for i in range(6):
            digit = QtWidgets.QLineEdit()
            digit.setMaxLength(1)
            digit.setFixedSize(40, 40)
            digit.setAlignment(Qt.AlignCenter)
            digit.setStyleSheet("font-size: 18px; font-weight: bold;")
            if i > 0:
                digit.setEnabled(False)
            self.otp_digits.append(digit)
            otp_layout.addWidget(digit)
            
            # Kết nối sự kiện
            digit.textChanged.connect(lambda text, idx=i: self.on_digit_changed(text, idx))
        
        # Nút xác thực
        self.verify_button = QtWidgets.QPushButton("Xác thực")
        self.verify_button.setEnabled(False)
        self.verify_button.clicked.connect(self.verify_otp)
        
        # Trạng thái
        self.verification_status = QtWidgets.QLabel("")
        self.verification_status.setAlignment(Qt.AlignCenter)
        
        # Thêm các widget vào layout
        layout.addStretch()
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(self.countdown_label)
        layout.addLayout(otp_layout)
        layout.addWidget(self.verify_button)
        layout.addWidget(self.verification_status)
        layout.addStretch()
        
        return widget
    
    def create_expired_widget(self):
        """Tạo widget cho trạng thái OTP hết hạn"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        
        # Icon hết hạn
        icon_label = QtWidgets.QLabel()
        icon_pixmap = QtGui.QPixmap(32, 32)
        icon_pixmap.fill(Qt.transparent)
        painter = QtGui.QPainter(icon_pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QtGui.QColor("#e74c3c"))
        painter.drawEllipse(2, 2, 28, 28)
        painter.setPen(QtGui.QPen(Qt.white, 2))
        painter.drawLine(10, 10, 22, 22)
        painter.drawLine(10, 22, 22, 10)
        painter.end()
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Tiêu đề
        title_label = QtWidgets.QLabel("Mã xác thực đã hết hạn")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Mô tả
        desc_label = QtWidgets.QLabel("Mã xác thực đã hết hiệu lực hoặc không chính xác.\nVui lòng yêu cầu mã mới để tiếp tục.")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        
        # Đồng hồ đếm ngược cho cooldown
        self.cooldown_label = QtWidgets.QLabel("")
        self.cooldown_label.setAlignment(Qt.AlignCenter)
        self.cooldown_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        # Nút lấy mã mới
        self.resend_button = QtWidgets.QPushButton("Lấy lại mã")
        self.resend_button.clicked.connect(self.resend_code)
        
        # Thông tin giới hạn
        self.limit_label = QtWidgets.QLabel("")
        self.limit_label.setAlignment(Qt.AlignCenter)
        self.limit_label.setWordWrap(True)
        
        # Thêm các widget vào layout
        layout.addStretch()
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(self.cooldown_label)
        layout.addWidget(self.resend_button)
        layout.addWidget(self.limit_label)
        layout.addStretch()
        
        return widget
    
    def center_on_screen(self):
        """Đặt cửa sổ vào giữa màn hình"""
        screen = QtWidgets.QApplication.desktop().availableGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)
    
    def create_loading_animation(self, size):
        """Tạo biểu tượng loading đơn giản"""
        pixmap = QtGui.QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        pen = QtGui.QPen(QtGui.QColor("#3498db"))
        pen.setWidth(3)
        painter.setPen(pen)
        
        painter.drawArc(3, 3, size-6, size-6, 0, 300 * 16)  # 300 độ
        painter.end()
        
        return pixmap
    
    def start_verification(self):
        """Bắt đầu quy trình xác thực"""
        # Đặt trạng thái hiện tại
        self.current_state = OTPVerificationState.LOADING
        self.state_stack.setCurrentIndex(self.current_state)
        
        # Kiểm tra giới hạn yêu cầu OTP
        if not self.check_otp_request_limits():
            return
        
        # Tạo thread gửi mã OTP
        self.request_thread = threading.Thread(target=self.request_otp_code)
        self.request_thread.daemon = True
        self.request_thread.start()
    
    def check_otp_request_limits(self):
        """
        Kiểm tra giới hạn yêu cầu OTP
        
        Returns:
            bool: True nếu có thể yêu cầu OTP, False nếu đã vượt quá giới hạn
        """
        # Đường dẫn file lưu thông tin giới hạn
        app_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
        os.makedirs(app_data_dir, exist_ok=True)
        limits_file = os.path.join(app_data_dir, "otp_limits.json")
        
        # Thông tin mặc định
        limits_data = {
            "last_request_time": None,
            "requests_count": 0,
            "reset_date": None
        }
        
        # Tải thông tin giới hạn nếu có
        if os.path.exists(limits_file):
            try:
                with open(limits_file, "r") as f:
                    limits_data = json.load(f)
            except json.JSONDecodeError:
                pass
        
        # Kiểm tra nếu cần reset đếm
        current_date = datetime.now().strftime("%Y-%m-%d")
        if limits_data["reset_date"] != current_date:
            limits_data["reset_date"] = current_date
            limits_data["requests_count"] = 0
        
        # Kiểm tra số lần yêu cầu trong ngày
        if limits_data["requests_count"] >= self.otp_reset_limit:
            QtWidgets.QMessageBox.critical(
                self,
                "Vượt quá giới hạn",
                f"Bạn đã vượt quá giới hạn yêu cầu mã OTP ({self.otp_reset_limit} lần) trong 24 giờ.\nVui lòng thử lại vào ngày mai."
            )
            self.reject()
            return False
        
        # Kiểm tra thời gian chờ giữa các lần yêu cầu
        if limits_data["last_request_time"]:
            last_time = datetime.fromisoformat(limits_data["last_request_time"])
            elapsed = (datetime.now() - last_time).total_seconds()
            
            if elapsed < self.cooldown_period:
                remaining = int(self.cooldown_period - elapsed)
                QtWidgets.QMessageBox.warning(
                    self,
                    "Vui lòng đợi",
                    f"Vui lòng đợi {remaining} giây trước khi yêu cầu mã mới."
                )
                self.reject()
                return False
        
        # Cập nhật thông tin giới hạn
        limits_data["last_request_time"] = datetime.now().isoformat()
        limits_data["requests_count"] += 1
        
        # Lưu thông tin giới hạn
        with open(limits_file, "w") as f:
            json.dump(limits_data, f)
        
        # Lưu thông tin số lần đã yêu cầu
        self.requests_count = limits_data["requests_count"]
        
        return True
    
    def request_otp_code(self):
        """Gửi yêu cầu mã OTP từ Telethon"""
        try:
            self.loading_status.setText("Đang kết nối đến Telegram API...")
            time.sleep(1)  # Tạm dừng để hiển thị trạng thái
            
            # Thực hiện yêu cầu mã bằng Telethon
            from telethon import TelegramClient
            
            # Đường dẫn session
            session_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "telegram_uploader")
            
            # Kết nối client
            client = TelegramClient(session_path, self.api_id, self.api_hash)
            client.connect()
            
            # Kiểm tra đã xác thực chưa
            if client.is_user_authorized():
                # Đã xác thực, thông báo và đóng modal
                QtCore.QMetaObject.invokeMethod(
                    self, 
                    "on_already_authorized", 
                    Qt.QueuedConnection
                )
                client.disconnect()
                return
            
            # Gửi yêu cầu mã
            self.loading_status.setText("Đang gửi mã xác thực đến Telegram...")
            result = client.send_code_request(self.phone)
            self.phone_code_hash = result.phone_code_hash
            client.disconnect()
            
            # Lưu thời gian yêu cầu OTP
            self.otp_requested_time = datetime.now()
            
            # Chuyển sang trạng thái xác thực
            QtCore.QMetaObject.invokeMethod(
                self, 
                "on_code_sent", 
                Qt.QueuedConnection
            )
            
        except Exception as e:
            # Xử lý lỗi
            error_message = str(e)
            QtCore.QMetaObject.invokeMethod(
                self, 
                "on_request_error", 
                Qt.QueuedConnection,
                QtCore.Q_ARG(str, error_message)
            )
    
    @QtCore.pyqtSlot()
    def on_already_authorized(self):
        """Xử lý khi người dùng đã được xác thực"""
        QtWidgets.QMessageBox.information(
            self,
            "Đã xác thực",
            "Tài khoản Telegram của bạn đã được xác thực trước đó.\nKhông cần xác thực lại."
        )
        
        # Đánh dấu xác thực thành công
        self.verification_success = True
        self.accept()
    
    @QtCore.pyqtSlot()
    def on_code_sent(self):
        """Xử lý khi mã OTP đã được gửi"""
        # Chuyển sang trạng thái xác thực
        self.current_state = OTPVerificationState.VERIFY
        self.state_stack.setCurrentIndex(self.current_state)
        
        # Thiết lập focus vào ô nhập đầu tiên
        self.otp_digits[0].setFocus()
        
        # Bắt đầu đếm ngược
        self.remaining_time = self.otp_timeout
        self.update_countdown()
        
        # Tạo timer đếm ngược
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(1000)  # 1 giây
    
    @QtCore.pyqtSlot(str)
    def on_request_error(self, error_message):
        """
        Xử lý khi có lỗi yêu cầu mã OTP
        
        Args:
            error_message (str): Thông báo lỗi
        """
        QtWidgets.QMessageBox.critical(
            self,
            "Lỗi yêu cầu mã",
            f"Không thể gửi mã xác thực: {error_message}"
        )
        self.reject()
    
    def on_digit_changed(self, text, index):
        """
        Xử lý khi người dùng nhập ký tự vào ô OTP
        
        Args:
            text (str): Ký tự đã nhập
            index (int): Chỉ số của ô
        """
        # Nếu đã nhập một ký tự vào ô hiện tại
        if len(text) == 1:
            # Di chuyển focus sang ô tiếp theo
            if index < 5:
                self.otp_digits[index + 1].setEnabled(True)
                self.otp_digits[index + 1].setFocus()
        
        # Kiểm tra xem đã nhập đủ 6 ký tự chưa
        self.check_otp_complete()
    
    def check_otp_complete(self):
        """Kiểm tra xem đã nhập đủ mã OTP chưa"""
        # Lấy mã OTP hiện tại
        otp_code = self.get_otp_code()
        
        # Kiểm tra độ dài
        if len(otp_code) == 6:
            # Đã nhập đủ, kích hoạt nút xác thực
            self.verify_button.setEnabled(True)
        else:
            # Chưa đủ, vô hiệu hóa nút xác thực
            self.verify_button.setEnabled(False)
    
    def get_otp_code(self):
        """
        Lấy mã OTP đã nhập
        
        Returns:
            str: Mã OTP
        """
        return "".join([digit.text() for digit in self.otp_digits])
    
    def update_countdown(self):
        """Cập nhật đồng hồ đếm ngược"""
        # Giảm thời gian còn lại
        self.remaining_time -= 1
        
        # Kiểm tra nếu hết thời gian
        if self.remaining_time <= 0:
            # Dừng timer
            self.countdown_timer.stop()
            
            # Chuyển sang trạng thái OTP hết hạn
            self.current_state = OTPVerificationState.EXPIRED
            self.state_stack.setCurrentIndex(self.current_state)
            
            # Cập nhật thông tin giới hạn
            self.limit_label.setText(f"Bạn đã sử dụng {self.requests_count}/{self.otp_reset_limit} lần yêu cầu mã trong ngày hôm nay.")
            
            # Kiểm tra xem còn có thể gửi lại không
            if self.requests_count >= self.otp_reset_limit:
                self.resend_button.setEnabled(False)
                self.resend_button.setText("Đã vượt quá giới hạn")
                self.cooldown_label.setText("Vui lòng thử lại vào ngày mai")
            else:
                # Bắt đầu đếm ngược cooldown
                self.start_cooldown_timer()
            
            return
        
        # Định dạng thời gian còn lại
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Cập nhật label
        self.countdown_label.setText(f"Mã có hiệu lực trong: {time_str}")
        
        # Thêm hiệu ứng nhấp nháy khi sắp hết thời gian
        if self.remaining_time < 60:
            if self.remaining_time % 2 == 0:
                self.countdown_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            else:
                self.countdown_label.setStyleSheet("color: #3498db; font-weight: bold;")
    
    def start_cooldown_timer(self):
        """Bắt đầu đếm ngược thời gian chờ giữa các lần yêu cầu OTP"""
        # Thiết lập thời gian chờ
        self.cooldown_remaining = self.cooldown_period
        self.resend_button.setEnabled(False)
        
        # Cập nhật label
        self.update_cooldown()
        
        # Tạo timer
        self.cooldown_timer = QTimer(self)
        self.cooldown_timer.timeout.connect(self.update_cooldown)
        self.cooldown_timer.start(1000)  # 1 giây
    
    def update_cooldown(self):
        """Cập nhật đồng hồ đếm ngược thời gian chờ"""
        # Giảm thời gian còn lại
        self.cooldown_remaining -= 1
        
        # Kiểm tra nếu hết thời gian chờ
        if self.cooldown_remaining <= 0:
            # Dừng timer
            self.cooldown_timer.stop()
            
            # Kích hoạt nút gửi lại
            self.resend_button.setEnabled(True)
            
            # Cập nhật label
            self.cooldown_label.setText("Bạn có thể yêu cầu mã mới ngay bây giờ")
            return
        
        # Cập nhật label
        self.cooldown_label.setText(f"Vui lòng đợi {self.cooldown_remaining} giây để yêu cầu mã mới")
    
    def verify_otp(self):
        """Xác thực mã OTP"""
        # Lấy mã OTP
        otp_code = self.get_otp_code()
        
        # Vô hiệu hóa nút xác thực
        self.verify_button.setEnabled(False)
        self.verify_button.setText("Đang xác thực...")
        
        # Cập nhật trạng thái
        self.verification_status.setText("Đang xác thực...")
        self.verification_status.setStyleSheet("color: #3498db;")
        
        # Tạo thread xác thực
        self.verify_thread = threading.Thread(target=self.verify_otp_code, args=(otp_code,))
        self.verify_thread.daemon = True
        self.verify_thread.start()
    
    def verify_otp_code(self, otp_code):
        """
        Xác thực mã OTP với Telethon
        
        Args:
            otp_code (str): Mã OTP đã nhập
        """
        try:
            # Thực hiện xác thực bằng Telethon
            from telethon import TelegramClient
            
            # Đường dẫn session
            session_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "telegram_uploader")
            
            # Kết nối client
            client = TelegramClient(session_path, self.api_id, self.api_hash)
            client.connect()
            
            # Kiểm tra đã xác thực chưa
            if client.is_user_authorized():
                # Đã xác thực
                QtCore.QMetaObject.invokeMethod(
                    self, 
                    "on_verification_success", 
                    Qt.QueuedConnection
                )
                client.disconnect()
                return
            
            # Gửi mã xác thực
            client.sign_in(self.phone, otp_code, phone_code_hash=self.phone_code_hash)
            client.disconnect()
            
            # Xác thực thành công
            QtCore.QMetaObject.invokeMethod(
                self, 
                "on_verification_success", 
                Qt.QueuedConnection
            )
            
        except Exception as e:
            # Xử lý lỗi
            error_message = str(e)
            QtCore.QMetaObject.invokeMethod(
                self, 
                "on_verification_error", 
                Qt.QueuedConnection,
                QtCore.Q_ARG(str, error_message)
            )
    
    @QtCore.pyqtSlot()
    def on_verification_success(self):
        """Xử lý khi xác thực thành công"""
        # Cập nhật UI
        self.verification_status.setText("Xác thực thành công!")
        self.verification_status.setStyleSheet("color: #2ecc71; font-weight: bold;")
        self.verify_button.setText("Đã xác thực")
        
        # Đánh dấu xác thực thành công
        self.verification_success = True
        
        # Dừng đếm ngược
        if hasattr(self, "countdown_timer") and self.countdown_timer.isActive():
            self.countdown_timer.stop()
        
        # Chờ 1 giây rồi đóng modal
        QTimer.singleShot(1000, self.accept)
    
    @QtCore.pyqtSlot(str)
    def on_verification_error(self, error_message):
        """
        Xử lý khi xác thực thất bại
        
        Args:
            error_message (str): Thông báo lỗi
        """
        # Cập nhật UI
        self.verification_status.setText(f"Lỗi: {error_message}")
        self.verification_status.setStyleSheet("color: #e74c3c;")
        self.verify_button.setText("Xác thực")
        self.verify_button.setEnabled(True)
        
        # Nếu lỗi liên quan đến mã không đúng, chuyển sang trạng thái hết hạn
        if "invalid" in error_message.lower() or "expired" in error_message.lower() or "code" in error_message.lower():
            # Dừng đếm ngược
            if hasattr(self, "countdown_timer") and self.countdown_timer.isActive():
                self.countdown_timer.stop()
            
            # Chuyển sang trạng thái OTP hết hạn
            self.current_state = OTPVerificationState.EXPIRED
            self.state_stack.setCurrentIndex(self.current_state)
            
            # Cập nhật thông tin giới hạn
            self.limit_label.setText(f"Bạn đã sử dụng {self.requests_count}/{self.otp_reset_limit} lần yêu cầu mã trong ngày hôm nay.")
            
            # Bắt đầu đếm ngược cooldown
            self.start_cooldown_timer()
    
    def resend_code(self):
        """Gửi lại mã OTP"""
        # Chuyển về trạng thái đang tải
        self.current_state = OTPVerificationState.LOADING
        self.state_stack.setCurrentIndex(self.current_state)
        
        # Kiểm tra giới hạn yêu cầu OTP
        if not self.check_otp_request_limits():
            return
        
        # Tạo thread gửi mã OTP
        self.request_thread = threading.Thread(target=self.request_otp_code)
        self.request_thread.daemon = True
        self.request_thread.start()
    
    def closeEvent(self, event):
        """
        Xử lý khi người dùng đóng modal
        
        Args:
            event: Sự kiện đóng
        """
        # Dừng các timer nếu đang chạy
        if hasattr(self, "countdown_timer") and self.countdown_timer.isActive():
            self.countdown_timer.stop()
        
        if hasattr(self, "cooldown_timer") and self.cooldown_timer.isActive():
            self.cooldown_timer.stop()
        
        # Từ chối nếu chưa xác thực thành công
        if not self.verification_success:
            self.reject()
        
        event.accept()

if __name__ == "__main__":
    # Test modal
    app = QtWidgets.QApplication(sys.argv)
    modal = OTPModal(api_id="12345678", api_hash="abcdef1234567890", phone="+84123456789")
    result = modal.exec_()
    print(f"Result: {result}, Success: {modal.verification_success}")
    sys.exit(app.exec_()) 