"""
Xử lý sự kiện cho UI Telegram
"""
import logging
import os
from PyQt5 import QtWidgets, QtCore
import traceback

logger = logging.getLogger(__name__)

def connect_signals(self):
    """Kết nối các sự kiện trong dialog cấu hình"""
    # Kết nối nút kiểm tra kết nối Telegram Bot API
    if hasattr(self, 'btnCheckConnection') and self.btnCheckConnection:
        self.btnCheckConnection.clicked.connect(self.check_telegram_connection)
    
    # Kết nối nút yêu cầu mã OTP Telethon
    if hasattr(self, 'requestOtpButton') and self.requestOtpButton:
        self.requestOtpButton.clicked.connect(self.request_telethon_code)
    
    # Kết nối sự kiện thay đổi tab
    if hasattr(self, 'tabWidget') and self.tabWidget:
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

def on_check_connection_clicked(self):
    """
    Xử lý sự kiện khi người dùng nhấn nút kiểm tra kết nối
    """
    try:
        # Lấy thông tin token và chat ID
        bot_token = self.botTokenEdit.text().strip()
        chat_id = self.chatIdEdit.text().strip()
        
        # Kiểm tra dữ liệu đầu vào
        if not bot_token:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Vui lòng nhập Bot Token!")
            return
        
        if not chat_id:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Vui lòng nhập Chat ID!")
            return
        
        # Vô hiệu hóa nút và thay đổi text
        if hasattr(self, 'btnCheckConnection') and self.btnCheckConnection:
            self.btnCheckConnection.setEnabled(False)
            self.btnCheckConnection.setText("Đang kiểm tra...")
            
            # Tạo thread kiểm tra kết nối
            self.test_thread = TelegramTestThread(bot_token, chat_id, self.app)
            
            # Kết nối tín hiệu khi hoàn thành
            self.test_thread.resultReady.connect(self.on_telegram_check_result)
            
            # Bắt đầu thread
            logger.info(f"Bắt đầu kiểm tra kết nối với Telegram: {chat_id}")
            self.test_thread.start()
        else:
            logger.error("Không tìm thấy btnCheckConnection trong UI")
            QtWidgets.QMessageBox.warning(self, "Lỗi UI", "Không tìm thấy nút kiểm tra kết nối. Vui lòng thử lại sau.")
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra kết nối Telegram: {str(e)}")
        logger.error(traceback.format_exc())
        QtWidgets.QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi khi kiểm tra kết nối: {str(e)}")
        
        # Khôi phục trạng thái nút nếu có lỗi
        if hasattr(self, 'btnCheckConnection') and self.btnCheckConnection:
            self.btnCheckConnection.setEnabled(True)
            self.btnCheckConnection.setText("Kiểm tra kết nối")

def on_save_config_clicked(self):
    """
    Xử lý sự kiện khi người dùng nhấn nút lưu cấu hình
    """
    try:
        # Kiểm tra xem đã kết nối Telegram Bot thành công chưa
        if self.tabWidget.currentIndex() == 0 and not self.telegram_connected:
            reply = QtWidgets.QMessageBox.question(
                self,
                "Xác nhận lưu",
                "Bạn chưa kiểm tra kết nối Telegram Bot.\nBạn có chắc muốn lưu cấu hình này không?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            
            if reply == QtWidgets.QMessageBox.No:
                return
        
        # Lưu cấu hình dựa vào tab hiện tại
        config_type = "Telegram Bot API" if self.tabWidget.currentIndex() == 0 else "Telethon API"
        logger.info(f"Đang lưu cấu hình {config_type}")
        
        # Thực hiện lưu cấu hình
        success = self.save_config()
        
        if success:
            logger.info(f"Đã lưu cấu hình {config_type} thành công")
            QtWidgets.QMessageBox.information(
                self,
                "Thành công",
                f"Đã lưu cấu hình {config_type} thành công!"
            )
            
            # Phát tín hiệu đã lưu cấu hình
            self.configSaved.emit(True)
            
            # Đóng dialog
            self.accept()
        else:
            logger.error(f"Lỗi khi lưu cấu hình {config_type}")
            QtWidgets.QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể lưu cấu hình {config_type}. Vui lòng kiểm tra lại thông tin!"
            )
            
            # Phát tín hiệu lưu thất bại
            self.configSaved.emit(False)
    except Exception as e:
        logger.error(f"Lỗi khi xử lý sự kiện lưu cấu hình: {str(e)}")
        logger.error(traceback.format_exc())
        QtWidgets.QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi khi lưu cấu hình: {str(e)}")

def on_tab_changed(self, index):
    """Xử lý khi tab được thay đổi"""
    # Kích hoạt wizard step tương ứng với tab
    self.activate_wizard_step(index + 1)

def request_otp(self):
    """Xử lý khi nút 'Yêu cầu mã OTP' được nhấn"""
    try:
        # Lấy thông tin API ID, API Hash và số điện thoại
        api_id = self.apiIdEdit.text().strip()
        api_hash = self.apiHashEdit.text().strip()
        phone = self.phoneEdit.text().strip()
        
        # Kiểm tra dữ liệu đầu vào
        if not api_id or not api_hash or not phone:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin API ID, API Hash và số điện thoại!")
            return
        
        # Hiển thị thông báo đang xử lý
        self.requestOtpButton.setEnabled(False)
        self.requestOtpButton.setText("Đang gửi yêu cầu...")
        
        # Gọi hàm yêu cầu OTP từ Telethon
        self.request_telethon_code(api_id, api_hash, phone)
    except Exception as e:
        logger.error(f"Lỗi khi yêu cầu mã OTP: {str(e)}")
        QtWidgets.QMessageBox.critical(self, "Lỗi", f"Không thể yêu cầu mã OTP: {str(e)}")
        
        # Khôi phục trạng thái nút
        self.requestOtpButton.setEnabled(True)
        self.requestOtpButton.setText("Yêu cầu mã OTP")
