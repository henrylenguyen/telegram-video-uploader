"""
Event handlers and signal connections for the MainUI class
"""
import logging
from PyQt5 import QtWidgets, QtCore

logger = logging.getLogger(__name__)

def connect_signals(self):
    """Connect signals to slots"""
    try:
        # Connect folder selection browse button if found
        if hasattr(self, 'browse_button') and self.browse_button:
            self.browse_button.clicked.connect(self.browse_folder)

        # Connect refresh button
        if hasattr(self, 'refresh_button') and self.refresh_button:
            self.refresh_button.clicked.connect(self.refresh_folder)

        # Connect view buttons
        if hasattr(self, 'view_button') and self.view_button:
            self.view_button.clicked.connect(self.view_video)

        if hasattr(self, 'play_button') and self.play_button:
            self.play_button.clicked.connect(self.view_video)

        # Connect upload buttons
        if hasattr(self, 'upload_this_button') and self.upload_this_button:
            self.upload_this_button.clicked.connect(self.upload_current_video)

        if hasattr(self, 'upload_button') and self.upload_button:
            self.upload_button.clicked.connect(self.upload_videos)

        # Connect selection buttons
        if hasattr(self, 'select_all_button') and self.select_all_button:
            self.select_all_button.clicked.connect(self.select_all_videos_ui)

        if hasattr(self, 'deselect_all_button') and self.deselect_all_button:
            self.deselect_all_button.clicked.connect(self.deselect_all_videos_ui)

        if hasattr(self, 'select_unuploaded_button') and self.select_unuploaded_button:
            self.select_unuploaded_button.clicked.connect(self.select_unuploaded_videos_ui)
            
        # Connect header tab buttons
        if hasattr(self, 'header_tab_group') and self.header_tab_group:
            self.header_tab_group.buttonClicked.connect(self.header_tab_clicked)
            
        # Connect sub-tab buttons
        if hasattr(self, 'subtab_group') and self.subtab_group:
            self.subtab_group.buttonClicked.connect(self.subtab_clicked)
        
        # Connect check boxes for video filtering
        if hasattr(self, 'duplicate_check_box') and self.duplicate_check_box:
            self.duplicate_check_box.stateChanged.connect(self.refresh_folder)
            
        if hasattr(self, 'history_check_box') and self.history_check_box:
            self.history_check_box.stateChanged.connect(self.refresh_folder)
            
        # Connect recent folders combo box
        if hasattr(self, 'recent_folders_combo') and self.recent_folders_combo:
            self.recent_folders_combo.currentIndexChanged.connect(self.load_recent_folder)
            
        # Connect search line edit
        if hasattr(self, 'search_line_edit') and self.search_line_edit:
            self.search_line_edit.textChanged.connect(self.filter_videos)
            
        # Connect sort combo box
        if hasattr(self, 'sort_combo_box') and self.sort_combo_box:
            self.sort_combo_box.currentIndexChanged.connect(self.sort_videos)
            
        # Connect pagination buttons
        if hasattr(self, 'next_page_button') and self.next_page_button:
            self.next_page_button.clicked.connect(self.next_page)
        if hasattr(self, 'prev_page_button') and self.prev_page_button:
            self.prev_page_button.clicked.connect(self.prev_page)
        if hasattr(self, 'first_page_button') and self.first_page_button:
            self.first_page_button.clicked.connect(lambda: self.go_to_page(1))
        if hasattr(self, 'last_page_button') and self.last_page_button:
            self.last_page_button.clicked.connect(self.last_page)
            
        logger.info("All signals connected successfully")
    except Exception as e:
        logger.error(f"Error connecting signals: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def header_tab_clicked(self, button):
    """Handle header tab button clicks"""
    # Set clicked button as checked, others as unchecked
    for btn in self.header_tab_group.buttons():
        btn.setChecked(btn == button)
    
    # Get the index of the clicked button
    index = self.header_tab_group.id(button)
    
    # Log the click
    logger.info(f"Header tab {index} clicked: {button.text()}")
    
    # Handle different tabs
    if index == 0:  # Upload tab
        # Already on this tab, do nothing
        pass
    else:
        # For other tabs, show development message
        QtWidgets.QMessageBox.information(
            self, 
            "Chức năng đang phát triển", 
            f"Chức năng '{button.text()}' đang được phát triển và sẽ có sẵn trong phiên bản tiếp theo."
        )
        
        # Reset to upload tab
        for btn in self.header_tab_group.buttons():
            if self.header_tab_group.id(btn) == 0:
                btn.setChecked(True)
            else:
                btn.setChecked(False)

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
    
    # Get the index of the clicked button
    index = self.subtab_group.id(button)
    
    # Log the click
    logger.info(f"Sub-tab clicked: {button.text()}")
    
    # Handle different sub-tabs
    if index == 0:  # Manual upload
        # Already on this tab, do nothing
        pass
    else:
        # For other sub-tabs, show development message
        QtWidgets.QMessageBox.information(
            self, 
            "Chức năng đang phát triển", 
            f"Chức năng '{button.text()}' đang được phát triển và sẽ có sẵn trong phiên bản tiếp theo."
        )
        
        # Reset to manual upload tab
        for btn in self.subtab_group.buttons():
            if self.subtab_group.id(btn) == 0:
                btn.setObjectName("activeTab")
                btn.setStyleSheet("""
                    color: #3498DB;
                    border-bottom: 3px solid #3498DB;
                    background-color: #EBF5FB;
                    font-weight: bold;
                """)
            else:
                btn.setObjectName("inactiveTab")
                btn.setStyleSheet("")
