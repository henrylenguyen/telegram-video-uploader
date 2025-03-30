"""
Module theo dõi thư mục và tự động tải video lên Telegram.
"""
import os
import time
import logging
import threading
from queue import Queue, Empty
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

logger = logging.getLogger("AutoUploader")

class FileWatcher:
    """
    Theo dõi thư mục để phát hiện file mới và thay đổi
    """
    def __init__(self, folder_path, extensions=None, callback=None, check_interval=60):
        """
        Khởi tạo FileWatcher
        
        Args:
            folder_path (str): Đường dẫn thư mục cần theo dõi
            extensions (list): Danh sách phần mở rộng file cần theo dõi (mặc định None -> theo dõi tất cả)
            callback (function): Hàm callback được gọi khi phát hiện file mới
            check_interval (int): Thời gian kiểm tra định kỳ (giây)
        """
        self.folder_path = folder_path
        self.extensions = extensions if extensions else []
        self.callback = callback
        self.check_interval = check_interval
        self.running = False
        self.watcher_thread = None
        self.watched_files = {}  # Dict lưu trạng thái các file đã biết
        
    def is_valid_file(self, file_path):
        """
        Kiểm tra xem file có đúng định dạng cần theo dõi không
        
        Args:
            file_path (str): Đường dẫn đến file cần kiểm tra
            
        Returns:
            bool: True nếu file cần theo dõi
        """
        if not os.path.isfile(file_path):
            return False
            
        if not self.extensions:  # Nếu không chỉ định phần mở rộng -> theo dõi tất cả
            return True
            
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.extensions
    
    def scan_folder(self):
        """
        Quét thư mục để tìm file mới và thay đổi
        
        Returns:
            list: Danh sách các file mới tìm thấy
        """
        if not os.path.exists(self.folder_path) or not os.path.isdir(self.folder_path):
            logger.error(f"Thư mục không tồn tại: {self.folder_path}")
            return []
            
        current_files = {}
        new_files = []
        
        try:
            # Quét thư mục
            for file_name in os.listdir(self.folder_path):
                file_path = os.path.join(self.folder_path, file_name)
                
                if self.is_valid_file(file_path):
                    # Lấy thông tin file
                    file_stat = os.stat(file_path)
                    file_size = file_stat.st_size
                    file_mtime = file_stat.st_mtime
                    
                    # Lưu thông tin file hiện tại
                    current_files[file_path] = {
                        'size': file_size,
                        'mtime': file_mtime
                    }
                    
                    # Kiểm tra xem file đã tồn tại trong danh sách đã biết chưa
                    if file_path not in self.watched_files:
                        logger.info(f"Phát hiện file mới: {file_name}")
                        new_files.append(file_path)
                    else:
                        # Kiểm tra xem file có thay đổi không
                        old_size = self.watched_files[file_path]['size']
                        old_mtime = self.watched_files[file_path]['mtime']
                        
                        if file_size != old_size or file_mtime != old_mtime:
                            logger.info(f"Phát hiện file thay đổi: {file_name}")
                            new_files.append(file_path)
            
            # Cập nhật danh sách file đã biết
            self.watched_files = current_files
            
            return new_files
            
        except Exception as e:
            logger.error(f"Lỗi khi quét thư mục {self.folder_path}: {str(e)}")
            return []
    
    def start(self):
        """
        Bắt đầu theo dõi thư mục
        """
        if self.running:
            return
            
        self.running = True
        self.watcher_thread = threading.Thread(target=self._watch_folder)
        self.watcher_thread.daemon = True
        self.watcher_thread.start()
        
        logger.info(f"Bắt đầu theo dõi thư mục: {self.folder_path}")
    
    def stop(self):
        """
        Dừng theo dõi thư mục
        """
        self.running = False
        if self.watcher_thread and self.watcher_thread.is_alive():
            self.watcher_thread.join(timeout=1.0)
            
        logger.info(f"Đã dừng theo dõi thư mục: {self.folder_path}")
    
    def _watch_folder(self):
        """
        Hàm chạy trong thread theo dõi thư mục
        """
        # Quét lần đầu để ghi nhận trạng thái ban đầu
        self.scan_folder()
        
        # Vòng lặp theo dõi
        while self.running:
            try:
                # Ngủ trước khi quét lại
                time.sleep(self.check_interval)
                
                # Quét thư mục
                new_files = self.scan_folder()
                
                # Gọi callback cho mỗi file mới
                if new_files and self.callback:
                    for file_path in new_files:
                        self.callback(file_path)
                
            except Exception as e:
                logger.error(f"Lỗi trong thread theo dõi: {str(e)}")
                time.sleep(5)  # Đợi một chút trước khi thử lại

