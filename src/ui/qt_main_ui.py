import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui, uic

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MainUI")

class MainUI(QtWidgets.QMainWindow):
    """Main UI class that loads components directly from .ui files"""

    def __init__(self, app_instance=None):
        super(MainUI, self).__init__()

        # Store reference to the main application (if provided)
        self.app = app_instance

        # Set window properties
        self.setWindowTitle("Telegram Video Uploader")
        self.resize(1200, 800)

        # Set window to maximize on startup
        self.showMaximized()

        # Apply global stylesheet
        self.apply_global_stylesheet()

        # Create main widget and layout
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Load UI components from .ui files
        self.load_ui_components()

        # Connect signals
        self.connect_signals()

        logger.info("Main UI initialized successfully")

    def apply_global_stylesheet(self):
        """Apply global stylesheet to maintain the beautiful design"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #F9FAFB;
                font-family: Arial;
            }

            QPushButton {
                border-radius: 4px;
            }

            QPushButton:hover {
                cursor: pointer;
            }

            QLineEdit {
                padding: 8px;
            }

            QScrollArea {
                border: none;
                background-color: transparent;
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

            QScrollBar:horizontal {
                border: none;
                background: #F1F5F9;
                height: 8px;
                border-radius: 4px;
            }

            QScrollBar::handle:horizontal {
                background: #CBD5E1;
                min-width: 20px;
                border-radius: 4px;
            }

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }

            /* Video list alternating colors */
            QFrame#videoItem1, QFrame#videoItem3, QFrame#videoItem5 {
                background-color: #FFFFFF;
            }
            
            QFrame#videoItem2, QFrame#videoItem4 {
                background-color: #F8FAFC;
            }
            
            QFrame#videoItem:hover {
                background-color: #F1F5F9;
            }
            
            /* Status tags center alignment */
            QLabel.statusNew, QLabel.statusDuplicate, QLabel.statusUploaded {
                qproperty-alignment: AlignCenter;
            }
        """)

    def load_ui_components(self):
        """Load all UI components from .ui files and assemble them"""
        # Main scroll area to enable scrolling for the whole content
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        # Container for all components
        self.scroll_content = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(0)  # Set to 0 to remove all spacing between components

        # Load header
        self.header = self.load_header()
        self.main_layout.addWidget(self.header)

        # Group folder selection and sub-tabs without spacing
        folder_tabs_container = QtWidgets.QWidget()
        folder_tabs_layout = QtWidgets.QVBoxLayout(folder_tabs_container)
        folder_tabs_layout.setContentsMargins(0, 0, 0, 0)
        folder_tabs_layout.setSpacing(0)  # No spacing between these components

        # Load folder selection and add to the group
        self.folder_selection = self.load_folder_selection()
        folder_tabs_layout.addWidget(self.folder_selection)

        # Load sub-tabs and add to the group
        self.sub_tabs = self.load_sub_tabs()
        folder_tabs_layout.addWidget(self.sub_tabs)

        # Add the grouped container to main layout
        self.scroll_layout.addWidget(folder_tabs_container)

        # Add spacing after the folder+tabs group
        spacer = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.scroll_layout.addItem(spacer)

        # Load video list and preview in a horizontal layout
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QHBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 0, 30, 0)

        self.video_list = self.load_video_list()
        content_layout.addWidget(self.video_list, 7)  # 70% width

        self.video_preview = self.load_video_preview()
        content_layout.addWidget(self.video_preview, 3)  # 30% width

        self.scroll_layout.addWidget(content_widget)

        # Load video frames with proper height
        self.video_frames = self.load_video_frames()
        self.scroll_layout.addWidget(self.video_frames)

        # Set scroll content and add to main layout
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        # Load action bar (always at bottom, not in scroll area)
        self.action_bar = self.load_action_bar()
        self.main_layout.addWidget(self.action_bar)

        # Apply additional styling and fixes
        self.apply_ui_fixes()

    def apply_ui_fixes(self):
        """Apply all the requested fixes to the UI components"""
        # Fix 1: Force white background on header with !important rule
        self.header.setStyleSheet(self.header.styleSheet() + """
            QWidget#Header {
                background-color: #FFFFFF !important;
            }
        """)
        
        # Fix 2 & 3: Style sub-tabs like header navbar
        if hasattr(self, 'sub_tabs'):
            # Make sub-tabs look like header tabs
            self.sub_tabs.setStyleSheet("""
                QWidget#SubTabs {
                    background-color: #FFFFFF;
                    border-radius: 0px;
                    border-top: none;
                }
                
                QPushButton#activeTab, QPushButton#inactiveTab {
                    border-radius: 0px;
                    padding: 0px 20px;
                    font-size: 16px;
                    min-width: 180px; 
                    qproperty-alignment: AlignCenter;
                }
                
                QPushButton#activeTab {
                    color: #3498DB;
                    border-bottom: 3px solid #3498DB;
                    background-color: #EBF5FB;
                    font-weight: bold;
                }
                
                QPushButton#inactiveTab {
                    color: #64748B;
                    background-color: transparent;
                }
                
                QPushButton#inactiveTab:hover {
                    color: #3498DB;
                    background-color: #F5F9FF;
                }
            """)
            
            # Make all tabs same width and apply center alignment
            for button in self.sub_tabs.findChildren(QtWidgets.QPushButton):
                button.setFixedWidth(180)
                button.setStyleSheet(button.styleSheet() + """
                    qproperty-alignment: AlignCenter;
                    border-radius: 0px;
                """)
        
        # Fix 4: Làm lại phần phân trang và giữ border như ảnh 3
        if hasattr(self, 'video_list'):
            # Cập nhật phần phân trang
            pagination_frame = self.video_list.findChild(QtWidgets.QFrame, "paginationFrame")
            if pagination_frame:
                pagination_frame.setStyleSheet("""
                    background-color: #FFFFFF;
                    border-top: 1px solid #E2E8F0;
                """)
                
                # Cập nhật các nút phân trang
                page_buttons = []
                for name in ["firstPageButton", "prevPageButton", "page1Button", "page2Button", "nextPageButton", "lastPageButton"]:
                    button = pagination_frame.findChild(QtWidgets.QPushButton, name)
                    if button:
                        page_buttons.append(button)
                        
                # Áp dụng style cho các nút
                for button in page_buttons:
                    if button.objectName() == "page1Button":
                        button.setStyleSheet("""
                            background-color: #3498DB;
                            color: white;
                            border: 1px solid #3498DB;
                            border-radius: 4px;
                            padding: 5px 10px;
                            font-size: 12px;
                            min-width: 30px;
                            max-width: 30px;
                            min-height: 30px;
                            max-height: 30px;
                            qproperty-alignment: AlignCenter;
                        """)
                    else:
                        button.setStyleSheet("""
                            background-color: #FFFFFF;
                            color: #64748B;
                            border: 1px solid #E2E8F0;
                            border-radius: 4px;
                            padding: 5px 10px;
                            font-size: 12px;
                            min-width: 30px;
                            max-width: 30px;
                            min-height: 30px;
                            max-height: 30px;
                            qproperty-alignment: AlignCenter;
                        """)
                    button.setCursor(QtCore.Qt.PointingHandCursor)
        
        # Fix 5: Đảm bảo video frames hiển thị đúng (cao 300px, cách trên dưới 20px)
        if hasattr(self, 'video_frames'):
            # Cập nhật margins để cách trên dưới 20px
            self.video_frames.setContentsMargins(30, 20, 30, 20)
            
            # Cập nhật chiều cao cho frames
            frames_scroll_area = self.video_frames.findChild(QtWidgets.QScrollArea, "framesScrollArea")
            if frames_scroll_area:
                frames_scroll_area.setMinimumHeight(350)
                
                # Cập nhật nội dung scroll area
                scroll_content = frames_scroll_area.widget()
                if scroll_content:
                    scroll_content.setMinimumHeight(350)
                    
                    # Cập nhật từng frame
                    for i in range(1, 6):
                        frame = scroll_content.findChild(QtWidgets.QFrame, f"frame{i}")
                        if frame:
                            frame.setMinimumHeight(300)
                            frame.setMaximumHeight(300)
                            frame.setFixedHeight(300)
                            frame.setStyleSheet("""
                                min-height: 300px;
                                max-height: 300px;
                                background-color: #FFFFFF;
                                border: 2px solid #E2E8F0;
                                border-radius: 6px;
                            """)

    def load_header(self):
        """Load header component from .ui file"""
        ui_path = os.path.join(self.get_ui_dir(), "header.ui")

        # Fix UI file before loading
        fixed_ui_path = self.fix_ui_file(ui_path)

        # Create widget and load UI
        header_widget = QtWidgets.QWidget()
        try:
            uic.loadUi(fixed_ui_path, header_widget)
            logger.info("Header UI loaded successfully")

            # Bỏ nền xám cho header
            header_widget.setStyleSheet(header_widget.styleSheet() + """
                QWidget#Header {
                    background-color: #FFFFFF !important;
                    border-bottom: 1px solid #E2E8F0;
                }
            """)

            # Add shadow effect
            self.add_shadow(header_widget)

            return header_widget
        except Exception as e:
            logger.error(f"Failed to load header UI: {str(e)}")
            # Fallback to a basic header if loading fails
            return self.create_fallback_header()

    def load_folder_selection(self):
        """Load folder selection component from .ui file"""
        ui_path = os.path.join(self.get_ui_dir(), "folder_selection.ui")

        # Fix UI file before loading
        fixed_ui_path = self.fix_ui_file(ui_path)

        # Create widget and load UI
        folder_widget = QtWidgets.QWidget()
        try:
            uic.loadUi(fixed_ui_path, folder_widget)
            logger.info("Folder selection UI loaded successfully")

            # Bỏ margin bottom để sát với sub-tabs
            folder_widget.setContentsMargins(30, 10, 30, 0)

            # Add shadow effect
            self.add_shadow(folder_widget)

            # Store reference to important controls
            self.folder_path_edit = folder_widget.findChild(QtWidgets.QLineEdit, "directoryLineEdit")
            self.browse_button = folder_widget.findChild(QtWidgets.QPushButton, "browseButton")
            
            # Thêm cursor pointer cho nút browse
            if self.browse_button:
                self.browse_button.setCursor(QtCore.Qt.PointingHandCursor)

            return folder_widget
        except Exception as e:
            logger.error(f"Failed to load folder selection UI: {str(e)}")
            # Fallback to a basic folder selection if loading fails
            return self.create_fallback_folder_selection()

    def load_sub_tabs(self):
        """Load sub-tabs component from .ui file"""
        ui_path = os.path.join(self.get_ui_dir(), "sub_tabs.ui")

        # Fix UI file before loading
        fixed_ui_path = self.fix_ui_file(ui_path)

        # Create widget and load UI
        tabs_widget = QtWidgets.QWidget()
        try:
            uic.loadUi(fixed_ui_path, tabs_widget)
            logger.info("Sub-tabs UI loaded successfully")

            # Làm giống navbar ở header
            tabs_widget.setStyleSheet("""
                QWidget#SubTabs {
                    background-color: #FFFFFF;
                    border-radius: 0px;
                }
                
                QPushButton#activeTab, QPushButton#inactiveTab {
                    border-radius: 0px;
                    padding: 0px 20px;
                    font-size: 16px;
                    min-width: 180px;
                    qproperty-alignment: AlignCenter;
                }
                
                QPushButton#activeTab {
                    color: #3498DB;
                    border-bottom: 3px solid #3498DB;
                    background-color: #EBF5FB;
                    font-weight: bold;
                }
                
                QPushButton#inactiveTab {
                    color: #64748B;
                    background-color: transparent;
                }
                
                QPushButton#inactiveTab:hover {
                    color: #3498DB;
                    background-color: #F5F9FF;
                }
            """)

            # Đảm bảo các nút con có style đúng
            for button in tabs_widget.findChildren(QtWidgets.QPushButton):
                button.setFixedWidth(180)
                button.setCursor(QtCore.Qt.PointingHandCursor)

            # Bỏ margin top để sát với folder selection
            tabs_widget.setContentsMargins(30, 0, 30, 10)

            # Add shadow effect
            self.add_shadow(tabs_widget)

            return tabs_widget
        except Exception as e:
            logger.error(f"Failed to load sub-tabs UI: {str(e)}")
            # Fallback to basic sub-tabs if loading fails
            return self.create_fallback_sub_tabs()

    def load_video_list(self):
        """Load video list component from .ui file"""
        ui_path = os.path.join(self.get_ui_dir(), "video_list.ui")

        # Fix UI file before loading
        fixed_ui_path = self.fix_ui_file(ui_path)

        # Create widget and load UI
        list_widget = QtWidgets.QWidget()
        try:
            uic.loadUi(fixed_ui_path, list_widget)
            logger.info("Video list UI loaded successfully")

            # Giữ border như ảnh 3
            list_widget.setStyleSheet(list_widget.styleSheet() + """
                QFrame#videoItem {
                    border-bottom: 1px solid #E2E8F0;
                }
                
                QLabel.statusNew, QLabel.statusDuplicate, QLabel.statusUploaded {
                    qproperty-alignment: AlignCenter;
                }
            """)

            # Tạo hiệu ứng alternating rows và làm cả hàng clickable
            for i in range(1, 6):
                videoItem = list_widget.findChild(QtWidgets.QFrame, f"videoItem{i}")
                if videoItem:
                    if i % 2 == 0:  # Even rows
                        videoItem.setStyleSheet("""
                            background-color: #F8FAFC;
                            border-bottom: 1px solid #E2E8F0;
                        """)
                    else:  # Odd rows
                        videoItem.setStyleSheet("""
                            background-color: #FFFFFF;
                            border-bottom: 1px solid #E2E8F0;
                        """)
                    
                    # Làm cả hàng có thể click để toggle checkbox
                    videoItem.mousePressEvent = lambda event, idx=i: self.toggle_checkbox(idx)
                    videoItem.setCursor(QtCore.Qt.PointingHandCursor)

            # Add shadow effect
            self.add_shadow(list_widget)

            return list_widget
        except Exception as e:
            logger.error(f"Failed to load video list UI: {str(e)}")
            # Fallback to a basic video list if loading fails
            return self.create_fallback_video_list()

    def load_video_preview(self):
        """Load video preview component from .ui file"""
        ui_path = os.path.join(self.get_ui_dir(), "video_preview.ui")

        # Fix UI file before loading
        fixed_ui_path = self.fix_ui_file(ui_path)

        # Create widget and load UI
        preview_widget = QtWidgets.QWidget()
        try:
            uic.loadUi(fixed_ui_path, preview_widget)
            logger.info("Video preview UI loaded successfully")

            # Add shadow effect
            self.add_shadow(preview_widget)

            # Store reference to important controls
            self.view_button = preview_widget.findChild(QtWidgets.QPushButton, "viewVideoButton")
            self.upload_this_button = preview_widget.findChild(QtWidgets.QPushButton, "uploadThisVideoButton")
            
            # Thêm cursor pointer cho các nút
            if self.view_button:
                self.view_button.setCursor(QtCore.Qt.PointingHandCursor)
            if self.upload_this_button:
                self.upload_this_button.setCursor(QtCore.Qt.PointingHandCursor)

            return preview_widget
        except Exception as e:
            logger.error(f"Failed to load video preview UI: {str(e)}")
            # Fallback to a basic video preview if loading fails
            return self.create_fallback_video_preview()

    def load_video_frames(self):
        """Load video frames component from .ui file"""
        ui_path = os.path.join(self.get_ui_dir(), "video_frames.ui")

        # Fix UI file before loading
        fixed_ui_path = self.fix_ui_file(ui_path)

        # Create widget and load UI
        frames_widget = QtWidgets.QWidget()
        try:
            uic.loadUi(fixed_ui_path, frames_widget)
            logger.info("Video frames UI loaded successfully")

            # Đặt margin top/bottom 20px
            frames_widget.setContentsMargins(30, 20, 30, 20)
            
            # Đảm bảo chiều cao của frames là 300px
            frames_scroll_area = frames_widget.findChild(QtWidgets.QScrollArea, "framesScrollArea")
            if frames_scroll_area:
                frames_scroll_area.setMinimumHeight(350)
                
                scroll_content = frames_scroll_area.widget()
                if scroll_content:
                    scroll_content.setMinimumHeight(350)
                    
                    for i in range(1, 6):
                        frame = scroll_content.findChild(QtWidgets.QFrame, f"frame{i}")
                        if frame:
                            frame.setMinimumHeight(300)
                            frame.setMaximumHeight(300)
                            frame.setFixedHeight(300)
                            frame.setStyleSheet("""
                                min-height: 300px;
                                max-height: 300px;
                                background-color: #FFFFFF;
                                border: 2px solid #E2E8F0;
                                border-radius: 6px;
                            """)

            # Add shadow effect
            self.add_shadow(frames_widget)

            return frames_widget
        except Exception as e:
            logger.error(f"Failed to load video frames UI: {str(e)}")
            # Fallback to a basic video frames if loading fails
            return self.create_fallback_video_frames()

    def load_action_bar(self):
        """Load action bar component from .ui file"""
        ui_path = os.path.join(self.get_ui_dir(), "action_bar.ui")

        # Fix UI file before loading
        fixed_ui_path = self.fix_ui_file(ui_path)

        # Create widget and load UI
        action_bar_widget = QtWidgets.QWidget()
        try:
            uic.loadUi(fixed_ui_path, action_bar_widget)
            logger.info("Action bar UI loaded successfully")

            # Make it look nice
            action_bar_widget.setContentsMargins(30, 5, 30, 10)

            # Store reference to important controls
            self.select_all_button = action_bar_widget.findChild(QtWidgets.QPushButton, "selectAllButton")
            self.deselect_all_button = action_bar_widget.findChild(QtWidgets.QPushButton, "deselectAllButton")
            self.select_unuploaded_button = action_bar_widget.findChild(QtWidgets.QPushButton, "selectUnuploadedButton")
            self.upload_button = action_bar_widget.findChild(QtWidgets.QPushButton, "uploadButton")
            
            # Thêm cursor pointer cho các nút
            for button in [self.select_all_button, self.deselect_all_button, 
                          self.select_unuploaded_button, self.upload_button]:
                if button:
                    button.setCursor(QtCore.Qt.PointingHandCursor)

            # Add shadow effect
            self.add_shadow(action_bar_widget)

            return action_bar_widget
        except Exception as e:
            logger.error(f"Failed to load action bar UI: {str(e)}")
            # Fallback to a basic action bar if loading fails
            return self.create_fallback_action_bar()

    # Helper methods
    def get_ui_dir(self):
        """Get the directory containing UI files"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "qt_designer", "main_tab")

    def fix_ui_file(self, ui_path):
        """Fix UI file compatibility issues with PyQt5"""
        # Check if file exists
        if not os.path.exists(ui_path):
            logger.error(f"UI file not found: {ui_path}")
            return ui_path

        try:
            with open(ui_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix orientation attributes
            content = content.replace('Qt::Orientation::Horizontal', 'Horizontal')
            content = content.replace('Qt::Orientation::Vertical', 'Vertical')

            # Create a temporary file with fixed content
            import tempfile
            temp = tempfile.NamedTemporaryFile(delete=False, suffix='.ui')
            temp_path = temp.name

            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Fixed UI file {ui_path} -> {temp_path}")
            return temp_path
        except Exception as e:
            logger.error(f"Error fixing UI file {ui_path}: {str(e)}")
            return ui_path

    def add_shadow(self, widget):
        """Add shadow effect to a widget"""
        try:
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QtGui.QColor(0, 0, 0, 30))
            shadow.setOffset(0, 2)
            widget.setGraphicsEffect(shadow)
        except Exception as e:
            logger.warning(f"Could not add shadow effect: {str(e)}")

    def toggle_checkbox(self, idx):
        """Toggle checkbox when clicking anywhere in the row"""
        checkbox = self.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{idx}")
        if checkbox:
            checkbox.setChecked(not checkbox.isChecked())
            logger.info(f"Toggled checkbox {idx}: {checkbox.isChecked()}")

    # Fallback UI creation methods (các phương thức fallback giữ nguyên)
    # ...

    def connect_signals(self):
        """Connect signals to slots"""
        # Connect folder selection browse button if found
        if hasattr(self, 'browse_button'):
            self.browse_button.clicked.connect(self.browse_folder)

        # Connect other buttons if found
        if hasattr(self, 'view_button'):
            self.view_button.clicked.connect(self.view_video)

        if hasattr(self, 'upload_this_button'):
            self.upload_this_button.clicked.connect(self.upload_current_video)

        if hasattr(self, 'select_all_button'):
            self.select_all_button.clicked.connect(self.select_all_videos)

        if hasattr(self, 'deselect_all_button'):
            self.deselect_all_button.clicked.connect(self.deselect_all_videos)

        if hasattr(self, 'select_unuploaded_button'):
            self.select_unuploaded_button.clicked.connect(self.select_unuploaded_videos)

        if hasattr(self, 'upload_button'):
            self.upload_button.clicked.connect(self.upload_selected_videos)

    # Slot methods - Chỉ giữ lại trích dẫn không có tính năng thực
    def browse_folder(self):
        """Open file dialog to browse for folder"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Chọn thư mục chứa video", "",
            QtWidgets.QFileDialog.ShowDirsOnly
        )

        if folder and hasattr(self, 'folder_path_edit'):
            self.folder_path_edit.setText(folder)
            logger.info(f"Selected folder: {folder}")

    def view_video(self):
        """Open the currently selected video in a media player"""
        logger.info("Opening video player")
        # Implementation would depend on your video playback method

    def upload_current_video(self):
        """Upload the currently previewed video"""
        logger.info("Uploading current video")
        # Implementation would connect to your upload logic

    def select_all_videos(self):
        """Select all videos in the list"""
        logger.info("Selecting all videos")
        if hasattr(self, 'video_list'):
            for i in range(1, 6):  # Assuming 5 videos in the list
                checkbox = self.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
                if checkbox:
                    checkbox.setChecked(True)

    def deselect_all_videos(self):
        """Deselect all videos in the list"""
        logger.info("Deselecting all videos")
        if hasattr(self, 'video_list'):
            for i in range(1, 6):  # Assuming 5 videos in the list
                checkbox = self.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
                if checkbox:
                    checkbox.setChecked(False)

    def select_unuploaded_videos(self):
        """Select only videos that haven't been uploaded"""
        logger.info("Selecting unuploaded videos")
        if hasattr(self, 'video_list'):
            for i in range(1, 6):  # Assuming 5 videos in the list
                status = self.video_list.findChild(QtWidgets.QLabel, f"status{i}")
                checkbox = self.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
                
                if status and checkbox:
                    # Select if status is "Mới" or not "Đã tải"
                    if status.text() == "Mới" or status.text() != "Đã tải":
                        checkbox.setChecked(True)
                    else:
                        checkbox.setChecked(False)

    def upload_selected_videos(self):
        """Upload all selected videos"""
        logger.info("Uploading selected videos")
        if hasattr(self, 'video_list'):
            selected_count = 0
            selected_videos = []
            
            for i in range(1, 6):  # Assuming 5 videos in the list
                checkbox = self.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
                label = self.video_list.findChild(QtWidgets.QLabel, f"label{i}")
                
                if checkbox and checkbox.isChecked() and label:
                    selected_count += 1
                    selected_videos.append(label.text())
                    
            logger.info(f"Uploading {selected_count} videos: {selected_videos}")
            # Implementation would connect to your upload logic

# Run the application if executed directly
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec_())