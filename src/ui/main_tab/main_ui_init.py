"""
UI initialization methods for the MainUI class
"""
import os
import logging
import traceback
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtCore import Qt

from ui.components.play_button import PlayButton

logger = logging.getLogger(__name__)

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
        
        QToolTip {
            background-color: #4a4a4a;
            color: white;
            border: 1px solid #343434;
            border-radius: 4px;
            padding: 4px;
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

        # Remove bottom margin to fit with sub-tabs
        folder_widget.setContentsMargins(30, 10, 30, 0)

        # Store reference to important controls
        self.folder_path_edit = folder_widget.findChild(QtWidgets.QLineEdit, "directoryLineEdit")
        self.browse_button = folder_widget.findChild(QtWidgets.QPushButton, "browseButton")
        self.refresh_button = folder_widget.findChild(QtWidgets.QPushButton, "refreshButton")
        self.recent_folders_combo = folder_widget.findChild(QtWidgets.QComboBox, "recentFoldersComboBox")
        self.folder_stats_label = folder_widget.findChild(QtWidgets.QLabel, "folderStatsLabel")
        
        # Clear mock data in recent folders combo
        self.recent_folders_combo.clear()
        self.recent_folders_combo.addItem("Thư mục gần đây")
        
        # Add tooltip to recent folders dropdown
        self.recent_folders_combo.setToolTip("Chọn thư mục từ danh sách thư mục gần đây")
        
        # Clear folder stats
        if self.folder_stats_label:
            self.folder_stats_label.setText("Tổng dung lượng: 0 B | 0 videos")

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
            button.setEnabled(True)  # Ensure all buttons are enabled
        
        # Store button group
        self.subtab_group = tab_button_group

        # Remove top margin to fit with folder selection
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
        
        # Clear mock data from video list
        for i in range(1, 11):
            videoItem = list_widget.findChild(QtWidgets.QFrame, f"videoItem{i}")
            label = list_widget.findChild(QtWidgets.QLabel, f"label{i}")
            status = list_widget.findChild(QtWidgets.QLabel, f"status{i}")
            checkbox = list_widget.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
            
            if videoItem:
                videoItem.setVisible(False)  # Hide all rows initially
            
            if label:
                label.setText("")  # Clear label text
            
            if status:
                status.setText("")  # Clear status
            
            if checkbox:
                checkbox.setChecked(False)  # Uncheck all checkboxes
            
            # Make entire row clickable to toggle checkbox and select video
            if videoItem:
                videoItem.mousePressEvent = lambda event, idx=i: self.on_video_row_clicked(idx)

        # Clear pagination info
        pagination_info = list_widget.findChild(QtWidgets.QLabel, "paginationInfoLabel")
        if pagination_info:
            pagination_info.setText("Hiển thị 0-0 trên tổng 0 videos")

        # Store references to controls
        self.duplicate_check_box = list_widget.findChild(QtWidgets.QCheckBox, "duplicateCheckBox")
        self.history_check_box = list_widget.findChild(QtWidgets.QCheckBox, "historyCheckBox")
        self.search_line_edit = list_widget.findChild(QtWidgets.QLineEdit, "searchLineEdit")
        self.sort_combo_box = list_widget.findChild(QtWidgets.QComboBox, "sortComboBox")
        self.pagination_info_label = list_widget.findChild(QtWidgets.QLabel, "paginationInfoLabel")
        
        # Get pagination buttons
        self.page1_button = None
        self.page2_button = None
        self.next_page_button = list_widget.findChild(QtWidgets.QPushButton, "nextPageButton")
        self.prev_page_button = list_widget.findChild(QtWidgets.QPushButton, "prevPageButton")
        self.first_page_button = list_widget.findChild(QtWidgets.QPushButton, "firstPageButton")
        self.last_page_button = list_widget.findChild(QtWidgets.QPushButton, "lastPageButton")

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
        
        # Clear mock data
        for field in ['fileNameValueLabel', 'durationValueLabel', 'resolutionValueLabel', 
                    'sizeValueLabel', 'statusValueLabel', 'codecValueLabel']:
            label = preview_widget.findChild(QtWidgets.QLabel, field)
            if label:
                label.setText("")

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

        return preview_widget
    except Exception as e:
        logger.error(f"Failed to load video preview UI: {str(e)}")
        logger.error(traceback.format_exc())
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

        # Prepare frame widgets for easy access and clear any existing content
        for i in range(1, 6):  # 5 frame containers
            frame_widget = frames_widget.findChild(QtWidgets.QFrame, f"frame{i}")
            if frame_widget:
                # Clear existing content and setup layout
                if frame_widget.layout():
                    while frame_widget.layout().count():
                        item = frame_widget.layout().takeAt(0)
                        widget = item.widget()
                        if widget:
                            widget.deleteLater()
                else:
                    layout = QtWidgets.QVBoxLayout(frame_widget)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setAlignment(QtCore.Qt.AlignCenter)

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
        self.selection_label = action_bar_widget.findChild(QtWidgets.QLabel, "selectionLabel")
        
        # Clear mock data
        if self.selection_label:
            self.selection_label.setText("Đã chọn: 0 video | Tổng dung lượng: 0 B")

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

def get_ui_dir(self):
    """Get the directory containing UI files"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "..", "qt_designer", "main_tab")

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
        
        # Fix property="cursor" issues
        content = content.replace('property="cursor"', 'property="cursorShape"')
        
        # Fix alignment property for buttons
        content = content.replace('property="alignment"', 'property="alignmentProperty"')

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

def update_cursor_properties(self):
    """Update cursor properties for all interactive elements"""
    # List of widgets that should have pointing hand cursor
    if hasattr(self, 'browse_button') and self.browse_button:
        self.browse_button.setCursor(QtCore.Qt.PointingHandCursor)
    
    if hasattr(self, 'refresh_button') and self.refresh_button:
        self.refresh_button.setCursor(QtCore.Qt.PointingHandCursor)
    
    if hasattr(self, 'view_button') and self.view_button:
        self.view_button.setCursor(QtCore.Qt.PointingHandCursor)
    
    if hasattr(self, 'play_button') and self.play_button:
        self.play_button.setCursor(QtCore.Qt.PointingHandCursor)
    
    if hasattr(self, 'upload_this_button') and self.upload_this_button:
        self.upload_this_button.setCursor(QtCore.Qt.PointingHandCursor)
    
    if hasattr(self, 'select_all_button') and self.select_all_button:
        self.select_all_button.setCursor(QtCore.Qt.PointingHandCursor)
    
    if hasattr(self, 'deselect_all_button') and self.deselect_all_button:
        self.deselect_all_button.setCursor(QtCore.Qt.PointingHandCursor)
    
    if hasattr(self, 'select_unuploaded_button') and self.select_unuploaded_button:
        self.select_unuploaded_button.setCursor(QtCore.Qt.PointingHandCursor)
    
    if hasattr(self, 'upload_button') and self.upload_button:
        self.upload_button.setCursor(QtCore.Qt.PointingHandCursor)
    
    # Handle video rows
    if hasattr(self, 'video_list'):
        for i in range(1, 11):
            videoItem = self.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
            if videoItem:
                videoItem.setCursor(QtCore.Qt.PointingHandCursor)
    
    # Handle video frames
    if hasattr(self, 'video_frames'):
        for i in range(1, 6):
            frame = self.video_frames.findChild(QtWidgets.QFrame, f"frame{i}")
            if frame:
                frame.setCursor(QtCore.Qt.PointingHandCursor)
                
    # Handle pagination buttons
    if hasattr(self, 'next_page_button') and self.next_page_button:
        self.next_page_button.setCursor(QtCore.Qt.PointingHandCursor)
    if hasattr(self, 'prev_page_button') and self.prev_page_button:
        self.prev_page_button.setCursor(QtCore.Qt.PointingHandCursor)
    if hasattr(self, 'first_page_button') and self.first_page_button:
        self.first_page_button.setCursor(QtCore.Qt.PointingHandCursor)
    if hasattr(self, 'last_page_button') and self.last_page_button:
        self.last_page_button.setCursor(QtCore.Qt.PointingHandCursor)
        
    # Handle tab buttons
    if hasattr(self, 'header_tab_group'):
        for button in self.header_tab_group.buttons():
            button.setCursor(QtCore.Qt.PointingHandCursor)
            
    if hasattr(self, 'subtab_group'):
        for button in self.subtab_group.buttons():
            button.setCursor(QtCore.Qt.PointingHandCursor)
