"""
Folder management methods for the MainUI class
"""
import os
import logging
import time
import traceback
from PyQt5 import QtWidgets, QtCore

from utils.main_tab import refresh_video_list, clear_video_preview, clear_video_frames

logger = logging.getLogger(__name__)

def initialize_folder(self):
    """Initialize folder from saved settings"""
    # Load recent folders from config
    self.load_recent_folders_from_config()
    
    # Try to get folder from app config
    folder_path = ""
    if hasattr(self, 'app') and hasattr(self.app, 'config'):
        # Check if config is a ConfigParser object or a dictionary
        if hasattr(self.app.config, 'get') and callable(self.app.config.get):
            try:
                # Check if it's ConfigParser object
                if hasattr(self.app.config, 'has_section') and self.app.config.has_section('SETTINGS'):
                    folder_path = self.app.config.get('SETTINGS', 'video_folder', fallback="")
                # Otherwise treat as dictionary
                elif isinstance(self.app.config, dict) and 'SETTINGS' in self.app.config:
                    settings = self.app.config.get('SETTINGS', {})
                    if isinstance(settings, dict):
                        folder_path = settings.get('video_folder', '')
            except Exception as e:
                logger.error(f"Error getting folder path from config: {str(e)}")
    
    # Set folder path and refresh
    if folder_path and os.path.exists(folder_path) and os.path.isdir(folder_path):
        self.folder_path_edit.setText(folder_path)
        self.refresh_folder()
        
    # Khởi tạo dropdown sắp xếp
    self.initialize_sort_dropdown()

def browse_folder(self):
    """Open file dialog to browse for folder"""
    folder = QtWidgets.QFileDialog.getExistingDirectory(
        self, "Chọn thư mục chứa video", "",
        QtWidgets.QFileDialog.ShowDirsOnly
    )

    if folder:
        self.folder_path_edit.setText(folder)
        logger.info(f"Selected folder: {folder}")
        
        # Refresh video list
        self.refresh_folder()
        
        # Save to recent folders
        self.add_to_recent_folders(folder)
        
        # Save to app config
        if hasattr(self, 'app') and hasattr(self.app, 'config') and hasattr(self.app, 'config_manager'):
            try:
                # Check if config is ConfigParser or dictionary
                if hasattr(self.app.config, 'has_section') and callable(self.app.config.has_section):
                    # ConfigParser approach
                    if not self.app.config.has_section('SETTINGS'):
                        self.app.config.add_section('SETTINGS')
                    self.app.config.set('SETTINGS', 'video_folder', folder)
                else:
                    # Dictionary approach
                    if 'SETTINGS' not in self.app.config:
                        self.app.config['SETTINGS'] = {}
                    self.app.config['SETTINGS']['video_folder'] = folder
                
                # Save config
                self.app.config_manager.save_config(self.app.config)
            except Exception as e:
                logger.error(f"Error saving folder to config: {str(e)}")

def refresh_folder(self):
    """Refresh danh sách video từ thư mục hiện tại - CẢI TIẾN"""
    folder_path = self.folder_path_edit.text()
    if not folder_path:
        return
            
    # Xóa thông tin video và frame hiện tại
    clear_video_preview(self)
    clear_video_frames(self)
    
    # Reset selected video
    self.selected_video = None
    
    # Reset phân trang về trang đầu tiên
    self.current_page = 1
    
    # Reset pagination manager nếu tồn tại
    if self.pagination_manager:
        self.pagination_manager.reset()
    
    # Hiển thị overlay loading
    self.show_loading_overlay("Đang quét thư mục video...", show_spinner=True)
    
    # Sử dụng QTimer để tránh đóng băng UI
    QtCore.QTimer.singleShot(100, self.refresh_folder_with_loading)

