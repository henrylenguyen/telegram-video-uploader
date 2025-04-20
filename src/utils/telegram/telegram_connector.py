"""
Module kết nối và quản lý Telegram
"""
import logging
import os
from utils.telegram.telegram_api import TelegramAPI
from utils.telegram.telethon_uploader import TelethonUploader

logger = logging.getLogger(__name__)

class TelegramConnector:
    """
    Quản lý kết nối với các dịch vụ Telegram
    """
    
    def __init__(self, app):
        """
        Khởi tạo connector
        
        Args:
            app: Instance của ứng dụng chính
        """
        self.app = app
        self.telegram_api = TelegramAPI()
        self.telethon_uploader = TelethonUploader()
        
        # Kết nối ngay khi khởi tạo
        self.connect_telegram(app)
    
    def connect_telegram(self, app):
        """
        Kết nối với Telegram dùng cả Bot API và Telethon API
        
        Args:
            app: Instance của ứng dụng chính
        """
        # Kết nối với Bot API
        bot_token = app.config['TELEGRAM'].get('bot_token', '')
        
        if bot_token:
            if self.telegram_api.connect(bot_token):
                logger.info("Đã kết nối thành công với Telegram Bot API")
            else:
                logger.error("Không thể kết nối với Telegram Bot API")
        
        # Kết nối với Telethon API
        self._connect_telethon(app)
    
    def _connect_telethon(self, app):
        """
        Kết nối với Telethon API
        
        Args:
            app: Instance của ứng dụng chính
        """
        use_telethon = app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
        logger.info(f"Cấu hình Telethon: use_telethon={use_telethon}")
        
        if use_telethon:
            # Kiểm tra cấu hình Telethon
            api_id = app.config.get('TELETHON', 'api_id', fallback='')
            api_hash = app.config.get('TELETHON', 'api_hash', fallback='')
            phone = app.config.get('TELETHON', 'phone', fallback='')
            
            if api_id and api_hash and phone:
                try:
                    # Chuyển api_id thành số nguyên
                    api_id = int(api_id)
                    
                    logger.info(f"Kiểm tra kết nối Telethon với api_id={api_id}, phone={phone}")
                    
                    # Thiết lập trạng thái kết nối
                    self.telethon_uploader.connected = True
                    
                    # Kiểm tra xác thực
                    already_connected = self.telethon_uploader.is_user_authorized()
                    logger.info(f"Kiểm tra xác thực Telethon: {already_connected}")
                    
                    if not already_connected:
                        # Thử đăng nhập không tương tác
                        login_result = self.telethon_uploader.login(api_id, api_hash, phone, interactive=False)
                        logger.info(f"Kết quả đăng nhập Telethon: {login_result}")
                    else:
                        logger.info("Telethon đã được xác thực sẵn")
                        
                except Exception as e:
                    logger.error(f"Lỗi khi kết nối Telethon: {str(e)}")
                    # Vẫn đặt connected = True để ưu tiên sử dụng
                    self.telethon_uploader.connected = True
            else:
                logger.warning("Cấu hình Telethon không đầy đủ")
                # Tắt Telethon nếu cấu hình không đầy đủ
                app.config['TELETHON']['use_telethon'] = 'false'
                try:
                    app.config_manager.save_config(app.config)
                except:
                    pass
        else:
            logger.info("Telethon bị tắt trong cấu hình")
