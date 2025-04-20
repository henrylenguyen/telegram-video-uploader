"""
Xử lý OTP cho UI Telegram
"""
import logging
import os
import threading
import asyncio
import traceback
from PyQt5 import QtWidgets, QtCore

logger = logging.getLogger(__name__)

def request_telethon_code(self):
    """Yêu cầu mã xác thực OTP từ Telethon"""
    # Kiểm tra dữ liệu đầu vào
    api_id = self.apiIdEdit.text().strip()
    api_hash = self.apiHashEdit.text().strip()
    phone = self.phoneEdit.text().strip()
    
    # Kiểm tra dữ liệu
    is_valid, error_message = self.validate_config("TELETHON")
    if not is_valid:
        QtWidgets.QMessageBox.warning(self, "Lỗi", error_message)
        return
    
    # Vô hiệu hóa nút
    self.requestOtpButton.setEnabled(False)
    self.requestOtpButton.setText("Đang gửi mã xác thực...")
    
    # Tạo thread gửi OTP
    otp_thread = threading.Thread(target=self._request_otp_thread, args=(api_id, api_hash, phone))
    otp_thread.daemon = True
    otp_thread.start()

def _request_otp_thread(self, api_id, api_hash, phone):
    """
    Thread gửi yêu cầu OTP
    
    Args:
        api_id: API ID
        api_hash: API Hash
        phone: Số điện thoại
    """
    try:
        # Lưu cấu hình trước
        self.save_config("TELETHON", {
            "api_id": api_id,
            "api_hash": api_hash,
            "phone": phone,
            "use_telethon": "true",
            "otp_verified": "false"
        })
        
        from utils.otp_manager import OTPManager
        
        # Tạo OTP Manager
        otp_manager = OTPManager()
        
        # Kiểm tra giới hạn yêu cầu OTP
        can_request, message = otp_manager.check_request_limits()
        if not can_request:
            # Kích hoạt UI thread để hiển thị thông báo
            QtCore.QMetaObject.invokeMethod(
                self, "_show_otp_limit_error",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, message)
            )
            return
        
        # Ghi nhận yêu cầu OTP
        otp_manager.record_request()
        
        # Kích hoạt UI thread để hiển thị modal OTP
        QtCore.QMetaObject.invokeMethod(
            self, "_show_otp_modal",
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(str, api_id),
            QtCore.Q_ARG(str, api_hash),
            QtCore.Q_ARG(str, phone)
        )
    except Exception as e:
        logger.error(f"Lỗi khi yêu cầu OTP: {str(e)}")
        logger.error(traceback.format_exc())
        # Kích hoạt UI thread để hiển thị lỗi
        QtCore.QMetaObject.invokeMethod(
            self, "_show_otp_request_error",
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(str, str(e))
        )
    finally:
        # Kích hoạt UI thread để bật lại nút
        QtCore.QMetaObject.invokeMethod(
            self, "_enable_otp_button",
            QtCore.Qt.QueuedConnection
        )

def _show_otp_limit_error(self, message):
    """Hiển thị lỗi giới hạn OTP"""
    QtWidgets.QMessageBox.warning(self, "Giới hạn yêu cầu OTP", message)

def _show_otp_request_error(self, error_message):
    """Hiển thị lỗi yêu cầu OTP"""
    QtWidgets.QMessageBox.critical(self, "Lỗi yêu cầu OTP", f"Không thể gửi mã OTP: {error_message}")

def _enable_otp_button(self):
    """Bật lại nút yêu cầu OTP"""
    self.requestOtpButton.setEnabled(True)
    self.requestOtpButton.setText("Gửi mã xác thực")

def _show_otp_modal(self, api_id, api_hash, phone):
    """Hiển thị modal nhập OTP"""
    from ui.telegram.telegram_ui_otp_modal import OTPModal
    
    try:
        # Tạo dialog xác thực OTP
        otp_dialog = OTPModal(self, api_id, api_hash, phone)
        
        # Kết nối sự kiện khi xác thực thành công
        otp_dialog.verificationSuccess.connect(self.on_otp_verification_success)
        
        # Hiển thị dialog
        otp_dialog.exec_()
    except Exception as e:
        logger.error(f"Lỗi khi hiển thị modal OTP: {str(e)}")
        logger.error(traceback.format_exc())
        QtWidgets.QMessageBox.critical(self, "Lỗi", f"Không thể hiển thị màn hình xác thực OTP: {str(e)}")

