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

# Áp dụng patches cho telethon integration
from utils.telethon_patch import apply_patches
apply_patches()

def main():
    """Hàm main để khởi chạy ứng dụng"""
    logger.info("Khởi động ứng dụng Telegram Video Uploader")
    
    # Import sau khi patch đã được áp dụng
    from app import USE_QT_UI, run_qt_ui, TelegramUploaderApp
    
    if USE_QT_UI:
        # Cố gắng sử dụng Qt UI
        try:
            # Chạy Qt UI
            result = run_qt_ui()
            
            # Nếu khởi động Qt UI thành công, kết thúc ở đây
            if result is not None:
                return result
            
            # Nếu thất bại, chuyển sang Tkinter
            logger.warning("Không thể khởi động Qt UI. Chuyển sang Tkinter.")
        except Exception as e:
            # Log lỗi
            logger.error(f"Lỗi khởi tạo giao diện Qt: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Tiếp tục chuyển sang Tkinter
            logger.info("Chuyển sang sử dụng giao diện Tkinter")
    
    # Tkinter UI (dùng khi Qt không hoạt động hoặc USE_QT_UI = False)
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