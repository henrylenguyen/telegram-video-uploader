import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtGui import QPainter, QColor, QPen, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MainUI")

class PlayButton(QtWidgets.QPushButton):
    """Custom play button with SVG-like triangle using QPainter"""
    
    def __init__(self, parent=None):
        super(PlayButton, self).__init__(parent)
        # Set size
        self.setFixedSize(70, 70)
        self.setCursor(Qt.PointingHandCursor)
        # No text
        self.setText("")
        # Default colors
        self.background_color = QColor("#3498DB")
        self.icon_color = QColor(255, 255, 255)
        # Update visuals
        self.update()
        
    def paintEvent(self, event):
        """Custom paint event to draw the play button"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw rounded background
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.background_color)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 25, 25)
        
        # Draw play triangle
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.icon_color)
        
        # Create a triangle polygon
        # Slightly offset to right to account for visual weight
        width = self.width()
        height = self.height()
        triangle_width = width * 0.4
        triangle_height = height * 0.4
        
        # Center the triangle within the button
        center_x = width / 2 + width * 0.03  # Slight right adjustment
        center_y = height / 2
        
        # Create triangle points
        triangle = QPolygonF()
        triangle.append(QPointF(center_x - triangle_width/2, center_y - triangle_height/2))
        triangle.append(QPointF(center_x + triangle_width/2, center_y))
        triangle.append(QPointF(center_x - triangle_width/2, center_y + triangle_height/2))
        
        # Draw the triangle
        painter.drawPolygon(triangle)
        
    def enterEvent(self, event):
        """Handle hover state"""
        self.background_color = QColor("#2980B9")
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle end of hover state"""
        self.background_color = QColor("#3498DB")
        self.update()
        super().leaveEvent(event)

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

        # Add 20px spacing after header
        spacer_after_header = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addItem(spacer_after_header)

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

            # Set up tab button group to handle exclusive selection
            tab_button_group = QtWidgets.QButtonGroup(header_widget)
            
            # Find all tab buttons
            tab_buttons = header_widget.findChildren(QtWidgets.QPushButton)
            
            # Add buttons to group and set initial state
            for i, button in enumerate(tab_buttons):
                tab_button_group.addButton(button, i)
                button.setCursor(QtCore.Qt.PointingHandCursor)
                
                # Set first button as checked by default
                if i == 0:
                    button.setChecked(True)
            
            # Store button group
            self.header_tab_group = tab_button_group

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

            # Set up tab button group to handle exclusive selection
            tab_button_group = QtWidgets.QButtonGroup(tabs_widget)
            
            # Find all tab buttons
            tab_buttons = tabs_widget.findChildren(QtWidgets.QPushButton)
            
            # Add buttons to group and set cursor
            for i, button in enumerate(tab_buttons):
                tab_button_group.addButton(button, i)
                button.setCursor(QtCore.Qt.PointingHandCursor)
                button.setEnabled(True)  # Ensure all buttons are enabled
            
            # Store button group
            self.subtab_group = tab_button_group

            # Bỏ margin top để sát với folder selection
            tabs_widget.setContentsMargins(30, 0, 30, 10)

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

            # Make rows clickable
            for i in range(1, 11):  # Increased to 10 for more mock data
                videoItem = list_widget.findChild(QtWidgets.QFrame, f"videoItem{i}")
                if videoItem:
                    # Make entire row clickable to toggle checkbox
                    videoItem.mousePressEvent = lambda event, idx=i: self.toggle_checkbox(idx)
                    videoItem.setCursor(QtCore.Qt.PointingHandCursor)

            # Add shadow effect
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QtGui.QColor(0, 0, 0, 30))
            shadow.setOffset(0, 2)
            list_widget.setGraphicsEffect(shadow)

            # Add bottom margin to prevent shadow clipping
            list_widget.setContentsMargins(
                list_widget.contentsMargins().left(),
                list_widget.contentsMargins().top(),
                list_widget.contentsMargins().right(),
                list_widget.contentsMargins().bottom() + 15
            )

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

            # Add custom SVG play button
            play_button_container = preview_widget.findChild(QtWidgets.QWidget, "playButtonContainer")
            if play_button_container:
                layout = QtWidgets.QVBoxLayout(play_button_container)
                layout.setContentsMargins(0, 0, 0, 0)
                
                # Create and add the custom play button
                self.play_button = PlayButton(play_button_container)
                layout.addWidget(self.play_button)
                
                # Connect click handler
                self.play_button.clicked.connect(self.view_video)

            # Add shadow effect
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QtGui.QColor(0, 0, 0, 30))
            shadow.setOffset(0, 2)
            preview_widget.setGraphicsEffect(shadow)

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

            # Add padding to scroll area for proper scrolling
            frames_scroll_area = frames_widget.findChild(QtWidgets.QScrollArea, "framesScrollArea")
            if frames_scroll_area:
                frames_scroll_area.setStyleSheet("""
                    QScrollArea {
                        padding: 15px;
                        border: none;
                    }
                    
                    QScrollArea > QWidget > QWidget {
                        padding: 15px;
                    }
                """)

            # Add shadow effect
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QtGui.QColor(0, 0, 0, 30))
            shadow.setOffset(0, 2)
            frames_widget.setGraphicsEffect(shadow)

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
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QtGui.QColor(0, 0, 0, 30))
            shadow.setOffset(0, 2)
            action_bar_widget.setGraphicsEffect(shadow)

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

    def toggle_checkbox(self, idx):
        """Toggle checkbox when clicking anywhere in the row"""
        checkbox = self.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{idx}")
        if checkbox:
            checkbox.setChecked(not checkbox.isChecked())
            logger.info(f"Toggled checkbox {idx}: {checkbox.isChecked()}")

    # Fallback UI creation methods
    def create_fallback_header(self):
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
        widget = QtWidgets.QWidget()
        widget.setObjectName("VideoList")
        
        layout = QtWidgets.QVBoxLayout(widget)
        
        title = QtWidgets.QLabel("Danh sách video")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        # Would add more elements here in a real implementation
        
        return widget
    
    def create_fallback_video_preview(self):
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
        widget = QtWidgets.QWidget()
        widget.setObjectName("VideoFrames")
        
        layout = QtWidgets.QVBoxLayout(widget)
        
        title = QtWidgets.QLabel("Các khung hình từ video")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        # Would add more elements here in a real implementation
        
        return widget
    
    def create_fallback_action_bar(self):
        widget = QtWidgets.QWidget()
        widget.setObjectName("ActionBar")
        
        layout = QtWidgets.QHBoxLayout(widget)
        
        self.select_all_button = QtWidgets.QPushButton("Chọn tất cả")
        layout.addWidget(self.select_all_button)
        
        self.deselect_all_button = QtWidgets.QPushButton("Bỏ chọn tất cả")
        layout.addWidget(self.deselect_all_button)
        
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addItem(spacer)
        
        self.upload_button = QtWidgets.QPushButton("Tải lên")
        layout.addWidget(self.upload_button)
        
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
            
        # Connect header tab buttons
        if hasattr(self, 'header_tab_group'):
            self.header_tab_group.buttonClicked.connect(self.header_tab_clicked)
            
        # Connect sub-tab buttons
        if hasattr(self, 'subtab_group'):
            self.subtab_group.buttonClicked.connect(self.subtab_clicked)
            
        # Connect play button in video preview if found
        if hasattr(self, 'play_button'):
            self.play_button.clicked.connect(self.view_video)

    def header_tab_clicked(self, button):
        """Handle header tab button clicks"""
        # Set clicked button as checked, others as unchecked
        for btn in self.header_tab_group.buttons():
            btn.setChecked(btn == button)
        
        # Switch stack widget based on button index
        index = self.header_tab_group.id(button)
        logger.info(f"Header tab {index} clicked: {button.text()}")
        
    def subtab_clicked(self, button):
        """Handle sub-tab button clicks"""
        # Set clicked button as checked, others as unchecked
        for btn in self.subtab_group.buttons():
            if btn.objectName() == "activeTab":
                btn.setObjectName("inactiveTab")
                btn.setStyleSheet("")  # Remove any custom style
            
        # Set the clicked button as active
        button.setObjectName("activeTab")
        button.setStyleSheet("""
            color: #3498DB;
            border-bottom: 3px solid #3498DB;
            background-color: #EBF5FB;
            font-weight: bold;
        """)
        
        logger.info(f"Sub-tab clicked: {button.text()}")

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
        if hasattr(self, 'video_list'):
            for i in range(1, 11):  # Increased to 10 for more items
                checkbox = self.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
                if checkbox:
                    checkbox.setChecked(True)

    def deselect_all_videos(self):
        """Deselect all videos in the list"""
        logger.info("Deselecting all videos")
        if hasattr(self, 'video_list'):
            for i in range(1, 11):  # Increased to 10 for more items
                checkbox = self.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
                if checkbox:
                    checkbox.setChecked(False)

    def select_unuploaded_videos(self):
        """Select only videos that haven't been uploaded"""
        logger.info("Selecting unuploaded videos")
        if hasattr(self, 'video_list'):
            for i in range(1, 11):  # Increased to 10 for more items
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
            
            for i in range(1, 11):  # Increased to 10 for more items
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