"""
Telegram Video Uploader
======================

Application for automatically uploading videos to Telegram with advanced features.
"""
import os
import sys
import logging
import tkinter as tk
from tkinter import messagebox
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
logger = logging.getLogger("TelegramUploader")

# Apply patches for telethon integration if needed
try:
    from utils.telethon_patch import apply_patches
    apply_patches()
    logger.info("Applied Telethon patches")
except ImportError:
    logger.info("Telethon patch module not found, skipping")
except Exception as e:
    logger.error(f"Error applying Telethon patches: {str(e)}")

def main():
    """Main function to start the application"""
    logger.info("Starting Telegram Video Uploader")
    
    # Import after patches have been applied
    from app import USE_QT_UI, TelegramUploaderApp
    
    try:
        # Qt UI Mode
        if USE_QT_UI:
            try:
                # Check if PyQt5 is available
                from PyQt5 import QtWidgets
                
                # Create Qt application
                qt_app = QtWidgets.QApplication(sys.argv)
                
                # Create app instance
                app = TelegramUploaderApp()
                
                # Run application
                return qt_app.exec_()
                
            except ImportError:
                logger.warning("PyQt5 not available, falling back to Tkinter")
                
            except Exception as e:
                logger.error(f"Error initializing Qt UI: {str(e)}")
                logger.error(traceback.format_exc())
                logger.info("Falling back to Tkinter")
        
        # Tkinter Mode (fallback)
        # Create root window
        root = tk.Tk()
        
        # Create app instance
        app = TelegramUploaderApp(root)
        
        # Run application
        root.mainloop()
        
    except Exception as e:
        # Log error
        logger.error(f"Unrecoverable error: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Show error message
        try:
            messagebox.showerror(
                "Critical Error",
                f"An unrecoverable error has occurred:\n\n{str(e)}\n\nPlease restart the application."
            )
        except:
            pass
            
        # Exit with error code
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())