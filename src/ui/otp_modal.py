"""
Module hiển thị giao diện xác thực OTP cho Telethon API
"""
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
import logging
import os
import traceback
import threading

logger = logging.getLogger(__name__)

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
        """Khởi tạo modal OTP"""
        super(OTPModal, self).__init__(parent, Qt.Window)
        
        # Lưu thông tin API
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        
        # Trạng thái hiện tại
        self.current_state = OTPVerificationState.LOADING
        
        # Biến lưu mã OTP
        self.otp_code = ""
        
        # Thời gian hết hạn OTP (mặc định 2 phút)
        self.otp_expiry_seconds = 120
        self.countdown_seconds = self.otp_expiry_seconds
        
        # Biến kiểm soát cooldown
        self.cooldown_seconds = 0
        
        # Thiết lập UI
        self.setup_ui()
        
        # Căn giữa cửa sổ
        self.center_on_screen()
        
        # Kết nối các sự kiện
        self.connect_events()
        
        # Tự động bắt đầu quá trình xác thực
        QtCore.QTimer.singleShot(100, self.start_verification)
    
    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        # Thiết lập cửa sổ
        self.setWindowTitle("Xác thực Telethon API")
        self.setFixedSize(500, 450)
        
        # Thiết lập stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 10px;
            }
            
            QLabel.titleLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1E293B;
            }
            
            QLabel.messageLabel {
                font-size: 16px;
                font-weight: bold;
                color: #3498DB;
            }
            
            QLabel.infoLabel {
                font-size: 14px;
                color: #64748B;
            }
            
            QPushButton.primaryButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 16px;
                font-weight: bold;
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
                font-size: 14px;
            }
            
            QPushButton.secondaryButton:hover {
                background-color: #D1E6FA;
            }
            
            QLineEdit.otpDigit {
                background-color: #F9FAFB;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 10px;
                font-size: 24px;
                color: #1E293B;
                text-align: center;
            }
            
            QFrame.statusInfo {
                background-color: #EBF8FF;
                border: 1px solid #BEE3F8;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        # Layout chính
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)
        
        # Stack cho các trạng thái khác nhau
        self.state_stack = QtWidgets.QStackedWidget()
        
        # Tạo giao diện cho các trạng thái
        self.loading_widget = self.create_loading_widget()
        self.verification_widget = self.create_verification_widget()
        self.expired_widget = self.create_expired_widget()
        
        # Thêm vào stack
        self.state_stack.addWidget(self.loading_widget)
        self.state_stack.addWidget(self.verification_widget)
        self.state_stack.addWidget(self.expired_widget)
        
        # Thêm vào layout chính
        self.main_layout.addWidget(self.state_stack)
        
        # Hiển thị trạng thái đầu tiên
        self.state_stack.setCurrentIndex(self.current_state)
    
    def create_loading_widget(self):
        """Tạo widget hiển thị khi đang tải/gửi mã OTP"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Tiêu đề
        title_label = QtWidgets.QLabel("Xác thực Telethon API")
        title_label.setProperty("class", "titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Biểu tượng loading
        loading_icon = self.create_loading_animation(50)
        layout.addWidget(loading_icon, 0, Qt.AlignCenter)
        
        # Thông báo
        self.loading_message = QtWidgets.QLabel("Đang gửi mã xác thực...")
        self.loading_message.setProperty("class", "messageLabel")
        self.loading_message.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.loading_message)
        
        # Số điện thoại
        phone_layout = QtWidgets.QHBoxLayout()
        phone_label = QtWidgets.QLabel("Số điện thoại:")
        phone_label.setProperty("class", "infoLabel")
        self.phone_edit = QtWidgets.QLineEdit()
        self.phone_edit.setReadOnly(True)
        if self.phone:
            self.phone_edit.setText(self.phone)
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_edit)
        layout.addLayout(phone_layout)
        
        # Thông tin
        info_label = QtWidgets.QLabel("Vui lòng đợi trong khi chúng tôi gửi mã xác thực đến tài khoản Telegram của bạn.")
        info_label.setProperty("class", "infoLabel")
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Nút hủy
        button_layout = QtWidgets.QHBoxLayout()
        self.cancel_button = QtWidgets.QPushButton("Hủy")
        self.cancel_button.setProperty("class", "secondaryButton")
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        return widget
    
    def create_verification_widget(self):
        """Tạo widget nhập mã xác thực OTP"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Tiêu đề
        title_label = QtWidgets.QLabel("Nhập mã xác thực")
        title_label.setProperty("class", "titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Thông báo
        message_layout = QtWidgets.QHBoxLayout()
        icon_label = QtWidgets.QLabel("🔒")
        icon_label.setStyleSheet("font-size: 20px;")
        self.verify_message = QtWidgets.QLabel("Nhập mã xác thực Telegram đã gửi cho bạn")
        self.verify_message.setProperty("class", "messageLabel")
        message_layout.addWidget(icon_label)
        message_layout.addWidget(self.verify_message)
        layout.addLayout(message_layout)
        
        # Nhập mã OTP
        otp_layout = QtWidgets.QHBoxLayout()
        otp_layout.setSpacing(10)
        
        # Tạo 5 ô nhập mã
        self.otp_digits = []
        for i in range(5):
            digit = QtWidgets.QLineEdit()
            digit.setProperty("class", "otpDigit")
            digit.setMaxLength(1)
            digit.setAlignment(Qt.AlignCenter)
            digit.setFixedSize(50, 50)
            digit.textChanged.connect(lambda text, idx=i: self.on_digit_changed(text, idx))
            otp_layout.addWidget(digit)
            self.otp_digits.append(digit)
        
        layout.addLayout(otp_layout)
        
        # Thời gian còn lại
        countdown_frame = QtWidgets.QFrame()
        countdown_frame.setProperty("class", "statusInfo")
        countdown_layout = QtWidgets.QHBoxLayout(countdown_frame)
        countdown_layout.setContentsMargins(10, 10, 10, 10)
        
        timer_icon = QtWidgets.QLabel("⏱️")
        timer_icon.setStyleSheet("font-size: 16px;")
        self.countdown_label = QtWidgets.QLabel("Mã xác thực còn hiệu lực trong: 02:00")
        countdown_layout.addWidget(timer_icon)
        countdown_layout.addWidget(self.countdown_label)
        countdown_layout.addStretch()
        
        layout.addWidget(countdown_frame)
        
        # Nút xác thực
        button_layout = QtWidgets.QHBoxLayout()
        self.verify_button = QtWidgets.QPushButton("Xác thực")
        self.verify_button.setProperty("class", "primaryButton")
        self.verify_button.setEnabled(False)
        
        self.resend_button = QtWidgets.QPushButton("Gửi lại mã")
        self.resend_button.setProperty("class", "secondaryButton")
        self.resend_button.setEnabled(False)
        
        button_layout.addWidget(self.resend_button)
        button_layout.addStretch()
        button_layout.addWidget(self.verify_button)
        layout.addLayout(button_layout)
        
        return widget
    
    def create_expired_widget(self):
        """Tạo widget hiển thị khi mã OTP hết hạn"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Tiêu đề
        title_label = QtWidgets.QLabel("Mã xác thực đã hết hạn")
        title_label.setProperty("class", "titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Biểu tượng
        icon_label = QtWidgets.QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 50px; color: #EF4444;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Thông báo
        message = QtWidgets.QLabel("Mã xác thực Telegram của bạn đã hết hạn hoặc không hợp lệ.")
        message.setProperty("class", "messageLabel")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Thông tin cooldown
        cooldown_frame = QtWidgets.QFrame()
        cooldown_frame.setProperty("class", "statusInfo")
        cooldown_layout = QtWidgets.QHBoxLayout(cooldown_frame)
        
        timer_icon = QtWidgets.QLabel("⏱️")
        timer_icon.setStyleSheet("font-size: 16px;")
        self.cooldown_label = QtWidgets.QLabel("Bạn cần đợi thêm 60 giây trước khi gửi lại mã")
        cooldown_layout.addWidget(timer_icon)
        cooldown_layout.addWidget(self.cooldown_label)
        
        layout.addWidget(cooldown_frame)
        
        # Nút gửi lại và hủy
        button_layout = QtWidgets.QHBoxLayout()
        self.expired_resend_button = QtWidgets.QPushButton("Gửi lại mã")
        self.expired_resend_button.setProperty("class", "primaryButton")
        self.expired_resend_button.setEnabled(False)
        
        self.expired_cancel_button = QtWidgets.QPushButton("Hủy")
        self.expired_cancel_button.setProperty("class", "secondaryButton")
        
        button_layout.addWidget(self.expired_cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.expired_resend_button)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        
        return widget
    
    def center_on_screen(self):
        """Đặt cửa sổ vào giữa màn hình"""
        frame_geometry = self.frameGeometry()
        screen_center = QtWidgets.QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
    
    def create_loading_animation(self, size):
        """Tạo label với animation loading xoay tròn"""
        loading_label = QtWidgets.QLabel()
        loading_label.setFixedSize(size, size)
        
        # Tạo movie từ ảnh động (nếu có)
        loading_movie = None
        try:
            # Thử tìm file loading.gif
            current_dir = os.path.dirname(os.path.abspath(__file__))
            loading_path = os.path.join(current_dir, "assets", "loading.gif")
            
            if not os.path.exists(loading_path):
                # Thử đường dẫn khác
                loading_path = os.path.join(current_dir, "..", "assets", "loading.gif")
            
            if os.path.exists(loading_path):
                loading_movie = QtGui.QMovie(loading_path)
                loading_movie.setScaledSize(QtCore.QSize(size, size))
                loading_label.setMovie(loading_movie)
                loading_movie.start()
        except Exception as e:
            logger.error(f"Không thể tạo loading animation: {str(e)}")
        
        # Nếu không có animation, tạo text thay thế
        if not loading_movie:
            loading_label.setText("⌛")
            loading_label.setAlignment(Qt.AlignCenter)
            loading_label.setStyleSheet(f"font-size: {size//2}px; color: #3498DB;")
        
        return loading_label
    
    def connect_events(self):
        """Kết nối sự kiện cho các control"""
        # Nút trong widget loading
        self.cancel_button.clicked.connect(self.reject)
        
        # Nút trong widget verification
        self.verify_button.clicked.connect(self.verify_otp)
        self.resend_button.clicked.connect(self.resend_code)
        
        # Nút trong widget expired
        self.expired_cancel_button.clicked.connect(self.reject)
        self.expired_resend_button.clicked.connect(self.resend_code)
    
    def start_verification(self):
        """Bắt đầu quá trình xác thực OTP"""
        # Kiểm tra giới hạn yêu cầu OTP
        if not self.check_otp_request_limits():
            return
        
        # Yêu cầu mã OTP
        self.request_otp_code()
    
    def check_otp_request_limits(self):
        """Kiểm tra giới hạn số lần yêu cầu OTP"""
        try:
            from utils.otp_manager import OTPManager
            
            # Khởi tạo OTP Manager
            otp_manager = OTPManager()
            
            # Kiểm tra giới hạn
            can_request, message = otp_manager.check_request_limits()
            
            if not can_request:
                # Hiển thị thông báo lỗi
                QtWidgets.QMessageBox.warning(
                    self,
                    "Giới hạn yêu cầu OTP",
                    message,
                    QtWidgets.QMessageBox.Ok
                )
                
                # Lấy thông tin giới hạn hiện tại
                limits = otp_manager.get_current_limits()
                
                # Nếu đang trong thời gian chờ cooldown, hiển thị màn hình expired
                if limits["cooldown_remaining"] > 0:
                    self.cooldown_seconds = limits["cooldown_remaining"]
                    self.current_state = OTPVerificationState.EXPIRED
                    self.state_stack.setCurrentIndex(self.current_state)
                    
                    # Cập nhật label cooldown
                    self.cooldown_label.setText(f"Bạn cần đợi thêm {self.cooldown_seconds} giây trước khi gửi lại mã")
                    
                    # Bắt đầu đếm ngược cooldown
                    self.start_cooldown_timer()
                    
                    return False
                else:
                    # Nếu đã vượt quá số lần yêu cầu trong ngày, đóng dialog
                self.reject()
                return False
        
            return True
        except Exception as e:
            logger.error(f"Lỗi kiểm tra giới hạn OTP: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Giả định có thể yêu cầu OTP
        return True
    
    def request_otp_code(self):
        """Gửi yêu cầu mã OTP đến Telethon API"""
        # Cập nhật giao diện
        self.loading_message.setText("Đang gửi mã xác thực...")
        QtWidgets.QApplication.processEvents()
        
        # Kiểm tra API ID và API Hash
        if not self.api_id or not self.api_hash or not self.phone:
            QtWidgets.QMessageBox.warning(
                self,
                "Thiếu thông tin",
                "Thiếu thông tin cấu hình Telethon API. Vui lòng kiểm tra lại.",
                QtWidgets.QMessageBox.Ok
            )
            self.reject()
            return
        
        # Ghi nhận yêu cầu OTP
        try:
            from utils.otp_manager import OTPManager
            otp_manager = OTPManager()
            otp_manager.record_request()
        except Exception as e:
            logger.error(f"Lỗi ghi nhận yêu cầu OTP: {str(e)}")
        
        # Tạo và khởi động thread yêu cầu OTP
        def otp_request_thread():
            try:
                from utils.otp_manager import TelethonSessionManager
                from telethon.errors import FloodWaitError, PhoneNumberInvalidError, ApiIdInvalidError
                
                session_manager = TelethonSessionManager()
                client = session_manager.create_client(self.api_id, self.api_hash)
                
                # Kiểm tra xem đã đăng nhập chưa
                async def check_auth():
                    await client.connect()
                    if await client.is_user_authorized():
                        # Đã đăng nhập rồi
                        QtCore.QMetaObject.invokeMethod(self, "on_already_authorized", Qt.QueuedConnection)
                        return True
                    
                    # Chưa đăng nhập, gửi mã xác thực
                    try:
                        await client.send_code_request(self.phone)
                        # Gửi mã thành công
                        QtCore.QMetaObject.invokeMethod(self, "on_code_sent", Qt.QueuedConnection)
                        return False
                    except FloodWaitError as e:
                        # Bị giới hạn, cần đợi
                        error_msg = f"Bạn cần đợi {e.seconds} giây trước khi gửi lại mã"
                        QtCore.QMetaObject.invokeMethod(
                            self, "on_request_error", 
                            Qt.QueuedConnection,
                            QtCore.Q_ARG(str, error_msg)
                        )
                    except (PhoneNumberInvalidError, ApiIdInvalidError) as e:
                        # Số điện thoại không hợp lệ
                        error_msg = f"Lỗi: {str(e)}"
                QtCore.QMetaObject.invokeMethod(
                            self, "on_request_error",
                            Qt.QueuedConnection,
                            QtCore.Q_ARG(str, error_msg)
                        )
                    except Exception as e:
                        # Lỗi khác
                        error_msg = f"Lỗi: {str(e)}"
            QtCore.QMetaObject.invokeMethod(
                            self, "on_request_error",
                            Qt.QueuedConnection,
                            QtCore.Q_ARG(str, error_msg)
                        )
                    
                    return False
                
                # Chạy coroutine
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(check_auth())
                loop.close()
            
        except Exception as e:
                logger.error(f"Lỗi khi gửi yêu cầu OTP: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Thông báo lỗi
            QtCore.QMetaObject.invokeMethod(
                    self, "on_request_error",
                Qt.QueuedConnection,
                    QtCore.Q_ARG(str, f"Lỗi: {str(e)}")
            )
        
        # Khởi động thread
        threading.Thread(target=otp_request_thread, daemon=True).start()
    
    @QtCore.pyqtSlot()
    def on_already_authorized(self):
        """Xử lý khi tài khoản đã được xác thực"""
        # Hiển thị thông báo
        QtWidgets.QMessageBox.information(
            self,
            "Đã xác thực",
            "Tài khoản Telethon của bạn đã được xác thực. Không cần nhập mã OTP.",
            QtWidgets.QMessageBox.Ok
        )
        
        # Cập nhật xác thực thành công và đóng dialog
        self.accept()
    
    @QtCore.pyqtSlot()
    def on_code_sent(self):
        """Xử lý khi mã OTP đã được gửi thành công"""
        # Cập nhật giao diện
        self.current_state = OTPVerificationState.VERIFY
        self.state_stack.setCurrentIndex(self.current_state)
        
        # Focus vào ô nhập đầu tiên
        if self.otp_digits and len(self.otp_digits) > 0:
        self.otp_digits[0].setFocus()
        
        # Bắt đầu đếm ngược
        self.countdown_seconds = self.otp_expiry_seconds
        timer = QTimer(self)
        timer.timeout.connect(self.update_countdown)
        timer.start(1000)
    
    @QtCore.pyqtSlot(str)
    def on_request_error(self, error_message):
        """Xử lý khi có lỗi yêu cầu mã OTP"""
        # Hiển thị thông báo lỗi
        QtWidgets.QMessageBox.warning(
            self,
            "Lỗi gửi mã xác thực",
            error_message,
            QtWidgets.QMessageBox.Ok
        )
        
        # Đóng dialog
        self.reject()
    
    def on_digit_changed(self, text, index):
        """Xử lý khi người dùng nhập ký tự vào ô OTP"""
        if text:
            # Tự động chuyển đến ô tiếp theo
            if index < len(self.otp_digits) - 1:
                self.otp_digits[index + 1].setFocus()
                
            # Kiểm tra xem đã nhập đủ OTP chưa
            self.check_otp_complete()
        
        # Xử lý khi xóa ký tự
        if not text and index > 0:
            # Focus về ô trước đó
            self.otp_digits[index - 1].setFocus()
    
    def check_otp_complete(self):
        """Kiểm tra xem đã nhập đủ mã OTP chưa và bật nút xác thực"""
        otp_code = self.get_otp_code()
        
        # Chỉ bật nút xác thực khi đã nhập đủ mã (đủ 5 ký tự)
        if len(otp_code) == 5:
            self.verify_button.setEnabled(True)
        else:
            self.verify_button.setEnabled(False)
    
    def get_otp_code(self):
        """Lấy mã OTP đã nhập"""
        if not hasattr(self, 'otp_digits'):
            return ""
        
        return ''.join([digit.text() for digit in self.otp_digits])
    
    def update_countdown(self):
        """Cập nhật thời gian còn lại của mã OTP"""
        if self.countdown_seconds > 0:
            self.countdown_seconds -= 1
            minutes = self.countdown_seconds // 60
            seconds = self.countdown_seconds % 60
            self.countdown_label.setText(f"Mã xác thực còn hiệu lực trong: {minutes:02d}:{seconds:02d}")
            
            # Bật nút gửi lại khi còn dưới 30 giây
            if self.countdown_seconds <= 30:
                self.resend_button.setEnabled(True)
        else:
            # Hết thời gian, chuyển sang trạng thái hết hạn
            self.current_state = OTPVerificationState.EXPIRED
            self.state_stack.setCurrentIndex(self.current_state)
            
            # Bắt đầu cooldown
            self.cooldown_seconds = 60  # 1 phút cooldown
            self.cooldown_label.setText(f"Bạn cần đợi thêm {self.cooldown_seconds} giây trước khi gửi lại mã")
            
                # Bắt đầu đếm ngược cooldown
                self.start_cooldown_timer()
    
    def start_cooldown_timer(self):
        """Bắt đầu đếm ngược thời gian chờ giữa các lần gửi mã"""
        # Tắt nút gửi lại
        self.expired_resend_button.setEnabled(False)
        
        # Bắt đầu timer
        timer = QTimer(self)
        timer.timeout.connect(self.update_cooldown)
        timer.start(1000)
    
    def update_cooldown(self):
        """Cập nhật thời gian chờ còn lại"""
        if self.cooldown_seconds > 0:
            self.cooldown_seconds -= 1
            self.cooldown_label.setText(f"Bạn cần đợi thêm {self.cooldown_seconds} giây trước khi gửi lại mã")
        else:
            # Hết thời gian cooldown
            self.cooldown_label.setText("Bạn có thể gửi lại mã xác thực ngay bây giờ")
            
            # Bật nút gửi lại
            self.expired_resend_button.setEnabled(True)
            
            # Dừng timer
            sender = self.sender()
            if isinstance(sender, QTimer):
                sender.stop()
    
    def verify_otp(self):
        """Xác thực mã OTP đã nhập"""
        # Lấy mã OTP
        otp_code = self.get_otp_code()
        
        # Kiểm tra mã có đủ độ dài không
        if len(otp_code) != 5:
            QtWidgets.QMessageBox.warning(
                self,
                "Mã không hợp lệ",
                "Vui lòng nhập đủ 5 ký tự của mã xác thực.",
                QtWidgets.QMessageBox.Ok
            )
            return
        
        # Tiến hành xác thực
        self.verify_otp_code(otp_code)
    
    def verify_otp_code(self, otp_code):
        """Gửi mã OTP đến Telethon API để xác thực"""
        # Cập nhật giao diện
        self.verify_button.setEnabled(False)
        self.verify_button.setText("Đang xác thực...")
        QtWidgets.QApplication.processEvents()
        
        # Tạo và khởi động thread xác thực
        def otp_verify_thread():
            try:
                from utils.otp_manager import TelethonSessionManager
                from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
                
                session_manager = TelethonSessionManager()
                client = session_manager.create_client(self.api_id, self.api_hash)
                
                # Xác thực OTP
                async def verify_code():
                    try:
                        await client.connect()
                        
                        # Nếu đã xác thực rồi
                        if await client.is_user_authorized():
                            QtCore.QMetaObject.invokeMethod(self, "on_verification_success", Qt.QueuedConnection)
                return
            
                        # Xác thực mã
                        await client.sign_in(self.phone, code=otp_code)
            
            # Xác thực thành công
                        QtCore.QMetaObject.invokeMethod(self, "on_verification_success", Qt.QueuedConnection)
                    except PhoneCodeInvalidError:
                        # Mã không hợp lệ
                        QtCore.QMetaObject.invokeMethod(
                            self, "on_verification_error",
                            Qt.QueuedConnection,
                            QtCore.Q_ARG(str, "Mã xác thực không đúng. Vui lòng thử lại.")
                        )
                    except SessionPasswordNeededError:
                        # Cần mật khẩu 2FA - không hỗ trợ trong UI này
                        QtCore.QMetaObject.invokeMethod(
                            self, "on_verification_error",
                            Qt.QueuedConnection,
                            QtCore.Q_ARG(str, "Tài khoản của bạn yêu cầu mật khẩu 2FA. Tính năng này chưa được hỗ trợ.")
                        )
                    except Exception as e:
                        # Lỗi khác
            QtCore.QMetaObject.invokeMethod(
                            self, "on_verification_error",
                            Qt.QueuedConnection,
                            QtCore.Q_ARG(str, f"Lỗi: {str(e)}")
                        )
                
                # Chạy coroutine
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(verify_code())
                loop.close()
                
        except Exception as e:
                logger.error(f"Lỗi khi xác thực OTP: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Thông báo lỗi
            QtCore.QMetaObject.invokeMethod(
                    self, "on_verification_error",
                Qt.QueuedConnection,
                    QtCore.Q_ARG(str, f"Lỗi: {str(e)}")
            )
        
        # Khởi động thread
        threading.Thread(target=otp_verify_thread, daemon=True).start()
    
    @QtCore.pyqtSlot()
    def on_verification_success(self):
        """Xử lý khi xác thực thành công"""
        # Hiển thị thông báo
        QtWidgets.QMessageBox.information(
            self,
            "Xác thực thành công",
            "Tài khoản Telethon của bạn đã được xác thực thành công.",
            QtWidgets.QMessageBox.Ok
        )
        
        # Cập nhật xác thực thành công và đóng dialog
        self.accept()
    
    @QtCore.pyqtSlot(str)
    def on_verification_error(self, error_message):
        """Xử lý khi có lỗi xác thực"""
        # Hiển thị thông báo lỗi
        QtWidgets.QMessageBox.warning(
            self,
            "Lỗi xác thực",
            error_message,
            QtWidgets.QMessageBox.Ok
        )
        
        # Reset UI
        self.verify_button.setEnabled(True)
        self.verify_button.setText("Xác thực")
        
        # Xóa mã OTP đã nhập và focus lại ô đầu tiên
        for digit in self.otp_digits:
            digit.clear()
        
        if self.otp_digits and len(self.otp_digits) > 0:
            self.otp_digits[0].setFocus()
    
    def resend_code(self):
        """Gửi lại mã OTP"""
        # Chuyển về trạng thái loading
        self.current_state = OTPVerificationState.LOADING
        self.state_stack.setCurrentIndex(self.current_state)
        
        # Xóa mã OTP đã nhập
        if hasattr(self, 'otp_digits'):
            for digit in self.otp_digits:
                digit.clear()
        
        # Gửi lại mã
        self.start_verification()
    
    def closeEvent(self, event):
        """Xử lý khi đóng cửa sổ"""
        # Dừng tất cả các timer
        for child in self.findChildren(QTimer):
            child.stop()
        
        # Chấp nhận sự kiện đóng
        event.accept()

if __name__ == "__main__":
    # Test modal
    app = QtWidgets.QApplication(sys.argv)
    modal = OTPModal(api_id="12345678", api_hash="abcdef1234567890", phone="+84123456789")
    result = modal.exec_()
    print(f"Result: {result}, Success: {modal.verification_success}")
    sys.exit(app.exec_()) 