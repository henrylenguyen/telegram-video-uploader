"""
Main entry point for Telegram Video Uploader application
"""
import sys
import os
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("telegram_uploader.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Main")

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to apply Telethon patches if needed
try:
    from utils.telethon_patch import apply_patches
    apply_patches()
    logger.info("Telethon patches applied")
except ImportError:
    logger.info("Telethon patch module not found, skipping")
except Exception as e:
    logger.error(f"Error applying Telethon patches: {str(e)}")

def main():
    """Main function to start the application"""
    logger.info("Starting Telegram Video Uploader")
    
    # Import application class
    from app import TelegramUploaderApp
    
    try:
        # Tạo ứng dụng PyQt6 (đã cập nhật từ PyQt5)
        from PyQt6 import QtWidgets
        
        # Tạo đối tượng ứng dụng
        app = TelegramUploaderApp()
        
        # Chạy ứng dụng
        return app.run()
        
    except Exception as e:
        # Ghi log lỗi
        logger.error(f"Lỗi không khắc phục được: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Hiển thị thông báo lỗi
        try:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                None,
                "Lỗi nghiêm trọng",
                f"Đã xảy ra lỗi không khắc phục được:\n\n{str(e)}\n\nVui lòng khởi động lại ứng dụng."
            )
        except:
            pass
            
        # Thoát với mã lỗi
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())