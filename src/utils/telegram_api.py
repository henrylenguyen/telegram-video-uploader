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
import configparser

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
        self.telethon_uploader = None
        
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
    
    def get_config_use_telethon(self):
        """
        Đọc cấu hình use_telethon trực tiếp từ file config.ini

        Returns:
            bool: True nếu use_telethon được bật trong config
        """
        try:
            # Đầu tiên, thử truy cập qua app toàn cục
            import sys
            for module_name in ['__main__', 'app']:
                if module_name in sys.modules:
                    main_module = sys.modules[module_name]
                    if hasattr(main_module, 'app'):
                        app = main_module.app
                        if hasattr(app, 'config'):
                            try:
                                use_telethon = app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
                                logger.info(f"Đọc use_telethon={use_telethon} từ app.config")
                                return use_telethon
                            except Exception:
                                pass
            
            # Nếu không thể truy cập qua app, đọc trực tiếp từ file config.ini
            config = configparser.ConfigParser()
            
            # Tìm file config.ini trong các vị trí khác nhau
            possible_paths = [
                'config.ini',
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config.ini'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.ini'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.ini')
            ]
            
            for config_path in possible_paths:
                if os.path.exists(config_path):
                    config.read(config_path)
                    if 'TELETHON' in config and 'use_telethon' in config['TELETHON']:
                        use_telethon_str = config['TELETHON']['use_telethon'].lower()
                        use_telethon = use_telethon_str == 'true' or use_telethon_str == '1'
                        logger.info(f"Đọc use_telethon={use_telethon} từ file config.ini tại {config_path}")
                        return use_telethon
            
            logger.warning("Không tìm thấy cấu hình use_telethon, mặc định = False")
            return False
        except Exception as e:
            logger.error(f"Lỗi khi đọc cấu hình use_telethon: {str(e)}")
            return False
    
    def get_telethon_config(self):
        """
        Đọc cấu hình Telethon từ config.ini

        Returns:
            tuple: (api_id, api_hash, phone) nếu tìm thấy, (None, None, None) nếu không
        """
        try:
            config = configparser.ConfigParser()
            
            # Tìm file config.ini trong các vị trí khác nhau
            possible_paths = [
                'config.ini',
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config.ini'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.ini'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.ini')
            ]
            
            for config_path in possible_paths:
                if os.path.exists(config_path):
                    config.read(config_path)
                    if 'TELETHON' in config:
                        api_id = config['TELETHON'].get('api_id', '')
                        api_hash = config['TELETHON'].get('api_hash', '')
                        phone = config['TELETHON'].get('phone', '')
                        
                        if api_id and api_hash and phone:
                            try:
                                api_id = int(api_id)
                                return (api_id, api_hash, phone)
                            except ValueError:
                                logger.error(f"api_id phải là số nguyên, nhận được: {api_id}")
            
            return (None, None, None)
        except Exception as e:
            logger.error(f"Lỗi khi đọc cấu hình Telethon: {str(e)}")
            return (None, None, None)
    
    def send_video_with_telethon(self, chat_id, video_path, caption=None, progress_callback=None):
        """
        Gửi video qua Telethon API
        
        Args:
            chat_id: ID của chat
            video_path: Đường dẫn đến video
            caption: Chú thích cho video
            progress_callback: Callback để cập nhật tiến trình
            
        Returns:
            bool: True nếu gửi thành công, False nếu không
        """
        try:
            # Tạo instance của TelethonUploader nếu chưa có
            if not self.telethon_uploader:
                # Import TelethonUploader
                from utils.telethon_uploader import TelethonUploader
                self.telethon_uploader = TelethonUploader()
                
                # Lấy cấu hình Telethon
                api_id, api_hash, phone = self.get_telethon_config()
                if not api_id or not api_hash or not phone:
                    logger.error("Không tìm thấy đủ cấu hình Telethon (api_id, api_hash, phone)")
                    return False
                
                # Login vào Telethon
                self.telethon_uploader.api_id = api_id
                self.telethon_uploader.api_hash = api_hash
                self.telethon_uploader.phone = phone
                
                # Khởi tạo client với cấu hình đã lấy được
                try:
                    if not self.telethon_uploader.client:
                        import asyncio
                        from telethon import TelegramClient
                        
                        # Đảm bảo có event loop
                        if not hasattr(self.telethon_uploader, 'loop') or not self.telethon_uploader.loop:
                            try:
                                self.telethon_uploader.loop = asyncio.get_event_loop()
                            except RuntimeError:
                                self.telethon_uploader.loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(self.telethon_uploader.loop)
                        
                        # Tạo session path
                        session_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'telegram_uploader')
                        
                        # Tạo client
                        self.telethon_uploader.client = TelegramClient(
                            session_path, 
                            api_id, 
                            api_hash,
                            loop=self.telethon_uploader.loop
                        )
                except Exception as e:
                    logger.error(f"Lỗi khi khởi tạo Telethon client: {str(e)}")
                    import traceback
                    logger.error(f"Stack trace: {traceback.format_exc()}")
            
            # Đánh dấu đã kết nối để bỏ qua các kiểm tra kết nối
            self.telethon_uploader.connected = True
            
            # Tải video lên với force=True để bỏ qua các kiểm tra kết nối
            result = self.telethon_uploader.upload_video(
                chat_id,
                video_path,
                caption=caption,
                progress_callback=progress_callback,
                force=True
            )
            
            return result
        except ImportError as e:
            logger.error(f"Lỗi import module Telethon: {str(e)}")
            from tkinter import messagebox
            messagebox.showerror(
                "Lỗi tải lên",
                f"Không thể tải lên video qua Telethon API do thiếu module cần thiết: {str(e)}.\n\n"
                f"Vui lòng cài đặt thư viện 'telethon' và thử lại."
            )
            return False
        except Exception as e:
            logger.error(f"Lỗi khi gửi video qua Telethon: {str(e)}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            from tkinter import messagebox
            messagebox.showerror(
                "Lỗi tải lên",
                f"Lỗi khi tải lên video qua Telethon API: {str(e)}."
            )
            return False
    
    def send_video(self, chat_id, video_path, caption=None, width=None, height=None, duration=None, disable_notification=False, progress_callback=None):
        """
        Gửi video đến Telegram chat/channel
        
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
            # Tính kích thước video
            video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            video_name = os.path.basename(video_path)
            
            logger.info(f"Kiểm tra video {video_name}: kích thước = {video_size_mb:.2f} MB")
            
            # Đọc use_telethon từ config
            use_telethon = self.get_config_use_telethon()
            logger.info(f"Cấu hình: use_telethon = {use_telethon}")
            
            # Kiểm tra video lớn và use_telethon = True
            if use_telethon and video_size_mb > 50:
                logger.info(f"✅ Video lớn ({video_size_mb:.2f} MB) + use_telethon=True -> Sử dụng Telethon")
                
                # Thông báo chuyển hướng
                from tkinter import messagebox
                messagebox.showinfo(
                    "Thông báo", 
                    f"Video '{video_name}' có kích thước {video_size_mb:.2f} MB sẽ được tải lên qua Telethon API."
                )
                
                # Sử dụng phương thức mới để gửi qua Telethon
                return self.send_video_with_telethon(chat_id, video_path, caption, progress_callback)
            
            # Chuẩn bị caption nếu không cung cấp
            if not caption:
                file_name = os.path.basename(video_path)
                caption = f"📹 {file_name}\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Cập nhật tiến trình lên 10% (chuẩn bị)
            if progress_callback:
                progress_callback(10)
                
            # Kiểm tra kích thước để quyết định phương pháp tải lên
            if video_size_mb <= 50:
                # Tải lên trực tiếp cho video nhỏ
                logger.info(f"Video nhỏ hơn 50MB, tải lên trực tiếp: {video_name} ({video_size_mb:.2f} MB)")
                return self._send_video_direct(chat_id, video_path, caption, width, height, duration, disable_notification)
            else:
                # Kiểm tra lại use_telethon một lần nữa - ĐIỂM CHẶN QUAN TRỌNG
                use_telethon = self.get_config_use_telethon()
                if use_telethon:
                    # KHÔNG ĐƯỢC PHÉP CHIA NHỎ VIDEO KHI use_telethon = True
                    logger.error(f"⛔ Video lớn ({video_size_mb:.2f} MB) + use_telethon=True, không được phép chia nhỏ")
                    
                    # Thông báo lỗi
                    from tkinter import messagebox
                    messagebox.showerror(
                        "Lỗi tải lên",
                        f"Video '{video_name}' có kích thước {video_size_mb:.2f} MB không thể được chia nhỏ khi bật tùy chọn 'Sử dụng Telethon API'.\n\n"
                        f"Vui lòng vào tab Cài đặt để đăng nhập Telethon API hoặc tắt tùy chọn này."
                    )
                    return False
                
                # Chỉ chia nhỏ nếu use_telethon = False
                logger.info(f"Video lớn + use_telethon=False -> Chia nhỏ video {video_name} ({video_size_mb:.2f} MB)")
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
        # KIỂM TRA CHẶT CHẼ use_telethon MỘT LẦN NỮA
        use_telethon = self.get_config_use_telethon()
        video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        video_name = os.path.basename(video_path)
        
        if use_telethon and video_size_mb > 50:
            logger.error(f"⛔ ĐIỂM CHẶN CUỐI CÙNG: Không được phép chia nhỏ video {video_name} ({video_size_mb:.2f} MB) khi use_telethon=True")
            from tkinter import messagebox
            messagebox.showerror(
                "Lỗi tải lên",
                f"Video '{video_name}' có kích thước {video_size_mb:.2f} MB không thể được chia nhỏ khi bật tùy chọn 'Sử dụng Telethon API'.\n\n"
                f"Vui lòng vào tab Cài đặt để đăng nhập Telethon API hoặc tắt tùy chọn này."
            )
            return False
            
        splitter = VideoSplitter()
        
        try:
            # Split the video into parts
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