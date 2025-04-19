"""
Module to handle pagination utilities for the UI components with improved reliability.
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
import logging

# Configure logger
logger = logging.getLogger(__name__)

class PaginationManager:
    """
    Manager for handling pagination with direct button management.
    Follows this pattern:
    [<<] [<] [1] [2] ... [current-1] [current] [current+1] ... [last-1] [last] [>] [>>]
    """
    
    def __init__(self, parent=None):
        """
        Initialize the pagination manager.
        
        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.current_page = 1
        self.total_pages = 1
        self.page_buttons = []        # List to track page number buttons
        self.ellipsis_labels = []     # List to track ellipsis labels
        self.first_page_button = None
        self.prev_page_button = None
        self.next_page_button = None
        self.last_page_button = None
        self.pagination_frame = None
        self.on_page_change_callback = None
        self.button_container = None  # Container for page buttons
        self.button_layout = None     # Layout for page buttons
        
        # Update styles - làm rõ với font bold hơn và kích thước lớn hơn
        self.active_page_style = """
            background-color: #3498DB; 
            color: white; 
            font-weight: bold; 
            border-radius: 4px; 
            min-width: 36px; 
            min-height: 36px; 
            max-width: 36px; 
            max-height: 36px;
            font-size: 14px;
        """
        
        self.inactive_page_style = """
            background-color: #FFFFFF; 
            color: #333; 
            border-radius: 4px; 
            min-width: 36px; 
            min-height: 36px; 
            max-width: 36px; 
            max-height: 36px;
            border: 1px solid #E2E8F0;
            font-size: 14px;
        """
        
        self.disabled_button_style = """
            background-color: #e0e0e0; 
            color: #a0a0a0; 
            border-radius: 4px; 
            min-width: 36px; 
            min-height: 36px; 
            max-width: 36px; 
            max-height: 36px;
            font-size: 14px;
        """
    
    def setup_pagination(self, pagination_frame, first_button, prev_button, next_button, last_button, on_page_change=None):
        """
        Setup pagination controls with improved error handling.
        
        Args:
            pagination_frame: Frame containing pagination controls
            first_button: First page button (<<)
            prev_button: Previous page button (<)
            next_button: Next page button (>)
            last_button: Last page button (>>)
            on_page_change: Callback when page changes
        """
        try:
            self.pagination_frame = pagination_frame
            self.first_page_button = first_button
            self.prev_page_button = prev_button
            self.next_page_button = next_button
            self.last_page_button = last_button
            self.on_page_change_callback = on_page_change
            
            # Connect navigation button signals
            if self.first_page_button:
                try:
                    self.first_page_button.clicked.disconnect()  # Disconnect existing
                except:
                    pass  # Ignore if no connections
                self.first_page_button.clicked.connect(self.go_to_first_page)
                self.first_page_button.setCursor(QtCore.Qt.PointingHandCursor)
            
            if self.prev_page_button:
                try:
                    self.prev_page_button.clicked.disconnect()
                except:
                    pass
                self.prev_page_button.clicked.connect(self.go_to_prev_page)
                self.prev_page_button.setCursor(QtCore.Qt.PointingHandCursor)
            
            if self.next_page_button:
                try:
                    self.next_page_button.clicked.disconnect()
                except:
                    pass
                self.next_page_button.clicked.connect(self.go_to_next_page)
                self.next_page_button.setCursor(QtCore.Qt.PointingHandCursor)
            
            if self.last_page_button:
                try:
                    self.last_page_button.clicked.disconnect()
                except:
                    pass
                self.last_page_button.clicked.connect(self.go_to_last_page)
                self.last_page_button.setCursor(QtCore.Qt.PointingHandCursor)
            
            # Find container for page buttons
            self.button_container = pagination_frame.findChild(QtWidgets.QWidget, "pageButtonsContainer")
            if not self.button_container:
                # Create container if not found
                self.button_container = QtWidgets.QWidget(pagination_frame)
                self.button_container.setObjectName("pageButtonsContainer")
                self.button_container.setMinimumWidth(300)
                self.button_container.setMinimumHeight(40)
                
                # Find position to insert container
                pagination_layout = pagination_frame.layout()
                if pagination_layout:
                    # Try to insert between prev and next buttons
                    prev_index = -1
                    next_index = -1
                    
                    for i in range(pagination_layout.count()):
                        item = pagination_layout.itemAt(i)
                        if item and item.widget() == prev_button:
                            prev_index = i
                        if item and item.widget() == next_button:
                            next_index = i
                    
                    if prev_index != -1 and next_index != -1 and prev_index < next_index:
                        pagination_layout.insertWidget(prev_index + 1, self.button_container)
                    else:
                        # Add after prev button if found
                        if prev_index != -1:
                            pagination_layout.insertWidget(prev_index + 1, self.button_container)
                        else:
                            # Add at a reasonable position
                            pagination_layout.insertWidget(max(1, pagination_layout.count() - 2), self.button_container)
            
            # Create layout for page buttons if needed
            if not self.button_layout or self.button_layout.parent() != self.button_container:
                # Clear any existing layout
                while self.button_container.layout():
                    old_layout = self.button_container.layout()
                    # Remove all widgets
                    while old_layout.count():
                        item = old_layout.takeAt(0)
                        if item.widget():
                            item.widget().setParent(None)
                    # Remove layout
                    QtWidgets.QWidget().setLayout(old_layout)
                    
                # Create new layout
                self.button_layout = QtWidgets.QHBoxLayout(self.button_container)
                self.button_layout.setContentsMargins(0, 0, 0, 0)
                self.button_layout.setSpacing(1)
                self.button_layout.setAlignment(Qt.AlignCenter)
            
            # Make sure container is visible
            self.button_container.setVisible(True)
            self.button_container.raise_()
            
            logger.info("Pagination setup successful")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up pagination: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def create_page_buttons(self, parent, total_pages=1):
        """
        Create all page buttons directly with improved button styling and z-order.
        
        Args:
            parent: Parent widget
            total_pages: Maximum number of pages to create
        """
        try:
            # Clear existing buttons
            self._clear_page_buttons()
            
            # Ensure total_pages is at least 1
            total_pages = max(1, total_pages)
            
            # Make sure button container exists
            if not self.button_container:
                # Find existing container or create new one
                self.button_container = parent.findChild(QtWidgets.QWidget, "pageButtonsContainer")
                if not self.button_container:
                    self.button_container = QtWidgets.QWidget(parent)
                    self.button_container.setObjectName("pageButtonsContainer")
                    self.button_container.setMinimumWidth(300)
                    self.button_container.setMinimumHeight(40)
                    
            # Make sure the button container has proper styling
            self.button_container.setStyleSheet("background-color: transparent;")
            
            # Ensure layout exists
            if not self.button_layout or self.button_layout.parent() != self.button_container:
                # Remove old layout if it exists
                if self.button_container.layout():
                    old_layout = self.button_container.layout()
                    # Clear layout
                    while old_layout.count():
                        item = old_layout.takeAt(0)
                        if item.widget():
                            item.widget().setParent(None)
                    # Delete layout
                    QtWidgets.QWidget().setLayout(old_layout)
                    
                # Create new layout
                self.button_layout = QtWidgets.QHBoxLayout(self.button_container)
                self.button_layout.setContentsMargins(0, 0, 0, 0)
                self.button_layout.setSpacing(1)
                self.button_layout.setAlignment(Qt.AlignCenter)
            
            # Create page buttons - create enough for all pages
            for i in range(1, total_pages + 1):
                # Create button with specific styling
                btn = QtWidgets.QPushButton(str(i), self.button_container)
                btn.setObjectName(f"pageButton{i}")
                btn.setFixedSize(36, 36)
                btn.setStyleSheet(self.inactive_page_style)
                btn.setCursor(QtCore.Qt.PointingHandCursor)
                btn.setVisible(False)  # Initially hidden
                
                # Connect click handler with a fixed reference to prevent garbage collection
                # Using a partial function to fix the page number
                page_num = i  # Create local variable to avoid lambda capture issue
                btn.clicked.connect(lambda checked=False, p=page_num: self.go_to_page(p))
                
                # Store button
                self.page_buttons.append(btn)
                
                # Log button creation
                logger.debug(f"Created page button {i}")
            
            # Create ellipsis buttons (only need max 2)
            for i in range(2):
                # Create ellipsis button
                ellipsis = QtWidgets.QPushButton("...", self.button_container)
                ellipsis.setObjectName(f"ellipsisButton{i}")
                ellipsis.setFixedSize(36, 36)
                ellipsis.setStyleSheet(self.inactive_page_style)
                ellipsis.setCursor(QtCore.Qt.PointingHandCursor)
                ellipsis.setVisible(False)  # Initially hidden
                
                # Store button
                self.ellipsis_labels.append(ellipsis)
            
            # Connect ellipsis buttons if created
            if len(self.ellipsis_labels) >= 2:
                # Left ellipsis jumps back 5 pages
                self.ellipsis_labels[0].clicked.connect(lambda: self.go_to_page(max(1, self.current_page - 5)))
                # Right ellipsis jumps forward 5 pages
                self.ellipsis_labels[1].clicked.connect(lambda: self.go_to_page(min(self.total_pages, self.current_page + 5)))
            
            # Make container visible
            self.button_container.setVisible(True)
            self.button_container.raise_()  # Bring to front
            
            logger.info(f"Created {len(self.page_buttons)} page buttons for {total_pages} total pages")
            
        except Exception as e:
            logger.error(f"Error creating page buttons: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    def update_pagination(self, current_page, total_pages):
        """
        Update pagination based on current page and total pages.
        
        Args:
            current_page: Current active page
            total_pages: Total number of pages
        """
        try:
            # Validate values
            self.current_page = max(1, min(current_page, max(1, total_pages)))
            self.total_pages = max(1, total_pages)
            
            logger.info(f"Updating pagination: current={self.current_page}, total={self.total_pages}")
            
            # Ẩn tất cả các nút trang và ellipsis đầu tiên
            self._hide_all_buttons()
            
            # Hiển thị các nút trang phù hợp với tổng số trang
            self._show_required_buttons()
            
            # Update navigation button states
            self._update_navigation_button_states()
            
            # Make sure button container is visible
            if hasattr(self, 'button_container'):
                self.button_container.setVisible(True)
                self.button_container.raise_()
            
        except Exception as e:
            logger.error(f"Error updating pagination: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _hide_all_buttons(self):
        """Hide all page buttons and ellipsis labels."""
        try:
            # Hide page buttons
            for btn in self.page_buttons:
                btn.setVisible(False)
            
            # Hide ellipsis labels
            for label in self.ellipsis_labels:
                label.setVisible(False)
            
        except Exception as e:
            logger.error(f"Error hiding buttons: {str(e)}")
    
    def _show_required_buttons(self):
        """Hiển thị các nút trang cần thiết dựa vào tổng số trang và trang hiện tại."""
        try:
            if not self.button_container:
                logger.error("Button container is not initialized")
                return
            
            # Số lượng nút phân trang sẵn có
            num_buttons = len(self.page_buttons)
            if num_buttons == 0:
                logger.warning("No page buttons found")
                return
            
            # Đảm bảo rằng tất cả các nút page buttons đã được tạo và có trong layout
            for i, btn in enumerate(self.page_buttons):
                page_num = i + 1
                if page_num <= self.total_pages:
                    # Cập nhật số trang hiển thị
                    btn.setText(str(page_num))
                    
                    # Set style phù hợp
                    if page_num == self.current_page:
                        btn.setStyleSheet(self.active_page_style)
                    else:
                        btn.setStyleSheet(self.inactive_page_style)
            
            # Trường hợp đơn giản: 7 trang hoặc ít hơn, hiển thị tất cả các trang
            if self.total_pages <= 7:
                # Hiển thị tất cả các nút trang cần thiết
                for i in range(min(self.total_pages, num_buttons)):
                    self.page_buttons[i].setVisible(True)
                
                # Ẩn các nút ellipsis
                for ellipsis in self.ellipsis_labels:
                    ellipsis.setVisible(False)
                
                logger.info(f"Hiển thị tất cả {self.total_pages} trang")
                return
            
            # Trường hợp có nhiều trang, hiển thị theo kiểu: 1 ... 4 5 6 ... 10 (ở vị trí trang 5)
            # Hiển thị nút trang đầu tiên
            self.page_buttons[0].setVisible(True)
            
            # Phân tích để quyết định cách hiển thị
            if self.current_page <= 4:
                # Trang hiện tại gần đầu (1-4): hiển thị 1 2 3 4 5 ... 10
                
                # Hiển thị 5 trang đầu
                for i in range(5):
                    if i < num_buttons and i < self.total_pages:
                        self.page_buttons[i].setVisible(True)
                
                # Hiển thị dấu ... bên phải
                if len(self.ellipsis_labels) > 0:
                    self.ellipsis_labels[0].setVisible(True)
                
                # Hiển thị trang cuối
                if self.total_pages - 1 < num_buttons:
                    self.page_buttons[self.total_pages - 1].setVisible(True)
                
                logger.info(f"Hiển thị phân trang kiểu đầu: 1-5 ... {self.total_pages}")
                
            elif self.current_page >= self.total_pages - 3:
                # Trang hiện tại gần cuối: hiển thị 1 ... 6 7 8 9 10
                
                # Hiển thị dấu ... bên trái sau trang đầu tiên
                if len(self.ellipsis_labels) > 0:
                    self.ellipsis_labels[0].setVisible(True)
                
                # Hiển thị 5 trang cuối
                for i in range(max(0, self.total_pages - 5), self.total_pages):
                    idx = i
                    if idx < num_buttons:
                        self.page_buttons[idx].setVisible(True)
                
                logger.info(f"Hiển thị phân trang kiểu cuối: 1 ... {self.total_pages-4}-{self.total_pages}")
                
            else:
                # Trang hiện tại ở giữa: hiển thị 1 ... 4 5 6 ... 10
                
                # Hiển thị dấu ... bên trái
                if len(self.ellipsis_labels) > 0:
                    self.ellipsis_labels[0].setVisible(True)
                
                # Hiển thị trang hiện tại và trang xung quanh
                for i in range(self.current_page - 2, self.current_page + 1):
                    if 0 <= i < num_buttons and i < self.total_pages:
                        self.page_buttons[i].setVisible(True)
                
                # Hiển thị dấu ... bên phải
                if len(self.ellipsis_labels) > 1:
                    self.ellipsis_labels[1].setVisible(True)
                
                # Hiển thị trang cuối
                if self.total_pages - 1 < num_buttons:
                    self.page_buttons[self.total_pages - 1].setVisible(True)
                
                logger.info(f"Hiển thị phân trang kiểu giữa: 1 ... {self.current_page-1} {self.current_page} {self.current_page+1} ... {self.total_pages}")
            
            # Cập nhật giao diện container
            self.button_container.updateGeometry()
            
        except Exception as e:
            logger.error(f"Error showing required buttons: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _clear_page_buttons(self):
        """Remove all page buttons."""
        try:
            # Remove page buttons
            for btn in self.page_buttons:
                try:
                    btn.setParent(None)
                    btn.deleteLater()
                except:
                    pass
            
            # Remove ellipsis labels
            for label in self.ellipsis_labels:
                try:
                    label.setParent(None)
                    label.deleteLater()
                except:
                    pass
            
            # Clear button lists
            self.page_buttons = []
            self.ellipsis_labels = []
            
        except Exception as e:
            logger.error(f"Error clearing page buttons: {str(e)}")
    
    def _update_navigation_button_states(self):
        """Update the enabled state and style of navigation buttons."""
        try:
            # Enable/disable previous buttons
            prev_enabled = self.current_page > 1
            if self.prev_page_button:
                self.prev_page_button.setEnabled(prev_enabled)
            if self.first_page_button:
                self.first_page_button.setEnabled(prev_enabled)
            
            # Enable/disable next buttons
            next_enabled = self.current_page < self.total_pages
            if self.next_page_button:
                self.next_page_button.setEnabled(next_enabled)
            if self.last_page_button:
                self.last_page_button.setEnabled(next_enabled)
            
            # Update button styles
            if self.prev_page_button:
                self._update_button_style(self.prev_page_button, prev_enabled)
            if self.first_page_button:
                self._update_button_style(self.first_page_button, prev_enabled)
            if self.next_page_button:
                self._update_button_style(self.next_page_button, next_enabled)
            if self.last_page_button:
                self._update_button_style(self.last_page_button, next_enabled)
            
        except Exception as e:
            logger.error(f"Error updating navigation button states: {str(e)}")
    
    def _update_button_style(self, button, enabled):
        """
        Update the style of a button based on enabled state.
        
        Args:
            button: The button to update
            enabled: Whether the button is enabled
        """
        if not button:
            return
            
        if enabled:
            button.setStyleSheet(self.inactive_page_style)
        else:
            button.setStyleSheet(self.disabled_button_style)
    
    def go_to_page(self, page):
        """Go to specific page."""
        try:
            # Validate page number
            page = max(1, min(page, max(1, self.total_pages)))
            
            # Only change if different page
            if self.current_page != page:
                logger.info(f"Changing page from {self.current_page} to {page}")
                old_page = self.current_page
                self.current_page = page
                
                # Update UI
                self.update_pagination(page, self.total_pages)
                
                # Call callback if provided
                if self.on_page_change_callback:
                    try:
                        logger.info(f"Calling page change callback with page {page}")
                        self.on_page_change_callback(page)
                    except Exception as e:
                        logger.error(f"Error in page change callback: {str(e)}")
                        logger.error(traceback.format_exc())
            else:
                logger.debug(f"Already on page {page}, not changing")
                
            return True
        except Exception as e:
            logger.error(f"Error navigating to page {page}: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def go_to_first_page(self):
        """Go to the first page."""
        self.go_to_page(1)
    
    def go_to_prev_page(self):
        """Go to the previous page."""
        self.go_to_page(self.current_page - 1)
    
    def go_to_next_page(self):
        """Go to the next page."""
        self.go_to_page(self.current_page + 1)
    
    def go_to_last_page(self):
        """Go to the last page."""
        self.go_to_page(self.total_pages)
    
    def reset(self):
        """Reset the pagination state."""
        self.current_page = 1
        self.total_pages = 1
        self._hide_all_buttons()
        self._update_navigation_button_states()