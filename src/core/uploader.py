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
        self.progress_dialog = None
    
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
        
        # Khởi tạo dialog tiến trình
        from utils.upload_progress_dialog import UploadProgressDialog
        self.progress_dialog = UploadProgressDialog(app.root, "Đang tải lên video", len(selected_videos))
        
        # Cập nhật tên video trong dialog
        for i, video_name in enumerate(selected_videos):
            self.progress_dialog.update_video_name(i, video_name)
        
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
        try:
            total_videos = len(video_files)
            successful_uploads = 0
            failed_uploads = 0
            
            # Cập nhật giao diện
            app.status_var.set(f"Đang tải lên {total_videos} video...")
            
            # Lấy thời gian chờ giữa các lần tải lên
            try:
                delay = int(app.config['SETTINGS']['delay_between_uploads'])
            except:
                delay = 5  # Mặc định 5 giây
            
            # Kiểm tra nên dùng Telethon hay không
            use_telethon = app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
            
            # Gửi thông báo bắt đầu tải lên
            if notification_chat_id:
                app.telegram_api.send_notification(
                    notification_chat_id, 
                    f"📤 Bắt đầu tải lên {total_videos} video"
                )
            
            # Tải lên từng video
            for index, video_file in enumerate(video_files):
                # Kiểm tra xem có yêu cầu dừng không
                if app.should_stop or (self.progress_dialog and self.progress_dialog.is_cancelled):
                    break
                
                # Đường dẫn đầy đủ
                video_path = os.path.join(folder_path, video_file)
                
                # Kiểm tra tệp có tồn tại không
                if not os.path.exists(video_path) or not os.path.isfile(video_path):
                    logger.error(f"Không tìm thấy video: {video_file}")
                    
                    # Cập nhật trạng thái thất bại
                    if self.progress_dialog:
                        self.progress_dialog.complete_video(index, success=False)
                    
                    failed_uploads += 1
                    continue
                
                # Cập nhật dialog tiến trình
                if self.progress_dialog:
                    self.progress_dialog.set_current_video(index, video_file)
                
                try:
                    # Cập nhật trạng thái
                    app.status_var.set(f"Đang tải lên video {index + 1}/{total_videos}: {video_file}")
                    
                    # Lấy kích thước file để xác định phương thức tải lên
                    file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                    
                    # Quyết định sử dụng Bot API hay Telethon
                    success = False
                    if use_telethon and file_size > 49 and app.telethon_uploader.connected:
                        # Sử dụng Telethon cho file lớn
                        logger.info(f"Sử dụng Telethon API để tải lên file lớn: {video_file} ({file_size:.2f} MB)")
                        app.status_var.set(f"Đang tải lên qua Telethon: {video_file}")
                        
                        # Định nghĩa callback tiến trình
                        def progress_callback(progress):
                            if self.progress_dialog:
                                self.progress_dialog.update_part_progress(1, progress)
                        
                        # Tải lên với callback tiến trình
                        success = app.telethon_uploader.upload_video(
                            chat_id, 
                            video_path, 
                            progress_callback=progress_callback
                        )
                    else:
                        # Thiết lập callback tiến trình cho video chia nhỏ
                        def video_split_callback(part_current, part_total, progress=None):
                            if self.progress_dialog:
                                self.progress_dialog.set_video_parts(part_total)
                                if progress is not None:
                                    self.progress_dialog.update_part_progress(part_current, progress)
                                else:
                                    self.progress_dialog.update_part_progress(part_current, 100)
                        
                        # Sử dụng Bot API với callback chia nhỏ
                        success = app.telegram_api.send_video(
                            chat_id, 
                            video_path,
                            split_callback=video_split_callback
                        )
                    
                    if success:
                        log_message = f"✅ Đã tải lên thành công: {video_file}"
                        logger.info(log_message)
                        successful_uploads += 1
                        
                        # Cập nhật dialog
                        if self.progress_dialog:
                            self.progress_dialog.complete_video(index, success=True)
                        
                        # Thêm vào lịch sử
                        video_hash = app.video_analyzer.calculate_video_hash(video_path)
                        if video_hash:
                            file_size = os.path.getsize(video_path)
                            app.upload_history.add_upload(video_hash, video_file, video_path, file_size)
                    else:
                        log_message = f"❌ Tải lên thất bại: {video_file}"
                        logger.error(log_message)
                        failed_uploads += 1
                        
                        # Cập nhật dialog
                        if self.progress_dialog:
                            self.progress_dialog.complete_video(index, success=False)
                    
                    # Cập nhật tiến trình
                    app.progress['value'] = index + 1
                    app.root.update_idletasks()
                    
                    # Chờ giữa các lần tải lên để tránh rate limit
                    if index < total_videos - 1 and not app.should_stop and not (self.progress_dialog and self.progress_dialog.is_cancelled):
                        time.sleep(delay)
                
                except Exception as e:
                    logger.error(f"Lỗi khi tải lên video {video_file}: {str(e)}")
                    failed_uploads += 1
                    
                    # Cập nhật dialog
                    if self.progress_dialog:
                        self.progress_dialog.complete_video(index, success=False)
                    
                    # Cập nhật trạng thái lỗi
                    app.status_var.set(f"Lỗi khi tải lên {video_file}: {str(e)}")
                    app.root.update_idletasks()
                    time.sleep(2)  # Hiển thị thông báo lỗi trong 2 giây
            
            # Đánh dấu hoàn tất cho dialog
            if self.progress_dialog:
                self.progress_dialog.complete_all()
            
            # Hoàn tất
            if app.should_stop or (self.progress_dialog and self.progress_dialog.is_cancelled):
                app.status_var.set(f"Đã dừng tải lên ({successful_uploads} thành công, {failed_uploads} thất bại)")
            else:
                app.status_var.set(f"Đã hoàn tất: {successful_uploads} thành công, {failed_uploads} thất bại")
                
                # Làm mới thống kê lịch sử
                from ui.history_tab import refresh_history_stats
                refresh_history_stats(app)
        
        except Exception as e:
            import traceback
            logger.error(f"Lỗi trong quá trình tải lên: {str(e)}")
            logger.error(traceback.format_exc())
            app.status_var.set(f"Lỗi: {str(e)}")
            
            # Đóng dialog nếu có lỗi
            if self.progress_dialog:
                self.progress_dialog.dialog.destroy()
        
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
            
            # Cập nhật dialog nếu đang hiển thị
            if self.progress_dialog:
                self.progress_dialog.cancel_upload()