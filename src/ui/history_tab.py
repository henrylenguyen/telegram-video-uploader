"""
Module tạo và quản lý tab lịch sử.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime

logger = logging.getLogger("HistoryTab")

def create_history_tab(app, parent):
    """
    Tạo giao diện cho tab lịch sử
    
    Args:
        app: Đối tượng TelegramUploaderApp
        parent: Frame cha
    """
    # Tiêu đề
    ttk.Label(
        parent, 
        text="Lịch sử tải lên", 
        style="Heading.TLabel"
    ).pack(pady=10)
    
    # Giới thiệu
    ttk.Label(
        parent, 
        text="Quản lý và xem thông tin về các video đã tải lên trước đó"
    ).pack(pady=5)
    
    # Frame điều khiển
    control_frame = ttk.Frame(parent)
    control_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Hiển thị số lượng video đã tải lên
    uploads = app.upload_history.get_all_uploads()
    upload_count = len(uploads)
    
    app.history_stats_label = ttk.Label(
        control_frame, 
        text=f"Tổng số video đã tải lên: {upload_count}"
    )
    app.history_stats_label.pack(side=tk.LEFT, padx=5)
    
    # Các nút điều khiển
    view_btn = tk.Button(
        control_frame, 
        text="Xem lịch sử chi tiết", 
        font=("Arial", 11),
        height=2,  # Chiều cao ~40px
        relief="raised", bg="#f0f0f0",
        command=lambda: show_history_dialog(app)
    )
    view_btn.pack(side=tk.RIGHT, padx=5)
    
    clear_btn = tk.Button(
        control_frame, 
        text="Xóa lịch sử", 
        font=("Arial", 11),
        height=2,  # Chiều cao ~40px
        relief="raised", bg="#e74c3c",
        fg="white",
        command=lambda: confirm_clear_history(app)
    )
    clear_btn.pack(side=tk.RIGHT, padx=5)
    
    # Frame thông tin
    info_frame = ttk.LabelFrame(parent, text="Thông tin về lịch sử tải lên")
    info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Tạo frame cho text có thể cuộn
    info_text = tk.Text(info_frame, wrap=tk.WORD, font=("Arial", 10))
    info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=info_text.yview)
    info_text.configure(yscrollcommand=info_scrollbar.set)
    
    # Sắp xếp
    info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Giải thích cách hoạt động
    info_content = (
        "Tính năng lịch sử tải lên giúp bạn theo dõi và quản lý các video đã tải lên trước đó. "
        "Khi tải lên một video, hệ thống sẽ lưu thông tin về video đó, bao gồm hash, tên file, "
        "kích thước và ngày tải lên.\n\n"
        
        "Ứng dụng sẽ tự động kiểm tra các video mới so với lịch sử đã lưu. Nếu phát hiện video "
        "trùng lặp, bạn sẽ được thông báo, giúp tránh tải lên cùng một video nhiều lần.\n\n"
        
        "Tính năng này đặc biệt hữu ích khi bạn làm việc với thư viện video lớn và qua nhiều phiên "
        "làm việc khác nhau. Tất cả dữ liệu lịch sử được lưu trong file JSON, giúp dễ dàng sao lưu "
        "và chuyển đến máy tính khác."
    )
    
    # Chèn văn bản vào widget
    info_text.insert(tk.END, info_content)
    info_text.config(state=tk.DISABLED)  # Đặt thành chỉ đọc
    
    # Khung thống kê
    stats_frame = ttk.LabelFrame(parent, text="Thống kê nhanh")
    stats_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Grid layout cho thống kê
    stats_frame.columnconfigure(0, weight=1)
    stats_frame.columnconfigure(1, weight=1)
    stats_frame.columnconfigure(2, weight=1)
    
    # Thống kê tổng số video
    ttk.Label(stats_frame, text="Tổng số video:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=5)
    app.total_videos_var = tk.StringVar(value=str(upload_count))
    ttk.Label(stats_frame, textvariable=app.total_videos_var, style="Status.TLabel").grid(
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
    app.month_videos_var = tk.StringVar(value=str(this_month_count))
    ttk.Label(stats_frame, textvariable=app.month_videos_var, style="Status.TLabel").grid(
        row=1, column=1, sticky=tk.W, padx=5, pady=5)
    
     # Nút làm mới thống kê
    refresh_stats_btn = tk.Button(
        stats_frame, 
        text="Làm mới thống kê", 
        font=("Arial", 11),
        height=2,  # Chiều cao ~40px
        relief="raised", bg="#f0f0f0",
        command=lambda: refresh_history_stats(app)
    )
    refresh_stats_btn.grid(row=0, column=2, rowspan=2, padx=20, pady=10)

def refresh_history_stats(app):
    """Làm mới thống kê lịch sử"""
    uploads = app.upload_history.get_all_uploads()
    upload_count = len(uploads)
    
    # Cập nhật nhãn và biến
    app.history_stats_label.config(text=f"Tổng số video đã tải lên: {upload_count}")
    app.total_videos_var.set(str(upload_count))
    
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
    
    app.month_videos_var.set(str(this_month_count))

def show_history_dialog(app):
    """Hiển thị dialog xem lịch sử chi tiết"""
    from utils.history_ui import UploadHistoryDialog
    dialog = UploadHistoryDialog(app.root, app.upload_history, app.video_analyzer)
    # Sau khi đóng dialog, làm mới thống kê
    app.root.wait_window(dialog.dialog)
    refresh_history_stats(app)

def confirm_clear_history(app):
    """Xác nhận và xóa toàn bộ lịch sử"""
    if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa toàn bộ lịch sử tải lên?"):
        # Xóa toàn bộ lịch sử
        app.upload_history.clear_history()
        
        # Cập nhật thống kê
        refresh_history_stats(app)
        
        # Thông báo
        messagebox.showinfo("Thành công", "Đã xóa toàn bộ lịch sử tải lên")