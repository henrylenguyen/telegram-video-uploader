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
from ui.guide_tab import create_guide_tab  # Thêm module tab hướng dẫn

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
        
        # Thiết lập style cho button
        style.configure("TButton", padding=(10, 5), font=default_font)
        
        # Style cho label
        style.configure("TLabel", font=default_font)
        style.configure("Heading.TLabel", font=heading_font)
        
        # Style cho các cửa sổ chính
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabelframe", background="#f0f0f0", font=default_font)
        style.configure("TLabelframe.Label", font=heading_font)
        
        # Style cho Treeview
        style.configure("Treeview", font=default_font, rowheight=30)
        style.configure("Treeview.Heading", font=heading_font)
        
        # Style cho thanh trạng thái
        style.configure("Status.TLabel", font=default_font, foreground="#0066CC")
        
        # Style cho checkbox lớn
        style.configure("Large.TCheckbutton", 
                    font=default_font,
                    indicatorsize=24)
        
        # Style cho Button tab - sửa style cho tab header
        style.configure("Tab.TButton", 
                    font=("Arial", 11, "bold"), 
                    padding=(15, 8))
        
        # Tạo style đặc biệt cho tab đang active
        style.configure("Tab.Active.TButton", 
                    font=("Arial", 11, "bold"),
                    padding=(15, 8),
                    background="#4a7ebb",
                    foreground="white")
        
        # Style cho các tab không active
        style.configure("Tab.Inactive.TButton",
                    font=("Arial", 11, "bold"),
                    padding=(15, 8),
                    background="#f0f0f0",
                    foreground="black")
        
        # Style cho Header
        style.configure("Header.TFrame", background="#4a7ebb")
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="white", background="#4a7ebb")
        
        # Style cho các nút màu sắc
        style.configure("Red.TButton", font=default_font)
        style.map("Red.TButton",
                background=[("active", "#c0392b"), ("!active", "#e74c3c")],
                foreground=[("active", "white"), ("!active", "white")])
        
        style.configure("Blue.TButton", font=default_font)
        style.map("Blue.TButton",
                background=[("active", "#2980b9"), ("!active", "#3498db")],
                foreground=[("active", "white"), ("!active", "white")])
    
    def safe_update_stringvar(self, stringvar, value):
        """
        Cập nhật StringVar an toàn từ thread không phải main thread
        
        Args:
            stringvar: StringVar cần cập nhật
            value: Giá trị mới
        """
        self.root.after(0, lambda: stringvar.set(value))
        
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
        
        # Queue for thread communication
        from queue import Queue
        status_queue = Queue()
        
        # Function để kiểm tra và cập nhật định kỳ
        def check_ffmpeg_status():
            # Check for updates from the setup thread
            try:
                if not status_queue.empty():
                    new_status = status_queue.get_nowait()
                    status_var.set(new_status)
                    
                    # If it's the success message, close the dialog after 1 second
                    if "thành công" in new_status:
                        progress.stop()
                        ffmpeg_info_dialog.after(1000, ffmpeg_info_dialog.destroy)
                        return
                        
                    # If it's an error message
                    elif "Lỗi" in new_status:
                        progress.stop()
                        ttk.Button(main_frame, text="Đóng", command=ffmpeg_info_dialog.destroy).pack(pady=10)
                        return
            except:
                pass
                
            # Continue checking if FFmpeg is available
            if self.ffmpeg_manager.is_available:
                progress.stop()
                status_var.set("Đã cài đặt FFmpeg thành công!")
                ffmpeg_info_dialog.after(1000, ffmpeg_info_dialog.destroy)
            else:
                # Kiểm tra trạng thái tải
                progress_value, status_text, is_downloading = self.ffmpeg_manager.get_download_status()
                status_var.set(status_text)
                
                # Tiếp tục kiểm tra
                ffmpeg_info_dialog.after(500, check_ffmpeg_status)
        
        # Bắt đầu thiết lập FFmpeg trong thread riêng
        def start_ffmpeg_setup():
            try:
                result = self.ffmpeg_manager.setup_ffmpeg()
                
                if result:
                    # Đã cài đặt thành công - send to queue instead of updating directly
                    status_queue.put("Đã cài đặt FFmpeg thành công!")
            except Exception as e:
                # Send error to queue
                status_queue.put(f"Lỗi: {str(e)}")
        
        # Chạy trong thread riêng để không chặn giao diện
        setup_thread = threading.Thread(target=start_ffmpeg_setup)
        setup_thread.daemon = True
        setup_thread.start()
        
        # Bắt đầu kiểm tra trạng thái
        ffmpeg_info_dialog.after(500, check_ffmpeg_status)
    
    def _create_ui(self):
        """Tạo giao diện người dùng"""
        # Tạo header
        header_frame = ttk.Frame(self.root, style="Header.TFrame")
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Logo và tên ứng dụng bên trái
        logo_frame = ttk.Frame(header_frame, style="Header.TFrame")
        logo_frame.pack(side=tk.LEFT, padx=15)
        
        ttk.Label(logo_frame, text="Henlladev", style="Header.TLabel").pack(pady=10)
        
        # Tab buttons frame in header
        self.header_tab_frame = ttk.Frame(header_frame, style="Header.TFrame")
        self.header_tab_frame.pack(side=tk.LEFT, pady=10)
        
        # Create tab buttons with proper styling
        self.tab_buttons = []
        tab_texts = ["Tải lên", "Cài đặt", "Lịch sử", "Nhật ký", "Hướng dẫn"]
        
        for i, text in enumerate(tab_texts):
            btn = tk.Button(
                self.header_tab_frame, 
                text=text,
                font=("Arial", 11, "bold"),
                padx=15, pady=8,
                relief="flat",
                bg="#4a7ebb" if i == 0 else "#f0f0f0",
                fg="white" if i == 0 else "black",
                command=lambda idx=i: self.switch_tab(idx)
            )
            btn.pack(side=tk.LEFT)
            self.tab_buttons.append(btn)
        
        # Create content frames directly instead of using notebook
        self.content_frames = []
        self.current_content = None
        
        main_content = ttk.Frame(self.root)
        settings_content = ttk.Frame(self.root)
        history_content = ttk.Frame(self.root)
        log_content = ttk.Frame(self.root)
        guide_content = ttk.Frame(self.root)
        
        self.content_frames = [main_content, settings_content, history_content, log_content, guide_content]
        
        # Tạo UI cho từng tab content
        create_main_tab(self, main_content)
        create_settings_tab(self, settings_content)
        create_history_tab(self, history_content)
        create_log_tab(self, log_content)
        create_guide_tab(self, guide_content)
        
        # Show first content by default
        self.show_content(0)
        
        # Tạo footer với màu nền xám và chiều cao cố định
        footer_frame = tk.Frame(self.root, bg="#f0f0f0", height=60)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        footer_frame.pack_propagate(False)  # Prevent the frame from shrinking

        # Frame cho các nút ở footer - right aligned with proper spacing
        button_frame = tk.Frame(footer_frame, bg="#f0f0f0")
        button_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        # Nút dừng lại - màu đỏ
        self.stop_btn = tk.Button(button_frame, text="Dừng tải", 
                                bg="#e74c3c", fg="white", 
                                font=("Arial", 11),
                                padx=15, pady=5,
                                command=lambda: self.uploader.stop_upload(self))
        self.stop_btn.pack(side=tk.RIGHT, padx=10)

        # Nút bắt đầu tải lên - màu xanh
        self.upload_btn = tk.Button(button_frame, text="Tải video lên", 
                                bg="#3498db", fg="white", 
                                font=("Arial", 11),
                                padx=15, pady=5,
                                command=lambda: self.uploader.start_upload(self))
        self.upload_btn.pack(side=tk.RIGHT, padx=10)
    
    def show_content(self, index):
        """Hiển thị nội dung của tab đã chọn"""
        # Hide current content if exists
        if self.current_content is not None:
            self.current_content.pack_forget()
        
        # Show selected content
        self.content_frames[index].pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        self.current_content = self.content_frames[index]
        
        # Update button styling
        for i, btn in enumerate(self.tab_buttons):
            if i == index:
                btn.config(bg="#4a7ebb", fg="white")
            else:
                btn.config(bg="#f0f0f0", fg="black")
                    
    def switch_tab(self, index):
        """Chuyển đổi tab khi nhấn nút trên header"""
        self.show_content(index)
    def on_tab_changed(self, event):
        """Xử lý khi tab thay đổi để cập nhật các nút header"""
        selected_tab = self.notebook.index("current")
        for i, btn in enumerate(self.tab_buttons):
            if i == selected_tab:
                btn.config(bg="#4a7ebb", fg="white")
            else:
                btn.config(bg="#f0f0f0", fg="black")
    
    def render_checkboxes(self):
        """Vẽ lại tất cả checkbox trên treeview"""
        # Xóa tất cả checkbox hiện tại
        if hasattr(self, 'checkbox_widgets'):
            for checkbox in self.checkbox_widgets:
                checkbox.destroy()
        
        self.checkbox_widgets = []
        
        # Kiểm tra xem có checkbox nào được chọn không
        any_checked = False
        for item_id in self.video_checkboxes:
            if self.video_checkboxes[item_id].get():
                any_checked = True
                break
        
        # Chỉ hiển thị checkbox nếu có ít nhất một checkbox được chọn
        if any_checked:
            # Tạo mới checkbox cho mỗi hàng hiển thị
            for item_id in self.video_tree.get_children():
                # Lấy checkbox từ dict
                check_var = self.video_checkboxes.get(item_id)
                if check_var:
                    from ui.main_tab import create_checkbox_cell
                    checkbox = create_checkbox_cell(self.video_tree, item_id, "#1")
                    if checkbox:
                        # Đặt trạng thái của checkbox
                        checkbox.set(check_var.get())
                        self.checkbox_widgets.append(checkbox)
        
    # ===== Các phương thức kết nối UI =====
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