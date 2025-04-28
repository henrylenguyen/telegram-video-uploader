"""
Module xử lý giao tiếp với Telegram Bot API.
"""
import os
import sys
import time
import json
import logging
import requests
import traceback
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TelegramAPI:
    """
    Lớp xử lý giao tiếp với Telegram Bot API
    """
    
    def __init__(self, token=None):
        """
        Khởi tạo lớp TelegramAPI
        
        Args:
            token (str, optional): Token của bot Telegram
        """
        self.token = token
        self.base_url = None
        self.connected = False
        self.bot_info = None
        
        # Kết nối nếu có token
        if self.token:
            self.connect(self.token)
    
    def connect(self, token):
        """
        Kết nối đến Telegram Bot API
        
        Args:
            token (str): Token của bot Telegram
            
        Returns:
            bool: True nếu kết nối thành công, False nếu thất bại
        """
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
        # Kiểm tra kết nối
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("ok", False):
                    self.bot_info = data.get("result", {})
                    self.connected = True
                    logger.info(f"Kết nối thành công đến bot {self.bot_info.get('username', 'unknown')}")
                    return True
            
            # Nếu không kết nối được
            logger.error(f"Không thể kết nối đến bot: {response.text}")
            self.connected = False
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi kết nối đến Telegram API: {str(e)}")
            logger.error(traceback.format_exc())
            self.connected = False
            return False
    
    def test_connection(self, chat_id, delete_after=None):
        """
        Kiểm tra kết nối bằng cách gửi một tin nhắn đến chat
        
        Args:
            chat_id (str): ID của chat cần gửi tin nhắn
            delete_after (int, optional): Số giây sau khi gửi tin nhắn sẽ tự động xóa
            
        Returns:
            dict: Thông tin của bot nếu kết nối thành công, None nếu thất bại
        """
        if not self.connected or not self.token:
            logger.error("Chưa kết nối đến Telegram Bot API")
            return None
            
        try:
            # Tạo tin nhắn kiểm tra kết nối
            current_time = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            message = f"🔄 Kiểm tra kết nối Telegram\n\n⏱ Thời gian: {current_time}\n\n⚙️ Bot: @{self.bot_info.get('username', 'unknown')}\n\n✅ Kết nối thành công!"
            
            # Gửi tin nhắn
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("ok", False):
                    # Lấy message_id để xóa sau nếu cần
                    message_id = data.get("result", {}).get("message_id")
                    
                    # Xóa tin nhắn sau một khoảng thời gian nếu được yêu cầu
                    if delete_after and message_id:
                        # Lập lịch xóa tin nhắn sau delete_after giây
                        self._schedule_delete_message(chat_id, message_id, delete_after)
                    
                    return self.bot_info
            
            # Nếu không gửi được tin nhắn
            logger.error(f"Không thể gửi tin nhắn đến chat {chat_id}: {response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi gửi tin nhắn kiểm tra: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def _schedule_delete_message(self, chat_id, message_id, delay):
        """
        Lên lịch xóa tin nhắn sau một khoảng thời gian
        
        Args:
            chat_id (str): ID của chat chứa tin nhắn
            message_id (int): ID của tin nhắn cần xóa
            delay (int): Số giây sau khi sẽ xóa tin nhắn
        """
        import threading
        
        def delete_message():
            # Đợi delay giây
            time.sleep(delay)
            
            # Xóa tin nhắn
            try:
                requests.post(
                    f"{self.base_url}/deleteMessage",
                    json={
                        "chat_id": chat_id,
                        "message_id": message_id
                    },
                    timeout=10
                )
            except Exception as e:
                logger.error(f"Lỗi khi xóa tin nhắn: {str(e)}")
        
        # Tạo thread mới để không chặn luồng chính
        thread = threading.Thread(target=delete_message)
        thread.daemon = True
        thread.start()
    
    def send_message(self, chat_id, text, parse_mode=None, disable_notification=False, reply_to_message_id=None):
        """
        Gửi tin nhắn đến chat
        
        Args:
            chat_id (str): ID của chat cần gửi tin nhắn
            text (str): Nội dung tin nhắn
            parse_mode (str, optional): Chế độ định dạng tin nhắn (HTML, Markdown)
            disable_notification (bool, optional): Tắt thông báo
            reply_to_message_id (int, optional): ID của tin nhắn cần trả lời
            
        Returns:
            dict: Kết quả của API nếu thành công, None nếu thất bại
        """
        if not self.connected or not self.token:
            logger.error("Chưa kết nối đến Telegram Bot API")
            return None
            
        try:
            # Tạo dữ liệu gửi đi
            data = {
                "chat_id": chat_id,
                "text": text
            }
            
            # Thêm các tham số tùy chọn
            if parse_mode:
                data["parse_mode"] = parse_mode
            
            if disable_notification:
                data["disable_notification"] = True
            
            if reply_to_message_id:
                data["reply_to_message_id"] = reply_to_message_id
            
            # Gửi tin nhắn
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("result")
            else:
                logger.error(f"Không thể gửi tin nhắn đến chat {chat_id}: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi gửi tin nhắn: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def send_photo(self, chat_id, photo, caption=None, parse_mode=None, disable_notification=False):
        """
        Gửi ảnh đến chat
        
        Args:
            chat_id (str): ID của chat cần gửi ảnh
            photo (str): Đường dẫn đến file ảnh hoặc file_id của ảnh đã tải lên
            caption (str, optional): Chú thích cho ảnh
            parse_mode (str, optional): Chế độ định dạng chú thích (HTML, Markdown)
            disable_notification (bool, optional): Tắt thông báo
            
        Returns:
            dict: Kết quả của API nếu thành công, None nếu thất bại
        """
        if not self.connected or not self.token:
            logger.error("Chưa kết nối đến Telegram Bot API")
            return None
            
        try:
            # Tạo dữ liệu gửi đi
            data = {
                "chat_id": chat_id
            }
            
            # Thêm các tham số tùy chọn
            if caption:
                data["caption"] = caption
            
            if parse_mode:
                data["parse_mode"] = parse_mode
            
            if disable_notification:
                data["disable_notification"] = True
            
            # Kiểm tra loại photo
            if os.path.exists(photo):
                # Nếu là đường dẫn file trên máy
                files = {"photo": open(photo, "rb")}
                response = requests.post(
                    f"{self.base_url}/sendPhoto",
                    data=data,
                    files=files,
                    timeout=60
                )
            else:
                # Nếu là file_id hoặc URL
                data["photo"] = photo
                response = requests.post(
                    f"{self.base_url}/sendPhoto",
                    json=data,
                    timeout=60
                )
            
            if response.status_code == 200:
                return response.json().get("result")
            else:
                logger.error(f"Không thể gửi ảnh đến chat {chat_id}: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi gửi ảnh: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def send_video(self, chat_id, video, caption=None, parse_mode=None, disable_notification=False, width=None, height=None, duration=None):
        """
        Gửi video đến chat
        
        Args:
            chat_id (str): ID của chat cần gửi video
            video (str): Đường dẫn đến file video hoặc file_id của video đã tải lên
            caption (str, optional): Chú thích cho video
            parse_mode (str, optional): Chế độ định dạng chú thích (HTML, Markdown)
            disable_notification (bool, optional): Tắt thông báo
            width (int, optional): Chiều rộng của video
            height (int, optional): Chiều cao của video
            duration (int, optional): Thời lượng của video (giây)
            
        Returns:
            dict: Kết quả của API nếu thành công, None nếu thất bại
        """
        if not self.connected or not self.token:
            logger.error("Chưa kết nối đến Telegram Bot API")
            return None
            
        try:
            # Tạo dữ liệu gửi đi
            data = {
                "chat_id": chat_id
            }
            
            # Thêm các tham số tùy chọn
            if caption:
                data["caption"] = caption
            
            if parse_mode:
                data["parse_mode"] = parse_mode
            
            if disable_notification:
                data["disable_notification"] = True
            
            if width:
                data["width"] = width
            
            if height:
                data["height"] = height
            
            if duration:
                data["duration"] = duration
            
            # Kiểm tra loại video
            if os.path.exists(video):
                # Nếu là đường dẫn file trên máy
                files = {"video": open(video, "rb")}
                response = requests.post(
                    f"{self.base_url}/sendVideo",
                    data=data,
                    files=files,
                    timeout=300  # Thời gian chờ dài hơn cho video
                )
            else:
                # Nếu là file_id hoặc URL
                data["video"] = video
                response = requests.post(
                    f"{self.base_url}/sendVideo",
                    json=data,
                    timeout=60
                )
            
            if response.status_code == 200:
                return response.json().get("result")
            else:
                logger.error(f"Không thể gửi video đến chat {chat_id}: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi gửi video: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def get_chat(self, chat_id):
        """
        Lấy thông tin của chat
        
        Args:
            chat_id (str): ID của chat cần lấy thông tin
            
        Returns:
            dict: Thông tin chat nếu thành công, None nếu thất bại
        """
        if not self.connected or not self.token:
            logger.error("Chưa kết nối đến Telegram Bot API")
            return None
            
        try:
            response = requests.get(
                f"{self.base_url}/getChat",
                params={"chat_id": chat_id},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("ok", False):
                    return data.get("result")
            
            # Nếu không lấy được thông tin chat
            logger.error(f"Không thể lấy thông tin chat {chat_id}: {response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi lấy thông tin chat: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def delete_message(self, chat_id, message_id):
        """
        Xóa tin nhắn khỏi chat
        
        Args:
            chat_id (str): ID của chat chứa tin nhắn
            message_id (int): ID của tin nhắn cần xóa
            
        Returns:
            bool: True nếu xóa thành công, False nếu thất bại
        """
        if not self.connected or not self.token:
            logger.error("Chưa kết nối đến Telegram Bot API")
            return False
            
        try:
            response = requests.post(
                f"{self.base_url}/deleteMessage",
                json={
                    "chat_id": chat_id,
                    "message_id": message_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("ok", False):
                    return True
            
            # Nếu không xóa được tin nhắn
            logger.error(f"Không thể xóa tin nhắn {message_id} từ chat {chat_id}: {response.text}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi xóa tin nhắn: {str(e)}")
            logger.error(traceback.format_exc())
            return False