"""
Module for settings tab UI
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def create_settings_tab(app, parent):
    """Tạo giao diện tab Cài đặt"""
    # Tạo frame chính để chứa nội dung
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Tạo các frame nội dung cho từng tab
    bot_frame = ttk.Frame(main_frame)
    telethon_frame = ttk.Frame(main_frame)
    general_frame = ttk.Frame(main_frame)
    
    # Tạo các nút tab tùy chỉnh
    tab_frame = ttk.Frame(main_frame)
    tab_frame.pack(fill=tk.X, padx=0, pady=0)
    
    # Tạo 3 nút tab
    bot_tab = tk.Button(tab_frame, text="Telegram Bot", height=2, relief="ridge",
                      font=("Arial", 11), command=lambda: show_tab(0))
    bot_tab.pack(side=tk.LEFT, fill=tk.Y, padx=1)
    
    telethon_tab = tk.Button(tab_frame, text="Telethon API (Video lớn)", height=2, relief="ridge",
                           font=("Arial", 11), command=lambda: show_tab(1))
    telethon_tab.pack(side=tk.LEFT, fill=tk.Y, padx=1)
    
    general_tab = tk.Button(tab_frame, text="Cài đặt chung", height=2, relief="ridge",
                          font=("Arial", 11), command=lambda: show_tab(2))
    general_tab.pack(side=tk.LEFT, fill=tk.Y, padx=1)
    
    tab_buttons = [bot_tab, telethon_tab, general_tab]
    tab_frames = [bot_frame, telethon_frame, general_frame]
    
    # Hàm hiển thị tab
    def show_tab(index):
        # Hiển thị frame đã chọn, ẩn các frame khác
        for i, frame in enumerate(tab_frames):
            if i == index:
                frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            else:
                frame.pack_forget()
        
        # Cập nhật style cho các nút
        for i, btn in enumerate(tab_buttons):
            if i == index:
                btn.config(bg="#4a7ebb", fg="white", relief="sunken")
            else:
                btn.config(bg="#f0f0f0", fg="black", relief="ridge")
    
    # Điền nội dung cho các tab
    create_bot_settings_tab(app, bot_frame)
    create_telethon_settings_tab(app, telethon_frame)
    create_general_settings_tab(app, general_frame)
    
    # Hiển thị tab đầu tiên mặc định
    show_tab(0)
    
    # Lưu danh sách tab và các hàm để có thể truy cập sau này
    app.tab_buttons = tab_buttons
    app.tab_frames = tab_frames
    app.show_tab = show_tab
    
    return main_frame

def create_bot_settings_tab(app, parent):
    """Tạo giao diện cài đặt Telegram Bot"""
    # Frame thông tin Telegram
    telegram_frame = ttk.LabelFrame(parent, text="Thông tin Telegram Bot")
    telegram_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Kiểm tra nếu đã có cấu hình
    has_bot_config = app.config['TELEGRAM']['bot_token'] and app.config['TELEGRAM']['chat_id']
    
    # Grid layout
    telegram_frame.columnconfigure(0, weight=1)
    telegram_frame.columnconfigure(1, weight=10)
    
    # Bot Token
    ttk.Label(telegram_frame, text="Bot Token:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=15)
    
    app.bot_token_var = tk.StringVar()
    app.bot_token_var.set(app.config['TELEGRAM']['bot_token'])
    
    # Entry với chiều cao cố định
    bot_token_frame = ttk.Frame(telegram_frame, height=40)
    bot_token_frame.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=10)
    bot_token_frame.pack_propagate(False)
    
    token_entry = ttk.Entry(
        bot_token_frame, 
        textvariable=app.bot_token_var, 
        state="readonly" if has_bot_config else "normal"
    )
    token_entry.pack(fill=tk.BOTH, expand=True)
    
    # Chat ID
    ttk.Label(telegram_frame, text="Chat ID:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=15)
    
    app.chat_id_var = tk.StringVar()
    app.chat_id_var.set(app.config['TELEGRAM']['chat_id'])
    
    # Entry với chiều cao cố định
    chat_id_frame = ttk.Frame(telegram_frame, height=40)
    chat_id_frame.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=10)
    chat_id_frame.pack_propagate(False)
    
    chat_id_entry = ttk.Entry(
        chat_id_frame,
        textvariable=app.chat_id_var,
        state="readonly" if has_bot_config else "normal"
    )
    chat_id_entry.pack(fill=tk.BOTH, expand=True)
    
    # Nút chỉnh sửa cấu hình - chỉ hiển thị nếu đã có cấu hình
    if has_bot_config:
        edit_frame = ttk.Frame(telegram_frame)
        edit_frame.grid(row=2, column=0, columnspan=2, sticky=tk.E, padx=5, pady=10)
        
        edit_btn = ttk.Button(
            edit_frame,
            text="Chỉnh sửa cấu hình",
            command=lambda: edit_telegram_config(app)
        )
        edit_btn.pack(side=tk.RIGHT)
    
    # Frame điều khiển - chỉ hiển thị nếu chưa có cấu hình
    if not has_bot_config:
        control_frame = ttk.Frame(telegram_frame)
        control_frame.grid(row=3, column=0, columnspan=2, sticky=tk.E+tk.W, padx=5, pady=10)
        
        # Nút kiểm tra kết nối
        test_btn = ttk.Button(
            control_frame,
            text="Kiểm tra kết nối Telegram",
            command=lambda: app.telegram_connector.test_telegram_connection(app)
        )
        test_btn.pack(side=tk.LEFT, padx=5)
        
        # Nút lưu cài đặt
        save_btn = ttk.Button(
            control_frame,
            text="Lưu cài đặt",
            command=lambda: app.telegram_connector.save_telegram_settings(app)
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
    
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
    
    # Check if Telethon is configured
    has_telethon_config = (
        app.config['TELETHON']['api_id'] and 
        app.config['TELETHON']['api_hash'] and 
        app.config['TELETHON']['phone']
    )
    
    # Grid layout
    telethon_frame.columnconfigure(0, weight=1)
    telethon_frame.columnconfigure(1, weight=10)
    
    # Checkbox bật/tắt Telethon - luôn tự động kích hoạt nếu có cấu hình
    app.use_telethon_var = tk.BooleanVar()
    app.use_telethon_var.set(True if has_telethon_config else False)
    
    use_telethon_cb = ttk.Checkbutton(
        telethon_frame, 
        text="Sử dụng Telethon API cho video lớn hơn 50MB", 
        variable=app.use_telethon_var,
        state="disabled" if not has_telethon_config else "normal"
    )
    use_telethon_cb.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
    
    # API ID
    ttk.Label(telethon_frame, text="API ID:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=15)
    
    app.api_id_var = tk.StringVar()
    app.api_id_var.set(app.config.get('TELETHON', 'api_id', fallback=''))
    
    # API ID Entry với chiều cao cố định
    api_id_frame = ttk.Frame(telethon_frame, height=40)
    api_id_frame.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=10)
    api_id_frame.pack_propagate(False)
    
    api_id_entry = ttk.Entry(
        api_id_frame,
        textvariable=app.api_id_var,
        state="readonly" if has_telethon_config else "normal"
    )
    api_id_entry.pack(fill=tk.BOTH, expand=True)
    
    # API Hash
    ttk.Label(telethon_frame, text="API Hash:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=15)
    
    app.api_hash_var = tk.StringVar()
    app.api_hash_var.set(app.config.get('TELETHON', 'api_hash', fallback=''))
    
    # API Hash Entry với chiều cao cố định
    api_hash_frame = ttk.Frame(telethon_frame, height=40)
    api_hash_frame.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=10)
    api_hash_frame.pack_propagate(False)
    
    api_hash_entry = ttk.Entry(
        api_hash_frame,
        textvariable=app.api_hash_var,
        state="readonly" if has_telethon_config else "normal"
    )
    api_hash_entry.pack(fill=tk.BOTH, expand=True)
    
    # Số điện thoại
    ttk.Label(telethon_frame, text="Số điện thoại:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=15)
    
    app.phone_var = tk.StringVar()
    app.phone_var.set(app.config.get('TELETHON', 'phone', fallback=''))
    
    # Số điện thoại Entry với chiều cao cố định
    phone_frame = ttk.Frame(telethon_frame, height=40)
    phone_frame.grid(row=3, column=1, sticky=tk.W+tk.E, padx=5, pady=10)
    phone_frame.pack_propagate(False)
    
    phone_entry = ttk.Entry(
        phone_frame,
        textvariable=app.phone_var,
        state="readonly" if has_telethon_config else "normal"
    )
    phone_entry.pack(fill=tk.BOTH, expand=True)
    
    # Ghi chú số điện thoại
    ttk.Label(
        telethon_frame, 
        text="(Định dạng: +84123456789)",
        foreground="gray"
    ).grid(row=4, column=1, sticky=tk.W, padx=5)
    
    # Trạng thái đăng nhập Telethon
    login_status_frame = ttk.Frame(telethon_frame)
    login_status_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
    
    # Lấy trạng thái từ log hoặc trạng thái hiện tại
    is_telethon_logged_in = True
    try:
        with open('logs/app.log', 'r') as log_file:
            logs = log_file.read()
            is_telethon_logged_in = "Không thể đăng nhập tự động" not in logs
    except:
        pass
    
    # Hiển thị trạng thái đăng nhập
    status_label = ttk.Label(
        login_status_frame,
        text="Trạng thái Telethon:",
        font=("Arial", 10, "bold")
    )
    status_label.pack(side=tk.LEFT, padx=5)
    
    status_text = ttk.Label(
        login_status_frame,
        text="✅ Đã đăng nhập" if is_telethon_logged_in else "❌ Chưa đăng nhập",
        foreground="green" if is_telethon_logged_in else "red",
        font=("Arial", 10)
    )
    status_text.pack(side=tk.LEFT, padx=5)
    
    # Nút đăng nhập lại Telethon (luôn hiện, bất kể config)
    login_btn = ttk.Button(
        login_status_frame, 
        text="Đăng nhập lại Telethon", 
        command=lambda: app.telegram_connector.login_telethon(app)
    )
    login_btn.pack(side=tk.RIGHT, padx=5)
    
    # Nút chỉnh sửa cấu hình - chỉ hiển thị nếu đã có cấu hình
    if has_telethon_config:
        edit_frame = ttk.Frame(telethon_frame)
        edit_frame.grid(row=6, column=0, columnspan=2, sticky=tk.E, padx=5, pady=10)
        
        edit_btn = ttk.Button(
            edit_frame, 
            text="Chỉnh sửa cấu hình", 
            command=lambda: edit_telethon_config(app)
        )
        edit_btn.pack(side=tk.RIGHT)
    
    # Frame điều khiển - chỉ hiển thị nếu chưa có cấu hình
    if not has_telethon_config:
        control_frame = ttk.Frame(telethon_frame)
        control_frame.grid(row=7, column=0, columnspan=2, sticky=tk.E+tk.W, padx=5, pady=10)
        
        # Nút lưu cài đặt
        save_btn = ttk.Button(
            control_frame, 
            text="Lưu cài đặt", 
            command=lambda: app.telegram_connector.save_telethon_settings(app)
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
    
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
        "4. Nhấn nút 'Đăng nhập lại Telethon' và nhập mã xác thực được gửi đến điện thoại/Telegram của bạn\n\n"
        "Lưu ý:\n"
        "- Khi bật tính năng này, video lớn hơn 50MB sẽ được tải lên qua tài khoản người dùng của bạn thay vì bot\n"
        "- Telethon sẽ tạo một phiên đăng nhập lưu trên máy tính, bạn không cần đăng nhập lại sau mỗi lần khởi động ứng dụng\n"
        "- Khuyên dùng cho các video có kích thước rất lớn, vì tốc độ tải lên qua Telethon thường nhanh hơn\n"
        "- Khi sử dụng Telethon, video sẽ không bị chia nhỏ, giúp dễ dàng xem và quản lý hơn"
    )
    
    # Chèn văn bản vào widget
    info_text.insert(tk.END, info_content)
    info_text.config(state=tk.DISABLED)  # Đặt thành chỉ đọc
    
    # Lưu cài đặt khi checkbox thay đổi
    app.use_telethon_var.trace_add("write", lambda *args: save_telethon_checkbox(app))

def create_general_settings_tab(app, parent):
    """Tạo giao diện cài đặt chung"""
    # Frame thư mục video
    folder_frame = ttk.LabelFrame(parent, text="Thư mục video")
    folder_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Thư mục video
    ttk.Label(folder_frame, text="Thư mục video:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    app.video_folder_var = tk.StringVar()
    app.video_folder_var.set(app.config['SETTINGS']['video_folder'])
    
    folder_entry = ttk.Entry(folder_frame, textvariable=app.video_folder_var, width=60)
    folder_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
    
    browse_btn = ttk.Button(
        folder_frame, 
        text="Chọn...", 
        command=lambda: browse_folder(app)
    )
    browse_btn.grid(row=0, column=2, padx=5, pady=5)
    
    # Frame cài đặt khác
    settings_frame = ttk.LabelFrame(parent, text="Cài đặt khác")
    settings_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Định dạng video hỗ trợ
    ttk.Label(settings_frame, text="Định dạng video hỗ trợ:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    app.video_extensions_var = tk.StringVar()
    app.video_extensions_var.set(app.config['SETTINGS']['video_extensions'])
    
    extensions_entry = ttk.Entry(settings_frame, textvariable=app.video_extensions_var, width=40)
    extensions_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
    
    # Thời gian chờ giữa các lần tải lên
    ttk.Label(settings_frame, text="Thời gian chờ giữa các lần tải lên (giây):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    
    app.delay_var = tk.StringVar()
    app.delay_var.set(app.config['SETTINGS']['delay_between_uploads'])
    
    delay_spinbox = ttk.Spinbox(settings_frame, from_=0, to=60, textvariable=app.delay_var, width=5)
    delay_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
    
    # Checkbox chức năng tự động tìm kiếm
    app.auto_mode_var = tk.BooleanVar()
    app.auto_mode_var.set(app.config.getboolean('SETTINGS', 'auto_mode', fallback=False))
    
    auto_check = ttk.Checkbutton(
        settings_frame, 
        text="Tự động tìm kiếm và tải lên video mới", 
        variable=app.auto_mode_var
    )
    auto_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
    
    # Thời gian kiểm tra tự động
    ttk.Label(settings_frame, text="Thời gian kiểm tra tự động (giây):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
    
    app.auto_check_interval_var = tk.StringVar()
    app.auto_check_interval_var.set(app.config.get('SETTINGS', 'auto_check_interval', fallback='60'))
    
    interval_spinbox = ttk.Spinbox(settings_frame, from_=10, to=3600, textvariable=app.auto_check_interval_var, width=5)
    interval_spinbox.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
    
    # Checkbox kiểm tra trùng lặp
    app.check_duplicates_var = tk.BooleanVar()
    app.check_duplicates_var.set(app.config.getboolean('SETTINGS', 'check_duplicates', fallback=True))
    
    check_dup = ttk.Checkbutton(
        settings_frame, 
        text="Kiểm tra trùng lặp tên file trước khi tải lên", 
        variable=app.check_duplicates_var
    )
    check_dup.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
    
    # Nút lưu cài đặt
    save_btn = ttk.Button(
        parent, 
        text="Lưu cài đặt", 
        command=lambda: save_settings(app)
    )
    save_btn.pack(side=tk.RIGHT, padx=10, pady=10)

def browse_folder(app):
    """Mở hộp thoại chọn thư mục"""
    folder = filedialog.askdirectory()
    if folder:
        app.video_folder_var.set(folder)
        # Cập nhật cả biến thư mục video trên tab chính nếu có
        if hasattr(app, 'main_video_folder_var'):
            app.main_video_folder_var.set(folder)

def edit_telegram_config(app):
    """Open modal dialog to edit Telegram Bot configuration"""
    from ui.edit_config_modal import TelegramEditModal
    TelegramEditModal(app)

def edit_telethon_config(app):
    """Open modal dialog to edit Telethon API configuration"""
    from ui.edit_config_modal import TelethonEditModal
    TelethonEditModal(app)

def save_telethon_checkbox(app):
    """Lưu trạng thái checkbox khi thay đổi"""
    app.config['TELETHON']['use_telethon'] = 'true' if app.use_telethon_var.get() else 'false'
    app.config_manager.save_config(app.config)

def save_settings(app):
    """Lưu cài đặt chung"""
    # Lưu thông tin từ các biến vào config
    app.config['SETTINGS']['video_folder'] = app.video_folder_var.get()
    app.config['SETTINGS']['video_extensions'] = app.video_extensions_var.get()
    app.config['SETTINGS']['delay_between_uploads'] = app.delay_var.get()
    app.config['SETTINGS']['auto_mode'] = 'true' if app.auto_mode_var.get() else 'false'
    app.config['SETTINGS']['auto_check_interval'] = app.auto_check_interval_var.get()
    app.config['SETTINGS']['check_duplicates'] = 'true' if app.check_duplicates_var.get() else 'false'
    
    # Lưu cấu hình
    app.config_manager.save_config(app.config)
    
    # Cập nhật biến thư mục video trên tab chính
    if hasattr(app, 'main_video_folder_var'):
        app.main_video_folder_var.set(app.video_folder_var.get())
    
    # Hiển thị thông báo
    messagebox.showinfo("Thành công", "Đã lưu cài đặt thành công!")