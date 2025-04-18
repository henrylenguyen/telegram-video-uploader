"""
Fallback UI creation methods for when the UI files fail to load
"""
import logging
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt

from ui.components.play_button import PlayButton

logger = logging.getLogger(__name__)

def create_fallback_header(self):
    """Create a simple fallback header widget when loading fails"""
    widget = QtWidgets.QWidget()
    widget.setObjectName("Header")
    widget.setMinimumHeight(70)
    widget.setMaximumHeight(70)
    
    layout = QtWidgets.QHBoxLayout(widget)
    
    logo = QtWidgets.QLabel("HENLLADEV")
    logo.setStyleSheet("font-size: 28px; font-weight: bold; color: #3498DB;")
    layout.addWidget(logo)
    
    spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    layout.addItem(spacer)
    
    return widget

def create_fallback_folder_selection(self):
    """Create a simple fallback folder selection widget when loading fails"""
    widget = QtWidgets.QWidget()
    widget.setObjectName("FolderSelection")
    
    layout = QtWidgets.QHBoxLayout(widget)
    
    label = QtWidgets.QLabel("Thư mục chứa video")
    layout.addWidget(label)
    
    self.folder_path_edit = QtWidgets.QLineEdit()
    layout.addWidget(self.folder_path_edit)
    
    self.browse_button = QtWidgets.QPushButton("Duyệt")
    layout.addWidget(self.browse_button)
    
    return widget

def create_fallback_sub_tabs(self):
    """Create a simple fallback sub-tabs widget when loading fails"""
    widget = QtWidgets.QWidget()
    widget.setObjectName("SubTabs")
    
    layout = QtWidgets.QHBoxLayout(widget)
    
    tab1 = QtWidgets.QPushButton("Tải lên thủ công")
    tab1.setObjectName("activeTab")
    layout.addWidget(tab1)
    
    tab2 = QtWidgets.QPushButton("Tự động tải lên")
    tab2.setObjectName("inactiveTab")
    layout.addWidget(tab2)
    
    spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    layout.addItem(spacer)
    
    return widget

def create_fallback_video_list(self):
    """Create a simple fallback video list widget when loading fails"""
    widget = QtWidgets.QWidget()
    widget.setObjectName("VideoList")
    
    layout = QtWidgets.QVBoxLayout(widget)
    
    title = QtWidgets.QLabel("Danh sách video")
    title.setStyleSheet("font-size: 20px; font-weight: bold;")
    layout.addWidget(title)
    
    # Add a placeholder scroll area
    scroll_area = QtWidgets.QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
    
    scroll_content = QtWidgets.QWidget()
    scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
    
    # Add placeholder message
    placeholder_label = QtWidgets.QLabel("Không thể tải danh sách video. Vui lòng kiểm tra lại.")
    placeholder_label.setAlignment(Qt.AlignCenter)
    placeholder_label.setStyleSheet("color: #64748B; font-size: 16px; padding: 20px;")
    scroll_layout.addWidget(placeholder_label)
    
    scroll_area.setWidget(scroll_content)
    layout.addWidget(scroll_area)
    
    # Store references to important controls to avoid None errors
    self.duplicate_check_box = QtWidgets.QCheckBox("Kiểm tra trùng lặp")
    self.history_check_box = QtWidgets.QCheckBox("Kiểm tra lịch sử")
    self.search_line_edit = QtWidgets.QLineEdit()
    self.sort_combo_box = QtWidgets.QComboBox()
    self.pagination_info_label = QtWidgets.QLabel()
    self.next_page_button = QtWidgets.QPushButton()
    self.prev_page_button = QtWidgets.QPushButton()
    self.first_page_button = QtWidgets.QPushButton()
    self.last_page_button = QtWidgets.QPushButton()
    
    return widget

def create_fallback_video_preview(self):
    """Create a simple fallback video preview widget when loading fails"""
    widget = QtWidgets.QWidget()
    widget.setObjectName("VideoPreview")
    
    layout = QtWidgets.QVBoxLayout(widget)
    
    title = QtWidgets.QLabel("Xem trước video")
    title.setStyleSheet("font-size: 20px; font-weight: bold;")
    layout.addWidget(title)
    
    # Create a preview frame
    preview_frame = QtWidgets.QFrame()
    preview_frame.setMinimumHeight(250)
    preview_frame.setStyleSheet("background-color: #F2F6FC; border-radius: 8px;")
    frame_layout = QtWidgets.QVBoxLayout(preview_frame)
    
    # Add custom play button
    self.play_button = PlayButton()
    frame_layout.addWidget(self.play_button, 0, Qt.AlignCenter)
    
    layout.addWidget(preview_frame)
    
    # Add buttons
    button_layout = QtWidgets.QHBoxLayout()
    self.view_button = QtWidgets.QPushButton("Xem video")
    self.view_button.setMinimumHeight(45)
    self.upload_this_button = QtWidgets.QPushButton("Tải lên video này")
    self.upload_this_button.setMinimumHeight(45)
    
    button_layout.addWidget(self.view_button)
    button_layout.addWidget(self.upload_this_button)
    
    layout.addLayout(button_layout)
    
    return widget

def create_fallback_video_frames(self):
    """Create a simple fallback video frames widget when loading fails"""
    widget = QtWidgets.QWidget()
    widget.setObjectName("VideoFrames")
    
    layout = QtWidgets.QVBoxLayout(widget)
    
    title = QtWidgets.QLabel("Các khung hình từ video")
    title.setStyleSheet("font-size: 20px; font-weight: bold;")
    layout.addWidget(title)
    
    # Create placeholder content
    placeholder = QtWidgets.QLabel("Không thể tải khung hình từ video. Vui lòng kiểm tra lại.")
    placeholder.setAlignment(Qt.AlignCenter)
    placeholder.setStyleSheet("color: #64748B; font-size: 16px; padding: 20px;")
    layout.addWidget(placeholder)
    
    return widget

def create_fallback_action_bar(self):
    """Create a simple fallback action bar widget when loading fails"""
    widget = QtWidgets.QWidget()
    widget.setObjectName("ActionBar")
    
    layout = QtWidgets.QHBoxLayout(widget)
    
    self.select_all_button = QtWidgets.QPushButton("Chọn tất cả")
    layout.addWidget(self.select_all_button)
    
    self.deselect_all_button = QtWidgets.QPushButton("Bỏ chọn tất cả")
    layout.addWidget(self.deselect_all_button)
    
    self.select_unuploaded_button = QtWidgets.QPushButton("Chọn video chưa tải lên")
    layout.addWidget(self.select_unuploaded_button)
    
    spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    layout.addItem(spacer)
    
    self.selection_label = QtWidgets.QLabel("Đã chọn: 0 video | Tổng dung lượng: 0 B")
    layout.addWidget(self.selection_label)
    
    spacer2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    layout.addItem(spacer2)
    
    self.upload_button = QtWidgets.QPushButton("Tải lên")
    layout.addWidget(self.upload_button)
    
    return widget
