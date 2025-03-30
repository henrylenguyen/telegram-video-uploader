"""
Module tạo và quản lý tab nhật ký.
"""
import tkinter as tk
from tkinter import ttk, filedialog
import logging

logger = logging.getLogger("LogTab")

def create_log_tab(app, parent):
    """
    Tạo giao diện cho tab nhật ký
    
    Args:
        app: Đối tượng TelegramUploaderApp
        parent: Frame cha
    """
    # Tiêu đề
    ttk.Label(
        parent, 
        text="Nhật ký hoạt động ứng dụng", 
        style="Heading.TLabel"
    ).pack(pady=10)
    
    # Frame chính chứa log (sử dụng fill=tk.BOTH, expand=True để lấp đầy không gian)
    log_frame = ttk.Frame(parent)
    log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Tạo Text widget và thanh cuộn
    app.log_text = tk.Text(log_frame, wrap=tk.WORD, font=("Arial", 10))
    log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=app.log_text.yview)
    app.log_text.configure(yscrollcommand=log_scrollbar.set)
    
    # Sắp xếp
    log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    app.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Đặt trạng thái chỉ đọc
    app.log_text.config(state=tk.DISABLED)
    
    # Frame nút điều khiển
    control_frame = ttk.Frame(parent)
    control_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Nút lưu log
    save_btn = ttk.Button(
        control_frame, 
        text="Lưu nhật ký", 
        command=lambda: save_log(app)
    )
    save_btn.pack(side=tk.RIGHT, padx=5)
    
    # Nút xóa log
    clear_btn = ttk.Button(
        control_frame, 
        text="Xóa nhật ký", 
        command=lambda: clear_log(app)
    )
    clear_btn.pack(side=tk.RIGHT, padx=5)
    
    # Khởi tạo hook cho logger
    setup_logger_hook(app)

def setup_logger_hook(app):
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
    log_handler = LogHandler(app.log_text)
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    log_handler.setLevel(logging.INFO)
    
    # Thêm handler vào root logger
    logging.getLogger().addHandler(log_handler)

def clear_log(app):
    """Xóa nội dung nhật ký"""
    app.log_text.config(state=tk.NORMAL)
    app.log_text.delete(1.0, tk.END)
    app.log_text.config(state=tk.DISABLED)
    
    # Thông báo
    logger.info("Đã xóa nhật ký")

def save_log(app):
    """Lưu nội dung nhật ký ra file"""
    from tkinter import filedialog
    import os
    from datetime import datetime
    
    # Mở hộp thoại chọn file
    file_path = filedialog.asksaveasfilename(
        defaultextension=".log",
        filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
        initialfile=f"telegram_uploader_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    
    if file_path:
        try:
            # Lấy nội dung log
            log_content = app.log_text.get(1.0, tk.END)
            
            # Ghi vào file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
            
            # Thông báo
            logger.info(f"Đã lưu nhật ký vào {file_path}")
        except Exception as e:
            logger.error(f"Lỗi khi lưu nhật ký: {str(e)}")