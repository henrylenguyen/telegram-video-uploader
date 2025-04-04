"""
Module quản lý lịch sử tải lên video.
Cung cấp chức năng ghi nhớ video đã tải lên giữa các phiên làm việc.
"""
import os
import json
import logging
from datetime import datetime
import shutil

logger = logging.getLogger("UploadHistory")

class UploadHistory:
    """
    Quản lý lịch sử tải lên video, lưu và tải thông tin video đã tải lên.
    Sử dụng JSON để lưu trữ dữ liệu giữa các phiên làm việc.
    """
    
    def __init__(self, history_file='upload_history.json'):
        """
        Khởi tạo quản lý lịch sử tải lên
        
        Args:
            history_file (str): Đường dẫn đến file lưu trữ lịch sử
        """
        self.history_file = history_file
        self.uploads = {}  # {hash: {filename, path, upload_date, file_size}}
        self.duplicates = {}  # {hash: [list of duplicate hashes]}
        self.load_history()
    
    def load_history(self):
        """Tải lịch sử tải lên từ file"""
        if not os.path.exists(self.history_file):
            logger.info(f"Không tìm thấy file lịch sử, tạo mới: {self.history_file}")
            return
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.uploads = data.get('uploads', {})
                self.duplicates = data.get('duplicates', {})
            
            logger.info(f"Đã tải lịch sử: {len(self.uploads)} video đã tải lên")
        except Exception as e:
            logger.error(f"Lỗi khi tải lịch sử: {str(e)}")
    
    def save_history(self):
        """Lưu lịch sử tải lên vào file"""
        try:
            # Tạo thư mục cha nếu không tồn tại
            os.makedirs(os.path.dirname(os.path.abspath(self.history_file)), exist_ok=True)
            
            # Tạo backup trước khi ghi đè
            if os.path.exists(self.history_file):
                backup_file = f"{self.history_file}.bak"
                shutil.copy2(self.history_file, backup_file)
            
            data = {
                'uploads': self.uploads,
                'duplicates': self.duplicates
            }
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Đã lưu lịch sử: {len(self.uploads)} video")
        except Exception as e:
            logger.error(f"Lỗi khi lưu lịch sử: {str(e)}")
    
    def add_upload(self, video_hash, filename, file_path, file_size):
        """
        Thêm video vào lịch sử tải lên
        
        Args:
            video_hash (str): Hash đặc trưng của video
            filename (str): Tên file video
            file_path (str): Đường dẫn đến file video
            file_size (int): Kích thước file (bytes)
        """
        upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.uploads[video_hash] = {
            'filename': filename,
            'path': file_path,
            'upload_date': upload_date,
            'file_size': file_size
        }
        
        # Lưu lịch sử sau mỗi lần thêm
        self.save_history()
        
        logger.info(f"Đã thêm video vào lịch sử: {filename} (hash: {video_hash[:8]}...)")
    
    def add_duplicate(self, video_hash, duplicate_hash):
        """
        Đánh dấu video là trùng lặp với video khác
        
        Args:
            video_hash (str): Hash video mới
            duplicate_hash (str): Hash video đã tồn tại mà nó trùng lặp với
        """
        if video_hash not in self.duplicates:
            self.duplicates[video_hash] = []
        
        if duplicate_hash not in self.duplicates[video_hash]:
            self.duplicates[video_hash].append(duplicate_hash)
            
            logger.info(f"Đã đánh dấu hash {video_hash[:8]}... trùng lặp với {duplicate_hash[:8]}...")
            self.save_history()
    
    def is_uploaded(self, video_hash):
        """
        Kiểm tra xem video đã được tải lên trước đó chưa
        
        Args:
            video_hash (str): Hash của video cần kiểm tra
            
        Returns:
            bool: True nếu video đã tải lên trước đó
        """
        return video_hash in self.uploads
    
    def get_upload_info(self, video_hash):
        """
        Lấy thông tin tải lên của video
        
        Args:
            video_hash (str): Hash của video
            
        Returns:
            dict/None: Thông tin video nếu tồn tại, None nếu không
        """
        return self.uploads.get(video_hash)
    
    def get_all_uploads(self):
        """
        Lấy danh sách tất cả video đã tải lên
        
        Returns:
            dict: Danh sách các video đã tải lên
        """
        return self.uploads
    
    def get_duplicates_of(self, video_hash):
        """
        Lấy danh sách hash của các video trùng lặp với video đã cho
        
        Args:
            video_hash (str): Hash của video cần kiểm tra
            
        Returns:
            list: Danh sách hash các video trùng lặp
        """
        return self.duplicates.get(video_hash, [])
    
    def get_duplicate_files(self, video_hash):
        """
        Lấy thông tin chi tiết của các video trùng lặp với video đã cho
        
        Args:
            video_hash (str): Hash của video cần kiểm tra
            
        Returns:
            list: Danh sách thông tin các video trùng lặp
        """
        duplicate_files = []
        duplicate_hashes = self.get_duplicates_of(video_hash)
        
        for hash_value in duplicate_hashes:
            info = self.get_upload_info(hash_value)
            if info:
                duplicate_files.append(info)
        
        return duplicate_files
    
    def remove_upload(self, video_hash):
        """
        Xóa video khỏi lịch sử tải lên
        
        Args:
            video_hash (str): Hash của video cần xóa
            
        Returns:
            bool: True nếu xóa thành công
        """
        if video_hash in self.uploads:
            del self.uploads[video_hash]
            
            # Dọn dẹp các tham chiếu trong duplicates
            for hash_value, duplicates in list(self.duplicates.items()):
                if video_hash in duplicates:
                    self.duplicates[hash_value].remove(video_hash)
                
                # Xóa các mục trống
                if not self.duplicates[hash_value]:
                    del self.duplicates[hash_value]
            
            # Xóa mục này khỏi duplicates nếu có
            if video_hash in self.duplicates:
                del self.duplicates[video_hash]
            
            self.save_history()
            logger.info(f"Đã xóa video khỏi lịch sử: hash {video_hash[:8]}...")
            return True
        
        return False
    
    def clear_history(self):
        """Xóa toàn bộ lịch sử tải lên"""
        self.uploads = {}
        self.duplicates = {}
        self.save_history()
        logger.info("Đã xóa toàn bộ lịch sử tải lên")
    
    def get_upload_by_hash(self, video_hash):
        """
        Tìm thông tin tải lên dựa trên hash của video
        
        Args:
            video_hash: Hash của video cần tìm
            
        Returns:
            dict: Thông tin tải lên hoặc None nếu không tìm thấy
        """
        if not video_hash:
            return None
            
        uploads = self.get_all_uploads()
        
        for upload_hash, upload_info in uploads.items():
            if upload_hash == video_hash:
                return upload_info
        
        return None

if __name__ == "__main__":
    # Mã kiểm thử
    logging.basicConfig(level=logging.DEBUG)
    
    history = UploadHistory("test_history.json")
    history.add_upload("hash1", "video1.mp4", "/path/to/video1.mp4", 10000000)
    history.add_upload("hash2", "video2.mp4", "/path/to/video2.mp4", 15000000)
    
    history.add_duplicate("hash3", "hash1")
    
    print(f"Video 1 đã tải lên: {history.is_uploaded('hash1')}")
    print(f"Thông tin video 1: {history.get_upload_info('hash1')}")
    print(f"Các video trùng lặp với hash1: {history.get_duplicates_of('hash1')}")
    
    history.remove_upload("hash1")
    print(f"Video 1 đã tải lên (sau khi xóa): {history.is_uploaded('hash1')}")
    
    history.clear_history()