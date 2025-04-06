"""
Module for patching VideoSplitter để ngăn chặn việc chia nhỏ video khi use_telethon=True
"""

import os
import logging
import tkinter.messagebox as messagebox
from functools import wraps

logger = logging.getLogger("TelethonPatch")

def apply_patches():
    """Áp dụng tất cả các patch cần thiết"""
    logger.info("Đang áp dụng TelethonPatch để ngăn chặn việc chia nhỏ video khi use_telethon=True")
    
    try:
        # Import VideoSplitter
        from utils.video_splitter import VideoSplitter
        
        # Lưu phương thức gốc
        original_split_video = VideoSplitter.split_video
        
        @wraps(original_split_video)
        def patched_split_video(self, *args, **kwargs):
            """Phiên bản patched của split_video để chặn việc chia nhỏ khi use_telethon=True"""
            logger.info("🔍 TelethonPatch: Kiểm tra trước khi chia nhỏ video")
            
            # Kiểm tra video path từ tham số
            video_path = args[0] if args else kwargs.get('video_path')
            if not video_path:
                logger.error("❌ TelethonPatch: Không tìm thấy video_path trong tham số")
                return original_split_video(self, *args, **kwargs)
                
            # Lấy kích thước video
            try:
                video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
                video_name = os.path.basename(video_path)
                logger.info(f"🔍 TelethonPatch: Video {video_name} ({video_size_mb:.2f} MB)")
            except Exception as e:
                logger.error(f"❌ TelethonPatch: Lỗi khi lấy kích thước video: {str(e)}")
                return original_split_video(self, *args, **kwargs)
            
            # Kiểm tra use_telethon từ cấu hình
            try:
                import sys
                main_module = sys.modules['__main__']
                use_telethon = False
                
                if hasattr(main_module, 'app') and hasattr(main_module.app, 'config'):
                    use_telethon = main_module.app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
                    logger.info(f"🔍 TelethonPatch: Kiểm tra từ app.config: use_telethon = {use_telethon}")
                
                # Kiểm tra nếu không thể lấy từ main_module.app
                if not use_telethon:
                    # Thử lấy từ các vị trí khác
                    try:
                        from configparser import ConfigParser
                        config = ConfigParser()
                        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')
                        if os.path.exists(config_path):
                            config.read(config_path)
                            if 'TELETHON' in config and 'use_telethon' in config['TELETHON']:
                                use_telethon = config['TELETHON'].getboolean('use_telethon', fallback=False)
                                logger.info(f"🔍 TelethonPatch: Kiểm tra từ file config.ini: use_telethon = {use_telethon}")
                    except Exception as e:
                        logger.error(f"❌ TelethonPatch: Lỗi khi đọc config.ini: {str(e)}")
                
                # BLOCK VIỆC CHIA NHỎ VIDEO KHI use_telethon=True và video lớn hơn 50MB
                if use_telethon and video_size_mb > 50:
                    logger.warning(f"⛔ TelethonPatch: CHẶN CHIA NHỎ VIDEO {video_name} ({video_size_mb:.2f} MB) vì use_telethon=True")
                    
                    # Hiển thị thông báo
                    messagebox.showerror(
                        "Lỗi - Không thể chia nhỏ video", 
                        f"Video '{video_name}' ({video_size_mb:.2f} MB) không thể được chia nhỏ khi bật tùy chọn 'Sử dụng Telethon API'.\n\n"
                        f"Vui lòng đảm bảo đã đăng nhập Telethon API trong tab Cài đặt, hoặc tắt tùy chọn 'Sử dụng Telethon API'."
                    )
                    
                    # Trả về danh sách trống để chỉ ra rằng không chia nhỏ thành công
                    return []
            except Exception as e:
                logger.error(f"❌ TelethonPatch: Lỗi khi kiểm tra use_telethon: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
            
            # Nếu không phải block, thực hiện phương thức gốc
            logger.info("✅ TelethonPatch: Cho phép chia nhỏ video")
            return original_split_video(self, *args, **kwargs)
        
        # Thay thế phương thức gốc bằng phiên bản patched
        VideoSplitter.split_video = patched_split_video
        logger.info("✅ TelethonPatch: Đã áp dụng patch cho VideoSplitter.split_video")
        
        return True
    except Exception as e:
        logger.error(f"❌ TelethonPatch: Lỗi khi áp dụng patch: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False