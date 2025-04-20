"""
Quản lý cấu hình cho UI Telegram
"""
import os
import logging
import configparser
from PyQt5 import QtWidgets

logger = logging.getLogger(__name__)

def load_existing_config(self):
    """Tải cấu hình hiện tại nếu có"""
    if not hasattr(self.app, 'config'):
        return
            
    # Tải cấu hình Bot API
    if 'TELEGRAM' in self.app.config:
        bot_token = self.app.config['TELEGRAM'].get('bot_token', '')
        chat_id = self.app.config['TELEGRAM'].get('chat_id', '')
        
        if hasattr(self, 'botTokenEdit') and self.botTokenEdit:
            self.botTokenEdit.setText(bot_token)
            
        if hasattr(self, 'chatIdEdit') and self.chatIdEdit:
            self.chatIdEdit.setText(chat_id)
    
    # Tải cấu hình Telethon API
    if 'TELETHON' in self.app.config:
        api_id = self.app.config['TELETHON'].get('api_id', '')
        api_hash = self.app.config['TELETHON'].get('api_hash', '')
        phone = self.app.config['TELETHON'].get('phone', '')
        
        if hasattr(self, 'apiIdEdit') and self.apiIdEdit:
            self.apiIdEdit.setText(api_id)
            
        if hasattr(self, 'apiHashEdit') and self.apiHashEdit:
            self.apiHashEdit.setText(api_hash)
            
        if hasattr(self, 'phoneEdit') and self.phoneEdit:
            self.phoneEdit.setText(phone)

def save_config(self, section, data):
    """
    Lưu cấu hình vào file config
    
    Args:
        section: Tên section (TELEGRAM hoặc TELETHON)
        data: Dict chứa dữ liệu cần lưu
    """
    try:
        # Đảm bảo section tồn tại
        if not self.app.config.has_section(section):
            self.app.config.add_section(section)
        
        # Lưu dữ liệu vào section
        for key, value in data.items():
            self.app.config[section][key] = value
        
        # Đường dẫn đến file cấu hình
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.ini')
        
        # Lưu cấu hình
        with open(config_path, 'w', encoding='utf-8') as configfile:
            self.app.config.write(configfile)
            
        # Cập nhật trạng thái
        if section == "TELEGRAM":
            self.telegram_connected = True
        elif section == "TELETHON":
            self.telethon_connected = True
            
        # Phát tín hiệu
        self.configSaved.emit(True)
        
        logger.info(f"Đã lưu cấu hình {section} thành công")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi lưu cấu hình {section}: {str(e)}")
        # Phát tín hiệu lỗi
        self.configSaved.emit(False)
        return False

def save_draft(self):
    """Lưu cấu hình hiện tại làm bản nháp"""
    try:
        # Lấy dữ liệu từ form
        bot_token = ''
        chat_id = ''
        api_id = ''
        api_hash = ''
        phone = ''
        
        if hasattr(self, 'botTokenEdit') and self.botTokenEdit:
            bot_token = self.botTokenEdit.text().strip()
            
        if hasattr(self, 'chatIdEdit') and self.chatIdEdit:
            chat_id = self.chatIdEdit.text().strip()
            
        if hasattr(self, 'apiIdEdit') and self.apiIdEdit:
            api_id = self.apiIdEdit.text().strip()
            
        if hasattr(self, 'apiHashEdit') and self.apiHashEdit:
            api_hash = self.apiHashEdit.text().strip()
            
        if hasattr(self, 'phoneEdit') and self.phoneEdit:
            phone = self.phoneEdit.text().strip()
        
        # Lưu cấu hình Bot API
        if bot_token or chat_id:
            # Kiểm tra section TELEGRAM tồn tại
            if not self.app.config.has_section('TELEGRAM'):
                self.app.config.add_section('TELEGRAM')
                
            # Lưu dữ liệu
            if bot_token:
                self.app.config['TELEGRAM']['bot_token'] = bot_token
            if chat_id:
                self.app.config['TELEGRAM']['chat_id'] = chat_id
        
        # Lưu cấu hình Telethon API
        if api_id or api_hash or phone:
            # Kiểm tra section TELETHON tồn tại
            if not self.app.config.has_section('TELETHON'):
                self.app.config.add_section('TELETHON')
                
            # Lưu dữ liệu
            if api_id:
                self.app.config['TELETHON']['api_id'] = api_id
            if api_hash:
                self.app.config['TELETHON']['api_hash'] = api_hash
            if phone:
                self.app.config['TELETHON']['phone'] = phone
        
        # Đường dẫn đến file cấu hình
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.ini')
        
        # Lưu cấu hình
        with open(config_path, 'w', encoding='utf-8') as configfile:
            self.app.config.write(configfile)
            
        logger.info("Đã lưu bản nháp cấu hình")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi lưu bản nháp cấu hình: {str(e)}")
        return False

def validate_config(self, section):
    """
    Kiểm tra cấu hình hợp lệ
    
    Args:
        section: Section cần kiểm tra (TELEGRAM hoặc TELETHON)
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if section == "TELEGRAM":
        # Kiểm tra Bot API
        bot_token = self.botTokenEdit.text().strip()
        chat_id = self.chatIdEdit.text().strip()
        
        if not bot_token:
            return (False, "Vui lòng nhập Bot Token")
            
        if not chat_id:
            return (False, "Vui lòng nhập Chat ID")
            
        # Kiểm tra định dạng Bot Token
        if ":" not in bot_token:
            return (False, "Bot Token không hợp lệ. Định dạng đúng: 123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw")
            
        # Kiểm tra định dạng Chat ID
        try:
            # Chat ID có thể bắt đầu bằng '-' cho nhóm
            chat_id_val = int(chat_id)
        except ValueError:
            return (False, "Chat ID phải là số nguyên")
        
        return (True, "")
    
    elif section == "TELETHON":
        # Kiểm tra Telethon API
        api_id = self.apiIdEdit.text().strip()
        api_hash = self.apiHashEdit.text().strip()
        phone = self.phoneEdit.text().strip()
        
        if not api_id:
            return (False, "Vui lòng nhập API ID")
            
        if not api_hash:
            return (False, "Vui lòng nhập API Hash")
            
        if not phone:
            return (False, "Vui lòng nhập số điện thoại")
            
        # Kiểm tra định dạng API ID
        try:
            api_id_val = int(api_id)
        except ValueError:
            return (False, "API ID phải là số nguyên")
            
        # Kiểm tra định dạng API Hash
        if len(api_hash) != 32 and not all(c in "0123456789abcdefABCDEF" for c in api_hash):
            return (False, "API Hash không hợp lệ. Phải là chuỗi 32 ký tự hex")
            
        # Kiểm tra định dạng số điện thoại
        if not phone.startswith("+"):
            return (False, "Số điện thoại phải bắt đầu bằng +. Ví dụ: +84123456789")
            
        return (True, "")
    
    return (False, "Section không hợp lệ")
