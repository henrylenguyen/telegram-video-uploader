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
        # Make sure to initialize these early for checkbox functionality
        self.video_checkboxes = {}
        self.checkbox_widgets = []
        
        # Add the render_checkboxes method directly to the app instance
        def render_checkboxes_method():
            try:
                from ui.components.checkbox import create_checkbox_cell
            except ImportError:
                try:
                    from .components.checkbox import create_checkbox_cell
                except ImportError:
                    from src.ui.components.checkbox import create_checkbox_cell
            
            # Clear existing checkboxes
            if hasattr(self, 'checkbox_widgets'):
                for checkbox in self.checkbox_widgets:
                    checkbox.destroy()
            
            self.checkbox_widgets = []
            
            # Create checkbox for each row
            for item_id in self.video_tree.get_children():
                if item_id not in self.video_checkboxes:
                    self.video_checkboxes[item_id] = tk.BooleanVar(value=False)
                
                checkbox = create_checkbox_cell(self.video_tree, item_id, "#1")
                if checkbox:
                    checkbox.set(self.video_checkboxes[item_id].get())
                    self.checkbox_widgets.append(checkbox)
            
            # Update UI to ensure checkboxes are visible
            self.root.update_idletasks()
        # Thêm các sự kiện để hiển thị checkbox
        def force_render_checkboxes():
            """Hàm hiển thị checkbox sau khi tạo UI"""
            if hasattr(self, 'video_tree'):  # Chỉ hiển thị nếu video_tree đã tồn tại
                try:
                    from ui.main_tab.main_tab_func import render_checkboxes
                    render_checkboxes(self)
                except (ImportError, AttributeError) as e:
                    import logging
                    logging.getLogger().error(f"Error rendering checkboxes: {str(e)}")
            else:
                # Thử lại sau nếu video_tree chưa được tạo
                self.root.after(500, force_render_checkboxes)

        # Hiển thị checkbox sau khi tạo UI
        self.root.after(1000, force_render_checkboxes)
        # Attach the method to the app
        self.render_checkboxes = render_checkboxes_method
        
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
            if i == 0:  # Active tab
                btn = tk.Button(
                    self.header_tab_frame, 
                    text=text,
                    font=("Arial", 11, "bold"),
                    padx=15, pady=8,
                    relief="flat",
                    bg="#D4D4D4",  # Slightly darker for active tab
                    fg="#2C3E50",
                    activebackground="#C0C0C0",
                    activeforeground="#2C3E50",
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
                    fg="#2C3E50",
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
        create_main_tab(self, main_content)
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
                        command=lambda: self._start_upload())
        self.upload_btn.pack(side=tk.RIGHT, padx=10)

        # Thêm nhãn trạng thái bên trái (optional)
        status_frame = tk.Frame(footer_frame, bg="#EDEDED")
        status_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.status_var = tk.StringVar(value="Sẵn sàng")
        status_label = tk.Label(status_frame, 
                            textvariable=self.status_var,
                            bg="#EDEDED",
                            fg="#555555",
                            font=("Arial", 10))
        status_label.pack(side=tk.LEFT)


    def switch_tab(self, tab_index):
        """Chuyển đổi giữa các tab"""
        # Update button styling
        for i, btn in enumerate(self.tab_buttons):
            if i == tab_index:
                btn.config(
                    bg="#D4D4D4",
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
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                    font=("Arial", 11)
                )
                # Add hover effect back for inactive tabs
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#E5E5E5"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#EDEDED"))
        
        # Hide current content
        if self.current_content is not None:
            self.current_content.pack_forget()
        
        # Show selected content
        self.content_frames[tab_index].pack(fill=tk.BOTH, expand=True)
        self.current_content = self.content_frames[tab_index]
        
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
    
    def render_checkboxes(self):
        """Vẽ lại tất cả checkbox trên treeview với xử lý lỗi tốt hơn"""
        try:
            # Import functions safely
            try:
                from ui.main_tab.main_tab_func import safely_render_checkboxes
                safely_render_checkboxes(self)
                return
            except ImportError:
                pass
                
            # Fallback if we can't import the safer version
            # Import CustomCheckbox từ components
            try:
                from ui.components.checkbox import create_checkbox_cell
            except ImportError:
                try:
                    from src.ui.components.checkbox import create_checkbox_cell
                except ImportError:
                    # Last resort: direct import
                    import sys, os
                    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                    from ui.components.checkbox import create_checkbox_cell
            
            # Xóa tất cả checkbox hiện tại
            if hasattr(self, 'checkbox_widgets'):
                for checkbox in self.checkbox_widgets:
                    try:
                        checkbox.destroy()
                    except Exception as e:
                        logger.error(f"Error destroying checkbox: {str(e)}")
            
            self.checkbox_widgets = []
            
            # Force cập nhật UI
            self.root.update_idletasks()
            
            # Get valid items only
            try:
                valid_items = [item for item in self.video_tree.get_children()]
            except Exception as e:
                logger.error(f"Error getting tree children: {str(e)}")
                valid_items = []
                
            # Clean up invalid references
            invalid_keys = [key for key in self.video_checkboxes if key not in valid_items]
            for key in invalid_keys:
                if key in self.video_checkboxes:
                    del self.video_checkboxes[key]
            
            # Tạo checkbox cho tất cả hàng có trong tree
            for item_id in valid_items:
                try:
                    if item_id not in self.video_checkboxes:
                        # Lấy thông tin video để quyết định có nên chọn mặc định không
                        video_values = self.video_tree.item(item_id, "values")
                        tags = self.video_tree.item(item_id, "tags")
                        status = video_values[2] if len(video_values) > 2 else ""
                        
                        # Mặc định chọn những video không phải đã tải lên hoặc trùng lặp
                        should_check = not (status == "Đã tải lên" or status == "Trùng lặp" or "uploaded" in tags or "duplicate" in tags)
                        self.video_checkboxes[item_id] = tk.BooleanVar(value=should_check)
                    
                    checkbox = create_checkbox_cell(self.video_tree, item_id, "#1")
                    if checkbox:
                        checkbox.set(self.video_checkboxes[item_id].get())
                        self.checkbox_widgets.append(checkbox)
                except Exception as e:
                    logger.error(f"Error creating checkbox for item {item_id}: {str(e)}")
            
            # Force cập nhật lại lần nữa để đảm bảo hiển thị
            self.root.update_idletasks()
        
        except Exception as e:
            logger.error(f"Error in render_checkboxes: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    # ===== Các phương thức kết nối UI =====
    def _start_upload(self):
        """Sử dụng logic kiểm tra trùng lặp trước khi tải lên"""
        try:
            from ui.main_tab.upload_button_logic import start_upload
            start_upload(self)
        except ImportError:
            # Fallback nếu không import được
            self.uploader.start_upload(self)
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