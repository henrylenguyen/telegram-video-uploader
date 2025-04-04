"""
Module quản lý tự động tải lên video.
"""
import os
import time
import logging
import threading
from tkinter import messagebox
import tkinter as tk
from utils.auto_uploader import AutoUploader, BulkUploader

logger = logging.getLogger("AutoUploaderManager")

class AutoUploaderManager:
    """
    Quản lý việc tự động tải lên video.
    """
    
    def __init__(self, app):
        """
        Khởi tạo AutoUploaderManager.
        
        Args:
            app: Đối tượng TelegramUploaderApp
        """
        self.app = app
    
    def safe_update_ui(self, app, func, *args, **kwargs):
        """
        Cập nhật UI an toàn từ thread không phải main thread
        
        Args:
            app: Đối tượng TelegramUploaderApp
            func: Hàm cập nhật UI
            *args, **kwargs: Tham số cho hàm
        """
        app.root.after(0, lambda: func(*args, **kwargs))
    
    def start_auto_upload(self, app):
        """Bắt đầu chế độ tự động tải lên"""
        # Kiểm tra chế độ tự động được chọn
        if app.auto_mode_var.get() == "bulk":
            self.start_bulk_upload(app)
            return
        
        # Phần còn lại của mã hiện tại cho chế độ theo dõi
        # Kiểm tra điều kiện
        if app.auto_upload_active:
            return
        
        # Kiểm tra thư mục
        folder_path = app.auto_folder_path.get()
        if not folder_path or not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            messagebox.showerror("Lỗi", "Thư mục không hợp lệ hoặc không tồn tại!")
            return
        
        # Kiểm tra cấu hình Telegram
        bot_token = app.config['TELEGRAM']['bot_token']
        chat_id = app.config['TELEGRAM']['chat_id']
        
        if not bot_token or not chat_id:
            messagebox.showerror("Lỗi", "Vui lòng cấu hình Bot Token và Chat ID trong tab Cài đặt!")
            app.notebook.select(2)  # Chuyển đến tab Cài đặt
            return
        
        # Kết nối lại với Telegram nếu cần
        if not app.telegram_api.connected:
            if not app.telegram_api.connect(bot_token):
                messagebox.showerror("Lỗi", "Không thể kết nối với Telegram API. Vui lòng kiểm tra Bot Token và kết nối internet!")
                return
        
        # Lấy cài đặt tự động
        try:
            check_interval = int(app.check_interval_var.get())
            if check_interval < 5:
                messagebox.showwarning("Cảnh báo", "Thời gian kiểm tra quá ngắn có thể gây tải nặng cho hệ thống. Khuyến nghị ít nhất 30 giây.")
                check_interval = max(5, check_interval)  # Đảm bảo ít nhất 5 giây
        except ValueError:
            messagebox.showerror("Lỗi", "Thời gian kiểm tra phải là một số nguyên!")
            return
        
        # Lấy danh sách phần mở rộng
        extensions = app.config['SETTINGS']['video_extensions'].split(',')
        
        # Cập nhật trạng thái giao diện
        app.auto_upload_active = True
        app.start_auto_btn.config(state=tk.DISABLED)
        app.stop_auto_btn.config(state=tk.NORMAL)
        app.bulk_upload_btn.config(state=tk.DISABLED)
        app.auto_status_var.set("Tự động tải lên: Hoạt động")
        
        # Thêm log
        self.add_auto_log(app, "Bắt đầu chế độ tự động tải lên")
        self.add_auto_log(app, f"Thư mục giám sát: {folder_path}")
        self.add_auto_log(app, f"Thời gian kiểm tra: {check_interval} giây")
        self.add_auto_log(app, f"Kiểm tra trùng lặp: {'Bật' if app.auto_check_duplicates_var.get() else 'Tắt'}")
        self.add_auto_log(app, f"Kiểm tra với lịch sử: {'Bật' if app.auto_check_history_var.get() else 'Tắt'}")
        
        # Khởi tạo AutoUploader nếu chưa có
        if not app.auto_uploader:
            app.auto_uploader = AutoUploader(app, app.video_analyzer)
            app.auto_uploader.set_log_callback(lambda msg: self.add_auto_log(app, msg))
        
        # Bắt đầu tự động tải lên
        app.auto_uploader.start(
            folder_path=folder_path,
            extensions=extensions,
            check_interval=check_interval,
            check_duplicates=app.auto_check_duplicates_var.get(),
            check_history=app.auto_check_history_var.get()
        )
        
        # Lưu cài đặt
        app.config['SETTINGS']['auto_mode'] = 'true'
        app.config['SETTINGS']['auto_check_interval'] = str(check_interval)
        app.config['SETTINGS']['check_duplicates'] = str(app.auto_check_duplicates_var.get()).lower()
        app.config_manager.save_config(app.config)
    
    def start_bulk_upload(self, app):
        """Bắt đầu quá trình tải lên hàng loạt"""
        # Kiểm tra điều kiện
        if app.auto_upload_active:
            messagebox.showwarning("Cảnh báo", "Chế độ tự động đang hoạt động. Vui lòng dừng lại trước.")
            return
        
        # Kiểm tra thư mục
        folder_path = app.auto_folder_path.get()
        if not folder_path or not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            messagebox.showerror("Lỗi", "Thư mục không hợp lệ hoặc không tồn tại!")
            return
        
        # Kiểm tra cấu hình Telegram
        bot_token = app.config['TELEGRAM']['bot_token']
        chat_id = app.config['TELEGRAM']['chat_id']
        
        if not bot_token or not chat_id:
            messagebox.showerror("Lỗi", "Vui lòng cấu hình Bot Token và Chat ID trong tab Cài đặt!")
            app.notebook.select(2)  # Chuyển đến tab Cài đặt
            return
        
        # Kết nối lại với Telegram nếu cần
        if not app.telegram_api.connected:
            if not app.telegram_api.connect(bot_token):
                messagebox.showerror("Lỗi", "Không thể kết nối với Telegram API. Vui lòng kiểm tra Bot Token và kết nối internet!")
                return
        
        # Lấy danh sách phần mở rộng
        extensions = app.config['SETTINGS']['video_extensions'].split(',')
        
        # Xác nhận từ người dùng
        if not messagebox.askyesno(
            "Xác nhận", 
            f"Ứng dụng sẽ quét và tải lên tất cả video từ thư mục:\n{folder_path}\n\nBạn có chắc muốn tiếp tục?"
        ):
            return
        
        # Khởi tạo BulkUploader nếu chưa có
        if not app.bulk_uploader:
            app.bulk_uploader = BulkUploader(app, app.video_analyzer)
            app.bulk_uploader.set_log_callback(lambda msg: self.add_auto_log(app, msg))
            app.bulk_uploader.set_progress_callback(lambda progress: self.update_bulk_progress(app, progress))
        
        # Cập nhật trạng thái
        app.auto_upload_active = True
        app.start_auto_btn.config(state=tk.DISABLED)
        app.stop_auto_btn.config(state=tk.NORMAL)
        app.bulk_upload_btn.config(state=tk.DISABLED)
        app.auto_status_var.set("Đang tải lên hàng loạt...")
        
        # Thêm log
        self.add_auto_log(app, "Bắt đầu quét và tải lên hàng loạt")
        
        # Bắt đầu quá trình quét và tải lên
        success = app.bulk_uploader.scan_and_upload(
            folder_path=folder_path,
            extensions=extensions,
            check_duplicates=app.auto_check_duplicates_var.get(),
            check_history=app.auto_check_history_var.get()
        )
        
        if not success:
            self.add_auto_log(app, "Không thể bắt đầu quá trình tải lên hàng loạt")
            app.auto_upload_active = False
            app.start_auto_btn.config(state=tk.NORMAL)
            app.bulk_upload_btn.config(state=tk.NORMAL)
            app.stop_auto_btn.config(state=tk.DISABLED)
            app.auto_status_var.set("Tự động tải lên: Tắt")
    
    def update_bulk_progress(self, app, progress):
        """Cập nhật tiến trình tải lên hàng loạt"""
        # Cập nhật thanh tiến trình an toàn 
        # qua main thread để tránh lỗi thread
        def _update():
            if progress >= 100:
                app.auto_status_var.set("Đã hoàn tất tải lên hàng loạt")
                app.auto_upload_active = False
                app.start_auto_btn.config(state=tk.NORMAL)
                app.bulk_upload_btn.config(state=tk.NORMAL)
                app.stop_auto_btn.config(state=tk.DISABLED)
                
                # Cập nhật thống kê lịch sử
                from ui.history_tab import refresh_history_stats
                refresh_history_stats(app)
            else:
                app.auto_status_var.set(f"Đang tải lên hàng loạt: {progress}%")
        
        self.safe_update_ui(app, _update)
    
    def stop_auto_upload(self, app):
        """Dừng chế độ tự động tải lên"""
        if not app.auto_upload_active:
            return
        
        # Dừng AutoUploader nếu đang hoạt động
        if app.auto_uploader:
            app.auto_uploader.stop()
        
        # Dừng BulkUploader nếu đang hoạt động
        if app.bulk_uploader:
            app.bulk_uploader.stop()
        
        # Cập nhật trạng thái
        app.auto_upload_active = False
        
        # Cập nhật giao diện
        app.start_auto_btn.config(state=tk.NORMAL)
        app.stop_auto_btn.config(state=tk.DISABLED)
        app.bulk_upload_btn.config(state=tk.NORMAL)
        app.auto_status_var.set("Tự động tải lên: Tắt")
        
        # Thêm log
        self.add_auto_log(app, "Đã dừng chế độ tự động tải lên")
        
        # Lưu cài đặt
        app.config['SETTINGS']['auto_mode'] = 'false'
        app.config_manager.save_config(app.config)
    
    def add_auto_log(self, app, message):
        """
        Thêm thông báo vào nhật ký tự động
        
        Args:
            app: Đối tượng TelegramUploaderApp
            message (str): Thông báo cần thêm
        """
        # Kiểm tra xem log đã được bật chưa
        if not hasattr(app, 'auto_log_var') or not app.auto_log_var.get():
            return
        
        # Đưa việc cập nhật UI vào main thread
        def update_log():
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            
            # Thêm vào Text widget
            app.auto_log_text.config(state=tk.NORMAL)
            app.auto_log_text.insert(tk.END, log_entry)
            app.auto_log_text.see(tk.END)  # Cuộn xuống dòng cuối
            app.auto_log_text.config(state=tk.DISABLED)
        
        self.safe_update_ui(app, update_log)
        
        # Thêm vào log chung
        logger.info(f"[AUTO] {message}")
    
    def set_log_callback(self, callback):
        """
        Đặt callback để ghi log
        
        Args:
            callback (function): Hàm callback nhận chuỗi log
        """
        self.log_callback = callback
    
    # Cập nhật lại _on_new_file để xử lý thread safety
    def _on_new_file(self, file_path):
        """
        Xử lý khi phát hiện file mới
        
        Args:
            file_path (str): Đường dẫn đến file mới
        """
        # Kiểm tra xem file đã được xử lý chưa
        if file_path in self.processed_files:
            return
            
        # Gọi log callback an toàn qua main thread
        if self.log_callback:
            self.log_callback(f"Đã phát hiện file mới: {os.path.basename(file_path)}")
        else:
            logger.info(f"Đã phát hiện file mới: {os.path.basename(file_path)}")
        
        # Kiểm tra lịch sử tải lên nếu cần
        if self.check_history and self.upload_history and self.video_analyzer:
            try:
                # Tính hash của video
                video_hash = self.video_analyzer.calculate_video_hash(file_path)
                
                # Kiểm tra xem video đã tồn tại trong lịch sử chưa
                if video_hash and self.upload_history.is_uploaded(video_hash):
                    if self.log_callback:
                        self.log_callback(f"Bỏ qua video đã tải lên trước đó: {os.path.basename(file_path)}")
                    else:
                        logger.info(f"Bỏ qua video đã tải lên trước đó: {os.path.basename(file_path)}")
                    
                    # Đánh dấu là đã xử lý để không xử lý lại
                    self.processed_files.add(file_path)
                    return
            except Exception as e:
                logger.error(f"Lỗi khi kiểm tra lịch sử video {os.path.basename(file_path)}: {str(e)}")
        
        # Thêm vào hàng đợi tải lên
        self.upload_queue.put(file_path)