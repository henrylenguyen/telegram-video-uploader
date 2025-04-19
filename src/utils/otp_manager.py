"""
Module quản lý xác thực OTP cho Telethon
"""
import os
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger("OTPManager")

class OTPManager:
    """
    Quản lý xác thực OTP cho Telethon API
    - Theo dõi và quản lý giới hạn yêu cầu OTP
    - Đảm bảo tuân thủ thời gian chờ giữa các lần yêu cầu
    - Lưu trữ thông tin OTP và trạng thái xác thực
    """
    
    def __init__(self, app_dir=None):
        """
        Khởi tạo OTP Manager
        
        Args:
            app_dir (str): Thư mục ứng dụng (nếu None, sử dụng thư mục hiện tại)
        """
        # Xác định thư mục gốc ứng dụng
        if app_dir:
            self.app_dir = app_dir
        else:
            self.app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Thư mục lưu trữ dữ liệu
        self.data_dir = os.path.join(self.app_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # File lưu trữ giới hạn OTP
        self.limits_file = os.path.join(self.data_dir, "otp_limits.json")
        
        # Cấu hình giới hạn
        self.max_daily_requests = 3  # Số lần tối đa mỗi ngày
        self.cooldown_period = 60    # Thời gian chờ giữa các lần yêu cầu (giây)
        
        # Dữ liệu giới hạn hiện tại
        self.limits_data = self._load_limits()
    
    def _load_limits(self):
        """
        Tải thông tin giới hạn từ file
        
        Returns:
            dict: Thông tin giới hạn
        """
        # Thông tin mặc định
        default_data = {
            "last_request_time": None,
            "requests_count": 0,
            "reset_date": None
        }
        
        # Tải từ file nếu có
        if os.path.exists(self.limits_file):
            try:
                with open(self.limits_file, "r") as f:
                    data = json.load(f)
                return data
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Lỗi tải file giới hạn OTP: {str(e)}")
        
        return default_data
    
    def _save_limits(self):
        """Lưu thông tin giới hạn vào file"""
        try:
            with open(self.limits_file, "w") as f:
                json.dump(self.limits_data, f)
        except IOError as e:
            logger.error(f"Lỗi lưu file giới hạn OTP: {str(e)}")
    
    def check_request_limits(self):
        """
        Kiểm tra giới hạn yêu cầu OTP
        
        Returns:
            tuple: (can_request, message) - can_request: bool, message: str nếu có lỗi
        """
        # Kiểm tra nếu cần reset đếm
        current_date = datetime.now().strftime("%Y-%m-%d")
        if self.limits_data["reset_date"] != current_date:
            # Reset đếm cho ngày mới
            self.limits_data["reset_date"] = current_date
            self.limits_data["requests_count"] = 0
            self._save_limits()
        
        # Kiểm tra số lần yêu cầu trong ngày
        if self.limits_data["requests_count"] >= self.max_daily_requests:
            return False, f"Bạn đã vượt quá giới hạn yêu cầu mã OTP ({self.max_daily_requests} lần) trong 24 giờ.\nVui lòng thử lại vào ngày mai."
        
        # Kiểm tra thời gian chờ giữa các lần yêu cầu
        if self.limits_data["last_request_time"]:
            last_time = datetime.fromisoformat(self.limits_data["last_request_time"])
            elapsed = (datetime.now() - last_time).total_seconds()
            
            if elapsed < self.cooldown_period:
                remaining = int(self.cooldown_period - elapsed)
                return False, f"Vui lòng đợi {remaining} giây trước khi yêu cầu mã mới."
        
        return True, None
    
    def record_request(self):
        """
        Ghi nhận một lần yêu cầu OTP
        
        Returns:
            int: Số lần đã yêu cầu trong ngày
        """
        # Kiểm tra nếu cần reset đếm
        current_date = datetime.now().strftime("%Y-%m-%d")
        if self.limits_data["reset_date"] != current_date:
            # Reset đếm cho ngày mới
            self.limits_data["reset_date"] = current_date
            self.limits_data["requests_count"] = 0
        
        # Cập nhật thông tin giới hạn
        self.limits_data["last_request_time"] = datetime.now().isoformat()
        self.limits_data["requests_count"] += 1
        
        # Lưu thông tin giới hạn
        self._save_limits()
        
        return self.limits_data["requests_count"]
    
    def get_current_limits(self):
        """
        Lấy thông tin giới hạn hiện tại
        
        Returns:
            dict: Thông tin giới hạn
        """
        # Kiểm tra nếu cần reset đếm
        current_date = datetime.now().strftime("%Y-%m-%d")
        if self.limits_data["reset_date"] != current_date:
            # Reset đếm cho ngày mới
            self.limits_data["reset_date"] = current_date
            self.limits_data["requests_count"] = 0
            self._save_limits()
        
        return {
            "requests_count": self.limits_data["requests_count"],
            "max_requests": self.max_daily_requests,
            "cooldown_period": self.cooldown_period,
            "cooldown_remaining": self._get_cooldown_remaining()
        }
    
    def _get_cooldown_remaining(self):
        """
        Tính thời gian còn lại cho cooldown
        
        Returns:
            int: Số giây còn lại, hoặc 0 nếu không trong cooldown
        """
        if not self.limits_data["last_request_time"]:
            return 0
        
        last_time = datetime.fromisoformat(self.limits_data["last_request_time"])
        elapsed = (datetime.now() - last_time).total_seconds()
        
        if elapsed < self.cooldown_period:
            return int(self.cooldown_period - elapsed)
        
        return 0
    
    def reset_limits(self):
        """Reset lại tất cả giới hạn (chỉ dùng cho mục đích kiểm thử)"""
        self.limits_data = {
            "last_request_time": None,
            "requests_count": 0,
            "reset_date": None
        }
        self._save_limits()

class TelethonSessionManager:
    """
    Quản lý phiên Telethon và dữ liệu xác thực
    """
    def __init__(self, app_dir=None):
        """
        Khởi tạo Session Manager
        
        Args:
            app_dir (str): Thư mục ứng dụng (nếu None, sử dụng thư mục hiện tại)
        """
        # Xác định thư mục gốc ứng dụng
        if app_dir:
            self.app_dir = app_dir
        else:
            self.app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Đường dẫn session
        self.session_path = os.path.join(self.app_dir, "telegram_uploader")
    
    def create_client(self, api_id, api_hash):
        """
        Tạo đối tượng TelegramClient
        
        Args:
            api_id (str): API ID
            api_hash (str): API Hash
        
        Returns:
            TelegramClient: Đối tượng TelegramClient
        """
        try:
            from telethon import TelegramClient
            return TelegramClient(self.session_path, api_id, api_hash)
        except ImportError:
            logger.error("Không thể import Telethon. Vui lòng cài đặt: pip install telethon")
            return None
    
    def is_session_available(self):
        """
        Kiểm tra xem đã có session Telethon chưa
        
        Returns:
            bool: True nếu đã có file session
        """
        session_file = f"{self.session_path}.session"
        return os.path.exists(session_file)
    
    def remove_session(self):
        """Xóa session hiện tại (đăng xuất)"""
        session_file = f"{self.session_path}.session"
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
                return True
            except OSError as e:
                logger.error(f"Lỗi xóa file session: {str(e)}")
                return False
        return True 