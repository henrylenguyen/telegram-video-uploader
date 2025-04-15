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
        self.scroll_layout.setSpacing(10)

        # Load header
        self.header = self.load_header()
        self.main_layout.addWidget(self.header)

        # Add spacing between header and content
        spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.scroll_layout.addItem(spacer)

        # Load components into scroll area
        self.folder_selection = self.load_folder_selection()
        self.scroll_layout.addWidget(self.folder_selection)

        # Load sub-tabs (tải lên thủ công, tự động, etc.)
        self.sub_tabs = self.load_sub_tabs()
        self.scroll_layout.addWidget(self.sub_tabs)

        # Load video list and preview in a horizontal layout
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QHBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 0, 30, 0)

        self.video_list = self.load_video_list()
        content_layout.addWidget(self.video_list, 7)  # 70% width

        self.video_preview = self.load_video_preview()
        content_layout.addWidget(self.video_preview, 3)  # 30% width

        self.scroll_layout.addWidget(content_widget)

        # Load video frames
        self.video_frames = self.load_video_frames()
        self.scroll_layout.addWidget(self.video_frames)

        # Set scroll content and add to main layout
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        # Load action bar (always at bottom, not in scroll area)
        self.action_bar = self.load_action_bar()
        self.main_layout.addWidget(self.action_bar)

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

            # Make it look nice
            folder_widget.setContentsMargins(30, 10, 30, 10)

            # Add shadow effect
            self.add_shadow(folder_widget)

            # Store reference to important controls
            self.folder_path_edit = folder_widget.findChild(QtWidgets.QLineEdit, "folderPathEdit")
            self.browse_button = folder_widget.findChild(QtWidgets.QPushButton, "browseButton")

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

            # Make it look nice
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

            # Make it look nice
            frames_widget.setContentsMargins(30, 0, 30, 10)

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

            # Add shadow effect
            self.add_shadow(action_bar_widget)

            # Store reference to important controls
            self.select_all_button = action_bar_widget.findChild(QtWidgets.QPushButton, "selectAllButton")
            self.deselect_all_button = action_bar_widget.findChild(QtWidgets.QPushButton, "deselectAllButton")
            self.select_unuploaded_button = action_bar_widget.findChild(QtWidgets.QPushButton, "selectUnuploadedButton")
            self.upload_button = action_bar_widget.findChild(QtWidgets.QPushButton, "uploadButton")

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

    # Fallback UI creation methods
    def create_fallback_header(self):
        """Create a basic header as fallback"""
        header = QtWidgets.QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet("background-color: #FFFFFF; border-bottom: 1px solid #E2E8F0;")

        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(30, 0, 30, 0)

        logo = QtWidgets.QLabel("henlladev")
        logo.setStyleSheet("font-size: 24px; font-weight: bold; color: #3498DB;")
        layout.addWidget(logo)

        layout.addStretch()

        tabs_layout = QtWidgets.QHBoxLayout()
        tabs_texts = ["Tải lên", "Cài đặt", "Lịch sử", "Nhật ký", "Hướng dẫn"]

        for i, text in enumerate(tabs_texts):
            btn = QtWidgets.QPushButton(text)
            btn.setFixedSize(110, 70)

            if i == 0:  # Active tab
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #EBF5FB;
                        color: #3498DB;
                        font-weight: bold;
                        border: none;
                        border-bottom: 3px solid #3498DB;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FFFFFF;
                        color: #64748B;
                        border: none;
                    }
                """)

            tabs_layout.addWidget(btn)

        layout.addLayout(tabs_layout)

        return header

    def create_fallback_folder_selection(self):
        """Create a basic folder selection as fallback"""
        widget = QtWidgets.QWidget()
        widget.setContentsMargins(30, 10, 30, 10)
        widget.setStyleSheet("background-color: #FFFFFF; border-radius: 10px;")

        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(20, 15, 20, 15)

        title = QtWidgets.QLabel("Thư mục chứa video")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: #1E293B;")
        layout.addWidget(title)

        input_layout = QtWidgets.QHBoxLayout()

        self.folder_path_edit = QtWidgets.QLineEdit("/Users/videos")
        self.folder_path_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E4E7EB;
                border-radius: 6px;
                padding: 10px;
                background-color: #F9FAFB;
                font-size: 13px;
                color: #64748B;
            }
        """)
        self.folder_path_edit.setFixedHeight(40)
        input_layout.addWidget(self.folder_path_edit)

        self.browse_button = QtWidgets.QPushButton("Duyệt")
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 13px;
            }
        """)
        self.browse_button.setFixedWidth(100)
        self.browse_button.setFixedHeight(40)
        input_layout.addWidget(self.browse_button)

        layout.addLayout(input_layout)

        self.add_shadow(widget)
        return widget

    def create_fallback_sub_tabs(self):
        """Create basic sub-tabs as fallback"""
        widget = QtWidgets.QWidget()
        widget.setContentsMargins(30, 0, 30, 10)
        widget.setStyleSheet("background-color: #FFFFFF; border-radius: 6px;")

        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)

        tab_texts = ["Tải lên thủ công", "Tự động tải lên", "Danh sách video trùng", "Danh sách đã tải lên"]

        for i, text in enumerate(tab_texts):
            btn = QtWidgets.QPushButton(text)
            btn.setFixedHeight(40)

            if i == 0:  # Active tab
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498DB;
                        color: white;
                        border-radius: 6px;
                        font-size: 13px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #64748B;
                        border-radius: 6px;
                        font-size: 13px;
                    }
                """)

            layout.addWidget(btn)

        layout.addStretch()

        self.add_shadow(widget)
        return widget

    def create_fallback_video_list(self):
        """Create a basic video list as fallback"""
        widget = QtWidgets.QWidget()
        widget.setStyleSheet("background-color: #FFFFFF; border-radius: 10px;")

        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(20, 15, 20, 15)

        title = QtWidgets.QLabel("Danh sách video")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: #1E293B;")
        layout.addWidget(title)

        # Video list placeholder
        list_widget = QtWidgets.QListWidget()
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: #F9FAFB;
                border: 1px solid #E4E7EB;
                border-radius: 6px;
            }
        """)
        layout.addWidget(list_widget)

        self.add_shadow(widget)
        return widget

    def create_fallback_video_preview(self):
        """Create a basic video preview as fallback"""
        widget = QtWidgets.QWidget()
        widget.setStyleSheet("background-color: #FFFFFF; border-radius: 10px;")

        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(20, 15, 20, 15)

        title = QtWidgets.QLabel("Xem trước video")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: #1E293B;")
        layout.addWidget(title)

        preview = QtWidgets.QFrame()
        preview.setStyleSheet("background-color: #F9FAFB; border: 1px solid #E4E7EB; border-radius: 6px;")
        preview.setMinimumHeight(200)
        layout.addWidget(preview)

        button_layout = QtWidgets.QHBoxLayout()

        self.view_button = QtWidgets.QPushButton("Xem video")
        self.view_button.setStyleSheet("background-color: #3498DB; color: white; border-radius: 6px; padding: 10px;")
        button_layout.addWidget(self.view_button)

        self.upload_this_button = QtWidgets.QPushButton("Tải lên video này")
        self.upload_this_button.setStyleSheet("background-color: #3498DB; color: white; border-radius: 6px; padding: 10px;")
        button_layout.addWidget(self.upload_this_button)

        layout.addLayout(button_layout)

        info_title = QtWidgets.QLabel("Thông tin video")
        info_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #1E293B; margin-top: 10px;")
        layout.addWidget(info_title)

        info_frame = QtWidgets.QFrame()
        info_frame.setStyleSheet("background-color: #F9FAFB; border: 1px solid #E4E7EB; border-radius: 6px;")
        info_layout = QtWidgets.QVBoxLayout(info_frame)

        info_layout.addWidget(QtWidgets.QLabel("Tên file: family_picnic.mp4"))
        info_layout.addWidget(QtWidgets.QLabel("Thời lượng: 00:03:45"))
        info_layout.addWidget(QtWidgets.QLabel("Độ phân giải: 1920 x 1080"))
        info_layout.addWidget(QtWidgets.QLabel("Kích thước: 42.5 MB"))

        layout.addWidget(info_frame)

        self.add_shadow(widget)
        return widget

    def create_fallback_video_frames(self):
        """Create basic video frames section as fallback"""
        widget = QtWidgets.QWidget()
        widget.setContentsMargins(30, 30, 30, 30)
        widget.setStyleSheet("background-color: #FFFFFF; border-radius: 8px;")

        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 15)

        title = QtWidgets.QLabel("Các khung hình từ video")
        title.setStyleSheet("font-weight: bold; font-size: 20px; color: #1E293B;")
        layout.addWidget(title)

        # Scroll area for frames
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        scroll.setMinimumHeight(350)  # Set minimum height to ensure frames are visible

        frames_widget = QtWidgets.QWidget()
        frames_layout = QtWidgets.QHBoxLayout(frames_widget)
        frames_layout.setSpacing(15)
        frames_layout.setContentsMargins(10, 10, 10, 10)

        # Create 5 frame placeholders
        for _ in range(5):
            frame = QtWidgets.QFrame()
            frame.setMinimumSize(200, 200)
            frame.setMinimumHeight(200)  # Ensure minimum height
            frame.setMaximumHeight(350)  # Limit maximum height
            frame.setStyleSheet("background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px;")
            frames_layout.addWidget(frame)

        frames_layout.addStretch()
        scroll.setWidget(frames_widget)
        layout.addWidget(scroll)

        self.add_shadow(widget)
        return widget

    def create_fallback_action_bar(self):
        """Create a basic action bar as fallback"""
        widget = QtWidgets.QWidget()
        widget.setContentsMargins(30, 5, 30, 10)
        widget.setStyleSheet("background-color: #FFFFFF; border-radius: 6px;")
        widget.setFixedHeight(40)

        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(5)

        self.select_all_button = QtWidgets.QPushButton("Chọn tất cả")
        self.select_all_button.setStyleSheet("""
            QPushButton {
                background-color: #EBF5FB;
                border: 1px solid #BFDBFE;
                color: #3498DB;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.select_all_button)

        self.deselect_all_button = QtWidgets.QPushButton("Bỏ chọn tất cả")
        self.deselect_all_button.setStyleSheet("""
            QPushButton {
                background-color: #EBF5FB;
                border: 1px solid #BFDBFE;
                color: #3498DB;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.deselect_all_button)

        self.select_unuploaded_button = QtWidgets.QPushButton("Chọn video chưa tải lên")
        self.select_unuploaded_button.setStyleSheet("""
            QPushButton {
                background-color: #EBF5FB;
                border: 1px solid #BFDBFE;
                color: #3498DB;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.select_unuploaded_button)

        layout.addStretch()

        selection_label = QtWidgets.QLabel("Đã chọn: 2 video")
        selection_label.setStyleSheet("color: #64748B; font-size: 13px;")
        layout.addWidget(selection_label)

        layout.addStretch()

        self.upload_button = QtWidgets.QPushButton("Tải lên")
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
                min-width: 150px;
            }
        """)
        layout.addWidget(self.upload_button)

        self.add_shadow(widget)
        return widget

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

    # Slot methods
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
        # Implementation would depend on your video list widget

    def deselect_all_videos(self):
        """Deselect all videos in the list"""
        logger.info("Deselecting all videos")
        # Implementation would depend on your video list widget

    def select_unuploaded_videos(self):
        """Select only videos that haven't been uploaded"""
        logger.info("Selecting unuploaded videos")
        # Implementation would depend on your video list widget

    def upload_selected_videos(self):
        """Upload all selected videos"""
        logger.info("Uploading selected videos")
        # Implementation would connect to your upload logic

# Run the application if executed directly
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec_())