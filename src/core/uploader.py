"""
Module xử lý tải lên video thủ công từ tab chính.
"""
import os
import time
import logging
import threading
import tkinter as tk
from tkinter import messagebox

logger = logging.getLogger("Uploader")

class Uploader:
    """
    Xử lý việc tải lên video thủ công từ giao diện.
    """
    
    def __init__(self, app):
        """
        Khởi tạo Uploader.
        
        Args:
            app: Đối tượng TelegramUploaderApp
        """
        self.app = app
    
    def start_upload(self, app):
        """Bắt đầu quá trình tải lên video"""
        # Kiểm tra điều kiện
        if app.is_uploading:
            return
        
        # Lấy danh sách video đã chọn qua checkboxes
        selected_videos = []
        for item in app.video_tree.get_children():
            check_var = app.video_checkboxes.get(item)
            if check_var and check_var.get():
                # Video đã được chọn qua checkbox
                video_name = app.video_tree.item(item, "values")[1]
                selected_videos.append(video_name)
        
        if not selected_videos:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một video để tải lên!")
            return
        
        # Kiểm tra cấu hình Telegram
        bot_token = app.config['TELEGRAM']['bot_token']
        chat_id = app.config['TELEGRAM']['chat_id']
        notification_chat_id = app.config['TELEGRAM']['notification_chat_id']
        
        if not bot_token or not chat_id:
            messagebox.showerror("Lỗi", "Vui lòng cấu hình Bot Token và Chat ID trong tab Cài đặt!")
            app.notebook.select(2)  # Chuyển đến tab Cài đặt
            return
        
        # Kết nối lại với Telegram nếu cần
        if not app.telegram_api.connected:
            if not app.telegram_api.connect(bot_token):
                messagebox.showerror("Lỗi", "Không thể kết nối với Telegram API. Vui lòng kiểm tra Bot Token và kết nối internet!")
                return
        
        # Bắt đầu quá trình tải lên
        app.is_uploading = True
        app.should_stop = False
        
        # Cập nhật trạng thái giao diện
        app.upload_btn.config(state=tk.DISABLED)
        app.stop_btn.config(state=tk.NORMAL)
        
        # Tạo và bắt đầu thread tải lên
        folder_path = app.folder_path.get()
        upload_thread = threading.Thread(
            target=self.upload_videos,
            args=(app, folder_path, selected_videos, chat_id, notification_chat_id)
        )
        upload_thread.daemon = True
        upload_thread.start()
    
    def upload_videos(self, app, folder_path, video_files, chat_id, notification_chat_id):
        """
        Tải lên các video trong thread riêng
        
        Args:
            app: Đối tượng TelegramUploaderApp
            folder_path (str): Đường dẫn thư mục
            video_files (list): Danh sách tên file video
            chat_id (str): ID chat Telegram đích
            notification_chat_id (str): ID chat để gửi thông báo
        """
        start_time = time.time()
        
        try:
            # Chuẩn bị thanh tiến trình
            total_videos = len(video_files)
            app.progress['maximum'] = total_videos
            app.progress['value'] = 0
            
            # Gửi thông báo bắt đầu
            start_message = f"🚀 Bắt đầu tải lên {total_videos} video"
            logger.info(start_message)
            
            if notification_chat_id:
                app.telegram_api.send_notification(notification_chat_id, start_message)
            
            # Thời gian chờ giữa các lần tải
            delay = int(app.config['SETTINGS'].get('delay_between_uploads', 5))
            
            # Biến để theo dõi kết quả tải lên
            successful_uploads = 0
            failed_uploads = 0
            skipped_uploads = 0
            
            # Kiểm tra cài đặt Telethon
            use_telethon = app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
            
            # Tải lên từng video
            for index, video_file in enumerate(video_files):
                if app.should_stop:
                    logger.info("Đã dừng quá trình tải lên theo yêu cầu")
                    break
                
                try:
                    # Đường dẫn đầy đủ đến file video
                    video_path = os.path.join(folder_path, video_file)
                    
                    # Kiểm tra kết nối internet
                    if not app.telegram_api.check_internet_connection():
                        error_msg = "Mất kết nối internet. Đang chờ kết nối lại..."
                        app.status_var.set(error_msg)
                        app.root.update_idletasks()
                        
                        # Chờ kết nối internet
                        while not app.telegram_api.check_internet_connection() and not app.should_stop:
                            time.sleep(5)
                            app.status_var.set(f"{error_msg} (đã chờ {(time.time() - start_time):.0f}s)")
                            app.root.update_idletasks()
                        
                        if app.should_stop:
                            break
                    
                    # Cập nhật trạng thái
                    status_text = f"Đang tải lên {index + 1}/{total_videos}: {video_file}"
                    app.status_var.set(status_text)
                    app.root.update_idletasks()
                    
                    # Kiểm tra kích thước file
                    file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                    
                    # Quyết định sử dụng Bot API hay Telethon
                    success = False
                    if use_telethon and file_size > 49 and app.telethon_uploader.connected:
                        # Sử dụng Telethon cho file lớn
                        logger.info(f"Sử dụng Telethon API để tải lên file lớn: {video_file} ({file_size:.2f} MB)")
                        app.status_var.set(f"Đang tải lên qua Telethon: {video_file}")
                        app.root.update_idletasks()
                        
                        success = app.telethon_uploader.upload_video(chat_id, video_path)
                    else:
                        # Sử dụng Bot API
                        success = app.telegram_api.send_video(chat_id, video_path)
                    
                    if success:
                        log_message = f"✅ Đã tải lên thành công: {video_file}"
                        logger.info(log_message)
                        successful_uploads += 1
                        
                        # Thêm vào lịch sử
                        video_hash = app.video_analyzer.calculate_video_hash(video_path)
                        if video_hash:
                            file_size = os.path.getsize(video_path)
                            app.upload_history.add_upload(video_hash, video_file, video_path, file_size)
                    else:
                        log_message = f"❌ Tải lên thất bại: {video_file}"
                        logger.error(log_message)
                        failed_uploads += 1
                    
                    # Cập nhật tiến trình
                    app.progress['value'] = index + 1
                    app.root.update_idletasks()
                    
                    # Chờ giữa các lần tải lên để tránh rate limit
                    if index < total_videos - 1 and not app.should_stop:
                        time.sleep(delay)
                
                except Exception as e:
                    logger.error(f"Lỗi khi tải lên video {video_file}: {str(e)}")
                    failed_uploads += 1
                    
                    # Cập nhật trạng thái lỗi
                    app.status_var.set(f"Lỗi khi tải lên {video_file}: {str(e)}")
                    app.root.update_idletasks()
                    time.sleep(2)  # Hiển thị thông báo lỗi trong 2 giây
            
            # Hoàn tất
            if app.should_stop:
                app.status_var.set(f"Đã dừng tải lên ({successful_uploads} thành công, {failed_uploads} thất bại)")
                
                if notification_chat_id:
                    app.telegram_api.send_notification(
                        notification_chat_id, 
                        f"🛑 Đã dừng tải lên ({successful_uploads} thành công, {failed_uploads} thất bại)"
                    )
            else:
                app.status_var.set(f"Đã hoàn tất: {successful_uploads} thành công, {failed_uploads} thất bại")
                
                if notification_chat_id:
                    app.telegram_api.send_notification(
                        notification_chat_id, 
                        f"✅ Đã hoàn tất tải lên: {successful_uploads} thành công, {failed_uploads} thất bại"
                    )
                
                # Làm mới thống kê lịch sử
                from ui.history_tab import refresh_history_stats
                refresh_history_stats(app)
        
        except Exception as e:
            import traceback
            logger.error(f"Lỗi trong quá trình tải lên: {str(e)}")
            logger.error(traceback.format_exc())
            app.status_var.set(f"Lỗi: {str(e)}")
        
        finally:
            # Cập nhật trạng thái
            app.is_uploading = False
            
            # Cập nhật giao diện
            app.upload_btn.config(state=tk.NORMAL)
            app.stop_btn.config(state=tk.DISABLED)
    
    def stop_upload(self, app):
        """Dừng quá trình tải lên"""
        if app.is_uploading:
            app.should_stop = True
            app.status_var.set("Đang dừng tải lên...")
            logger.info("Đã yêu cầu dừng quá trình tải lên")