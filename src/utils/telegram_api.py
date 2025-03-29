"""
Module quản lý tương tác với Telegram API.
"""
import os
import time
import logging
import threading
from datetime import datetime
import telebot
from telebot.types import InputFile

# Cấu hình logging
logger = logging.getLogger("TelegramAPI")

class TelegramAPI:
    """
    Quản lý tương tác với Telegram API qua pyTelegramBotAPI.
    """
    
    def __init__(self):
        """Khởi tạo TelegramAPI"""
        self.bot = None
        self.connected = False
        self.send_lock = threading.Lock()  # Lock để đồng bộ hóa gửi tin nhắn
    
    def connect(self, bot_token):
        """
        Kết nối với bot Telegram
        
        Args:
            bot_token (str): Bot token từ BotFather
            
        Returns:
            bool: True nếu kết nối thành công
        """
        if self.connected and self.bot:
            return True
            
        try:
            # Tạo đối tượng bot
            self.bot = telebot.TeleBot(bot_token)
            
            # Kiểm tra kết nối bằng cách lấy thông tin bot
            bot_info = self.bot.get_me()
            
            if bot_info:
                logger.info(f"Đã kết nối thành công với bot: @{bot_info.username}")
                self.connected = True
                return True
            else:
                logger.error("Không thể lấy thông tin bot")
                self.bot = None
                self.connected = False
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi kết nối với Telegram API: {str(e)}")
            self.bot = None
            self.connected = False
            return False
    
    def disconnect(self):
        """
        Ngắt kết nối với bot Telegram
        """
        self.bot = None
        self.connected = False
        logger.info("Đã ngắt kết nối với Telegram API")
    
    def send_message(self, chat_id, text, disable_notification=False):
        """
        Gửi tin nhắn văn bản
        
        Args:
            chat_id (str/int): ID của cuộc trò chuyện/kênh
            text (str): Nội dung tin nhắn
            disable_notification (bool): Có tắt thông báo không
            
        Returns:
            bool: True nếu gửi thành công
        """
        if not self.connected or not self.bot:
            logger.error("Chưa kết nối với Telegram API")
            return False
            
        try:
            with self.send_lock:  # Sử dụng lock để tránh lỗi flood control
                self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode='HTML',
                    disable_notification=disable_notification
                )
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi gửi tin nhắn: {str(e)}")
            return False
    
    def send_video(self, chat_id, video_path, caption=None, width=None, height=None, duration=None, disable_notification=False):
        """
        Gửi file video
        
        Args:
            chat_id (str/int): ID của cuộc trò chuyện/kênh
            video_path (str): Đường dẫn đến file video
            caption (str): Chú thích cho video
            width (int): Chiều rộng video
            height (int): Chiều cao video
            duration (int): Thời lượng video (giây)
            disable_notification (bool): Có tắt thông báo không
            
        Returns:
            bool: True nếu gửi thành công
        """
        if not self.connected or not self.bot:
            logger.error("Chưa kết nối với Telegram API")
            return False
            
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            logger.error(f"File video không tồn tại: {video_path}")
            return False
            
        try:
            # Kiểm tra kích thước file
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            
            if file_size > 50:
                logger.error(f"File video quá lớn ({file_size:.2f} MB > 50 MB)")
                return False
                
            # Chuẩn bị caption nếu không có
            if not caption:
                file_name = os.path.basename(video_path)
                caption = f"📹 {file_name}\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
            with self.send_lock:  # Sử dụng lock để tránh lỗi flood control
                # Mở file video
                with open(video_path, 'rb') as video_file:
                    # Gửi video
                    self.bot.send_video(
                        chat_id=chat_id,
                        video=video_file,
                        caption=caption,
                        width=width,
                        height=height,
                        duration=duration,
                        disable_notification=disable_notification,
                        supports_streaming=True  # Hỗ trợ phát trực tuyến
                    )
                    
            logger.info(f"Đã gửi video thành công: {os.path.basename(video_path)}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi gửi video {os.path.basename(video_path)}: {str(e)}")
            return False
    
    def send_notification(self, notification_chat_id, text, disable_notification=False):
        """
        Gửi thông báo đến chat ID nhận thông báo
        
        Args:
            notification_chat_id (str/int): ID chat nhận thông báo
            text (str): Nội dung thông báo
            disable_notification (bool): Có tắt thông báo không
            
        Returns:
            bool: True nếu gửi thành công
        """
        if not notification_chat_id:
            return False
            
        return self.send_message(notification_chat_id, text, disable_notification)
    
    def test_connection(self, bot_token, chat_id):
        """
        Kiểm tra kết nối và quyền gửi tin nhắn
        
        Args:
            bot_token (str): Bot token cần kiểm tra
            chat_id (str/int): Chat ID cần kiểm tra quyền
            
        Returns:
            tuple: (success, message) - success là bool, message là thông báo kết quả
        """
        try:
            # Kết nối với token mới
            test_bot = telebot.TeleBot(bot_token)
            
            # Lấy thông tin bot
            bot_info = test_bot.get_me()
            if not bot_info:
                return False, "Không thể lấy thông tin bot. Vui lòng kiểm tra Bot Token."
                
            # Kiểm tra quyền gửi tin nhắn
            if chat_id:
                test_message = f"🔄 Kiểm tra kết nối từ Telegram Video Uploader\n⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                test_bot.send_message(chat_id, test_message)
                
            return True, f"Kết nối thành công với bot @{bot_info.username}"
            
        except telebot.apihelper.ApiException as e:
            if "Forbidden" in str(e):
                return False, "Bot không có quyền gửi tin nhắn đến chat ID này. Vui lòng kiểm tra quyền của bot."
            elif "Bad Request" in str(e) and "chat not found" in str(e).lower():
                return False, "Chat ID không hợp lệ hoặc không tồn tại."
            else:
                return False, f"Lỗi API Telegram: {str(e)}"
        except Exception as e:
            return False, f"Lỗi khi kiểm tra kết nối: {str(e)}"

if __name__ == "__main__":
    # Mã kiểm thử
    logging.basicConfig(level=logging.DEBUG)
    
    api = TelegramAPI()
    
    # Thay thế với bot token và chat ID thật
    BOT_TOKEN = "YOUR_BOT_TOKEN"
    CHAT_ID = "YOUR_CHAT_ID"
    
    if api.connect(BOT_TOKEN):
        print("Kết nối thành công")
        
        # Gửi tin nhắn kiểm tra
        if api.send_message(CHAT_ID, "Tin nhắn kiểm tra từ TelegramAPI"):
            print("Đã gửi tin nhắn thành công")
        else:
            print("Gửi tin nhắn thất bại")
            
        api.disconnect()
    else:
        print("Kết nối thất bại")