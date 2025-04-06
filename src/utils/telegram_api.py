"""
Module for interacting with Telegram API
"""

import os
import logging
import tempfile
import time
from datetime import datetime
import telebot
from telebot import apihelper
from telebot.types import InputFile
from utils.video_splitter import VideoSplitter

logger = logging.getLogger("TelegramAPI")

class TelegramAPI:
    """
    Class for interacting with Telegram API
    """
    
    def __init__(self, bot_token=None):
        """
        Initialize Telegram API
        
        Args:
            bot_token (str): Telegram Bot token
        """
        self.bot = None
        self.connected = False
        
        # Connect if token provided
        if bot_token:
            self.connect(bot_token)
    
    def connect(self, bot_token):
        """
        Connect to Telegram Bot API
        
        Args:
            bot_token (str): Telegram Bot token
            
        Returns:
            bool: True if connected successfully
        """
        try:
            # Set up API
            self.bot = telebot.TeleBot(bot_token)
            
            # Test connection
            bot_info = self.bot.get_me()
            if bot_info:
                self.connected = True
                return True
            else:
                self.connected = False
                return False
        except Exception as e:
            logger.error(f"Lỗi khi kết nối Telegram: {str(e)}")
            self.bot = None
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Telegram Bot API"""
        self.bot = None
        self.connected = False
    
    def send_message(self, chat_id, text, parse_mode="HTML", disable_notification=False):
        """
        Send a message to Telegram
        
        Args:
            chat_id (str/int): ID của cuộc trò chuyện/kênh
            text (str): Nội dung tin nhắn
            parse_mode (str): Chế độ parse (HTML/Markdown)
            disable_notification (bool): Có tắt thông báo không
            
        Returns:
            bool: True nếu gửi thành công
        """
        if not self.connected or not self.bot:
            logger.error("Chưa kết nối với Telegram API")
            return False
            
        try:
            message = self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_notification=disable_notification
            )
            return message is not None
        except Exception as e:
            logger.error(f"Lỗi khi gửi tin nhắn: {str(e)}")
            return False
    
    def send_video(self, chat_id, video_path, caption=None, width=None, height=None, duration=None, disable_notification=False, progress_callback=None):
        """
        Gửi video đến Telegram chat/channel, với chức năng Telethon cải tiến
        
        Args:
            chat_id (str/int): ID của cuộc trò chuyện/kênh
            video_path (str): Đường dẫn đến file video
            caption (str): Chú thích cho video
            width (int): Chiều rộng video
            height (int): Chiều cao video
            duration (int): Thời lượng video (giây)
            disable_notification (bool): Có tắt thông báo không
            progress_callback (function): Callback để cập nhật tiến trình
            
        Returns:
            bool: True nếu gửi thành công
        """
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            logger.error(f"File video không tồn tại: {video_path}")
            return False
            
        try:
            # Lấy thông tin video
            video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            video_name = os.path.basename(video_path)
            
            # Chuẩn bị caption nếu không cung cấp
            if not caption:
                file_name = os.path.basename(video_path)
                caption = f"📹 {file_name}\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Cập nhật tiến trình lên 10% (chuẩn bị)
            if progress_callback:
                progress_callback(10)
            
            # KIỂM TRA TELETHON TRỰC TIẾP - Cách tiếp cận đơn giản hơn
            # Chỉ kiểm tra cho video lớn (trên 50MB)
            if video_size_mb > 50:
                logger.info(f"Video lớn phát hiện: {video_name} ({video_size_mb:.2f} MB)")
                
                # TRUY CẬP TRỰC TIẾP INSTANCE APP - Đáng tin cậy hơn
                try:
                    # Thử import instance app chính
                    import sys
                    main_module = sys.modules['__main__']
                    if hasattr(main_module, 'app'):
                        app = main_module.app
                        
                        # Kiểm tra xem Telethon có được bật trong config không
                        use_telethon = app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
                        logger.info(f"Cấu hình Telethon: use_telethon={use_telethon}")
                        
                        if use_telethon:
                            # Lấy telethon uploader trực tiếp từ app
                            telethon_uploader = app.telethon_uploader
                            
                            # Ghi log trạng thái kết nối Telethon
                            telethon_connected = getattr(telethon_uploader, 'connected', False)
                            logger.info(f"Trạng thái kết nối Telethon: {telethon_connected}")
                            
                            # Kiểm tra kết nối nếu trạng thái không rõ ràng
                            if not telethon_connected:
                                logger.info("Thử kết nối lại với Telethon API...")
                                # Lấy thông tin xác thực trực tiếp từ config
                                api_id = app.config.get('TELETHON', 'api_id', fallback='')
                                api_hash = app.config.get('TELETHON', 'api_hash', fallback='')
                                phone = app.config.get('TELETHON', 'phone', fallback='')
                                
                                if api_id and api_hash and phone:
                                    # Thử đăng nhập lại (không tương tác)
                                    try:
                                        api_id = int(api_id)
                                        login_result = telethon_uploader.login(api_id, api_hash, phone, interactive=False)
                                        logger.info(f"Kết quả login Telethon: {login_result}")
                                        telethon_connected = telethon_uploader.connected
                                    except Exception as e:
                                        logger.error(f"Lỗi khi kết nối Telethon: {str(e)}")
                            
                            # Nếu đã kết nối, sử dụng Telethon
                            if telethon_connected:
                                logger.info(f"🔄 Sử dụng Telethon API để tải lên video lớn: {video_name} ({video_size_mb:.2f} MB)")
                                
                                # Cập nhật tiến trình lên 20% (bắt đầu tải lên qua Telethon)
                                if progress_callback:
                                    progress_callback(20)
                                
                                # Tải lên qua Telethon
                                telethon_result = telethon_uploader.upload_video(
                                    chat_id, 
                                    video_path,
                                    caption=caption,
                                    progress_callback=progress_callback
                                )
                                
                                if telethon_result:
                                    logger.info(f"✅ Đã tải lên thành công qua Telethon: {video_name}")
                                    return True
                                else:
                                    logger.error(f"❌ Tải lên thất bại qua Telethon: {video_name}")
                                    logger.info("Quay lại phương pháp thông thường...")
                            else:
                                logger.warning("⚠️ Telethon được cấu hình nhưng không kết nối. Quay lại phương pháp thông thường.")
                        else:
                            logger.info("Telethon không được bật trong cấu hình. Sử dụng phương pháp thông thường.")
                except Exception as e:
                    logger.error(f"Lỗi khi kiểm tra Telethon: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
            
            # Quay lại phương pháp tiêu chuẩn (tải lên trực tiếp hoặc chia nhỏ)
            if video_size_mb <= 50:
                # Tải lên trực tiếp cho video nhỏ
                return self._send_video_direct(chat_id, video_path, caption, width, height, duration, disable_notification)
            else:
                # Chia nhỏ và tải lên theo từng phần cho video lớn
                logger.info(f"🔄 Đang xử lý video lớn: {video_name} ({video_size_mb:.2f} MB)")
                return self._send_video_split(chat_id, video_path, caption, disable_notification, progress_callback)
        
        except Exception as e:
            logger.error(f"Lỗi khi gửi video {os.path.basename(video_path)}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _send_video_direct(self, chat_id, video_path, caption=None, width=None, height=None, duration=None, disable_notification=False, retry_count=3):
        """
        Gửi video trực tiếp đến Telegram
        
        Args:
            chat_id (str/int): ID của cuộc trò chuyện/kênh
            video_path (str): Đường dẫn đến file video
            caption (str): Chú thích cho video
            width (int): Chiều rộng video
            height (int): Chiều cao video
            duration (int): Thời lượng video (giây)
            disable_notification (bool): Có tắt thông báo không
            retry_count (int): Số lần thử lại nếu gặp lỗi
            
        Returns:
            bool: True nếu gửi thành công
        """
        if not self.connected or not self.bot:
            logger.error("Chưa kết nối với Telegram API")
            return False
        
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            logger.error(f"File video không tồn tại: {video_path}")
            return False
        
        # Retry mechanism
        attempt = 0
        while attempt < retry_count:
            try:
                # Open file in binary mode
                with open(video_path, 'rb') as video_file:
                    # Send video
                    message = self.bot.send_video(
                        chat_id=chat_id,
                        video=video_file,
                        caption=caption,
                        width=width,
                        height=height,
                        duration=duration,
                        disable_notification=disable_notification,
                        supports_streaming=True
                    )
                    
                    # Check if video was sent successfully
                    if message and message.video:
                        logger.info(f"✅ Đã gửi video thành công: {os.path.basename(video_path)}")
                        return True
                    else:
                        logger.warning(f"⚠️ Video đã được gửi nhưng không nhận được xác nhận: {os.path.basename(video_path)}")
                        return True  # Consider it successful if no error was thrown
            
            except apihelper.ApiTelegramException as e:
                if e.error_code == 413:  # Request Entity Too Large
                    logger.error(f"❌ Video quá lớn cho Telegram Bot API: {os.path.basename(video_path)}")
                    return False  # No retry for this error
                    
                logger.warning(f"⚠️ Lỗi API Telegram (lần {attempt+1}/{retry_count}): {str(e)}")
                
            except Exception as e:
                logger.warning(f"⚠️ Lỗi khi gửi video (lần {attempt+1}/{retry_count}): {str(e)}")
            
            # Retry after delay
            attempt += 1
            if attempt < retry_count:
                retry_delay = 5  # seconds
                logger.info(f"Thử lại sau {retry_delay} giây...")
                time.sleep(retry_delay)
        
        logger.error(f"❌ Không thể gửi video sau {retry_count} lần thử: {os.path.basename(video_path)}")
        return False
    
    def _send_video_split(self, chat_id, video_path, caption=None, disable_notification=False, progress_callback=None):
        """
        Chia nhỏ video và gửi từng phần
        
        Args:
            chat_id (str/int): ID của cuộc trò chuyện/kênh
            video_path (str): Đường dẫn đến file video
            caption (str): Chú thích cho video
            disable_notification (bool): Có tắt thông báo không
            progress_callback (function): Callback để cập nhật tiến trình
            
        Returns:
            bool: True nếu tất cả các phần được gửi thành công
        """
        # FORCE TELETHON CHECK một lần nữa để chắc chắn
        video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        logger.info(f"FORCE CHECK TELETHON: Video size = {video_size_mb:.2f} MB")
        try:
            import sys
            main_module = sys.modules['__main__']
            if hasattr(main_module, 'app'):
                app = main_module.app
                use_telethon = app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
                logger.info(f"FORCE CHECK TELETHON: use_telethon = {use_telethon}")
                
                if use_telethon:
                    telethon_uploader = app.telethon_uploader
                    telethon_connected = getattr(telethon_uploader, 'connected', False)
                    logger.info(f"FORCE CHECK TELETHON: telethon_connected = {telethon_connected}")
                    
                    if telethon_connected:
                        logger.info(f"FORCE CHECK TELETHON: Thử tải lên qua Telethon")
                        result = telethon_uploader.upload_video(
                            chat_id, video_path, caption=caption, progress_callback=progress_callback
                        )
                        if result:
                            logger.info("FORCE CHECK TELETHON: TẢI LÊN THÀNH CÔNG QUA TELETHON!")
                            return True
                        logger.error("FORCE CHECK TELETHON: Tải lên thất bại")
                        
                    # Kiểm tra khả năng kết nối
                    else:
                        try:
                            is_connected = telethon_uploader.is_connected()
                            logger.info(f"FORCE CHECK TELETHON: is_connected() = {is_connected}")
                            
                            if is_connected:
                                telethon_uploader.connected = True
                                logger.info("FORCE CHECK TELETHON: Đã thiết lập connected = True")
                                
                                # Thử upload lại
                                result = telethon_uploader.upload_video(
                                    chat_id, video_path, caption=caption, progress_callback=progress_callback
                                )
                                if result:
                                    logger.info("FORCE CHECK TELETHON: TẢI LÊN THÀNH CÔNG QUA TELETHON SAU KHI TỰ SỬA!")
                                    return True
                        except:
                            pass
        except Exception as e:
            logger.error(f"FORCE CHECK TELETHON ERROR: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
        # Create a video splitter
        splitter = VideoSplitter()
        
        try:
            # Split the video into parts
            video_name = os.path.basename(video_path)
            video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            logger.info(f"Video {video_name} ({video_size_mb:.2f} MB) sẽ được gửi thành nhiều phần")
            
            # QUAN TRỌNG: Chỉ truyền một tham số tới split_video
            video_parts = splitter.split_video(video_path)
            if not video_parts:
                logger.error(f"Không thể chia nhỏ video: {video_name}")
                return False
            
            # Send each part
            total_parts = len(video_parts)
            part_index = 0
            successful_parts = 0
            
            for part_path in video_parts:
                part_index += 1
                part_name = os.path.basename(part_path)
                
                # Generate part caption
                if caption:
                    part_caption = f"{caption}\n\n📌 Phần {part_index}/{total_parts}"
                else:
                    part_caption = f"📹 {video_name} (Phần {part_index}/{total_parts})"
                
                # Calculate progress range for this part
                # Each part starts at 10% and goes to 90% spread across all parts
                progress_start = 10 + (part_index - 1) * 80 / total_parts
                progress_end = 10 + part_index * 80 / total_parts
                
                # Custom progress callback for this part
                if progress_callback:
                    part_progress_callback = lambda p: progress_callback(
                        int(progress_start + (progress_end - progress_start) * p / 100)
                    )
                else:
                    part_progress_callback = None
                
                # Send this part
                logger.info(f"🔄 Đang gửi phần {part_index}/{total_parts}: {part_name}")
                
                # Make multiple attempts if needed
                max_attempts = 4
                for attempt in range(max_attempts):
                    try:
                        success = self._send_video_direct(
                            chat_id,
                            part_path,
                            part_caption,
                            disable_notification=disable_notification
                        )
                        
                        if success:
                            successful_parts += 1
                            # Update progress to end of this part
                            if progress_callback:
                                progress_callback(int(progress_end))
                            break
                        
                        if attempt < max_attempts - 1:
                            logger.warning(f"⚠️ Lỗi kết nối (lần {attempt+1}/{max_attempts}), thử lại sau 10 giây...")
                            time.sleep(10)  # Wait before retrying
                        else:
                            logger.error(f"❌ Đã thử {max_attempts} lần nhưng không thể gửi phần {part_index}/{total_parts}")
                    
                    except Exception as e:
                        logger.error(f"Lỗi khi gửi phần {part_index}/{total_parts}: {str(e)}")
                        if attempt < max_attempts - 1:
                            logger.warning(f"⚠️ Thử lại sau 10 giây...")
                            time.sleep(10)  # Wait before retrying
            
            # Clean up temporary files
            try:
                for part_path in video_parts:
                    if os.path.exists(part_path):
                        os.remove(part_path)
            except Exception as e:
                logger.warning(f"⚠️ Không thể xóa file tạm thời: {str(e)}")
            
            # Check if all parts were sent successfully
            if successful_parts == total_parts:
                logger.info(f"✅ Đã gửi thành công tất cả {total_parts} phần của video {video_name}")
                # Set progress to 100%
                if progress_callback:
                    progress_callback(100)
                return True
            else:
                logger.error(f"❌ Chỉ gửi được {successful_parts}/{total_parts} phần của video {video_name}")
                return False
            
        except Exception as e:
            logger.error(f"Lỗi khi gửi video theo từng phần: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
            
    def delete_message(self, chat_id, message_id):
        """
        Xóa tin nhắn khỏi Telegram
        
        Args:
            chat_id (str/int): ID của cuộc trò chuyện/kênh
            message_id (int): ID của tin nhắn cần xóa
            
        Returns:
            bool: True nếu xóa thành công
        """
        if not self.connected or not self.bot:
            logger.error("Chưa kết nối với Telegram API")
            return False
            
        try:
            result = self.bot.delete_message(chat_id, message_id)
            return result
        except Exception as e:
            logger.error(f"Lỗi khi xóa tin nhắn: {str(e)}")
            return False