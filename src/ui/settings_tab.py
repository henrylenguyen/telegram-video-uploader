"""
Module tạo và quản lý tab cài đặt.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging

logger = logging.getLogger("SettingsTab")

def create_settings_tab(app, parent):
    """
    Tạo giao diện cho tab cài đặt
    
    Args:
        app: Đối tượng TelegramUploaderApp
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
    create_bot_settings_tab(app, bot_tab)
    create_telethon_settings_tab(app, telethon_tab)
    create_general_settings_tab(app, general_tab)

def create_bot_settings_tab(app, parent):
    """Tạo giao diện cài đặt Telegram Bot"""
    # Frame thông tin Telegram
    telegram_frame = ttk.LabelFrame(parent, text="Thông tin Telegram Bot")
    telegram_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Bot Token
    ttk.Label(telegram_frame, text="Bot Token:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    app.bot_token_var = tk.StringVar()
    app.bot_token_var.set(app.config['TELEGRAM']['bot_token'])
    
    # Use larger font size instead of height property
    token_entry = tk.Entry(telegram_frame, textvariable=app.bot_token_var, 
                          font=("Arial", 14),  # Larger font makes the entry field taller
                          relief="groove", bg="white", 
                          highlightthickness=1,
                          highlightbackground="#cccccc",
                          width=60)
    token_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=10)  # Use more padding
    
    # Chat ID đích
    ttk.Label(telegram_frame, text="Chat ID:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    
    app.chat_id_var = tk.StringVar()
    app.chat_id_var.set(app.config['TELEGRAM']['chat_id'])
    
    # Use larger font size instead of height property
    chat_id_entry = tk.Entry(telegram_frame, textvariable=app.chat_id_var, 
                            font=("Arial", 14),  # Larger font makes the entry field taller
                            relief="groove", bg="white", 
                            highlightthickness=1,
                            highlightbackground="#cccccc",
                            width=60)
    chat_id_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=10)  # Use more padding
    
    # Frame điều khiển
    control_frame = ttk.Frame(parent)
    control_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Nút kiểm tra kết nối
    test_btn = tk.Button(control_frame, text="Kiểm tra kết nối Telegram", 
                        font=("Arial", 11),
                        relief="raised", bg="#f0f0f0",
                        command=lambda: app.telegram_connector.test_telegram_connection(app))
    test_btn.pack(side=tk.LEFT, padx=5, pady=10)
    
    # Nút lưu cài đặt
    save_btn = tk.Button(control_frame, text="Lưu cài đặt", 
                        font=("Arial", 11),
                        relief="raised", bg="#f0f0f0",
                        command=lambda: app.telegram_connector.save_telegram_settings(app))
    save_btn.pack(side=tk.RIGHT, padx=5, pady=10)
    
    # Thêm thông tin hướng dẫn
    info_frame = ttk.LabelFrame(parent, text="Thông tin bổ sung")
    info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Tạo Text widget để hiển thị thông tin với thanh cuộn
    info_text = tk.Text(info_frame, wrap=tk.WORD, font=("Arial", 10))
    info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=info_text.yview)
    info_text.configure(yscrollcommand=info_scrollbar.set)
    
    # Sắp xếp
    info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Nội dung hướng dẫn
    info_content = (
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
    info_text.insert(tk.END, info_content)
    info_text.config(state=tk.DISABLED)  # Đặt thành chỉ đọc
def create_telethon_settings_tab(app, parent):
    """Tạo giao diện cài đặt Telethon API (cho video lớn)"""
    # Frame thông tin Telethon API
    telethon_frame = ttk.LabelFrame(parent, text="Thông tin Telethon API (cho video lớn)")
    telethon_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Checkbox bật/tắt Telethon
    app.use_telethon_var = tk.BooleanVar()
    app.use_telethon_var.set(app.config.getboolean('TELETHON', 'use_telethon', fallback=False))
    
    use_telethon_cb = ttk.Checkbutton(
        telethon_frame, 
        text="Sử dụng Telethon API cho video lớn hơn 50MB", 
        variable=app.use_telethon_var
    )
    use_telethon_cb.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
    
    # API ID
    ttk.Label(telethon_frame, text="API ID:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    
    app.api_id_var = tk.StringVar()
    app.api_id_var.set(app.config.get('TELETHON', 'api_id', fallback=''))
    
    api_id_entry = ttk.Entry(telethon_frame, textvariable=app.api_id_var, width=30)
    api_id_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
    
    # API Hash
    ttk.Label(telethon_frame, text="API Hash:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
    
    app.api_hash_var = tk.StringVar()
    app.api_hash_var.set(app.config.get('TELETHON', 'api_hash', fallback=''))
    
    api_hash_entry = ttk.Entry(telethon_frame, textvariable=app.api_hash_var, width=60)
    api_hash_entry.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
    
    # Số điện thoại
    ttk.Label(telethon_frame, text="Số điện thoại:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
    
    app.phone_var = tk.StringVar()
    app.phone_var.set(app.config.get('TELETHON', 'phone', fallback=''))
    
    phone_entry = ttk.Entry(telethon_frame, textvariable=app.phone_var, width=30)
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
                         command=lambda: app.telegram_connector.login_telethon(app))
    login_btn.pack(side=tk.LEFT, padx=5, pady=10)
    
    # Nút lưu cài đặt
    save_btn = ttk.Button(control_frame, text="Lưu cài đặt", 
                         command=lambda: app.telegram_connector.save_telethon_settings(app))
    save_btn.pack(side=tk.RIGHT, padx=5, pady=10)
    
    # Thêm thông tin hướng dẫn
    info_frame = ttk.LabelFrame(parent, text="Thông tin về Telethon API")
    info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Tạo Text widget với thanh cuộn
    info_text = tk.Text(info_frame, wrap=tk.WORD, font=("Arial", 10))
    info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=info_text.yview)
    info_text.configure(yscrollcommand=info_scrollbar.set)
    
    # Sắp xếp
    info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Nội dung hướng dẫn
    info_content = (
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
    info_text.insert(tk.END, info_content)
    info_text.config(state=tk.DISABLED)  # Đặt thành chỉ đọc

def create_general_settings_tab(app, parent):
    """Tạo giao diện cài đặt chung"""
    # Frame cài đặt chung
    settings_frame = ttk.LabelFrame(parent, text="Cài đặt chung")
    settings_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Định dạng video
    ttk.Label(settings_frame, text="Định dạng video hỗ trợ:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    app.video_extensions_var = tk.StringVar()
    app.video_extensions_var.set(app.config['SETTINGS']['video_extensions'])
    
    extensions_entry = ttk.Entry(settings_frame, textvariable=app.video_extensions_var, width=60)
    extensions_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
    
    # Thời gian chờ
    ttk.Label(settings_frame, text="Thời gian chờ giữa các lần tải (giây):").grid(
        row=1, column=0, sticky=tk.W, padx=5, pady=5)
    
    app.delay_var = tk.StringVar()
    app.delay_var.set(app.config['SETTINGS']['delay_between_uploads'])
    
    delay_entry = ttk.Entry(settings_frame, textvariable=app.delay_var, width=10)
    delay_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
    
    # Frame điều khiển
    control_frame = ttk.Frame(parent)
    control_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Nút lưu cài đặt
    save_btn = ttk.Button(control_frame, text="Lưu cài đặt", 
                         command=lambda: app.config_manager.save_general_settings(app))
    save_btn.pack(side=tk.RIGHT, padx=5, pady=10)
    
    # Thêm thông tin về các cài đặt
    info_frame = ttk.LabelFrame(parent, text="Mô tả các cài đặt")
    info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Tạo Text widget với thanh cuộn
    info_text = tk.Text(info_frame, wrap=tk.WORD, font=("Arial", 10))
    info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=info_text.yview)
    info_text.configure(yscrollcommand=info_scrollbar.set)
    
    # Sắp xếp
    info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Nội dung mô tả
    info_content = (
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
    info_text.insert(tk.END, info_content)
    info_text.config(state=tk.DISABLED)  # Đặt thành chỉ đọc