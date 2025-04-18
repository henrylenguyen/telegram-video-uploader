"""
Video management methods for the MainUI class
"""
import os
import logging
import traceback
import subprocess
import platform
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

from utils.main_tab import (
    display_video_info, 
    display_video_frames,
    upload_single_video,
    upload_selected_videos,
    select_all_videos,
    deselect_all_videos,
    select_unuploaded_videos
)

logger = logging.getLogger(__name__)

def update_video_list_ui(self):
    """Update video list UI with current videos"""
    if not hasattr(self, 'video_list'):
        return
    
    try:
        # Calculate pagination
        items_per_page = 10
        total_pages = max(1, (len(self.all_videos) + items_per_page - 1) // items_per_page)
        
        # Ensure current page is valid
        self.current_page = min(max(1, self.current_page), max(1, total_pages))
        
        # Calculate start and end indices for current page
        start_idx = (self.current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(self.all_videos))
        
        # Get videos for current page
        current_videos = self.all_videos[start_idx:end_idx]
        display_count = len(current_videos)
        
        # Debug log
        logger.info(f"Hiển thị {display_count} video từ vị trí {start_idx} đến {end_idx}")
        logger.info(f"Tổng số video: {len(self.all_videos)}")
        
        # Đảm bảo tất cả các hàng được xử lý (ẩn/hiện, cập nhật nội dung)
        for i in range(1, 11):
            # Get widgets
            row = self.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
            label = self.video_list.findChild(QtWidgets.QLabel, f"label{i}")
            status = self.video_list.findChild(QtWidgets.QLabel, f"status{i}")
            checkbox = self.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
            
            # Kiểm tra xem tất cả các widget cần thiết đã được tìm thấy chưa
            if row is None or label is None or status is None or checkbox is None:
                logger.warning(f"Không tìm thấy đủ các widget cho hàng {i}")
                continue
                
            # Xử lý hiển thị hoặc ẩn các hàng
            if i <= display_count:
                # Hiển thị hàng
                row.setVisible(True)
                
                # Lấy thông tin video và cập nhật nội dung
                video_idx = i - 1
                if video_idx < len(current_videos):
                    video = current_videos[video_idx]
                    
                    # Cập nhật tên và thiết lập tooltip hiển thị đầy đủ
                    video_name = video.get("name", "")
                    
                    # Lưu trữ tên đầy đủ của video vào thuộc tính của label
                    label.setProperty("fullVideoName", video_name)
                    
                    # Để các tên file dài sẽ hiển thị theo max-width 800px trong CSS
                    # Chỉ rút gọn nếu quá dài (trên 120 ký tự, tương đương với khoảng 800px)
                    MAX_FILENAME_LENGTH = 120  # Tăng độ dài tối đa trước khi cắt ngắn (tương ứng với 800px)
                    
                    # Chỉ cắt ngắn nếu tên file quá dài
                    if len(video_name) > MAX_FILENAME_LENGTH:
                        # Cắt giữa với dấu 3 chấm rõ ràng (hiển thị đầu và cuối của filename)
                        start_length = MAX_FILENAME_LENGTH * 2 // 3  # Hiển thị nhiều hơn ở đầu
                        end_length = MAX_FILENAME_LENGTH - start_length - 3  # 3 là dộ dài của dấu "..."
                        display_name = video_name[:start_length] + "..." + video_name[-end_length:]
                        label.setText(display_name)
                    else:
                        # Tên file đủ ngắn để hiển thị hoàn toàn
                        label.setText(video_name)
                    
                    # Luôn thiết lập tooltip để hiển thị tên đầy đủ khi hover
                    label.setToolTip(video_name)
                    
                    # Cập nhật trạng thái
                    status_text = "Mới"
                    status_class = "statusNew"
                    
                    if video.get("status") == "uploaded":
                        status_text = "Đã tải"
                        status_class = "statusUploaded"
                    elif video.get("status") == "duplicate":
                        status_text = "Trùng"
                        status_class = "statusDuplicate"
                    
                    status.setText(status_text)
                    status.setProperty("class", status_class)
                    
                    # Cập nhật style
                    status.style().unpolish(status)
                    status.style().polish(status)
                    
                    # Đặt trạng thái checkbox
                    checkbox.setChecked(video.get("status") == "new")
                    
                    logger.debug(f"Hiển thị video {i}: {video.get('name')}, Trạng thái: {status_text}")
                else:
                    logger.warning(f"Chỉ số video không hợp lệ: {video_idx} >= {len(current_videos)}")
            else:
                # Ẩn hàng
                row.setVisible(False)
                
                # Xóa nội dung hiện tại
                label.setText("")
                status.setText("")
                checkbox.setChecked(False)
                
                logger.debug(f"Ẩn hàng {i}")
        
        # Đảm bảo pagination frame hiển thị
        pagination_frame = self.video_list.findChild(QtWidgets.QFrame, "paginationFrame")
        if pagination_frame:
            pagination_frame.setVisible(True)
        
        # Update pagination info - ĐẢM BẢO HIỂN THỊ THÔNG TIN TỔNG SỐ VIDEO
        if hasattr(self, 'pagination_info_label') and self.pagination_info_label:
            duplicate_count = sum(1 for v in self.all_videos if v.get("status") == "duplicate")
            uploaded_count = sum(1 for v in self.all_videos if v.get("status") == "uploaded")
            
            if len(self.all_videos) > 0:
                info_text = f"Hiển thị {start_idx+1}-{end_idx} trên tổng {len(self.all_videos)} videos"
                if duplicate_count > 0:
                    info_text += f", có {duplicate_count} video trùng"
                if uploaded_count > 0:
                    info_text += f", có {uploaded_count} đã tải lên"
                self.pagination_info_label.setText(info_text)
                self.pagination_info_label.setVisible(True)
            else:
                self.pagination_info_label.setText("Không có video nào trong thư mục này")
                self.pagination_info_label.setVisible(True)
        
        # Update pagination UI with improved approach
        self._update_pagination_ui(total_pages)  # Changed back to _update_pagination_ui
        
        # Update selection count
        self.update_selection_count()
        
        # Update folder stats
        if hasattr(self, 'folder_stats_label'):
            total_size = sum(video.get("file_size_bytes", 0) for video in self.all_videos)
            size_str = self.format_file_size(total_size)
            self.folder_stats_label.setText(f"Tổng dung lượng: {size_str} | {len(self.all_videos)} videos")
            self.folder_stats_label.setVisible(True)
    
    except Exception as e:
        logger.error(f"Lỗi trong update_video_list_ui: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def debug_video_list_issue(self):
    """
    Hàm để kiểm tra và debug vấn đề chỉ hiển thị 1 video trong danh sách.
    Gọi hàm này trước khi gọi update_video_list_ui().
    """
    try:
        # Kiểm tra số lượng video trong all_videos
        logger.info(f"Tổng số video trong all_videos: {len(self.all_videos)}")
        
        # Kiểm tra trạng thái hiển thị của các hàng video
        visible_rows = 0
        for i in range(1, 11):
            row = self.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
            if row and row.isVisible():
                visible_rows += 1
        logger.info(f"Số hàng đang hiển thị: {visible_rows}")
        
        # Kiểm tra các video item có tồn tại không
        missing_items = []
        for i in range(1, 11):
            row = self.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
            if not row:
                missing_items.append(i)
        
        if missing_items:
            logger.error(f"Thiếu các videoItem: {missing_items}")
        else:
            logger.info("Tất cả videoItem đều tồn tại")
        
        # Kiểm tra phân trang
        items_per_page = 10
        total_pages = max(1, (len(self.all_videos) + items_per_page - 1) // items_per_page)
        logger.info(f"Trang hiện tại: {self.current_page}, Tổng số trang: {total_pages}")
        
        # Kiểm tra chỉ số bắt đầu và kết thúc
        start_idx = (self.current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(self.all_videos))
        logger.info(f"Chỉ số bắt đầu: {start_idx}, Chỉ số kết thúc: {end_idx}")
        
        # Kiểm tra xem các hàng có được cập nhật đúng không
        for i in range(1, 11):
            if i <= end_idx - start_idx:
                row = self.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
                label = self.video_list.findChild(QtWidgets.QLabel, f"label{i}")
                
                if row and label:
                    video_idx = start_idx + i - 1
                    if video_idx < len(self.all_videos):
                        video = self.all_videos[video_idx]
                        logger.info(f"Hàng {i}: Dự kiến hiển thị video '{video['name']}'")
                        logger.info(f"Hàng {i} thực tế: {label.text()}, Hiển thị: {row.isVisible()}")
        
        # Đảm bảo cập nhật trạng thái hiển thị của tất cả các hàng
        for i in range(1, 11):
            row = self.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
            if row:
                if i <= end_idx - start_idx:
                    row.setVisible(True)
                    logger.info(f"Đặt hàng {i} thành hiển thị")
                else:
                    row.setVisible(False)
                    logger.info(f"Đặt hàng {i} thành ẩn")
    
    except Exception as e:
        logger.error(f"Lỗi khi debug video list: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def update_selection_count(self):
    """Update the selection count in the action bar"""
    if not hasattr(self, 'selection_label'):
        return
        
    # Reset counters
    self.selected_video_count = 0
    self.selected_videos_size = 0
    
    # Count selected videos
    for i in range(1, 11):  # Assuming up to 10 videos displayed at once
        checkbox = self.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
        row = self.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
        
        # Only count if checkbox exists, is checked, and row is visible
        if checkbox and row and checkbox.isChecked() and row.isVisible():
            self.selected_video_count += 1
            
            # Find video info in all_videos
            label = self.video_list.findChild(QtWidgets.QLabel, f"label{i}")
            if label:
                video_name = label.text()
                for video in self.all_videos:
                    if video.get("name") == video_name:
                        self.selected_videos_size += video.get("file_size_bytes", 0)
                        break
    
    # Format total size
    size_str = self.format_file_size(self.selected_videos_size)
    
    # Update label
    self.selection_label.setText(f"Đã chọn: {self.selected_video_count} video | Tổng dung lượng: {size_str}")

def format_file_size(self, size_in_bytes):
    """Format file size in bytes to human-readable string"""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} GB"

def on_video_row_clicked(self, idx):
    """Handle click on a video row"""
    # Toggle checkbox
    checkbox = self.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{idx}")
    if checkbox:
        checkbox.setChecked(not checkbox.isChecked())
        logger.info(f"Toggled checkbox {idx}: {checkbox.isChecked()}")
        
        # Update selection count
        self.update_selection_count()
    
    # Get video name (use the full name stored in property instead of displayed text)
    label = self.video_list.findChild(QtWidgets.QLabel, f"label{idx}")
    if label:
        # Lấy tên đầy đủ của video từ thuộc tính đã lưu trữ
        full_video_name = label.property("fullVideoName")
        
        # Nếu không có thuộc tính, sử dụng text hiển thị (cho trường hợp cần tương thích ngược)
        if not full_video_name:
            full_video_name = label.text()
            
        self.selected_video = full_video_name
        logger.info(f"Selected video: {full_video_name}")
        
        # Display video information
        self.display_selected_video()

def display_selected_video(self):
    """Display information about the selected video"""
    if not self.selected_video:
        return
    
    # Find video path
    video_path = None
    for video in self.all_videos:
        if video.get("name") == self.selected_video:
            video_path = video.get("path")
            break
    
    if not video_path or not os.path.exists(video_path):
        logger.error(f"Video file not found: {self.selected_video}")
        return
    
    # Display video info in the preview
    display_video_info(self, video_path)
    
    # Display video frames
    display_video_frames(self, video_path)

def view_video(self):
    """Open the currently selected video in a media player"""
    if not self.selected_video:
        return
    
    # Find video path
    video_path = None
    for video in self.all_videos:
        if video.get("name") == self.selected_video:
            video_path = video.get("path")
            break
    
    if not video_path or not os.path.exists(video_path):
        logger.error(f"Video file not found: {self.selected_video}")
        return
    
    # Open video with default player
    system = platform.system()
    
    try:
        if system == "Windows":
            os.startfile(video_path)
        elif system == "Darwin":  # macOS
            subprocess.call(["open", video_path])
        else:  # Linux
            subprocess.call(["xdg-open", video_path])
            
        logger.info(f"Opened video: {video_path}")
    except Exception as e:
        logger.error(f"Error opening video: {str(e)}")
        QtWidgets.QMessageBox.warning(self, "Lỗi", f"Không thể mở video: {str(e)}")

def upload_current_video(self):
    """Upload the currently selected video"""
    if not self.selected_video:
        QtWidgets.QMessageBox.information(self, "Thông báo", "Vui lòng chọn một video!")
        return
    
    # Find video path
    video_path = None
    for video in self.all_videos:
        if video.get("name") == self.selected_video:
            video_path = video.get("path")
            break
    
    if not video_path or not os.path.exists(video_path):
        logger.error(f"Video file not found: {self.selected_video}")
        return
    
    # Use utility function to upload
    upload_single_video(self, self.selected_video, video_path)

def upload_videos(self):
    """Upload all selected videos"""
    upload_selected_videos(self)
    
    # Refresh folder after upload
    self.refresh_folder()

def select_all_videos_ui(self):
    """Select all videos in the list"""
    select_all_videos(self)
    self.update_selection_count()

def deselect_all_videos_ui(self):
    """Deselect all videos in the list"""
    deselect_all_videos(self)
    self.update_selection_count()

def select_unuploaded_videos_ui(self):
    """Select only videos that haven't been uploaded"""
    select_unuploaded_videos(self)
    self.update_selection_count()

def initialize_sort_dropdown(self):
    """
    Thiết lập dropdown sắp xếp video với tùy chọn mặc định
    """
    if not hasattr(self, 'sort_combo_box'):
        return
    
    try:
        # Xóa tất cả mục hiện tại
        self.sort_combo_box.clear()
        
        # Thêm các tùy chọn sắp xếp
        sort_options = [
            "Sắp xếp theo tên (A-Z)",  # Mặc định
            "Sắp xếp theo tên (Z-A)",
            "Kích thước (lớn → nhỏ)",
            "Kích thước (nhỏ → lớn)",
            "Thời lượng video (dài → ngắn)",
            "Thời lượng video (ngắn → dài)",
            "Ngày tạo (mới → cũ)",
            "Ngày tạo (cũ → mới)",
            "Trạng thái"
        ]
        
        for option in sort_options:
            self.sort_combo_box.addItem(option)
        
        # Thiết lập tùy chọn mặc định (A-Z)
        self.sort_combo_box.setCurrentIndex(0)
        
        # Kết nối sự kiện thay đổi
        self.sort_combo_box.currentIndexChanged.connect(self.sort_videos)
        
        # Áp dụng sắp xếp mặc định
        self.sort_videos(0)
        
        logger.info("Đã thiết lập dropdown sắp xếp thành công")
    except Exception as e:
        logger.error(f"Lỗi khi thiết lập dropdown sắp xếp: {str(e)}")
        logger.error(traceback.format_exc())

def sort_videos(self, index):
    """
    Sắp xếp video theo tiêu chí đã chọn
    
    Args:
        index: Chỉ số tùy chọn sắp xếp trong dropdown
    """
    if not hasattr(self, 'all_videos') or not self.all_videos:
        return
    
    try:
        logger.info(f"Sắp xếp videos theo tùy chọn: {index}")
        
        # Lấy text option từ combobox nếu có
        sort_text = self.sort_combo_box.currentText() if hasattr(self, 'sort_combo_box') else ""
        
        # Sắp xếp dựa trên tùy chọn
        if index == 0 or "tên (A-Z)" in sort_text:  # Tên (A-Z)
            self.all_videos.sort(key=lambda v: v.get("name", "").lower())
        elif index == 1 or "tên (Z-A)" in sort_text:  # Tên (Z-A)
            self.all_videos.sort(key=lambda v: v.get("name", "").lower(), reverse=True)
        elif index == 2 or "lớn → nhỏ" in sort_text:  # Kích thước (lớn → nhỏ)
            self.all_videos.sort(key=lambda v: v.get("file_size_bytes", 0), reverse=True)
        elif index == 3 or "nhỏ → lớn" in sort_text:  # Kích thước (nhỏ → lớn)
            self.all_videos.sort(key=lambda v: v.get("file_size_bytes", 0))
        elif index == 4 or "dài → ngắn" in sort_text:  # Thời lượng (dài → ngắn)
            self.all_videos.sort(key=lambda v: v.get("duration", 0), reverse=True)
        elif index == 5 or "ngắn → dài" in sort_text:  # Thời lượng (ngắn → dài)
            self.all_videos.sort(key=lambda v: v.get("duration", 0))
        elif index == 6 or "mới → cũ" in sort_text:  # Ngày tạo (mới → cũ)
            # Sử dụng os.path.getctime để lấy thời gian tạo file
            self.all_videos.sort(
                key=lambda v: os.path.getctime(v.get("path", "")) if os.path.exists(v.get("path", "")) else 0, 
                reverse=True
            )
        elif index == 7 or "cũ → mới" in sort_text:  # Ngày tạo (cũ → mới)
            self.all_videos.sort(
                key=lambda v: os.path.getctime(v.get("path", "")) if os.path.exists(v.get("path", "")) else 0
            )
        elif index == 8 or "Trạng thái" in sort_text:  # Trạng thái
            # Sắp xếp theo trạng thái (uploaded, duplicate, new)
            status_order = {"uploaded": 0, "duplicate": 1, "new": 2}
            self.all_videos.sort(key=lambda v: status_order.get(v.get("status", "new"), 3))
        
        # Reset về trang đầu tiên
        self.current_page = 1
        
        # Cập nhật UI
        self.update_video_list_ui()
        
        logger.info(f"Đã sắp xếp {len(self.all_videos)} videos")
    except Exception as e:
        logger.error(f"Lỗi khi sắp xếp videos: {str(e)}")
        logger.error(traceback.format_exc())

def filter_videos(self, text):
    """Filter videos by name"""
    if not text:
        # If no filter, show all videos
        self.update_video_list_ui()
        return
    
    # Filter videos by name (case insensitive)
    text = text.lower()
    filtered_videos = [v for v in self.all_videos if text in v["name"].lower()]
    
    # Replace all_videos temporarily for UI update
    saved_videos = self.all_videos
    self.all_videos = filtered_videos
    self.current_page = 1  # Reset to first page
    self.update_video_list_ui()
    self.all_videos = saved_videos

def update_pagination_ui(self, total_pages):
    """
    Cập nhật UI phân trang với cách tiếp cận đáng tin cậy hơn
    
    Args:
        total_pages: Tổng số trang
    """
    try:
        # Ghi log để debug
        logger.info(f"update_pagination_ui được gọi với tổng số trang: {total_pages}")
        
        # Find and validate pagination frame
        pagination_frame = self._find_pagination_frame()
        if not pagination_frame:
            return
        
        # Ensure UI elements exist
        self._ensure_pagination_elements(pagination_frame)
        
        # Initialize pagination manager if needed
        self._init_pagination_manager(pagination_frame, total_pages)
        
        # Update the pagination with current state
        if self.pagination_manager:
            self.pagination_manager.update_pagination(self.current_page, total_pages)
        
        # Ensure frame visibility
        pagination_frame.update()
        pagination_frame.show()
        
        # Log update completion
        logger.info(f"Cập nhật phân trang hoàn tất: trang {self.current_page}/{total_pages}")
            
    except Exception as e:
        logger.error(f"Lỗi cập nhật UI phân trang: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def _find_pagination_frame(self):
    """Find and validate the pagination frame"""
    pagination_frame = self.video_list.findChild(QtWidgets.QFrame, "paginationFrame")
    if not pagination_frame:
        logger.error("Không tìm thấy pagination frame")
        return None
    
    # Ensure frame is visible with proper height
    pagination_frame.setVisible(True)
    pagination_frame.setMinimumHeight(60)
    return pagination_frame

def _ensure_pagination_elements(self, pagination_frame):
    """Ensure all pagination UI elements exist and are visible"""
    # Find or initialize pagination info label
    if not hasattr(self, 'pagination_info_label') or not self.pagination_info_label:
        self.pagination_info_label = pagination_frame.findChild(QtWidgets.QLabel, "paginationInfoLabel")
        if self.pagination_info_label:
            self.pagination_info_label.setVisible(True)
    
    # Find or initialize navigation buttons
    self._ensure_navigation_button(pagination_frame, 'first_page_button', "firstPageButton")
    self._ensure_navigation_button(pagination_frame, 'prev_page_button', "prevPageButton")
    self._ensure_navigation_button(pagination_frame, 'next_page_button', "nextPageButton")
    self._ensure_navigation_button(pagination_frame, 'last_page_button', "lastPageButton")
    
    # Ensure proper layout
    self._ensure_pagination_layout(pagination_frame)

def _ensure_navigation_button(self, parent, attr_name, object_name):
    """Ensure a specific navigation button exists and is visible"""
    if not getattr(self, attr_name, None):
        button = parent.findChild(QtWidgets.QPushButton, object_name)
        if button:
            setattr(self, attr_name, button)
            button.setVisible(True)

def _ensure_pagination_layout(self, pagination_frame):
    """Ensure pagination frame has a proper layout"""
    pagination_layout = pagination_frame.layout()
    if not pagination_layout:
        # Create a new layout if one doesn't exist
        pagination_layout = QtWidgets.QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(15, 10, 15, 10)
        pagination_layout.setSpacing(5)
        
        # Add basic elements to the layout
        self._setup_fresh_pagination_layout(pagination_layout)

def _setup_fresh_pagination_layout(self, layout):
    """Set up a new pagination layout with basic elements"""
    # Add info label if it exists
    if self.pagination_info_label:
        layout.addWidget(self.pagination_info_label)
        layout.addStretch(1)
    
    # Add navigation buttons
    if self.first_page_button:
        layout.addWidget(self.first_page_button)
    
    if self.prev_page_button:
        layout.addWidget(self.prev_page_button)
    
    # Add placeholder for page buttons
    page_buttons_placeholder = QtWidgets.QWidget()
    page_buttons_placeholder.setObjectName("page_buttons_placeholder")
    page_buttons_placeholder.setMinimumWidth(300)  # Space for page buttons
    layout.addWidget(page_buttons_placeholder)
    
    # Add remaining navigation buttons
    if self.next_page_button:
        layout.addWidget(self.next_page_button)
    
    if self.last_page_button:
        layout.addWidget(self.last_page_button)

def _init_pagination_manager(self, pagination_frame, total_pages):
    """Initialize or update the pagination manager"""
    if not self.pagination_manager:
        # Import and create pagination manager
        from utils.pagination_utils import PaginationManager
        self.pagination_manager = PaginationManager(self)
        
        # Create page buttons
        self.pagination_manager.create_page_buttons(pagination_frame, total_pages)
        
        # Set up pagination manager
        setup_success = self.pagination_manager.setup_pagination(
            pagination_frame=pagination_frame,
            first_button=self.first_page_button,
            prev_button=self.prev_page_button,
            next_button=self.next_page_button,
            last_button=self.last_page_button,
            on_page_change=self.handle_page_change
        )
        
        if not setup_success:
            logger.error("Không thể thiết lập pagination manager")
            return
            
        logger.info("Đã khởi tạo pagination manager thành công")
    else:
        # Update existing pagination manager if needed
        if len(self.pagination_manager.page_buttons) < total_pages:
            self.pagination_manager.create_page_buttons(pagination_frame, total_pages)

def handle_page_change(self, new_page):
    """
    Xử lý khi có thay đổi trang từ pagination manager
    
    Args:
        new_page: Trang mới đã chọn
    """
    if self.current_page != new_page:
        self.current_page = new_page
        self.update_video_list_ui()

def go_to_page(self, page):
    """Go to specific page"""
    items_per_page = 10
    total_pages = (len(self.all_videos) + items_per_page - 1) // items_per_page
    
    # Ràng buộc page trong phạm vi hợp lệ
    page = max(1, min(page, total_pages))
    
    if self.current_page != page:
        self.current_page = page
        self.update_video_list_ui()

def next_page(self):
    """Go to next page"""
    items_per_page = 10
    total_pages = (len(self.all_videos) + items_per_page - 1) // items_per_page
    
    if self.current_page < total_pages:
        self.current_page += 1
        self.update_video_list_ui()

def prev_page(self):
    """Go to previous page"""
    if self.current_page > 1:
        self.current_page -= 1
        self.update_video_list_ui()

def last_page(self):
    """Go to last page"""
    items_per_page = 10
    total_pages = (len(self.all_videos) + items_per_page - 1) // items_per_page
    
    if self.current_page != total_pages:
        self.current_page = total_pages
        self.update_video_list_ui()

def update_video_preview_ui(self):
    """
    Cập nhật UI video_preview để thêm ScrollArea cho thông tin video
    """
    if not hasattr(self, 'video_preview'):
        return
        
    try:
        # Tìm info panel hiện tại
        info_panel = self.video_preview.findChild(QtWidgets.QWidget, "infoPanel")
        if not info_panel:
            logger.error("Không tìm thấy info panel")
            return
        
        # Đảm bảo chúng ta chỉ thay đổi một lần - kiểm tra nếu đã có scroll area
        scroll_area = self.video_preview.findChild(QtWidgets.QScrollArea, "infoScrollArea")
        if scroll_area:
            logger.info("ScrollArea đã tồn tại, không cần cập nhật lại")
            return
        
        # Lấy layout của info panel
        form_layout = info_panel.layout()
        if not form_layout or not isinstance(form_layout, QtWidgets.QFormLayout):
            logger.error("Form layout không hợp lệ")
            return
        
        # Tạo ScrollArea mới
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setObjectName("infoScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #F1F5F9;
                width: 8px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                min-height: 20px;
                border-radius: 4px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Tạo widget mới cho nội dung
        content_widget = QtWidgets.QWidget()
        content_widget.setObjectName("infoContent")
        
        # Tạo layout mới cho nội dung
        new_form_layout = QtWidgets.QFormLayout(content_widget)
        new_form_layout.setHorizontalSpacing(30)
        new_form_layout.setVerticalSpacing(15)
        new_form_layout.setContentsMargins(15, 15, 15, 15)
        
        # Tạo các label mới với nội dung giới hạn chiều rộng và ngắt dòng
        fields = [
            ('fileNameLabel', 'fileNameValueLabel'), 
            ('durationLabel', 'durationValueLabel'),
            ('resolutionLabel', 'resolutionValueLabel'),
            ('sizeLabel', 'sizeValueLabel'),
            ('statusLabel', 'statusValueLabel'),
            ('codecLabel', 'codecValueLabel')
        ]
        
        for label_name, value_name in fields:
            label = info_panel.findChild(QtWidgets.QLabel, label_name)
            value = info_panel.findChild(QtWidgets.QLabel, value_name)
            
            if label and value:
                # Tạo bản sao của label
                new_label = QtWidgets.QLabel(label.text())
                new_label.setObjectName(label_name)
                new_label.setProperty("class", "infoLabel")
                
                # Xử lý văn bản hợp lý cho label
                text_value = value.text()
                tooltip_text = text_value  # Lưu trữ toàn bộ text cho tooltip
                
                # Tạo bản sao của value label với xử lý text tốt hơn
                new_value = QtWidgets.QLabel(text_value)
                new_value.setObjectName(value_name)
                new_value.setProperty("class", "valueLabel")
                new_value.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Cho phép select text
                
                # Cấu hình hiển thị nhất quán cho tất cả các trường
                # Mặc định các trường chỉ dùng 1 dòng với ellipsis
                metrics = QtGui.QFontMetrics(new_value.font())
                use_ellipsis = True
                use_word_wrap = False
                field_height = 22
                max_width = 300
                
                # Xử lý đặc biệt cho tất cả các trường thông tin
                # Tất cả các trường sẽ là một dòng duy nhất với ellipsis
                field_height = 22
                
                # Xử lý trường trạng thái Trùng với để rút gọn quá dài
                if value_name == "statusValueLabel" and "Trùng với:" in text_value:
                    # Tạo văn bản rút gọn
                    parts = text_value.split("Trùng với: ")
                    if len(parts) > 1:
                        prefix = "Trùng với: "
                        items = parts[1].split(", ")
                        
                        if len(items) > 2:
                            # Chỉ giải gọn lại file đầu tiên, dùng ký tự ... thể hiện bị cắt
                            shortened_text = prefix + items[0] + "..."
                            new_value.setText(shortened_text)
                            
                # Tùy chỉnh cấu hình và style theo loại trường
                if value_name == "fileNameValueLabel":
                    # Cắt giữa cho tên file với 3 chấm ở giữa
                    # Tính toán độ dài và tạo text đã cắt bởi QFontMetrics
                    new_value.setText(metrics.elidedText(new_value.text(), Qt.ElideMiddle, 250))
                
                elif value_name == "statusValueLabel":
                    # Đảm bảo trường trạng thái hiển thị đúng với text dài 
                    # Giữa nguyên style màu sắc của trạng thái khi áp dụng ellipsis mới
                    original_style = ""
                    if value.styleSheet():
                        original_style = value.styleSheet()
                    
                    # Áp dụng style đặc biệt cho trường status - chỉ định rõ max-width
                    new_value.setStyleSheet(original_style + """
                        QLabel {
                            text-overflow: ellipsis;
                            overflow: hidden; 
                            white-space: nowrap;
                            max-width: 250px;
                        }
                    """)
                    
                    # Tạo text cắt bởi QFontMetrics - đảm bảo phần elide (3 chấm) hiển thị rõ ràng
                    # Chỉ cắt nếu chưa cắt trước đó (kiểm tra xem đã có dấu ... chưa)
                    if not new_value.text().endswith("..."):
                        new_value.setText(metrics.elidedText(new_value.text(), Qt.ElideRight, 230))
                else:
                    # Các trường thông tin khác - cắt phần cuối với ellipsis
                    new_value.setText(metrics.elidedText(new_value.text(), Qt.ElideRight, 250))
                
                # Thiết lập các thuộc tính chung
                new_value.setWordWrap(use_word_wrap)
                new_value.setMinimumHeight(field_height)
                new_value.setMaximumHeight(field_height)
                
                # Các thiết lập bổ sung cho field
                new_value.setMinimumWidth(250)
                new_value.setMaximumWidth(400)  # Chiều rộng phù hợp với text đã cắt ngắn
                
                # Luôn thiết lập tooltip để hiển thị đầy đủ nội dung
                if text_value:
                    new_value.setToolTip(tooltip_text)
                
                # Style cải tiến cho các trường thông thường
                new_value.setStyleSheet("""
                    QLabel {
                        line-height: 125%;
                        margin-top: 1px;
                        margin-bottom: 1px;
                        padding-top: 1px;
                        padding-bottom: 1px;
                        white-space: nowrap;
                        text-overflow: ellipsis;
                        overflow: hidden;
                    }
                """)
                
                # Áp dụng stylesheet tương ứng cho status label
                if value_name == "statusValueLabel" and value.styleSheet():
                    # Kết hợp stylesheet mới với stylesheet trạng thái
                    current_style = value.styleSheet()
                    new_value.setStyleSheet("""
                        QLabel {
                            line-height: 125%;
                            margin-top: 1px;
                            margin-bottom: 1px;
                            padding-top: 1px;
                            padding-bottom: 1px;
                        }
                    """ + current_style)
                
                # Thêm vào layout mới
                new_form_layout.addRow(new_label, new_value)
        
        # Đặt widget nội dung vào scroll area
        scroll_area.setWidget(content_widget)
        
        # Xóa widget info panel cũ và thay bằng scroll area
        parent_layout = info_panel.parentWidget().layout()
        parent_index = parent_layout.indexOf(info_panel)
        
        # Xóa widget cũ khỏi layout
        parent_layout.removeWidget(info_panel)
        info_panel.setParent(None)
        info_panel.deleteLater()
        
        # Thêm scroll area vào vị trí cũ
        parent_layout.insertWidget(parent_index, scroll_area)
        
        # Lưu tham chiếu mới
        self.info_scroll_area = scroll_area
        self.info_content = content_widget
        
        logger.info("Đã cập nhật thành công UI thông tin video với ScrollArea")
        
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật UI thông tin video: {str(e)}")
        logger.error(traceback.format_exc())