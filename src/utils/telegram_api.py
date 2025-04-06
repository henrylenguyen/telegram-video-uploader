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
        
        # NGAY TỪ ĐẦU: Kiểm tra use_telethon và kích thước video để quyết định luồng xử lý
        try:
            video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            video_name = os.path.basename(video_path)
            
            # Log thông tin để debug - THÊM ĐIỂM KIỂM TRA MỚI
            logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA A] Kiểm tra ban đầu, video size = {video_size_mb:.2f} MB")
            
            # Kiểm tra use_telethon từ cấu hình
            import sys
            main_module = sys.modules['__main__']
            if hasattr(main_module, 'app'):
                app = main_module.app
                use_telethon = app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
                
                logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA B] use_telethon = {use_telethon}")
                
                # ĐIỀU KIỆN QUAN TRỌNG: Log chi tiết
                if video_size_mb > 50:
                    logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA C] Video lớn hơn 50MB ({video_size_mb:.2f} MB)")
                    
                if use_telethon:
                    logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA D] use_telethon = True")
                
                # ĐIỀU KIỆN QUAN TRỌNG: Nếu use_telethon=True và video lớn, chuyển hướng sang uploader
                if use_telethon and video_size_mb > 50:
                    logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA E] ✅ VIDEO LỚN + USE_TELETHON=TRUE => BUỘC CHUYỂN HƯỚNG")
                    
                    # Thông báo cho người dùng
                    from tkinter import messagebox
                    messagebox.showinfo(
                        "Thông báo", 
                        f"Video '{video_name}' có kích thước {video_size_mb:.2f} MB sẽ được tải lên qua Telethon API."
                    )
                    
                    # Kiểm tra sự tồn tại của uploader và telethon_uploader
                    has_uploader = hasattr(app, 'uploader')
                    has_telethon = hasattr(app, 'telethon_uploader')
                    logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA F] has_uploader={has_uploader}, has_telethon={has_telethon}")
                    
                    # CHUYỂN HƯỚNG SANG UPLOADER để dùng Telethon - NẾU CÓ
                    if has_uploader:
                        logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA G] 🚀 Chuyển hướng sang app.uploader._send_video")
                        try:
                            # TRỰC TIẾP gọi _send_video với force_telethon=True
                            # Thêm tham số mới để đảm bảo luôn dùng Telethon
                            if hasattr(app.uploader, '_send_video'):
                                # Thử gọi với tham số force_telethon
                                try:
                                    logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA H] Gọi _send_video với force_telethon=True")
                                    result = app.uploader._send_video(video_path, chat_id, caption, force_telethon=True)
                                    logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA I] Kết quả từ uploader._send_video: {result}")
                                    return result
                                except TypeError:
                                    # Nếu không nhận tham số force_telethon
                                    logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA J] Gọi _send_video không có force_telethon")
                                    result = app.uploader._send_video(video_path, chat_id, caption)
                                    logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA K] Kết quả từ uploader._send_video: {result}")
                                    return result
                            else:
                                logger.error(f"TELEGRAM_API: [ĐIỂM KIỂM TRA L] ❌ Không tìm thấy phương thức _send_video")
                        except Exception as e:
                            logger.error(f"TELEGRAM_API: [ĐIỂM KIỂM TRA M] ❌ Lỗi khi gọi uploader._send_video: {str(e)}")
                            import traceback
                            logger.error(f"TELEGRAM_API: [STACK TRACE] {traceback.format_exc()}")
                    
                    # Dự phòng: Gọi trực tiếp telethon_uploader nếu uploader không tồn tại hoặc lỗi
                    if has_telethon:
                        logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA N] 🚀 Chuyển hướng sang app.telethon_uploader.upload_video")
                        try:
                            # Thêm force=True để bỏ qua kiểm tra kết nối
                            result = app.telethon_uploader.upload_video(
                                chat_id, 
                                video_path, 
                                caption=caption,
                                progress_callback=progress_callback,
                                force=True  # Đảm bảo bỏ qua kiểm tra kết nối
                            )
                            logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA O] Kết quả từ telethon_uploader.upload_video: {result}")
                            return result
                        except Exception as e:
                            logger.error(f"TELEGRAM_API: [ĐIỂM KIỂM TRA P] ❌ Lỗi khi gọi telethon_uploader.upload_video: {str(e)}")
                            import traceback
                            logger.error(f"TELEGRAM_API: [STACK TRACE] {traceback.format_exc()}")
                    
                    # Nếu không tìm thấy cả uploader và telethon_uploader, báo lỗi
                    logger.error(f"TELEGRAM_API: [ĐIỂM KIỂM TRA Q] ❌ Không tìm thấy uploader hoặc telethon_uploader")
                    messagebox.showerror(
                        "Lỗi tải lên",
                        f"Video '{video_name}' có kích thước {video_size_mb:.2f} MB vượt quá giới hạn 50MB.\n\n"
                        f"Đã bật 'Sử dụng Telethon API' nhưng không thể tìm thấy module Telethon.\n"
                        f"Vui lòng liên hệ nhà phát triển."
                    )
                    return False
                else:
                    logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA R] ❌ Không đủ điều kiện để chuyển hướng (use_telethon={use_telethon}, video size={video_size_mb:.2f} MB)")
        except Exception as e:
            logger.error(f"TELEGRAM_API: [ĐIỂM KIỂM TRA S] ❌ Lỗi khi kiểm tra ban đầu: {str(e)}")
            import traceback
            logger.error(f"TELEGRAM_API: [STACK TRACE] {traceback.format_exc()}")
        
        # NẾU KHÔNG DÙNG TELETHON HOẶC VIDEO NHỎ HƠN 50MB, TIẾP TỤC XỬ LÝ THÔNG THƯỜNG
        logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA T] Tiếp tục xử lý thông thường cho video {video_name}")
        
        try:
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
                logger.info(f"TELEGRAM_API: Video nhỏ hơn 50MB, tải lên trực tiếp: {video_name} ({video_size_mb:.2f} MB)")
                return self._send_video_direct(chat_id, video_path, caption, width, height, duration, disable_notification)
            else:
                # Kiểm tra lại use_telethon một lần nữa (phòng hờ) - THÊM LOG
                try:
                    import sys
                    main_module = sys.modules['__main__']
                    if hasattr(main_module, 'app'):
                        app = main_module.app
                        use_telethon = app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
                        
                        logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA U] Kiểm tra cuối cùng - use_telethon = {use_telethon}")
                        
                        if use_telethon:
                            # Không chia nhỏ nếu use_telethon = true
                            logger.error(f"TELEGRAM_API: [ĐIỂM KIỂM TRA V] ⚠️ FINAL CHECK - use_telethon = true, video lớn {video_size_mb:.2f} MB, không được chia nhỏ")
                            from tkinter import messagebox
                            messagebox.showerror(
                                "Lỗi tải lên",
                                f"Video '{video_name}' có kích thước {video_size_mb:.2f} MB vượt quá giới hạn 50MB.\n\n"
                                f"Vì bạn đã bật 'Sử dụng Telethon API', ứng dụng sẽ không chia nhỏ video.\n"
                                f"Vui lòng sử dụng chức năng tải lên qua Telethon hoặc tắt tùy chọn này."
                            )
                            return False
                except Exception as e:
                    logger.error(f"TELEGRAM_API: [ĐIỂM KIỂM TRA W] ❌ Lỗi khi kiểm tra use_telethon lần cuối: {str(e)}")
                    import traceback
                    logger.error(f"TELEGRAM_API: [STACK TRACE] {traceback.format_exc()}")
                
                # Nếu không bật use_telethon, chia nhỏ video
                logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA X] 🔄 Đang xử lý video lớn: {video_name} ({video_size_mb:.2f} MB)")
                return self._send_video_split(chat_id, video_path, caption, disable_notification, progress_callback)
            
        except Exception as e:
            logger.error(f"TELEGRAM_API: Lỗi khi gửi video {os.path.basename(video_path)}: {str(e)}")
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
        # KIỂM TRA USE_TELETHON MỘT LẦN NỮA - ĐIỂM KIỂM TRA CUỐI CÙNG
        try:
            video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            video_name = os.path.basename(video_path)
            
            logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA Split-A] Bắt đầu chia nhỏ video {video_name} ({video_size_mb:.2f} MB)")
            
            import sys
            main_module = sys.modules['__main__']
            if hasattr(main_module, 'app'):
                app = main_module.app
                use_telethon = app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
                
                logger.info(f"TELEGRAM_API: [ĐIỂM KIỂM TRA Split-B] Kiểm tra cuối cùng use_telethon = {use_telethon}")
                
                if use_telethon:
                    # CRITICAL: KHÔNG CHO PHÉP CHIA NHỎ VIDEO KHI use_telethon = True
                    logger.error(f"TELEGRAM_API: [ĐIỂM KIỂM TRA Split-C] ⛔️ VẪN CHẠY VÀO CHIA NHỎ - use_telethon = {use_telethon}, video lớn {video_size_mb:.2f} MB")
                    
                    from tkinter import messagebox
                    messagebox.showerror(
                        "Lỗi nghiêm trọng",
                        f"Phát hiện vấn đề nghiêm trọng: Video lớn không được chia nhỏ khi bật 'Sử dụng Telethon API'.\n\n"
                        f"Đây là lỗi hệ thống, vui lòng liên hệ nhà phát triển.\n\n"
                        f"Chi tiết: Video '{video_name}' ({video_size_mb:.2f} MB)"
                    )
                    return False
        except Exception as e:
            logger.error(f"TELEGRAM_API: [ĐIỂM KIỂM TRA Split-D] ❌ Lỗi khi kiểm tra use_telethon trong _send_video_split: {str(e)}")
            import traceback
            logger.error(f"TELEGRAM_API: [STACK TRACE] {traceback.format_exc()}")
        
        # Báo cáo kích thước video
        video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        logger.info(f"FORCE CHECK TELETHON: Video size = {video_size_mb:.2f} MB")
        
        # Tiếp tục logic chia nhỏ nếu không bật Telethon
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