def refresh_folder_with_loading(self):
    """Làm mới thư mục với hiệu ứng loading - CẢI TIẾN"""
    self.update_video_list_ui()
    self.debug_video_list_issue()
    try:
        # Đặt con trỏ wait
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        
        folder_path = self.folder_path_edit.text()
        
        # Hiển thị đang quét video
        self.loading_overlay.set_message(f"Đang quét video trong thư mục...\n{folder_path}")
        QtWidgets.QApplication.processEvents()
        
        # Đếm số file trong thư mục 
        video_count = self.count_video_files(folder_path)
        
        # Hiển thị số lượng video đã tìm thấy
        self.loading_overlay.set_message(f"Đã tìm thấy {video_count} video.\nĐang phân tích...")
        QtWidgets.QApplication.processEvents()
        
        # Nếu có nhiều file, xử lý từng batch
        if video_count > 100:
            # Tạo progress dialog
            progress_dialog = QtWidgets.QProgressDialog(
                f"Đang quét {video_count} video trong thư mục...", 
                "Hủy", 0, 100, self
            )
            progress_dialog.setWindowTitle("Đang tải danh sách video")
            progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
            progress_dialog.show()
            
            # Sử dụng hàm tiện ích để làm mới danh sách video với báo cáo tiến trình
            self.all_videos = []
            
            # Xử lý file theo batch
            total_files = 0
            for root, _, files in os.walk(folder_path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in ['.mp4', '.avi', '.mkv', '.mov', '.webm', '.m4v', '.flv', '.wmv']:
                        total_files += 1
            
            processed_files = 0
            for root, _, files in os.walk(folder_path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in ['.mp4', '.avi', '.mkv', '.mov', '.webm', '.m4v', '.flv', '.wmv']:
                        file_path = os.path.join(root, file)
                        video_info = {
                            "name": file,
                            "path": file_path,
                            "status": "new",
                            "file_size_bytes": os.path.getsize(file_path)
                        }
                        self.all_videos.append(video_info)
                        
                        processed_files += 1
                        progress = int((processed_files / total_files) * 100)
                        progress_dialog.setValue(progress)
                        
                        # Cập nhật loading overlay
                        self.loading_overlay.set_message(f"Đã quét {processed_files}/{total_files} video...")
                        QtWidgets.QApplication.processEvents()
                        
                        if progress_dialog.wasCanceled():
                            break
                    
                    if progress_dialog.wasCanceled():
                        break
                
                if progress_dialog.wasCanceled():
                    break
            
            progress_dialog.close()
        else:
            # Sử dụng hàm tiện ích để làm mới danh sách video
            self.all_videos = refresh_video_list(self, folder_path)
        
        # Kiểm tra nếu có FFmpeg để hiển thị frames
        has_ffmpeg = self.check_ffmpeg_installed()
        if not has_ffmpeg:
            self.loading_overlay.set_message("Đang hoàn tất... (FFmpeg không có sẵn, không thể trích xuất khung hình)")
            QtWidgets.QApplication.processEvents()
            time.sleep(1)  # Cho phép người dùng đọc thông báo
        
        # Cập nhật từ điển video
        self.videos = {}
        for video in self.all_videos:
            self.videos[video["name"]] = video["path"]
        
        # Reset bộ đếm lựa chọn
        self.selected_video_count = 0
        self.selected_videos_size = 0
        
        # Cập nhật UI
        self.update_video_list_ui()
        
        # Lưu thư mục vào danh sách gần đây
        self.add_to_recent_folders(folder_path)
        
    except Exception as e:
        logger.error(f"Lỗi khi làm mới thư mục: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Hiển thị thông báo lỗi
        QtWidgets.QMessageBox.critical(self, "Lỗi", f"Không thể quét thư mục: {str(e)}")
    finally:
        # Khôi phục con trỏ và ẩn loading overlay
        QtWidgets.QApplication.restoreOverrideCursor()
        self.loading_overlay.hide()

def show_loading_overlay(self, message="Đang tải...", show_spinner=True):
    """
    Hiển thị overlay loading với hiệu ứng nâng cao
    
    Args:
        message: Thông báo hiển thị
        show_spinner: Có hiển thị spinner hay không
    """
    # Đảm bảo overlay đã được tạo
    if not hasattr(self, 'loading_overlay') or not self.loading_overlay:
        self.loading_overlay = LoadingOverlay(self.central_widget)
    
    # Cập nhật kích thước
    self.loading_overlay.resize(self.central_widget.size())
    
    # Thiết lập thông báo
    self.loading_overlay.set_message(message)
    
    # Bật/tắt spinner
    self.loading_overlay.show_spinner(show_spinner)
    
    # Hiển thị overlay
    self.loading_overlay.show()
    
    # Cập nhật UI ngay lập tức
    QtWidgets.QApplication.processEvents()

def load_recent_folder(self, index):
    """Load folder from recent folders combo box"""
    try:
        # Ghi log để debug
        logger.debug(f"load_recent_folder được gọi với index={index}, count={self.recent_folders_combo.count()}")
        
        # Không thực hiện hành động nếu người dùng chọn tiêu đề
        if index <= 0:  # Tiêu đề "Thư mục gần đây"
            return
        
        # Lấy đường dẫn đầy đủ từ userData (nếu có) hoặc từ text
        folder = self.recent_folders_combo.itemData(index, QtCore.Qt.UserRole)
        if not folder:  # Nếu không có userData, sử dụng text hiển thị
            folder = self.recent_folders_combo.itemText(index)
        
        logger.debug(f"Đã lấy folder từ combobox: {folder}")
        
        # Kiểm tra xem thư mục có tồn tại không
        if not os.path.exists(folder):
            # Hiển thị cảnh báo và xóa thư mục không tồn tại khỏi dropdown
            result = QtWidgets.QMessageBox.warning(
                self, 
                "Lỗi", 
                f"Thư mục không tồn tại hoặc không hợp lệ:\n{folder}", 
                QtWidgets.QMessageBox.Ok
            )
            
            # Xóa thư mục không hợp lệ khỏi dropdown và config
            self.recent_folders_combo.removeItem(index)
            self.save_recent_folders_to_config()
            
            # Đặt lại dropdown về item đầu tiên ("Đường dẫn gần đây")
            self.recent_folders_combo.setCurrentIndex(0)
            return
        
        # Hiển thị tooltip đầy đủ đường dẫn
        self.recent_folders_combo.setToolTip(folder)
        
        # Clear existing previews first
        clear_video_preview(self)
        
        # Set folder path in the edit box
        self.folder_path_edit.setText(folder)
        
        # Block signals để tránh đệ quy
        self.recent_folders_combo.blockSignals(True)
        
        # Nếu là một mục khác mục đầu tiên (sau title), hãy di chuyển nó lên đầu
        if index > 1:
            # Lưu đường dẫn đầy đủ và văn bản hiển thị
            full_path = folder
            display_text = self.truncate_path(full_path)
            
            # Xóa mục hiện tại
            self.recent_folders_combo.removeItem(index)
            
            # Thêm vào đầu danh sách (sau title)
            self.recent_folders_combo.insertItem(1, display_text)
            self.recent_folders_combo.setItemData(1, full_path, QtCore.Qt.UserRole)
            self.recent_folders_combo.setCurrentIndex(1)
            
            logger.debug(f"Đã di chuyển thư mục '{folder}' lên vị trí đầu tiên")
        
        # Unblock signals
        self.recent_folders_combo.blockSignals(False)
        
        # Lưu cấu hình 
        self.save_recent_folders_to_config()
        
        # Làm mới thư mục
        self.refresh_folder()
        
        logger.debug(f"Hoàn thành load_recent_folder với thư mục: {folder}")
    except Exception as e:
        logger.error(f"Lỗi khi tải thư mục gần đây: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Đảm bảo unblock signals
        if hasattr(self, 'recent_folders_combo'):
            self.recent_folders_combo.blockSignals(False)

def load_recent_folders_from_config(self):
    """Load recent folders from config"""
    if not hasattr(self, 'recent_folders_combo'):
        return
            
    # Clear existing items except the first one (header)
    while self.recent_folders_combo.count() > 1:
        self.recent_folders_combo.removeItem(1)
    
    # Try to get recent folders from config
    try:
        if hasattr(self, 'app') and hasattr(self.app, 'config'):
            # Check if config is ConfigParser or dictionary
            if hasattr(self.app.config, 'has_section') and callable(self.app.config.has_section):
                # ConfigParser approach
                if self.app.config.has_section('RECENT_FOLDERS'):
                    # Load each folder from config
                    for i in range(10):  # Load up to 10 recent folders
                        key = f"folder_{i}"
                        try:
                            if self.app.config.has_option('RECENT_FOLDERS', key):
                                folder = self.app.config.get('RECENT_FOLDERS', key)
                                if folder and os.path.exists(folder):
                                    self.recent_folders_combo.addItem(folder)
                        except Exception as e:
                            logger.error(f"Error loading folder {i} from config: {str(e)}")
            
            # Dictionary approach
            elif isinstance(self.app.config, dict) and 'RECENT_FOLDERS' in self.app.config:
                recent_folders = self.app.config.get('RECENT_FOLDERS', {})
                if isinstance(recent_folders, dict):
                    # Load each folder from config
                    for i in range(10):  # Load up to 10 recent folders
                        key = f"folder_{i}"
                        if key in recent_folders:
                            folder = recent_folders.get(key)
                            if folder and os.path.exists(folder):
                                self.recent_folders_combo.addItem(folder)
            
            # If no RECENT_FOLDERS section exists yet and config_manager is available
            elif hasattr(self.app, 'config_manager'):
                if isinstance(self.app.config, dict):
                    self.app.config['RECENT_FOLDERS'] = {}
                    self.app.config_manager.save_config(self.app.config)
        
        # Direct approach in case app or app.config is not available
        else:
            # Try to load directly from config.ini file
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.ini')
            if os.path.exists(config_path):
                import configparser
                config = configparser.ConfigParser()
                config.read(config_path, encoding='utf-8')
                
                if 'RECENT_FOLDERS' in config:
                    for i in range(10):
                        key = f"folder_{i}"
                        if config.has_option('RECENT_FOLDERS', key):
                            folder = config.get('RECENT_FOLDERS', key)
                            if folder and os.path.exists(folder):
                                self.recent_folders_combo.addItem(folder)
    except Exception as e:
        logger.error(f"Error loading recent folders from config: {str(e)}")

def save_recent_folders_to_config(self):
    """Save recent folders to config"""
    if not hasattr(self, 'recent_folders_combo'):
        return
            
    # Try to save to app.config if available
    try:
        if hasattr(self, 'app') and hasattr(self.app, 'config'):
            # Check if app.config is ConfigParser or dictionary
            if hasattr(self.app.config, 'has_section') and callable(self.app.config.has_section):
                # ConfigParser approach
                if not self.app.config.has_section('RECENT_FOLDERS'):
                    self.app.config.add_section('RECENT_FOLDERS')
                
                # Clear existing entries
                for option in self.app.config.options('RECENT_FOLDERS'):
                    if option.startswith('folder_'):
                        self.app.config.remove_option('RECENT_FOLDERS', option)
                
                # Save current folders - QUAN TRỌNG: bắt đầu từ 0 để đúng với định dạng folder_0, folder_1,...
                folder_count = 0
                for i in range(1, min(self.recent_folders_combo.count(), 11)):
                    # Lấy đường dẫn đầy đủ từ userData, nếu không có thì lấy từ text
                    folder = self.recent_folders_combo.itemData(i, QtCore.Qt.UserRole)
                    if not folder:  # Nếu không có userData
                        folder = self.recent_folders_combo.itemText(i)
                        
                    # Kiểm tra đường dẫn hợp lệ trước khi lưu
                    if folder and os.path.isdir(folder):
                        self.app.config.set('RECENT_FOLDERS', f"folder_{folder_count}", os.path.normpath(folder))
                        folder_count += 1
                
                # Save config if config_manager available
                if hasattr(self.app, 'config_manager'):
                    self.app.config_manager.save_config(self.app.config)
            
            # Dictionary approach
            elif isinstance(self.app.config, dict):
                # Create RECENT_FOLDERS section if it doesn't exist
                if 'RECENT_FOLDERS' not in self.app.config:
                    self.app.config['RECENT_FOLDERS'] = {}
                elif not isinstance(self.app.config['RECENT_FOLDERS'], dict):
                    self.app.config['RECENT_FOLDERS'] = {}
                
                # Clear existing entries
                for key in list(self.app.config['RECENT_FOLDERS'].keys()):
                    if key.startswith('folder_'):
                        del self.app.config['RECENT_FOLDERS'][key]
                
                # Save current folders - QUAN TRỌNG: bắt đầu từ 0 để đúng với định dạng folder_0, folder_1,...
                folder_count = 0
                for i in range(1, min(self.recent_folders_combo.count(), 11)):
                    # Lấy đường dẫn đầy đủ từ userData, nếu không có thì lấy từ text
                    folder = self.recent_folders_combo.itemData(i, QtCore.Qt.UserRole)
                    if not folder:  # Nếu không có userData
                        folder = self.recent_folders_combo.itemText(i)
                        
                    # Kiểm tra đường dẫn hợp lệ trước khi lưu
                    if folder and os.path.isdir(folder):
                        self.app.config['RECENT_FOLDERS'][f"folder_{folder_count}"] = os.path.normpath(folder)
                        folder_count += 1
                
                # Save config
                if hasattr(self.app, 'config_manager'):
                    self.app.config_manager.save_config(self.app.config)
        
        # Direct approach in case app or app.config is not available
        else:
            # Try to save directly to config.ini file
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.ini')
            import configparser
            config = configparser.ConfigParser()
            
            # Load existing config if available
            if os.path.exists(config_path):
                config.read(config_path, encoding='utf-8')
            
            # Create RECENT_FOLDERS section if it doesn't exist
            if 'RECENT_FOLDERS' not in config:
                config['RECENT_FOLDERS'] = {}
            
            # Clear existing entries
            for key in list(config['RECENT_FOLDERS'].keys()):
                if key.startswith('folder_'):
                    del config['RECENT_FOLDERS'][key]
            
            # Save current folders
            for i in range(1, min(self.recent_folders_combo.count(), 11)):
                # Lấy đường dẫn đầy đủ từ userData, nếu không có thì lấy từ text
                folder = self.recent_folders_combo.itemData(i, QtCore.Qt.UserRole)
                if not folder:  # Nếu không có userData
                    folder = self.recent_folders_combo.itemText(i)
                config['RECENT_FOLDERS'][f"folder_{i-1}"] = folder
            
            # Write to file
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)
                
    except Exception as e:
        logger.error(f"Error saving recent folders to config file: {str(e)}")
        logger.error(traceback.format_exc())

def add_to_recent_folders(self, folder_path):
    """Add folder to recent folders dropdown - IMPROVED"""
    if not hasattr(self, 'recent_folders_combo'):
        logger.error("recent_folders_combo không tồn tại")
        return
            
    try:
        # Đảm bảo đường dẫn đầy đủ - chuẩn hóa đường dẫn để tránh các phiên bản khác nhau của cùng đường dẫn
        folder_path = os.path.normpath(os.path.abspath(folder_path))
        
        # Kiểm tra xem thư mục có tồn tại
        if not os.path.isdir(folder_path):
            logger.warning(f"Thư mục không tồn tại hoặc không phải thư mục: {folder_path}")
            return
                
        # Tạm thời ngắt kết nối tín hiệu để tránh kích hoạt đệ quy
        self.recent_folders_combo.blockSignals(True)
        
        # Kiểm tra xem thư mục đã có trong danh sách chưa
        found_index = -1
        for i in range(1, self.recent_folders_combo.count()):
            item_path = self.recent_folders_combo.itemData(i, QtCore.Qt.UserRole)
            if not item_path:  # Nếu không có userData, sử dụng text hiển thị
                item_path = self.recent_folders_combo.itemText(i)
                
            # Chuẩn hóa đường dẫn để so sánh chính xác
            if item_path and os.path.normpath(os.path.abspath(item_path)) == folder_path:
                found_index = i
                break
                
        # Nếu đã tìm thấy, xóa nó (sẽ được thêm vào đầu danh sách)
        if found_index != -1:
            self.recent_folders_combo.removeItem(found_index)
                
        # Thêm vào đầu danh sách (ngay sau tiêu đề)
        display_text = self.truncate_path(folder_path)
        self.recent_folders_combo.insertItem(1, display_text)
        self.recent_folders_combo.setItemData(1, folder_path, QtCore.Qt.UserRole)  # Lưu đường dẫn đầy đủ vào user data
        self.recent_folders_combo.setCurrentIndex(1)  # Chọn thư mục vừa thêm
        
        # Thiết lập tooltip để hiển thị đường dẫn đầy đủ
        self.recent_folders_combo.setToolTip(folder_path)
        
        # Giới hạn số lượng thư mục gần đây đến 5 để tránh quá nhiều
        while self.recent_folders_combo.count() > 6:  # 1 tiêu đề + 5 thư mục
            self.recent_folders_combo.removeItem(self.recent_folders_combo.count() - 1)
                
        # Bật lại tín hiệu
        self.recent_folders_combo.blockSignals(False)
                
        # Lưu vào config
        self.save_recent_folders_to_config()
    except Exception as e:
        logger.error(f"Lỗi khi thêm thư mục vào danh sách gần đây: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Đảm bảo bật lại tín hiệu ngay cả khi có lỗi
        if hasattr(self, 'recent_folders_combo'):
            self.recent_folders_combo.blockSignals(False)

def truncate_path(self, path, max_length=30):
    """Cắt ngắn đường dẫn nếu quá dài để hiển thị"""
    if not path:
        return ""
    
    try:
        # Nếu đường dẫn quá dài, cắt phần giữa và thêm ...
        if len(path) > max_length:
            # Giữ lại phần đầu và phần cuối, thêm dấu ... ở giữa
            half_length = (max_length - 3) // 2
            return path[:half_length] + "..." + path[-half_length:]
        return path
    except Exception as e:
        logger.error(f"Lỗi khi cắt ngắn đường dẫn: {str(e)}")
        return path

def count_video_files(self, folder_path):
    """
    Đếm số lượng file video trong thư mục
    
    Args:
        folder_path: Đường dẫn thư mục
            
    Returns:
        int: Số lượng file video
    """
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.webm', '.m4v', '.flv', '.wmv']
    count = 0
    
    try:
        for root, _, files in os.walk(folder_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in video_extensions:
                    count += 1
    except Exception as e:
        logger.error(f"Lỗi khi đếm file video: {str(e)}")
    
    return count

def check_ffmpeg_installed(self):
    """
    Kiểm tra xem FFmpeg có được cài đặt không
    
    Returns:
        bool: True nếu FFmpeg được cài đặt, ngược lại False
    """
    try:
        # Thử chạy lệnh ffmpeg -version
        import subprocess
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            timeout=2
        )
        return result.returncode == 0
    except:
        return False
