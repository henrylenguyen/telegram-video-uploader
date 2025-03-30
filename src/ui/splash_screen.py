"""
Module tạo và hiển thị màn hình chào khi khởi động ứng dụng.
"""
import tkinter as tk
from tkinter import ttk
import os
import logging

logger = logging.getLogger("SplashScreen")

def show_splash_screen(app):
    """
    Hiển thị splash screen khi khởi động ứng dụng
    
    Args:
        app: Đối tượng TelegramUploaderApp
    """
    splash = tk.Toplevel(app.root)
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
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icon.ico')
        if os.path.exists(icon_path):
            # Sử dụng PhotoImage nếu có thể
            logo = tk.PhotoImage(file=icon_path)
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
    setup_statuses = {}
    setup_labels = {}
    
    for i, item in enumerate(setup_items):
        item_frame = ttk.Frame(setup_frame)
        item_frame.pack(fill=tk.X, pady=3)
        
        # Biểu tượng trạng thái (bắt đầu là trống)
        status_var = tk.StringVar(value="⬜")
        setup_statuses[item] = status_var
        status_label = ttk.Label(item_frame, textvariable=status_var, width=3)
        status_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Nội dung mục
        item_label = ttk.Label(item_frame, text=item, style="Splash.TLabel")
        item_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        setup_labels[item] = item_label
    
    # Thanh tiến trình
    splash_progress = ttk.Progressbar(
        main_frame, 
        orient="horizontal", 
        length=400, 
        mode="determinate",
        style="SplashProgress.Horizontal.TProgressbar"
    )
    splash_progress.pack(fill=tk.X, pady=(20, 10))
    splash_progress["maximum"] = 100
    splash_progress["value"] = 0
    
    # Nhãn trạng thái
    splash_status = tk.StringVar(value="Đang khởi động ứng dụng...")
    status_label = ttk.Label(
        main_frame, 
        textvariable=splash_status,
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
    app.root.update()
    
    # Mô phỏng quá trình cài đặt
    simulate_setup(app, splash, setup_items, setup_statuses, splash_progress, splash_status)

def simulate_setup(app, splash, setup_items, setup_statuses, splash_progress, splash_status):
    """
    Mô phỏng quá trình cài đặt và hiển thị trên splash screen
    
    Args:
        app: Đối tượng TelegramUploaderApp
        splash: Cửa sổ splash
        setup_items: Danh sách các mục cài đặt
        setup_statuses: Dict lưu trạng thái các mục
        splash_progress: Thanh tiến trình
        splash_status: Nhãn trạng thái
    """
    total_steps = len(setup_items)
    
    def update_step(step, item):
        # Cập nhật trạng thái mục
        setup_statuses[item].set("✅")
        
        # Cập nhật thanh tiến trình
        progress_value = (step + 1) / total_steps * 100
        splash_progress["value"] = progress_value
        
        # Cập nhật nhãn trạng thái
        if step < total_steps - 1:
            next_item = setup_items[step + 1]
            splash_status.set(f"Đang {next_item.lower()}...")
        else:
            splash_status.set("Đã sẵn sàng khởi động...")
        
        # Cập nhật giao diện
        app.root.update_idletasks()
    
    # Mô phỏng các bước cài đặt
    for i, item in enumerate(setup_items):
        # Đặt nhãn trạng thái
        splash_status.set(f"Đang {item.lower()}...")
        app.root.update_idletasks()
        
        # Mô phỏng thời gian xử lý
        delay = 300  # ms
        app.root.after(delay, lambda s=i, it=item: update_step(s, it))
        app.root.after(delay + 50)  # Chờ một chút để hiệu ứng mượt hơn
    
    # Sau khi hoàn tất tất cả các bước, đóng splash screen
    app.root.after(1500, splash.destroy)