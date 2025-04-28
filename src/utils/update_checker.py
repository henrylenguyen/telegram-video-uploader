"""
Module kiểm tra cập nhật ứng dụng.
"""
import os
import sys
import json
import time
import logging
import requests
import threading
import traceback
import configparser
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class UpdateChecker:
    """
    Lớp kiểm tra cập nhật ứng dụng
    """
    
    # URL API kiểm tra cập nhật mặc định (cần thay đổi thành URL thực tế)
    DEFAULT_UPDATE_URL = "https://api.example.com/updates/check"
    
    # Thời gian tối thiểu giữa các lần kiểm tra cập nhật (giây)
    MIN_CHECK_INTERVAL = 24 * 60 * 60  # 1 ngày
    
    def __init__(self, app_version="1.0.0", app_name="Telegram Video Uploader", update_url=None, app_dir=None):
        """
        Khởi tạo UpdateChecker
        
        Args:
            app_version (str): Phiên bản hiện tại của ứng dụng
            app_name (str): Tên ứng dụng
            update_url (str, optional): URL API kiểm tra cập nhật
            app_dir (str, optional): Thư mục ứng dụng chính
        """
        self.app_version = app_version
        self.app_name = app_name
        self.update_url = update_url or self.DEFAULT_UPDATE_URL
        
        # Xác định thư mục gốc ứng dụng
        if app_dir:
            self.app_dir = app_dir
        elif getattr(sys, 'frozen', False):
            # Nếu đóng gói bằng PyInstaller
            self.app_dir = os.path.dirname(sys.executable)
        else:
            # Thư mục chứa script
            self.app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Đường dẫn tới thư mục dữ liệu
        self.data_dir = os.path.join(self.app_dir, 'data')
        
        # Đảm bảo thư mục dữ liệu tồn tại
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Đường dẫn tới file lưu thông tin cập nhật
        self.update_info_file = os.path.join(self.data_dir, 'update_info.json')
        
        # Lấy cấu hình
        self._load_config()
    
    def _load_config(self):
        """Nạp cấu hình từ file config.ini"""
        try:
            # Lấy đường dẫn đến file cấu hình
            config_path = os.path.join(self.app_dir, "config.ini")
            
            if os.path.exists(config_path):
                config = configparser.ConfigParser()
                with open(config_path, 'r', encoding='utf-8') as f:
                    config.read_file(f)
                
                # Nạp URL kiểm tra cập nhật từ cấu hình nếu có
                if 'APP' in config and 'update_url' in config['APP']:
                    self.update_url = config['APP']['update_url']
                
                # Nạp phiên bản ứng dụng từ cấu hình nếu có
                if 'APP' in config and 'version' in config['APP']:
                    self.app_version = config['APP']['version']
                
                # Nạp tên ứng dụng từ cấu hình nếu có
                if 'APP' in config and 'app_name' in config['APP']:
                    self.app_name = config['APP']['app_name']
                
                # Nạp thời gian kiểm tra cập nhật từ cấu hình
                if 'APP' in config and 'update_check_interval' in config['APP']:
                    try:
                        self.MIN_CHECK_INTERVAL = int(config['APP']['update_check_interval'])
                    except ValueError:
                        pass
        except Exception as e:
            logger.error(f"Lỗi khi đọc cấu hình: {str(e)}")
            logger.error(traceback.format_exc())
    
    def _load_update_info(self):
        """
        Đọc thông tin cập nhật từ file
        
        Returns:
            dict: Thông tin cập nhật
        """
        # Thông tin mặc định
        update_info = {
            'last_check': None,
            'last_version': self.app_version,
            'has_update': False,
            'update_url': None,
            'update_notes': None,
            'notified': False
        }
        
        try:
            # Kiểm tra nếu file thông tin cập nhật tồn tại
            if os.path.exists(self.update_info_file):
                with open(self.update_info_file, 'r', encoding='utf-8') as f:
                    file_info = json.load(f)
                    
                    # Cập nhật thông tin từ file
                    for key in update_info:
                        if key in file_info:
                            update_info[key] = file_info[key]
        except Exception as e:
            logger.error(f"Lỗi khi đọc thông tin cập nhật: {str(e)}")
            logger.error(traceback.format_exc())
        
        return update_info
    
    def _save_update_info(self, update_info):
        """
        Lưu thông tin cập nhật vào file
        
        Args:
            update_info (dict): Thông tin cập nhật
        """
        try:
            with open(self.update_info_file, 'w', encoding='utf-8') as f:
                json.dump(update_info, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Lỗi khi lưu thông tin cập nhật: {str(e)}")
            logger.error(traceback.format_exc())
    
    def _compare_versions(self, version1, version2):
        """
        So sánh hai phiên bản
        
        Args:
            version1 (str): Phiên bản thứ nhất
            version2 (str): Phiên bản thứ hai
            
        Returns:
            int: -1 nếu version1 < version2, 0 nếu version1 = version2, 1 nếu version1 > version2
        """
        try:
            # Chuyển đổi các phiên bản thành danh sách các số
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # Đảm bảo cả hai danh sách có cùng độ dài
            while len(v1_parts) < len(v2_parts):
                v1_parts.append(0)
            while len(v2_parts) < len(v1_parts):
                v2_parts.append(0)
            
            # So sánh từng phần
            for i in range(len(v1_parts)):
                if v1_parts[i] < v2_parts[i]:
                    return -1
                elif v1_parts[i] > v2_parts[i]:
                    return 1
            
            # Nếu mọi phần đều bằng nhau
            return 0
        except Exception as e:
            logger.error(f"Lỗi khi so sánh phiên bản: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Trong trường hợp lỗi, coi như không có cập nhật
            return 0
    
    def check_for_updates(self, force=False):
        """
        Kiểm tra cập nhật từ server
        
        Args:
            force (bool, optional): Bắt buộc kiểm tra ngay cả khi mới kiểm tra gần đây
            
        Returns:
            dict: Kết quả kiểm tra cập nhật
        """
        # Đọc thông tin cập nhật hiện tại
        update_info = self._load_update_info()
        
        # Kiểm tra xem có cần kiểm tra cập nhật không
        if not force and update_info['last_check']:
            last_check_time = datetime.fromisoformat(update_info['last_check'])
            time_since_last_check = (datetime.now() - last_check_time).total_seconds()
            
            if time_since_last_check < self.MIN_CHECK_INTERVAL:
                # Nếu mới kiểm tra gần đây, trả về thông tin đã có
                logger.info(f"Đã kiểm tra cập nhật gần đây ({(time_since_last_check / 3600):.2f} giờ trước). Bỏ qua.")
                
                # Kiểm tra xem có cập nhật không
                has_update = update_info.get('has_update', False)
                
                if has_update:
                    # Nếu có cập nhật, trả về thông tin cập nhật
                    return {
                        'has_update': True,
                        'current_version': self.app_version,
                        'latest_version': update_info.get('last_version', self.app_version),
                        'update_url': update_info.get('update_url', None),
                        'update_notes': update_info.get('update_notes', None),
                        'last_check': update_info.get('last_check', None),
                        'notified': update_info.get('notified', False)
                    }
                
                # Nếu không có cập nhật, trả về thông tin hiện tại
                return {
                    'has_update': False,
                    'current_version': self.app_version,
                    'latest_version': self.app_version,
                    'last_check': update_info.get('last_check', None)
                }
        
        try:
            # Chuẩn bị dữ liệu gửi lên server
            params = {
                'app_name': self.app_name,
                'current_version': self.app_version,
                'platform': sys.platform
            }
            
            # Giả lập kết quả từ server nếu URL là mặc định
            if self.update_url == self.DEFAULT_UPDATE_URL:
                # Giả lập phiên bản mới hơn
                fake_version = '1.1.0' if self._compare_versions(self.app_version, '1.1.0') < 0 else f"{self.app_version}.1"
                response_data = {
                    'status': 'success',
                    'has_update': self._compare_versions(self.app_version, fake_version) < 0,
                    'latest_version': fake_version,
                    'update_url': 'https://example.com/download',
                    'update_notes': 'Bản cập nhật mới với nhiều tính năng hấp dẫn.',
                    'update_size': '25.5 MB',
                    'update_date': datetime.now().strftime('%Y-%m-%d')
                }
            else:
                # Gửi yêu cầu kiểm tra cập nhật đến server
                response = requests.get(
                    self.update_url,
                    params=params,
                    timeout=10
                )
                
                # Kiểm tra phản hồi từ server
                if response.status_code == 200:
                    response_data = response.json()
                else:
                    # Nếu server trả về lỗi, sử dụng thông tin hiện tại
                    logger.error(f"Lỗi khi kiểm tra cập nhật. Mã lỗi: {response.status_code}")
                    return {
                        'has_update': False,
                        'current_version': self.app_version,
                        'latest_version': self.app_version,
                        'error': f"Lỗi kết nối đến server. Mã lỗi: {response.status_code}",
                        'last_check': datetime.now().isoformat()
                    }
            
            # Cập nhật thông tin
            update_info['last_check'] = datetime.now().isoformat()
            update_info['last_version'] = response_data.get('latest_version', self.app_version)
            update_info['has_update'] = response_data.get('has_update', False)
            update_info['update_url'] = response_data.get('update_url', None)
            update_info['update_notes'] = response_data.get('update_notes', None)
            
            # Nếu đây là lần đầu phát hiện cập nhật, đánh dấu là chưa thông báo
            if update_info['has_update'] and update_info['last_version'] != self.app_version:
                update_info['notified'] = False
            
            # Lưu thông tin cập nhật
            self._save_update_info(update_info)
            
            # Trả về kết quả
            result = {
                'has_update': update_info['has_update'],
                'current_version': self.app_version,
                'latest_version': update_info['last_version'],
                'update_url': update_info['update_url'],
                'update_notes': update_info['update_notes'],
                'last_check': update_info['last_check'],
                'notified': update_info['notified']
            }
            
            # Thêm thông tin bổ sung từ server nếu có
            if 'update_size' in response_data:
                result['update_size'] = response_data['update_size']
            
            if 'update_date' in response_data:
                result['update_date'] = response_data['update_date']
            
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi kết nối khi kiểm tra cập nhật: {str(e)}")
            
            # Cập nhật thời gian kiểm tra cuối
            update_info['last_check'] = datetime.now().isoformat()
            self._save_update_info(update_info)
            
            # Trả về thông tin lỗi
            return {
                'has_update': False,
                'current_version': self.app_version,
                'latest_version': self.app_version,
                'error': f"Lỗi kết nối: {str(e)}",
                'last_check': update_info['last_check']
            }
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra cập nhật: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Cập nhật thời gian kiểm tra cuối
            update_info['last_check'] = datetime.now().isoformat()
            self._save_update_info(update_info)
            
            # Trả về thông tin lỗi
            return {
                'has_update': False,
                'current_version': self.app_version,
                'latest_version': self.app_version,
                'error': f"Lỗi không xác định: {str(e)}",
                'last_check': update_info['last_check']
            }
    
    def check_for_updates_async(self, callback=None, force=False):
        """
        Kiểm tra cập nhật bất đồng bộ
        
        Args:
            callback (callable, optional): Hàm được gọi khi kiểm tra hoàn tất
            force (bool, optional): Bắt buộc kiểm tra ngay cả khi mới kiểm tra gần đây
        """
        def _check_and_callback():
            try:
                result = self.check_for_updates(force)
                
                if callback:
                    callback(result)
            except Exception as e:
                logger.error(f"Lỗi trong thread kiểm tra cập nhật: {str(e)}")
                logger.error(traceback.format_exc())
                
                if callback:
                    callback({
                        'has_update': False,
                        'current_version': self.app_version,
                        'latest_version': self.app_version,
                        'error': f"Lỗi trong thread: {str(e)}",
                        'last_check': datetime.now().isoformat()
                    })
        
        # Tạo và bắt đầu thread kiểm tra cập nhật
        thread = threading.Thread(target=_check_and_callback)
        thread.daemon = True
        thread.start()
    
    def mark_as_notified(self):
        """
        Đánh dấu đã thông báo cập nhật
        
        Returns:
            bool: True nếu đánh dấu thành công, False nếu thất bại
        """
        try:
            # Đọc thông tin cập nhật
            update_info = self._load_update_info()
            
            # Đánh dấu đã thông báo
            update_info['notified'] = True
            
            # Lưu thông tin cập nhật
            self._save_update_info(update_info)
            
            return True
        except Exception as e:
            logger.error(f"Lỗi khi đánh dấu đã thông báo cập nhật: {str(e)}")
            logger.error(traceback.format_exc())
            
            return False
    
    def manual_check(self):
        """
        Kiểm tra cập nhật thủ công (bỏ qua kiểm tra thời gian)
        
        Returns:
            dict: Kết quả kiểm tra cập nhật
        """
        return self.check_for_updates(force=True)


if __name__ == "__main__":
    # Mã kiểm thử
    logging.basicConfig(level=logging.DEBUG)
    
    checker = UpdateChecker()
    
    print("Kiểm tra cập nhật:")
    result = checker.check_for_updates()
    
    if 'error' in result:
        print(f"  Lỗi: {result['error']}")
    else:
        print(f"  Phiên bản hiện tại: {result['current_version']}")
        print(f"  Phiên bản mới nhất: {result['latest_version']}")
        print(f"  Có cập nhật: {'Có' if result['has_update'] else 'Không'}")
        
        if result['has_update']:
            print(f"  Đường dẫn tải: {result['update_url']}")
            print(f"  Ghi chú: {result['update_notes']}")
        
        print(f"  Kiểm tra lần cuối: {result['last_check']}")
