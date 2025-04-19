"""
Main UI module for Telegram Video Uploader PyQt5 version.
This is the entry point that imports and uses all other UI modules.
"""
import sys
import os
import logging
import traceback
from PyQt5 import QtWidgets, QtCore, QtGui

# Import UI components
from ui.components.loading_overlay import LoadingOverlay
from ui.components.play_button import PlayButton

# Import UI initialization methods
from ui.main_tab.main_ui_init import (
    apply_global_stylesheet,
    load_ui_components,
    get_ui_dir,
    fix_ui_file,
    update_cursor_properties,
    load_header,
    load_folder_selection,
    load_sub_tabs,
    load_video_list,
    load_video_preview,
    load_video_frames,
    load_action_bar
)

# Import fallback UI methods
from ui.main_tab.main_ui_fallbacks import (
    create_fallback_header,
    create_fallback_folder_selection,
    create_fallback_sub_tabs,
    create_fallback_video_list,
    create_fallback_video_preview,
    create_fallback_video_frames,
    create_fallback_action_bar
)

# Import folder management methods
from ui.main_tab.main_ui_folder import (
    initialize_folder,
    browse_folder,
    refresh_folder,
    refresh_folder_with_loading,
    show_loading_overlay,
    load_recent_folder,
    load_recent_folders_from_config,
    save_recent_folders_to_config,
    add_to_recent_folders,
    truncate_path,
    count_video_files,
    check_ffmpeg_installed
)

# Import video management methods
from ui.main_tab.main_ui_video import (
    update_video_list_ui,
    debug_video_list_issue,
    update_selection_count,
    format_file_size,
    on_video_row_clicked,
    display_selected_video,
    view_video,
    upload_current_video,
    upload_videos,
    select_all_videos_ui,
    deselect_all_videos_ui,
    select_unuploaded_videos_ui,
    initialize_sort_dropdown,
    sort_videos,
    filter_videos,
    update_pagination_ui,
    handle_page_change,
    go_to_page,
    next_page,
    prev_page,
    last_page,
    update_video_preview_ui
)

# Import event handlers
from ui.main_tab.main_ui_events import (
    connect_signals,
    header_tab_clicked,
    subtab_clicked
)
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MainUI")

