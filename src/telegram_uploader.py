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
from queue import Queue
import traceback

# Thêm thư mục nguồn vào đường dẫn
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Nhập các module tiện ích
    from utils.video_analyzer import VideoAnalyzer
    from utils.auto_uploader import AutoUploader, FileWatcher
    from utils.telegram_api import TelegramAPI
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
        self.root.geometry("950x650")
        self.root.minsize(800, 600)
        
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
        
        # Khởi tạo các thành phần
        self.video_analyzer = VideoAnalyzer()
        self.telegram_api = TelegramAPI()
        self.upload_queue = Queue()
        self.auto_uploader = None
        self.auto_upload_active = False
        self.watcher_thread = None
        
        # Kết nối với Telegram
        self.connect_telegram()
        
        # Tạo giao diện
        self.create_ui()
        
        # Khi đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def show_splash_screen(self):
        """Hiển thị splash screen khi khởi động ứng dụng"""
        splash = tk.Toplevel(self.root)
        splash.title("Đang khởi động...")
        splash.geometry("400x250")
        splash.overrideredirect(True)  # Ẩn thanh tiêu đề
        
        # Đặt splash vào giữa màn hình
        splash.update_idletasks()
        width = splash.winfo_width()
        height = splash.winfo_height()
        x = (splash.winfo_screenwidth() // 2) - (width // 2)
        y = (splash.winfo_screenheight() // 2) - (height // 2)
        splash.geometry(f"{width}x{height}+{x}+{y}")
        
        # Tạo frame chính
        main_frame = ttk.Frame(splash, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Đặt màu nền
        main_frame.configure(style="Splash.TFrame")
        style = ttk.Style()
        style.configure("Splash.TFrame", background="#f0f0f0")
        
        # Tiêu đề
        ttk.Label(
            main_frame, 
            text="Telegram Video Uploader", 
            font=("Arial", 18, "bold"),
            background="#f0f0f0"
        ).pack(pady=(30, 10))
        
        # Phiên bản
        ttk.Label(
            main_frame, 
            text="Phiên bản 1.0",
            font=("Arial", 10),
            background="#f0f0f0"
        ).pack()
        
        # Thanh tiến trình
        progress = ttk.Progressbar(main_frame, orient="horizontal", length=300, mode="indeterminate")
        progress.pack(pady=(30, 10))
        progress.start(10)
        
        # Nhãn trạng thái
        status_label = ttk.Label(
            main_frame, 
            text="Đang khởi động ứng dụng...",
            background="#f0f0f0"
        )
        status_label.pack(pady=10)
        
        # Bản quyền
        ttk.Label(
            main_frame, 
            text="© 2025 Telegram Video Uploader",
            font=("Arial", 8),
            foreground="gray",
            background="#f0f0f0"
        ).pack(side=tk.BOTTOM, pady=10)
        
        # Cập nhật giao diện
        self.root.update()
        
        # Đóng splash screen sau 2 giây
        self.root.after(2000, splash.destroy)
    
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
            
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            
            # Hiển thị cửa sổ cấu hình ban đầu nếu đây là lần đầu chạy
            self.show_first_run_config_dialog()
        
        config.read('config.ini', encoding='utf-8')
        return config
    
    def show_first_run_config_dialog(self):
        """Hiển thị cửa sổ cấu hình khi chạy lần đầu"""
        config_dialog = tk.Toplevel(self.root)
        config_dialog.title("Cấu hình ban đầu")
        config_dialog.geometry("500x400")
        config_dialog.resizable(False, False)
        config_dialog.transient(self.root)
        config_dialog.grab_set()  # Làm cho cửa sổ này là modal
        
        # Tạo frame chính
        main_frame = ttk.Frame(config_dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        ttk.Label(
            main_frame, 
            text="Chào mừng đến với Telegram Video Uploader!", 
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        ttk.Label(
            main_frame, 
            text="Vui lòng nhập thông tin cấu hình cho ứng dụng", 
            font=("Arial", 10)
        ).pack(pady=5)
        
        # Frame nhập thông tin Telegram
        telegram_frame = ttk.LabelFrame(main_frame, text="Thông tin Telegram Bot", padding=10)
        telegram_frame.pack(fill=tk.X, pady=10)
        
        # Bot Token
        ttk.Label(telegram_frame, text="Bot Token:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        token_entry = ttk.Entry(telegram_frame, width=40)
        token_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Thêm tooltip cho Bot Token
        ttk.Label(
            telegram_frame, 
            text="(Lấy từ @BotFather trên Telegram)",
            font=("Arial", 8),
            foreground="gray"
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # Chat ID đích
        ttk.Label(telegram_frame, text="Chat ID đích:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        chat_id_entry = ttk.Entry(telegram_frame, width=40)
        chat_id_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Thêm tooltip cho Chat ID
        ttk.Label(
            telegram_frame, 
            text="(ID kênh/nhóm để gửi video)",
            font=("Arial", 8),
            foreground="gray"
        ).grid(row=1, column=2, padx=5, pady=5)
        
        # Chat ID thông báo
        ttk.Label(telegram_frame, text="Chat ID thông báo:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        notif_id_entry = ttk.Entry(telegram_frame, width=40)
        notif_id_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Thêm tooltip
        ttk.Label(
            telegram_frame, 
            text="(ID của bạn để nhận thông báo)",
            font=("Arial", 8),
            foreground="gray"
        ).grid(row=2, column=2, padx=5, pady=5)
        
        # Thêm hướng dẫn
        help_frame = ttk.LabelFrame(main_frame, text="Hướng dẫn lấy thông tin", padding=10)
        help_frame.pack(fill=tk.X, pady=10)
        
        help_text = (
            "1. Tạo bot mới: Tìm @BotFather trên Telegram, gửi lệnh /newbot\n"
            "2. Lấy Bot Token từ tin nhắn BotFather gửi sau khi tạo bot\n"
            "3. Thêm bot vào kênh/nhóm, làm cho bot là admin để gửi media\n"
            "4. Lấy Chat ID: Gửi tin nhắn trong kênh/nhóm, sau đó truy cập\n"
            "   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates\n"
            "5. Để lấy Chat ID cá nhân: Tìm @userinfobot trên Telegram và nhắn tin"
        )
        
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT)
        help_label.pack(padx=5, pady=5, anchor=tk.W)
        
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
        def test_connection():
            bot_token = token_entry.get()
            notification_chat_id = notif_id_entry.get()
            
            if not bot_token:
                messagebox.showerror("Lỗi", "Vui lòng nhập Bot Token!")
                return
                
            if not notification_chat_id:
                messagebox.showerror("Lỗi", "Vui lòng nhập Chat ID thông báo!")
                return
                
            # Sử dụng TelegramAPI để kiểm tra kết nối
            success, message = self.telegram_api.test_connection(bot_token, notification_chat_id)
            
            if success:
                messagebox.showinfo("Thành công", message)
            else:
                messagebox.showerror("Lỗi", message)
        
        # Frame chứa các nút
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
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
        
        # Tab log
        log_tab = ttk.Frame(self.notebook)
        self.notebook.add(log_tab, text="Nhật ký")
        
        # Tạo UI cho tab chính
        self.create_main_tab(main_tab)
        
        # Tạo UI cho tab tự động
        self.create_auto_tab(auto_tab)
        
        # Tạo UI cho tab cài đặt
        self.create_settings_tab(settings_tab)
        
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
        
        browse_btn = ttk.Button(folder_frame, text="Duyệt...", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # Frame kiểm soát
        control_top_frame = ttk.Frame(parent)
        control_top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Nút làm mới danh sách
        refresh_btn = ttk.Button(control_top_frame, text="Làm mới danh sách", command=self.refresh_video_list)
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
        
        # Frame hiển thị danh sách video
        videos_frame = ttk.LabelFrame(parent, text="Danh sách video")
        videos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo frame cho danh sách và thanh cuộn
        list_frame = ttk.Frame(videos_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tạo scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Danh sách video với đa lựa chọn
        self.video_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        self.video_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Cấu hình scrollbar
        self.video_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.video_listbox.yview)
        
        # Frame thông tin video
        info_frame = ttk.LabelFrame(parent, text="Thông tin video đã chọn")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame thông tin bên trái
        info_left_frame = ttk.Frame(info_frame)
        info_left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Hiển thị hình thu nhỏ
        self.thumbnail_label = ttk.Label(info_left_frame, text="Không có video nào được chọn")
        self.thumbnail_label.pack(padx=5, pady=5)
        
        # Frame thông tin bên phải
        info_right_frame = ttk.Frame(info_frame)
        info_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thông tin chi tiết
        self.info_text = tk.Text(info_right_frame, height=4, width=40, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.config(state=tk.DISABLED)
        
        # Xử lý sự kiện chọn video
        self.video_listbox.bind('<<ListboxSelect>>', self.on_video_select)
        
        # Frame trạng thái và điều khiển
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Thanh tiến trình
        self.progress = ttk.Progressbar(control_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        # Nhãn trạng thái
        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
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
        self.remove_duplicates_btn = ttk.Button(btn_frame, text="Loại bỏ trùng lặp", command=self.remove_duplicates)
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
                                command=lambda: self.browse_folder(auto=True))
        browse_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # Frame cài đặt tự động
        auto_settings_frame = ttk.LabelFrame(parent, text="Cài đặt tự động")
        auto_settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Thời gian kiểm tra
        ttk.Label(auto_settings_frame, text="Kiểm tra thư mục mỗi (giây):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
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
        
        # Checkbox lưu log
        self.auto_log_var = tk.BooleanVar()
        self.auto_log_var.set(True)
        
        auto_log_cb = ttk.Checkbutton(
            auto_settings_frame, 
            text="Ghi nhật ký hoạt động tự động", 
            variable=self.auto_log_var
        )
        auto_log_cb.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Frame trạng thái
        status_frame = ttk.LabelFrame(parent, text="Trạng thái giám sát")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo Text widget để hiển thị log hoạt động tự động
        self.auto_log_text = tk.Text(status_frame, wrap=tk.WORD, width=80, height=15)
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
            font=("Arial", 10, "bold")
        )
        auto_status_label.pack(pady=5)
        
        # Frame nút
        auto_btn_frame = ttk.Frame(control_frame)
        auto_btn_frame.pack(fill=tk.X, pady=10)
        
        # Nút bắt đầu tự động
        self.start_auto_btn = ttk.Button(
            auto_btn_frame, 
            text="Bắt đầu tự động", 
            command=self.start"""
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
from queue import Queue
import traceback

# Thêm thư mục nguồn vào đường dẫn
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Nhập các module tiện ích
    from utils.video_analyzer import VideoAnalyzer
    from utils.auto_uploader import AutoUploader, FileWatcher
    from utils.telegram_api import TelegramAPI
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
        self.root.geometry("950x650")
        self.root.minsize(800, 600)
        
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
        
        # Khởi tạo các thành phần
        self.video_analyzer = VideoAnalyzer()
        self.telegram_api = TelegramAPI()
        self.upload_queue = Queue()
        self.auto_uploader = None
        self.auto_upload_active = False
        self.watcher_thread = None
        
        # Kết nối với Telegram
        self.connect_telegram()
        
        # Tạo giao diện
        self.create_ui()
        
        # Khi đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def show_splash_screen(self):
        """Hiển thị splash screen khi khởi động ứng dụng"""
        splash = tk.Toplevel(self.root)
        splash.title("Đang khởi động...")
        splash.geometry("400x250")
        splash.overrideredirect(True)  # Ẩn thanh tiêu đề
        
        # Đặt splash vào giữa màn hình
        splash.update_idletasks()
        width = splash.winfo_width()
        height = splash.winfo_height()
        x = (splash.winfo_screenwidth() // 2) - (width // 2)
        y = (splash.winfo_screenheight() // 2) - (height // 2)
        splash.geometry(f"{width}x{height}+{x}+{y}")
        
        # Tạo frame chính
        main_frame = ttk.Frame(splash, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Đặt màu nền
        main_frame.configure(style="Splash.TFrame")
        style = ttk.Style()
        style.configure("Splash.TFrame", background="#f0f0f0")
        
        # Tiêu đề
        ttk.Label(
            main_frame, 
            text="Telegram Video Uploader", 
            font=("Arial", 18, "bold"),
            background="#f0f0f0"
        ).pack(pady=(30, 10))
        
        # Phiên bản
        ttk.Label(
            main_frame, 
            text="Phiên bản 1.0",
            font=("Arial", 10),
            background="#f0f0f0"
        ).pack()
        
        # Thanh tiến trình
        progress = ttk.Progressbar(main_frame, orient="horizontal", length=300, mode="indeterminate")
        progress.pack(pady=(30, 10))
        progress.start(10)
        
        # Nhãn trạng thái
        status_label = ttk.Label(
            main_frame, 
            text="Đang khởi động ứng dụng...",
            background="#f0f0f0"
        )
        status_label.pack(pady=10)
        
        # Bản quyền
        ttk.Label(
            main_frame, 
            text="© 2025 Telegram Video Uploader",
            font=("Arial", 8),
            foreground="gray",
            background="#f0f0f0"
        ).pack(side=tk.BOTTOM, pady=10)
        
        # Cập nhật giao diện
        self.root.update()
        
        # Đóng splash screen sau 2 giây
        self.root.after(2000, splash.destroy)
    
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
            
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            
            # Hiển thị cửa sổ cấu hình ban đầu nếu đây là lần đầu chạy
            self.show_first_run_config_dialog()
        
        config.read('config.ini', encoding='utf-8')
        return config
    
    def show_first_run_config_dialog(self):
        """Hiển thị cửa sổ cấu hình khi chạy lần đầu"""
        config_dialog = tk.Toplevel(self.root)
        config_dialog.title("Cấu hình ban đầu")
        config_dialog.geometry("500x400")
        config_dialog.resizable(False, False)
        config_dialog.transient(self.root)
        config_dialog.grab_set()  # Làm cho cửa sổ này là modal
        
        # Tạo frame chính
        main_frame = ttk.Frame(config_dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        ttk.Label(
            main_frame, 
            text="Chào mừng đến với Telegram Video Uploader!", 
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        ttk.Label(
            main_frame, 
            text="Vui lòng nhập thông tin cấu hình cho ứng dụng", 
            font=("Arial", 10)
        ).pack(pady=5)
        
        # Frame nhập thông tin Telegram
        telegram_frame = ttk.LabelFrame(main_frame, text="Thông tin Telegram Bot", padding=10)
        telegram_frame.pack(fill=tk.X, pady=10)
        
        # Bot Token
        ttk.Label(telegram_frame, text="Bot Token:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        token_entry = ttk.Entry(telegram_frame, width=40)
        token_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Thêm tooltip cho Bot Token
        ttk.Label(
            telegram_frame, 
            text="(Lấy từ @BotFather trên Telegram)",
            font=("Arial", 8),
            foreground="gray"
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # Chat ID đích
        ttk.Label(telegram_frame, text="Chat ID đích:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        chat_id_entry = ttk.Entry(telegram_frame, width=40)
        chat_id_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Thêm tooltip cho Chat ID
        ttk.Label(
            telegram_frame, 
            text="(ID kênh/nhóm để gửi video)",
            font=("Arial", 8),
            foreground="gray"
        ).grid(row=1, column=2, padx=5, pady=5)
        
        # Chat ID thông báo
        ttk.Label(telegram_frame, text="Chat ID thông báo:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        notif_id_entry = ttk.Entry(telegram_frame, width=40)
        notif_id_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Thêm tooltip
        ttk.Label(
            telegram_frame, 
            text="(ID của bạn để nhận thông báo)",
            font=("Arial", 8),
            foreground="gray"
        ).grid(row=2, column=2, padx=5, pady=5)
        
        # Thêm hướng dẫn
        help_frame = ttk.LabelFrame(main_frame, text="Hướng dẫn lấy thông tin", padding=10)
        help_frame.pack(fill=tk.X, pady=10)
        
        help_text = (
            "1. Tạo bot mới: Tìm @BotFather trên Telegram, gửi lệnh /newbot\n"
            "2. Lấy Bot Token từ tin nhắn BotFather gửi sau khi tạo bot\n"
            "3. Thêm bot vào kênh/nhóm, làm cho bot là admin để gửi media\n"
            "4. Lấy Chat ID: Gửi tin nhắn trong kênh/nhóm, sau đó truy cập\n"
            "   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates\n"
            "5. Để lấy Chat ID cá nhân: Tìm @userinfobot trên Telegram và nhắn tin"
        )
        
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT)
        help_label.pack(padx=5, pady=5, anchor=tk.W)
        
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
        def test_connection():
            bot_token = token_entry.get()
            notification_chat_id = notif_id_entry.get()
            
            if not bot_token:
                messagebox.showerror("Lỗi", "Vui lòng nhập Bot Token!")
                return
                
            if not notification_chat_id:
                messagebox.showerror("Lỗi", "Vui lòng nhập Chat ID thông báo!")
                return
                
            # Sử dụng TelegramAPI để kiểm tra kết nối
            success, message = self.telegram_api.test_connection(bot_token, notification_chat_id)
            
            if success:
                messagebox.showinfo("Thành công", message)
            else:
                messagebox.showerror("Lỗi", message)
        
        # Frame chứa các nút
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
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
        
        # Tab log
        log_tab = ttk.Frame(self.notebook)
        self.notebook.add(log_tab, text="Nhật ký")
        
        # Tạo UI cho tab chính
        self.create_main_tab(main_tab)
        
        # Tạo UI cho tab tự động
        self.create_auto_tab(auto_tab)
        
        # Tạo UI cho tab cài đặt
        self.create_settings_tab(settings_tab)
        
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
        
        browse_btn = ttk.Button(folder_frame, text="Duyệt...", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # Frame kiểm soát
        control_top_frame = ttk.Frame(parent)
        control_top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Nút làm mới danh sách
        refresh_btn = ttk.Button(control_top_frame, text="Làm mới danh sách", command=self.refresh_video_list)
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
        
        # Frame hiển thị danh sách video
        videos_frame = ttk.LabelFrame(parent, text="Danh sách video")
        videos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo frame cho danh sách và thanh cuộn
        list_frame = ttk.Frame(videos_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tạo scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Danh sách video với đa lựa chọn
        self.video_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        self.video_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Cấu hình scrollbar
        self.video_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.video_listbox.yview)
        
        # Frame thông tin video
        info_frame = ttk.LabelFrame(parent, text="Thông tin video đã chọn")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame thông tin bên trái
        info_left_frame = ttk.Frame(info_frame)
        info_left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Hiển thị hình thu nhỏ
        self.thumbnail_label = ttk.Label(info_left_frame, text="Không có video nào được chọn")
        self.thumbnail_label.pack(padx=5, pady=5)
        
        # Frame thông tin bên phải
        info_right_frame = ttk.Frame(info_frame)
        info_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thông tin chi tiết
        self.info_text = tk.Text(info_right_frame, height=4, width=40, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.config(state=tk.DISABLED)
        
        # Xử lý sự kiện chọn video
        self.video_listbox.bind('<<ListboxSelect>>', self.on_video_select)
        
        # Frame trạng thái và điều khiển
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Thanh tiến trình
        self.progress = ttk.Progressbar(control_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        # Nhãn trạng thái
        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
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
        self.remove_duplicates_btn = ttk.Button(btn_frame, text="Loại bỏ trùng lặp", command=self.remove_duplicates)
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
                                command=lambda: self.browse_folder(auto=True))
        browse_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # Frame cài đặt tự động
        auto_settings_frame = ttk.LabelFrame(parent, text="Cài đặt tự động")
        auto_settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Thời gian kiểm tra
        ttk.Label(auto_settings_frame, text="Kiểm tra thư mục mỗi (giây):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
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
        
        # Checkbox lưu log
        self.auto_log_var = tk.BooleanVar()
        self.auto_log_var.set(True)
        
        auto_log_cb = ttk.Checkbutton(
            auto_settings_frame, 
            text="Ghi nhật ký hoạt động tự động", 
            variable=self.auto_log_var
        )
        auto_log_cb.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Frame trạng thái
        status_frame = ttk.LabelFrame(parent, text="Trạng thái giám sát")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo Text widget để hiển thị log hoạt động tự động
        self.auto_log_text = tk.Text(status_frame, wrap=tk.WORD, width=80, height=15)
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
            font=("Arial", 10, "bold")
        )
        auto_status_label.pack(pady=5)
        
        # Frame nút
        auto_btn_frame = ttk.Frame(control_frame)
        auto_btn_frame.pack(fill=tk.X, pady=10)
        
        # Nút bắt đầu tự động
        self.start_auto_btn = ttk.Button(
            auto_btn_frame, 
            text="Bắt đầu tự động", 
            command=self"""
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
from queue import Queue
import traceback

# Thêm thư mục nguồn vào đường dẫn
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Nhập các module tiện ích
    from utils.video_analyzer import VideoAnalyzer
    from utils.auto_uploader import AutoUploader, FileWatcher
    from utils.telegram_api import TelegramAPI
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
        self.root.geometry("950x650")
        self.root.minsize(800, 600)
        
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
        
        # Khởi tạo các thành phần
        self.video_analyzer = VideoAnalyzer()
        self.telegram_api = TelegramAPI()
        self.upload_queue = Queue()
        self.auto_uploader = None
        self.auto_upload_active = False
        self.watcher_thread = None
        
        # Kết nối với Telegram
        self.connect_telegram()
        
        # Tạo giao diện
        self.create_ui()
        
        # Khi đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def show_splash_screen(self):
        """Hiển thị splash screen khi khởi động ứng dụng"""
        splash = tk.Toplevel(self.root)
        splash.title("Đang khởi động...")
        splash.geometry("400x250")
        splash.overrideredirect(True)  # Ẩn thanh tiêu đề
        
        # Đặt splash vào giữa màn hình
        splash.update_idletasks()
        width = splash.winfo_width()
        height = splash.winfo_height()
        x = (splash.winfo_screenwidth() // 2) - (width // 2)
        y = (splash.winfo_screenheight() // 2) - (height // 2)
        splash.geometry(f"{width}x{height}+{x}+{y}")
        
        # Tạo frame chính
        main_frame = ttk.Frame(splash, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Đặt màu nền
        main_frame.configure(style="Splash.TFrame")
        style = ttk.Style()
        style.configure("Splash.TFrame", background="#f0f0f0")
        
        # Tiêu đề
        ttk.Label(
            main_frame, 
            text="Telegram Video Uploader", 
            font=("Arial", 18, "bold"),
            background="#f0f0f0"
        ).pack(pady=(30, 10))
        
        # Phiên bản
        ttk.Label(
            main_frame, 
            text="Phiên bản 1.0",
            font=("Arial", 10),
            background="#f0f0f0"
        ).pack()
        
        # Thanh tiến trình
        progress = ttk.Progressbar(main_frame, orient="horizontal", length=300, mode="indeterminate")
        progress.pack(pady=(30, 10))
        progress.start(10)
        
        # Nhãn trạng thái
        status_label = ttk.Label(
            main_frame, 
            text="Đang khởi động ứng dụng...",
            background="#f0f0f0"
        )
        status_label.pack(pady=10)
        
        # Bản quyền
        ttk.Label(
            main_frame, 
            text="© 2025 Telegram Video Uploader",
            font=("Arial", 8),
            foreground="gray",
            background="#f0f0f0"
        ).pack(side=tk.BOTTOM, pady=10)
        
        # Cập nhật giao diện
        self.root.update()
        
        # Đóng splash screen sau 2 giây
        self.root.after(2000, splash.destroy)
    
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
            
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            
            # Hiển thị cửa sổ cấu hình ban đầu nếu đây là lần đầu chạy
            self.show_first_run_config_dialog()
        
        config.read('config.ini', encoding='utf-8')
        return config
    
    def show_first_run_config_dialog(self):
        """Hiển thị cửa sổ cấu hình khi chạy lần đầu"""
        config_dialog = tk.Toplevel(self.root)
        config_dialog.title("Cấu hình ban đầu")
        config_dialog.geometry("500x400")
        config_dialog.resizable(False, False)
        config_dialog.transient(self.root)
        config_dialog.grab_set()  # Làm cho cửa sổ này là modal
        
        # Tạo frame chính
        main_frame = ttk.Frame(config_dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        ttk.Label(
            main_frame, 
            text="Chào mừng đến với Telegram Video Uploader!", 
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        ttk.Label(
            main_frame, 
            text="Vui lòng nhập thông tin cấu hình cho ứng dụng", 
            font=("Arial", 10)
        ).pack(pady=5)
        
        # Frame nhập thông tin Telegram
        telegram_frame = ttk.LabelFrame(main_frame, text="Thông tin Telegram Bot", padding=10)
        telegram_frame.pack(fill=tk.X, pady=10)
        
        # Bot Token
        ttk.Label(telegram_frame, text="Bot Token:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        token_entry = ttk.Entry(telegram_frame, width=40)
        token_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Thêm tooltip cho Bot Token
        ttk.Label(
            telegram_frame, 
            text="(Lấy từ @BotFather trên Telegram)",
            font=("Arial", 8),
            foreground="gray"
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # Chat ID đích
        ttk.Label(telegram_frame, text="Chat ID đích:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        chat_id_entry = ttk.Entry(telegram_frame, width=40)
        chat_id_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Thêm tooltip cho Chat ID
        ttk.Label(
            telegram_frame, 
            text="(ID kênh/nhóm để gửi video)",
            font=("Arial", 8),
            foreground="gray"
        ).grid(row=1, column=2, padx=5, pady=5)
        
        # Chat ID thông báo
        ttk.Label(telegram_frame, text="Chat ID thông báo:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        notif_id_entry = ttk.Entry(telegram_frame, width=40)
        notif_id_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Thêm tooltip
        ttk.Label(
            telegram_frame, 
            text="(ID của bạn để nhận thông báo)",
            font=("Arial", 8),
            foreground="gray"
        ).grid(row=2, column=2, padx=5, pady=5)
        
        # Thêm hướng dẫn
        help_frame = ttk.LabelFrame(main_frame, text="Hướng dẫn lấy thông tin", padding=10)
        help_frame.pack(fill=tk.X, pady=10)
        
        help_text = (
            "1. Tạo bot mới: Tìm @BotFather trên Telegram, gửi lệnh /newbot\n"
            "2. Lấy Bot Token từ tin nhắn BotFather gửi sau khi tạo bot\n"
            "3. Thêm bot vào kênh/nhóm, làm cho bot là admin để gửi media\n"
            "4. Lấy Chat ID: Gửi tin nhắn trong kênh/nhóm, sau đó truy cập\n"
            "   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates\n"
            "5. Để lấy Chat ID cá nhân: Tìm @userinfobot trên Telegram và nhắn tin"
        )
        
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT)
        help_label.pack(padx=5, pady=5, anchor=tk.W)
        
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
        def test_connection():
            bot_token = token_entry.get()
            notification_chat_id = notif_id_entry.get()
            
            if not bot_token:
                messagebox.showerror("Lỗi", "Vui lòng nhập Bot Token!")
                return
                
            if not notification_chat_id:
                messagebox.showerror("Lỗi", "Vui lòng nhập Chat ID thông báo!")
                return
                
            # Sử dụng TelegramAPI để kiểm tra kết nối
            success, message = self.telegram_api.test_connection(bot_token, notification_chat_id)
            
            if success:
                messagebox.showinfo("Thành công", message)
            else:
                messagebox.showerror("Lỗi", message)
        
        # Frame chứa các nút
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
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
        
        # Tab log
        log_tab = ttk.Frame(self.notebook)
        self.notebook.add(log_tab, text="Nhật ký")
        
        # Tạo UI cho tab chính
        self.create_main_tab(main_tab)
        
        # Tạo UI cho tab tự động
        self.create_auto_tab(auto_tab)
        
        # Tạo UI cho tab cài đặt
        self.create_settings_tab(settings_tab)
        
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
        
        browse_btn = ttk.Button(folder_frame, text="Duyệt...", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # Frame kiểm soát
        control_top_frame = ttk.Frame(parent)
        control_top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Nút làm mới danh sách
        refresh_btn = ttk.Button(control_top_frame, text="Làm mới danh sách", command=self.refresh_video_list)
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
        
        # Frame hiển thị danh sách video
        videos_frame = ttk.LabelFrame(parent, text="Danh sách video")
        videos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo frame cho danh sách và thanh cuộn
        list_frame = ttk.Frame(videos_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tạo scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Danh sách video với đa lựa chọn
        self.video_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        self.video_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Cấu hình scrollbar
        self.video_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.video_listbox.yview)
        
        # Frame thông tin video
        info_frame = ttk.LabelFrame(parent, text="Thông tin video đã chọn")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame thông tin bên trái
        info_left_frame = ttk.Frame(info_frame)
        info_left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Hiển thị hình thu nhỏ
        self.thumbnail_label = ttk.Label(info_left_frame, text="Không có video nào được chọn")
        self.thumbnail_label.pack(padx=5, pady=5)
        
        # Frame thông tin bên phải
        info_right_frame = ttk.Frame(info_frame)
        info_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thông tin chi tiết
        self.info_text = tk.Text(info_right_frame, height=4, width=40, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.config(state=tk.DISABLED)
        
        # Xử lý sự kiện chọn video
        self.video_listbox.bind('<<ListboxSelect>>', self.on_video_select)
        
        # Frame trạng thái và điều khiển
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Thanh tiến trình
        self.progress = ttk.Progressbar(control_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        # Nhãn trạng thái
        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
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
        self.remove_duplicates_btn = ttk.Button(btn_frame, text="Loại bỏ trùng lặp", command=self.remove_duplicates)
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
                                command=lambda: self.browse_folder(auto=True))
        browse_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # Frame cài đặt tự động
        auto_settings_frame = ttk.LabelFrame(parent, text="Cài đặt tự động")
        auto_settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Thời gian kiểm tra
        ttk.Label(auto_settings_frame, text="Kiểm tra thư mục mỗi (giây):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
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
        
        # Checkbox lưu log
        self.auto_log_var = tk.BooleanVar()
        self.auto_log_var.set(True)
        
        auto_log_cb = ttk.Checkbutton(
            auto_settings_frame, 
            text="Ghi nhật ký hoạt động tự động", 
            variable=self.auto_log_var
        )
        auto_log_cb.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Frame trạng thái
        status_frame = ttk.LabelFrame(parent, text="Trạng thái giám sát")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo Text widget để hiển thị log hoạt động tự động
        self.auto_log_text = tk.Text(status_frame, wrap=tk.WORD, width=80, height=15)
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
            font=("Arial", 10, "bold")
        )
        auto_status_label.pack(pady=5)
        
        # Frame nút
        auto_btn_frame = ttk.Frame(control_frame)
        auto_btn_frame.pack(fill=tk.X, pady=10)
        
        # Nút bắt đầu tự động
        self.start_auto_btn = ttk.Button(
            auto_btn_frame, 
            text="Bắt đầu tự động", 
            command=self"""
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
from queue import Queue
import traceback

# Thêm thư mục nguồn vào đường dẫn
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Nhập các module tiện ích
    from utils.video_analyzer import VideoAnalyzer
    from utils.auto_uploader import AutoUploader, FileWatcher
    from utils.telegram_api import TelegramAPI
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
        self.root.geometry("950x650")
        self.root.minsize(800, 600)
        
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
        
        # Khởi tạo các thành phần
        self.video_analyzer = VideoAnalyzer()
        self.telegram_api = TelegramAPI()
        self.upload_queue = Queue()
        self.auto_uploader = None
        self.auto_upload_active = False
        self.watcher_thread = None
        
        # Kết nối với Telegram
        self.connect_telegram()
        
        # Tạo giao diện
        self.create_ui()
        
        # Khi đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def show_splash_screen(self):
        """Hiển thị splash screen khi khởi động ứng dụng"""
        splash = tk.Toplevel(self.root)
        splash.title("Đang khởi động...")
        splash.geometry("400x250")
        splash.overrideredirect(True)  # Ẩn thanh tiêu đề
        
        # Đặt splash vào giữa màn hình
        splash.update_idletasks()
        width = splash.winfo_width()
        height = splash.winfo_height()
        x = (splash.winfo_screenwidth() // 2) - (width // 2)
        y = (splash.winfo_screenheight() // 2) - (height // 2)
        splash.geometry(f"{width}x{height}+{x}+{y}")
        
        # Tạo frame chính
        main_frame = ttk.Frame(splash, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Đặt màu nền
        main_frame.configure(style="Splash.TFrame")
        style = ttk.Style()
        style.configure("Splash.TFrame", background="#f0f0f0")
        
        # Tiêu đề
        ttk.Label(
            main_frame, 
            text="Telegram Video Uploader", 
            font=("Arial", 18, "bold"),
            background="#f0f0f0"
        ).pack(pady=(30, 10))
        
        # Phiên bản
        ttk.Label(
            main_frame, 
            text="Phiên bản 1.0",
            font=("Arial", 10),
            background="#f0f0f0"
        ).pack()
        
        # Thanh tiến trình
        progress = ttk.Progressbar(main_frame, orient="horizontal", length=300, mode="indeterminate")
        progress.pack(pady=(30, 10))
        progress.start(10)
        
        # Nhãn trạng thái
        status_label = ttk.Label(
            main_frame, 
            text="Đang khởi động ứng dụng...",
            background="#f0f0f0"
        )
        status_label.pack(pady=10)
        
        # Bản quyền
        ttk.Label(
            main_frame, 
            text="© 2025 Telegram Video Uploader",
            font=("Arial", 8),
            foreground="gray",
            background="#f0f0f0"
        ).pack(side=tk.BOTTOM, pady=10)
        
        # Cập nhật giao diện
        self.root.update()
        
        # Đóng splash screen sau 2 giây
        self.root.after(2000, splash.destroy)
    
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
            
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            
            # Hiển thị cửa sổ cấu hình ban đầu nếu đây là lần đầu chạy
            self.show_first_run_config_dialog()
        
        config.read('config.ini', encoding='utf-8')
        return config
    
    def show_first_run_config_dialog(self):
        """Hiển thị cửa sổ cấu hình khi chạy lần đầu"""
        config_dialog = tk.Toplevel(self.root)
        config_dialog.title("Cấu hình ban đầu")
        config_dialog.geometry("500x400")
        config_dialog.resizable(False, False)
        config_dialog.transient(self.root)
        config_dialog.grab_set()  # Làm cho cửa sổ này là modal
        
        # Tạo frame chính
        main_frame = ttk.Frame(config_dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        ttk.Label(
            main_frame, 
            text="Chào mừng đến với Telegram Video Uploader!", 
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        ttk.Label(
            main_frame, 
            text="Vui lòng nhập thông tin cấu hình cho ứng dụng", 
            font=("Arial", 10)
        ).pack(pady=5)
        
        # Frame nhập thông tin Telegram
        telegram_frame = ttk.LabelFrame(main_frame, text="Thông tin Telegram Bot", padding=10)
        telegram_frame.pack(fill=tk.X, pady=10)
        
        # Bot Token
        ttk.Label(telegram_frame, text="Bot Token:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        token_entry = ttk.Entry(telegram_frame, width=40)
        token_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Thêm tooltip cho Bot Token
        ttk.Label(
            telegram_frame, 
            text="(Lấy từ @BotFather trên Telegram)",
            font=("Arial", 8),
            foreground="gray"
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # Chat ID đích
        ttk.Label(telegram_frame, text="Chat ID đích:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        chat_id_entry = ttk.Entry(telegram_frame, width=40)
        chat_id_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Thêm tooltip cho Chat ID
        ttk.Label(
            telegram_frame, 
            text="(ID kênh/nhóm để gửi video)",
            font=("Arial", 8),
            foreground="gray"
        ).grid(row=1, column=2, padx=5, pady=5)
        
        # Chat ID thông báo
        ttk.Label(telegram_frame, text="Chat ID thông báo:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        notif_id_entry = ttk.Entry(telegram_frame, width=40)
        notif_id_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Thêm tooltip
        ttk.Label(
            telegram_frame, 
            text="(ID của bạn để nhận thông báo)",
            font=("Arial", 8),
            foreground="gray"
        ).grid(row=2, column=2, padx=5, pady=5)
        
        # Thêm hướng dẫn
        help_frame = ttk.LabelFrame(main_frame, text="Hướng dẫn lấy thông tin", padding=10)
        help_frame.pack(fill=tk.X, pady=10)
        
        help_text = (
            "1. Tạo bot mới: Tìm @BotFather trên Telegram, gửi lệnh /newbot\n"
            "2. Lấy Bot Token từ tin nhắn BotFather gửi sau khi tạo bot\n"
            "3. Thêm bot vào kênh/nhóm, làm cho bot là admin để gửi media\n"
            "4. Lấy Chat ID: Gửi tin nhắn trong kênh/nhóm, sau đó truy cập\n"
            "   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates\n"
            "5. Để lấy Chat ID cá nhân: Tìm @userinfobot trên Telegram và nhắn tin"
        )
        
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT)
        help_label.pack(padx=5, pady=5, anchor=tk.W)
        
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
        def test_connection():
            bot_token = token_entry.get()
            notification_chat_id = notif_id_entry.get()
            
            if not bot_token:
                messagebox.showerror("Lỗi", "Vui lòng nhập Bot Token!")
                return
                
            if not notification_chat_id:
                messagebox.showerror("Lỗi", "Vui lòng nhập Chat ID thông báo!")
                return
                
            # Sử dụng TelegramAPI để kiểm tra kết nối
            success, message = self.telegram_api.test_connection(bot_token, notification_chat_id)
            
            if success:
                messagebox.showinfo("Thành công", message)
            else:
                messagebox.showerror("Lỗi", message)
        
        # Frame chứa các nút
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
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
        
        # Tab log
        log_tab = ttk.Frame(self.notebook)
        self.notebook.add(log_tab, text="Nhật ký")
        
        # Tạo UI cho tab chính
        self.create_main_tab(main_tab)
        
        # Tạo UI cho tab tự động
        self.create_auto_tab(auto_tab)
        
        # Tạo UI cho tab cài đặt
        self.create_settings_tab(settings_tab)
        
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
        
        browse_btn = ttk.Button(folder_frame, text="Duyệt...", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # Frame kiểm soát
        control_top_frame = ttk.Frame(parent)
        control_top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Nút làm mới danh sách
        refresh_btn = ttk.Button(control_top_frame, text="Làm mới danh sách", command=self.refresh_video_list)
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
        
        # Frame hiển thị danh sách video
        videos_frame = ttk.LabelFrame(parent, text="Danh sách video")
        videos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo frame cho danh sách và thanh cuộn
        list_frame = ttk.Frame(videos_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tạo scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Danh sách video với đa lựa chọn
        self.video_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        self.video_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Cấu hình scrollbar
        self.video_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.video_listbox.yview)
        
        # Frame thông tin video
        info_frame = ttk.LabelFrame(parent, text="Thông tin video đã chọn")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame thông tin bên trái
        info_left_frame = ttk.Frame(info_frame)
        info_left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Hiển thị hình thu nhỏ
        self.thumbnail_label = ttk.Label(info_left_frame, text="Không có video nào được chọn")
        self.thumbnail_label.pack(padx=5, pady=5)
        
        # Frame thông tin bên phải
        info_right_frame = ttk.Frame(info_frame)
        info_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thông tin chi tiết
        self.info_text = tk.Text(info_right_frame, height=4, width=40, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.config(state=tk.DISABLED)
        
        # Xử lý sự kiện chọn video
        self.video_listbox.bind('<<ListboxSelect>>', self.on_video_select)
        
        # Frame trạng thái và điều khiển
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Thanh tiến trình
        self.progress = ttk.Progressbar(control_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        # Nhãn trạng thái
        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
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
        self.remove_duplicates_btn = ttk.Button(btn_frame, text="Loại bỏ trùng lặp", command=self.remove_duplicates)
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
                                command=lambda: self.browse_folder(auto=True))
        browse_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # Frame cài đặt tự động
        auto_settings_frame = ttk.LabelFrame(parent, text="Cài đặt tự động")
        auto_settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Thời gian kiểm tra
        ttk.Label(auto_settings_frame, text="Kiểm tra thư mục mỗi (giây):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
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
        
        # Checkbox lưu log
        self.auto_log_var = tk.BooleanVar()
        self.auto_log_var.set(True)
        
        auto_log_cb = ttk.Checkbutton(
            auto_settings_frame, 
            text="Ghi nhật ký hoạt động tự động", 
            variable=self.auto_log_var
        )
        auto_log_cb.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Frame trạng thái
        status_frame = ttk.LabelFrame(parent, text="Trạng thái giám sát")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo Text widget để hiển thị log hoạt động tự động
        self.auto_log_text = tk.Text(status_frame, wrap=tk.WORD, width=80, height=15)
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
            font=("Arial", 10, "bold")
        )
        auto_status_label.pack(pady=5)
        
        # Frame nút
        auto_btn_frame = ttk.Frame(control_frame)
        auto_btn_frame.pack(fill=tk.X, pady