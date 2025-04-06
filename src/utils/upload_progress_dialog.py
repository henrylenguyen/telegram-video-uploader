"""
Module hiển thị tiến trình tải lên dưới dạng cửa sổ modal.
"""
import tkinter as tk
from tkinter import ttk
import time
import threading
import logging
from PIL import Image, ImageTk
from ui.components.progress_animation import (
    create_animation_for_progress_bar,
    ICON_PENDING, ICON_PROCESSING, ICON_SUCCESS, ICON_ERROR
)

logger = logging.getLogger("UploadProgressDialog")

class UploadProgressDialog:
    """
    Cửa sổ modal hiển thị tiến trình tải lên video lên Telegram.
    Phiên bản cải tiến với thanh tiến trình sinh động.
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
        self.animations = []  # Lưu các đối tượng animation
        
        # Biểu tượng
        self.icon_pending = ICON_PENDING
        self.icon_loading = ICON_PROCESSING
        self.icon_success = ICON_SUCCESS
        self.icon_error = ICON_ERROR
        
        # Khởi tạo modal
        self.create_dialog()
    
    def create_dialog(self):
        """Tạo dialog tiến trình với kích thước lớn hơn cho các button"""
        # Tạo top level window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Đặt kích thước và vị trí
        window_width = 650  # Rộng hơn một chút
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
            length=600,  # Dài hơn một chút
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
        canvas_window = canvas.create_window((0, 0), window=self.videos_frame, anchor="nw", width=600)
        
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
                length=480,  # Dài hơn một chút
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
            
            # Tạo animation manager cho từng video
            animation = create_animation_for_progress_bar(
                parent=self.dialog,
                progress_var=progress_var,
                status_label=status_var,
                callback=self._on_progress_update
            )
            self.animations.append(animation)
        
        # Frame nút
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        
        # Container cho nút với kích thước cố định
        btn_container = ttk.Frame(btn_frame, width=150, height=40)  # Kích thước lớn hơn cho nút
        btn_container.pack_propagate(False)  # Giữ kích thước
        btn_container.pack()
        
        # Nút hủy/đóng (đảm bảo luôn hiển thị đầy đủ chữ)
        self.cancel_btn = ttk.Button(
            btn_container,
            text="Hủy tải lên",  # Tên dài hơn, rõ ràng hơn
            command=self.cancel_upload
        )
        self.cancel_btn.pack(fill=tk.BOTH, expand=True)
    
    def _on_progress_update(self, progress):
        """Callback khi tiến trình thay đổi, cập nhật tiến trình tổng thể"""
        self.update_overall_progress()
    
    def on_close(self):
        """Xử lý khi đóng cửa sổ"""
        if not self.is_cancelled and self.current_video < self.total_videos:
            if tk.messagebox.askyesno("Xác nhận", "Bạn có chắc muốn hủy quá trình tải lên?"):
                self.cancel_upload()
                self.dialog.destroy()
        else:
            # Hủy tất cả animation
            for animation in self.animations:
                animation.cleanup()
            
            self.dialog.destroy()
    
    def cancel_upload(self):
        """Hủy quá trình tải lên"""
        self.is_cancelled = True
        self.cancel_btn.config(text="Đang hủy...", state=tk.DISABLED)
        
        # Hủy tất cả animation
        for animation in self.animations:
            animation.cancel()
        
        # Cập nhật trạng thái các video chưa tải
        for i in range(self.current_video, self.total_videos):
            self.status_vars[i].set("Đã hủy")
            self.icon_labels[i].config(text=self.icon_error)
        
        # Thay đổi nút
        self.cancel_btn.config(text="Đóng cửa sổ", state=tk.NORMAL, command=self.dialog.destroy)
            
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
        
        # Sử dụng after để đảm bảo cập nhật UI từ main thread
        self.dialog.after(0, lambda: self.status_vars[index].set("Đang tải lên..."))
        self.dialog.after(0, lambda: self.icon_labels[index].config(text=self.icon_loading))
        self.dialog.after(0, self.update_overall_progress)
        
        # Bắt đầu animation tiến trình
        if 0 <= index < len(self.animations):
            self.animations[index].start_animation(0, "Đang tải lên... ")
    
    def set_video_parts(self, total_parts):
        """Đặt tổng số phần của video hiện tại"""
        self.total_parts = max(1, total_parts)
        self.current_part = 0
    
    def update_part_progress(self, part_index, progress):
        """
        Cập nhật tiến trình của phần hiện tại
        
        Args:
            part_index: Chỉ số phần hiện tại (1-based)
            progress: Giá trị tiến trình (0-100)
        """
        self.current_part = part_index
        
        # Tính toán tiến trình tổng thể của video hiện tại
        overall_video_progress = ((part_index - 1) + progress/100) / self.total_parts * 100
        
        # Cập nhật hiển thị thông qua main thread
        def update_ui():
            if 0 <= self.current_video < len(self.progress_vars):
                self.progress_vars[self.current_video].set(overall_video_progress)
                
                # Cập nhật trạng thái
                if self.total_parts > 1:
                    self.status_vars[self.current_video].set(f"Phần {part_index}/{self.total_parts} ({progress:.0f}%)")
                else:
                    self.status_vars[self.current_video].set(f"{progress:.0f}%")
            
            self.update_overall_progress()
        
        self.dialog.after(0, update_ui)
    
    def complete_video(self, index, success=True):
        """Đánh dấu video đã hoàn tất"""
        if 0 <= index < len(self.animations):
            # Dừng animation và đặt trạng thái hoàn tất
            completion_text = "Hoàn tất" if success else "Lỗi"
            self.animations[index].set_completed(success, completion_text)
            
            # Cập nhật icon và UI khác
            def update_ui():
                if 0 <= index < len(self.icon_labels):
                    icon = self.icon_success if success else self.icon_error
                    self.icon_labels[index].config(text=icon)
                self.update_overall_progress()
            
            self.dialog.after(0, update_ui)
    
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
        # Dừng tất cả animation
        for animation in self.animations:
            animation.cleanup()
        
        def update_ui():
            self.current_video = self.total_videos
            self.overall_var.set(100)
            
            # Đảm bảo nút hiển thị đầy đủ chữ
            button_text = "Đóng cửa sổ"  # Dài hơn để đảm bảo button đủ rộng
            self.cancel_btn.config(text=button_text, command=self.dialog.destroy)
            self.dialog.title("Hoàn tất tải lên")
        
        self.dialog.after(0, update_ui)