class MainUI(QtWidgets.QMainWindow):
    """Main UI class that loads components directly from .ui files"""

    def __init__(self, app_instance=None):
        super(MainUI, self).__init__()

        # Store reference to the main application (if provided)
        self.app = app_instance

        # Data storage for videos
        self.all_videos = []  # Stores all video information
        self.videos = {}      # Maps video names to paths
        self.selected_video = None  # Currently selected video
        self.frame_paths = []  # Paths to video frames
        self.current_page = 1  # Current pagination page
        self.selected_video_count = 0  # Number of selected videos
        self.selected_videos_size = 0  # Total size of selected videos

        # Khởi tạo pagination manager
        self.pagination_manager = None

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

        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self.central_widget)
        self.loading_overlay.resize(self.central_widget.size())

        try:
            # Log module information
            logger.info(f"Module path: {__file__}")
            logger.info(f"PyQt5 imported: {QtWidgets.__file__}")
            
            # Load UI components from .ui files
            self.load_ui_components()

            # Connect signals
            self.connect_signals()
            
            # Update cursor properties
            self.update_cursor_properties()

            # Initialize video list
            self.initialize_folder()

            logger.info("Main UI initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing UI: {str(e)}")
            logger.error(traceback.format_exc())
            QtWidgets.QMessageBox.critical(self, "Error", f"Error initializing UI: {str(e)}")

    # Bind imported methods to the class
    # UI initialization
    apply_global_stylesheet = apply_global_stylesheet
    load_ui_components = load_ui_components
    get_ui_dir = get_ui_dir
    fix_ui_file = fix_ui_file
    update_cursor_properties = update_cursor_properties
    load_header = load_header
    load_folder_selection = load_folder_selection
    load_sub_tabs = load_sub_tabs
    load_video_list = load_video_list
    load_video_preview = load_video_preview
    load_video_frames = load_video_frames
    load_action_bar = load_action_bar
    
    # Fallback UI
    create_fallback_header = create_fallback_header
    create_fallback_folder_selection = create_fallback_folder_selection
    create_fallback_sub_tabs = create_fallback_sub_tabs
    create_fallback_video_list = create_fallback_video_list
    create_fallback_video_preview = create_fallback_video_preview
    create_fallback_video_frames = create_fallback_video_frames
    create_fallback_action_bar = create_fallback_action_bar
    
    # Folder management
    initialize_folder = initialize_folder
    browse_folder = browse_folder
    refresh_folder = refresh_folder
    refresh_folder_with_loading = refresh_folder_with_loading
    show_loading_overlay = show_loading_overlay
    load_recent_folder = load_recent_folder
    load_recent_folders_from_config = load_recent_folders_from_config
    save_recent_folders_to_config = save_recent_folders_to_config
    add_to_recent_folders = add_to_recent_folders
    truncate_path = truncate_path
    count_video_files = count_video_files
    check_ffmpeg_installed = check_ffmpeg_installed
    
    # Video management
    update_video_list_ui = update_video_list_ui
    debug_video_list_issue = debug_video_list_issue
    update_selection_count = update_selection_count
    format_file_size = format_file_size
    on_video_row_clicked = on_video_row_clicked
    display_selected_video = display_selected_video
    view_video = view_video
    upload_current_video = upload_current_video
    upload_videos = upload_videos
    select_all_videos_ui = select_all_videos_ui
    deselect_all_videos_ui = deselect_all_videos_ui
    select_unuploaded_videos_ui = select_unuploaded_videos_ui
    initialize_sort_dropdown = initialize_sort_dropdown
    sort_videos = sort_videos
    filter_videos = filter_videos
    _update_pagination_ui = update_pagination_ui
    handle_page_change = handle_page_change
    go_to_page = go_to_page
    next_page = next_page
    prev_page = prev_page
    last_page = last_page
    update_video_preview_ui = update_video_preview_ui
    
    # Event handlers
    connect_signals = connect_signals
    header_tab_clicked = header_tab_clicked
    subtab_clicked = subtab_clicked

    def resizeEvent(self, event):
        """Handle resize event to update loading overlay size"""
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.resize(self.central_widget.size())
        super(MainUI, self).resizeEvent(event)

    def apply_global_stylesheet(self):
        """Apply global stylesheet to the application"""
        stylesheet_path = os.path.join(os.path.dirname(__file__), "..", "qt_designer", "styles.qss")
        try:
            with open(stylesheet_path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            logger.error(f"Không thể áp dụng stylesheet: {str(e)}")
            
    def loadCustomUi(self, ui_path, target_widget):
        """Tải file UI vào widget đích"""
        try:
            # Đảm bảo đường dẫn UI hợp lệ
            if not os.path.exists(ui_path):
                logger.error(f"File UI không tồn tại: {ui_path}")
                return False
                
            # Tạo QFile từ đường dẫn
            temp_file = None
            try:
                # Sửa đường dẫn Windows sang Unix nếu cần (do PyQt6 trên Qt Designer có thể gây lỗi)
                with open(ui_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Ghi nội dung vào file tạm
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(suffix=".ui", delete=False)
                temp_file.write(content.encode("utf-8"))
                temp_file.close()
                
                # Load UI từ file tạm
                from PyQt5 import uic
                uic.loadUi(temp_file.name, target_widget)
                
                logger.info(f"Đã tải UI file {ui_path} thành công")
                return True
                
            finally:
                # Xóa file tạm nếu tồn tại
                if temp_file and os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
                    
        except Exception as e:
            logger.error(f"Lỗi khi tải UI: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

# Run the application if executed directly
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec_())
