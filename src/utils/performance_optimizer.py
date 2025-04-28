"""
Module tối ưu hóa hiệu suất ứng dụng.
"""
import os
import gc
import sys
import time
import shutil
import psutil
import logging
import traceback
import threading
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """
    Lớp tối ưu hóa hiệu suất ứng dụng
    """
    
    def __init__(self, app_dir=None):
        """
        Khởi tạo PerformanceOptimizer
        
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
        
        # Đường dẫn tới thư mục cache
        self.cache_dir = os.path.join(self.app_dir, 'cache')
        
        # Đường dẫn tới thư mục temp
        self.temp_dir = os.path.join(self.app_dir, 'temp')
        
        # Đường dẫn tới thư mục logs
        self.logs_dir = os.path.join(self.app_dir, 'logs')
        
        # Kích thước tối đa của thư mục cache (100MB)
        self.max_cache_size = 100 * 1024 * 1024
        
        # Số ngày để giữ file logs
        self.log_retention_days = 7
        
        # Current process
        self.process = psutil.Process(os.getpid())
    
    def optimize_memory(self):
        """
        Tối ưu hóa sử dụng bộ nhớ
        
        Returns:
            dict: Thông tin về bộ nhớ trước và sau khi tối ưu hóa
        """
        try:
            # Lấy thông tin bộ nhớ trước khi tối ưu hóa
            before_memory = self.process.memory_info().rss
            
            # Chạy garbage collector
            collected = gc.collect()
            
            # Lấy thông tin bộ nhớ sau khi tối ưu hóa
            after_memory = self.process.memory_info().rss
            
            # Tính toán bộ nhớ đã giải phóng
            memory_freed = before_memory - after_memory
            
            # Trả về thông tin
            return {
                'before': {
                    'memory_usage': before_memory,
                    'formatted': self._format_size(before_memory)
                },
                'after': {
                    'memory_usage': after_memory,
                    'formatted': self._format_size(after_memory)
                },
                'freed': {
                    'memory': memory_freed,
                    'formatted': self._format_size(memory_freed),
                    'percentage': round((memory_freed / before_memory) * 100, 2) if before_memory > 0 else 0
                },
                'objects_collected': collected,
                'success': True
            }
        except Exception as e:
            logger.error(f"Lỗi khi tối ưu hóa bộ nhớ: {str(e)}")
            logger.error(traceback.format_exc())
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_size(self, size_bytes):
        """Định dạng kích thước thành chuỗi dễ đọc"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def cleanup_cache(self):
        """
        Dọn dẹp thư mục cache
        
        Returns:
            dict: Thông tin về kết quả dọn dẹp
        """
        try:
            # Kiểm tra nếu thư mục cache tồn tại
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir, exist_ok=True)
                return {'success': True, 'message': 'Thư mục cache mới được tạo'}
            
            # Tính kích thước trước khi dọn dẹp
            before_size = self._get_dir_size(self.cache_dir)
            
            # Nếu kích thước cache nhỏ hơn kích thước tối đa, không cần dọn dẹp
            if before_size < self.max_cache_size:
                return {
                    'success': True,
                    'cache_size': {
                        'before': before_size,
                        'formatted': self._format_size(before_size)
                    },
                    'message': f"Cache đang ở mức cho phép ({self._format_size(before_size)})"
                }
            
            # Lấy danh sách các file theo thời gian sửa đổi
            files_info = []
            for root, _, files in os.walk(self.cache_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(file_path)
                        size = os.path.getsize(file_path)
                        files_info.append((file_path, mtime, size))
                    except (FileNotFoundError, PermissionError):
                        pass
            
            # Sắp xếp theo thời gian sửa đổi (cũ nhất trước)
            files_info.sort(key=lambda x: x[1])
            
            # Xóa các file cũ nhất cho đến khi kích thước cache dưới ngưỡng cho phép
            files_removed = 0
            space_freed = 0
            current_size = before_size
            
            for file_path, _, size in files_info:
                if current_size <= self.max_cache_size * 0.8:  # Giữ cache dưới 80% ngưỡng
                    break
                
                try:
                    os.remove(file_path)
                    files_removed += 1
                    space_freed += size
                    current_size -= size
                except (FileNotFoundError, PermissionError) as e:
                    logger.warning(f"Không thể xóa {file_path}: {str(e)}")
            
            # Tính kích thước sau khi dọn dẹp
            after_size = self._get_dir_size(self.cache_dir)
            
            # Trả về thông tin về kết quả dọn dẹp
            return {
                'success': True,
                'files_removed': files_removed,
                'space_freed': space_freed,
                'formatted_space_freed': self._format_size(space_freed),
                'cache_size': {
                    'before': before_size,
                    'after': after_size,
                    'formatted_before': self._format_size(before_size),
                    'formatted_after': self._format_size(after_size)
                },
                'message': f"Đã dọn dẹp {files_removed} file, giải phóng {self._format_size(space_freed)}"
            }
        except Exception as e:
            logger.error(f"Lỗi khi dọn dẹp cache: {str(e)}")
            logger.error(traceback.format_exc())
            
            return {
                'success': False,
                'error': str(e),
                'message': f"Lỗi: {str(e)}"
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
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (FileNotFoundError, PermissionError):
                    pass
        return total_size
    
    def cleanup_logs(self):
        """
        Dọn dẹp các file log cũ
        
        Returns:
            dict: Thông tin về kết quả dọn dẹp
        """
        try:
            # Kiểm tra nếu thư mục logs tồn tại
            if not os.path.exists(self.logs_dir):
                os.makedirs(self.logs_dir, exist_ok=True)
                return {'success': True, 'message': 'Thư mục logs mới được tạo'}
            
            # Tính kích thước trước khi dọn dẹp
            before_size = self._get_dir_size(self.logs_dir)
            
            # Thời gian giới hạn (logs cũ hơn thời gian này sẽ bị xóa)
            cutoff_time = datetime.now() - timedelta(days=self.log_retention_days)
            
            # Xóa các file log cũ
            files_removed = 0
            space_freed = 0
            
            for file in os.listdir(self.logs_dir):
                file_path = os.path.join(self.logs_dir, file)
                if os.path.isfile(file_path) and file.lower().endswith('.log'):
                    try:
                        # Lấy thời gian sửa đổi của file
                        mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        # Nếu file cũ hơn thời gian giới hạn, xóa nó
                        if mtime < cutoff_time:
                            size = os.path.getsize(file_path)
                            os.remove(file_path)
                            files_removed += 1
                            space_freed += size
                    except (FileNotFoundError, PermissionError) as e:
                        logger.warning(f"Không thể xóa {file_path}: {str(e)}")
            
            # Tính kích thước sau khi dọn dẹp
            after_size = self._get_dir_size(self.logs_dir)
            
            # Trả về thông tin về kết quả dọn dẹp
            return {
                'success': True,
                'files_removed': files_removed,
                'space_freed': space_freed,
                'formatted_space_freed': self._format_size(space_freed),
                'logs_size': {
                    'before': before_size,
                    'after': after_size,
                    'formatted_before': self._format_size(before_size),
                    'formatted_after': self._format_size(after_size)
                },
                'message': f"Đã dọn dẹp {files_removed} file log, giải phóng {self._format_size(space_freed)}"
            }
        except Exception as e:
            logger.error(f"Lỗi khi dọn dẹp logs: {str(e)}")
            logger.error(traceback.format_exc())
            
            return {
                'success': False,
                'error': str(e),
                'message': f"Lỗi: {str(e)}"
            }
    
    def cleanup_temp(self):
        """
        Dọn dẹp thư mục tạm
        
        Returns:
            dict: Thông tin về kết quả dọn dẹp
        """
        try:
            # Kiểm tra nếu thư mục tạm tồn tại
            if not os.path.exists(self.temp_dir):
                os.makedirs(self.temp_dir, exist_ok=True)
                return {'success': True, 'message': 'Thư mục tạm mới được tạo'}
            
            # Tính kích thước trước khi dọn dẹp
            before_size = self._get_dir_size(self.temp_dir)
            
            # Xóa tất cả các file trong thư mục tạm
            files_removed = 0
            space_freed = 0
            
            for item in os.listdir(self.temp_dir):
                item_path = os.path.join(self.temp_dir, item)
                try:
                    if os.path.isfile(item_path):
                        size = os.path.getsize(item_path)
                        os.unlink(item_path)
                        files_removed += 1
                        space_freed += size
                    elif os.path.isdir(item_path):
                        dir_size = self._get_dir_size(item_path)
                        shutil.rmtree(item_path)
                        files_removed += 1
                        space_freed += dir_size
                except (FileNotFoundError, PermissionError) as e:
                    logger.warning(f"Không thể xóa {item_path}: {str(e)}")
            
            # Tính kích thước sau khi dọn dẹp
            after_size = self._get_dir_size(self.temp_dir)
            
            # Trả về thông tin về kết quả dọn dẹp
            return {
                'success': True,
                'files_removed': files_removed,
                'space_freed': space_freed,
                'formatted_space_freed': self._format_size(space_freed),
                'temp_size': {
                    'before': before_size,
                    'after': after_size,
                    'formatted_before': self._format_size(before_size),
                    'formatted_after': self._format_size(after_size)
                },
                'message': f"Đã dọn dẹp {files_removed} mục trong thư mục tạm, giải phóng {self._format_size(space_freed)}"
            }
        except Exception as e:
            logger.error(f"Lỗi khi dọn dẹp thư mục tạm: {str(e)}")
            logger.error(traceback.format_exc())
            
            return {
                'success': False,
                'error': str(e),
                'message': f"Lỗi: {str(e)}"
            }
    
    def optimize_all(self):
        """
        Thực hiện tất cả các tối ưu hóa
        
        Returns:
            dict: Thông tin về kết quả tối ưu hóa
        """
        try:
            # Dọn dẹp cache
            cache_result = self.cleanup_cache()
            
            # Dọn dẹp logs
            logs_result = self.cleanup_logs()
            
            # Dọn dẹp temp
            temp_result = self.cleanup_temp()
            
            # Tối ưu hóa bộ nhớ
            memory_result = self.optimize_memory()
            
            # Tính tổng không gian đã giải phóng
            total_space_freed = 0
            if cache_result['success']:
                total_space_freed += cache_result.get('space_freed', 0)
            
            if logs_result['success']:
                total_space_freed += logs_result.get('space_freed', 0)
            
            if temp_result['success']:
                total_space_freed += temp_result.get('space_freed', 0)
            
            # Trả về thông tin tổng hợp
            return {
                'success': True,
                'cache': cache_result,
                'logs': logs_result,
                'temp': temp_result,
                'memory': memory_result,
                'total_space_freed': {
                    'size': total_space_freed,
                    'formatted': self._format_size(total_space_freed)
                },
                'message': f"Đã tối ưu hóa hiệu suất, giải phóng tổng cộng {self._format_size(total_space_freed)}"
            }
        except Exception as e:
            logger.error(f"Lỗi khi tối ưu hóa hiệu suất: {str(e)}")
            logger.error(traceback.format_exc())
            
            return {
                'success': False,
                'error': str(e),
                'message': f"Lỗi khi tối ưu hóa hiệu suất: {str(e)}"
            }
    
    def optimize_async(self, callback=None):
        """
        Thực hiện tối ưu hóa trong một thread riêng
        
        Args:
            callback (callable, optional): Hàm được gọi khi tối ưu hóa hoàn tất
        """
        def _optimize_and_callback():
            try:
                result = self.optimize_all()
                
                if callback:
                    callback(result)
            except Exception as e:
                logger.error(f"Lỗi trong thread tối ưu hóa: {str(e)}")
                logger.error(traceback.format_exc())
                
                if callback:
                    callback({
                        'success': False,
                        'error': f"Lỗi trong thread: {str(e)}",
                        'message': f"Lỗi khi tối ưu hóa hiệu suất: {str(e)}"
                    })
        
        # Tạo và bắt đầu thread tối ưu hóa
        thread = threading.Thread(target=_optimize_and_callback)
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    # Mã kiểm thử
    logging.basicConfig(level=logging.DEBUG)
    
    optimizer = PerformanceOptimizer()
    
    print("\nTối ưu hóa bộ nhớ:")
    memory_result = optimizer.optimize_memory()
    if memory_result['success']:
        print(f"  Bộ nhớ trước khi tối ưu: {memory_result['before']['formatted']}")
        print(f"  Bộ nhớ sau khi tối ưu: {memory_result['after']['formatted']}")
        print(f"  Bộ nhớ đã giải phóng: {memory_result['freed']['formatted']} ({memory_result['freed']['percentage']}%)")
        print(f"  Đối tượng đã thu gom: {memory_result['objects_collected']}")
    else:
        print(f"  Lỗi: {memory_result.get('error', 'Unknown error')}")
    
    print("\nDọn dẹp cache:")
    cache_result = optimizer.cleanup_cache()
    if cache_result['success']:
        print(f"  {cache_result['message']}")
        if 'cache_size' in cache_result:
            print(f"  Kích thước cache trước: {cache_result['cache_size']['formatted_before']}")
            print(f"  Kích thước cache sau: {cache_result['cache_size']['formatted_after']}")
    else:
        print(f"  Lỗi: {cache_result.get('error', 'Unknown error')}")
    
    print("\nDọn dẹp logs:")
    logs_result = optimizer.cleanup_logs()
    if logs_result['success']:
        print(f"  {logs_result['message']}")
        if 'logs_size' in logs_result:
            print(f"  Kích thước logs trước: {logs_result['logs_size']['formatted_before']}")
            print(f"  Kích thước logs sau: {logs_result['logs_size']['formatted_after']}")
    else:
        print(f"  Lỗi: {logs_result.get('error', 'Unknown error')}")
    
    print("\nDọn dẹp thư mục tạm:")
    temp_result = optimizer.cleanup_temp()
    if temp_result['success']:
        print(f"  {temp_result['message']}")
        if 'temp_size' in temp_result:
            print(f"  Kích thước temp trước: {temp_result['temp_size']['formatted_before']}")
            print(f"  Kích thước temp sau: {temp_result['temp_size']['formatted_after']}")
    else:
        print(f"  Lỗi: {temp_result.get('error', 'Unknown error')}")
