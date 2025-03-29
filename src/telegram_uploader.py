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
from queue import Queue, Empty
import traceback

# Thêm thư mục nguồn vào đường dẫn
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Nhập các module tiện ích
    from utils.video_analyzer import VideoAnalyzer
    from utils.auto_uploader import AutoUploader, FileWatcher, BulkUploader
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
        self.bulk_uploader = None
        self.auto_upload_active = False
        self.watcher_thread = None
        
        # Lưu trữ video và thông tin liên quan
        self.videos = {}  # Dict lưu thông tin video
        self.duplicate_groups = []  # Danh sách các nhóm video trùng lặp
        
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
        # Frame thông tin Telegram
        telegram_frame = ttk.LabelFrame(parent, text="Thông tin Telegram Bot")
        telegram_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Bot Token
        ttk.Label(telegram_frame, text="Bot Token:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.bot_token_var = tk.StringVar()
        self.bot_token_var.set(self.config['TELEGRAM']['bot_token'])
        
        token_entry = ttk.Entry(telegram_frame, textvariable=self.bot_token_var, width=50)
        token_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Chat ID đích
        ttk.Label(telegram_frame, text="Chat ID đích:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.chat_id_var = tk.StringVar()
        self.chat_id_var.set(self.config['TELEGRAM']['chat_id'])
        
        chat_id_entry = ttk.Entry(telegram_frame, textvariable=self.chat_id_var, width=50)
        chat_id_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Chat ID thông báo
        ttk.Label(telegram_frame, text="Chat ID thông báo:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.notification_chat_id_var = tk.StringVar()
        self.notification_chat_id_var.set(self.config['TELEGRAM']['notification_chat_id'])
        
        notif_id_entry = ttk.Entry(telegram_frame, textvariable=self.notification_chat_id_var, width=50)
        notif_id_entry.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Frame cài đặt chung
        settings_frame = ttk.LabelFrame(parent, text="Cài đặt chung")
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Định dạng video
        ttk.Label(settings_frame, text="Định dạng video hỗ trợ:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.video_extensions_var = tk.StringVar()
        self.video_extensions_var.set(self.config['SETTINGS']['video_extensions'])
        
        extensions_entry = ttk.Entry(settings_frame, textvariable=self.video_extensions_var, width=50)
        extensions_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Thời gian chờ
        ttk.Label(settings_frame, text="Thời gian chờ giữa các lần tải (giây):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.delay_var = tk.StringVar()
        self.delay_var.set(self.config['SETTINGS']['delay_between_uploads'])
        
        delay_entry = ttk.Entry(settings_frame, textvariable=self.delay_var, width=10)
        delay_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Frame điều khiển
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Nút kiểm tra kết nối
        test_btn = ttk.Button(control_frame, text="Kiểm tra kết nối Telegram", command=self.test_telegram_connection)
        test_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Nút lưu cài đặt
        save_btn = ttk.Button(control_frame, text="Lưu cài đặt", command=self.save_settings)
        save_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # Thêm thông tin hướng dẫn
        info_frame = ttk.LabelFrame(parent, text="Thông tin bổ sung")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_text = (
            "Lưu ý khi sử dụng Telegram Video Uploader:\n\n"
            "1. Bot Telegram cần có quyền gửi tin nhắn và media trong kênh/nhóm đích\n"
            "2. Ứng dụng hỗ trợ tải lên video không giới hạn kích thước\n"
            "3. Chat ID kênh/nhóm thường có dạng -100xxxxxxxxxx\n"
            "4. Chat ID cá nhân có thể lấy bằng cách nhắn tin cho @userinfobot\n"
            "5. Các định dạng video hỗ trợ được ngăn cách bằng dấu phẩy (không có khoảng trắng)\n"
        )
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(padx=5, pady=5, anchor=tk.W)
    
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
            font=("Arial", 12, "bold")
        ).pack(pady=10)
        
        # Frame chứa log
        log_frame = ttk.Frame(parent)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tạo Text widget để hiển thị log
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, width=80, height=25)
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
    
    def setup_logger_hook(self):
        """Thiết lập hook để ghi log vào Text widget"""
        # Tạo handler tùy chỉnh
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                logging.Handler.__init__(self)
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                
                def append():
                    self.text_widget.config(state=tk.NORMAL)
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)  # Cuộn xuống dòng cuối
                    self.text_widget.config(state=tk.DISABLED)
                
                # Thực hiện từ thread giao diện
                self.text_widget.after(0, append)
        
        # Tạo handler và định dạng
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Thêm handler vào logger
        logger.addHandler(text_handler)
    
    def clear_log(self):
        """Xóa nội dung log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        logger.info("Đã xóa nhật ký")
    
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
        self.video_listbox.delete(0, tk.END)
        self.videos = {}
        self.duplicate_groups = []
        
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
        
        # Thêm video vào danh sách
        for video in video_files:
            self.video_listbox.insert(tk.END, video)
            # Lưu đường dẫn đầy đủ
            self.videos[video] = os.path.join(folder_path, video)
        
        # Cập nhật trạng thái
        file_count = len(video_files)
        self.status_var.set(f"Đã tìm thấy {file_count} video")
        
        # Nếu có yêu cầu kiểm tra trùng lặp
        if self.check_duplicates_var.get() and file_count > 1:
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
                            # Tìm vị trí trong listbox
                            for i in range(self.video_listbox.size()):
                                if self.video_listbox.get(i) == video_name:
                                    self.video_listbox.itemconfig(i, {'bg': '#FFD2D2'})  # Màu đỏ nhạt
                                    marked_videos.add(video_name)
                
                self.status_var.set(f"Đã tìm thấy {file_count} video ({len(marked_videos)} video trùng lặp)")
            else:
                self.status_var.set(f"Đã tìm thấy {file_count} video (không có trùng lặp)")
    
    def on_video_select(self, event):
        """
        Xử lý sự kiện khi chọn video từ danh sách
        
        Args:
            event: Sự kiện Tkinter
        """
        # Lấy chỉ số được chọn
        selected_indices = self.video_listbox.curselection()
        
        if not selected_indices:
            # Không có video nào được chọn
            self.thumbnail_label.config(text="Không có video nào được chọn")
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.config(state=tk.DISABLED)
            return
        
        # Lấy tên video đầu tiên được chọn
        selected_index = selected_indices[0]
        selected_video = self.video_listbox.get(selected_index)
        
        # Lấy đường dẫn
        video_path = self.videos.get(selected_video)
        
        if not video_path or not os.path.exists(video_path):
            return
        
        # Hiển thị thông tin video
        self.display_video_info(video_path)
    
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
        
        # Hiển thị thông tin
        file_name = info.get('file_name', os.path.basename(video_path))
        duration = info.get('duration', 0)
        resolution = info.get('resolution', 'Không rõ')
        file_size = info.get('file_size', 'Không rõ')
        
        # Kiểm tra trùng lặp
        duplicate_info = ""
        
        if self.check_duplicates_var.get() and self.duplicate_groups:
            for group in self.duplicate_groups:
                if video_path in group:
                    # Video này nằm trong một nhóm trùng lặp
                    if len(group) > 1:
                        other_videos = [os.path.basename(v) for v in group if v != video_path]
                        duplicate_info = f"\nTrùng lặp với: {', '.join(other_videos)}"
                    break
        
        # Định dạng thông tin
        info_text = (
            f"Tên file: {file_name}\n"
            f"Thời lượng: {duration:.2f} giây\n"
            f"Độ phân giải: {resolution}\n"
            f"Kích thước: {file_size}{duplicate_info}"
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
        
        # Lấy danh sách video đã chọn
        selected_indices = self.video_listbox.curselection()
        
        if not selected_indices:
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
        
        # Lấy video đã chọn
        selected_videos = [self.video_listbox.get(i) for i in selected_indices]
        folder_path = self.folder_path.get()
        
        # Bắt đầu quá trình tải lên
        self.is_uploading = True
        self.should_stop = False
        
        # Cập nhật trạng thái giao diện
        self.upload_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Tạo và bắt đầu thread tải lên
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
            
            # Tải lên từng video
            for index, video_file in enumerate(video_files):
                if self.should_stop:
                    logger.info("Đã dừng quá trình tải lên theo yêu cầu")
                    break
                
                try:
                    # Đường dẫn đầy đủ đến file video
                    video_path = os.path.join(folder_path, video_file)
                    
                    # Cập nhật trạng thái
                    status_text = f"Đang tải lên {index + 1}/{total_videos}: {video_file}"
                    self.status_var.set(status_text)
                    self.root.update_idletasks()
                    
                    # Tải lên video
                    success = self.telegram_api.send_video(chat_id, video_path)
                    
                    if success:
                        log_message = f"✅ Đã tải lên thành công: {video_file}"
                        logger.info(log_message)
                    else:
                        log_message = f"❌ Tải lên thất bại: {video_file}"
                        logger.error(log_message)
                    
                    # Cập nhật tiến trình
                    self.progress['value'] = index + 1
                    self.root.update_idletasks()
                    
                    # Chờ giữa các lần tải lên để tránh rate limit
                    if index < total_videos - 1 and not self.should_stop:
                        time.sleep(delay)
                
                except Exception as e:
                    logger.error(f"Lỗi khi tải lên video {video_file}: {str(e)}")
            
            # Hoàn tất
            if self.should_stop:
                self.status_var.set(f"Đã dừng tải lên ({self.progress['value']}/{total_videos})")
                
                if notification_chat_id:
                    self.telegram_api.send_notification(
                        notification_chat_id, 
                        f"🛑 Đã dừng tải lên ({self.progress['value']}/{total_videos})"
                    )
            else:
                self.status_var.set(f"Đã hoàn tất tải lên {total_videos} video")
                
                if notification_chat_id:
                    self.telegram_api.send_notification(
                        notification_chat_id, 
                        f"✅ Đã hoàn tất tải lên {total_videos} video"
                    )
        
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
        if not self.duplicate_groups:
            messagebox.showinfo("Thông báo", "Không có video trùng lặp nào để loại bỏ!")
            return
        
        # Tập hợp các video cần giữ lại (một video từ mỗi nhóm trùng lặp)
        keep_videos = set()
        # Tập hợp các video cần loại bỏ
        remove_videos = set()
        
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
        
        if not remove_videos:
            messagebox.showinfo("Thông báo", "Không có video trùng lặp nào để loại bỏ!")
            return
        
        # Loại bỏ các video trùng lặp khỏi listbox
        video_names_to_remove = [os.path.basename(video) for video in remove_videos]
        
        # Duyệt từ cuối danh sách để tránh lỗi chỉ số
        for i in range(self.video_listbox.size() - 1, -1, -1):
            video_name = self.video_listbox.get(i)
            if video_name in video_names_to_remove:
                self.video_listbox.delete(i)
                # Xóa khỏi dict videos
                if video_name in self.videos:
                    del self.videos[video_name]
        
        # Cập nhật trạng thái
        removed_count = len(video_names_to_remove)
        logger.info(f"Đã loại bỏ {removed_count} video trùng lặp")
        self.status_var.set(f"Đã loại bỏ {removed_count} video trùng lặp")
        
        # Xóa thông tin trùng lặp đã xử lý
        self.duplicate_groups = []
    
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
        
        # Khởi tạo AutoUploader nếu chưa có
        if not self.auto_uploader:
            self.auto_uploader = AutoUploader(self, self.video_analyzer)
            self.auto_uploader.set_log_callback(self.add_auto_log)
        
        # Bắt đầu tự động tải lên
        self.auto_uploader.start(
            folder_path=folder_path,
            extensions=extensions,
            check_interval=check_interval,
            check_duplicates=self.auto_check_duplicates_var.get()
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
            check_duplicates=self.auto_check_duplicates_var.get()
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
            # Tải lên video
            success = self.telegram_api.send_video(chat_id, video_path)
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
        
        # Kiểm tra kết nối
        success, message = self.telegram_api.test_connection(bot_token, notification_chat_id)
        
        if success:
            messagebox.showinfo("Thành công", message)
        else:
            messagebox.showerror("Lỗi", message)
        
        # Khôi phục trạng thái
        self.status_var.set("Sẵn sàng")
    
    def save_settings(self):
        """Lưu cài đặt từ giao diện vào file cấu hình"""
        # Lấy giá trị từ giao diện
        bot_token = self.bot_token_var.get()
        chat_id = self.chat_id_var.get()
        notification_chat_id = self.notification_chat_id_var.get()
        video_extensions = self.video_extensions_var.get()
        delay = self.delay_var.get()
        
        # Lưu vào cấu hình
        self.config['TELEGRAM']['bot_token'] = bot_token
        self.config['TELEGRAM']['chat_id'] = chat_id
        self.config['TELEGRAM']['notification_chat_id'] = notification_chat_id
        
        self.config['SETTINGS']['video_extensions'] = video_extensions
        self.config['SETTINGS']['delay_between_uploads'] = delay
        
        # Ghi file
        with open('config.ini', 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
        
        # Thông báo
        messagebox.showinfo("Thông báo", "Đã lưu cài đặt thành công!")
        
        # Kết nối lại với Telegram nếu Bot Token thay đổi
        if bot_token != self.telegram_api.bot_token:
            self.telegram_api.disconnect()
            self.connect_telegram()
    
    def on_closing(self):
        """Xử lý khi đóng cửa sổ"""
        # Kiểm tra xem có đang tải lên không
        if self.is_uploading:
            if messagebox.askyesno("Xác nhận thoát", "Đang tải lên video. Bạn có chắc muốn thoát không?"):
                self.cleanup_and_exit()
            else:
                return
        elif self.auto_upload_active:
            if messagebox.askyesno("Xác nhận thoát", "Chế độ tự động đang hoạt động. Bạn có chắc muốn thoát không?"):
                self.cleanup_and_exit()
            else:
                return
        else:
            self.cleanup_and_exit()
    
    def cleanup_and_exit(self):
        """Dọn dẹp tài nguyên và thoát"""
        # Dừng tự động tải lên
        if self.auto_upload_active:
            if self.auto_uploader:
                self.auto_uploader.stop()
            if self.bulk_uploader:
                self.bulk_uploader.stop()
        
        # Dừng phân tích video
        if self.video_analyzer:
            self.video_analyzer.stop_async_analysis()
        
        # Ngắt kết nối Telegram
        if self.telegram_api:
            self.telegram_api.disconnect()
        
        # Lưu cấu hình cuối cùng
        with open('config.ini', 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
        
        # Đóng cửa sổ
        self.root.destroy()

def config_main():
    """Chạy ứng dụng ở chế độ cấu hình"""
    root = tk.Tk()
    root.title("Telegram Uploader Config")
    root.geometry("500x400")
    
    # Hiển thị cửa sổ cấu hình
    app = TelegramUploaderApp(root)
    app.notebook.select(2)  # Chuyển đến tab Cài đặt
    
    # Ẩn các tab khác
    app.notebook.tab(0, state="hidden")  # Ẩn tab Tải lên
    app.notebook.tab(1, state="hidden")  # Ẩn tab Tự động
    
    root.mainloop()

def main():
    """Hàm chính để chạy ứng dụng"""
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) > 1 and sys.argv[1] == "--config":
        config_main()
        return
    
    # Chạy ứng dụng chính
    root = tk.Tk()
    app = TelegramUploaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()