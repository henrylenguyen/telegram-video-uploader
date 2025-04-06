"""
Module xử lý chia nhỏ video lớn thành các phần nhỏ hơn hoặc nén video.
"""
import os
import subprocess
import logging
import math
import tempfile
import shutil
import sys
import configparser
from datetime import datetime

logger = logging.getLogger("VideoSplitter")

class VideoSplitter:
    """
    Lớp xử lý việc chia nhỏ hoặc nén video lớn để phù hợp với giới hạn Telegram.
    Cung cấp hai cách tiếp cận:
    1. Chia video lớn thành nhiều phần nhỏ
    2. Nén video để giảm kích thước
    """
    
    def __init__(self, max_size_mb=49, temp_dir=None):
        """
        Khởi tạo VideoSplitter
        
        Args:
            max_size_mb (int): Kích thước tối đa (MB) cho mỗi phần video
            temp_dir (str): Thư mục lưu trữ tạm thời (mặc định là None -> sử dụng thư mục tạm hệ thống)
        """
        self.max_size_mb = max_size_mb
        self.temp_dir = temp_dir or tempfile.gettempdir()
        
        # Tạo thư mục con trong thư mục tạm để lưu các phần video
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.work_dir = os.path.join(self.temp_dir, f"telegram_video_splitter_{timestamp}")
        
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)
            
        logger.info(f"VideoSplitter đã được khởi tạo với kích thước tối đa {max_size_mb}MB mỗi phần")
        logger.info(f"Thư mục làm việc: {self.work_dir}")

        # Kiểm tra và thiết lập đường dẫn FFmpeg
        self._setup_ffmpeg_path()
    
    def __del__(self):
        """Xóa thư mục tạm khi đối tượng bị hủy"""
        try:
            if os.path.exists(self.work_dir):
                shutil.rmtree(self.work_dir)
                logger.debug(f"Đã xóa thư mục tạm: {self.work_dir}")
        except Exception as e:
            logger.error(f"Lỗi khi xóa thư mục tạm: {e}")
    
    def _setup_ffmpeg_path(self):
        """Cài đặt đường dẫn FFmpeg cho ứng dụng đóng gói"""
        try:
            # Kiểm tra xem FFmpeg có sẵn trong PATH không
            if self._check_ffmpeg():
                return

            # Nếu không có trong PATH, thử tìm trong thư mục ứng dụng
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Nếu đóng gói với PyInstaller
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
                
            ffmpeg_dir = os.path.join(base_dir, 'ffmpeg')
            
            if os.path.exists(ffmpeg_dir):
                logger.info(f"Tìm thấy thư mục FFmpeg trong ứng dụng: {ffmpeg_dir}")
                
                # Thêm vào PATH
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
                logger.info("Đã thêm FFmpeg vào PATH")
                
                # Kiểm tra lại
                if self._check_ffmpeg():
                    logger.info("FFmpeg đã được thiết lập thành công")
                    return
            
            logger.warning("Không tìm thấy FFmpeg. Một số tính năng xử lý video lớn có thể không hoạt động.")
            
        except Exception as e:
            logger.error(f"Lỗi khi thiết lập đường dẫn FFmpeg: {e}")
    
    def _check_ffmpeg(self):
        """
        Kiểm tra xem FFmpeg đã được cài đặt chưa
        
        Returns:
            bool: True nếu FFmpeg đã được cài đặt
        """
        try:
            subprocess.run(
                ["ffmpeg", "-version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                check=True
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error("FFmpeg chưa được cài đặt hoặc không tìm thấy trong PATH.")
            return False
    
    def get_video_duration(self, video_path):
        """
        Lấy thời lượng của video sử dụng FFmpeg
        
        Args:
            video_path (str): Đường dẫn đến file video
            
        Returns:
            float: Thời lượng video tính bằng giây hoặc None nếu có lỗi
        """
        if not self._check_ffmpeg():
            return None
            
        try:
            cmd = [
                "ffprobe", 
                "-v", "error", 
                "-show_entries", "format=duration", 
                "-of", "default=noprint_wrappers=1:nokey=1", 
                video_path
            ]
            
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            duration = float(result.stdout.strip())
            return duration
        except Exception as e:
            logger.error(f"Lỗi khi lấy thời lượng video: {e}")
            return None
    
    def get_config_use_telethon(self):
        """
        Đọc cấu hình use_telethon trực tiếp từ file config.ini

        Returns:
            bool: True nếu use_telethon được bật trong config
        """
        try:
            # Đầu tiên, thử truy cập qua app toàn cục
            import sys
            for module_name in ['__main__', 'app']:
                if module_name in sys.modules:
                    main_module = sys.modules[module_name]
                    if hasattr(main_module, 'app'):
                        app = main_module.app
                        if hasattr(app, 'config'):
                            try:
                                use_telethon = app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
                                logger.info(f"Đọc use_telethon={use_telethon} từ app.config")
                                return use_telethon
                            except Exception:
                                pass
            
            # Nếu không thể truy cập qua app, đọc trực tiếp từ file config.ini
            config = configparser.ConfigParser()
            
            # Tìm file config.ini trong các vị trí khác nhau
            possible_paths = [
                'config.ini',
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config.ini'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.ini'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.ini')
            ]
            
            for config_path in possible_paths:
                if os.path.exists(config_path):
                    config.read(config_path)
                    if 'TELETHON' in config and 'use_telethon' in config['TELETHON']:
                        use_telethon_str = config['TELETHON']['use_telethon'].lower()
                        use_telethon = use_telethon_str == 'true' or use_telethon_str == '1'
                        logger.info(f"Đọc use_telethon={use_telethon} từ file config.ini tại {config_path}")
                        return use_telethon
            
            logger.warning("Không tìm thấy cấu hình use_telethon, mặc định = False")
            return False
        except Exception as e:
            logger.error(f"Lỗi khi đọc cấu hình use_telethon: {str(e)}")
            return False
    
    def split_video(self, video_path, output_dir=None):
        """
        Chia nhỏ video thành nhiều phần, mỗi phần dưới kích thước tối đa
        
        Args:
            video_path (str): Đường dẫn đến file video
            output_dir (str, optional): Thư mục đầu ra. Nếu không cung cấp, sử dụng thư mục làm việc mặc định
                
        Returns:
            list: Danh sách đường dẫn đến các phần video, hoặc [] nếu có lỗi
        """
        # Đầu tiên, kiểm tra nếu file không tồn tại
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            logger.error(f"Video không tồn tại: {video_path}")
            return []
        
        # Lấy thông tin video
        video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        video_name = os.path.basename(video_path)
        
        # KIỂM TRA CHẶT CHẼ: Nếu video lớn và use_telethon = True, không cho phép chia nhỏ
        if video_size_mb > 50:
            use_telethon = self.get_config_use_telethon()
            if use_telethon:
                logger.error(f"⛔ Không thể chia nhỏ video {video_name} ({video_size_mb:.2f} MB) khi use_telethon=True")
                
                # Hiển thị thông báo lỗi
                try:
                    from tkinter import messagebox
                    messagebox.showerror(
                        "Lỗi - Không thể chia nhỏ video", 
                        f"Video '{video_name}' ({video_size_mb:.2f} MB) không thể được chia nhỏ khi bật tùy chọn 'Sử dụng Telethon API'.\n\n"
                        f"Vui lòng đảm bảo đã đăng nhập Telethon API trong tab Cài đặt, hoặc tắt tùy chọn này."
                    )
                except Exception as e:
                    logger.error(f"Không thể hiển thị thông báo lỗi: {str(e)}")
                
                return []  # Trả về danh sách trống để báo hiệu lỗi
        
        # Nếu FFmpeg không sẵn sàng, không thể chia nhỏ
        if not self._check_ffmpeg():
            return []
            
        try:
            # Cập nhật thư mục làm việc nếu output_dir được chỉ định
            work_dir = output_dir if output_dir else self.work_dir
            
            # Đảm bảo thư mục tồn tại
            os.makedirs(work_dir, exist_ok=True)
            
            # Kiểm tra kích thước file
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # Kích thước tính bằng MB
            
            # Nếu file đã nhỏ hơn giới hạn, trả về file gốc
            if file_size <= self.max_size_mb:
                logger.info(f"Video {os.path.basename(video_path)} đã nhỏ hơn giới hạn {self.max_size_mb}MB")
                return [video_path]
                
            # Lấy thời lượng video
            duration = self.get_video_duration(video_path)
            if not duration:
                logger.error(f"Không thể lấy thời lượng của video {os.path.basename(video_path)}")
                return []
                
            # Tính số phần cần chia
            num_parts = math.ceil(file_size / self.max_size_mb)
            # Tính thời lượng mỗi phần (giây)
            part_duration = duration / num_parts
            
            logger.info(f"Chia video {os.path.basename(video_path)} thành {num_parts} phần")
            logger.info(f"Kích thước gốc: {file_size:.2f}MB, Thời lượng: {duration:.2f}s")
            logger.info(f"Thời lượng mỗi phần: {part_duration:.2f}s")
            
            # Tạo phần đầu ra
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_paths = []
            
            for i in range(num_parts):
                start_time = i * part_duration
                # Đường dẫn đầu ra - sử dụng work_dir cập nhật
                output_path = os.path.join(work_dir, f"{base_name}_part{i+1:03d}.mp4")
                
                # Command để cắt video thành phần
                cmd = [
                    "ffmpeg",
                    "-y",  # Ghi đè file nếu đã tồn tại
                    "-i", video_path,
                    "-ss", str(start_time),  # Thời gian bắt đầu
                    "-t", str(part_duration),  # Thời lượng đoạn cắt
                    "-c", "copy",  # Sao chép codec không mã hóa lại
                    output_path
                ]
                
                # Thực thi lệnh
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Kiểm tra xem file đã được tạo chưa
                if os.path.exists(output_path):
                    output_size = os.path.getsize(output_path) / (1024 * 1024)
                    logger.info(f"Đã tạo phần {i+1}/{num_parts}: {os.path.basename(output_path)} ({output_size:.2f}MB)")
                    output_paths.append(output_path)
                else:
                    logger.error(f"Không thể tạo phần {i+1}/{num_parts} của video")
            
            return output_paths
            
        except Exception as e:
            logger.error(f"Lỗi khi chia nhỏ video {os.path.basename(video_path)}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
            
    def compress_video(self, video_path, target_size_mb=None):
        """
        Nén video để giảm kích thước
        
        Args:
            video_path (str): Đường dẫn đến file video
            target_size_mb (int): Kích thước đích tính bằng MB (mặc định None -> sử dụng max_size_mb)
            
        Returns:
            str: Đường dẫn đến video đã nén hoặc None nếu có lỗi
        """
        if not self._check_ffmpeg():
            return None
            
        target_size = target_size_mb or self.max_size_mb
        
        try:
            # Kiểm tra kích thước file
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # Kích thước tính bằng MB
            
            # Nếu file đã nhỏ hơn giới hạn, trả về file gốc
            if file_size <= target_size:
                logger.info(f"Video {os.path.basename(video_path)} đã nhỏ hơn giới hạn {target_size}MB")
                return video_path
                
            # Lấy thời lượng video
            duration = self.get_video_duration(video_path)
            if not duration:
                logger.error(f"Không thể lấy thời lượng của video {os.path.basename(video_path)}")
                return None
                
            # Tính bitrate cần thiết
            # Công thức: bitrate (kb/s) = target_size_kb / duration_seconds * 8
            target_bitrate = int((target_size * 1024) / duration * 8 * 0.95)  # Giảm 5% để đảm bảo dưới giới hạn
            
            # Đường dẫn đầu ra
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.work_dir, f"{base_name}_compressed.mp4")
            
            logger.info(f"Nén video {os.path.basename(video_path)}")
            logger.info(f"Kích thước gốc: {file_size:.2f}MB, Kích thước đích: {target_size}MB")
            logger.info(f"Bitrate mục tiêu: {target_bitrate}kb/s")
            
            # Command để nén video
            cmd = [
                "ffmpeg",
                "-y",
                "-i", video_path,
                "-c:v", "libx264",
                "-b:v", f"{target_bitrate}k",
                "-preset", "medium",  # Cân bằng giữa tốc độ nén và chất lượng
                "-c:a", "aac",
                "-b:a", "128k",
                output_path
            ]
            
            # Thực thi lệnh
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Kiểm tra xem file đã được tạo chưa
            if os.path.exists(output_path):
                output_size = os.path.getsize(output_path) / (1024 * 1024)
                logger.info(f"Đã nén video: {os.path.basename(output_path)} ({output_size:.2f}MB)")
                
                if output_size > target_size:
                    logger.warning(f"Video vẫn lớn hơn giới hạn ({output_size:.2f}MB > {target_size}MB)")
                    
                return output_path
            else:
                logger.error(f"Không thể nén video {os.path.basename(video_path)}")
                return None
                
        except Exception as e:
            logger.error(f"Lỗi khi nén video {os.path.basename(video_path)}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
if __name__ == "__main__":
    # Mã kiểm thử
    logging.basicConfig(level=logging.DEBUG)
    
    splitter = VideoSplitter(max_size_mb=20)
    test_video = "path/to/test/large_video.mp4"
    
    if os.path.exists(test_video):
        # Chia nhỏ video
        parts = splitter.split_video(test_video)
        print(f"Đã chia thành {len(parts)} phần: {parts}")
        
        # Nén video
        compressed = splitter.compress_video(test_video)
        print(f"Đã nén video: {compressed}")
    else:
        print(f"Video kiểm thử không tìm thấy: {test_video}")