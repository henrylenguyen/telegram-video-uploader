"""
Module kiểm tra và quản lý không gian lưu trữ của ứng dụng.
"""
import os
import sys
import shutil
import logging
import traceback
import tempfile
import platform
from pathlib import Path

logger = logging.getLogger(__name__)

class DiskSpaceChecker:
    """
    Lớp kiểm tra và quản lý không gian lưu trữ
    """
    
    # Không gian tối thiểu cần thiết cho ứng dụng (tính bằng bytes)
    MIN_REQUIRED_SPACE = 1024 * 1024 * 1024  # 1GB
    
    # Không gian đề xuất cho ứng dụng hoạt động tốt (tính bằng bytes)
    RECOMMENDED_SPACE = 5 * 1024 * 1024 * 1024  # 5GB
    
    # Kích thước ước tính của ứng dụng (tính bằng bytes)
    ESTIMATED_APP_SIZE = 100 * 1024 * 1024  # 100MB
    
    def __init__(self, app_dir=None):
        """
        Khởi tạo DiskSpaceChecker
        
        Args:
            app_dir (str, optional): Thư mục ứng dụng chính
        """
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
        
        # Đường dẫn tới thư mục cache
        self.cache_dir = os.path.join(self.app_dir, 'cache')
        
        # Đường dẫn tới thư mục tạm
        self.temp_dir = os.path.join(self.app_dir, 'temp')
        
        # Đường dẫn tới thư mục logs
        self.logs_dir = os.path.join(self.app_dir, 'logs')
        
        # Đường dẫn tới thư mục chứa FFmpeg
        self.ffmpeg_dir = os.path.join(self.app_dir, 'ffmpeg')
        
        # Danh sách các thư mục cần kiểm tra
        self.directories = [
            self.data_dir,
            self.cache_dir,
            self.temp_dir,
            self.logs_dir,
            self.ffmpeg_dir
        ]
    
    def check_space(self, path=None):
        """
        Kiểm tra không gian trống trên ổ đĩa chứa path
        
        Args:
            path (str, optional): Đường dẫn cần kiểm tra. Mặc định là thư mục ứng dụng
            
        Returns:
            dict: Thông tin về không gian ổ đĩa
        """
        if path is None:
            path = self.app_dir
        
        try:
            # Lấy thông tin không gian đĩa
            if platform.system() == 'Windows':
                total, used, free = shutil.disk_usage(path)
            else:
                stat = os.statvfs(path)
                # Dung lượng tổng
                total = stat.f_frsize * stat.f_blocks
                # Không gian trống có thể sử dụng bởi cả root và user
                free = stat.f_frsize * stat.f_bavail
                # Không gian đã sử dụng
                used = total - free
            
            # Tạo dictionary chứa thông tin không gian đĩa
            disk_info = {
                'total': total,
                'used': used,
                'free': free,
                'percent_used': round((used / total) * 100, 2),
                'percent_free': round((free / total) * 100, 2),
                'has_min_space': free >= self.MIN_REQUIRED_SPACE,
                'has_recommended_space': free >= self.RECOMMENDED_SPACE,
                'drive': os.path.splitdrive(os.path.abspath(path))[0] if platform.system() == 'Windows' else Path(path).parts[0],
                'formatted': {
                    'total': self._format_size(total),
                    'used': self._format_size(used),
                    'free': self._format_size(free)
                }
            }
            
            return disk_info
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra không gian đĩa: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Trả về dictionary mặc định với thông tin lỗi
            return {
                'total': 0,
                'used': 0,
                'free': 0,
                'percent_used': 0,
                'percent_free': 0,
                'has_min_space': False,
                'has_recommended_space': False,
                'drive': '',
                'error': str(e),
                'formatted': {
                    'total': '0 B',
                    'used': '0 B',
                    'free': '0 B'
                }
            }
    
    def _format_size(self, size_bytes):
        """Định dạng kích thước file thành chuỗi dễ đọc"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def get_app_size(self):
        """
        Tính toán kích thước hiện tại của ứng dụng
        
        Returns:
            dict: Thông tin về kích thước ứng dụng
        """
        try:
            total_size = 0
            
            # Tính tổng kích thước của các thư mục
            for directory in self.directories:
                if os.path.exists(directory):
                    dir_size = self._get_dir_size(directory)
                    total_size += dir_size
            
            return {
                'size': total_size,
                'formatted': self._format_size(total_size)
            }
        except Exception as e:
            logger.error(f"Lỗi khi tính toán kích thước ứng dụng: {str(e)}")
            logger.error(traceback.format_exc())
            
            return {
                'size': 0,
                'formatted': '0 B',
                'error': str(e)
            }
    
    def _get_dir_size(self, path):
        """
        Tính tổng kích thước của một thư mục
        
        Args:
            path (str): Đường dẫn tới thư mục
            
        Returns:
            int: Kích thước thư mục tính bằng bytes
        """
        total_size = 0
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total_size += entry.stat().st_size
                elif entry.is_dir():
                    total_size += self._get_dir_size(entry.path)
        return total_size
    
    def check_temp_write_permission(self):
        """
        Kiểm tra quyền ghi vào thư mục tạm
        
        Returns:
            bool: True nếu có quyền ghi, False nếu không
        """
        try:
            # Tạo file tạm để kiểm tra quyền ghi
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(b"Test write permission")
            temp_file.close()
            
            # Xóa file tạm
            os.unlink(temp_file.name)
            
            return True
        except Exception as e:
            logger.error(f"Không có quyền ghi vào thư mục tạm: {str(e)}")
            logger.error(traceback.format_exc())
            
            return False
    
    def cleanup_temp(self):
        """
        Dọn dẹp thư mục tạm
        
        Returns:
            dict: Thông tin về kết quả dọn dẹp
        """
        try:
            # Kiểm tra nếu thư mục tạm tồn tại
            if not os.path.exists(self.temp_dir):
                return {'success': True, 'message': 'Thư mục tạm chưa tồn tại'}
            
            # Tính kích thước trước khi dọn dẹp
            before_size = self._get_dir_size(self.temp_dir)
            
            # Xóa tất cả các file trong thư mục tạm
            files_removed = 0
            for item in os.listdir(self.temp_dir):
                item_path = os.path.join(self.temp_dir, item)
                try:
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                        files_removed += 1
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        files_removed += 1
                except Exception as e:
                    logger.error(f"Lỗi khi xóa {item_path}: {str(e)}")
            
            # Tính kích thước sau khi dọn dẹp
            after_size = self._get_dir_size(self.temp_dir)
            
            # Trả về thông tin về kết quả dọn dẹp
            return {
                'success': True,
                'files_removed': files_removed,
                'space_freed': before_size - after_size,
                'formatted_space_freed': self._format_size(before_size - after_size),
                'message': f"Đã dọn dẹp {files_removed} mục, giải phóng {self._format_size(before_size - after_size)}"
            }
        except Exception as e:
            logger.error(f"Lỗi khi dọn dẹp thư mục tạm: {str(e)}")
            logger.error(traceback.format_exc())
            
            return {
                'success': False,
                'files_removed': 0,
                'space_freed': 0,
                'formatted_space_freed': '0 B',
                'error': str(e),
                'message': f"Lỗi: {str(e)}"
            }
    
    def check_all(self):
        """
        Kiểm tra toàn bộ không gian lưu trữ và quyền truy cập
        
        Returns:
            dict: Kết quả kiểm tra
        """
        results = {
            'disk_space': self.check_space(),
            'app_size': self.get_app_size(),
            'write_permission': self.check_temp_write_permission(),
            'estimated_app_size': {
                'size': self.ESTIMATED_APP_SIZE,
                'formatted': self._format_size(self.ESTIMATED_APP_SIZE)
            }
        }
        
        # Kiểm tra xem ứng dụng có đủ không gian để hoạt động không
        results['has_sufficient_space'] = results['disk_space']['has_min_space']
        
        # Kiểm tra xem có đủ không gian cho ứng dụng phát triển không
        results['has_room_to_grow'] = results['disk_space']['free'] > (self.ESTIMATED_APP_SIZE * 10)
        
        return results


if __name__ == "__main__":
    # Mã kiểm thử
    logging.basicConfig(level=logging.DEBUG)
    
    checker = DiskSpaceChecker()
    print(f"Thông tin không gian đĩa:")
    disk_info = checker.check_space()
    print(f"  Tổng dung lượng: {disk_info['formatted']['total']}")
    print(f"  Đã sử dụng: {disk_info['formatted']['used']} ({disk_info['percent_used']}%)")
    print(f"  Còn trống: {disk_info['formatted']['free']} ({disk_info['percent_free']}%)")
    print(f"  Đủ không gian tối thiểu: {'Có' if disk_info['has_min_space'] else 'Không'}")
    print(f"  Đủ không gian đề xuất: {'Có' if disk_info['has_recommended_space'] else 'Không'}")
    
    print("\nKích thước ứng dụng:")
    app_size = checker.get_app_size()
    print(f"  Kích thước hiện tại: {app_size['formatted']}")
    
    print("\nQuyền ghi:")
    write_permission = checker.check_temp_write_permission()
    print(f"  Có quyền ghi vào thư mục tạm: {'Có' if write_permission else 'Không'}")
    
    print("\nDọn dẹp thư mục tạm:")
    cleanup_result = checker.cleanup_temp()
    print(f"  Kết quả: {cleanup_result['message']}")
