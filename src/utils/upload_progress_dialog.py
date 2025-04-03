"""
Module hiển thị tiến trình tải lên dưới dạng cửa sổ modal.
"""
import tkinter as tk
from tkinter import ttk
import time
import threading
import logging
from PIL import Image, ImageTk

logger = logging.getLogger("UploadProgressDialog")

class UploadProgressDialog:
    """
    Cửa sổ modal hiển thị tiến trình tải lên video lên Telegram.
    Hỗ trợ hiển thị tiến trình tải từng phần khi video được chia nhỏ.
    """
    
    def __init__(self, parent, title="Đang tải lên", total_videos=1):
        """
        Khởi tạo dialog tiến trình tải lên
        
        Args:
            parent: Cửa sổ cha (Tkinter window)
            title: Tiêu đề cửa sổ
            total_videos: Tổng số video cần tải lên
        """
        self.parent = parent
        self.title = title
        self.total_videos = total_videos
        self.current_video = 0
        self.current_part = 0
        self.total_parts = 1
        self.is_cancelled = False
        self.dialog = None
        self.progress_bars = []
        self.status_labels = []
        self.progress_vars = []
        self.icon_labels = []
        self.status_vars = []
        self.video_names = []
        
        # Biểu tượng
        self.icon_pending = "⏳"
        self.icon_loading = "⌛"
        self.icon_success = "✅"
        self.icon_error = "❌"
        
        # Khởi tạo modal
        self.create_dialog()
    
    def create_dialog(self):
        """Tạo dialog tiến trình"""
        # Tạo top level window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        
        # Thiết lập thuộc tính modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Đặt kích thước và vị trí
        window_width = 600
        window_height = 300 + min(self.total_videos * 40, 300)
        
        # Đặt vị trí giữa màn hình
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        self.dialog.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Không cho phép thay đổi kích thước
        self.dialog.resizable(False, False)
        
        # Khóa đóng cửa sổ bằng nút X
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Frame chính
        main_frame = ttk.Frame(self.dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        ttk.Label(
            main_frame,
            text="Tiến trình tải lên video lên Telegram",
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 15))
        
        # Tiến trình tổng thể
        ttk.Label(
            main_frame,
            text="Tiến trình tổng thể:",
            font=("Arial", 10, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.overall_var = tk.DoubleVar(value=0)
        self.overall_progress = ttk.Progressbar(
            main_frame,
            variable=self.overall_var,
            length=550,
            mode="determinate"
        )
        self.overall_progress.pack(fill=tk.X, pady=(0, 15))
        
        # Tạo frame có thanh cuộn cho danh sách video
        scrollable_frame = ttk.Frame(main_frame)
        scrollable_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Canvas và scrollbar
        canvas = tk.Canvas(scrollable_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scrollable_frame, orient="vertical", command=canvas.yview)
        
        self.videos_frame = ttk.Frame(canvas)
        
        # Cấu hình canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Đặt videos_frame vào canvas
        canvas_window = canvas.create_window((0, 0), window=self.videos_frame, anchor="nw", width=550)
        
        # Đặt canvas và scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tạo các tiến trình cho từng video
        for i in range(self.total_videos):
            # Frame cho mỗi video
            video_frame = ttk.Frame(self.videos_frame)
            video_frame.pack(fill=tk.X, pady=5)
            
            # Biểu tượng trạng thái
            icon_label = ttk.Label(video_frame, text=self.icon_pending, font=("Arial", 12))
            icon_label.pack(side=tk.LEFT, padx=(0, 10))
            self.icon_labels.append(icon_label)
            
            # Frame thông tin
            info_frame = ttk.Frame(video_frame)
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Tên video
            video_name_var = tk.StringVar(value=f"Video {i+1}")
            self.video_names.append(video_name_var)
            
            ttk.Label(
                info_frame,
                textvariable=video_name_var,
                font=("Arial", 9, "bold")
            ).pack(anchor=tk.W, pady=(0, 2))
            
            # Thanh tiến trình
            progress_var = tk.DoubleVar(value=0)
            self.progress_vars.append(progress_var)
            
            progress_bar = ttk.Progressbar(
                info_frame,
                variable=progress_var,
                length=450,
                mode="determinate"
            )
            progress_bar.pack(fill=tk.X, pady=(0, 2))
            self.progress_bars.append(progress_bar)
            
            # Trạng thái
            status_var = tk.StringVar(value="Đang chờ...")
            self.status_vars.append(status_var)
            
            status_label = ttk.Label(info_frame, textvariable=status_var, font=("Arial", 8))
            status_label.pack(anchor=tk.W)
            self.status_labels.append(status_label)
        
        # Nút hủy/đóng
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)
        
        self.cancel_btn = ttk.Button(
            button_frame,
            text="Hủy",
            command=self.cancel_upload,
            width=15
        )
        self.cancel_btn.pack()
    
    def on_close(self):
        """Xử lý khi đóng cửa sổ"""
        if not self.is_cancelled and self.current_video < self.total_videos:
            if tk.messagebox.askyesno("Xác nhận", "Bạn có chắc muốn hủy quá trình tải lên?"):
                self.cancel_upload()
                self.dialog.destroy()
        else:
            self.dialog.destroy()
    
    def cancel_upload(self):
        """Hủy quá trình tải lên"""
        self.is_cancelled = True
        self.cancel_btn.config(state=tk.DISABLED)
        
        # Cập nhật trạng thái các video chưa tải
        for i in range(self.current_video, self.total_videos):
            self.status_vars[i].set("Đã hủy")
            self.icon_labels[i].config(text=self.icon_error)
            
        # Thông báo hủy tải
        logger.info("Người dùng đã hủy quá trình tải lên video")
    
    def update_video_name(self, index, name):
        """Cập nhật tên video"""
        if 0 <= index < len(self.video_names):
            self.video_names[index].set(name)
    
    def set_current_video(self, index, name):
        """Đặt video hiện tại đang tải lên"""
        self.current_video = index
        self.update_video_name(index, name)
        self.status_vars[index].set("Đang tải lên...")
        self.icon_labels[index].config(text=self.icon_loading)
        self.update_overall_progress()
    
    def set_video_parts(self, total_parts):
        """Đặt tổng số phần của video hiện tại"""
        self.total_parts = max(1, total_parts)
        self.current_part = 0
    
    def update_part_progress(self, part_index, progress):
        """Cập nhật tiến trình của phần hiện tại"""
        self.current_part = part_index
        
        # Tính toán tiến trình tổng thể của video hiện tại
        overall_video_progress = ((part_index - 1) + progress/100) / self.total_parts * 100
        
        # Cập nhật hiển thị
        if 0 <= self.current_video < len(self.progress_vars):
            self.progress_vars[self.current_video].set(overall_video_progress)
            
            # Cập nhật trạng thái
            if self.total_parts > 1:
                self.status_vars[self.current_video].set(f"Phần {part_index}/{self.total_parts} ({progress:.0f}%)")
            else:
                self.status_vars[self.current_video].set(f"{progress:.0f}%")
        
        self.update_overall_progress()
    
    def complete_video(self, index, success=True):
        """Đánh dấu video đã hoàn tất"""
        if 0 <= index < len(self.status_vars):
            if success:
                self.status_vars[index].set("Hoàn tất")
                self.icon_labels[index].config(text=self.icon_success)
                self.progress_vars[index].set(100)
            else:
                self.status_vars[index].set("Lỗi")
                self.icon_labels[index].config(text=self.icon_error)
        
        self.update_overall_progress()
    
    def update_overall_progress(self):
        """Cập nhật tiến trình tổng thể"""
        if self.total_videos > 0:
            # Tính toán tiến trình dựa trên số video đã hoàn thành và tiến trình video hiện tại
            completed_progress = self.current_video * 100
            
            if self.current_video < self.total_videos:
                current_progress = self.progress_vars[self.current_video].get()
                completed_progress += current_progress
            
            overall = completed_progress / self.total_videos
            self.overall_var.set(overall)
    
    def complete_all(self):
        """Đánh dấu tất cả quá trình đã hoàn tất"""
        self.current_video = self.total_videos
        self.overall_var.set(100)
        self.cancel_btn.config(text="Đóng", command=self.dialog.destroy)
        
        # Cập nhật UI
        self.dialog.title("Hoàn tất tải lên") 