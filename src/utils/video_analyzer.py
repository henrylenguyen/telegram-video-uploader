"""
Module phân tích và so sánh video để phát hiện nội dung trùng lặp.
"""
import cv2
import numpy as np
import os
import logging
import hashlib
from PIL import Image, ImageTk
import imagehash
import tkinter as tk
from threading import Thread
from queue import Queue

# Cấu hình logging
logger = logging.getLogger("VideoAnalyzer")

class VideoAnalyzer:
    """
    Lớp phân tích và so sánh video để phát hiện nội dung trùng lặp.
    
    Phương pháp:
    1. Trích xuất các khung hình ở các vị trí khác nhau trong video
    2. Tính toán perceptual hash cho mỗi khung hình
    3. Kết hợp các hash để tạo hash đại diện cho video
    4. So sánh hash để phát hiện video trùng lặp
    """
    
    def __init__(self):
        """Khởi tạo VideoAnalyzer"""
        self.cache = {}  # Cache để lưu thông tin video đã phân tích
        self.analysis_queue = Queue()  # Hàng đợi cho phân tích bất đồng bộ
        self.worker_thread = None
        self.is_analyzing = False
    
    def start_async_analysis(self, callback=None):
        """Bắt đầu thread phân tích video bất đồng bộ"""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.is_analyzing = True
            self.worker_thread = Thread(target=self._async_analysis_worker, args=(callback,))
            self.worker_thread.daemon = True
            self.worker_thread.start()
            logger.info("Đã bắt đầu thread phân tích video")
    
    def stop_async_analysis(self):
        """Dừng thread phân tích video"""
        self.is_analyzing = False
        if self.worker_thread and self.worker_thread.is_alive():
            # Đợi thread kết thúc
            self.worker_thread.join(timeout=1.0)
            logger.info("Đã dừng thread phân tích video")
    
    def _async_analysis_worker(self, callback):
        """Worker thread xử lý hàng đợi phân tích video"""
        while self.is_analyzing:
            try:
                # Lấy video từ hàng đợi với timeout
                video_path = self.analysis_queue.get(timeout=1.0)
                
                # Phân tích video
                hash_value = self.calculate_video_hash(video_path)
                
                # Gọi callback nếu có
                if callback:
                    callback(video_path, hash_value)
                
                # Đánh dấu task hoàn thành
                self.analysis_queue.task_done()
                
            except Exception as e:
                if not isinstance(e, Queue.Empty):  # Bỏ qua lỗi timeout
                    logger.error(f"Lỗi trong thread phân tích: {e}")
    
    def queue_video_for_analysis(self, video_path):
        """Thêm video vào hàng đợi để phân tích bất đồng bộ"""
        if os.path.exists(video_path) and os.path.isfile(video_path):
            self.analysis_queue.put(video_path)
            return True
        return False
    
    def calculate_video_hash(self, video_path):
        """
        Tính toán giá trị hash dựa trên nội dung video.
        
        Args:
            video_path (str): Đường dẫn đến file video
            
        Returns:
            str: Hash đại diện cho video hoặc None nếu có lỗi
        """
        try:
            # Kiểm tra trong cache trước
            if video_path in self.cache:
                return self.cache[video_path]['hash']
            
            # Mở video
            video = cv2.VideoCapture(video_path)
            
            if not video.isOpened():
                logger.error(f"Không thể mở video: {video_path}")
                return None
            
            # Lấy thông tin cơ bản
            fps = video.get(cv2.CAP_PROP_FPS)
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            logger.debug(f"Video {video_path}: {width}x{height}, {fps} fps, {duration:.2f}s, {frame_count} frames")
            
            # Lấy khung hình ở các vị trí khác nhau
            frames = []
            positions = [0.1, 0.3, 0.5, 0.7, 0.9]  # Vị trí tương đối (10%, 30%, 50%, 70%, 90%)
            
            for pos in positions:
                frame_pos = int(frame_count * pos)
                if frame_pos > 0:
                    video.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                    ret, frame = video.read()
                    if ret:
                        # Chuyển đổi khung hình sang ảnh PIL
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pil_img = Image.fromarray(frame)
                        
                        # Thay đổi kích thước để tăng tốc độ xử lý
                        pil_img = pil_img.resize((128, 128))
                        
                        # Tính toán perceptual hash
                        img_hash = imagehash.phash(pil_img)
                        frames.append(str(img_hash))
            
            video.release()
            
            # Tạo hash dựa trên nội dung khung hình và thông tin khác
            content_string = '|'.join(frames) + f"|{duration:.2f}|{fps:.2f}|{width}x{height}"
            content_hash = hashlib.md5(content_string.encode()).hexdigest()
            
            # Lưu vào cache
            self.cache[video_path] = {
                'hash': content_hash,
                'duration': duration,
                'frame_count': frame_count,
                'resolution': f"{width}x{height}",
                'fps': fps
            }
            
            logger.debug(f"Đã tính toán hash cho video {video_path}: {content_hash[:8]}...")
            return content_hash
            
        except Exception as e:
            logger.error(f"Lỗi khi tính toán hash video {video_path}: {e}")
            return None
    
    def get_thumbnail(self, video_path, size=(160, 120)):
        """
        Tạo hình thu nhỏ từ video
        
        Args:
            video_path (str): Đường dẫn đến file video
            size (tuple): Kích thước hình thu nhỏ (width, height)
            
        Returns:
            ImageTk.PhotoImage: Hình thu nhỏ định dạng Tkinter hoặc None nếu có lỗi
        """
        try:
            video = cv2.VideoCapture(video_path)
            
            if not video.isOpened():
                logger.error(f"Không thể mở video để tạo thumbnail: {video_path}")
                return None
            
            # Lấy khung hình ở vị trí 20%
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            video.set(cv2.CAP_PROP_POS_FRAMES, int(frame_count * 0.2))
            
            ret, frame = video.read()
            video.release()
            
            if not ret:
                logger.error(f"Không thể đọc khung hình từ video: {video_path}")
                return None
            
            # Chuyển đổi khung hình sang ảnh PIL
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame)
            
            # Thay đổi kích thước
            pil_img = pil_img.resize(size, Image.LANCZOS)
            
            # Chuyển đổi sang định dạng Tkinter
            img_tk = ImageTk.PhotoImage(pil_img)
            
            return img_tk
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo hình thu nhỏ cho video {video_path}: {e}")
            return None
    
    def compare_videos(self, video1_path, video2_path, threshold=0.9):
        """
        So sánh hai video để xác định có trùng lặp không
        
        Args:
            video1_path (str): Đường dẫn đến video 1
            video2_path (str): Đường dẫn đến video 2
            threshold (float): Ngưỡng tương đồng (0.0 - 1.0)
            
        Returns:
            bool: True nếu hai video được xác định là trùng lặp
        """
        # Tính hash cho cả hai video nếu chưa có
        hash1 = self.cache.get(video1_path, {}).get('hash')
        if not hash1:
            hash1 = self.calculate_video_hash(video1_path)
        
        hash2 = self.cache.get(video2_path, {}).get('hash')
        if not hash2:
            hash2 = self.calculate_video_hash(video2_path)
        
        # Nếu không thể tính hash cho một trong hai video
        if not hash1 or not hash2:
            return False
        
        # Nếu hash giống nhau hoàn toàn
        if hash1 == hash2:
            logger.info(f"Phát hiện video trùng lặp: {os.path.basename(video1_path)} và {os.path.basename(video2_path)}")
            return True
        
        # Kiểm tra thời lượng từ cache
        info1 = self.cache.get(video1_path, {})
        info2 = self.cache.get(video2_path, {})
        
        # Nếu thời lượng chênh lệch quá nhiều thì không phải trùng lặp
        if 'duration' in info1 and 'duration' in info2:
            duration1 = info1['duration']
            duration2 = info2['duration']
            
            # Nếu thời lượng chênh lệch hơn 5%, coi là khác nhau
            if abs(duration1 - duration2) / max(duration1, duration2) > 0.05:
                return False
        
        return False  # Mặc định coi là khác nhau
    
    def find_duplicates(self, video_paths):
        """
        Tìm các video trùng lặp trong danh sách
        
        Args:
            video_paths (list): Danh sách đường dẫn video
            
        Returns:
            list: Danh sách các nhóm video trùng lặp
        """
        logger.info(f"Bắt đầu tìm video trùng lặp trong {len(video_paths)} video...")
        
        # Tính toán hash cho tất cả video
        for path in video_paths:
            if path not in self.cache:
                self.calculate_video_hash(path)
        
        # Nhóm các video theo hash
        hash_groups = {}
        for path in video_paths:
            hash_val = self.cache.get(path, {}).get('hash')
            if hash_val:
                if hash_val not in hash_groups:
                    hash_groups[hash_val] = []
                hash_groups[hash_val].append(path)
        
        # Tìm các nhóm trùng lặp (có nhiều hơn 1 video)
        duplicates = [group for group in hash_groups.values() if len(group) > 1]
        
        if duplicates:
            logger.info(f"Đã tìm thấy {len(duplicates)} nhóm video trùng lặp")
            for i, group in enumerate(duplicates, 1):
                logger.debug(f"Nhóm trùng lặp {i}: {[os.path.basename(v) for v in group]}")
        else:
            logger.info("Không tìm thấy video trùng lặp")
        
        return duplicates
    
    def get_video_info(self, video_path):
        """
        Lấy thông tin chi tiết về video
        
        Args:
            video_path (str): Đường dẫn đến file video
            
        Returns:
            dict: Thông tin video hoặc None nếu có lỗi
        """
        # Kiểm tra trong cache trước
        if video_path in self.cache:
            info = self.cache[video_path].copy()
            # Thêm thông tin file
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            info['file_size'] = f"{file_size:.2f} MB"
            info['file_name'] = os.path.basename(video_path)
            return info
        
        # Nếu chưa có trong cache, tính hash (sẽ thêm vào cache)
        self.calculate_video_hash(video_path)
        
        # Kiểm tra lại trong cache
        if video_path in self.cache:
            info = self.cache[video_path].copy()
            # Thêm thông tin file
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            info['file_size'] = f"{file_size:.2f} MB"
            info['file_name'] = os.path.basename(video_path)
            return info
        
        return None

if __name__ == "__main__":
    # Mã kiểm thử
    logging.basicConfig(level=logging.DEBUG)
    
    analyzer = VideoAnalyzer()
    test_video = "path/to/test/video.mp4"
    
    if os.path.exists(test_video):
        hash_val = analyzer.calculate_video_hash(test_video)
        print(f"Video hash: {hash_val}")
        
        info = analyzer.get_video_info(test_video)
        print(f"Video info: {info}")
    else:
        print(f"Test video not found: {test_video}")