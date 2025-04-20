"""
Module quản lý kết nối với Telegram Bot API
"""
import requests
import logging
import json
import os
from pathlib import Path
import traceback

logger = logging.getLogger(__name__)

class TelegramAPI:
    """
    Lớp xử lý giao tiếp với Telegram Bot API
    """
    
    API_URL = "https://api.telegram.org/bot{token}/{method}"
    
    def __init__(self, bot_token=None):
        """
        Khởi tạo API Telegram
        
        Args:
            bot_token (str): Token của Telegram Bot
        """
        self.bot_token = bot_token
        self.connected = False
        self.bot_info = None
    
    def connect(self, bot_token):
        """
        Kết nối với Telegram Bot API
        
        Args:
            bot_token (str): Token của Telegram Bot
            
        Returns:
            bool: Kết nối thành công hay không
        """
        self.bot_token = bot_token
        
        try:
            # Kiểm tra kết nối bằng cách gọi getMe
            response = self._make_request("getMe")
            
            if response and response.get("ok"):
                self.connected = True
                self.bot_info = response.get("result", {})
                logger.info(f"Đã kết nối với bot @{self.bot_info.get('username')}")
                return True
            else:
                self.connected = False
                error_desc = response.get("description", "Lỗi không xác định") if response else "Không có phản hồi"
                logger.error(f"Lỗi kết nối Telegram: {error_desc}")
                return False
        except Exception as e:
            self.connected = False
            logger.error(f"Lỗi kết nối Telegram: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def disconnect(self):
        """Ngắt kết nối với Telegram Bot API"""
        self.connected = False
        self.bot_token = None
        self.bot_info = None
    
    def test_connection(self, chat_id, delete_after=None):
        """
        Kiểm tra kết nối bằng cách gửi tin nhắn thử nghiệm
        
        Args:
            chat_id (str): ID của chat
            delete_after (int): Xóa tin nhắn sau bao nhiêu giây (None để không xóa)
            
        Returns:
            dict: Thông tin bot nếu thành công, None nếu thất bại
        """
        if not self.connected or not self.bot_token:
            logger.error("Chưa kết nối với Telegram Bot API")
            return None
        
        try:
            # Gửi tin nhắn thử nghiệm
            test_message = "✅ Kiểm tra kết nối thành công!"
            response = self._make_request("sendMessage", {
                "chat_id": chat_id,
                "text": test_message,
                "disable_notification": True
            })
            
            if response and response.get("ok"):
                logger.info(f"Kiểm tra kết nối thành công đến chat {chat_id}")
                
                # Nếu cần xóa tin nhắn sau đó
                if delete_after and delete_after > 0:
                    message_id = response.get("result", {}).get("message_id")
                    if message_id:
                        # Xóa tin nhắn sau delete_after giây
                        import threading
                        import time
                        
                        def delete_message_later():
                            time.sleep(delete_after)
                            self.delete_message(chat_id, message_id)
                        
                        # Tạo thread xóa tin nhắn
                        delete_thread = threading.Thread(target=delete_message_later)
                        delete_thread.daemon = True
                        delete_thread.start()
                
                return self.bot_info
            else:
                error_desc = response.get("description", "Lỗi không xác định") if response else "Không có phản hồi"
                logger.error(f"Kiểm tra kết nối thất bại: {error_desc}")
                return None
        except Exception as e:
            logger.error(f"Lỗi kiểm tra kết nối: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def delete_message(self, chat_id, message_id):
        """
        Xóa tin nhắn
        
        Args:
            chat_id (str): ID của chat
            message_id (int): ID của tin nhắn
            
        Returns:
            bool: Xóa thành công hay không
        """
        if not self.connected or not self.bot_token:
            logger.error("Chưa kết nối với Telegram Bot API")
            return False
        
        try:
            response = self._make_request("deleteMessage", {
                "chat_id": chat_id,
                "message_id": message_id
            })
            
            if response and response.get("ok"):
                logger.info(f"Đã xóa tin nhắn {message_id} trong chat {chat_id}")
                return True
            else:
                error_desc = response.get("description", "Lỗi không xác định") if response else "Không có phản hồi"
                logger.error(f"Không thể xóa tin nhắn: {error_desc}")
                return False
        except Exception as e:
            logger.error(f"Lỗi khi xóa tin nhắn: {str(e)}")
            return False
    
    def _make_request(self, method, params=None):
        """
        Gửi yêu cầu đến Telegram Bot API
        
        Args:
            method (str): Phương thức API
            params (dict): Tham số cho phương thức
            
        Returns:
            dict: Kết quả từ API hoặc None nếu có lỗi
        """
        if not self.bot_token:
            logger.error("Chưa cung cấp bot token")
            return None
        
        url = self.API_URL.format(token=self.bot_token, method=method)
        
        try:
            response = requests.post(url, json=params if params else {}, timeout=30)
            return response.json()
        except Exception as e:
            logger.error(f"Lỗi khi gọi API {method}: {str(e)}")
            return None
