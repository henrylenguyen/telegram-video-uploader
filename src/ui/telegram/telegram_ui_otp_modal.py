"""
Modal OTP cho Telegram UI
"""
import logging
import os
import threading
import asyncio
import time
import traceback
import tempfile
from PyQt5 import QtWidgets, QtCore, QtGui, uic

logger = logging.getLogger(__name__)

class OTPModal(QtWidgets.QDialog):
    """
    Dialog xác thực OTP cho Telethon API
    """
    # Tín hiệu khi xác thực thành công
    verificationSuccess = QtCore.pyqtSignal()
    
    def __init__(self, parent=None, api_id=None, api_hash=None, phone=None, force_manual_ui=False):
        """
        Khởi tạo modal OTP
        
        Args:
            parent: Widget cha
            api_id: API ID của Telethon
            api_hash: API Hash của Telethon
            phone: Số điện thoại
            force_manual_ui: Buộc sử dụng UI thủ công
        """
        super(OTPModal, self).__init__(parent)
        
        # Lưu thông tin Telethon
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        
        # Đặt tiêu đề
        self.setWindowTitle("Xác thực Telethon API")
        
        # Tạo UI
        if force_manual_ui:
            logger.info("Đã chọn ưu tiên UI thủ công cho OTP Modal")
            self.setup_ui_manually()
        else:
            # Thử tải UI từ file
            ui_path = os.path.join(self.get_ui_dir(), "otp_modal.ui")
            
            if not os.path.exists(ui_path):
                logger.warning(f"Không tìm thấy file UI: {ui_path}. Sử dụng UI thủ công.")
                self.setup_ui_manually()
            else:
                try:
                    # Sửa file UI để xử lý các vấn đề tương thích
                    fixed_ui_path = self.fix_ui_file(ui_path)
                    logger.info(f"Đang tải UI OTP Modal từ file: {fixed_ui_path}")
                    
                    # Tải UI từ file đã được sửa
                    uic.loadUi(fixed_ui_path, self)
                    logger.info("Đã tải UI OTP Modal từ file thành công")
                    
                    # Tìm và kết nối các thành phần UI
                    self._collect_ui_components()
                except Exception as e:
                    logger.error(f"Lỗi khi tải UI OTP Modal từ file: {str(e)}")
                    logger.error(f"Chi tiết lỗi:")
                    logger.error(traceback.format_exc())
                    
                    # Sử dụng UI thủ công khi có lỗi
                    logger.info("Đang tạo UI thủ công do lỗi khi tải file UI")
                    self.setup_ui_manually()
        
        # Căn giữa
        self.center_on_screen()
        
        # Bắt đầu yêu cầu mã OTP
        self.start_otp_request()
    
    def get_ui_dir(self):
        """Lấy thư mục chứa file UI"""
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "qt_designer")
    
    def fix_ui_file(self, ui_path):
        """Sửa các vấn đề tương thích trong file UI"""
        # Kiểm tra file tồn tại
        if not os.path.exists(ui_path):
            logger.error(f"File UI không tồn tại: {ui_path}")
            return ui_path
            
        try:
            with open(ui_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Các thay thế cơ bản
            # Sửa các thuộc tính orientation
            content = content.replace('Qt::Orientation::Horizontal', 'Horizontal')
            content = content.replace('Qt::Orientation::Vertical', 'Vertical')
            
            # Sửa tham chiếu không có Orientation:: prefix
            content = content.replace('Qt::Horizontal', 'Horizontal')
            content = content.replace('Qt::Vertical', 'Vertical')
            
            # Sửa thuộc tính cursor
            content = content.replace('property="cursor"', 'property="cursorShape"')
            
            # Sửa thuộc tính alignment cho các nút
            content = content.replace('property="alignment"', 'property="alignmentProperty"')
            
            # Sửa các vấn đề với Qt::AlignmentFlag
            content = content.replace('Qt::AlignmentFlag::', '')
            content = content.replace('Qt::AlignLeading', 'AlignLeading')
            content = content.replace('Qt::AlignLeft', 'AlignLeft')
            content = content.replace('Qt::AlignRight', 'AlignRight')
            content = content.replace('Qt::AlignCenter', 'AlignCenter')
            content = content.replace('Qt::AlignTop', 'AlignTop')
            content = content.replace('Qt::AlignBottom', 'AlignBottom')
            content = content.replace('Qt::AlignHCenter', 'AlignHCenter')
            content = content.replace('Qt::AlignVCenter', 'AlignVCenter')
            content = content.replace('Qt::AlignJustify', 'AlignJustify')
            
            # Sửa các vấn đề với các enum khác
            content = content.replace('Qt::', '')
            
            # Tạo file tạm với nội dung đã sửa
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ui')
            temp_path = temp_file.name
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info(f"Đã sửa file UI {ui_path} -> {temp_path}")
            return temp_path
        except Exception as e:
            logger.error(f"Lỗi khi sửa file UI {ui_path}: {str(e)}")
            logger.error(traceback.format_exc())
            return ui_path
    
    def _collect_ui_components(self):
        """Tìm và kết nối các thành phần UI"""
        # Tìm các ô nhập OTP
        self.otp_fields = []
        for i in range(5):
            field = self.findChild(QtWidgets.QLineEdit, f"otpField{i+1}")
            if field:
                field.textChanged.connect(lambda text, idx=i: self.on_otp_digit_changed(text, idx))
                self.otp_fields.append(field)
            else:
                logger.warning(f"Không tìm thấy ô nhập OTP {i+1}")
        
        # Tìm các label
        self.message_label = self.findChild(QtWidgets.QLabel, "messageLabel")
        self.expiry_label = self.findChild(QtWidgets.QLabel, "expiryLabel")
        
        # Tìm nút gửi lại
        self.resend_button = self.findChild(QtWidgets.QPushButton, "resendButton")
        if self.resend_button:
            self.resend_button.setEnabled(False)
            self.resend_button.clicked.connect(self.resend_otp)
    
    def setup_ui_manually(self):
        """Thiết lập giao diện người dùng theo cách thủ công"""
        # Thiết lập layout chính
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        
        # Tiêu đề
        title_label = QtWidgets.QLabel("Xác thực Telethon API")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label, 0, QtCore.Qt.AlignCenter)
        
        # Thông báo
        self.message_label = QtWidgets.QLabel(
            f"Đang gửi mã xác thực đến số điện thoại {self.phone}.\n"
            "Vui lòng kiểm tra tin nhắn Telegram và nhập mã OTP dưới đây:"
        )
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)
        
        # Layout cho các ô nhập OTP
        otp_layout = QtWidgets.QHBoxLayout()
        
        # Tạo 5 ô nhập OTP
        self.otp_fields = []
        for i in range(5):
            otp_field = QtWidgets.QLineEdit()
            otp_field.setObjectName(f"otpField{i+1}")
            otp_field.setMaxLength(1)
            otp_field.setFixedSize(40, 40)
            otp_field.setAlignment(QtCore.Qt.AlignCenter)
            otp_field.setStyleSheet("""
                QLineEdit {
                    font-size: 18px;
                    border: 1px solid #E2E8F0;
                    border-radius: 6px;
                }
            """)
            
            # Kết nối sự kiện thay đổi văn bản
            otp_field.textChanged.connect(lambda text, idx=i: self.on_otp_digit_changed(text, idx))
            
            otp_layout.addWidget(otp_field)
            self.otp_fields.append(otp_field)
        
        layout.addLayout(otp_layout)
        
        # Thời gian hết hạn
        self.expiry_label = QtWidgets.QLabel("Mã xác thực sẽ hết hạn sau: 5:00")
        self.expiry_label.setObjectName("expiryLabel")
        layout.addWidget(self.expiry_label, 0, QtCore.Qt.AlignCenter)
        
        # Nút gửi lại
        self.resend_button = QtWidgets.QPushButton("Gửi lại mã")
        self.resend_button.setObjectName("resendButton")
        self.resend_button.setEnabled(False)
        self.resend_button.clicked.connect(self.resend_otp)
        layout.addWidget(self.resend_button)
        
        # Đặt kích thước
        self.resize(400, 250)
        
        logger.info("Đã tạo UI thủ công cho OTP Modal thành công")
    
    def center_on_screen(self):
        """Căn giữa cửa sổ trên màn hình"""
        screen = QtWidgets.QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)
    
    def start_otp_request(self):
        """Bắt đầu yêu cầu mã OTP"""
        # Thời gian hết hạn mã OTP (5 phút)
        self.remaining_seconds = 5 * 60
        
        # Bắt đầu đếm ngược
        self.countdown_timer = QtCore.QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(1000)  # Cập nhật mỗi giây
        
        # Focus vào ô đầu tiên
        if self.otp_fields:
            self.otp_fields[0].setFocus()
    
    def update_countdown(self):
        """Cập nhật đếm ngược thời gian"""
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            
            # Định dạng thời gian
            minutes = self.remaining_seconds // 60
            seconds = self.remaining_seconds % 60
            time_str = f"{minutes}:{seconds:02d}"
            
            # Cập nhật label
            self.expiry_label.setText(f"Mã xác thực sẽ hết hạn sau: {time_str}")
            
            # Bật nút gửi lại sau 30 giây
            if not self.resend_button.isEnabled() and self.remaining_seconds <= 4 * 60 + 30:
                self.resend_button.setEnabled(True)
        else:
            # Hết thời gian
            self.countdown_timer.stop()
            self.expiry_label.setText("Mã xác thực đã hết hạn")
            
            # Hiển thị thông báo
            QtWidgets.QMessageBox.warning(
                self,
                "Hết hạn",
                "Mã xác thực đã hết hạn. Vui lòng gửi lại mã mới."
            )
            
            # Xóa các ô OTP
            for field in self.otp_fields:
                field.clear()
            
            # Bật nút gửi lại
            self.resend_button.setEnabled(True)
    
    def on_otp_digit_changed(self, text, index):
        """
        Xử lý khi thay đổi ký tự trong ô OTP
        
        Args:
            text: Văn bản mới
            index: Chỉ số của ô
        """
        if text:
            # Nếu nhập ký tự thì chuyển đến ô tiếp theo
            if index < len(self.otp_fields) - 1:
                self.otp_fields[index + 1].setFocus()
            
            # Kiểm tra nếu đã nhập đủ OTP
            self.check_otp_complete()
        elif index > 0 and not text:
            # Nếu xóa ký tự thì quay lại ô trước đó
            self.otp_fields[index - 1].setFocus()
    
    def check_otp_complete(self):
        """Kiểm tra nếu đã nhập đủ OTP thì thực hiện xác thực"""
        otp_code = self.get_otp_code()
        
        if len(otp_code) == len(self.otp_fields):
            # Thực hiện xác thực
            self.verify_otp(otp_code)
    
    def get_otp_code(self):
        """Lấy mã OTP từ các ô nhập"""
        return ''.join([field.text() for field in self.otp_fields if field.text()])
    
    def verify_otp(self, otp_code):
        """
        Xác thực mã OTP
        
        Args:
            otp_code: Mã OTP cần xác thực
        """
        try:
            from utils.otp_manager import TelethonSessionManager
            
            # Vô hiệu hóa UI
            for field in self.otp_fields:
                field.setEnabled(False)
            self.resend_button.setEnabled(False)
            
            # Tạo session manager
            session_manager = TelethonSessionManager()
            
            # Tạo client
            client = session_manager.create_client(self.api_id, self.api_hash)
            
            # Tạo thread xác thực
            verify_thread = threading.Thread(target=self._verify_otp_thread, args=(client, otp_code))
            verify_thread.daemon = True
            verify_thread.start()
            
        except Exception as e:
            logger.error(f"Lỗi khi xác thực OTP: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Lỗi", f"Không thể xác thực OTP: {str(e)}")
            
            # Bật lại UI
            for field in self.otp_fields:
                field.setEnabled(True)
            self.resend_button.setEnabled(True)
    
    def _verify_otp_thread(self, client, otp_code):
        """
        Thread xác thực OTP
        
        Args:
            client: TelegramClient
            otp_code: Mã OTP
        """
        try:
            # Tạo event loop mới
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Định nghĩa coroutine xác thực
            async def verify_code():
                try:
                    # Kết nối
                    await client.connect()
                    
                    # Kiểm tra nếu đã xác thực
                    if await client.is_user_authorized():
                        logger.info("Người dùng đã được xác thực")
                        
                        # Thông báo thành công về UI thread
                        QtCore.QMetaObject.invokeMethod(
                            self, "_on_verification_success",
                            QtCore.Qt.QueuedConnection
                        )
                    else:
                        # Xác thực với OTP
                        await client.sign_in(self.phone, code=otp_code)
                        
                        # Thông báo thành công về UI thread
                        QtCore.QMetaObject.invokeMethod(
                            self, "_on_verification_success",
                            QtCore.Qt.QueuedConnection
                        )
                        
                except Exception as e:
                    logger.error(f"Lỗi xác thực OTP: {str(e)}")
                    
                    # Thông báo lỗi về UI thread
                    QtCore.QMetaObject.invokeMethod(
                        self, "_on_verification_error",
                        QtCore.Qt.QueuedConnection,
                        QtCore.Q_ARG(str, str(e))
                    )
            
            # Chạy coroutine
            loop.run_until_complete(verify_code())
            loop.close()
            
        except Exception as e:
            logger.error(f"Lỗi thread xác thực OTP: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Thông báo lỗi về UI thread
            QtCore.QMetaObject.invokeMethod(
                self, "_on_verification_error",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, str(e))
            )
    
    def _on_verification_success(self):
        """Xử lý khi xác thực thành công"""
        # Dừng đếm ngược
        if hasattr(self, 'countdown_timer') and self.countdown_timer.isActive():
            self.countdown_timer.stop()
        
        # Hiển thị thông báo
        QtWidgets.QMessageBox.information(
            self,
            "Thành công",
            "Xác thực Telethon API thành công!"
        )
        
        # Phát tín hiệu thành công
        self.verificationSuccess.emit()
        
        # Đóng dialog
        self.accept()
    
    def _on_verification_error(self, error_message):
        """
        Xử lý khi xác thực thất bại
        
        Args:
            error_message: Thông báo lỗi
        """
        # Hiển thị thông báo lỗi
        QtWidgets.QMessageBox.critical(
            self,
            "Lỗi xác thực",
            f"Không thể xác thực Telethon API: {error_message}"
        )
        
        # Bật lại UI
        for field in self.otp_fields:
            field.setEnabled(True)
            field.clear()
        self.resend_button.setEnabled(True)
        
        # Focus vào ô đầu tiên
        if self.otp_fields:
            self.otp_fields[0].setFocus()
    
    def resend_otp(self):
        """Gửi lại mã OTP"""
        # Vô hiệu hóa nút
        self.resend_button.setEnabled(False)
        
        # Xóa các ô OTP
        for field in self.otp_fields:
            field.clear()
        
        # Tạo thread gửi lại OTP
        resend_thread = threading.Thread(target=self._resend_otp_thread)
        resend_thread.daemon = True
        resend_thread.start()
    
    def _resend_otp_thread(self):
        """Thread gửi lại OTP"""
        try:
            from utils.otp_manager import TelethonSessionManager
            
            # Tạo session manager
            session_manager = TelethonSessionManager()
            
            # Tạo client
            client = session_manager.create_client(self.api_id, self.api_hash)
            
            # Tạo event loop mới
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Định nghĩa coroutine gửi lại mã
            async def resend_code():
                try:
                    # Kết nối
                    await client.connect()
                    
                    # Gửi lại mã
                    await client.send_code_request(self.phone)
                    
                    # Thông báo thành công về UI thread
                    QtCore.QMetaObject.invokeMethod(
                        self, "_on_resend_success",
                        QtCore.Qt.QueuedConnection
                    )
                    
                except Exception as e:
                    logger.error(f"Lỗi gửi lại OTP: {str(e)}")
                    
                    # Thông báo lỗi về UI thread
                    QtCore.QMetaObject.invokeMethod(
                        self, "_on_resend_error",
                        QtCore.Qt.QueuedConnection,
                        QtCore.Q_ARG(str, str(e))
                    )
            
            # Chạy coroutine
            loop.run_until_complete(resend_code())
            loop.close()
            
        except Exception as e:
            logger.error(f"Lỗi thread gửi lại OTP: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Thông báo lỗi về UI thread
            QtCore.QMetaObject.invokeMethod(
                self, "_on_resend_error",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, str(e))
            )
    
    def _on_resend_success(self):
        """Xử lý khi gửi lại mã thành công"""
        # Hiển thị thông báo
        QtWidgets.QMessageBox.information(
            self,
            "Đã gửi lại mã",
            f"Đã gửi lại mã xác thực đến số điện thoại {self.phone}."
        )
        
        # Reset thời gian hết hạn
        self.remaining_seconds = 5 * 60
        
        # Bắt đầu đếm ngược
        if hasattr(self, 'countdown_timer'):
            if not self.countdown_timer.isActive():
                self.countdown_timer.start(1000)
        else:
            self.countdown_timer = QtCore.QTimer(self)
            self.countdown_timer.timeout.connect(self.update_countdown)
            self.countdown_timer.start(1000)
        
        # Focus vào ô đầu tiên
        if self.otp_fields:
            self.otp_fields[0].setFocus()
    
    def _on_resend_error(self, error_message):
        """
        Xử lý khi gửi lại mã thất bại
        
        Args:
            error_message: Thông báo lỗi
        """
        # Hiển thị thông báo lỗi
        QtWidgets.QMessageBox.critical(
            self,
            "Lỗi gửi lại mã",
            f"Không thể gửi lại mã xác thực: {error_message}"
        )
        
        # Bật lại nút gửi lại
        self.resend_button.setEnabled(True)
    
    def closeEvent(self, event):
        """
        Xử lý khi đóng dialog
        
        Args:
            event: Sự kiện đóng
        """
        # Dừng đếm ngược
        if hasattr(self, 'countdown_timer') and self.countdown_timer.isActive():
            self.countdown_timer.stop()
        
        # Chấp nhận sự kiện đóng
        event.accept()
