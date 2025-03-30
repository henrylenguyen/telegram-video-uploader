"""
Lớp ứng dụng chính cho Telegram Video Uploader.
"""
import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from queue import Queue

# Import các module
from ui.splash_screen import show_splash_screen
from ui.main_tab import create_main_tab
from ui.auto_tab import create_auto_tab
from ui.settings_tab import create_settings_tab
from ui.history_tab import create_history_tab
from ui.log_tab import create_log_tab

from core.config_manager import ConfigManager
from core.uploader import Uploader
from core.auto_uploader import AutoUploaderManager
from core.telegram_connector import TelegramConnector

# Import các tiện ích
from utils.video_analyzer import VideoAnalyzer
from utils.upload_history import UploadHistory
from utils.ffmpeg_manager import FFmpegManager
from utils.telethon_uploader import TelethonUploader
from utils.auto_uploader import AutoUploader, BulkUploader

logger = logging.getLogger("TelegramUploader")

class TelegramUploaderApp:
    """
    Ứng dụng chính để tải video lên Telegram.
    """
    def __init__(self, root):
        """
        Khởi tạo ứng dụng.
        
        Args:
            root: Cửa sổ gốc Tkinter
        """
        self.root = root
        self.root.title("Telegram Video Uploader")
        
        # Thiết lập kích thước và vị trí cửa sổ
        self._setup_window()
        
        # Thiết lập style
        self._setup_styles()
        
        # Hiển thị splash screen
        show_splash_screen(self)
        
        # Khởi tạo các thành phần
        self._initialize_components()
        
        # Tạo giao diện
        self._create_ui()
        
        # Khi đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_window(self):
        """Thiết lập kích thước và vị trí cửa sổ"""
        # Lấy kích thước màn hình
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Thiết lập kích thước cửa sổ
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # Đặt vị trí cửa sổ vào giữa màn hình
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        # Áp dụng kích thước và vị trí
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.root.minsize(1024, 768)
        
        # Mở toàn màn hình khi bắt đầu (chỉ cho Windows)
        self.root.state('zoomed')
        
        # Thiết lập icon nếu có
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            logger.warning(f"Không thể đặt icon: {e}")
    
    def _setup_styles(self):
        """Thiết lập style cho các widget ttk"""
        style = ttk.Style()
        
        # Thiết lập font chung
        default_font = ("Segoe UI", 10)
        heading_font = ("Segoe UI", 11, "bold")
        
        # Thiết lập style cho button để tránh bị thu hẹp
        style.configure("TButton", padding=(10, 5), font=default_font)
        
        # Style cho label
        style.configure("TLabel", font=default_font)
        style.configure("Heading.TLabel", font=heading_font)
        
        # Style cho các cửa sổ chính
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabelframe", background="#f0f0f0", font=default_font)
        style.configure("TLabelframe.Label", font=heading_font)
        
        # Style cho Treeview
        style.configure("Treeview", font=default_font, rowheight=25)
        style.configure("Treeview.Heading", font=heading_font)
        
        # Style cho thanh trạng thái
        style.configure("Status.TLabel", font=default_font, foreground="#0066CC")
        
        # Style cho nút cảnh báo
        style.configure("Warning.TButton", foreground="red")
        
        # Style cho tab
        style.configure("TNotebook.Tab", font=default_font, padding=(10, 5))
    
    def _initialize_components(self):
        """Khởi tạo các thành phần của ứng dụng"""
        # Biến trạng thái
        self.is_uploading = False
        self.should_stop = False
        self.current_frames = []  # Lưu trữ các frame hiện tại
        self.auto_upload_active = False
        
        # Khởi tạo quản lý cấu hình
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # Khởi tạo các thành phần khác
        self.ffmpeg_manager = FFmpegManager()
        # Thiết lập FFmpeg
        self._setup_ffmpeg()
        
        history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload_history.json')
        self.upload_history = UploadHistory(history_file)
        
        self.video_analyzer = VideoAnalyzer()
        self.videos = {}  # Dict lưu thông tin video
        self.duplicate_groups = []  # Danh sách các nhóm video trùng lặp
        
        # Khởi tạo kết nối Telegram
        self.telegram_connector = TelegramConnector(self)
        self.telegram_api = self.telegram_connector.telegram_api
        self.telethon_uploader = self.telegram_connector.telethon_uploader
        
        # Khởi tạo quản lý tải lên
        self.uploader = Uploader(self)
        self.upload_queue = Queue()
        
        # Khởi tạo quản lý tải lên tự động
        self.auto_uploader_manager = AutoUploaderManager(self)
        self.auto_uploader = None
        self.bulk_uploader = None
        self.watcher_thread = None
        
        # Khởi tạo từ điển callbacks cho UI
        self.ui_callbacks = {
            'browse_folder': self._browse_folder,
            'refresh_video_list': self._refresh_video_list,
            'on_video_tree_click': self._on_video_tree_click,
            'on_video_select': self._on_video_select,
            'select_all_videos': self._select_all_videos,
            'deselect_all_videos': self._deselect_all_videos,
            'invert_video_selection': self._invert_video_selection,
            'play_selected_video': self._play_selected_video,
            'remove_duplicates': self._remove_duplicates
        }
    
    def _setup_ffmpeg(self):
        """Thiết lập FFmpeg"""
        # Hiển thị thông báo cho người dùng
        ffmpeg_info_dialog = tk.Toplevel(self.root)
        ffmpeg_info_dialog.title("Đang thiết lập FFmpeg")
        ffmpeg_info_dialog.geometry("400x150")
        ffmpeg_info_dialog.resizable(False, False)
        ffmpeg_info_dialog.transient(self.root)
        ffmpeg_info_dialog.grab_set()
        
        # Đặt vị trí vào giữa màn hình
        ffmpeg_info_dialog.update_idletasks()
        width = ffmpeg_info_dialog.winfo_width()
        height = ffmpeg_info_dialog.winfo_height()
        x = (ffmpeg_info_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (ffmpeg_info_dialog.winfo_screenheight() // 2) - (height // 2)
        ffmpeg_info_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Tạo giao diện
        main_frame = ttk.Frame(ffmpeg_info_dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Đang kiểm tra và cài đặt FFmpeg...", 
                 style="Heading.TLabel").pack(pady=(0, 10))
        
        # Thanh tiến trình
        progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode='indeterminate')
        progress.pack(fill=tk.X, pady=10)
        progress.start(10)
        
        # Nhãn trạng thái
        status_var = tk.StringVar(value="Đang kiểm tra...")
        status_label = ttk.Label(main_frame, textvariable=status_var, style="Status.TLabel")
        status_label.pack(pady=5)
        
        # Function để kiểm tra và cập nhật định kỳ
        def check_ffmpeg_status():
            # Lấy trạng thái từ FFmpegManager
            progress_value, status_text, is_downloading = self.ffmpeg_manager.get_download_status()
            status_var.set(status_text)
            
            # Nếu đã thiết lập xong hoặc lỗi
            if self.ffmpeg_manager.is_available or (not is_downloading and "Lỗi" in status_text):
                progress.stop()
                
                if self.ffmpeg_manager.is_available:
                    status_var.set("Đã cài đặt FFmpeg thành công!")
                    # Đóng cửa sổ sau 1 giây
                    ffmpeg_info_dialog.after(1000, ffmpeg_info_dialog.destroy)
                else:
                    status_var.set(status_text)
                    # Thêm nút đóng
                    ttk.Button(main_frame, text="Đóng", command=ffmpeg_info_dialog.destroy).pack(pady=10)
            else:
                # Tiếp tục kiểm tra
                ffmpeg_info_dialog.after(500, check_ffmpeg_status)
        
        # Bắt đầu thiết lập FFmpeg trong thread riêng
        def start_ffmpeg_setup():
            result = self.ffmpeg_manager.setup_ffmpeg()
            if result:
                # Đã cài đặt thành công
                status_var.set("Đã cài đặt FFmpeg thành công!")
                progress.stop()
                ffmpeg_info_dialog.after(1000, ffmpeg_info_dialog.destroy)
        
        # Chạy trong thread riêng để không chặn giao diện
        setup_thread = threading.Thread(target=start_ffmpeg_setup)
        setup_thread.daemon = True
        setup_thread.start()
        
        # Bắt đầu kiểm tra trạng thái
        ffmpeg_info_dialog.after(500, check_ffmpeg_status)
    
    def _create_ui(self):
        """Tạo giao diện người dùng"""
        # Tạo notebook (tab)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo các tab
        main_tab = ttk.Frame(self.notebook)
        auto_tab = ttk.Frame(self.notebook)
        settings_tab = ttk.Frame(self.notebook)
        history_tab = ttk.Frame(self.notebook)
        log_tab = ttk.Frame(self.notebook)
        
        # Thêm các tab vào notebook
        self.notebook.add(main_tab, text="Tải lên")
        self.notebook.add(auto_tab, text="Tự động")
        self.notebook.add(settings_tab, text="Cài đặt")
        self.notebook.add(history_tab, text="Lịch sử")
        self.notebook.add(log_tab, text="Nhật ký")
        
        # Tạo UI cho từng tab
        create_main_tab(self, main_tab)
        create_auto_tab(self, auto_tab)
        create_settings_tab(self, settings_tab)
        create_history_tab(self, history_tab)
        create_log_tab(self, log_tab)
    
    # ===== Các phương thức kết nối UI =====
    
    def _browse_folder(self, auto=False):
        """Chuyển tiếp đến hàm browse_folder trong module main_tab"""
        from ui.main_tab import browse_folder
        browse_folder(self, auto)
    
    def _refresh_video_list(self):
        """Chuyển tiếp đến hàm refresh_video_list trong module main_tab"""
        from ui.main_tab import refresh_video_list
        refresh_video_list(self)
    
    def _on_video_tree_click(self, event):
        """Chuyển tiếp đến hàm on_video_tree_click trong module main_tab"""
        from ui.main_tab import on_video_tree_click
        on_video_tree_click(self, event)
    
    def _on_video_select(self, event):
        """Chuyển tiếp đến hàm on_video_select trong module main_tab"""
        from ui.main_tab import on_video_select
        on_video_select(self, event)
    
    def _select_all_videos(self):
        """Chuyển tiếp đến hàm select_all_videos trong module main_tab"""
        from ui.main_tab import select_all_videos
        select_all_videos(self)
    
    def _deselect_all_videos(self):
        """Chuyển tiếp đến hàm deselect_all_videos trong module main_tab"""
        from ui.main_tab import deselect_all_videos
        deselect_all_videos(self)
    
    def _invert_video_selection(self):
        """Chuyển tiếp đến hàm invert_video_selection trong module main_tab"""
        from ui.main_tab import invert_video_selection
        invert_video_selection(self)
    
    def _play_selected_video(self):
        """Chuyển tiếp đến hàm play_selected_video trong module main_tab"""
        from ui.main_tab import play_selected_video
        play_selected_video(self)
    
    def _remove_duplicates(self):
        """Chuyển tiếp đến hàm remove_duplicates trong module main_tab"""
        from ui.main_tab import remove_duplicates
        remove_duplicates(self)
    
    def _on_closing(self):
        """Xử lý khi đóng ứng dụng"""
        # Dừng tất cả hoạt động
        if self.is_uploading:
            # Nếu đang tải lên, yêu cầu xác nhận
            if not messagebox.askyesno("Xác nhận", "Đang có video đang tải lên. Bạn có chắc muốn thoát?"):
                return
            
            # Dừng quá trình tải lên
            self.should_stop = True
        
        if self.auto_upload_active:
            # Dừng chế độ tự động
            self.auto_uploader_manager.stop_auto_upload(self)
        
        # Lưu cấu hình
        self.config_manager.save_config(self.config)
        
        # Ngắt kết nối các API
        if hasattr(self, 'telegram_api'):
            self.telegram_api.disconnect()
        
        if hasattr(self, 'telethon_uploader'):
            self.telethon_uploader.disconnect()
        
        # Đóng ứng dụng
        self.root.destroy()
        logger.info("Đã đóng ứng dụng")