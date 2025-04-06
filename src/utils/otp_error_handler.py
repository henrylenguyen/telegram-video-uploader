"""
Module xử lý các lỗi liên quan đến OTP từ Telegram API
"""
import re
import tkinter as tk
import logging

logger = logging.getLogger("OTPErrorHandler")

def format_wait_time(seconds):
    """
    Định dạng thời gian chờ từ giây sang định dạng giờ:phút:giây
    
    Args:
        seconds (int): Số giây cần đợi
        
    Returns:
        str: Chuỗi thời gian định dạng giờ:phút:giây
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    time_parts = []
    if hours > 0:
        time_parts.append(f"{hours} giờ")
    if minutes > 0:
        time_parts.append(f"{minutes} phút")
    if seconds > 0 or not time_parts:  # Luôn hiển thị giây nếu không có giờ/phút
        time_parts.append(f"{seconds} giây")
    
    return " ".join(time_parts)

def handle_flood_wait_error(error_message, parent_widget):
    """
    Xử lý lỗi FloodWaitError và hiển thị thông báo thân thiện
    
    Args:
        error_message (str): Nội dung lỗi từ Telegram
        parent_widget: Widget cha để hiển thị dialog
        
    Returns:
        tk.Toplevel: Đối tượng dialog để tham chiếu sau này
    """
    logger.info(f"Xử lý lỗi FloodWaitError: {error_message}")
    
    # Trích xuất thời gian chờ từ thông báo lỗi
    wait_seconds = 0
    match = re.search(r'A wait of (\d+) seconds', error_message)
    if match:
        wait_seconds = int(match.group(1))
        logger.info(f"Thời gian chờ được trích xuất: {wait_seconds} giây")
    else:
        # Nếu không tìm thấy, thử mẫu khác
        match = re.search(r'(\d+)', error_message)
        if match:
            wait_seconds = int(match.group(1))
            logger.info(f"Thời gian chờ được trích xuất (mẫu phụ): {wait_seconds} giây")
        else:
            wait_seconds = 300  # Mặc định 5 phút nếu không tìm thấy
            logger.warning(f"Không thể trích xuất thời gian chờ, sử dụng mặc định: {wait_seconds} giây")
    
    # Định dạng thời gian chờ
    formatted_time = format_wait_time(wait_seconds)
    
    # Tạo thông báo chi tiết
    message = (
        f"⏰ Đã đạt giới hạn yêu cầu mã OTP từ Telegram\n\n"
        f"Vui lòng đợi {formatted_time} trước khi thử lại.\n\n"
        f"Nguyên nhân có thể là do:\n"
        f"• Bạn đã yêu cầu mã OTP quá nhiều lần trong thời gian ngắn\n"
        f"• Tài khoản đang bị giới hạn tạm thời vì lý do bảo mật\n\n"
        f"Bạn có thể đóng cửa sổ này và thử lại sau."
    )
    
    try:
        # Hiển thị dialog tùy chỉnh thay vì messagebox tiêu chuẩn
        dialog = tk.Toplevel(parent_widget)
        dialog.title("Giới hạn yêu cầu OTP")
        dialog.transient(parent_widget)
        dialog.grab_set()
        
        # Đặt kích thước và vị trí
        window_width = 500
        window_height = 300
        
        # Đặt vị trí giữa màn hình
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        dialog.resizable(False, False)
        
        # Thiết lập style
        dialog.configure(bg="#f5f5f5")
        
        # Icon cảnh báo
        warning_label = tk.Label(dialog, text="⚠️", font=("Arial", 48), bg="#f5f5f5")
        warning_label.pack(pady=(15, 5))
        
        # Tiêu đề
        title_label = tk.Label(
            dialog, 
            text="Vui lòng đợi trước khi thử lại", 
            font=("Arial", 14, "bold"),
            bg="#f5f5f5"
        )
        title_label.pack(pady=(0, 10))
        
        # Nội dung thông báo
        message_frame = tk.Frame(dialog, bg="#f5f5f5", padx=20)
        message_frame.pack(fill=tk.BOTH, expand=True)
        
        message_label = tk.Label(
            message_frame, 
            text=message,
            justify=tk.LEFT,
            font=("Arial", 11),
            wraplength=450,
            bg="#f5f5f5"
        )
        message_label.pack(fill=tk.BOTH, expand=True)
        
        # Nút đóng
        btn_frame = tk.Frame(dialog, bg="#f5f5f5")
        btn_frame.pack(pady=15)
        
        close_btn = tk.Button(
            btn_frame, 
            text="Đã hiểu",
            font=("Arial", 11),
            width=15,
            height=2,
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            command=dialog.destroy
        )
        close_btn.pack()
        
        # Tạo đồng hồ đếm ngược nếu thời gian chờ < 1 giờ
        if wait_seconds < 3600:
            countdown_var = tk.StringVar()
            countdown_label = tk.Label(
                dialog,
                textvariable=countdown_var,
                font=("Arial", 10),
                bg="#f5f5f5"
            )
            countdown_label.pack(pady=(0, 10))
            
            # Hàm cập nhật đồng hồ đếm ngược
            remaining_seconds = min(wait_seconds, 3600)  # Giới hạn tối đa 1 giờ
            
            def update_countdown():
                nonlocal remaining_seconds
                if remaining_seconds > 0 and dialog.winfo_exists():
                    remaining_seconds -= 1
                    countdown_var.set(f"Còn lại: {format_wait_time(remaining_seconds)}")
                    dialog.after(1000, update_countdown)
            
            # Bắt đầu đếm ngược
            countdown_var.set(f"Còn lại: {format_wait_time(remaining_seconds)}")
            dialog.after(1000, update_countdown)
        
        return dialog
        
    except Exception as e:
        # Fallback nếu không thể tạo dialog tùy chỉnh
        logger.error(f"Lỗi khi tạo dialog: {str(e)}")
        import tkinter.messagebox as messagebox
        messagebox.showwarning(
            "Giới hạn yêu cầu OTP",
            f"Đã đạt giới hạn lấy OTP trong thời gian này, xin vui lòng thử lại sau: {formatted_time}"
        )
        return None