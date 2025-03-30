"""
Module quản lý kết nối với Telegram API.
"""
import logging
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

logger = logging.getLogger("TelegramConnector")

class TelegramConnector:
    """
    Quản lý việc kết nối và tương tác với Telegram API.
    """
    
    def __init__(self, app):
        """
        Khởi tạo TelegramConnector.
        
        Args:
            app: Đối tượng TelegramUploaderApp
        """
        from utils.telegram_api import TelegramAPI
        from utils.telethon_uploader import TelethonUploader
        
        self.telegram_api = TelegramAPI()
        self.telethon_uploader = TelethonUploader()
        
        # Kết nối ban đầu
        self.connect_telegram(app)
    
    def connect_telegram(self, app):
        """
        Kết nối với bot Telegram
        
        Args:
            app: Đối tượng TelegramUploaderApp
        """
        bot_token = app.config['TELEGRAM']['bot_token']
        
        if bot_token:
            # Sử dụng TelegramAPI để kết nối
            if self.telegram_api.connect(bot_token):
                logger.info("Đã kết nối với bot Telegram thành công")
                
                # Gửi thông báo đã kết nối
                notification_chat_id = app.config['TELEGRAM']['notification_chat_id']
                if notification_chat_id:
                    try:
                        self.telegram_api.send_message(
                            notification_chat_id, 
                            "✅ Ứng dụng đã kết nối thành công!"
                        )
                    except Exception as e:
                        logger.error(f"Không thể gửi thông báo: {e}")
            else:
                logger.error("Không thể kết nối với bot Telegram")
                
                # Nếu không thể kết nối, kiểm tra xem có phải là lần đầu chạy hay không
                if not app.config['TELEGRAM']['notification_chat_id'] and not app.config['TELEGRAM']['chat_id']:
                    # Hiển thị hộp thoại yêu cầu cấu hình
                    messagebox.showwarning(
                        "Cấu hình chưa hoàn tất", 
                        "Bạn cần cấu hình thông tin Telegram. Vui lòng nhập thông tin trong tab Cài đặt."
                    )
        
        # Kết nối Telethon nếu có thông tin cấu hình
        use_telethon = app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
        if use_telethon:
            api_id = app.config.get('TELETHON', 'api_id', fallback='')
            api_hash = app.config.get('TELETHON', 'api_hash', fallback='')
            phone = app.config.get('TELETHON', 'phone', fallback='')
            
            if api_id and api_hash and phone:
                try:
                    api_id = int(api_id)
                    if self.telethon_uploader.login(api_id, api_hash, phone, interactive=False):
                        logger.info("Đã kết nối với Telegram API (Telethon) thành công")
                except Exception as e:
                    logger.error(f"Lỗi khi kết nối Telethon: {str(e)}")
    
    def test_telegram_connection(self, app):
      """
      Kiểm tra kết nối Telegram
      
      Args:
          app: Đối tượng TelegramUploaderApp
      """
      bot_token = app.bot_token_var.get()
      notification_chat_id = app.notification_chat_id_var.get()
      
      if not bot_token:
          messagebox.showerror("Lỗi", "Vui lòng nhập Bot Token!")
          return
          
      if not notification_chat_id:
          # Nếu không có chat ID thông báo, thử dùng chat ID đích
          notification_chat_id = app.chat_id_var.get()
          if not notification_chat_id:
              messagebox.showerror("Lỗi", "Vui lòng nhập Chat ID thông báo hoặc Chat ID đích!")
              return
      
      # Hiển thị thông báo đang kiểm tra
      app.status_var.set("Đang kiểm tra kết nối Telegram...")
      app.root.update_idletasks()
      
      try:
          # Vì phần telegram_api có thể chưa được khởi tạo đúng,
          # tạo một instance mới để kiểm tra kết nối
          from utils.telegram_api import TelegramAPI
          temp_api = TelegramAPI()  # Esta línea tenía un problema de indentación
          success, message = temp_api.test_connection(bot_token, notification_chat_id)
          
          if success:
              # Nếu thành công, lưu lại instance
              self.telegram_api = temp_api
              messagebox.showinfo("Thành công", message)
          else:
              messagebox.showerror("Lỗi", message)
      except Exception as e:
          messagebox.showerror("Lỗi kết nối", f"Không thể kiểm tra kết nối: {str(e)}")
      
      # Khôi phục trạng thái
      app.status_var.set("Sẵn sàng")
    
    def login_telethon(self, app):
        """
        Đăng nhập vào Telethon API để tải lên file lớn
        
        Args:
            app: Đối tượng TelegramUploaderApp
        """
        # Lấy thông tin từ giao diện
        api_id = app.api_id_var.get()
        api_hash = app.api_hash_var.get()
        phone = app.phone_var.get()
        
        # Kiểm tra các trường
        if not api_id or not api_hash or not phone:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ API ID, API Hash và số điện thoại!")
            return
        
        try:
            # Chuyển đổi API ID sang số
            api_id = int(api_id)
            
            # Hiển thị dialog đăng nhập
            if self.telethon_uploader.show_login_dialog(app.root):
                # Đăng nhập thành công
                messagebox.showinfo(
                    "Thành công", 
                    "Đăng nhập Telethon thành công! Bạn có thể tải lên video lớn hơn 50MB."
                )
                
                # Lưu cài đặt
                app.config['TELETHON']['api_id'] = str(api_id)
                app.config['TELETHON']['api_hash'] = api_hash
                app.config['TELETHON']['phone'] = phone
                app.config_manager.save_config(app.config)
            else:
                messagebox.showerror("Lỗi", "Đăng nhập Telethon thất bại. Vui lòng kiểm tra thông tin và thử lại.")
        except ValueError:
            messagebox.showerror("Lỗi", "API ID phải là một số nguyên!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi đăng nhập Telethon: {str(e)}")
    
    def save_telegram_settings(self, app):
        """
        Lưu cài đặt Telegram Bot từ giao diện vào file cấu hình
        
        Args:
            app: Đối tượng TelegramUploaderApp
        """
        # Lấy giá trị từ giao diện
        bot_token = app.bot_token_var.get()
        chat_id = app.chat_id_var.get()
        notification_chat_id = app.notification_chat_id_var.get()
        
        # Lưu vào cấu hình
        app.config['TELEGRAM']['bot_token'] = bot_token
        app.config['TELEGRAM']['chat_id'] = chat_id
        app.config['TELEGRAM']['notification_chat_id'] = notification_chat_id
        
        # Ghi file
        app.config_manager.save_config(app.config)
        
        # Thông báo
        messagebox.showinfo("Thông báo", "Đã lưu cài đặt Bot Telegram thành công!")
        
        # Kết nối lại với Telegram nếu Bot Token thay đổi
        if bot_token != self.telegram_api.bot_token:
            self.telegram_api.disconnect()
            self.connect_telegram(app)
    
    def save_telethon_settings(self, app):
        """
        Lưu cài đặt Telethon từ giao diện vào file cấu hình
        
        Args:
            app: Đối tượng TelegramUploaderApp
        """
        # Lấy giá trị từ giao diện
        use_telethon = app.use_telethon_var.get()
        api_id = app.api_id_var.get()
        api_hash = app.api_hash_var.get()
        phone = app.phone_var.get()
        
        # Lưu vào cấu hình
        app.config['TELETHON']['use_telethon'] = str(use_telethon).lower()
        app.config['TELETHON']['api_id'] = api_id
        app.config['TELETHON']['api_hash'] = api_hash
        app.config['TELETHON']['phone'] = phone
        
        # Ghi file
        app.config_manager.save_config(app.config)
        
        # Thông báo
        messagebox.showinfo("Thông báo", "Đã lưu cài đặt Telethon thành công!")