def verify_otp_code(self, otp_code):
    """
    Xác thực mã OTP
    
    Args:
        otp_code: Mã OTP cần xác thực
    """
    # Lấy thông tin cấu hình
    api_id = self.apiIdEdit.text().strip()
    api_hash = self.apiHashEdit.text().strip()
    phone = self.phoneEdit.text().strip()
    
    # Tạo thread xác thực OTP
    verify_thread = threading.Thread(target=self._verify_otp_thread, args=(api_id, api_hash, phone, otp_code))
    verify_thread.daemon = True
    verify_thread.start()

def _verify_otp_thread(self, api_id, api_hash, phone, otp_code):
    """
    Thread xác thực OTP
    
    Args:
        api_id: API ID
        api_hash: API Hash
        phone: Số điện thoại
        otp_code: Mã OTP
    """
    try:
        from utils.otp_manager import TelethonSessionManager
        
        # Tạo session manager
        session_manager = TelethonSessionManager()
        
        # Tạo client
        client = session_manager.create_client(api_id, api_hash)
        
        # Xác thực OTP
        async def verify_code():
            try:
                # Kết nối
                await client.connect()
                
                # Kiểm tra nếu đã xác thực
                if await client.is_user_authorized():
                    logger.info("Người dùng đã được xác thực")
                    # Cập nhật trạng thái xác thực trong cấu hình
                    QtCore.QMetaObject.invokeMethod(
                        self, "_update_otp_verified_status",
                        QtCore.Qt.QueuedConnection,
                        QtCore.Q_ARG(bool, True)
                    )
                else:
                    # Xác thực mã
                    await client.sign_in(phone, code=otp_code)
                    
                    # Xác thực thành công
                    QtCore.QMetaObject.invokeMethod(
                        self, "_update_otp_verified_status",
                        QtCore.Qt.QueuedConnection,
                        QtCore.Q_ARG(bool, True)
                    )
                
                # Ngắt kết nối
                await client.disconnect()
                
            except Exception as e:
                logger.error(f"Lỗi xác thực OTP: {str(e)}")
                # Thông báo lỗi về UI thread
                QtCore.QMetaObject.invokeMethod(
                    self, "_show_otp_verification_error",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, str(e))
                )
        
        # Tạo event loop và chạy coroutine
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(verify_code())
        loop.close()
        
    except Exception as e:
        logger.error(f"Lỗi xác thực OTP: {str(e)}")
        logger.error(traceback.format_exc())
        # Thông báo lỗi về UI thread
        QtCore.QMetaObject.invokeMethod(
            self, "_show_otp_verification_error",
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(str, str(e))
        )

def _show_otp_verification_error(self, error_message):
    """Hiển thị lỗi xác thực OTP"""
    QtWidgets.QMessageBox.critical(self, "Lỗi xác thực OTP", f"Không thể xác thực OTP: {error_message}")

def _update_otp_verified_status(self, verified):
    """Cập nhật trạng thái xác thực OTP trong cấu hình"""
    try:
        # Cập nhật cấu hình
        self.save_config("TELETHON", {
            "otp_verified": "true" if verified else "false"
        })
        
        # Cập nhật giao diện
        if verified:
            QtWidgets.QMessageBox.information(self, "Xác thực thành công", 
                "Xác thực Telethon API thành công! Bạn có thể sử dụng tính năng tải lên video không giới hạn kích thước.")
            
            # Gọi phương thức xử lý khi xác thực thành công
            self.on_otp_verification_success()
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật trạng thái xác thực OTP: {str(e)}")
        logger.error(traceback.format_exc())

def on_otp_verification_success(self):
    """Xử lý khi xác thực OTP thành công"""
    # Cập nhật trạng thái kết nối
    self.telethon_connected = True
    
    # Cập nhật giao diện
    self.requestOtpButton.setText("Đã xác thực")
    self.requestOtpButton.setEnabled(False)
    self.requestOtpButton.setStyleSheet("""
        QPushButton {
            background-color: #10B981;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px;
            font-size: 14px;
        }
    """)
    
    # Phát tín hiệu
    self.configSaved.emit(True)
