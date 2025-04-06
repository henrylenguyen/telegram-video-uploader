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
        return self.upload_videos([video_path], chat_id, caption, progress_callback)
    
    def _send_video(self, video_path, chat_id, caption=None):
        """Gửi video lên Telegram"""
        # DIRECT TELETHON UPLOAD - Bỏ qua mọi logic khác
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        if file_size_mb > 50:  # Chỉ sử dụng cho file lớn
            logger.info(f"DIRECT TELETHON: Phát hiện video lớn ({file_size_mb:.2f} MB), thử sử dụng Telethon trực tiếp")
            try:
                # Kiểm tra trạng thái Telethon
                use_telethon = self.app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
                if use_telethon and hasattr(self.app, 'telethon_uploader'):
                    telethon_uploader = self.app.telethon_uploader
                    
                    # BYPASS - Tự động thiết lập connected = True nếu is_connected() thành công
                    try:
                        is_connected = telethon_uploader.is_connected()
                        if is_connected:
                            telethon_uploader.connected = True
                            logger.info("DIRECT TELETHON: Tự động đặt connected = True vì is_connected() = True")
                    except:
                        pass
                        
                    # Kiểm tra kết nối Telethon
                    telethon_connected = getattr(telethon_uploader, 'connected', False)
                    logger.info(f"DIRECT TELETHON: Trạng thái kết nối = {telethon_connected}")
                        
                    if telethon_connected:
                        # Cập nhật tiến trình
                        self.update_progress(20, "Đang tải lên qua Telethon...")
                        
                        # Sử dụng callback tiến trình
                        def progress_callback(percent):
                            self.update_progress(percent, f"Đang tải lên... {percent}%")
                        
                        # Tải lên qua Telethon
                        logger.info(f"DIRECT TELETHON: Đang tải lên video {os.path.basename(video_path)}")
                        result = telethon_uploader.upload_video(
                            chat_id, 
                            video_path,
                            caption=caption,
                            progress_callback=progress_callback
                        )
                        
                        if result:
                            logger.info(f"DIRECT TELETHON: Tải lên thành công!")
                            self.update_progress(100, "Tải lên hoàn tất!")
                            return True
                        else:
                            logger.error(f"DIRECT TELETHON: Tải lên thất bại, quay lại phương pháp thông thường")
            except Exception as e:
                logger.error(f"DIRECT TELETHON: Lỗi - {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Mã gốc: sử dụng Telegram API
        try:
            # Cập nhật tiến độ
            self.update_progress(10, "Đang chuẩn bị tải lên...")
            
            # Sử dụng callback tiến độ
            def progress_callback(percent):
                self.update_progress(percent, f"Đang tải lên... {percent}%")
            
            # Gửi video qua Telegram API
            logger.info(f"Tải lên video qua Telegram API: {os.path.basename(video_path)}")
            
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
                self.update_progress(100, "Tải lên hoàn tất!")
            else:
                self.update_progress(0, "Tải lên thất bại!")
                
            return result
            
        except Exception as e:
            logger.error(f"Lỗi khi tải lên video: {str(e)}")
            logger.error(traceback.format_exc())
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