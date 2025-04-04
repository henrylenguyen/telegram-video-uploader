"""
Module tạo và quản lý tab tự động tải lên.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import os

logger = logging.getLogger("AutoTab")

def create_auto_tab(app, parent):
    """
    Tạo giao diện cho tab tự động
    
    Args:
        app: Đối tượng TelegramUploaderApp
        parent: Frame cha
    """
    # Frame chọn thư mục giám sát
    folder_frame = ttk.LabelFrame(parent, text="Thư mục giám sát tự động")
    folder_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Đường dẫn thư mục
    app.auto_folder_path = tk.StringVar()
    app.auto_folder_path.set(app.config['SETTINGS']['video_folder'])
    
    # Ô input và nút duyệt cải thiện layout với chiều cao 40px
    input_frame = ttk.Frame(folder_frame)
    input_frame.pack(fill=tk.X, padx=5, pady=5)
    
    folder_entry = tk.Entry(input_frame, textvariable=app.auto_folder_path, 
                          font=("Arial", 11), 
                          relief="groove", bg="white",
                          highlightthickness=1,
                          highlightbackground="#cccccc")
    folder_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
    folder_entry.configure(height=2)  # Chiều cao ~40px
    
    # Nút "Duyệt..." với kích thước đủ
    from ui.main_tab import browse_folder  # Import hàm để sử dụng
    browse_btn = tk.Button(input_frame, text="Duyệt...", 
                          font=("Arial", 11), width=10,
                          height=2,  # Chiều cao ~40px
                          relief="raised", bg="#f0f0f0",
                          command=lambda: browse_folder(app, auto=True))
    browse_btn.pack(side=tk.RIGHT, padx=5, pady=5)
    
    # Thêm khung chọn chế độ tự động
    mode_frame = ttk.LabelFrame(parent, text="Chế độ tự động")
    mode_frame.pack(fill=tk.X, padx=10, pady=10)

    # Radio buttons cho các chế độ
    app.auto_mode_var = tk.StringVar(value="watch")
    watch_radio = ttk.Radiobutton(
        mode_frame, 
        text="Theo dõi thư mục (tải lên video mới khi phát hiện)",
        variable=app.auto_mode_var,
        value="watch"
    )
    watch_radio.pack(anchor=tk.W, padx=5, pady=3)

    bulk_radio = ttk.Radiobutton(
        mode_frame, 
        text="Tải lên hàng loạt (quét và tải tất cả video trong thư mục)",
        variable=app.auto_mode_var,
        value="bulk"
    )
    bulk_radio.pack(anchor=tk.W, padx=5, pady=3)
    
    # Frame cài đặt tự động
    auto_settings_frame = ttk.LabelFrame(parent, text="Cài đặt tự động")
    auto_settings_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Thời gian kiểm tra
    ttk.Label(auto_settings_frame, text="Kiểm tra thư mục mỗi (giây):").grid(
        row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    app.check_interval_var = tk.StringVar()
    app.check_interval_var.set(app.config['SETTINGS']['auto_check_interval'])
    
    check_interval_entry = ttk.Entry(auto_settings_frame, textvariable=app.check_interval_var, width=10)
    check_interval_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
    
    # Checkbox kiểm tra trùng lặp
    app.auto_check_duplicates_var = tk.BooleanVar()
    app.auto_check_duplicates_var.set(app.config['SETTINGS'].getboolean('check_duplicates', True))
    
    check_duplicates_cb = ttk.Checkbutton(
        auto_settings_frame, 
        text="Tự động loại bỏ video trùng lặp", 
        variable=app.auto_check_duplicates_var
    )
    check_duplicates_cb.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
    
    # Checkbox kiểm tra với lịch sử
    app.auto_check_history_var = tk.BooleanVar()
    app.auto_check_history_var.set(True)
    
    check_history_cb = ttk.Checkbutton(
        auto_settings_frame, 
        text="Kiểm tra với lịch sử đã tải lên", 
        variable=app.auto_check_history_var
    )
    check_history_cb.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
    
    # Checkbox lưu log
    app.auto_log_var = tk.BooleanVar()
    app.auto_log_var.set(True)
    
    auto_log_cb = ttk.Checkbutton(
        auto_settings_frame, 
        text="Ghi nhật ký hoạt động tự động", 
        variable=app.auto_log_var
    )
    auto_log_cb.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
    
    # Frame trạng thái
    status_frame = ttk.LabelFrame(parent, text="Trạng thái giám sát")
    status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Frame chứa log và thanh cuộn
    log_container = ttk.Frame(status_frame)
    log_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Tạo Text widget để hiển thị log hoạt động tự động
    app.auto_log_text = tk.Text(log_container, wrap=tk.WORD, width=80, height=15, font=("Arial", 10))
    
    # QUAN TRỌNG: Thêm thanh cuộn và thiết lập đúng cách
    auto_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=app.auto_log_text.yview)
    app.auto_log_text.config(yscrollcommand=auto_scrollbar.set)
    
    # Vị trí đúng: auto_log_text bên trái, scrollbar bên phải
    auto_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    app.auto_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Frame điều khiển
    control_frame = ttk.Frame(parent)
    control_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Nhãn trạng thái
    app.auto_status_var = tk.StringVar()
    app.auto_status_var.set("Tự động tải lên: Tắt")
    
    auto_status_label = ttk.Label(
        control_frame, 
        textvariable=app.auto_status_var,
        style="Status.TLabel"
    )
    auto_status_label.pack(pady=5)
    
    # Frame nút
    auto_btn_frame = ttk.Frame(control_frame)
    auto_btn_frame.pack(fill=tk.X, pady=10)
    
    # Nút bắt đầu tự động - kích thước đủ cho chữ
    app.start_auto_btn = ttk.Button(
        auto_btn_frame, 
        text="Bắt đầu tự động", 
        command=lambda: app.auto_uploader_manager.start_auto_upload(app)
    )
    app.start_auto_btn.pack(side=tk.LEFT, padx=5)
    
    # Nút dừng tự động
    app.stop_auto_btn = ttk.Button(
        auto_btn_frame, 
        text="Dừng tự động", 
        command=lambda: app.auto_uploader_manager.stop_auto_upload(app),
        state=tk.DISABLED
    )
    app.stop_auto_btn.pack(side=tk.LEFT, padx=5)
    
    # Nút tải lên hàng loạt
    app.bulk_upload_btn = ttk.Button(
        auto_btn_frame, 
        text="Tải lên tất cả", 
        command=lambda: app.auto_uploader_manager.start_bulk_upload(app)
    )
    app.bulk_upload_btn.pack(side=tk.RIGHT, padx=5)

def add_auto_log(app, message):
    """
    Thêm thông báo vào nhật ký tự động
    
    Args:
        app: Đối tượng TelegramUploaderApp
        message (str): Thông báo cần thêm
    """
    if not app.auto_log_var.get():
        return
        
    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    # Thêm vào Text widget
    app.auto_log_text.config(state=tk.NORMAL)
    app.auto_log_text.insert(tk.END, log_entry)
    app.auto_log_text.see(tk.END)  # Cuộn xuống dòng cuối
    app.auto_log_text.config(state=tk.DISABLED)
    
    # Thêm vào log chung
    logger.info(f"[AUTO] {message}")