"""
Module quản lý tương tác với Telegram API.
"""
import os
import time
import logging
import threading
import socket
import requests
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
    
    def send_with_retry(self, send_func, max_retries=3, retry_delay=5):
        """
        Thực thi một hàm gửi với cơ chế tự động thử lại
        
        Args:
            send_func: Hàm gửi dữ liệu cần thực thi
            max_retries (int): Số lần thử lại tối đa
            retry_delay (int): Thời gian chờ giữa các lần thử lại (giây)
            
        Returns:
            Kết quả từ hàm gửi hoặc False nếu tất cả các lần thử đều thất bại
        """
        retries = 0
        last_error = None
        
        while retries <= max_retries:
            try:
                # Kiểm tra kết nối trước khi gửi
                if not self.connected or not self.bot:
                    # Thử kết nối lại
                    if not self.connect(self.bot_token):
                        logger.error("Mất kết nối và không thể kết nối lại")
                        time.sleep(retry_delay)
                        retries += 1
                        continue
                
                # Thực thi hàm gửi
                result = send_func()
                if result:
                    # Thành công
                    return result
                
                # Nếu gửi thất bại nhưng không có ngoại lệ
                retries += 1
                time.sleep(retry_delay)
                
            except telebot.apihelper.ApiTelegramException as e:
                # Xử lý lỗi API Telegram
                last_error = e
                logger.error(f"Lỗi API Telegram (lần {retries+1}/{max_retries+1}): {e}")
                
                # Xử lý các lỗi cụ thể
                if "Too Many Requests" in str(e) or "retry after" in str(e).lower():
                    # Lỗi rate limit, lấy thời gian chờ từ lỗi
                    wait_time = 5  # Mặc định 5 giây
                    try:
                        # Thử lấy thời gian chờ từ thông báo lỗi
                        import re
                        match = re.search(r'retry after (\d+)', str(e).lower())
                        if match:
                            wait_time = int(match.group(1)) + 1
                    except:
                        pass
                    
                    logger.info(f"Rate limit vượt quá, đợi {wait_time} giây")
                    time.sleep(wait_time)
                elif "Bad Request" in str(e) and "file is too big" in str(e).lower():
                    # Lỗi file quá lớn, không thử lại
                    logger.error("File quá lớn cho Telegram Bot API (giới hạn 50MB)")
                    return False
                else:
                    # Lỗi khác, đợi trước khi thử lại
                    time.sleep(retry_delay)
                
                retries += 1
            
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                # Lỗi kết nối hoặc timeout
                last_error = e
                logger.error(f"Lỗi kết nối (lần {retries+1}/{max_retries+1}): {e}")
                
                # Đợi lâu hơn cho lỗi kết nối
                time.sleep(retry_delay * 2)
                retries += 1
            
            except Exception as e:
                # Lỗi khác
                last_error = e
                logger.error(f"Lỗi không xác định (lần {retries+1}/{max_retries+1}): {e}")
                time.sleep(retry_delay)
                retries += 1
        
        # Nếu đã thử hết số lần
        logger.error(f"Đã thử {max_retries+1} lần nhưng vẫn thất bại: {last_error}")
        return False
    
    def send_video(self, chat_id, video_path, caption=None):
        """
        Gửi video đến chat ID
        
        Args:
            chat_id (str/int): ID chat nhận video
            video_path (str): Đường dẫn đến file video
            caption (str, optional): Chú thích cho video
            
        Returns:
            bool: True nếu gửi thành công
        """
        if not self.bot:
            logger.error("Chưa kết nối với bot Telegram!")
            return False
            
        video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        video_name = os.path.basename(video_path)
        
        # Kiểm tra nếu Telethon được bật và video lớn hơn 50MB
        use_telethon = False
        try:
            from app import app
            if hasattr(app, "config"):
                use_telethon = app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
        except:
            # Nếu không thể lấy từ app, kiểm tra trong cấu hình
            config = configparser.ConfigParser()
            config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.ini')
            if os.path.exists(config_file):
                config.read(config_file)
                if 'TELETHON' in config:
                    use_telethon = config.getboolean('TELETHON', 'use_telethon', fallback=False)
        
        if use_telethon and video_size_mb > 50:
            # Dùng Telethon để gửi video lớn
            try:
                from utils.telethon_uploader import telethon_uploader
                logger.info(f"🔄 Sử dụng Telethon API để tải lên video lớn: {video_name} ({video_size_mb:.2f} MB)")
                return telethon_uploader.send_video(chat_id, video_path, caption)
            except Exception as e:
                logger.error(f"Lỗi khi sử dụng Telethon: {str(e)}")
                # Nếu Telethon thất bại, quay lại xử lý thông thường
                logger.warning("Quay lại phương pháp tải lên thông thường")
        
        # Phương pháp gửi thông thường sử dụng Bot API
        logger.info(f"🔄 Đang xử lý video lớn: {video_name} ({video_size_mb:.2f} MB)")
        
        # Nếu video nhỏ hơn 50MB, gửi trực tiếp
        if video_size_mb <= 50:
            return self._send_video_directly(chat_id, video_path, caption)
        
        # Chia nhỏ video nếu lớn hơn 50MB
        from utils.video_splitter import VideoSplitter
        splitter = VideoSplitter()
        parts = splitter.split_video(video_path)
        
        if not parts:
            logger.error(f"Không thể chia nhỏ video: {video_name}")
            return False
        
        logger.info(f"Video {video_name} ({video_size_mb:.2f} MB) sẽ được gửi thành {len(parts)} phần")
        
        # Gửi từng phần
        total_parts = len(parts)
        for i, part in enumerate(parts, 1):
            part_caption = f"{caption or video_name} - Phần {i}/{total_parts}"
            success = self._send_video_directly(chat_id, part, part_caption)
            if not success:
                logger.error(f"Lỗi khi gửi phần {i}/{total_parts}")
                return False
            time.sleep(1)  # Chờ giữa các lần gửi
        
        # Xóa các file tạm
        for part in parts:
            try:
                os.remove(part)
            except:
                pass
        
        return True
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
    
    def send_video(self, chat_id, video_path, caption=None, width=None, height=None, duration=None, disable_notification=False, progress_callback=None):
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
            progress_callback (function): Callback để cập nhật tiến trình (không bắt buộc)
            
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
            
            # Update progress to 10% (preparing)
            if progress_callback:
                progress_callback(10)
            
            # Xử lý theo chế độ
            if mode == 'direct':
                # Update progress to 20% (starting direct upload)
                if progress_callback:
                    progress_callback(20)
                    
                # Gửi trực tiếp nếu kích thước cho phép
                result = self._send_video_direct(chat_id, video_path, caption, width, height, duration, disable_notification)
                
                # Update progress to 100% if successful
                if result and progress_callback:
                    progress_callback(100)
                    
                return result
            elif mode == 'split':
                # Xử lý video lớn bằng cách chia nhỏ
                return self._send_video_split(chat_id, video_path, caption, disable_notification, progress_callback)
            else:
                logger.error(f"Chế độ không hợp lệ: {mode}")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi gửi video {os.path.basename(video_path)}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def _send_video_split(self, chat_id, video_path, caption, disable_notification=False, progress_callback=None):
        """
        Gửi video lớn bằng cách chia nhỏ
        
        Args:
            chat_id (str/int): ID chat
            video_path (str): Đường dẫn video
            caption (str): Chú thích
            disable_notification (bool): Tắt thông báo
            progress_callback (function): Callback để cập nhật tiến trình (không bắt buộc)
            
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
            
            # Update progress to 15% (processing video)
            if progress_callback:
                progress_callback(15)
            
            # Chia nhỏ video
            video_parts = self.video_splitter.split_video(video_path)
            
            # Update progress to 25% (splitting completed)
            if progress_callback:
                progress_callback(25)
            
            if not video_parts:
                # Thử phương pháp nén
                logger.info(f"Không thể chia nhỏ video, thử phương pháp nén...")
                
                # Update progress to 30% (trying compression)
                if progress_callback:
                    progress_callback(30)
                    
                compressed_video = self.video_splitter.compress_video(video_path)
                
                # Update progress to 50% (compression completed)
                if progress_callback:
                    progress_callback(50)
                    
                if compressed_video and os.path.exists(compressed_video):
                    # Kiểm tra kích thước sau khi nén
                    compressed_size = os.path.getsize(compressed_video) / (1024 * 1024)
                    
                    if compressed_size <= 49:
                        # Nếu đã nén xuống dưới 50MB, gửi bình thường
                        logger.info(f"Video đã được nén: {file_name} ({file_size:.2f}MB → {compressed_size:.2f}MB)")
                        
                        # Update progress to 60% (starting upload of compressed video)
                        if progress_callback:
                            progress_callback(60)
                            
                        result = self._send_video_direct(
                            chat_id,
                            compressed_video,
                            caption,
                            disable_notification=disable_notification
                        )
                        
                        # Update progress to 100% if successful
                        if result and progress_callback:
                            progress_callback(100)
                            
                        return result
                    else:
                        # Nếu vẫn lớn hơn 50MB sau khi nén
                        logger.exception(f"❌ Không thể xử lý video: {file_name} (vẫn lớn hơn 50MB sau khi nén)")
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
            
            # Gửi từng phần
            total_parts = len(video_parts)
            for i, part_path in enumerate(video_parts):
                # Calculate progress (25% to 95%)
                if progress_callback:
                    percent = 25 + (i / total_parts) * 70
                    progress_callback(int(percent))
                    
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
            
            # Update progress to 100%
            if progress_callback:
                progress_callback(100)
                
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi gửi video chia nhỏ {os.path.basename(video_path)}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            return False
        
    def _send_video_direct(self, chat_id, video_path, caption, width=None, height=None, duration=None, disable_notification=False):
        """
        Gửi video trực tiếp không qua xử lý, với cơ chế tự động thử lại
        
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
        def _send():
            with self.send_lock:  # Sử dụng lock để tránh lỗi flood control
                # Mở file video
                with open(video_path, 'rb') as video_file:
                    # Gửi video
                    self.bot.send_video(
                        chat_id=chat_id,
                        video=video_file,
                        width=width,
                        height=height,
                        duration=duration,
                        disable_notification=disable_notification,
                        supports_streaming=True  # Hỗ trợ phát trực tuyến
                    )
            
            logger.info(f"Đã gửi video thành công: {os.path.basename(video_path)}")
            return True
        
        return self.send_with_retry(_send)
    

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
        # Không gửi thông báo theo yêu cầu, chỉ ghi log
        logger.info(f"Thông báo (không gửi): {text}")
        return True
    
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
    
    def check_internet_connection(self):
        """
        Kiểm tra kết nối internet
        
        Returns:
            bool: True nếu có kết nối internet
        """
        try:
            # Thử kết nối đến Google DNS
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            pass
        
        try:
            # Thử kết nối đến Telegram API
            socket.create_connection(("api.telegram.org", 443), timeout=3)
            return True
        except OSError:
            pass
        
        return False

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