class BulkUploader:
    """
    Quản lý việc tải lên hàng loạt các video có sẵn trong thư mục
    """
    def __init__(self, telegram_uploader, video_analyzer=None, upload_history=None):
        """
        Khởi tạo BulkUploader
        
        Args:
            telegram_uploader: Đối tượng quản lý tải lên Telegram
            video_analyzer: Đối tượng phân tích video (có thể None)
            upload_history: Đối tượng quản lý lịch sử tải lên (có thể None)
        """
        self.telegram_uploader = telegram_uploader
        self.video_analyzer = video_analyzer
        self.upload_history = upload_history
        self.upload_queue = Queue()
        self.upload_thread = None
        self.running = False
        self.check_duplicates = True
        self.check_history = True  # Thêm biến kiểm tra lịch sử
        self.processed_files = set()  # Tập hợp các file đã xử lý
        self.log_callback = None
        self.progress_callback = None
        
    def set_log_callback(self, callback):
        """
        Đặt callback để ghi log
        
        Args:
            callback (function): Hàm callback nhận chuỗi log
        """
        self.log_callback = callback
    
    def set_progress_callback(self, callback):
        """
        Đặt callback để cập nhật tiến trình
        
        Args:
            callback (function): Hàm callback nhận giá trị tiến trình (0-100)
        """
        self.progress_callback = callback
    
    def log(self, message):
        """
        Ghi log thông qua callback nếu có
        
        Args:
            message (str): Thông báo cần ghi log
        """
        logger.info(message)
        if self.log_callback:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_callback(f"[{timestamp}] {message}")
    
    def scan_and_upload(self, folder_path, extensions, check_duplicates=True, check_history=True):
        """
        Quét thư mục và tải lên tất cả video phù hợp
        
        Args:
            folder_path (str): Đường dẫn thư mục cần quét
            extensions (list): Danh sách phần mở rộng file cần quét
            check_duplicates (bool): Có kiểm tra video trùng lặp không
            check_history (bool): Có kiểm tra video trong lịch sử tải lên không
        """
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            self.log(f"Thư mục không tồn tại: {folder_path}")
            return False
        
        self.check_duplicates = check_duplicates
        self.check_history = check_history
        
        try:
            # Quét thư mục
            self.log(f"Đang quét thư mục: {folder_path}")
            
            videos = []
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext in extensions:
                        videos.append(file_path)
            
            if not videos:
                self.log(f"Không tìm thấy video nào trong thư mục: {folder_path}")
                return False
            
            self.log(f"Đã tìm thấy {len(videos)} video")
            
            # Xử lý trùng lặp nếu cần
            if self.check_duplicates and self.video_analyzer and len(videos) > 1:
                self.log("Đang kiểm tra video trùng lặp...")
                duplicate_groups = self.video_analyzer.find_duplicates(videos)
                
                if duplicate_groups:
                    # Tập hợp các video cần giữ lại (một video từ mỗi nhóm trùng lặp)
                    keep_videos = set()
                    # Tập hợp các video cần loại bỏ
                    remove_videos = set()
                    
                    for group in duplicate_groups:
                        if len(group) > 1:
                            # Chọn video có kích thước lớn nhất trong nhóm để giữ lại
                            best_video = max(group, key=os.path.getsize)
                            
                            # Thêm vào danh sách giữ lại
                            keep_videos.add(best_video)
                            
                            # Thêm các video còn lại vào danh sách loại bỏ
                            for video in group:
                                if video != best_video:
                                    remove_videos.add(video)
                    
                    # Cập nhật danh sách video
                    for video in remove_videos:
                        if video in videos:
                            videos.remove(video)
                    
                    self.log(f"Đã loại bỏ {len(remove_videos)} video trùng lặp")
            
            # Kiểm tra lịch sử tải lên nếu cần
            if self.check_history and self.upload_history and len(videos) > 0:
                self.log("Đang kiểm tra với lịch sử tải lên...")
                
                # Tập hợp video đã tải lên trước đó
                already_uploaded = set()
                
                for video_path in videos.copy():  # Sử dụng copy để tránh lỗi khi sửa đổi danh sách đang lặp
                    try:
                        # Tính hash của video
                        video_hash = self.video_analyzer.calculate_video_hash(video_path)
                        
                        # Kiểm tra xem video đã tồn tại trong lịch sử chưa
                        if video_hash and self.upload_history.is_uploaded(video_hash):
                            already_uploaded.add(video_path)
                            videos.remove(video_path)
                    except Exception as e:
                        logger.error(f"Lỗi khi kiểm tra lịch sử video {os.path.basename(video_path)}: {str(e)}")
                
                if already_uploaded:
                    self.log(f"Đã loại bỏ {len(already_uploaded)} video đã tải lên trước đó")
            
            if not videos:
                self.log("Không còn video nào để tải lên sau khi lọc")
                return False
            
            # Bắt đầu tải lên
            self.start()
            
            # Thêm các video vào hàng đợi
            for video in videos:
                self.upload_queue.put(video)
            
            self.log(f"Đã thêm {len(videos)} video vào hàng đợi tải lên")
            return True
            
        except Exception as e:
            self.log(f"Lỗi khi quét thư mục: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def start(self):
        """
        Bắt đầu quá trình tải lên
        """
        if self.running:
            return
            
        self.running = True
        
        # Xóa danh sách đã xử lý
        self.processed_files.clear()
        
        # Bắt đầu thread tải lên
        self.upload_thread = threading.Thread(target=self._upload_worker)
        self.upload_thread.daemon = True
        self.upload_thread.start()
        
        self.log("Bắt đầu quá trình tải lên hàng loạt")
    
    def stop(self):
        """
        Dừng quá trình tải lên
        """
        if not self.running:
            return
            
        self.running = False
        
        # Đợi thread tải lên kết thúc
        if self.upload_thread and self.upload_thread.is_alive():
            self.upload_thread.join(timeout=1.0)
            
        self.log("Đã dừng quá trình tải lên hàng loạt")
    
    def _upload_worker(self):
        """
        Thread xử lý hàng đợi tải lên
        """
        total_count = self.upload_queue.qsize()
        processed_count = 0
        
        while self.running:
            try:
                # Lấy video từ hàng đợi với timeout
                try:
                    file_path = self.upload_queue.get(timeout=1.0)
                except Empty:
                    # Hàng đợi đã xử lý hết
                    self.log("Đã hoàn tất tất cả video trong hàng đợi")
                    self.running = False
                    break
                
                try:
                    # Kiểm tra trùng lặp nếu được yêu cầu
                    is_duplicate = False
                    if self.check_duplicates and self.video_analyzer:
                        # Kiểm tra trùng lặp với các file đã xử lý
                        for existing_file in self.processed_files:
                            if self.video_analyzer.compare_videos(file_path, existing_file):
                                is_duplicate = True
                                duplicate_name = os.path.basename(existing_file)
                                self.log(f"Phát hiện trùng lặp: {os.path.basename(file_path)} với {duplicate_name}")
                                break
                    
                    # Kiểm tra lịch sử tải lên nếu được yêu cầu
                    already_uploaded = False
                    if not is_duplicate and self.check_history and self.upload_history:
                        video_hash = self.video_analyzer.calculate_video_hash(file_path)
                        if video_hash and self.upload_history.is_uploaded(video_hash):
                            already_uploaded = True
                            self.log(f"Bỏ qua video đã tải lên trước đó: {os.path.basename(file_path)}")
                    
                    # Nếu không trùng lặp và chưa tải lên, tải lên Telegram
                    if not is_duplicate and not already_uploaded:
                        self.log(f"Đang tải lên: {os.path.basename(file_path)}")
                        
                        # Gọi hàm tải lên của telegram_uploader
                        success = self.telegram_uploader.upload_single_video(file_path)
                        
                        if success:
                            self.log(f"Đã tải lên thành công: {os.path.basename(file_path)}")
                        else:
                            self.log(f"Tải lên thất bại: {os.path.basename(file_path)}")
                    
                    # Đánh dấu file đã được xử lý
                    self.processed_files.add(file_path)
                    
                    # Cập nhật tiến trình
                    processed_count += 1
                    if self.progress_callback and total_count > 0:
                        progress = int(processed_count / total_count * 100)
                        self.progress_callback(progress)
                
                except Exception as e:
                    self.log(f"Lỗi khi xử lý file {os.path.basename(file_path)}: {str(e)}")
                
                # Đánh dấu task hoàn thành
                self.upload_queue.task_done()
                
                # Chờ một chút trước khi xử lý file tiếp theo
                time.sleep(1)
                
            except Exception as e:
                if not isinstance(e, Empty):  # Bỏ qua lỗi timeout
                    self.log(f"Lỗi trong thread tải lên: {str(e)}")
        
        # Đảm bảo tiến trình đạt 100% khi hoàn tất
        if self.progress_callback:
            self.progress_callback(100)

class AutoUploader:
    """
    Quản lý việc tự động tải video lên Telegram
    """
    def __init__(self, telegram_uploader, video_analyzer=None, upload_history=None):
        """
        Khởi tạo AutoUploader
        
        Args:
            telegram_uploader: Đối tượng quản lý tải lên Telegram
            video_analyzer: Đối tượng phân tích video (có thể None)
            upload_history: Đối tượng quản lý lịch sử tải lên (có thể None)
        """
        self.telegram_uploader = telegram_uploader
        self.video_analyzer = video_analyzer
        self.upload_history = upload_history
        self.file_watcher = None
        self.upload_queue = Queue()
        self.upload_thread = None
        self.running = False
        self.check_duplicates = True
        self.check_history = True  # Thêm biến kiểm tra lịch sử
        self.processed_files = set()  # Tập hợp các file đã xử lý
        self.log_callback = None
    
    def set_log_callback(self, callback):
        """
        Đặt callback để ghi log
        
        Args:
            callback (function): Hàm callback nhận chuỗi log
        """
        self.log_callback = callback
    
    def log(self, message):
        """
        Ghi log thông qua callback nếu có
        
        Args:
            message (str): Thông báo cần ghi log
        """
        logger.info(message)
        if self.log_callback:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_callback(f"[{timestamp}] {message}")
    
    def start(self, folder_path, extensions, check_interval=60, check_duplicates=True, check_history=True):
        """
        Bắt đầu tự động tải lên
        
        Args:
            folder_path (str): Đường dẫn thư mục cần theo dõi
            extensions (list): Danh sách phần mở rộng file cần theo dõi
            check_interval (int): Thời gian kiểm tra định kỳ (giây)
            check_duplicates (bool): Có kiểm tra video trùng lặp không
            check_history (bool): Có kiểm tra video trong lịch sử tải lên không
        """
        if self.running:
            return
            
        self.running = True
        self.check_duplicates = check_duplicates
        self.check_history = check_history
        
        # Tạo đối tượng theo dõi thư mục
        self.file_watcher = FileWatcher(
            folder_path=folder_path,
            extensions=extensions,
            callback=self._on_new_file,
            check_interval=check_interval
        )
        
        # Bắt đầu thread tải lên
        self.upload_thread = threading.Thread(target=self._upload_worker)
        self.upload_thread.daemon = True
        self.upload_thread.start()
        
        # Bắt đầu theo dõi thư mục
        self.file_watcher.start()
        
        self.log(f"Bắt đầu tự động tải lên từ thư mục: {folder_path}")
        self.log(f"Định dạng được hỗ trợ: {', '.join(extensions)}")
        self.log(f"Thời gian kiểm tra: {check_interval} giây")
        self.log(f"Kiểm tra trùng lặp: {'Bật' if check_duplicates else 'Tắt'}")
        self.log(f"Kiểm tra lịch sử: {'Bật' if check_history else 'Tắt'}")
    
    def stop(self):
        """
        Dừng tự động tải lên
        """
        if not self.running:
            return
            
        self.running = False
        
        # Dừng theo dõi thư mục
        if self.file_watcher:
            self.file_watcher.stop()
            
        # Đợi thread tải lên kết thúc
        if self.upload_thread and self.upload_thread.is_alive():
            self.upload_thread.join(timeout=1.0)
            
        self.log("Đã dừng tự động tải lên")
    
    def _on_new_file(self, file_path):
        """
        Xử lý khi phát hiện file mới
        
        Args:
            file_path (str): Đường dẫn đến file mới
        """
        # Kiểm tra xem file đã được xử lý chưa
        if file_path in self.processed_files:
            return
            
        self.log(f"Đã phát hiện file mới: {os.path.basename(file_path)}")
        
        # Kiểm tra lịch sử tải lên nếu cần
        if self.check_history and self.upload_history and self.video_analyzer:
            try:
                # Tính hash của video
                video_hash = self.video_analyzer.calculate_video_hash(file_path)
                
                # Kiểm tra xem video đã tồn tại trong lịch sử chưa
                if video_hash and self.upload_history.is_uploaded(video_hash):
                    self.log(f"Bỏ qua video đã tải lên trước đó: {os.path.basename(file_path)}")
                    # Đánh dấu là đã xử lý để không xử lý lại
                    self.processed_files.add(file_path)
                    return
            except Exception as e:
                logger.error(f"Lỗi khi kiểm tra lịch sử video {os.path.basename(file_path)}: {str(e)}")
        
        # Thêm vào hàng đợi tải lên
        self.upload_queue.put(file_path)
    
    def _upload_worker(self):
        """
        Thread xử lý hàng đợi tải lên
        """
        while self.running:
            try:
                # Lấy file từ hàng đợi với timeout
                file_path = self.upload_queue.get(timeout=1.0)
                
                try:
                    # Kiểm tra trùng lặp nếu được yêu cầu
                    is_duplicate = False
                    if self.check_duplicates and self.video_analyzer:
                        # Lấy danh sách các file đã xử lý
                        processed_list = list(self.processed_files)
                        
                        # Kiểm tra trùng lặp với các file đã xử lý
                        for existing_file in processed_list:
                            if self.video_analyzer.compare_videos(file_path, existing_file):
                                is_duplicate = True
                                duplicate_name = os.path.basename(existing_file)
                                self.log(f"Phát hiện trùng lặp: {os.path.basename(file_path)} với {duplicate_name}")
                                break
                    
                    # Nếu không trùng lặp, tải lên Telegram
                    if not is_duplicate:
                        self.log(f"Đang tải lên: {os.path.basename(file_path)}")
                        
                        # Gọi hàm tải lên của telegram_uploader
                        success = self.telegram_uploader.upload_single_video(file_path)
                        
                        if success:
                            self.log(f"Đã tải lên thành công: {os.path.basename(file_path)}")
                        else:
                            self.log(f"Tải lên thất bại: {os.path.basename(file_path)}")
                    
                    # Đánh dấu file đã được xử lý
                    self.processed_files.add(file_path)
                
                except Exception as e:
                    self.log(f"Lỗi khi xử lý file {os.path.basename(file_path)}: {str(e)}")
                
                # Đánh dấu task hoàn thành
                self.upload_queue.task_done()
                
                # Chờ một chút trước khi xử lý file tiếp theo
                time.sleep(1)
                
            except Exception as e:
                if not isinstance(e, Empty):  # Bỏ qua lỗi timeout
                    self.log(f"Lỗi trong thread tải lên: {str(e)}")

if __name__ == "__main__":
    # Mã kiểm thử
    logging.basicConfig(level=logging.DEBUG)
    
    def test_callback(file_path):
        print(f"File mới: {file_path}")
    
    # Kiểm thử FileWatcher
    watcher = FileWatcher(
        folder_path="./test",
        extensions=['.mp4', '.avi', '.mkv'],
        callback=test_callback,
        check_interval=5
    )
    
    try:
        watcher.start()
        print("Đang theo dõi thư mục. Nhấn Ctrl+C để dừng...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
        print("Đã dừng theo dõi thư mục.")