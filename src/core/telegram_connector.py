"""
Module for connecting to Telegram services
"""

import logging
from tkinter import messagebox
from utils.telegram_api import TelegramAPI
from utils.telethon_uploader import TelethonUploader

logger = logging.getLogger("TelegramConnector")

class TelegramConnector:
    """
    Class để kết nối với Telegram sử dụng cả Bot API và Telethon API
    """
    
    def __init__(self, app):
        """
        Khởi tạo Telegram connector
        
        Args:
            app: TelegramUploaderApp instance
        """
        self.app = app
        self.telegram_api = TelegramAPI()
        self.telethon_uploader = TelethonUploader()
        
        # Kết nối với Telegram
        self.connect_telegram(app)
    
    def connect_telegram(self, app):
        """
        Kết nối với Telegram sử dụng cả Bot API và Telethon API
        
        Args:
            app: TelegramUploaderApp instance
        """
        # Kết nối với Telegram Bot API
        bot_token = app.config['TELEGRAM']['bot_token']
        
        if bot_token:
            # Kết nối với Telegram Bot API
            if self.telegram_api.connect(bot_token):
                logger.info("Đã kết nối với bot Telegram thành công")
            else:
                logger.error("Không thể kết nối với bot Telegram")
                
                # Hiển thị hộp thoại cấu hình nếu đây là lần chạy đầu tiên
                if not app.config['TELEGRAM']['chat_id']:
                    messagebox.showwarning(
                        "Cấu hình chưa hoàn tất", 
                        "Bạn cần cấu hình thông tin Telegram. Vui lòng nhập thông tin trong tab Cài đặt."
                    )
        
        # Kết nối với Telethon API nếu được cấu hình
        self._connect_telethon(app)
        
    def _connect_telethon(self, app):
        """
        Kết nối với Telethon API với xử lý lỗi tốt hơn và ghi log gỡ lỗi
        
        Args:
            app: TelegramUploaderApp instance
        """
        use_telethon = app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
        logger.info(f"Cấu hình Telethon: use_telethon={use_telethon}")
        
        if use_telethon:
            # Kiểm tra xem cấu hình Telethon có đầy đủ không
            api_id = app.config.get('TELETHON', 'api_id', fallback='')
            api_hash = app.config.get('TELETHON', 'api_hash', fallback='')
            phone = app.config.get('TELETHON', 'phone', fallback='')
            
            if api_id and api_hash and phone:
                try:
                    # Chuyển đổi api_id thành int
                    api_id = int(api_id)
                    
                    # Ghi log trạng thái hiện tại
                    logger.info(f"Kiểm tra kết nối Telethon với api_id={api_id}, phone={phone}")
                    
                    # THAY ĐỔI: Thiết lập connected = True nếu đã có cấu hình đầy đủ
                    self.telethon_uploader.connected = True
                    logger.info("Đã thiết lập telethon_uploader.connected = True do có cấu hình đầy đủ")
                    
                    # Kiểm tra xem đã kết nối chưa mà không chặn UI
                    try:
                        already_connected = self.telethon_uploader.is_user_authorized()
                        logger.info(f"Kiểm tra xác thực người dùng Telethon: {already_connected}")
                    except Exception as e:
                        logger.error(f"Lỗi kiểm tra xác thực người dùng: {str(e)}")
                        already_connected = False
                    
                    if not already_connected:
                        # Thử đăng nhập không tương tác
                        login_result = self.telethon_uploader.login(api_id, api_hash, phone, interactive=False)
                        logger.info(f"Kết quả đăng nhập Telethon: {login_result}")
                        
                        if login_result:
                            logger.info("Đã kết nối với Telegram API (Telethon) thành công")
                        else:
                            # Vẫn giữ connected = True để ưu tiên dùng Telethon
                            logger.warning("Không thể đăng nhập Telethon tự động, nhưng vẫn ưu tiên sử dụng Telethon")
                            
                            # Lên lịch hiển thị hộp thoại đăng nhập sau khi khởi động hoàn tất
                            def show_login_dialog():
                                from ui.edit_config_modal import TelethonEditModal
                                TelethonEditModal(app)
                            
                            # Hiển thị hộp thoại đăng nhập sau 3 giây
                            app.root.after(3000, show_login_dialog)
                    else:
                        logger.info("Telethon đã được kết nối sẵn")
                except Exception as e:
                    logger.error(f"Lỗi khi kết nối Telethon: {str(e)}")
                    # Vẫn đặt connected = True dù lỗi
                    self.telethon_uploader.connected = True
                    logger.info("Đã thiết lập telethon_uploader.connected = True dù gặp lỗi kết nối")
                    import traceback
                    logger.error(traceback.format_exc())
            else:
                logger.warning("Cấu hình Telethon không đầy đủ (thiếu api_id, api_hash, hoặc phone)")
                # Tắt Telethon nếu cấu hình không đầy đủ
                app.config['TELETHON']['use_telethon'] = 'false'
                try:
                    app.config_manager.save_config(app.config)
                except:
                    pass
        else:
            logger.info("Telethon bị tắt trong cấu hình")