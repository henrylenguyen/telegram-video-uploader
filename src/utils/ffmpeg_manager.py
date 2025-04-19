"""
Module quản lý FFmpeg và đảm bảo FFmpeg có sẵn cho ứng dụng.
"""
import os
import sys
import subprocess
import logging
import urllib.request
import zipfile
import platform
import shutil
import time
import threading
from pathlib import Path
from datetime import timedelta

logger = logging.getLogger("FFmpegManager")

class FFmpegManager:
    """
    Quản lý việc tải và thiết lập FFmpeg cho ứng dụng.
    Đảm bảo FFmpeg luôn có sẵn dù người dùng không cài đặt.
    """
    
    # URL tải FFmpeg (Windows chọn phiên bản gpl để có thêm filters)
    FFMPEG_URLS = {
        'windows': "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
        'linux': "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz",
        'darwin': "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"  # macOS
    }
    
    def __init__(self, app_dir=None):
        """
        Khởi tạo FFmpegManager
        
        Args:
            app_dir (str): Thư mục ứng dụng chính (nếu None, sẽ sử dụng thư mục hiện tại)
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
        
        # Thư mục lưu trữ FFmpeg
        self.ffmpeg_dir = os.path.join(self.app_dir, 'ffmpeg')
        
        # Xác định đường dẫn FFmpeg và FFprobe
        self.ffmpeg_path = None
        self.ffprobe_path = None
        
        # Cờ trạng thái
        self.is_available = False
        self.is_downloading = False
        self.download_progress = 0
        self.download_status = "Chưa tải"
        
        # Thông tin về tốc độ tải
        self.download_speed = 0  # Bytes/giây
        self.estimated_time = "Đang tính..."  # Thời gian hoàn thành dự kiến
        self.total_size = 0  # Tổng kích thước file
        self.downloaded_size = 0  # Kích thước đã tải
        
        # Theo dõi thời gian tải
        self.last_update_time = 0
        self.last_download_size = 0
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(self.ffmpeg_dir, exist_ok=True)
        
        # Xác định ffmpeg đã có trong thư mục hay chưa
        self._check_bundled_ffmpeg()
    
    def _check_bundled_ffmpeg(self):
        """Kiểm tra ffmpeg đã được cài đặt trong thư mục ứng dụng chưa"""
        current_os = platform.system().lower()
        
        # Xác định đuôi file theo hệ điều hành
        exe_ext = ".exe" if current_os == "windows" else ""
        
        # Đường dẫn FFmpeg và FFprobe
        self.ffmpeg_path = os.path.join(self.ffmpeg_dir, f"ffmpeg{exe_ext}")
        self.ffprobe_path = os.path.join(self.ffmpeg_dir, f"ffprobe{exe_ext}")
        
        # Kiểm tra file có tồn tại không
        if os.path.exists(self.ffmpeg_path) and os.path.exists(self.ffprobe_path):
            logger.info(f"Đã tìm thấy FFmpeg trong thư mục ứng dụng: {self.ffmpeg_dir}")
            self.is_available = True
            return True
        
        return False
    
    def check_system_ffmpeg(self):
        """
        Kiểm tra FFmpeg đã được cài đặt trong hệ thống chưa
        
        Returns:
            bool: True nếu đã cài đặt
        """
        try:
            # Thử chạy lệnh ffmpeg
            proc = subprocess.run(
                ["ffmpeg", "-version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                check=False  # Không raises exception nếu lỗi
            )
            
            if proc.returncode == 0:
                logger.info("Đã tìm thấy FFmpeg trong hệ thống")
                self.is_available = True
                return True
            
            return False
        except Exception:
            return False
    
    def setup_ffmpeg(self):
        """
        Thiết lập FFmpeg, đảm bảo có sẵn để sử dụng bằng cách:
        1. Kiểm tra FFmpeg đã có trong ứng dụng chưa
        2. Kiểm tra FFmpeg đã cài trong hệ thống chưa
        3. Nếu không, tải FFmpeg về và cài đặt
        
        Returns:
            bool: True nếu thiết lập thành công
        """
        # Kiểm tra đã có trong thư mục ứng dụng chưa
        if self._check_bundled_ffmpeg():
            self._add_to_path()
            return True
        
        # Kiểm tra đã cài trong hệ thống chưa
        if self.check_system_ffmpeg():
            return True
        
        # Nếu không có, tải FFmpeg
        logger.info("Không tìm thấy FFmpeg, tiến hành tải về...")
        
        # Tải bất đồng bộ để không chặn giao diện
        download_thread = threading.Thread(target=self._download_ffmpeg)
        download_thread.daemon = True
        download_thread.start()
        
        return False
    
    def _format_size(self, size_bytes):
        """Định dạng kích thước file thành chuỗi dễ đọc"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.2f} GB"
    
    def _format_speed(self, speed_bytes):
        """Định dạng tốc độ tải thành chuỗi dễ đọc"""
        if speed_bytes < 1024:
            return f"{speed_bytes:.1f} B/s"
        elif speed_bytes < 1024 * 1024:
            return f"{speed_bytes/1024:.1f} KB/s"
        else:
            return f"{speed_bytes/(1024*1024):.1f} MB/s"
    
    def _format_time(self, seconds):
        """Định dạng thời gian thành chuỗi dễ đọc"""
        if seconds < 60:
            return f"{seconds:.0f} giây"
        elif seconds < 3600:
            return f"{seconds//60:.0f} phút {seconds%60:.0f} giây"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours:.0f} giờ {minutes:.0f} phút"
    
    def _download_ffmpeg(self):
        """Tải FFmpeg từ internet"""
        current_os = platform.system().lower()
        if current_os not in self.FFMPEG_URLS:
            logger.error(f"Không hỗ trợ hệ điều hành: {current_os}")
            self.download_status = f"Lỗi: Không hỗ trợ hệ điều hành {current_os}"
            return False
        
        url = self.FFMPEG_URLS[current_os]
        self.is_downloading = True
        self.download_status = "Đang chuẩn bị tải FFmpeg..."
        
        try:
            # Tạo thư mục tạm
            temp_dir = os.path.join(self.app_dir, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Tên file tải về
            file_ext = '.zip' if current_os in ['windows', 'darwin'] else '.tar.xz'
            download_file = os.path.join(temp_dir, f"ffmpeg{file_ext}")
            
            # Class để báo cáo tiến trình tải
            class DownloadProgressReporter:
                def __init__(self, manager):
                    self.manager = manager
                    self.manager.last_update_time = time.time()
                    self.manager.last_download_size = 0
                
                def __call__(self, block_num, block_size, total_size):
                    self.manager.total_size = total_size
                    downloaded = block_num * block_size
                    self.manager.downloaded_size = downloaded
                    
                    if total_size > 0:
                        # Tính phần trăm hoàn thành
                        percent = min(100, downloaded * 100 / total_size)
                        self.manager.download_progress = percent
                        
                        # Tính tốc độ tải
                        current_time = time.time()
                        time_diff = current_time - self.manager.last_update_time
                        
                        if time_diff >= 0.5:  # Cập nhật mỗi 0.5 giây
                            size_diff = downloaded - self.manager.last_download_size
                            
                            if time_diff > 0:
                                speed = size_diff / time_diff
                                self.manager.download_speed = speed
                                
                                # Tính thời gian còn lại
                                if speed > 0:
                                    remaining_bytes = total_size - downloaded
                                    est_time = remaining_bytes / speed
                                    self.manager.estimated_time = self.manager._format_time(est_time)
                                else:
                                    self.manager.estimated_time = "Đang tính..."
                            
                            # Cập nhật trạng thái
                            status = f"Đang tải: {percent:.1f}% - "
                            status += f"{self.manager._format_size(downloaded)}/{self.manager._format_size(total_size)} - "
                            status += f"{self.manager._format_speed(self.manager.download_speed)}"
                            
                            if percent < 100:
                                status += f" - Còn: {self.manager.estimated_time}"
                                
                            self.manager.download_status = status
                            
                            # Cập nhật các giá trị theo dõi
                            self.manager.last_update_time = current_time
                            self.manager.last_download_size = downloaded
            
            # Tải file
            progress_reporter = DownloadProgressReporter(self)
            logger.info(f"Bắt đầu tải FFmpeg từ {url}")
            
            self.download_status = "Đang tải FFmpeg..."
            urllib.request.urlretrieve(url, download_file, progress_reporter)
            
            # Giải nén file
            self.download_status = "Đang giải nén FFmpeg..."
            if current_os == 'windows' or current_os == 'darwin':
                with zipfile.ZipFile(download_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
            else:  # Linux
                subprocess.run(['tar', '-xf', download_file, '-C', temp_dir], check=True)
            
            # Dọn dẹp thư mục ffmpeg cũ nếu có
            if os.path.exists(self.ffmpeg_dir):
                shutil.rmtree(self.ffmpeg_dir)
            os.makedirs(self.ffmpeg_dir, exist_ok=True)
            
            # Di chuyển file ffmpeg và ffprobe vào thư mục ứng dụng
            if current_os == 'windows':
                # Tìm thư mục bin sau khi giải nén
                for root, dirs, files in os.walk(temp_dir):
                    if 'bin' in dirs:
                        bin_dir = os.path.join(root, 'bin')
                        
                        # Tìm ffmpeg.exe và ffprobe.exe
                        for file in os.listdir(bin_dir):
                            if file.startswith('ffmpeg') or file.startswith('ffprobe'):
                                src_file = os.path.join(bin_dir, file)
                                dst_file = os.path.join(self.ffmpeg_dir, file)
                                shutil.copy2(src_file, dst_file)
                        break
            elif current_os == 'darwin':
                # macOS: Tìm ffmpeg và ffprobe
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file == 'ffmpeg' or file == 'ffprobe':
                            src_file = os.path.join(root, file)
                            dst_file = os.path.join(self.ffmpeg_dir, file)
                            shutil.copy2(src_file, dst_file)
                            os.chmod(dst_file, 0o755)  # Thêm quyền thực thi
            else:
                # Linux: Tìm ffmpeg và ffprobe
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file == 'ffmpeg' or file == 'ffprobe':
                            src_file = os.path.join(root, file)
                            dst_file = os.path.join(self.ffmpeg_dir, file)
                            shutil.copy2(src_file, dst_file)
                            os.chmod(dst_file, 0o755)  # Thêm quyền thực thi
            
            # Dọn dẹp thư mục tạm
            shutil.rmtree(temp_dir)
            
            # Kiểm tra xem đã có FFmpeg chưa
            if self._check_bundled_ffmpeg():
                self._add_to_path()
                self.download_status = "Đã tải và cài đặt FFmpeg thành công"
                logger.info("Đã tải và cài đặt FFmpeg thành công")
                return True
            else:
                self.download_status = "Lỗi không tìm thấy FFmpeg sau khi tải"
                logger.error("Lỗi không tìm thấy FFmpeg sau khi tải")
                return False
                
        except Exception as e:
            self.is_downloading = False
            self.download_status = f"Lỗi khi tải FFmpeg: {str(e)}"
            logger.error(f"Lỗi khi tải FFmpeg: {str(e)}")
            return False
    
    def _add_to_path(self):
        """Thêm thư mục FFmpeg vào PATH"""
        if self.is_available and os.path.exists(self.ffmpeg_dir):
            # Thêm vào PATH
            os.environ["PATH"] = self.ffmpeg_dir + os.pathsep + os.environ["PATH"]
            logger.info(f"Đã thêm {self.ffmpeg_dir} vào PATH")
    
    def wait_for_download(self, timeout=30):
        """
        Đợi cho đến khi tải xong FFmpeg
        
        Args:
            timeout (int): Thời gian tối đa đợi (giây)
            
        Returns:
            bool: True nếu tải thành công
        """
        start_time = time.time()
        while self.is_downloading and time.time() - start_time < timeout:
            time.sleep(0.5)
        
        return self.is_available
    
    def get_ffmpeg_path(self):
        """
        Lấy đường dẫn đến ffmpeg
        
        Returns:
            str: Đường dẫn đến ffmpeg
        """
        if self.is_available:
            if os.path.exists(self.ffmpeg_path):
                return self.ffmpeg_path
            else:
                return "ffmpeg"  # Sử dụng ffmpeg từ PATH
        
        return None
    
    def get_ffprobe_path(self):
        """
        Lấy đường dẫn đến ffprobe
        
        Returns:
            str: Đường dẫn đến ffprobe
        """
        if self.is_available:
            if os.path.exists(self.ffprobe_path):
                return self.ffprobe_path
            else:
                return "ffprobe"  # Sử dụng ffprobe từ PATH
        
        return None
    
    def get_download_status(self):
        """
        Lấy trạng thái tải FFmpeg
        
        Returns:
            tuple: (progress, status, is_downloading)
        """
        return (self.download_progress, self.download_status, self.is_downloading)

if __name__ == "__main__":
    # Mã kiểm thử
    logging.basicConfig(level=logging.DEBUG)
    
    manager = FFmpegManager()
    print(f"Kiểm tra FFmpeg trong ứng dụng: {manager._check_bundled_ffmpeg()}")
    print(f"Kiểm tra FFmpeg trong hệ thống: {manager.check_system_ffmpeg()}")
    
    if not manager.is_available:
        print("Bắt đầu tải FFmpeg...")
        manager.setup_ffmpeg()
        
        # Đợi tải xong
        while manager.is_downloading:
            progress, status, _ = manager.get_download_status()
            print(f"Tiến trình: {progress:.1f}% - {status}")
            time.sleep(1)
        
        print(f"Kết quả: {manager.get_download_status()[1]}")
    
    print(f"FFmpeg path: {manager.get_ffmpeg_path()}")
    print(f"FFprobe path: {manager.get_ffprobe_path()}")