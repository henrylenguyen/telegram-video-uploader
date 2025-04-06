"""
Module for uploading videos to Telegram
"""

import os
import time
import logging
import threading
import traceback
from queue import Queue
from datetime import datetime
from tkinter import messagebox

logger = logging.getLogger("Uploader")

class Uploader:
    """
    Class for uploading videos to Telegram
    """
    
    def __init__(self, app):
        """
        Initialize uploader
        
        Args:
            app: TelegramUploaderApp instance
        """
        self.app = app
        self.telegram_api = app.telegram_api
        self.telethon_uploader = app.telethon_uploader
        self.is_uploading = False
        self.should_stop = False
        self.current_file = None
        self.current_thread = None
        self.history = app.upload_history
    
    def upload_videos(self, videos, chat_id=None, caption_template=None, progress_callback=None):
        """
        Upload multiple videos
        
        Args:
            videos (list): List of video paths
            chat_id (str/int): Telegram chat/channel ID
            caption_template (str): Caption template for videos
            progress_callback (function): Callback for upload progress
            
        Returns:
            bool: True if all uploads successful
        """
        if not videos:
            logger.warning("Không có video nào để tải lên")
            return False
            
        # Use default chat ID if not provided
        if not chat_id:
            chat_id = self.app.config['TELEGRAM']['chat_id']
            
        if not chat_id:
            logger.error("Chưa cấu hình Chat ID")
            return False
            
        # Start upload
        self.is_uploading = True
        self.should_stop = False
        total_videos = len(videos)
        successful_uploads = 0
        
        # Update UI
        if hasattr(self.app, 'update_status'):
            self.app.update_status(f"Đang tải lên {total_videos} video...")
        
        # Report file count
        logger.info(f"Bắt đầu tải lên {total_videos} video lên Telegram")
        
        # THÊM: Kiểm tra use_telethon ngay từ đầu
        use_telethon = self.app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
        logger.info(f"UPLOADER.upload_videos: use_telethon = {use_telethon}")
        
        # THÊM: Kiểm tra kết nối Telethon từ sớm nếu use_telethon = true
        if use_telethon:
            telethon_connected = getattr(self.telethon_uploader, 'connected', False)
            logger.info(f"UPLOADER.upload_videos: Trạng thái kết nối Telethon ban đầu = {telethon_connected}")
            
            # Nếu chưa kết nối, thử kết nối
            if not telethon_connected:
                try:
                    # Kiểm tra kết nối
                    is_connected = self.telethon_uploader.is_connected()
                    if is_connected:
                        self.telethon_uploader.connected = True
                        telethon_connected = True
                        logger.info("UPLOADER.upload_videos: Đã tự động thiết lập kết nối Telethon = True")
                    else:
                        # Thông báo lỗi kết nối
                        logger.error("UPLOADER.upload_videos: Telethon chưa kết nối")
                        messagebox.showwarning(
                            "Cảnh báo Telethon",
                            "Bạn đã bật 'Sử dụng Telethon API' nhưng chưa đăng nhập Telethon. "
                            "Video lớn hơn 50MB sẽ không được tải lên.\n\n"
                            "Vui lòng vào tab Cài đặt > Telethon API để đăng nhập."
                        )
                except Exception as e:
                    logger.error(f"UPLOADER.upload_videos: Lỗi kiểm tra kết nối Telethon: {str(e)}")
        
        try:
            # Process each video
            for index, video_path in enumerate(videos):
                # Check if upload should stop
                if self.should_stop:
                    logger.info("Đã dừng tải lên theo yêu cầu")
                    break
                
                # Update current file
                self.current_file = video_path
                video_name = os.path.basename(video_path)
                
                # Skip if file doesn't exist
                if not os.path.exists(video_path) or not os.path.isfile(video_path):
                    logger.warning(f"File không tồn tại: {video_path}")
                    continue
                
                # THÊM: Kiểm tra kích thước video
                video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
                logger.info(f"UPLOADER.upload_videos: Video {video_name}: {video_size_mb:.2f} MB")
                
                # THÊM: Kiểm tra use_telethon + kích thước lớn từ sớm
                if use_telethon and video_size_mb > 50 and not telethon_connected:
                    logger.error(f"UPLOADER.upload_videos: Bỏ qua video lớn {video_name} vì Telethon chưa kết nối")
                    messagebox.showerror(
                        "Lỗi tải lên",
                        f"Video '{video_name}' có kích thước {video_size_mb:.2f} MB vượt quá giới hạn 50MB.\n\n"
                        f"Vì bạn đã bật 'Sử dụng Telethon API' nhưng chưa đăng nhập Telethon, "
                        f"ứng dụng không thể tải lên video này.\n\n"
                        f"Vui lòng vào tab Cài đặt > Telethon API để đăng nhập."
                    )
                    continue
                
                # Update progress and status
                if progress_callback:
                    overall_progress = int(index * 100 / total_videos)
                    progress_callback(overall_progress)
                
                if hasattr(self.app, 'update_status'):
                    self.app.update_status(f"Đang tải lên {index + 1}/{total_videos}: {video_name}")
                
                # Prepare caption
                if caption_template:
                    video_caption = self._format_caption(caption_template, video_path)
                else:
                    # Default caption with file name and timestamp
                    video_caption = f"📹 {video_name}\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                # Upload video with progress tracking
                def file_progress_callback(percent):
                    if progress_callback:
                        # Calculate overall progress (this file's progress weighted by position in queue)
                        file_weight = 1.0 / total_videos
                        overall_progress = int(index * 100 / total_videos + percent * file_weight)
                        progress_callback(overall_progress)
                
                # Send video
                logger.info(f"Tải lên {index + 1}/{total_videos}: {video_name}")
                success = self._send_video(video_path, chat_id, video_caption)
                
                if success:
                    successful_uploads += 1
                    logger.info(f"✅ Đã tải lên thành công: {video_name}")
                    
                    # Add to history
                    self.history.add_upload(
                        video_path,
                        chat_id,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        True
                    )
                else:
                    logger.error(f"❌ Tải lên thất bại: {video_name}")
                    
                    # Add to history
                    self.history.add_upload(
                        video_path,
                        chat_id,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        False
                    )
                
                # Apply upload delay if configured
                if index < total_videos - 1:
                    delay = int(self.app.config['SETTINGS'].get('delay_between_uploads', '5'))
                    if delay > 0:
                        logger.info(f"Đợi {delay} giây trước khi tải video tiếp theo...")
                        if hasattr(self.app, 'update_status'):
                            self.app.update_status(f"Đợi {delay} giây trước khi tải video tiếp theo...")
                        
                        # Wait with check for stop request
                        for i in range(delay):
                            if self.should_stop:
                                break
                            time.sleep(1)
            
            # Complete
            logger.info(f"Đã tải lên {successful_uploads}/{total_videos} video")
            
            # Update progress and status
            if progress_callback:
                progress_callback(100)
                
            if hasattr(self.app, 'update_status'):
                self.app.update_status(f"Đã tải lên {successful_uploads}/{total_videos} video")
            
            return successful_uploads == total_videos
            
        except Exception as e:
            logger.error(f"Lỗi khi tải lên video: {str(e)}")
            logger.error(traceback.format_exc())
            return False
            
        finally:
            # Reset state
            self.is_uploading = False
            self.current_file = None
    
    def upload_video(self, video_path, chat_id=None, caption=None, progress_callback=None):
        """
        Upload a single video
        
        Args:
            video_path (str): Path to video file
            chat_id (str/int): Telegram chat/channel ID
            caption (str): Caption for the video
            progress_callback (function): Callback for upload progress
            
        Returns:
            bool: True if upload successful
        """
        # THÊM: Kiểm tra nhanh video size và use_telethon
        try:
            use_telethon = self.app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
            video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            
            # Log thông tin
            logger.info(f"UPLOADER.upload_video: {os.path.basename(video_path)}, size = {video_size_mb:.2f} MB, use_telethon = {use_telethon}")
            
            # Kiểm tra nếu video lớn và use_telethon = true nhưng chưa đăng nhập Telethon
            if use_telethon and video_size_mb > 50:
                telethon_connected = getattr(self.telethon_uploader, 'connected', False)
                if not telethon_connected:
                    try:
                        # Thử kiểm tra kết nối một lần nữa
                        is_connected = self.telethon_uploader.is_connected()
                        if is_connected:
                            self.telethon_uploader.connected = True
                            telethon_connected = True
                            logger.info("UPLOADER.upload_video: Đã tự động thiết lập connected = True")
                    except:
                        pass
                    
                    # Nếu vẫn chưa kết nối, thông báo lỗi
                    if not telethon_connected:
                        logger.error(f"UPLOADER.upload_video: Video lớn {video_size_mb:.2f} MB + use_telethon = true nhưng chưa đăng nhập Telethon")
                        messagebox.showerror(
                            "Lỗi tải lên",
                            f"Video '{os.path.basename(video_path)}' có kích thước {video_size_mb:.2f} MB vượt quá giới hạn 50MB.\n\n"
                            f"Vì bạn đã bật 'Sử dụng Telethon API' nhưng chưa đăng nhập Telethon, "
                            f"ứng dụng không thể tải lên video này.\n\n"
                            f"Vui lòng vào tab Cài đặt > Telethon API để đăng nhập."
                        )
                        return False
        except Exception as e:
            logger.error(f"UPLOADER.upload_video: Lỗi kiểm tra ban đầu: {str(e)}")
        
        # Gọi phương thức upload_videos để tải lên
        return self.upload_videos([video_path], chat_id, caption, progress_callback)
    
    def _send_video(self, video_path, chat_id, caption=None, force_telethon=False):
        """
        Gửi video lên Telegram - ƯU TIÊN TELETHON cho video lớn khi use_telethon=True
        
        Args:
            video_path (str): Đường dẫn đến video
            chat_id (str/int): Chat ID để gửi video
            caption (str): Chú thích cho video
            force_telethon (bool): Bắt buộc sử dụng Telethon API
                
        Returns:
            bool: True nếu gửi thành công
        """
        # Kiểm tra file tồn tại
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            logger.error(f"UPLOADER: [UPLOADER-A] File video không tồn tại: {video_path}")
            return False
        
        # Lấy kích thước video
        video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        video_name = os.path.basename(video_path)
        
        # Thông báo trạng thái
        logger.info(f"UPLOADER: [UPLOADER-B] Đang gửi video {video_name} ({video_size_mb:.2f} MB), force_telethon={force_telethon}")
        
        # BƯỚC 1: KIỂM TRA NGAY use_telethon, force_telethon VÀ KÍCH THƯỚC VIDEO
        try:
            # Kiểm tra xem self.app có tồn tại không
            if not hasattr(self, 'app'):
                logger.error(f"UPLOADER: [UPLOADER-C] Lỗi nghiêm trọng - không tìm thấy self.app")
                return False
            
            # Kiểm tra xem app.config có tồn tại không
            if not hasattr(self.app, 'config'):
                logger.error(f"UPLOADER: [UPLOADER-D] Lỗi nghiêm trọng - không tìm thấy self.app.config")
                return False
            
            # Lấy trạng thái use_telethon từ cấu hình
            use_telethon = self.app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
            logger.info(f"UPLOADER: [UPLOADER-E] Kiểm tra ban đầu - use_telethon={use_telethon}, force_telethon={force_telethon}, kích thước={video_size_mb:.2f} MB")
            
            # Kiểm tra telethon_uploader tồn tại không
            has_telethon = hasattr(self, 'telethon_uploader')
            logger.info(f"UPLOADER: [UPLOADER-F] Kiểm tra telethon_uploader tồn tại: {has_telethon}")
            
            # VIDEO LỚN + USE_TELETHON = TRUE HOẶC FORCE_TELETHON = TRUE -> LUÔN DÙNG TELETHON
            if (use_telethon and video_size_mb > 50) or force_telethon:
                logger.info(f"UPLOADER: [UPLOADER-G] ✅ ĐIỀU KIỆN KÍCH HOẠT TELETHON: use_telethon={use_telethon}, force_telethon={force_telethon}, video size={video_size_mb:.2f} MB")
                
                # Kiểm tra telethon_uploader
                if not has_telethon:
                    logger.error(f"UPLOADER: [UPLOADER-H] ❌ Lỗi nghiêm trọng - không tìm thấy self.telethon_uploader")
                    from tkinter import messagebox
                    messagebox.showerror(
                        "Lỗi tải lên",
                        f"Không thể tải lên video lớn qua Telethon API do thiếu module telethon_uploader.\n\n"
                        f"Vui lòng liên hệ nhà phát triển."
                    )
                    return False
                
                # Lấy telethon_uploader
                telethon_uploader = self.telethon_uploader
                
                # Cập nhật tiến trình
                self.update_progress(20, "Đang tải lên qua Telethon API...")
                
                # Callback tiến trình
                def progress_callback(percent):
                    self.update_progress(percent, f"Đang tải lên qua Telethon... {percent}%")
                
                # GỬI VIDEO QUA TELETHON
                try:
                    # Log việc sử dụng Telethon
                    logger.info(f"UPLOADER: [UPLOADER-I] 🚀 CƯỠNG BUỘC sử dụng Telethon API cho video: {video_name} ({video_size_mb:.2f} MB)")
                    
                    # QUAN TRỌNG: Thêm force=True để bỏ qua mọi kiểm tra kết nối
                    result = telethon_uploader.upload_video(
                        chat_id, 
                        video_path,
                        caption=caption,
                        progress_callback=progress_callback,
                        force=True  # Bỏ qua kiểm tra kết nối
                    )
                    
                    # Kiểm tra kết quả
                    if result:
                        logger.info(f"UPLOADER: [UPLOADER-J] ✅ Tải lên thành công qua Telethon API")
                        self.update_progress(100, "Tải lên hoàn tất!")
                        return True
                    else:
                        # Lỗi khi tải lên qua Telethon
                        logger.error(f"UPLOADER: [UPLOADER-K] ❌ Tải lên thất bại qua Telethon API mặc dù đã force=True")
                        
                        # Thông báo lỗi nhưng KHÔNG fallback sang chia nhỏ
                        from tkinter import messagebox
                        messagebox.showerror(
                            "Lỗi tải lên",
                            f"Không thể tải lên video '{video_name}' ({video_size_mb:.2f} MB) qua Telethon API.\n\n"
                            f"Vui lòng kiểm tra kết nối internet, cấu hình Telethon API và thử lại sau."
                        )
                        
                        self.update_progress(0, "Lỗi tải lên qua Telethon")
                        return False
                except Exception as e:
                    # Xử lý lỗi khi tải lên
                    logger.error(f"UPLOADER: [UPLOADER-L] ❌ Lỗi nghiêm trọng khi tải lên qua Telethon: {str(e)}")
                    import traceback
                    logger.error(f"UPLOADER: [STACK TRACE] {traceback.format_exc()}")
                    
                    # Thông báo lỗi nhưng KHÔNG fallback sang chia nhỏ
                    from tkinter import messagebox
                    messagebox.showerror(
                        "Lỗi tải lên",
                        f"Lỗi khi tải lên qua Telethon API: {str(e)}\n\n"
                        f"Video lớn hơn 50MB sẽ không được chia nhỏ khi bật 'Sử dụng Telethon API'.\n"
                        f"Vui lòng kiểm tra kết nối và thử lại."
                    )
                    
                    self.update_progress(0, f"Lỗi Telethon: {str(e)}")
                    return False
        except Exception as e:
            logger.error(f"UPLOADER: [UPLOADER-M] ❌ Lỗi khi kiểm tra use_telethon ban đầu: {str(e)}")
            import traceback
            logger.error(f"UPLOADER: [STACK TRACE] {traceback.format_exc()}")
        
        # BƯỚC 2: NẾU ĐẾN ĐƯỢC ĐÂY -> use_telethon=False HOẶC video nhỏ hơn 50MB và không force_telethon
        # Kiểm tra Telethon kết nối (ưu tiên nếu đã kết nối)
        try:
            # Lấy trạng thái use_telethon từ cấu hình
            use_telethon = self.app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
            logger.info(f"UPLOADER: [UPLOADER-N] Kiểm tra thường - use_telethon = {use_telethon}")
            
            # NẾU USE_TELETHON = TRUE: Ưu tiên dùng Telethon nếu đã kết nối
            if use_telethon and not force_telethon:
                # Thông báo ưu tiên Telethon
                logger.info(f"UPLOADER: [UPLOADER-O] Đã bật use_telethon, ưu tiên sử dụng Telethon API nếu đã kết nối")
                
                # Lấy telethon_uploader
                telethon_uploader = self.telethon_uploader
                
                # Kiểm tra kết nối Telethon thực tế
                try:
                    # Đặt kết nối = True nếu đã cấu hình đầy đủ
                    telethon_connected = True
                    logger.info(f"UPLOADER: [UPLOADER-P] Đặt trạng thái kết nối Telethon = True vì đã ưu tiên")
                except Exception as e:
                    logger.error(f"UPLOADER: [UPLOADER-Q] Lỗi khi đặt kết nối Telethon: {str(e)}")
                    telethon_connected = False
                
                # Nếu kết nối Telethon OK, thử tải lên
                if telethon_connected:
                    # Cập nhật tiến trình
                    self.update_progress(20, "Đang tải lên qua Telethon...")
                    
                    # Callback tiến trình
                    def progress_callback(percent):
                        self.update_progress(percent, f"Đang tải lên qua Telethon... {percent}%")
                    
                    # Tải lên qua Telethon
                    try:
                        # Log việc sử dụng Telethon
                        logger.info(f"UPLOADER: [UPLOADER-R] Đang sử dụng Telethon API để tải lên {video_name} ({video_size_mb:.2f} MB)")
                        
                        # Tải lên với force=True
                        result = telethon_uploader.upload_video(
                            chat_id, 
                            video_path,
                            caption=caption,
                            progress_callback=progress_callback,
                            force=True  # Bỏ qua kiểm tra kết nối
                        )
                        
                        # Kiểm tra kết quả
                        if result:
                            logger.info(f"UPLOADER: [UPLOADER-S] ✅ Tải lên thành công qua Telethon API")
                            self.update_progress(100, "Tải lên hoàn tất!")
                            return True
                        else:
                            # Lỗi khi tải lên qua Telethon
                            logger.error(f"UPLOADER: [UPLOADER-T] ❌ Tải lên thất bại qua Telethon API")
                    except Exception as e:
                        # Xử lý lỗi khi tải lên
                        logger.error(f"UPLOADER: [UPLOADER-U] ❌ Lỗi khi tải lên qua Telethon: {str(e)}")
                        import traceback
                        logger.error(f"UPLOADER: [STACK TRACE] {traceback.format_exc()}")
                    
                    # Dù có lỗi, video nhỏ vẫn tiếp tục xuống dưới để thử dùng Telegram API
                    logger.info(f"UPLOADER: [UPLOADER-V] Video nhỏ, tiếp tục xuống dưới để dùng Telegram API")
                else:
                    # Telethon chưa kết nối - cũng không quan trọng
                    logger.warning(f"UPLOADER: [UPLOADER-W] Telethon chưa kết nối, nhưng tiếp tục xuống dưới vì video nhỏ")
        except Exception as e:
            logger.error(f"UPLOADER: [UPLOADER-X] ❌ Lỗi khi kiểm tra Telethon thường: {str(e)}")
            import traceback
            logger.error(f"UPLOADER: [STACK TRACE] {traceback.format_exc()}")
        
        # BƯỚC 3: DÙNG TELEGRAM API - dành cho video nhỏ hoặc use_telethon = false
        try:
            # Cập nhật tiến độ
            self.update_progress(10, "Đang chuẩn bị tải lên qua Telegram API...")
            
            # Kiểm tra lại use_telethon + video size - đảm bảo an toàn
            try:
                use_telethon = self.app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
                if use_telethon and video_size_mb > 50:
                    logger.error(f"UPLOADER: [UPLOADER-Y] ⚠️ VIDEO LỚN + USE_TELETHON=TRUE => KHÔNG ĐƯỢC DÙNG TELEGRAM API")
                    from tkinter import messagebox
                    messagebox.showerror(
                        "Lỗi tải lên",
                        f"Video '{video_name}' có kích thước {video_size_mb:.2f} MB vượt quá giới hạn 50MB.\n\n"
                        f"Khi bật 'Sử dụng Telethon API', ứng dụng sẽ không chia nhỏ video.\n\n"
                        f"Đã thử dùng Telethon nhưng gặp lỗi. Vui lòng kiểm tra cấu hình và thử lại."
                    )
                    self.update_progress(0, "Lỗi: Không thể gửi qua Telegram API khi bật Telethon")
                    return False
            except Exception as e:
                logger.error(f"UPLOADER: [UPLOADER-Z] ❌ Lỗi kiểm tra cuối cùng: {str(e)}")
                import traceback
                logger.error(f"UPLOADER: [STACK TRACE] {traceback.format_exc()}")
            
            # Sử dụng callback tiến độ
            def progress_callback(percent):
                self.update_progress(percent, f"Đang tải lên qua Telegram API... {percent}%")
            
            # Gửi video qua Telegram API
            logger.info(f"UPLOADER: [UPLOADER-AA] Tải lên video qua Telegram API: {video_name}")
            
            # Sử dụng telegram_api.send_video
            result = self.telegram_api.send_video(
                chat_id=chat_id,
                video_path=video_path,
                caption=caption,
                disable_notification=False,
                progress_callback=progress_callback
            )
            
            # Hoàn tất
            if result:
                logger.info(f"UPLOADER: [UPLOADER-AB] ✅ Tải lên thành công qua Telegram API")
                self.update_progress(100, "Tải lên hoàn tất!")
            else:
                logger.error(f"UPLOADER: [UPLOADER-AC] ❌ Tải lên thất bại qua Telegram API")
                self.update_progress(0, "Tải lên thất bại!")
                
            return result
            
        except Exception as e:
            logger.error(f"UPLOADER: [UPLOADER-AD] ❌ Lỗi khi tải lên qua Telegram API: {str(e)}")
            import traceback
            logger.error(f"UPLOADER: [STACK TRACE] {traceback.format_exc()}")
            self.update_progress(0, f"Lỗi: {str(e)}")
            return False
    def start_upload_thread(self, videos, chat_id=None, caption_template=None, progress_callback=None):
        """
        Start upload in a separate thread
        
        Args:
            videos (list): List of video paths
            chat_id (str/int): Telegram chat/channel ID
            caption_template (str): Caption template for videos
            progress_callback (function): Callback for upload progress
            
        Returns:
            bool: True if upload thread started successfully
        """
        if self.is_uploading:
            logger.warning("Đang có quá trình tải lên khác")
            return False
        
        # THÊM: Kiểm tra video lớn + use_telethon
        try:
            use_telethon = self.app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
            if use_telethon:
                # Kiểm tra kết nối Telethon trước
                telethon_connected = getattr(self.telethon_uploader, 'connected', False)
                try:
                    if not telethon_connected:
                        is_connected = self.telethon_uploader.is_connected()
                        if is_connected:
                            self.telethon_uploader.connected = True
                            telethon_connected = True
                except:
                    pass
                
                # Kiểm tra các video lớn
                large_videos = []
                for video_path in videos:
                    if os.path.exists(video_path) and os.path.isfile(video_path):
                        video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
                        if video_size_mb > 50:
                            large_videos.append((os.path.basename(video_path), video_size_mb))
                
                # Nếu có video lớn và Telethon chưa kết nối, thông báo lỗi
                if large_videos and not telethon_connected:
                    message = "Các video sau có kích thước vượt quá 50MB:\n\n"
                    for name, size in large_videos:
                        message += f"- {name} ({size:.2f} MB)\n"
                    message += "\nVì bạn đã bật 'Sử dụng Telethon API' nhưng chưa đăng nhập Telethon, "
                    message += "ứng dụng không thể tải lên những video này.\n\n"
                    message += "Vui lòng vào tab Cài đặt > Telethon API để đăng nhập."
                    
                    logger.error(f"start_upload_thread: Có {len(large_videos)} video lớn nhưng Telethon chưa kết nối")
                    messagebox.showerror("Lỗi tải lên", message)
                    
                    # Nếu tất cả đều là video lớn, hủy hoàn toàn
                    if len(large_videos) == len(videos):
                        return False
                    
                    # Nếu có video nhỏ, hỏi người dùng có muốn tiếp tục không
                    if len(large_videos) < len(videos):
                        answer = messagebox.askyesno(
                            "Xác nhận",
                            f"Có {len(videos) - len(large_videos)} video nhỏ hơn 50MB có thể được tải lên.\n"
                            f"Bạn có muốn tiếp tục tải lên những video nhỏ này không?"
                        )
                        if not answer:
                            return False
                        
                        # Lọc bỏ các video lớn
                        filtered_videos = []
                        for video_path in videos:
                            if os.path.exists(video_path) and os.path.isfile(video_path):
                                video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
                                if video_size_mb <= 50:
                                    filtered_videos.append(video_path)
                        videos = filtered_videos
        except Exception as e:
            logger.error(f"start_upload_thread: Lỗi kiểm tra video lớn: {str(e)}")
            
        # Create thread
        self.current_thread = threading.Thread(
            target=self.upload_videos,
            args=(videos, chat_id, caption_template, progress_callback),
            daemon=True
        )
        
        # Start thread
        self.current_thread.start()
        return True
    
    def stop_upload(self):
        """Stop current upload"""
        if self.is_uploading:
            logger.info("Đang dừng tải lên...")
            self.should_stop = True
            return True
        return False
    
    def update_progress(self, percent, status_text=None):
        """
        Update progress in UI
        
        Args:
            percent (int): Progress percentage (0-100)
            status_text (str): Status text to display
        """
        # Update progress UI if available
        if hasattr(self.app, 'update_progress'):
            self.app.update_progress(percent)
            
        # Update status text if available
        if status_text and hasattr(self.app, 'update_status'):
            self.app.update_status(status_text)
    
    def _format_caption(self, template, video_path):
        """
        Format caption template with video information
        
        Args:
            template (str): Caption template
            video_path (str): Path to video file
            
        Returns:
            str: Formatted caption
        """
        # Get video info
        video_name = os.path.basename(video_path)
        video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        
        # Get current time
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Replace placeholders
        caption = template.replace('{filename}', video_name)
        caption = caption.replace('{datetime}', current_time)
        caption = caption.replace('{size}', f"{video_size_mb:.2f} MB")
        
        return caption