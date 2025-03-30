"""
Telegram Video Uploader
======================

Ứng dụng tự động tải video lên Telegram với các tính năng tiên tiến.
"""
import os
import sys
import time
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import PhotoImage
from datetime import datetime
import configparser
import threading
import re
import socket
from queue import Queue, Empty
import traceback
import cv2
from PIL import Image, ImageTk

# Thêm thư mục nguồn vào đường dẫn
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Nhập các module tiện ích
    from utils.video_analyzer import VideoAnalyzer
    from utils.auto_uploader import AutoUploader, FileWatcher, BulkUploader
    from utils.telegram_api import TelegramAPI
    from utils.upload_history import UploadHistory
    from utils.history_ui import UploadHistoryDialog
    from utils.ffmpeg_manager import FFmpegManager
    from utils.telethon_uploader import TelethonUploader
except ImportError as e:
    # Xử lý trường hợp không tìm thấy module
    print(f"Lỗi khi nhập module: {e}")
    print("Đảm bảo thư mục 'utils' tồn tại và chứa các module cần thiết.")
    sys.exit(1)

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("telegram_uploader.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
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
        
        # Lấy kích thước màn hình
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Thiết lập kích thước cửa sổ gần như toàn màn hình
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # Đặt vị trí cửa sổ vào giữa màn hình
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        # Áp dụng kích thước và vị trí
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.root.minsize(1024, 768)  # Tăng kích thước tối thiểu
        
        # Mở toàn màn hình khi bắt đầu (chỉ cho Windows)
        self.root.state('zoomed')
        
        # Thiết lập icon nếu có
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            logger.warning(f"Không thể đặt icon: {e}")
        
        # Tạo splash screen
        self.show_splash_screen()
        
        # Biến trạng thái
        self.is_uploading = False
        self.should_stop = False
        self.config = self.load_config()
        self.current_frames = []  # Lưu trữ các frame hiện tại
        
        # Khởi tạo quản lý FFmpeg
        self.ffmpeg_manager = FFmpegManager()
        
        # Khởi tạo lịch sử tải lên
        history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload_history.json')
        self.upload_history = UploadHistory(history_file)
        
        # Khởi tạo các thành phần
        self.video_analyzer = VideoAnalyzer()
        self.telegram_api = TelegramAPI()
        self.telethon_uploader = TelethonUploader()
        self.upload_queue = Queue()
        self.auto_uploader = None
        self.bulk_uploader = None
        self.auto_upload_active = False
        self.watcher_thread = None
        
        # Khởi tạo style cho ttk widgets
        self.setup_styles()
        
        # Lưu trữ video và thông tin liên quan
        self.videos = {}  # Dict lưu thông tin video
        self.duplicate_groups = []  # Danh sách các nhóm video trùng lặp
        
        # Cài đặt FFmpeg
        self.setup_ffmpeg()
        
        # Kết nối với Telegram
        self.connect_telegram()
        
        # Tạo giao diện
        self.create_ui()
        
        # Khi đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    def setup_styles(self):
        """Thiết lập style cho các widget ttk"""
        style = ttk.Style()
        
        # Thiết lập font chung
        default_font = ("Segoe UI", 10)
        heading_font = ("Segoe UI", 11, "bold")
        
        # Thiết lập style cho button để tránh bị thu hẹp
        style.configure("TButton", padding=(10, 5), font=default_font)
        # Bỏ thuộc tính width để nút có thể mở rộng theo nội dung
        
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
    
    def setup_ffmpeg(self):
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
    
    def show_splash_screen(self):
        """Hiển thị splash screen khi khởi động ứng dụng"""
        splash = tk.Toplevel(self.root)
        splash.title("Đang khởi động...")
        splash.geometry("500x350")
        splash.overrideredirect(True)  # Ẩn thanh tiêu đề
        
        # Đặt splash vào giữa màn hình
        splash.update_idletasks()
        width = splash.winfo_width()
        height = splash.winfo_height()
        x = (splash.winfo_screenwidth() // 2) - (width // 2)
        y = (splash.winfo_screenheight() // 2) - (height // 2)
        splash.geometry(f"{width}x{height}+{x}+{y}")
        
        # Thiết lập màu nền và kiểu dáng
        splash.configure(bg="#f0f0f0")
        style = ttk.Style()
        style.configure("Splash.TFrame", background="#f0f0f0")
        style.configure("Splash.TLabel", background="#f0f0f0", foreground="#333333")
        style.configure("SplashTitle.TLabel", background="#f0f0f0", foreground="#333333", font=("Arial", 18, "bold"))
        style.configure("SplashVersion.TLabel", background="#f0f0f0", foreground="#555555", font=("Arial", 10))
        style.configure("SplashStatus.TLabel", background="#f0f0f0", foreground="#555555", font=("Arial", 9))
        style.configure("SplashProgress.Horizontal.TProgressbar", background="#4a7ebb", troughcolor="#dddddd", borderwidth=0, thickness=10)
        
        # Tạo frame chính
        main_frame = ttk.Frame(splash, padding=20, style="Splash.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo hoặc biểu tượng
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
            if os.path.exists(icon_path):
                # Sử dụng PhotoImage nếu có thể
                logo = PhotoImage(file=icon_path)
                logo = logo.subsample(2, 2)  # Giảm kích thước
                logo_label = ttk.Label(main_frame, image=logo, background="#f0f0f0")
                logo_label.image = logo  # Giữ tham chiếu
                logo_label.pack(pady=(10, 20))
        except Exception:
            pass  # Nếu không thể tải logo, bỏ qua
        
        # Tiêu đề
        ttk.Label(
            main_frame, 
            text="Telegram Video Uploader", 
            style="SplashTitle.TLabel"
        ).pack(pady=(10, 5))
        
        # Phiên bản
        ttk.Label(
            main_frame, 
            text="Phiên bản 1.0",
            style="SplashVersion.TLabel"
        ).pack(pady=(0, 20))
        
        # Khung cài đặt
        setup_frame = ttk.Frame(main_frame, padding=5)
        setup_frame.pack(fill=tk.X, pady=10)
        
        # Các mục cài đặt với biểu tượng tick
        setup_items = [
            "Kiểm tra cấu hình hệ thống",
            "Khởi tạo tài nguyên ứng dụng",
            "Chuẩn bị bộ phân tích video",
            "Kiểm tra kết nối",
            "Tải các thành phần giao diện"
        ]
        
        # Biến lưu trạng thái các mục
        self.setup_statuses = {}
        self.setup_labels = {}
        
        for i, item in enumerate(setup_items):
            item_frame = ttk.Frame(setup_frame)
            item_frame.pack(fill=tk.X, pady=3)
            
            # Biểu tượng trạng thái (bắt đầu là trống)
            status_var = tk.StringVar(value="⬜")
            self.setup_statuses[item] = status_var
            status_label = ttk.Label(item_frame, textvariable=status_var, width=3)
            status_label.pack(side=tk.LEFT, padx=(0, 5))
            
            # Nội dung mục
            item_label = ttk.Label(item_frame, text=item, style="Splash.TLabel")
            item_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.setup_labels[item] = item_label
        
        # Thanh tiến trình
        self.splash_progress = ttk.Progressbar(
            main_frame, 
            orient="horizontal", 
            length=400, 
            mode="determinate",
            style="SplashProgress.Horizontal.TProgressbar"
        )
        self.splash_progress.pack(fill=tk.X, pady=(20, 10))
        self.splash_progress["maximum"] = 100
        self.splash_progress["value"] = 0
        
        # Nhãn trạng thái
        self.splash_status = tk.StringVar(value="Đang khởi động ứng dụng...")
        status_label = ttk.Label(
            main_frame, 
            textvariable=self.splash_status,
            style="SplashStatus.TLabel"
        )
        status_label.pack(pady=5)
        
        # Bản quyền
        ttk.Label(
            main_frame, 
            text="© 2025 Telegram Video Uploader",
            style="SplashStatus.TLabel"
        ).pack(side=tk.BOTTOM, pady=10)
        
        # Cập nhật giao diện
        self.root.update()
        
        # Mô phỏng quá trình cài đặt
        self.simulate_setup(splash, setup_items)

    def simulate_setup(self, splash, setup_items):
        """
        Mô phỏng quá trình cài đặt và hiển thị trên splash screen
        
        Args:
            splash: Cửa sổ splash
            setup_items: Danh sách các mục cài đặt
        """
        total_steps = len(setup_items)
        
        def update_step(step, item):
            # Cập nhật trạng thái mục
            self.setup_statuses[item].set("✅")
            
            # Cập nhật thanh tiến trình
            progress_value = (step + 1) / total_steps * 100
            self.splash_progress["value"] = progress_value
            
            # Cập nhật nhãn trạng thái
            if step < total_steps - 1:
                next_item = setup_items[step + 1]
                self.splash_status.set(f"Đang {next_item.lower()}...")
            else:
                self.splash_status.set("Đã sẵn sàng khởi động...")
            
            # Cập nhật giao diện
            self.root.update_idletasks()
        
        # Mô phỏng các bước cài đặt
        for i, item in enumerate(setup_items):
            # Đặt nhãn trạng thái
            self.splash_status.set(f"Đang {item.lower()}...")
            self.root.update_idletasks()
            
            # Mô phỏng thời gian xử lý
            delay = 300  # ms
            self.root.after(delay, lambda s=i, it=item: update_step(s, it))
            self.root.after(delay + 50)  # Chờ một chút để hiệu ứng mượt hơn
        
        # Sau khi hoàn tất tất cả các bước, đóng splash screen
        self.root.after(1500, splash.destroy)
    
    def load_config(self):
        """
        Tải cấu hình từ file config.ini
        
        Returns:
            configparser.ConfigParser: Đối tượng cấu hình
        """
        config = configparser.ConfigParser()
        
        # Tạo file cấu hình mặc định nếu không tồn tại
        if not os.path.exists('config.ini'):
            config['TELEGRAM'] = {
                'bot_token': '',
                'chat_id': '',
                'notification_chat_id': ''
            }
            config['SETTINGS'] = {
                'video_folder': '',
                'video_extensions': '.mp4,.avi,.mkv,.mov,.wmv',
                'delay_between_uploads': '5',
                'auto_mode': 'false',
                'check_duplicates': 'true',
                'auto_check_interval': '60'  # Thời gian kiểm tra tự động (giây)
            }
            config['TELETHON'] = {
                'api_id': '',
                'api_hash': '',
                'phone': '',
                'use_telethon': 'false'
            }
            
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            
            # Hiển thị cửa sổ cấu hình ban đầu nếu đây là lần đầu chạy
            self.show_first_run_config_dialog()
        
        config.read('config.ini', encoding='utf-8')
        
        # Đảm bảo section TELETHON tồn tại
        if 'TELETHON' not in config:
            config['TELETHON'] = {
                'api_id': '',
                'api_hash': '',
                'phone': '',
                'use_telethon': 'false'
            }
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config.write(configfile)
        
        return config
    def show_first_run_config_dialog(self):
        """Hiển thị cửa sổ cấu hình khi chạy lần đầu"""
        config_dialog = tk.Toplevel(self.root)
        config_dialog.title("Cấu hình ban đầu")
        config_dialog.geometry("800x600")
        config_dialog.resizable(True, True)
        config_dialog.transient(self.root)
        config_dialog.grab_set()  # Làm cho cửa sổ này là modal
        
        # Tạo frame chính
        main_frame = ttk.Frame(config_dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        ttk.Label(
            main_frame, 
            text="Chào mừng đến với Telegram Video Uploader!", 
            style="Heading.TLabel"
        ).pack(pady=10)
        
        ttk.Label(
            main_frame, 
            text="Vui lòng nhập thông tin cấu hình cho ứng dụng"
        ).pack(pady=5)
        
        # Frame nhập thông tin Telegram
        telegram_frame = ttk.LabelFrame(main_frame, text="Thông tin Telegram Bot", padding=10)
        telegram_frame.pack(fill=tk.X, pady=10)
        
        # Bot Token
        ttk.Label(telegram_frame, text="Bot Token:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        token_entry = ttk.Entry(telegram_frame, width=60)
        token_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Thêm tooltip cho Bot Token
        ttk.Label(
            telegram_frame, 
            text="(Lấy từ @BotFather trên Telegram)",
            foreground="gray"
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # Chat ID đích
        ttk.Label(telegram_frame, text="Chat ID đích:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        chat_id_entry = ttk.Entry(telegram_frame, width=60)
        chat_id_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Thêm tooltip cho Chat ID
        ttk.Label(
            telegram_frame, 
            text="(ID kênh/nhóm để gửi video)",
            foreground="gray"
        ).grid(row=1, column=2, padx=5, pady=5)
        
        # Chat ID thông báo
        ttk.Label(telegram_frame, text="Chat ID thông báo:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        notif_id_entry = ttk.Entry(telegram_frame, width=60)
        notif_id_entry.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Thêm tooltip
        ttk.Label(
            telegram_frame, 
            text="(ID của bạn để nhận thông báo)",
            foreground="gray"
        ).grid(row=2, column=2, padx=5, pady=5)
        
        # Thêm hướng dẫn với thanh cuộn
        help_frame = ttk.LabelFrame(main_frame, text="Hướng dẫn lấy thông tin", padding=10)
        help_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Tạo frame cho nội dung có thể cuộn
        help_scroll_frame = ttk.Frame(help_frame)
        help_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # Thêm thanh cuộn
        help_scrollbar = ttk.Scrollbar(help_scroll_frame)
        help_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tạo Text widget thay vì Label để có thể cuộn
        help_text_widget = tk.Text(help_scroll_frame, wrap=tk.WORD, height=15, width=70)
        help_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Kết nối thanh cuộn
        help_text_widget.config(yscrollcommand=help_scrollbar.set)
        help_scrollbar.config(command=help_text_widget.yview)
        
        # Nội dung hướng dẫn
        help_text = (
            "1. Tạo bot mới: Tìm @BotFather trên Telegram, gửi lệnh /newbot\n"
            "2. Lấy Bot Token từ tin nhắn BotFather gửi sau khi tạo bot\n"
            "3. Thêm bot vào kênh/nhóm, làm cho bot là admin để gửi media\n"
            "4. Lấy Chat ID: Gửi tin nhắn trong kênh/nhóm, sau đó truy cập\n"
            "   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates\n"
            "5. Để lấy Chat ID cá nhân: Tìm @userinfobot trên Telegram và nhắn tin\n\n"
            "Hướng dẫn chi tiết đối với kênh:\n"
            "1. Thêm bot vào kênh và đặt làm admin\n"
            "2. Gửi một tin nhắn trong kênh\n"
            "3. Truy cập URL: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates\n"
            "4. Tìm phần \"chat\" > \"id\" trong kết quả JSON (ID kênh thường có dạng -100xxxxxxxxxx)\n\n"
            "Hướng dẫn chi tiết đối với nhóm:\n"
            "1. Thêm bot vào nhóm\n"
            "2. Gửi tin nhắn trong nhóm (có thể bạn cần 'mở khóa' bot bằng lệnh /start)\n"
            "3. Truy cập URL: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates\n"
            "4. Tìm phần \"chat\" > \"id\" trong kết quả JSON\n\n"
            "Hướng dẫn chi tiết để lấy Chat ID cá nhân:\n"
            "1. Tìm @userinfobot hoặc @chatid_echo_bot trên Telegram\n"
            "2. Gửi bất kỳ tin nhắn nào và bot sẽ phản hồi với ID của bạn\n\n"
            "Lưu ý quan trọng:\n"
            "- Bot Token là thông tin nhạy cảm, không nên chia sẻ với người khác\n"
            "- Đảm bảo bot có đủ quyền trong kênh/nhóm (quyền gửi tin nhắn và media)\n"
            "- Đối với kênh công khai, bạn có thể lấy ID bằng cách thêm -100 vào trước ID số của kênh\n"
            "- Telegram giới hạn kích thước file bot có thể gửi là 50MB, ứng dụng sẽ tự động xử lý file lớn hơn"
        )
        
        # Chèn văn bản vào widget
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)  # Đặt thành chỉ đọc

        # Frame chứa các nút
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Nút lưu cấu hình
        def save_initial_config():
            # Lưu thông tin vào config
            config = configparser.ConfigParser()
            config.read('config.ini', encoding='utf-8')
            
            config['TELEGRAM']['bot_token'] = token_entry.get()
            config['TELEGRAM']['chat_id'] = chat_id_entry.get()
            config['TELEGRAM']['notification_chat_id'] = notif_id_entry.get()
            
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            
            # Đóng dialog
            config_dialog.destroy()
            
            # Thông báo
            messagebox.showinfo(
                "Cấu hình hoàn tất", 
                "Đã lưu cấu hình ban đầu. Bạn có thể thay đổi cấu hình trong tab Cài đặt."
            )
        
        # Nút kiểm tra kết nối
        def test_connection(self):
            """Kiểm tra kết nối Telegram"""
            bot_token = self.bot_token_var.get()
            notification_chat_id = self.notification_chat_id_var.get()
            
            if not bot_token:
                messagebox.showerror("Lỗi", "Vui lòng nhập Bot Token!")
                return
                
            if not notification_chat_id:
                # Nếu không có chat ID thông báo, thử dùng chat ID đích
                notification_chat_id = self.chat_id_var.get()
                if not notification_chat_id:
                    messagebox.showerror("Lỗi", "Vui lòng nhập Chat ID thông báo hoặc Chat ID đích!")
                    return
            
            # Hiển thị thông báo đang kiểm tra
            self.status_var.set("Đang kiểm tra kết nối Telegram...")
            self.root.update_idletasks()
            
            try:
                # Tạo một instance tạm thời để kiểm tra kết nối
                from utils.telegram_api import TelegramAPI
                temp_api = TelegramAPI()
                success, message = temp_api.test_connection(bot_token, notification_chat_id)
                
                if success:
                    # Nếu thành công, lưu lại instance
                    self.telegram_api = temp_api
                    messagebox.showinfo("Thành công", message)
                else:
                    messagebox.showerror("Lỗi", message)
            except Exception as e:
                messagebox.showerror("Lỗi kết nối", f"Không thể kiểm tra kết nối: {str(e)}")
            
            # Khôi phục trạng thái
            self.status_var.set("Sẵn sàng")
        
        # Nút kiểm tra kết nối
        test_btn = ttk.Button(button_frame, text="Kiểm tra kết nối", command=test_connection)
        test_btn.pack(side=tk.LEFT, padx=5)
        
        # Nút lưu
        save_btn = ttk.Button(button_frame, text="Lưu cấu hình", command=save_initial_config)
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Đặt dialog vào giữa màn hình
        config_dialog.update_idletasks()
        width = config_dialog.winfo_width()
        height = config_dialog.winfo_height()
        x = (config_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (config_dialog.winfo_screenheight() // 2) - (height // 2)
        config_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Đợi cho đến khi dialog đóng
        self.root.wait_window(config_dialog)
    
    def connect_telegram(self):
        """Kết nối với bot Telegram"""
        bot_token = self.config['TELEGRAM']['bot_token']
        
        if bot_token:
            # Sử dụng TelegramAPI để kết nối
            if self.telegram_api.connect(bot_token):
                logger.info("Đã kết nối với bot Telegram thành công")
                
                # Gửi thông báo đã kết nối
                notification_chat_id = self.config['TELEGRAM']['notification_chat_id']
                if notification_chat_id:
                    try:
                        self.telegram_api.send_message(
                            notification_chat_id, 
                            "✅ Ứng dụng đã kết nối thành công!"
                        )
                    except Exception as e:
                        logger.error(f"Không thể gửi thông báo: {e}")
            else:
                logger.error("Không thể kết nối với bot Telegram")
                
                # Nếu không thể kết nối, kiểm tra xem có phải là lần đầu chạy hay không
                if not self.config['TELEGRAM']['notification_chat_id'] and not self.config['TELEGRAM']['chat_id']:
                    # Hiển thị hộp thoại yêu cầu cấu hình
                    messagebox.showwarning(
                        "Cấu hình chưa hoàn tất", 
                        "Bạn cần cấu hình thông tin Telegram. Vui lòng nhập thông tin trong tab Cài đặt."
                    )
        
        # Kết nối Telethon nếu có thông tin cấu hình
        use_telethon = self.config.getboolean('TELETHON', 'use_telethon', fallback=False)
        if use_telethon:
            api_id = self.config.get('TELETHON', 'api_id', fallback='')
            api_hash = self.config.get('TELETHON', 'api_hash', fallback='')
            phone = self.config.get('TELETHON', 'phone', fallback='')
            
            if api_id and api_hash and phone:
                try:
                    api_id = int(api_id)
                    if self.telethon_uploader.login(api_id, api_hash, phone, interactive=False):
                        logger.info("Đã kết nối với Telegram API (Telethon) thành công")
                except Exception as e:
                    logger.error(f"Lỗi khi kết nối Telethon: {str(e)}")
    
    def create_ui(self):
        """Tạo giao diện người dùng"""
        # Tạo notebook (tab)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab chính
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text="Tải lên")
        
        # Tab tự động
        auto_tab = ttk.Frame(self.notebook)
        self.notebook.add(auto_tab, text="Tự động")
        
        # Tab cài đặt
        settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(settings_tab, text="Cài đặt")
        
        # Tab lịch sử
        history_tab = ttk.Frame(self.notebook)
        self.notebook.add(history_tab, text="Lịch sử")
        
        # Tab log
        log_tab = ttk.Frame(self.notebook)
        self.notebook.add(log_tab, text="Nhật ký")
        
        # Tạo UI cho tab chính
        self.create_main_tab(main_tab)
        
        # Tạo UI cho tab tự động
        self.create_auto_tab(auto_tab)
        
        # Tạo UI cho tab cài đặt
        self.create_settings_tab(settings_tab)
        
        # Tạo UI cho tab lịch sử
        self.create_history_tab(history_tab)
        
        # Tạo UI cho tab log
        self.create_log_tab(log_tab)
    
    def create_main_tab(self, parent):
        """
        Tạo giao diện cho tab chính
        
        Args:
            parent: Frame cha
        """
        # Frame chọn thư mục
        folder_frame = ttk.LabelFrame(parent, text="Thư mục chứa video")
        folder_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Đường dẫn thư mục
        self.folder_path = tk.StringVar()
        self.folder_path.set(self.config['SETTINGS']['video_folder'])
        
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=50)
        folder_entry.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(folder_frame, text="Duyệt...", command=self.browse_folder, width=10)
        browse_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # Frame kiểm soát
        control_top_frame = ttk.Frame(parent)
        control_top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Nút làm mới danh sách
        refresh_btn = ttk.Button(control_top_frame, text="Làm mới danh sách", 
                                command=self.refresh_video_list, width=20)
        refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Checkbox kiểm tra trùng lặp
        self.check_duplicates_var = tk.BooleanVar()
        self.check_duplicates_var.set(self.config['SETTINGS'].getboolean('check_duplicates', True))
        
        check_duplicates_cb = ttk.Checkbutton(
            control_top_frame, 
            text="Kiểm tra video trùng lặp", 
            variable=self.check_duplicates_var,
            command=self.refresh_video_list
        )
        check_duplicates_cb.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Checkbox kiểm tra với lịch sử
        self.check_history_var = tk.BooleanVar()
        self.check_history_var.set(True)
        
        check_history_cb = ttk.Checkbutton(
            control_top_frame, 
            text="Kiểm tra với lịch sử đã tải lên", 
            variable=self.check_history_var,
            command=self.refresh_video_list
        )
        check_history_cb.pack(side=tk.RIGHT, padx=15, pady=5)
        
        # Frame hiển thị danh sách video
        videos_frame = ttk.LabelFrame(parent, text="Danh sách video")
        videos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo frame cho danh sách và thanh cuộn
        list_frame = ttk.Frame(videos_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thay đổi lớn: Sử dụng Treeview thay vì Listbox
        # Cấu hình cột
        self.video_tree = ttk.Treeview(list_frame, columns=("select", "filename", "status", "info"), show="headings")
        self.video_tree.heading("select", text="")
        self.video_tree.heading("filename", text="Tên file")
        self.video_tree.heading("status", text="Trạng thái")
        self.video_tree.heading("info", text="Thông tin thêm")
        
        # Thiết lập độ rộng cột
        self.video_tree.column("select", width=30, anchor=tk.CENTER)
        self.video_tree.column("filename", width=400, anchor=tk.W)
        self.video_tree.column("status", width=150, anchor=tk.CENTER)
        self.video_tree.column("info", width=200, anchor=tk.W)
        
        # Tạo scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.video_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Liên kết scrollbar với treeview
        self.video_tree.config(yscrollcommand=scrollbar.set)
        self.video_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Biến lưu trữ checkbox
        self.video_checkboxes = {}  # {item_id: BooleanVar}
        
        # Xử lý sự kiện khi click vào cột checkbox
        self.video_tree.bind("<ButtonRelease-1>", self.on_video_tree_click)
        
        # Xử lý sự kiện khi chọn video
        self.video_tree.bind("<<TreeviewSelect>>", self.on_video_select)
        
        # Tạo 3 nút dưới danh sách
        tree_buttons_frame = ttk.Frame(videos_frame)
        tree_buttons_frame.pack(fill=tk.X, pady=5)
        
        select_all_btn = ttk.Button(tree_buttons_frame, text="Chọn tất cả", 
                               command=self.select_all_videos)
        select_all_btn.pack(side=tk.LEFT, padx=5)
        
        deselect_all_btn = ttk.Button(tree_buttons_frame, text="Bỏ chọn tất cả", 
                                 command=self.deselect_all_videos)
        deselect_all_btn.pack(side=tk.LEFT, padx=5)
        
        invert_selection_btn = ttk.Button(tree_buttons_frame, text="Đảo chọn", 
                                     command=self.invert_video_selection)
        invert_selection_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame thông tin video
        info_frame = ttk.LabelFrame(parent, text="Thông tin video đã chọn")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame thông tin bên trái
        info_left_frame = ttk.Frame(info_frame)
        info_left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Hiển thị hình thu nhỏ
        self.thumbnail_label = ttk.Label(info_left_frame, text="Không có video nào được chọn")
        self.thumbnail_label.pack(padx=5, pady=5)
        
        # Thêm nút để xem video
        self.play_video_btn = ttk.Button(info_left_frame, text="Xem video", 
                                   command=self.play_selected_video,
                                   state=tk.DISABLED)
        self.play_video_btn.pack(padx=5, pady=5)
        
        # Frame thông tin bên phải
        info_right_frame = ttk.Frame(info_frame)
        info_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thông tin chi tiết
        self.info_text = tk.Text(info_right_frame, height=6, width=40, wrap=tk.WORD, font=("Arial", 10))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.config(state=tk.DISABLED)
        
        # Frame hiển thị các frame từ video
        frames_frame = ttk.LabelFrame(parent, text="Các khung hình từ video")
        frames_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame chứa các hình thu nhỏ
        self.frames_container = ttk.Frame(frames_frame)
        self.frames_container.pack(fill=tk.X, padx=5, pady=5)
        
        # Tạo 5 label cho các frame
        self.frame_labels = []
        for i in range(5):
            frame = ttk.Frame(self.frames_container)
            frame.pack(side=tk.LEFT, padx=5, expand=True)
            
            label = ttk.Label(frame, text=f"Frame {i+1}")
            label.pack(pady=2)
            
            self.frame_labels.append(label)
        
        # Frame trạng thái và điều khiển
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Thanh tiến trình
        self.progress = ttk.Progressbar(control_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        # Nhãn trạng thái
        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, style="Status.TLabel")
        status_label.pack(pady=5)
        
        # Frame chứa các nút điều khiển
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # Nút tải lên
        self.upload_btn = ttk.Button(btn_frame, text="Bắt đầu tải lên", command=self.start_upload)
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        # Nút dừng
        self.stop_btn = ttk.Button(btn_frame, text="Dừng lại", command=self.stop_upload, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Nút xóa video trùng lặp
        self.remove_duplicates_btn = ttk.Button(btn_frame, text="Loại bỏ trùng lặp", 
                                           command=self.remove_duplicates)
        self.remove_duplicates_btn.pack(side=tk.RIGHT, padx=5)
    def create_auto_tab(self, parent):
        """
        Tạo giao diện cho tab tự động
        
        Args:
            parent: Frame cha
        """
        # Frame chọn thư mục giám sát
        folder_frame = ttk.LabelFrame(parent, text="Thư mục giám sát tự động")
        folder_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Đường dẫn thư mục
        self.auto_folder_path = tk.StringVar()
        self.auto_folder_path.set(self.config['SETTINGS']['video_folder'])
        
        folder_entry = ttk.Entry(folder_frame, textvariable=self.auto_folder_path, width=50)
        folder_entry.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(folder_frame, text="Duyệt...", 
                                command=lambda: self.browse_folder(auto=True),
                                width=10)
        browse_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # Thêm khung chọn chế độ tự động
        mode_frame = ttk.LabelFrame(parent, text="Chế độ tự động")
        mode_frame.pack(fill=tk.X, padx=10, pady=10)

        # Radio buttons cho các chế độ
        self.auto_mode_var = tk.StringVar(value="watch")
        watch_radio = ttk.Radiobutton(
            mode_frame, 
            text="Theo dõi thư mục (tải lên video mới khi phát hiện)",
            variable=self.auto_mode_var,
            value="watch"
        )
        watch_radio.pack(anchor=tk.W, padx=5, pady=3)

        bulk_radio = ttk.Radiobutton(
            mode_frame, 
            text="Tải lên hàng loạt (quét và tải tất cả video trong thư mục)",
            variable=self.auto_mode_var,
            value="bulk"
        )
        bulk_radio.pack(anchor=tk.W, padx=5, pady=3)
        
        # Frame cài đặt tự động
        auto_settings_frame = ttk.LabelFrame(parent, text="Cài đặt tự động")
        auto_settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Thời gian kiểm tra
        ttk.Label(auto_settings_frame, text="Kiểm tra thư mục mỗi (giây):").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.check_interval_var = tk.StringVar()
        self.check_interval_var.set(self.config['SETTINGS']['auto_check_interval'])
        
        check_interval_entry = ttk.Entry(auto_settings_frame, textvariable=self.check_interval_var, width=10)
        check_interval_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Checkbox kiểm tra trùng lặp
        self.auto_check_duplicates_var = tk.BooleanVar()
        self.auto_check_duplicates_var.set(self.config['SETTINGS'].getboolean('check_duplicates', True))
        
        check_duplicates_cb = ttk.Checkbutton(
            auto_settings_frame, 
            text="Tự động loại bỏ video trùng lặp", 
            variable=self.auto_check_duplicates_var
        )
        check_duplicates_cb.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Checkbox kiểm tra với lịch sử
        self.auto_check_history_var = tk.BooleanVar()
        self.auto_check_history_var.set(True)
        
        check_history_cb = ttk.Checkbutton(
            auto_settings_frame, 
            text="Kiểm tra với lịch sử đã tải lên", 
            variable=self.auto_check_history_var
        )
        check_history_cb.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Checkbox lưu log
        self.auto_log_var = tk.BooleanVar()
        self.auto_log_var.set(True)
        
        auto_log_cb = ttk.Checkbutton(
            auto_settings_frame, 
            text="Ghi nhật ký hoạt động tự động", 
            variable=self.auto_log_var
        )
        auto_log_cb.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Frame trạng thái
        status_frame = ttk.LabelFrame(parent, text="Trạng thái giám sát")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo Text widget để hiển thị log hoạt động tự động
        self.auto_log_text = tk.Text(status_frame, wrap=tk.WORD, width=80, height=15, font=("Arial", 10))
        self.auto_log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thêm thanh cuộn
        auto_scrollbar = ttk.Scrollbar(self.auto_log_text)
        auto_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cấu hình
        self.auto_log_text.config(yscrollcommand=auto_scrollbar.set)
        auto_scrollbar.config(command=self.auto_log_text.yview)
        
        # Frame điều khiển
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Nhãn trạng thái
        self.auto_status_var = tk.StringVar()
        self.auto_status_var.set("Tự động tải lên: Tắt")
        
        auto_status_label = ttk.Label(
            control_frame, 
            textvariable=self.auto_status_var,
            style="Status.TLabel"
        )
        auto_status_label.pack(pady=5)
        
        # Frame nút
        auto_btn_frame = ttk.Frame(control_frame)
        auto_btn_frame.pack(fill=tk.X, pady=10)
        
        # Nút bắt đầu tự động
        self.start_auto_btn = ttk.Button(
            auto_btn_frame, 
            text="Bắt đầu tự động", 
            command=self.start_auto_upload
        )
        self.start_auto_btn.pack(side=tk.LEFT, padx=5)
        
        # Nút dừng tự động
        self.stop_auto_btn = ttk.Button(
            auto_btn_frame, 
            text="Dừng tự động", 
            command=self.stop_auto_upload,
            state=tk.DISABLED
        )
        self.stop_auto_btn.pack(side=tk.LEFT, padx=5)
        
        # Nút tải lên hàng loạt
        self.bulk_upload_btn = ttk.Button(
            auto_btn_frame, 
            text="Tải lên tất cả", 
            command=self.start_bulk_upload
        )
        self.bulk_upload_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_settings_tab(self, parent):
        """
        Tạo giao diện cho tab cài đặt
        
        Args:
            parent: Frame cha
        """
        # Tạo notebook cho các tab cài đặt con
        settings_notebook = ttk.Notebook(parent)
        settings_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab cài đặt Bot
        bot_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(bot_tab, text="Telegram Bot")
        
        # Tab cài đặt Telethon (cho file lớn)
        telethon_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(telethon_tab, text="Telethon API (Video lớn)")
        
        # Tab cài đặt chung
        general_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(general_tab, text="Cài đặt chung")
        
        # Tạo giao diện cho từng tab con
        self.create_bot_settings_tab(bot_tab)
        self.create_telethon_settings_tab(telethon_tab)
        self.create_general_settings_tab(general_tab)
    
    def create_bot_settings_tab(self, parent):
        """Tạo giao diện cài đặt Telegram Bot"""
        # Frame thông tin Telegram
        telegram_frame = ttk.LabelFrame(parent, text="Thông tin Telegram Bot")
        telegram_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Bot Token
        ttk.Label(telegram_frame, text="Bot Token:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.bot_token_var = tk.StringVar()
        self.bot_token_var.set(self.config['TELEGRAM']['bot_token'])
        
        token_entry = ttk.Entry(telegram_frame, textvariable=self.bot_token_var, width=60)
        token_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Chat ID đích
        ttk.Label(telegram_frame, text="Chat ID đích:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.chat_id_var = tk.StringVar()
        self.chat_id_var.set(self.config['TELEGRAM']['chat_id'])
        
        chat_id_entry = ttk.Entry(telegram_frame, textvariable=self.chat_id_var, width=60)
        chat_id_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Chat ID thông báo
        ttk.Label(telegram_frame, text="Chat ID thông báo:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.notification_chat_id_var = tk.StringVar()
        self.notification_chat_id_var.set(self.config['TELEGRAM']['notification_chat_id'])
        
        notif_id_entry = ttk.Entry(telegram_frame, textvariable=self.notification_chat_id_var, width=60)
        notif_id_entry.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Frame điều khiển
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Nút kiểm tra kết nối
        test_btn = ttk.Button(control_frame, text="Kiểm tra kết nối Telegram", 
                             command=self.test_telegram_connection)
        test_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Nút lưu cài đặt
        save_btn = ttk.Button(control_frame, text="Lưu cài đặt", command=self.save_settings)
        save_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # Thêm thông tin hướng dẫn
        info_frame = ttk.LabelFrame(parent, text="Thông tin bổ sung")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo frame cho text có thể cuộn
        info_scroll_frame = ttk.Frame(info_frame)
        info_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thêm thanh cuộn
        info_scrollbar = ttk.Scrollbar(info_scroll_frame)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tạo Text widget để hiển thị thông tin
        info_text_widget = tk.Text(info_scroll_frame, wrap=tk.WORD, width=80, height=15, font=("Arial", 10))
        info_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Kết nối thanh cuộn
        info_text_widget.config(yscrollcommand=info_scrollbar.set)
        info_scrollbar.config(command=info_text_widget.yview)
        
        info_text = (
            "Lưu ý khi sử dụng Telegram Video Uploader:\n\n"
            "1. Bot Telegram cần có quyền gửi tin nhắn và media trong kênh/nhóm đích\n"
            "2. Giới hạn kích thước file của Telegram Bot API là 50MB\n"
            "3. Chat ID kênh/nhóm thường có dạng -100xxxxxxxxxx\n"
            "4. Chat ID cá nhân có thể lấy bằng cách nhắn tin cho @userinfobot\n\n"
            "Hướng dẫn chi tiết:\n\n"
            "- Để tạo bot mới: Tìm @BotFather trên Telegram, gửi lệnh /newbot\n"
            "- Để lấy Chat ID từ API: Truy cập https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates\n"
            "- Tìm phần \"chat\" > \"id\" trong kết quả JSON\n\n"
            "Xử lý video lớn:\n\n"
            "- Telegram giới hạn kích thước file bot có thể gửi là 50MB\n"
            "- Ứng dụng sẽ tự động chia nhỏ hoặc nén video lớn hơn 50MB\n"
            "- Hoặc bạn có thể sử dụng Telethon API (tab cài đặt bên cạnh) để tải lên file lớn không giới hạn kích thước"
        )
        
        # Chèn văn bản vào widget
        info_text_widget.insert(tk.END, info_text)
        info_text_widget.config(state=tk.DISABLED)  # Đặt thành chỉ đọc
    
    def create_telethon_settings_tab(self, parent):
        """Tạo giao diện cài đặt Telethon API (cho video lớn)"""
        # Frame thông tin Telethon API
        telethon_frame = ttk.LabelFrame(parent, text="Thông tin Telethon API (cho video lớn)")
        telethon_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Checkbox bật/tắt Telethon
        self.use_telethon_var = tk.BooleanVar()
        self.use_telethon_var.set(self.config.getboolean('TELETHON', 'use_telethon', fallback=False))
        
        use_telethon_cb = ttk.Checkbutton(
            telethon_frame, 
            text="Sử dụng Telethon API cho video lớn hơn 50MB", 
            variable=self.use_telethon_var
        )
        use_telethon_cb.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
        
        # API ID
        ttk.Label(telethon_frame, text="API ID:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.api_id_var = tk.StringVar()
        self.api_id_var.set(self.config.get('TELETHON', 'api_id', fallback=''))
        
        api_id_entry = ttk.Entry(telethon_frame, textvariable=self.api_id_var, width=30)
        api_id_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # API Hash
        ttk.Label(telethon_frame, text="API Hash:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.api_hash_var = tk.StringVar()
        self.api_hash_var.set(self.config.get('TELETHON', 'api_hash', fallback=''))
        
        api_hash_entry = ttk.Entry(telethon_frame, textvariable=self.api_hash_var, width=60)
        api_hash_entry.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Số điện thoại
        ttk.Label(telethon_frame, text="Số điện thoại:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.phone_var = tk.StringVar()
        self.phone_var.set(self.config.get('TELETHON', 'phone', fallback=''))
        
        phone_entry = ttk.Entry(telethon_frame, textvariable=self.phone_var, width=30)
        phone_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Ghi chú số điện thoại
        ttk.Label(
            telethon_frame, 
            text="(Định dạng: +84123456789)",
            foreground="gray"
        ).grid(row=4, column=1, sticky=tk.W, padx=5)
        
        # Frame điều khiển
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Nút đăng nhập Telethon
        login_btn = ttk.Button(control_frame, text="Đăng nhập Telethon", 
                             command=self.login_telethon)
        login_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Nút lưu cài đặt
        save_btn = ttk.Button(control_frame, text="Lưu cài đặt", command=self.save_telethon_settings)
        save_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # Thêm thông tin hướng dẫn
        info_frame = ttk.LabelFrame(parent, text="Thông tin về Telethon API")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo Text widget để hiển thị thông tin
        info_text_widget = tk.Text(info_frame, wrap=tk.WORD, width=80, height=15, font=("Arial", 10))
        info_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_text = (
            "Telethon API cho phép tải lên video có kích thước lớn không giới hạn\n\n"
            "Để sử dụng Telethon API, bạn cần:\n"
            "1. Tạo ứng dụng API trên my.telegram.org/apps\n"
            "2. Nhập API ID và API Hash từ trang web trên\n"
            "3. Nhập số điện thoại Telegram của bạn (định dạng +84123456789)\n"
            "4. Nhấn nút 'Đăng nhập Telethon' và nhập mã xác thực được gửi đến điện thoại/Telegram của bạn\n\n"
            "Lưu ý:\n"
            "- Khi bật tính năng này, video lớn hơn 50MB sẽ được tải lên qua tài khoản người dùng của bạn thay vì bot\n"
            "- Telethon sẽ tạo một phiên đăng nhập lưu trên máy tính, bạn không cần đăng nhập lại sau mỗi lần khởi động ứng dụng\n"
            "- Khuyên dùng cho các video có kích thước rất lớn, vì tốc độ tải lên qua Telethon thường nhanh hơn\n"
            "- Khi sử dụng Telethon, video sẽ không bị chia nhỏ, giúp dễ dàng xem và quản lý hơn"
        )
        
        # Chèn văn bản vào widget
        info_text_widget.insert(tk.END, info_text)
        info_text_widget.config(state=tk.DISABLED)  # Đặt thành chỉ đọc
    
    def create_general_settings_tab(self, parent):
        """Tạo giao diện cài đặt chung"""
        # Frame cài đặt chung
        settings_frame = ttk.LabelFrame(parent, text="Cài đặt chung")
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Định dạng video
        ttk.Label(settings_frame, text="Định dạng video hỗ trợ:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.video_extensions_var = tk.StringVar()
        self.video_extensions_var.set(self.config['SETTINGS']['video_extensions'])
        
        extensions_entry = ttk.Entry(settings_frame, textvariable=self.video_extensions_var, width=60)
        extensions_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Thời gian chờ
        ttk.Label(settings_frame, text="Thời gian chờ giữa các lần tải (giây):").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.delay_var = tk.StringVar()
        self.delay_var.set(self.config['SETTINGS']['delay_between_uploads'])
        
        delay_entry = ttk.Entry(settings_frame, textvariable=self.delay_var, width=10)
        delay_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Frame điều khiển
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Nút lưu cài đặt
        save_btn = ttk.Button(control_frame, text="Lưu cài đặt", command=self.save_general_settings)
        save_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # Thêm thông tin về các cài đặt
        info_frame = ttk.LabelFrame(parent, text="Mô tả các cài đặt")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo Text widget để hiển thị thông tin
        info_text_widget = tk.Text(info_frame, wrap=tk.WORD, width=80, height=15, font=("Arial", 10))
        info_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_text = (
            "Định dạng video hỗ trợ:\n"
            "Danh sách các phần mở rộng file video được hỗ trợ, ngăn cách bằng dấu phẩy (không có khoảng trắng).\n"
            "Ví dụ: .mp4,.avi,.mkv,.mov,.wmv\n\n"
            
            "Thời gian chờ giữa các lần tải:\n"
            "Khoảng thời gian chờ giữa mỗi lần tải video lên Telegram, tính bằng giây.\n"
            "Giá trị khuyến nghị: 5-10 giây để tránh bị giới hạn tốc độ từ Telegram.\n\n"
            
            "Lưu ý:\n"
            "- Việc đặt thời gian chờ quá ngắn có thể dẫn đến lỗi 'Too Many Requests' từ Telegram\n"
            "- Ứng dụng sẽ tự động thử lại khi gặp lỗi giới hạn tốc độ, nhưng điều này có thể làm chậm quá trình tải lên\n"
            "- Nếu bạn thường xuyên tải lên nhiều video cùng lúc, hãy tăng thời gian chờ để tránh bị giới hạn"
        )
        
        # Chèn văn bản vào widget
        info_text_widget.insert(tk.END, info_text)
        info_text_widget.config(state=tk.DISABLED)  # Đặt thành chỉ đọc
    
    def create_history_tab(self, parent):
        """
        Tạo giao diện cho tab lịch sử
        
        Args:
            parent: Frame cha
        """
        # Frame chính
        main_frame = ttk.Frame(parent, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        ttk.Label(
            main_frame, 
            text="Lịch sử tải lên", 
            style="Heading.TLabel"
        ).pack(pady=10)
        
        # Giới thiệu
        ttk.Label(
            main_frame, 
            text="Quản lý và xem thông tin về các video đã tải lên trước đó"
        ).pack(pady=5)
        
        # Frame điều khiển
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Hiển thị số lượng video đã tải lên
        uploads = self.upload_history.get_all_uploads()
        upload_count = len(uploads)
        
        self.history_stats_label = ttk.Label(
            control_frame, 
            text=f"Tổng số video đã tải lên: {upload_count}"
        )
        self.history_stats_label.pack(side=tk.LEFT, padx=5)
        
        # Các nút điều khiển
        view_btn = ttk.Button(
            control_frame, 
            text="Xem lịch sử chi tiết", 
            command=self.show_history_dialog
        )
        view_btn.pack(side=tk.RIGHT, padx=5)
        
        clear_btn = ttk.Button(
            control_frame, 
            text="Xóa lịch sử", 
            command=self.confirm_clear_history,
            style="Warning.TButton"
        )
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Frame thông tin
        info_frame = ttk.LabelFrame(main_frame, text="Thông tin về lịch sử tải lên")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Giải thích cách hoạt động
        info_text = (
            "Tính năng lịch sử tải lên giúp bạn theo dõi và quản lý các video đã tải lên trước đó. "
            "Khi tải lên một video, hệ thống sẽ lưu thông tin về video đó, bao gồm hash, tên file, "
            "kích thước và ngày tải lên.\n\n"
            
            "Ứng dụng sẽ tự động kiểm tra các video mới so với lịch sử đã lưu. Nếu phát hiện video "
            "trùng lặp, bạn sẽ được thông báo, giúp tránh tải lên cùng một video nhiều lần.\n\n"
            
            "Tính năng này đặc biệt hữu ích khi bạn làm việc với thư viện video lớn và qua nhiều phiên "
            "làm việc khác nhau. Tất cả dữ liệu lịch sử được lưu trong file JSON, giúp dễ dàng sao lưu "
            "và chuyển đến máy tính khác."
        )
        
        info_text_widget = tk.Text(info_frame, wrap=tk.WORD, height=10, width=80, font=("Arial", 10))
        info_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        info_text_widget.insert(tk.END, info_text)
        info_text_widget.config(state=tk.DISABLED)  # Đặt thành chỉ đọc
        
        # Khung thống kê
        stats_frame = ttk.LabelFrame(main_frame, text="Thống kê nhanh")
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Grid layout cho thống kê
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        
        # Thống kê tổng số video
        ttk.Label(stats_frame, text="Tổng số video:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=5)
        self.total_videos_var = tk.StringVar(value=str(upload_count))
        ttk.Label(stats_frame, textvariable=self.total_videos_var, style="Status.TLabel").grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Thống kê video trong tháng này
        today = datetime.now()
        this_month_count = 0
        for info in uploads.values():
            try:
                upload_date = datetime.strptime(info.get('upload_date', ''), "%Y-%m-%d %H:%M:%S")
                if upload_date.year == today.year and upload_date.month == today.month:
                    this_month_count += 1
            except:
                pass
        
        ttk.Label(stats_frame, text="Video tải lên tháng này:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=5)
        self.month_videos_var = tk.StringVar(value=str(this_month_count))
        ttk.Label(stats_frame, textvariable=self.month_videos_var, style="Status.TLabel").grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Nút làm mới thống kê
        refresh_stats_btn = ttk.Button(
            stats_frame, 
            text="Làm mới thống kê", 
            command=self.refresh_history_stats,
            width=15
        )
        refresh_stats_btn.grid(row=0, column=2, rowspan=2, padx=20, pady=10)
    
    def create_log_tab(self, parent):
        """
        Tạo giao diện cho tab nhật ký
        
        Args:
            parent: Frame cha
        """
        # Tiêu đề
        ttk.Label(
            parent, 
            text="Nhật ký hoạt động ứng dụng", 
            style="Heading.TLabel"
        ).pack(pady=10)
        
        # Frame chứa log
        log_frame = ttk.Frame(parent)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tạo Text widget để hiển thị log
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, width=80, height=25, font=("Arial", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Thêm thanh cuộn
        log_scrollbar = ttk.Scrollbar(log_frame)
        log_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        
        # Cấu hình
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.log_text.yview)
        
        # Đặt trạng thái chỉ đọc
        self.log_text.config(state=tk.DISABLED)
        
        # Frame nút điều khiển
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Nút xóa log
        clear_btn = ttk.Button(control_frame, text="Xóa nhật ký", command=self.clear_log)
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Khởi tạo hook cho logger
        self.setup_logger_hook()
    def browse_folder(self, auto=False):
        """
        Mở hộp thoại chọn thư mục
        
        Args:
            auto (bool): True nếu chọn thư mục cho tab tự động
        """
        folder_path = filedialog.askdirectory(title="Chọn thư mục chứa video")
        
        if folder_path:
            if auto:
                self.auto_folder_path.set(folder_path)
                # Lưu vào cấu hình
                self.config['SETTINGS']['video_folder'] = folder_path
                with open('config.ini', 'w', encoding='utf-8') as configfile:
                    self.config.write(configfile)
            else:
                self.folder_path.set(folder_path)
                # Làm mới danh sách video
                self.refresh_video_list()
                # Lưu vào cấu hình
                self.config['SETTINGS']['video_folder'] = folder_path
                with open('config.ini', 'w', encoding='utf-8') as configfile:
                    self.config.write(configfile)
    
    def refresh_video_list(self):
        """Làm mới danh sách video từ thư mục đã chọn"""
        folder_path = self.folder_path.get()
        
        if not folder_path or not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            messagebox.showerror("Lỗi", "Thư mục không hợp lệ hoặc không tồn tại!")
            return
        
        # Xóa danh sách hiện tại
        for item in self.video_tree.get_children():
            self.video_tree.delete(item)
        self.videos = {}
        self.duplicate_groups = []
        self.video_checkboxes = {}
        
        # Lấy danh sách phần mở rộng video hợp lệ
        extensions = self.config['SETTINGS']['video_extensions'].split(',')
        
        # Cập nhật trạng thái
        self.status_var.set("Đang quét thư mục...")
        self.root.update_idletasks()
        
        # Quét thư mục
        video_files = []
        for file in os.listdir(folder_path):
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in extensions:
                video_files.append(file)
        
        # Kiểm tra nếu không có video nào
        if not video_files:
            self.status_var.set(f"Không tìm thấy video trong thư mục (định dạng hỗ trợ: {', '.join(extensions)})")
            return
        
        # Tạo danh sách video đã tải lên để so sánh
        already_uploaded_videos = set()
        
        # Thêm video vào treeview
        for video in video_files:
            # Đường dẫn đầy đủ
            video_path = os.path.join(folder_path, video)
            self.videos[video] = video_path
            
            # Tạo checkbox var
            check_var = tk.BooleanVar(value=False)
            
            # Thêm vào treeview với checkbox
            item_id = self.video_tree.insert("", tk.END, values=("☐", video, "", ""))
            
            # Lưu biến checkbox
            self.video_checkboxes[item_id] = check_var
        
        # Nếu có yêu cầu kiểm tra với lịch sử
        if self.check_history_var.get():
            self.status_var.set("Đang kiểm tra với lịch sử tải lên...")
            self.root.update_idletasks()
            
            # Lấy lịch sử đã tải lên
            upload_history = self.upload_history.get_all_uploads()
            
            # Kiểm tra từng video
            for item in self.video_tree.get_children():
                video_name = self.video_tree.item(item, "values")[1]
                video_path = self.videos.get(video_name)
                
                if video_path:
                    video_hash = self.video_analyzer.calculate_video_hash(video_path)
                    if video_hash and self.upload_history.is_uploaded(video_hash):
                        # Đánh dấu đã tải lên
                        self.video_tree.item(item, values=(self.video_tree.item(item, "values")[0], 
                                                        video_name, 
                                                        "Đã tải lên", 
                                                        ""))
                        already_uploaded_videos.add(video_name)
        
        # Nếu có yêu cầu kiểm tra trùng lặp
        if self.check_duplicates_var.get() and len(video_files) > 1:
            self.status_var.set("Đang phân tích video để tìm trùng lặp...")
            self.root.update_idletasks()
            
            # Tìm các video trùng lặp
            video_paths = [os.path.join(folder_path, video) for video in video_files]
            self.duplicate_groups = self.video_analyzer.find_duplicates(video_paths)
            
            # Đánh dấu các video trùng lặp
            if self.duplicate_groups:
                # Danh sách video đã đánh dấu trùng lặp
                marked_videos = set()
                
                for group in self.duplicate_groups:
                    # Chỉ đánh dấu nếu có từ 2 video trở lên trong nhóm
                    if len(group) > 1:
                        for video_path in group:
                            video_name = os.path.basename(video_path)
                            
                            # Tìm video trong treeview
                            for item in self.video_tree.get_children():
                                tree_video_name = self.video_tree.item(item, "values")[1]
                                
                                if tree_video_name == video_name:
                                    current_values = self.video_tree.item(item, "values")
                                    status = current_values[2] or "Trùng lặp"
                                    
                                    # Tìm tên video trùng lặp khác trong nhóm
                                    dup_names = [os.path.basename(v) for v in group if v != video_path]
                                    info = f"Trùng với: {', '.join(dup_names[:2])}"
                                    if len(dup_names) > 2:
                                        info += f" và {len(dup_names)-2} video khác"
                                    
                                    # Cập nhật trạng thái
                                    self.video_tree.item(item, values=(current_values[0], 
                                                                     tree_video_name, 
                                                                     status, 
                                                                     info))
                                    self.video_tree.item(item, tags=("duplicate",))
                                    marked_videos.add(video_name)
                                    break
                
                # Đặt style cho video trùng lặp
                self.video_tree.tag_configure("duplicate", background="#FFD2D2")  # Màu đỏ nhạt
                
                self.status_var.set(f"Đã tìm thấy {len(video_files)} video ({len(marked_videos)} video trùng lặp)")
            else:
                self.status_var.set(f"Đã tìm thấy {len(video_files)} video (không có trùng lặp)")
        
        # Đánh dấu các video đã tải lên trước đó
        if already_uploaded_videos:
            # Đặt style cho video đã tải lên
            self.video_tree.tag_configure("uploaded", background="#D2F0FF")  # Màu xanh nhạt
            
            for item in self.video_tree.get_children():
                video_name = self.video_tree.item(item, "values")[1]
                if video_name in already_uploaded_videos:
                    # Đánh dấu video đã tải lên
                    current_values = self.video_tree.item(item, "values")
                    self.video_tree.item(item, values=(current_values[0], 
                                                    video_name, 
                                                    "Đã tải lên", 
                                                    current_values[3]))
                    self.video_tree.item(item, tags=("uploaded",))
            
            self.status_var.set(f"Đã tìm thấy {len(video_files)} video ({len(already_uploaded_videos)} đã tải lên trước đó)")

    def on_video_tree_click(self, event):
        """Xử lý khi click vào cột checkbox"""
        region = self.video_tree.identify("region", event.x, event.y)
        if region == "heading":
            return  # Bỏ qua nếu click vào tiêu đề
        
        item = self.video_tree.identify("item", event.x, event.y)
        if not item:
            return  # Bỏ qua nếu không click vào item nào
        
        column = self.video_tree.identify("column", event.x, event.y)
        if column == "#1":  # Cột checkbox
            # Lấy biến checkbox
            check_var = self.video_checkboxes.get(item)
            if check_var:
                # Đảo trạng thái checkbox
                check_var.set(not check_var.get())
                
                # Cập nhật hiển thị
                current_values = self.video_tree.item(item, "values")
                checkbox_text = "☑" if check_var.get() else "☐"
                
                self.video_tree.item(item, values=(checkbox_text, 
                                                current_values[1], 
                                                current_values[2], 
                                                current_values[3]))

    def select_all_videos(self):
        """Chọn tất cả video trong danh sách"""
        for item in self.video_tree.get_children():
            check_var = self.video_checkboxes.get(item)
            if check_var:
                check_var.set(True)
                
                # Cập nhật hiển thị
                current_values = self.video_tree.item(item, "values")
                self.video_tree.item(item, values=("☑", 
                                                current_values[1], 
                                                current_values[2], 
                                                current_values[3]))

    def deselect_all_videos(self):
        """Bỏ chọn tất cả video trong danh sách"""
        for item in self.video_tree.get_children():
            check_var = self.video_checkboxes.get(item)
            if check_var:
                check_var.set(False)
                
                # Cập nhật hiển thị
                current_values = self.video_tree.item(item, "values")
                self.video_tree.item(item, values=("☐", 
                                                current_values[1], 
                                                current_values[2], 
                                                current_values[3]))

    def invert_video_selection(self):
        """Đảo trạng thái chọn tất cả video"""
        for item in self.video_tree.get_children():
            check_var = self.video_checkboxes.get(item)
            if check_var:
                # Đảo trạng thái
                check_var.set(not check_var.get())
                
                # Cập nhật hiển thị
                current_values = self.video_tree.item(item, "values")
                checkbox_text = "☑" if check_var.get() else "☐"
                
                self.video_tree.item(item, values=(checkbox_text, 
                                                current_values[1], 
                                                current_values[2], 
                                                current_values[3]))

    def play_selected_video(self):
        """Phát video đã chọn bằng trình phát mặc định của hệ thống"""
        # Lấy video đã chọn
        selected_items = self.video_tree.selection()
        if not selected_items:
            return
        
        # Lấy tên video
        video_name = self.video_tree.item(selected_items[0], "values")[1]
        video_path = self.videos.get(video_name)
        
        if not video_path or not os.path.exists(video_path):
            messagebox.showerror("Lỗi", "Không tìm thấy file video!")
            return
        
        try:
            # Mở video bằng ứng dụng mặc định
            if os.name == 'nt':  # Windows
                os.startfile(video_path)
            elif os.name == 'posix':  # Linux, macOS
                import subprocess
                subprocess.call(('xdg-open' if os.uname().sysname == 'Linux' else 'open', video_path))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở video: {str(e)}")

    def on_video_select(self, event):
        """Xử lý khi chọn video từ treeview"""
        # Lấy video đã chọn
        selected_items = self.video_tree.selection()
        
        if not selected_items:
            # Không có video nào được chọn
            self.thumbnail_label.config(text="Không có video nào được chọn")
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.config(state=tk.DISABLED)
            self.play_video_btn.config(state=tk.DISABLED)
            
            # Xóa các frame
            for label in self.frame_labels:
                label.config(text="", image="")
            
            return
        
        # Lấy tên video
        video_name = self.video_tree.item(selected_items[0], "values")[1]
        video_path = self.videos.get(video_name)
        
        if not video_path or not os.path.exists(video_path):
            return
        
        # Bật nút phát video
        self.play_video_btn.config(state=tk.NORMAL)
        
        # Hiển thị thông tin video
        self.display_video_info(video_path)
        
        # Hiển thị các frame từ video
        self.display_video_frames(video_path)

    def display_video_frames(self, video_path):
        """
        Hiển thị các frame từ video
        
        Args:
            video_path (str): Đường dẫn đến file video
        """
        try:
            # Sử dụng OpenCV để lấy các frame
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return
            
            # Lấy tổng số frame
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Chọn 5 vị trí ngẫu nhiên
            import random
            positions = sorted([random.uniform(0.1, 0.9) for _ in range(5)])
            
            # Lưu các frame
            frames = []
            
            for pos in positions:
                frame_pos = int(frame_count * pos)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                
                if ret:
                    # Chuyển frame sang định dạng PIL
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_pil = Image.fromarray(frame)
                    
                    # Thay đổi kích thước
                    frame_pil = frame_pil.resize((120, 90), Image.LANCZOS)
                    
                    # Chuyển sang định dạng Tkinter
                    frame_tk = ImageTk.PhotoImage(frame_pil)
                    frames.append(frame_tk)
            
            cap.release()
            
            # Lưu tham chiếu để tránh bị thu hồi bởi garbage collector
            self.current_frames = frames
            
            # Hiển thị các frame
            for i, frame in enumerate(frames):
                if i < len(self.frame_labels):
                    pos_percent = int(positions[i] * 100)
                    self.frame_labels[i].config(text=f"Frame {pos_percent}%", image=frame)
        
        except Exception as e:
            logger.error(f"Lỗi khi lấy frame từ video: {str(e)}")
    
    def display_video_info(self, video_path):
        """
        Hiển thị thông tin chi tiết của video
        
        Args:
            video_path (str): Đường dẫn đến file video
        """
        # Lấy thông tin video
        info = self.video_analyzer.get_video_info(video_path)
        
        if not info:
            return
        
        # Tạo hình thu nhỏ
        thumbnail = self.video_analyzer.get_thumbnail(video_path)
        
        if thumbnail:
            # Lưu tham chiếu để tránh bị thu hồi bởi garbage collector
            self.current_thumbnail = thumbnail
            self.thumbnail_label.config(image=thumbnail, text="")
        else:
            self.thumbnail_label.config(text="Không thể tạo hình thu nhỏ", image="")
        
        # Tính hash video để kiểm tra với lịch sử
        video_hash = info.get('hash', None)
        
        # Hiển thị thông tin
        file_name = info.get('file_name', os.path.basename(video_path))
        duration = info.get('duration', 0)
        resolution = info.get('resolution', 'Không rõ')
        file_size = info.get('file_size', 'Không rõ')
        
        # Kiểm tra trùng lặp
        duplicate_info = ""
        history_info = ""
        
        # Kiểm tra với lịch sử tải lên
        if video_hash and self.check_history_var.get():
            if self.upload_history.is_uploaded(video_hash):
                upload_info = self.upload_history.get_upload_info(video_hash)
                if upload_info:
                    history_info = f"\n\nĐã tải lên trước đó vào: {upload_info.get('upload_date', 'Không rõ')}"
        
        # Kiểm tra trùng lặp trong thư mục hiện tại
        if self.check_duplicates_var.get() and self.duplicate_groups:
            for group in self.duplicate_groups:
                if video_path in group:
                    # Video này nằm trong một nhóm trùng lặp
                    if len(group) > 1:
                        other_videos = [os.path.basename(v) for v in group if v != video_path]
                        duplicate_info = f"\n\nTrùng lặp với: {', '.join(other_videos)}"
                    break
        
        # Định dạng thông tin
        info_text = (
            f"Tên file: {file_name}\n"
            f"Thời lượng: {duration:.2f} giây\n"
            f"Độ phân giải: {resolution}\n"
            f"Kích thước: {file_size}{duplicate_info}{history_info}"
        )
        
        # Hiển thị thông tin
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info_text)
        self.info_text.config(state=tk.DISABLED)
    def start_upload(self):
        """Bắt đầu quá trình tải lên video"""
        # Kiểm tra điều kiện
        if self.is_uploading:
            return
        
        # Lấy danh sách video đã chọn qua checkboxes
        selected_videos = []
        for item in self.video_tree.get_children():
            check_var = self.video_checkboxes.get(item)
            if check_var and check_var.get():
                # Video đã được chọn qua checkbox
                video_name = self.video_tree.item(item, "values")[1]
                selected_videos.append(video_name)
        
        if not selected_videos:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một video để tải lên!")
            return
        
        # Kiểm tra cấu hình Telegram
        bot_token = self.config['TELEGRAM']['bot_token']
        chat_id = self.config['TELEGRAM']['chat_id']
        notification_chat_id = self.config['TELEGRAM']['notification_chat_id']
        
        if not bot_token or not chat_id:
            messagebox.showerror("Lỗi", "Vui lòng cấu hình Bot Token và Chat ID trong tab Cài đặt!")
            self.notebook.select(2)  # Chuyển đến tab Cài đặt
            return
        
        # Kết nối lại với Telegram nếu cần
        if not self.telegram_api.connected:
            if not self.telegram_api.connect(bot_token):
                messagebox.showerror("Lỗi", "Không thể kết nối với Telegram API. Vui lòng kiểm tra Bot Token và kết nối internet!")
                return
        
        # Bắt đầu quá trình tải lên
        self.is_uploading = True
        self.should_stop = False
        
        # Cập nhật trạng thái giao diện
        self.upload_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Tạo và bắt đầu thread tải lên
        folder_path = self.folder_path.get()
        upload_thread = threading.Thread(
            target=self.upload_videos,
            args=(folder_path, selected_videos, chat_id, notification_chat_id)
        )
        upload_thread.daemon = True
        upload_thread.start()
    
    def upload_videos(self, folder_path, video_files, chat_id, notification_chat_id):
        """
        Tải lên các video trong thread riêng
        
        Args:
            folder_path (str): Đường dẫn thư mục
            video_files (list): Danh sách tên file video
            chat_id (str): ID chat Telegram đích
            notification_chat_id (str): ID chat để gửi thông báo
        """
        start_time = time.time()
        
        try:
            # Chuẩn bị thanh tiến trình
            total_videos = len(video_files)
            self.progress['maximum'] = total_videos
            self.progress['value'] = 0
            
            # Gửi thông báo bắt đầu
            start_message = f"🚀 Bắt đầu tải lên {total_videos} video"
            logger.info(start_message)
            
            if notification_chat_id:
                self.telegram_api.send_notification(notification_chat_id, start_message)
            
            # Thời gian chờ giữa các lần tải
            delay = int(self.config['SETTINGS'].get('delay_between_uploads', 5))
            
            # Biến để theo dõi kết quả tải lên
            successful_uploads = 0
            failed_uploads = 0
            skipped_uploads = 0
            
            # Kiểm tra cài đặt Telethon
            use_telethon = self.config.getboolean('TELETHON', 'use_telethon', fallback=False)
            
            # Tải lên từng video
            for index, video_file in enumerate(video_files):
                if self.should_stop:
                    logger.info("Đã dừng quá trình tải lên theo yêu cầu")
                    break
                
                try:
                    # Đường dẫn đầy đủ đến file video
                    video_path = os.path.join(folder_path, video_file)
                    
                    # Kiểm tra kết nối internet
                    if not self.telegram_api.check_internet_connection():
                        error_msg = "Mất kết nối internet. Đang chờ kết nối lại..."
                        self.status_var.set(error_msg)
                        self.root.update_idletasks()
                        
                        # Chờ kết nối internet
                        while not self.telegram_api.check_internet_connection() and not self.should_stop:
                            time.sleep(5)
                            self.status_var.set(f"{error_msg} (đã chờ {(time.time() - start_time):.0f}s)")
                            self.root.update_idletasks()
                        
                        if self.should_stop:
                            break
                    
                    # Cập nhật trạng thái
                    status_text = f"Đang tải lên {index + 1}/{total_videos}: {video_file}"
                    self.status_var.set(status_text)
                    self.root.update_idletasks()
                    
                    # Kiểm tra kích thước file
                    file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                    
                    # Quyết định sử dụng Bot API hay Telethon
                    success = False
                    if use_telethon and file_size > 49 and self.telethon_uploader.connected:
                        # Sử dụng Telethon cho file lớn
                        logger.info(f"Sử dụng Telethon API để tải lên file lớn: {video_file} ({file_size:.2f} MB)")
                        self.status_var.set(f"Đang tải lên qua Telethon: {video_file}")
                        self.root.update_idletasks()
                        
                        success = self.telethon_uploader.upload_video(chat_id, video_path)
                    else:
                        # Sử dụng Bot API
                        success = self.telegram_api.send_video(chat_id, video_path)
                    
                    if success:
                        log_message = f"✅ Đã tải lên thành công: {video_file}"
                        logger.info(log_message)
                        successful_uploads += 1
                        
                        # Thêm vào lịch sử
                        video_hash = self.video_analyzer.calculate_video_hash(video_path)
                        if video_hash:
                            file_size = os.path.getsize(video_path)
                            self.upload_history.add_upload(video_hash, video_file, video_path, file_size)
                    else:
                        log_message = f"❌ Tải lên thất bại: {video_file}"
                        logger.error(log_message)
                        failed_uploads += 1
                    
                    # Cập nhật tiến trình
                    self.progress['value'] = index + 1
                    self.root.update_idletasks()
                    
                    # Chờ giữa các lần tải lên để tránh rate limit
                    if index < total_videos - 1 and not self.should_stop:
                        time.sleep(delay)
                
                except Exception as e:
                    logger.error(f"Lỗi khi tải lên video {video_file}: {str(e)}")
                    failed_uploads += 1
                    
                    # Cập nhật trạng thái lỗi
                    self.status_var.set(f"Lỗi khi tải lên {video_file}: {str(e)}")
                    self.root.update_idletasks()
                    time.sleep(2)  # Hiển thị thông báo lỗi trong 2 giây
            
            # Hoàn tất
            if self.should_stop:
                self.status_var.set(f"Đã dừng tải lên ({successful_uploads} thành công, {failed_uploads} thất bại)")
                
                if notification_chat_id:
                    self.telegram_api.send_notification(
                        notification_chat_id, 
                        f"🛑 Đã dừng tải lên ({successful_uploads} thành công, {failed_uploads} thất bại)"
                    )
            else:
                self.status_var.set(f"Đã hoàn tất: {successful_uploads} thành công, {failed_uploads} thất bại")
                
                if notification_chat_id:
                    self.telegram_api.send_notification(
                        notification_chat_id, 
                        f"✅ Đã hoàn tất tải lên: {successful_uploads} thành công, {failed_uploads} thất bại"
                    )
                
                # Làm mới thống kê lịch sử
                self.refresh_history_stats()
        
        except Exception as e:
            logger.error(f"Lỗi trong quá trình tải lên: {str(e)}")
            logger.error(traceback.format_exc())
            self.status_var.set(f"Lỗi: {str(e)}")
        
        finally:
            # Cập nhật trạng thái
            self.is_uploading = False
            
            # Cập nhật giao diện
            self.upload_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def stop_upload(self):
        """Dừng quá trình tải lên"""
        if self.is_uploading:
            self.should_stop = True
            self.status_var.set("Đang dừng tải lên...")
            logger.info("Đã yêu cầu dừng quá trình tải lên")
    
    def remove_duplicates(self):
        """Loại bỏ video trùng lặp khỏi danh sách"""
        if not self.duplicate_groups and not self.check_history_var.get():
            messagebox.showinfo("Thông báo", "Không có video trùng lặp nào để loại bỏ!")
            return
        
        # Tập hợp các video cần giữ lại (một video từ mỗi nhóm trùng lặp)
        keep_videos = set()
        # Tập hợp các video cần loại bỏ
        remove_videos = set()
        
        # Xử lý trùng lặp trong thư mục hiện tại
        for group in self.duplicate_groups:
            if len(group) > 1:
                # Chọn video có kích thước lớn nhất trong nhóm để giữ lại
                best_video = max(group, key=os.path.getsize)
                
                # Thêm vào danh sách giữ lại
                keep_videos.add(best_video)
                
                # Thêm các video còn lại vào danh sách loại bỏ
                for video in group:
                    if video != best_video:
                        remove_videos.add(video)
        
        # Xử lý trùng lặp với lịch sử nếu có yêu cầu
        if self.check_history_var.get():
            # Lấy video trong thư mục
            for video_name, video_path in self.videos.items():
                # Tính hash của video
                video_hash = self.video_analyzer.calculate_video_hash(video_path)
                
                # Kiểm tra nếu đã tồn tại trong lịch sử
                if video_hash and self.upload_history.is_uploaded(video_hash):
                    # Thêm vào danh sách loại bỏ nếu không phải là video tốt nhất
                    if video_path not in keep_videos:
                        remove_videos.add(video_path)
        
        if not remove_videos:
            messagebox.showinfo("Thông báo", "Không có video trùng lặp nào để loại bỏ!")
            return
        
        # Loại bỏ các video trùng lặp khỏi treeview
        video_names_to_remove = [os.path.basename(video) for video in remove_videos]
        
        # Xóa từ treeview
        for item in list(self.video_tree.get_children()):
            video_name = self.video_tree.item(item, "values")[1]
            if video_name in video_names_to_remove:
                self.video_tree.delete(item)
                # Xóa khỏi dict videos
                if video_name in self.videos:
                    del self.videos[video_name]
                # Xóa khỏi video_checkboxes
                if item in self.video_checkboxes:
                    del self.video_checkboxes[item]
        
        # Cập nhật trạng thái
        removed_count = len(video_names_to_remove)
        logger.info(f"Đã loại bỏ {removed_count} video trùng lặp")
        self.status_var.set(f"Đã loại bỏ {removed_count} video trùng lặp")
    
    def start_auto_upload(self):
        """Bắt đầu chế độ tự động tải lên"""
        # Kiểm tra chế độ tự động được chọn
        if self.auto_mode_var.get() == "bulk":
            self.start_bulk_upload()
            return
        
        # Phần còn lại của mã hiện tại cho chế độ theo dõi
        # Kiểm tra điều kiện
        if self.auto_upload_active:
            return
        
        # Kiểm tra thư mục
        folder_path = self.auto_folder_path.get()
        if not folder_path or not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            messagebox.showerror("Lỗi", "Thư mục không hợp lệ hoặc không tồn tại!")
            return
        
        # Kiểm tra cấu hình Telegram
        bot_token = self.config['TELEGRAM']['bot_token']
        chat_id = self.config['TELEGRAM']['chat_id']
        
        if not bot_token or not chat_id:
            messagebox.showerror("Lỗi", "Vui lòng cấu hình Bot Token và Chat ID trong tab Cài đặt!")
            self.notebook.select(2)  # Chuyển đến tab Cài đặt
            return
        
        # Kết nối lại với Telegram nếu cần
        if not self.telegram_api.connected:
            if not self.telegram_api.connect(bot_token):
                messagebox.showerror("Lỗi", "Không thể kết nối với Telegram API. Vui lòng kiểm tra Bot Token và kết nối internet!")
                return
        
        # Lấy cài đặt tự động
        try:
            check_interval = int(self.check_interval_var.get())
            if check_interval < 5:
                messagebox.showwarning("Cảnh báo", "Thời gian kiểm tra quá ngắn có thể gây tải nặng cho hệ thống. Khuyến nghị ít nhất 30 giây.")
                check_interval = max(5, check_interval)  # Đảm bảo ít nhất 5 giây
        except ValueError:
            messagebox.showerror("Lỗi", "Thời gian kiểm tra phải là một số nguyên!")
            return
        
        # Lấy danh sách phần mở rộng
        extensions = self.config['SETTINGS']['video_extensions'].split(',')
        
        # Cập nhật trạng thái giao diện
        self.auto_upload_active = True
        self.start_auto_btn.config(state=tk.DISABLED)
        self.stop_auto_btn.config(state=tk.NORMAL)
        self.bulk_upload_btn.config(state=tk.DISABLED)
        self.auto_status_var.set("Tự động tải lên: Hoạt động")
        
        # Thêm log
        self.add_auto_log("Bắt đầu chế độ tự động tải lên")
        self.add_auto_log(f"Thư mục giám sát: {folder_path}")
        self.add_auto_log(f"Thời gian kiểm tra: {check_interval} giây")
        self.add_auto_log(f"Kiểm tra trùng lặp: {'Bật' if self.auto_check_duplicates_var.get() else 'Tắt'}")
        self.add_auto_log(f"Kiểm tra với lịch sử: {'Bật' if self.auto_check_history_var.get() else 'Tắt'}")
        
        # Khởi tạo AutoUploader nếu chưa có
        if not self.auto_uploader:
            self.auto_uploader = AutoUploader(self, self.video_analyzer)
            self.auto_uploader.set_log_callback(self.add_auto_log)
        
        # Bắt đầu tự động tải lên
        self.auto_uploader.start(
            folder_path=folder_path,
            extensions=extensions,
            check_interval=check_interval,
            check_duplicates=self.auto_check_duplicates_var.get(),
            check_history=self.auto_check_history_var.get()
        )
        
        # Lưu cài đặt
        self.config['SETTINGS']['auto_mode'] = 'true'
        self.config['SETTINGS']['auto_check_interval'] = str(check_interval)
        self.config['SETTINGS']['check_duplicates'] = str(self.auto_check_duplicates_var.get()).lower()
        with open('config.ini', 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
            
    def start_bulk_upload(self):
        """Bắt đầu quá trình tải lên hàng loạt"""
        # Kiểm tra điều kiện
        if self.auto_upload_active:
            messagebox.showwarning("Cảnh báo", "Chế độ tự động đang hoạt động. Vui lòng dừng lại trước.")
            return
        
        # Kiểm tra thư mục
        folder_path = self.auto_folder_path.get()
        if not folder_path or not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            messagebox.showerror("Lỗi", "Thư mục không hợp lệ hoặc không tồn tại!")
            return
        
        # Kiểm tra cấu hình Telegram
        bot_token = self.config['TELEGRAM']['bot_token']
        chat_id = self.config['TELEGRAM']['chat_id']
        
        if not bot_token or not chat_id:
            messagebox.showerror("Lỗi", "Vui lòng cấu hình Bot Token và Chat ID trong tab Cài đặt!")
            self.notebook.select(2)  # Chuyển đến tab Cài đặt
            return
        
        # Kết nối lại với Telegram nếu cần
        if not self.telegram_api.connected:
            if not self.telegram_api.connect(bot_token):
                messagebox.showerror("Lỗi", "Không thể kết nối với Telegram API. Vui lòng kiểm tra Bot Token và kết nối internet!")
                return
        
        # Lấy danh sách phần mở rộng
        extensions = self.config['SETTINGS']['video_extensions'].split(',')
        
        # Xác nhận từ người dùng
        if not messagebox.askyesno(
            "Xác nhận", 
            f"Ứng dụng sẽ quét và tải lên tất cả video từ thư mục:\n{folder_path}\n\nBạn có chắc muốn tiếp tục?"
        ):
            return
        
        # Khởi tạo BulkUploader nếu chưa có
        if not self.bulk_uploader:
            self.bulk_uploader = BulkUploader(self, self.video_analyzer)
            self.bulk_uploader.set_log_callback(self.add_auto_log)
            self.bulk_uploader.set_progress_callback(self.update_bulk_progress)
        
        # Cập nhật trạng thái
        self.auto_upload_active = True
        self.start_auto_btn.config(state=tk.DISABLED)
        self.stop_auto_btn.config(state=tk.NORMAL)
        self.bulk_upload_btn.config(state=tk.DISABLED)
        self.auto_status_var.set("Đang tải lên hàng loạt...")
        
        # Thêm log
        self.add_auto_log("Bắt đầu quét và tải lên hàng loạt")
        
        # Bắt đầu quá trình quét và tải lên
        success = self.bulk_uploader.scan_and_upload(
            folder_path=folder_path,
            extensions=extensions,
            check_duplicates=self.auto_check_duplicates_var.get(),
            check_history=self.auto_check_history_var.get()
        )
        
        if not success:
            self.add_auto_log("Không thể bắt đầu quá trình tải lên hàng loạt")
            self.auto_upload_active = False
            self.start_auto_btn.config(state=tk.NORMAL)
            self.bulk_upload_btn.config(state=tk.NORMAL)
            self.stop_auto_btn.config(state=tk.DISABLED)
            self.auto_status_var.set("Tự động tải lên: Tắt")

    def update_bulk_progress(self, progress):
        """Cập nhật tiến trình tải lên hàng loạt"""
        # Cập nhật thanh tiến trình nếu có
        if progress >= 100:
            self.auto_status_var.set("Đã hoàn tất tải lên hàng loạt")
            self.auto_upload_active = False
            self.start_auto_btn.config(state=tk.NORMAL)
            self.bulk_upload_btn.config(state=tk.NORMAL)
            self.stop_auto_btn.config(state=tk.DISABLED)
            
            # Cập nhật thống kê lịch sử
            self.refresh_history_stats()
        else:
            self.auto_status_var.set(f"Đang tải lên hàng loạt: {progress}%")
    
    def stop_auto_upload(self):
        """Dừng chế độ tự động tải lên"""
        if not self.auto_upload_active:
            return
        
        # Dừng AutoUploader nếu đang hoạt động
        if self.auto_uploader:
            self.auto_uploader.stop()
        
        # Dừng BulkUploader nếu đang hoạt động
        if self.bulk_uploader:
            self.bulk_uploader.stop()
        
        # Cập nhật trạng thái
        self.auto_upload_active = False
        
        # Cập nhật giao diện
        self.start_auto_btn.config(state=tk.NORMAL)
        self.stop_auto_btn.config(state=tk.DISABLED)
        self.bulk_upload_btn.config(state=tk.NORMAL)
        self.auto_status_var.set("Tự động tải lên: Tắt")
        
        # Thêm log
        self.add_auto_log("Đã dừng chế độ tự động tải lên")
        
        # Lưu cài đặt
        self.config['SETTINGS']['auto_mode'] = 'false'
        with open('config.ini', 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
    
    def add_auto_log(self, message):
        """
        Thêm thông báo vào nhật ký tự động
        
        Args:
            message (str): Thông báo cần thêm
        """
        if not self.auto_log_var.get():
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Thêm vào Text widget
        self.auto_log_text.config(state=tk.NORMAL)
        self.auto_log_text.insert(tk.END, log_entry)
        self.auto_log_text.see(tk.END)  # Cuộn xuống dòng cuối
        self.auto_log_text.config(state=tk.DISABLED)
        
        # Thêm vào log chung
        logger.info(f"[AUTO] {message}")
    
    def upload_single_video(self, video_path):
        """
        Tải lên một video duy nhất (được gọi từ AutoUploader)
        
        Args:
            video_path (str): Đường dẫn đến file video
            
        Returns:
            bool: True nếu tải lên thành công
        """
        chat_id = self.config['TELEGRAM']['chat_id']
        
        try:
            # Kiểm tra với lịch sử nếu có yêu cầu
            if hasattr(self, 'auto_check_history_var') and self.auto_check_history_var.get():
                video_hash = self.video_analyzer.calculate_video_hash(video_path)
                if video_hash and self.upload_history.is_uploaded(video_hash):
                    logger.info(f"Bỏ qua video đã tải lên trước đó: {os.path.basename(video_path)}")
                    return True  # Coi như đã tải lên thành công vì đã tồn tại
            
            # Kiểm tra kích thước file
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            
            # Quyết định sử dụng Bot API hay Telethon
            use_telethon = self.config.getboolean('TELETHON', 'use_telethon', fallback=False)
            success = False
            
            if use_telethon and file_size > 49 and self.telethon_uploader.connected:
                # Sử dụng Telethon cho file lớn
                logger.info(f"Sử dụng Telethon API để tải lên file lớn: {os.path.basename(video_path)} ({file_size:.2f} MB)")
                success = self.telethon_uploader.upload_video(chat_id, video_path)
            else:
                # Sử dụng Bot API
                success = self.telegram_api.send_video(chat_id, video_path)
            
            # Nếu tải lên thành công, thêm vào lịch sử
            if success:
                video_hash = self.video_analyzer.calculate_video_hash(video_path)
                if video_hash:
                    file_size = os.path.getsize(video_path)
                    file_name = os.path.basename(video_path)
                    self.upload_history.add_upload(video_hash, file_name, video_path, file_size)
            
            return success
        except Exception as e:
            logger.error(f"Lỗi khi tải lên video {os.path.basename(video_path)}: {str(e)}")
            return False
    
    def test_telegram_connection(self):
        """Kiểm tra kết nối Telegram"""
        bot_token = self.bot_token_var.get()
        notification_chat_id = self.notification_chat_id_var.get()
        
        if not bot_token:
            messagebox.showerror("Lỗi", "Vui lòng nhập Bot Token!")
            return
            
        if not notification_chat_id:
            # Nếu không có chat ID thông báo, thử dùng chat ID đích
            notification_chat_id = self.chat_id_var.get()
            if not notification_chat_id:
                messagebox.showerror("Lỗi", "Vui lòng nhập Chat ID thông báo hoặc Chat ID đích!")
                return
        
        # Hiển thị thông báo đang kiểm tra
        self.status_var.set("Đang kiểm tra kết nối Telegram...")
        self.root.update_idletasks()
        
        try:
            # Vì phần telegram_api có thể chưa được khởi tạo đúng,
            # tạo một instance mới để kiểm tra kết nối
            from utils.telegram_api import TelegramAPI
            temp_api = TelegramAPI()
            success, message = temp_api.test_connection(bot_token, notification_chat_id)
            
            if success:
                # Nếu thành công, lưu lại instance
                self.telegram_api = temp_api
                messagebox.showinfo("Thành công", message)
            else:
                messagebox.showerror("Lỗi", message)
        except Exception as e:
            messagebox.showerror("Lỗi kết nối", f"Không thể kiểm tra kết nối: {str(e)}")
        
        # Khôi phục trạng thái
        self.status_var.set("Sẵn sàng")
    
    def login_telethon(self):
        """Đăng nhập vào Telethon API để tải lên file lớn"""
        # Lấy thông tin từ giao diện
        api_id = self.api_id_var.get()
        api_hash = self.api_hash_var.get()
        phone = self.phone_var.get()
        
        # Kiểm tra các trường
        if not api_id or not api_hash or not phone:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ API ID, API Hash và số điện thoại!")
            return
        
        try:
            # Chuyển đổi API ID sang số
            api_id = int(api_id)
            
            # Hiển thị dialog đăng nhập
            if self.telethon_uploader.show_login_dialog(self.root):
                # Đăng nhập thành công
                messagebox.showinfo(
                    "Thành công", 
                    "Đăng nhập Telethon thành công! Bạn có thể tải lên video lớn hơn 50MB."
                )
                
                # Lưu cài đặt
                self.config['TELETHON']['api_id'] = str(api_id)
                self.config['TELETHON']['api_hash'] = api_hash
                self.config['TELETHON']['phone'] = phone
                with open('config.ini', 'w', encoding='utf-8') as configfile:
                    self.config.write(configfile)
            else:
                messagebox.showerror("Lỗi", "Đăng nhập Telethon thất bại. Vui lòng kiểm tra thông tin và thử lại.")
        except ValueError:
            messagebox.showerror("Lỗi", "API ID phải là một số nguyên!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi đăng nhập Telethon: {str(e)}")
    
    def save_settings(self):
        """Lưu cài đặt Telegram Bot từ giao diện vào file cấu hình"""
        # Lấy giá trị từ giao diện
        bot_token = self.bot_token_var.get()
        chat_id = self.chat_id_var.get()
        notification_chat_id = self.notification_chat_id_var.get()
        
        # Lưu vào cấu hình
        self.config['TELEGRAM']['bot_token'] = bot_token
        self.config['TELEGRAM']['chat_id'] = chat_id
        self.config['TELEGRAM']['notification_chat_id'] = notification_chat_id
        
        # Ghi file
        with open('config.ini', 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
        
        # Thông báo
        messagebox.showinfo("Thông báo", "Đã lưu cài đặt Bot Telegram thành công!")
        
        # Kết nối lại với Telegram nếu Bot Token thay đổi
        if bot_token != self.telegram_api.bot_token:
            self.telegram_api.disconnect()
            self.connect_telegram()
    
    def save_telethon_settings(self):
        """Lưu cài đặt Telethon từ giao diện vào file cấu hình"""
        # Lấy giá trị từ giao diện
        use_telethon = self.use_telethon_var.get()
        api_id = self.api_id_var.get()
        api_hash = self.api_hash_var.get()
        phone = self.phone_var.get()
        
        # Lưu vào cấu hình
        self.config['TELETHON']['use_telethon'] = str(use_telethon).lower()
        self.config['TELETHON']['api_id'] = api_id
        self.config['TELETHON']['api_hash'] = api_hash
        self.config['TELETHON']['phone'] = phone
        
        # Ghi file
        with open('config.ini', 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
        
        # Thông báo
        messagebox.showinfo("Thông báo", "Đã lưu cài đặt Telethon thành công!")
    
    def save_general_settings(self):
        """Lưu cài đặt chung từ giao diện vào file cấu hình"""
        # Lấy giá trị từ giao diện
        video_extensions = self.video_extensions_var.get()
        delay = self.delay_var.get()
        
        try:
            # Kiểm tra giá trị
            delay_value = int(delay)
            if delay_value < 0:
                raise ValueError("Thời gian chờ không được âm")
        except ValueError:
            messagebox.showerror("Lỗi", "Thời gian chờ phải là một số nguyên không âm!")
            return
        
        # Lưu vào cấu hình
        self.config['SETTINGS']['video_extensions'] = video_extensions
        self.config['SETTINGS']['delay_between_uploads'] = delay
        
        # Ghi file
        with open('config.ini', 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
        
        # Thông báo
        messagebox.showinfo("Thông báo", "Đã lưu cài đặt chung thành công!")
    
    def refresh_history_stats(self):
        """Làm mới thống kê lịch sử"""
        uploads = self.upload_history.get_all_uploads()
        upload_count = len(uploads)
        
        # Cập nhật nhãn và biến
        self.history_stats_label.config(text=f"Tổng số video đã tải lên: {upload_count}")
        self.total_videos_var.set(str(upload_count))
        
        # Tính video trong tháng này
        today = datetime.now()
        this_month_count = 0
        for info in uploads.values():
            try:
                upload_date = datetime.strptime(info.get('upload_date', ''), "%Y-%m-%d %H:%M:%S")
                if upload_date.year == today.year and upload_date.month == today.month:
                    this_month_count += 1
            except:
                pass
        
        self.month_videos_var.set(str(this_month_count))
    
    def show_history_dialog(self):
        """Hiển thị dialog xem lịch sử chi tiết"""
        dialog = UploadHistoryDialog(self.root, self.upload_history, self.video_analyzer)
        # Sau khi đóng dialog, làm mới thống kê
        self.root.wait_window(dialog.dialog)
        self.refresh_history_stats()
    
    def confirm_clear_history(self):
        """Xác nhận và xóa toàn bộ lịch sử"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa toàn bộ lịch sử tải lên?"):
            # Xóa toàn bộ lịch sử
            self.upload_history.clear_history()
            
            # Cập nhật thống kê
            self.refresh_history_stats()
            
            # Thông báo
            messagebox.showinfo("Thành công", "Đã xóa toàn bộ lịch sử tải lên")
    def setup_logger_hook(self):
        """Thiết lập hook để bắt các thông báo log và hiển thị trên UI"""
        class LogHandler(logging.Handler):
            def __init__(self, text_widget):
                logging.Handler.__init__(self)
                self.text_widget = text_widget
                # Giới hạn số dòng để tránh tràn bộ nhớ
                self.max_lines = 1000
                
            def emit(self, record):
                msg = self.format(record)
                
                # Thêm vào Text widget
                def append():
                    self.text_widget.config(state=tk.NORMAL)
                    
                    # Thêm tin nhắn mới
                    self.text_widget.insert(tk.END, msg + '\n')
                    
                    # Kiểm tra số dòng
                    lines = self.text_widget.get('1.0', tk.END).split('\n')
                    if len(lines) > self.max_lines:
                        # Xóa các dòng cũ nếu quá giới hạn
                        excess_lines = len(lines) - self.max_lines
                        self.text_widget.delete('1.0', f'{excess_lines + 1}.0')
                    
                    self.text_widget.see(tk.END)  # Cuộn xuống cuối
                    self.text_widget.config(state=tk.DISABLED)
                
                # Phải chạy trong luồng chính của Tkinter
                self.text_widget.after(0, append)
        
        # Tạo handler với định dạng riêng
        log_handler = LogHandler(self.log_text)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        log_handler.setLevel(logging.INFO)
        
        # Thêm handler vào root logger
        logging.getLogger().addHandler(log_handler)
    
    def clear_log(self):
        """Xóa nội dung nhật ký"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Thông báo
        logger.info("Đã xóa nhật ký")
    
    def check_internet_connection(self):
        """
        Kiểm tra kết nối internet
        
        Returns:
            bool: True nếu có kết nối internet
        """
        try:
            # Thử kết nối đến Google DNS
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            pass
        
        try:
            # Thử kết nối đến Telegram API
            socket.create_connection(("api.telegram.org", 443), timeout=3)
            return True
        except OSError:
            pass
        
        return False
    
    def on_closing(self):
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
            self.stop_auto_upload()
        
        # Lưu cấu hình
        with open('config.ini', 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
        
        # Ngắt kết nối các API
        if self.telegram_api:
            self.telegram_api.disconnect()
        
        if self.telethon_uploader:
            self.telethon_uploader.disconnect()
        
        # Đóng ứng dụng
        self.root.destroy()
        logger.info("Đã đóng ứng dụng")


def main():
    """Hàm main để khởi chạy ứng dụng"""
    # Cấu hình logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("telegram_uploader.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("Khởi động ứng dụng Telegram Video Uploader")
    
    # Tạo cửa sổ gốc
    root = tk.Tk()
    
    try:
        # Khởi tạo ứng dụng
        app = TelegramUploaderApp(root)
        
        # Chạy main loop
        root.mainloop()
    except Exception as e:
        # Log lỗi
        logger.error(f"Lỗi không thể khôi phục: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Hiển thị thông báo lỗi
        messagebox.showerror(
            "Lỗi nghiêm trọng",
            f"Đã xảy ra lỗi không thể khôi phục:\n\n{str(e)}\n\nVui lòng khởi động lại ứng dụng."
        )
        
        # Đóng ứng dụng
        root.destroy()


if __name__ == "__main__":
    main()