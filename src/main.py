"""
Telegram Video Uploader
======================

Ứng dụng tự động tải video lên Telegram với các tính năng tiên tiến.
"""
import os
import sys
import logging
import tkinter as tk
from tkinter import messagebox
import traceback

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

# Import lớp ứng dụng chính
from app import TelegramUploaderApp
# Áp dụng patches cho telethon integration
from utils.telethon_patch import apply_patches
apply_patches()
def main():
    """Hàm main để khởi chạy ứng dụng"""
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