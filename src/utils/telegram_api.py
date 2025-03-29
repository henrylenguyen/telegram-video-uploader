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

# Nhập module VideoSplitter để xử lý file lớn
try:
    from utils.video_splitter import VideoSplitter
except ImportError:
    from video_splitter import VideoSplitter

# Cấu hình logging
logger = logging.getLogger("TelegramAPI")

class TelegramAPI:
    """
    Quản lý tương tác với Telegram API qua pyTelegramBotAPI.
    Hỗ trợ tải lên video không giới hạn kích thước bằng cách chia nhỏ.
    """
    
    def __init__(self):
        """Khởi tạo TelegramAPI"""
        self.bot = None
        self.connected = False
        self.send_lock = threading.Lock()  # Lock để đồng bộ hóa gửi tin nhắn
        self.bot_token = None
        self.video_splitter = VideoSplitter()
    
    def connect(self, bot_token):
        """
        Kết nối với bot Telegram
        
        Args:
            bot_token (str): Bot token từ BotFather
            
        Returns:
            bool: True nếu kết nối thành công
        """
        if self.connected and self.bot and self.bot_token == bot_token:
            return True
            
        try:
            # Tạo đối tượng bot
            self.bot = telebot.TeleBot(bot_token)
            
            # Kiểm tra kết nối bằng cách lấy thông tin bot
            bot_info = self.bot.get_me()
            
            if bot_info:
                logger.info(f"Đã kết nối thành công với bot: @{bot_info.username}")
                self.connected = True
                self.bot_token = bot_token
                return True
            else:
                logger.error("Không thể lấy thông tin bot")
                self.bot = None
                self.connected = False
                self.bot_token = None
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi kết nối với Telegram API: {str(e)}")
            self.bot = None
            self.connected = False
            self.bot_token = None
            return False
    
    def disconnect(self):
        """
        Ngắt kết nối với bot Telegram
        """
        self.bot = None
        self.connected = False
        self.bot_token = None
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
    
    def _check_file_size(self, file_path):
        """
        Kiểm tra kích thước file và quyết định cách xử lý
        
        Args:
            file_path (str): Đường dẫn đến file
            
        Returns:
            tuple: (mode, size_mb)
                mode: 'direct' nếu < 50MB, 'split' nếu cần chia nhỏ, 'compress' nếu cần nén
                size_mb: Kích thước file tính bằng MB
        """
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return None, 0
            
        # Kích thước file tính bằng MB
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        if size_mb <= 49:  # Giới hạn an toàn là 49MB
            return 'direct', size_mb
        else:
            # Ưu tiên chia nhỏ trước
            return 'split', size_mb
    
    def send_video(self, chat_id, video_path, caption=None, width=None, height=None, duration=None, disable_notification=False):
        """
        Gửi file video, tự động xử lý video lớn hơn 50MB
        
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
            mode, file_size = self._check_file_size(video_path)
            
            # Chuẩn bị caption nếu không có
            if not caption:
                file_name = os.path.basename(video_path)
                caption = f"📹 {file_name}\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Xử lý theo chế độ
            if mode == 'direct':
                # Gửi trực tiếp nếu kích thước cho phép
                return self._send_video_direct(chat_id, video_path, caption, width, height, duration, disable_notification)
            elif mode == 'split':
                # Xử lý video lớn bằng cách chia nhỏ
                return self._send_video_split(chat_id, video_path, caption, disable_notification)
            else:
                logger.error(f"Chế độ không hợp lệ: {mode}")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi gửi video {os.path.basename(video_path)}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _send_video_direct(self, chat_id, video_path, caption, width=None, height=None, duration=None, disable_notification=False):
        """
        Gửi video trực tiếp không qua xử lý
        
        Args:
            chat_id (str/int): ID chat
            video_path (str): Đường dẫn video
            caption (str): Chú thích
            width (int): Chiều rộng
            height (int): Chiều cao
            duration (int): Thời lượng
            disable_notification (bool): Tắt thông báo
            
        Returns:
            bool: True nếu thành công
        """
        try:
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
            logger.error(f"Lỗi khi gửi video trực tiếp {os.path.basename(video_path)}: {str(e)}")
            return False
    
    def _send_video_split(self, chat_id, video_path, caption, disable_notification=False):
        """
        Gửi video lớn bằng cách chia nhỏ
        
        Args:
            chat_id (str/int): ID chat
            video_path (str): Đường dẫn video
            caption (str): Chú thích
            disable_notification (bool): Tắt thông báo
            
        Returns:
            bool: True nếu thành công
        """
        try:
            # Lấy thông tin video gốc
            file_name = os.path.basename(video_path)
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            
            # Thông báo bắt đầu xử lý
            start_message = f"🔄 Đang xử lý video lớn: {file_name} ({file_size:.2f} MB)"
            logger.info(start_message)
            
            self.send_message(chat_id, start_message)
            
            # Chia nhỏ video
            video_parts = self.video_splitter.split_video(video_path)
            
            if not video_parts:
                # Thử phương pháp nén
                logger.info(f"Không thể chia nhỏ video, thử phương pháp nén...")
                compressed_video = self.video_splitter.compress_video(video_path)
                
                if compressed_video and os.path.exists(compressed_video):
                    # Kiểm tra kích thước sau khi nén
                    compressed_size = os.path.getsize(compressed_video) / (1024 * 1024)
                    
                    if compressed_size <= 49:
                        # Nếu đã nén xuống dưới 50MB, gửi bình thường
                        self.send_message(
                            chat_id,
                            f"Video đã được nén: {file_name} ({file_size:.2f}MB → {compressed_size:.2f}MB)"
                        )
                        
                        return self._send_video_direct(
                            chat_id,
                            compressed_video,
                            caption,
                            disable_notification=disable_notification
                        )
                    else:
                        # Nếu vẫn lớn hơn 50MB sau khi nén
                        self.send_message(
                            chat_id,
                            f"❌ Không thể xử lý video: {file_name} (vẫn lớn hơn 50MB sau khi nén)"
                        )
                        return False
                else:
                    # Không thể nén
                    self.send_message(
                        chat_id,
                        f"❌ Không thể xử lý video: {file_name} (không thể chia nhỏ hoặc nén)"
                    )
                    return False
            
            # Thông báo số lượng phần
            part_message = f"Video {file_name} ({file_size:.2f} MB) sẽ được gửi thành {len(video_parts)} phần"
            logger.info(part_message)
            self.send_message(chat_id, part_message)
            
            # Gửi từng phần
            for i, part_path in enumerate(video_parts):
                part_caption = f"{caption}\nPhần {i+1}/{len(video_parts)}"
                
                # Gửi phần video
                success = self._send_video_direct(
                    chat_id,
                    part_path,
                    part_caption,
                    disable_notification=disable_notification
                )
                
                if not success:
                    logger.error(f"Lỗi khi gửi phần {i+1}/{len(video_parts)} của video {file_name}")
                    return False
                
                # Chờ giữa các lần gửi để tránh flood
                if i < len(video_parts) - 1:
                    time.sleep(2)
            
            # Thông báo hoàn tất
            complete_message = f"✅ Đã gửi xong video: {file_name} ({len(video_parts)} phần)"
            logger.info(complete_message)
            self.send_message(chat_id, complete_message)
            
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi gửi video chia nhỏ {os.path.basename(video_path)}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Thông báo lỗi
            error_message = f"❌ Lỗi khi gửi video: {os.path.basename(video_path)}\n{str(e)}"
            self.send_message(chat_id, error_message)
            
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
        
        # Thử nghiệm gửi video lớn
        # api.send_video(CHAT_ID, "/path/to/large/video.mp4")
        
        # Gửi tin nhắn kiểm tra
        if api.send_message(CHAT_ID, "Tin nhắn kiểm tra từ TelegramAPI"):
            print("Đã gửi tin nhắn thành công")
        else:
            print("Gửi tin nhắn thất bại")
            
        api.disconnect()
    else:
        print("Kết nối thất bại")