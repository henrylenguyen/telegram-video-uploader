"""
Module quản lý các cài đặt cấu hình của ứng dụng.
"""
import os
import configparser
import logging
import tkinter as tk
from tkinter import messagebox

logger = logging.getLogger("ConfigManager")

class ConfigManager:
    """
    Quản lý cài đặt cấu hình của ứng dụng.
    """
    
    def __init__(self, config_file='config.ini'):
        """
        Khởi tạo ConfigManager.
        
        Args:
            config_file (str): Đường dẫn đến file cấu hình
        """
        self.config_file = config_file
    
    def load_config(self):
        """
        Tải cấu hình từ file config.ini
        
        Returns:
            configparser.ConfigParser: Đối tượng cấu hình
        """
        config = configparser.ConfigParser()
        
        # Tạo file cấu hình mặc định nếu không tồn tại
        if not os.path.exists(self.config_file):
            config['TELEGRAM'] = {
                'bot_token': '',
                'chat_id': '',
                'notification_chat_id': ''  # Giữ lại để tương thích ngược
            }
            config['SETTINGS'] = {
                'video_folder': '',
                'video_extensions': '.mp4,.avi,.mkv,.mov,.wmv',
                'delay_between_uploads': '5',
                'auto_mode': 'false',
                'check_duplicates': 'true',
                'auto_check_interval': '60'  # Thời gian kiểm tra tự động (giây)
            }
            config['TELETHON'] = {
                'api_id': '',
                'api_hash': '',
                'phone': '',
                'use_telethon': 'false'
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            
            # Hiển thị cửa sổ cấu hình ban đầu nếu đây là lần đầu chạy
            self.show_first_run_config_dialog()
        
        config.read(self.config_file, encoding='utf-8')
        
        # Đảm bảo section TELETHON tồn tại
        if 'TELETHON' not in config:
            config['TELETHON'] = {
                'api_id': '',
                'api_hash': '',
                'phone': '',
                'use_telethon': 'false'
            }
        
        # Đảm bảo notification_chat_id luôn giống chat_id để đơn giản hóa
        if 'TELEGRAM' in config and 'chat_id' in config['TELEGRAM']:
            config['TELEGRAM']['notification_chat_id'] = config['TELEGRAM']['chat_id']
        
        return config
    def save_config(self, config):
        """
        Lưu cấu hình vào file
        
        Args:
            config (configparser.ConfigParser): Đối tượng cấu hình
        """
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        logger.info("Đã lưu cấu hình")
    
    def save_general_settings(self, app):
        """Lưu cài đặt chung từ giao diện vào file cấu hình"""
        # Lấy giá trị từ giao diện
        video_extensions = app.video_extensions_var.get()
        delay = app.delay_var.get()
        
        try:
            # Kiểm tra giá trị
            delay_value = int(delay)
            if delay_value < 0:
                raise ValueError("Thời gian chờ không được âm")
        except ValueError:
            messagebox.showerror("Lỗi", "Thời gian chờ phải là một số nguyên không âm!")
            return
        
        # Lưu vào cấu hình
        app.config['SETTINGS']['video_extensions'] = video_extensions
        app.config['SETTINGS']['delay_between_uploads'] = delay
        
        # Ghi file
        self.save_config(app.config)
        
        # Thông báo
        messagebox.showinfo("Thông báo", "Đã lưu cài đặt chung thành công!")
    
    def show_first_run_config_dialog(self):
        """Hiển thị cửa sổ cấu hình khi chạy lần đầu"""
        # Tạo cửa sổ cấu hình sẽ được hiển thị sau khi khởi động ứng dụng
        # Sẽ được triển khai đầy đủ trong phiên bản hoàn chỉnh
        logger.info("Cài đặt lần đầu: Tạo file cấu hình mặc định")