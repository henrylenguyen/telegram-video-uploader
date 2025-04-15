"""
Telegram Video Uploader Application
==================================

Ứng dụng chính để tải video lên Telegram với các tính năng tiên tiến.
"""
import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from queue import Queue

# Định nghĩa biến để quyết định dùng Qt hay Tkinter
USE_QT_UI = True  # True = dùng Qt, False = dùng Tkinter

# Import PyQt5 nếu sử dụng Qt UI
if USE_QT_UI:
    try:
        from PyQt5 import QtWidgets
    except ImportError:
        USE_QT_UI = False
        logging.warning("Không thể import PyQt5, chuyển sang sử dụng Tkinter")

# Import các module
from ui.splash_screen import show_splash_screen
from ui.settings_tab import create_settings_tab
from ui.history_tab import create_history_tab
from ui.log_tab import create_log_tab
from ui.guide_tab import create_guide_tab

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

# Function để khởi chạy Qt UI
def run_qt_ui():
    """Khởi chạy giao diện Qt"""
    try:
        # Import the Qt UI
        from ui.qt_main_ui import MainUI
        
        # Create Qt application
        qt_app = QtWidgets.QApplication(sys.argv)
        
        # Create main window
        main_window = MainUI()
        
        # Show the window
        main_window.show()
        
        # Run the application
        return qt_app.exec_()
    except Exception as e:
        logger.error(f"Error starting Qt UI: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

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
        self.info_vars = {}
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
                
        # Style cho gallery components
        style.configure("Thumb.TFrame", background="#f8f8f8", borderwidth=2, relief="groove")
        style.configure("ThumbActive.TFrame", background="#f8f8f8", borderwidth=3, relief="raised")
        style.configure("Controls.TFrame", background="#f0f0f0", borderwidth=1, relief="groove")
        style.configure("Thumbnails.TFrame", background="#f8f8f8")
    
    def safe_update_stringvar(self, stringvar, value):
        """
        Cập nhật StringVar an toàn từ thread không phải main thread
        
        Args:
            stringvar: StringVar cần cập nhật
            value: Giá trị mới
        """
        self.root.after(0, lambda: stringvar.set(value))

    def _initialize_components(self):
        """Enhanced component initialization with better error handling"""
        # Status variables
        self.is_uploading = False
        self.should_stop = False
        self.current_frames = []  # Store current frames
        self.auto_upload_active = False
        
        # Initialize configuration manager
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # Initialize other components
        self.ffmpeg_manager = FFmpegManager()
        # Setup FFmpeg with error handling
        try:
            self._setup_ffmpeg()
        except Exception as e:
            logger.error(f"Error setting up FFmpeg: {str(e)}")
            # Continue anyway - FFmpeg errors will be handled when needed
        
        # Initialize history
        try:
            history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload_history.json')
            self.upload_history = UploadHistory(history_file)
        except Exception as e:
            logger.error(f"Error initializing upload history: {str(e)}")
            # Create empty history as fallback
            self.upload_history = UploadHistory()
        
        # Initialize video analyzer
        self.video_analyzer = VideoAnalyzer()
        self.videos = {}  # Dict to store video info
        self.duplicate_groups = []  # List of duplicate video groups
        
        # Initialize Telegram connection with error handling
        try:
            self.telegram_connector = TelegramConnector(self)
            self.telegram_api = self.telegram_connector.telegram_api
            self.telethon_uploader = self.telegram_connector.telethon_uploader
        except Exception as e:
            logger.error(f"Error initializing Telegram connection: {str(e)}")
            # Create minimal instances as fallback
            from utils.telegram_api import TelegramAPI
            from utils.telethon_uploader import TelethonUploader
            self.telegram_api = TelegramAPI()
            self.telethon_uploader = TelethonUploader()
        
        # Initialize upload manager
        self.uploader = Uploader(self)
        self.upload_queue = Queue()
        
        # Initialize auto upload manager
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
        # Make sure to initialize these early for checkbox functionality
        self.video_checkboxes = {}
        self.checkbox_widgets = []
        
        # Tạo style cho các thành phần
        style = ttk.Style()
        
        # Style cho header
        style.configure("Header.TFrame", background="#EDEDED", relief="raised")
        style.configure("Header.TLabel", background="#EDEDED", font=("Arial", 16, "bold"), foreground="#2C3E50")
        
        # Style cho tab buttons
        style.configure("Tab.TButton", font=("Arial", 11), padding=(15, 8))
        
        # Tạo header với hiệu ứng 3D và đường viền
        header_frame = tk.Frame(self.root, bg="#EDEDED", relief="raised", bd=1)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Logo và tên ứng dụng bên trái với gradient text
        logo_frame = tk.Frame(header_frame, bg="#EDEDED")
        logo_frame.pack(side=tk.LEFT, padx=15)
        
        logo_label = tk.Label(logo_frame, text="Henlladev", 
                            font=("Arial", 18, "bold"), 
                            fg="#2C3E50",
                            bg="#EDEDED")
        logo_label.pack(pady=10)
        
        # Add subtle shadow effect to logo text
        shadow_label = tk.Label(logo_frame, text="Henlladev", 
                            font=("Arial", 18, "bold"), 
                            fg="#C0C0C0", 
                            bg="#EDEDED")
        shadow_label.place(in_=logo_label, x=1, y=1)
        logo_label.lift()  # Bring main text to front
        
        # Tab buttons frame in header
        self.header_tab_frame = tk.Frame(header_frame, bg="#EDEDED")
        self.header_tab_frame.pack(side=tk.LEFT, pady=10)
        
        # Create tab buttons with proper styling - gradient effect for active tab
        self.tab_buttons = []
        tab_texts = ["Tải lên", "Cài đặt", "Lịch sử", "Nhật ký", "Hướng dẫn"]
        
        for i, text in enumerate(tab_texts):
            # Use gradient colors for active tab and hover effects
            if i == 0:  # Active tab - use blue color
                btn = tk.Button(
                    self.header_tab_frame, 
                    text=text,
                    font=("Arial", 11, "bold"),
                    padx=15, pady=8,
                    relief="flat",
                    bg="#2E86C1",  # Blue color for active tab
                    fg="white",    # White text for better contrast
                    activebackground="#2980b9",
                    activeforeground="white",
                    bd=1,
                    highlightthickness=1,
                    highlightbackground="#BEBEBE",
                    command=lambda idx=i: self.switch_tab(idx)
                )
            else:  # Inactive tabs
                btn = tk.Button(
                    self.header_tab_frame, 
                    text=text,
                    font=("Arial", 11),
                    padx=15, pady=8,
                    relief="flat",
                    bg="#EDEDED",
                    fg="#2C3E50",  # Dark blue text
                    activebackground="#D4D4D4",
                    activeforeground="#2C3E50",
                    bd=0,
                    highlightthickness=0,
                    command=lambda idx=i: self.switch_tab(idx)
                )
                
                # Add hover effect
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#E5E5E5"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#EDEDED"))
                
            btn.pack(side=tk.LEFT)
            self.tab_buttons.append(btn)
        
        # Add subtle shadow line below header
        separator = ttk.Separator(self.root, orient="horizontal")
        separator.pack(fill=tk.X, pady=0)
        
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
        # Thông báo cho main tab mà không sử dụng main_tab Tkinter nữa
        ttk.Label(
            main_content, 
            text="Tab Tải lên đã được chuyển sang sử dụng giao diện Qt", 
            font=("Arial", 16, "bold")
        ).pack(pady=100)
        
        ttk.Label(
            main_content, 
            text="Vui lòng sử dụng giao diện Qt để xem và sử dụng tính năng này.", 
            font=("Arial", 14)
        ).pack(pady=10)
        
        # Các tab khác vẫn dùng Tkinter như bình thường
        create_settings_tab(self, settings_content)
        create_history_tab(self, history_content)
        create_log_tab(self, log_content)
        create_guide_tab(self, guide_content)
        
        # Show first content by default
        self.show_content(0)
        
        footer_frame = tk.Frame(self.root, bg="#EDEDED", height=60, relief="raised", bd=1)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        footer_frame.pack_propagate(False)  

        # Frame cho các nút ở footer - right aligned with proper spacing
        button_frame = tk.Frame(footer_frame, bg="#EDEDED")
        button_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        # Nút bắt đầu tải lên - màu xanh (chỉ giữ nút này, bỏ nút dừng)
        self.upload_btn = tk.Button(button_frame, text="Tải video lên", 
                        bg="#3498db", fg="white", 
                        font=("Arial", 11, "bold"),
                        padx=15, pady=8,
                        relief="flat",
                        bd=0,
                        activebackground="#2980b9",
                        activeforeground="white",
                        state=tk.DISABLED,  # Disabled in Tkinter mode
                        command=self._start_upload)
        self.upload_btn.pack(side=tk.RIGHT, padx=10)

        # Thêm nhãn trạng thái bên trái (optional)
        status_frame = tk.Frame(footer_frame, bg="#EDEDED")
        status_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.status_var = tk.StringVar(value="Sẵn sàng (Qt Mode)")
        status_label = tk.Label(status_frame, 
                            textvariable=self.status_var,
                            bg="#EDEDED",
                            fg="#555555",
                            font=("Arial", 10))
        status_label.pack(side=tk.LEFT)
        # Check if Telegram is configured, and show config modal if not
        self.check_telegram_config()

    def check_telegram_config(self):
        """Kiểm tra cấu hình Telegram và hiển thị modal nếu cần"""
        # Check if bot token and chat ID are configured
        bot_token = self.config['TELEGRAM']['bot_token']
        chat_id = self.config['TELEGRAM']['chat_id']
        
        if not bot_token or not chat_id:
            # Import and show configuration modal
            try:
                from ui.config_modal import TelegramConfigModal
                # Use after() to ensure the UI is fully loaded first
                self.root.after(1000, lambda: TelegramConfigModal(self))
            except Exception as e:
                logger.error(f"Error showing config modal: {str(e)}")
                # Fallback to simple message
                messagebox.showwarning(
                    "Cấu hình chưa hoàn tất", 
                    "Bạn cần cấu hình thông tin Telegram trong tab Cài đặt."
                )

    def switch_tab(self, tab_index):
        """Improved tab switching with proper visual feedback"""
        # Update button styling for main tabs
        for i, btn in enumerate(self.tab_buttons):
            if i == tab_index:
                btn.config(
                    bg="#2E86C1",  # Blue color for active tab
                    fg="white",    # White text for better contrast
                    relief="flat",
                    bd=1,
                    highlightthickness=1,
                    highlightbackground="#BEBEBE",
                    font=("Arial", 11, "bold")
                )
                # Remove hover bindings for active tab
                btn.unbind("<Enter>")
                btn.unbind("<Leave>")
            else:
                btn.config(
                    bg="#EDEDED",
                    fg="#2C3E50",  # Dark blue text for inactive tabs
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                    font=("Arial", 11)
                )
                # Re-add hover effect for inactive tabs
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#E5E5E5"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#EDEDED"))
        
        # Hide current content
        if self.current_content is not None:
            self.current_content.pack_forget()
        
        # Show selected content
        self.content_frames[tab_index].pack(fill=tk.BOTH, expand=True)
        self.current_content = self.content_frames[tab_index]
        
        # Reset any sub-tabs if present
        # This ensures sub-tabs are reset when switching main tabs
        if hasattr(self, 'show_tab') and tab_index == 1:  # If switching to Settings tab
            # Reset to first sub-tab
            self.show_tab(0)
    
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
                    
    def on_tab_changed(self, event):
        """Xử lý khi tab thay đổi để cập nhật các nút header"""
        selected_tab = self.notebook.index("current")
        for i, btn in enumerate(self.tab_buttons):
            if i == selected_tab:
                btn.config(bg="#4a7ebb", fg="white")
            else:
                btn.config(bg="#f0f0f0", fg="black")
    
    def _start_upload(self):
        """Sử dụng logic kiểm tra trùng lặp trước khi tải lên - KHÔNG SỬ DỤNG Ở CHẾ ĐỘ TKINTER"""
        messagebox.showinfo("Chế độ Qt", "Vui lòng sử dụng giao diện Qt để sử dụng tính năng này")
    
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
        
        # Xóa thư mục tạm nếu có
        if hasattr(self, 'temp_dir') and self.temp_dir and os.path.exists(self.temp_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
                logger.info(f"Đã xóa thư mục tạm: {self.temp_dir}")
            except Exception as e:
                logger.error(f"Lỗi khi xóa thư mục tạm: {str(e)}")
        
        # Đóng ứng dụng
        self.root.destroy()
        logger.info("Đã đóng ứng dụng")