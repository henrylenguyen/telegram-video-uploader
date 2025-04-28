"""
Module xử lý giao tiếp với Telethon API.
"""
import os
import sys
import logging
import asyncio
import traceback
import configparser
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class TelethonAPI:
    """
    Lớp xử lý giao tiếp với Telethon API
    """
    
    def __init__(self, api_id=None, api_hash=None, phone=None):
        """
        Khởi tạo lớp TelethonAPI
        
        Args:
            api_id (str, optional): API ID của Telethon
            api_hash (str, optional): API Hash của Telethon
            phone (str, optional): Số điện thoại đã đăng ký với Telegram
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.client = None
        self.loop = None
        self.connected = False
        self.authenticated = False
        
        # Nạp cấu hình nếu chưa được cung cấp
        if not all([self.api_id, self.api_hash, self.phone]):
            self._load_config()
    
    def _load_config(self):
        """Nạp cấu hình từ file config.ini"""
        try:
            # Lấy đường dẫn đến file cấu hình
            app_root = str(Path(__file__).parent.parent.parent.parent)
            config_path = os.path.join(app_root, "config.ini")
            
            if os.path.exists(config_path):
                config = configparser.ConfigParser()
                with open(config_path, 'r', encoding='utf-8') as f:
                    config.read_file(f)
                
                # Nạp cấu hình Telethon
                if 'TELETHON' in config:
                    if not self.api_id and 'api_id' in config['TELETHON']:
                        self.api_id = config['TELETHON']['api_id']
                    
                    if not self.api_hash and 'api_hash' in config['TELETHON']:
                        self.api_hash = config['TELETHON']['api_hash']
                    
                    if not self.phone and 'phone' in config['TELETHON']:
                        self.phone = config['TELETHON']['phone']
                    
                    # Kiểm tra xem đã xác thực OTP chưa
                    if 'otp_verified' in config['TELETHON']:
                        self.authenticated = config.getboolean('TELETHON', 'otp_verified', fallback=False)
        except Exception as e:
            logger.error(f"Lỗi khi đọc cấu hình: {str(e)}")
            logger.error(traceback.format_exc())
    
    def connect(self):
        """
        Kết nối đến Telethon API
        
        Returns:
            bool: True nếu kết nối thành công, False nếu thất bại
        """
        # Kiểm tra thông tin cấu hình
        if not all([self.api_id, self.api_hash, self.phone]):
            logger.error("Thiếu thông tin cấu hình Telethon API")
            return False
        
        try:
            # Import thư viện Telethon
            from telethon import TelegramClient
            import telethon.errors as telethon_errors
            
            # Tạo thư mục lưu session
            app_root = str(Path(__file__).parent.parent.parent.parent)
            session_dir = os.path.join(app_root, "data", "sessions")
            os.makedirs(session_dir, exist_ok=True)
            
            # Tên file session
            session_name = os.path.join(session_dir, f"telethon_{self.phone.replace('+', '')}")
            
            # Khởi tạo client
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            self.client = TelegramClient(
                session_name,
                int(self.api_id),
                self.api_hash,
                loop=self.loop
            )
            
            # Kết nối đến Telegram
            self.loop.run_until_complete(self.client.connect())
            
            # Kiểm tra đã đăng nhập chưa
            if self.loop.run_until_complete(self.client.is_user_authorized()):
                self.connected = True
                self.authenticated = True
                me = self.loop.run_until_complete(self.client.get_me())
                logger.info(f"Đã kết nối đến tài khoản Telegram {me.username if me.username else me.phone}")
                return True
            else:
                # Nếu chưa đăng nhập, kiểm tra xem đã xác thực OTP chưa
                if self.authenticated:
                    # Nếu đã xác thực OTP nhưng vẫn chưa đăng nhập, thử đăng nhập lại
                    logger.warning("Đã xác thực OTP nhưng chưa đăng nhập. Cần xác thực lại")
                    
                    # Cập nhật trạng thái xác thực
                    self._update_auth_status(False)
                    self.authenticated = False
                
                self.connected = False
                return False
        except ImportError:
            logger.error("Thư viện Telethon chưa được cài đặt")
            return False
        except Exception as e:
            logger.error(f"Lỗi khi kết nối đến Telethon API: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def disconnect(self):
        """
        Ngắt kết nối khỏi Telethon API
        
        Returns:
            bool: True nếu ngắt kết nối thành công, False nếu thất bại
        """
        if self.client is None:
            return True
        
        try:
            # Ngắt kết nối
            self.loop.run_until_complete(self.client.disconnect())
            self.connected = False
            return True
        except Exception as e:
            logger.error(f"Lỗi khi ngắt kết nối khỏi Telethon API: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def _update_auth_status(self, status):
        """
        Cập nhật trạng thái xác thực OTP trong file cấu hình
        
        Args:
            status (bool): Trạng thái xác thực OTP (True: đã xác thực, False: chưa xác thực)
            
        Returns:
            bool: True nếu cập nhật thành công, False nếu thất bại
        """
        try:
            # Lấy đường dẫn đến file cấu hình
            app_root = str(Path(__file__).parent.parent.parent.parent)
            config_path = os.path.join(app_root, "config.ini")
            
            if os.path.exists(config_path):
                config = configparser.ConfigParser()
                with open(config_path, 'r', encoding='utf-8') as f:
                    config.read_file(f)
                
                # Cập nhật trạng thái xác thực OTP
                if 'TELETHON' not in config:
                    config['TELETHON'] = {}
                
                config['TELETHON']['otp_verified'] = 'true' if status else 'false'
                
                # Lưu cấu hình
                with open(config_path, 'w', encoding='utf-8') as f:
                    config.write(f)
                
                return True
            
            return False
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật trạng thái xác thực OTP: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def upload_file(self, file_path, caption=None, progress_callback=None):
        """
        Tải file lên Telegram
        
        Args:
            file_path (str): Đường dẫn đến file cần tải lên
            caption (str, optional): Chú thích cho file
            progress_callback (callable, optional): Callback function để theo dõi tiến trình tải lên
            
        Returns:
            dict: Thông tin của file đã tải lên nếu thành công, None nếu thất bại
        """
        if not self.connected or not self.authenticated or self.client is None:
            logger.error("Chưa kết nối hoặc xác thực Telethon API")
            return None
        
        try:
            # Kiểm tra đường dẫn file
            if not os.path.exists(file_path):
                logger.error(f"File {file_path} không tồn tại")
                return None
            
            # Kiểm tra kích thước file
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            # Xác định loại file dựa vào extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Hàm định dạng kích thước file để hiển thị
            def format_size(size):
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if abs(size) < 1024.0:
                        return f"{size:.2f} {unit}"
                    size /= 1024.0
                return f"{size:.2f} TB"
            
            # Hàm callback để theo dõi tiến trình
            last_update_time = [datetime.now()]
            last_percentage = [0]
            
            # Tạo callback function để cập nhật tiến trình
            async def _progress_callback(current, total):
                # Tính toán phần trăm
                percentage = int(current * 100 / total)
                
                # Kiểm tra xem có cần cập nhật tiến trình không (tránh cập nhật quá nhiều)
                current_time = datetime.now()
                if (percentage > last_percentage[0] and 
                    (percentage % 5 == 0 or  # Mỗi 5%
                     (current_time - last_update_time[0]).total_seconds() > 1)):  # Hoặc mỗi giây
                    
                    # Cập nhật thời gian và phần trăm cuối cùng
                    last_update_time[0] = current_time
                    last_percentage[0] = percentage
                    
                    # Gọi callback function nếu có
                    if progress_callback:
                        progress_callback(current, total, percentage)
                    
                    # Ghi log
                    logger.info(f"Đang tải lên {file_name}: {percentage}% ({format_size(current)}/{format_size(total)})")
            
            # Lấy tham số cho file
            file_params = {
                "file": file_path,
                "caption": caption if caption else f"File: {file_name}\nKích thước: {format_size(file_size)}"
            }
            
            # Hàm progress chỉ được hỗ trợ khi tải lên dưới dạng media
            if progress_callback:
                file_params["progress_callback"] = _progress_callback
            
            # Upload file tùy theo loại
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                # Upload dưới dạng ảnh
                result = self.loop.run_until_complete(
                    self.client.send_file(
                        'me',  # Gửi cho chính mình trước
                        **file_params
                    )
                )
            elif file_ext in ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv']:
                # Upload dưới dạng video
                result = self.loop.run_until_complete(
                    self.client.send_file(
                        'me',  # Gửi cho chính mình trước
                        **file_params,
                        supports_streaming=True
                    )
                )
            else:
                # Upload dưới dạng document
                result = self.loop.run_until_complete(
                    self.client.send_file(
                        'me',  # Gửi cho chính mình trước
                        **file_params
                    )
                )
            
            # Trả về thông tin file đã tải lên
            return {
                'id': result.id,
                'file_name': file_name,
                'file_size': file_size,
                'upload_time': datetime.now().isoformat(),
                'media_type': result.media.__class__.__name__ if hasattr(result, 'media') else 'Unknown'
            }
        except Exception as e:
            logger.error(f"Lỗi khi tải file lên Telethon: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def forward_to_chat(self, message_id, chat_id):
        """
        Chuyển tiếp tin nhắn từ 'me' đến chat khác
        
        Args:
            message_id (int): ID của tin nhắn cần chuyển tiếp
            chat_id (str): ID của chat đích
            
        Returns:
            bool: True nếu chuyển tiếp thành công, False nếu thất bại
        """
        if not self.connected or not self.authenticated or self.client is None:
            logger.error("Chưa kết nối hoặc xác thực Telethon API")
            return False
        
        try:
            # Chuyển tiếp tin nhắn
            self.loop.run_until_complete(
                self.client.forward_messages(
                    chat_id,
                    message_id,
                    'me'
                )
            )
            
            return True
        except Exception as e:
            logger.error(f"Lỗi khi chuyển tiếp tin nhắn: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def get_chat_info(self, chat_id):
        """
        Lấy thông tin của chat
        
        Args:
            chat_id (str): ID của chat cần lấy thông tin
            
        Returns:
            dict: Thông tin chat nếu thành công, None nếu thất bại
        """
        if not self.connected or not self.authenticated or self.client is None:
            logger.error("Chưa kết nối hoặc xác thực Telethon API")
            return None
        
        try:
            # Lấy thông tin chat
            entity = self.loop.run_until_complete(self.client.get_entity(chat_id))
            
            # Chuyển đổi entity thành dict
            return {
                'id': entity.id,
                'title': getattr(entity, 'title', None),
                'username': getattr(entity, 'username', None),
                'first_name': getattr(entity, 'first_name', None),
                'last_name': getattr(entity, 'last_name', None),
                'type': entity.__class__.__name__
            }
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin chat: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def get_me(self):
        """
        Lấy thông tin tài khoản đã đăng nhập
        
        Returns:
            dict: Thông tin tài khoản nếu thành công, None nếu thất bại
        """
        if not self.connected or self.client is None:
            logger.error("Chưa kết nối Telethon API")
            return None
        
        try:
            # Lấy thông tin tài khoản
            me = self.loop.run_until_complete(self.client.get_me())
            
            # Chuyển đổi entity thành dict
            return {
                'id': me.id,
                'username': me.username,
                'first_name': me.first_name,
                'last_name': me.last_name,
                'phone': me.phone,
                'is_bot': me.bot
            }
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin tài khoản: {str(e)}")
            logger.error(traceback.format_exc())
            return None