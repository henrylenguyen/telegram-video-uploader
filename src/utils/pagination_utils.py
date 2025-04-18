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
        
        # Cập nhật kích thước lớn hơn cho stylesheets
        self.active_page_style = """
            background-color: #3498DB; 
            color: white; 
            font-weight: bold; 
            border-radius: 4px; 
            min-width: 40px; 
            min-height: 40px; 
            max-width: 40px; 
            max-height: 40px;
            font-size: 14px;
        """
        
        self.inactive_page_style = """
            background-color: #FFFFFF; 
            color: #333; 
            border-radius: 4px; 
            min-width: 40px; 
            min-height: 40px; 
            max-width: 40px; 
            max-height: 40px;
            border: 1px solid #E2E8F0;
            font-size: 14px;
        """
        
        self.disabled_button_style = """
            background-color: #e0e0e0; 
            color: #a0a0a0; 
            border-radius: 4px; 
            min-width: 40px; 
            min-height: 40px; 
            max-width: 40px; 
            max-height: 40px;
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
            
        Returns:
            bool: True if setup successful, False otherwise
        """
        try:
            self.pagination_frame = pagination_frame
            self.first_page_button = first_button
            self.prev_page_button = prev_button
            self.next_page_button = next_button
            self.last_page_button = last_button
            self.on_page_change_callback = on_page_change
            
            # Verify all buttons are valid widgets
            if not all([isinstance(btn, QtWidgets.QPushButton) for btn in [first_button, prev_button, next_button, last_button] if btn]):
                logger.error("Không phải tất cả các nút đều là QPushButton hợp lệ")
                return False
            
            # Connect navigation button signals with error handling
            try:
                if self.first_page_button:
                    try:
                        self.first_page_button.clicked.disconnect() # Disconnect existing
                    except:
                        pass # Ignore if no connections
                    self.first_page_button.clicked.connect(self.go_to_first_page)
                
                if self.prev_page_button:
                    try:
                        self.prev_page_button.clicked.disconnect()
                    except:
                        pass
                    self.prev_page_button.clicked.connect(self.go_to_prev_page)
                
                if self.next_page_button:
                    try:
                        self.next_page_button.clicked.disconnect()
                    except:
                        pass
                    self.next_page_button.clicked.connect(self.go_to_next_page)
                
                if self.last_page_button:
                    try:
                        self.last_page_button.clicked.disconnect()
                    except:
                        pass
                    self.last_page_button.clicked.connect(self.go_to_last_page)
            
            except Exception as e:
                logger.error(f"Lỗi khi kết nối tín hiệu nút: {str(e)}")
                return False
            
            # Set cursors
            for btn in [first_button, prev_button, next_button, last_button]:
                if btn:
                    btn.setCursor(QtCore.Qt.PointingHandCursor)
            
            logger.info("Thiết lập pagination manager thành công")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi thiết lập pagination manager: {str(e)}")
            return False
    
    def create_page_buttons(self, parent, total_pages=1):
        """
        Create all page buttons directly and hide them initially.
        This pre-creates all buttons to avoid constant recreation.
        
        Args:
            parent: Parent widget
            total_pages: Maximum number of pages to create
        """
        try:
            self._clear_page_buttons()
            
            # Create page number buttons (more than enough)
            max_buttons = min(100, max(10, total_pages))
            for i in range(1, max_buttons + 1):
                btn = QtWidgets.QPushButton(str(i), parent)
                btn.setFixedSize(40, 40)  # Kích thước lớn hơn
                btn.setStyleSheet(self.inactive_page_style)
                btn.setCursor(QtCore.Qt.PointingHandCursor)
                btn.setVisible(False)  # Hide initially
                btn.clicked.connect(lambda checked, p=i: self.go_to_page(p))
                self.page_buttons.append(btn)
            
            # Create ellipsis labels
            for i in range(2):  # We need at most 2 ellipsis
                label = QtWidgets.QPushButton("...", parent)
                label.setFixedSize(40, 40)  # Kích thước lớn hơn
                label.setStyleSheet(self.inactive_page_style)
                label.setCursor(QtCore.Qt.PointingHandCursor)
                label.setVisible(False)  # Hide initially
                self.ellipsis_labels.append(label)
            
            # Connect ellipsis clicks
            if len(self.ellipsis_labels) >= 2:
                # Left ellipsis jumps back
                self.ellipsis_labels[0].clicked.connect(
                    lambda: self.go_to_page(max(1, self.current_page - 5))
                )
                # Right ellipsis jumps forward 
                self.ellipsis_labels[1].clicked.connect(
                    lambda: self.go_to_page(min(self.total_pages, self.current_page + 5))
                )
            
            logger.info(f"Đã tạo {len(self.page_buttons)} nút trang và {len(self.ellipsis_labels)} nhãn dấu chấm lửng")
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo các nút trang: {str(e)}")
    def update_pagination(self, current_page, total_pages):
        """
        Update pagination based on current page and total pages.
        
        Args:
            current_page: Current active page
            total_pages: Total number of pages
        """
        try:
            # Ensure valid values
            self.current_page = max(1, min(current_page, max(1, total_pages)))
            self.total_pages = max(1, total_pages)
            
            logger.debug(f"Cập nhật phân trang: current={self.current_page}, total={self.total_pages}")
            
            # Calculate visible pages
            visible_pages = self._calculate_visible_pages()
            logger.debug(f"Các trang hiển thị: {visible_pages}")
            
            # Hide all buttons first
            self._hide_all_buttons()
            
            # Position and show the needed buttons
            self._position_buttons(visible_pages)
            
            # Update navigation button states
            self._update_navigation_button_states()
            
        except Exception as e:
            logger.error(f"Lỗi cập nhật phân trang: {str(e)}")
    
    def _hide_all_buttons(self):
        """Hide all page buttons and ellipsis labels."""
        try:
            # Hide all page buttons
            for btn in self.page_buttons:
                btn.setVisible(False)
                
            # Hide all ellipsis labels
            for label in self.ellipsis_labels:
                label.setVisible(False)
                
        except Exception as e:
            logger.error(f"Lỗi ẩn các nút: {str(e)}")
    
    def _position_buttons(self, visible_pages):
        """
        Position and show buttons according to visible pages.
        
        Args:
            visible_pages: List of page numbers and ellipses to show
        """
        try:
            # We need the parent to get coordinates
            if not self.pagination_frame or not self.prev_page_button:
                logger.error("Không có pagination_frame hoặc prev_button để định vị nút")
                return
                
            # Start position (after prev button)
            start_x = self.prev_page_button.x() + self.prev_page_button.width() + 5
            
            # Current position
            current_x = start_x
            
            # Process each visible page
            for i, item in enumerate(visible_pages):
                if item == "...":
                    # Show and position ellipsis
                    ellipsis_index = 0 if i < len(visible_pages)/2 else 1
                    if ellipsis_index < len(self.ellipsis_labels):
                        label = self.ellipsis_labels[ellipsis_index]
                        label.move(current_x, self.prev_page_button.y())
                        label.setVisible(True)
                        current_x += label.width() + 5
                else:
                    # Show and position page button
                    page_num = item
                    btn_index = page_num - 1  # 0-based index
                    
                    if btn_index < len(self.page_buttons):
                        btn = self.page_buttons[btn_index]
                        btn.setText(str(page_num))
                        
                        # Set active style for current page
                        if page_num == self.current_page:
                            btn.setStyleSheet(self.active_page_style)
                        else:
                            btn.setStyleSheet(self.inactive_page_style)
                            
                        # Position and show
                        btn.move(current_x, self.prev_page_button.y())
                        btn.setVisible(True)
                        
                        # Update current_x for next button
                        current_x += btn.width() + 5
                    else:
                        logger.warning(f"Chỉ số nút trang vượt quá: {btn_index} >= {len(self.page_buttons)}")
            
            # Update next button position
            if self.next_page_button:
                self.next_page_button.move(current_x, self.next_page_button.y())
                self.next_page_button.setVisible(True)
                
            # Update last button position
            if self.last_page_button and self.next_page_button:
                self.last_page_button.move(current_x + self.next_page_button.width() + 5, self.last_page_button.y())
                self.last_page_button.setVisible(True)
                
        except Exception as e:
            logger.error(f"Lỗi định vị nút: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _calculate_visible_pages(self):
        """
        Calculate which page numbers and ellipses to show.
        
        Returns:
            list: List of page numbers and ellipses to display
        """
        try:
            visible_pages = []
            
            # Xử lý trường hợp đơn giản khi số trang ít
            if self.total_pages <= 7:
                # Hiển thị tất cả các trang khi có ít trang
                return list(range(1, self.total_pages + 1))
            
            # Luôn hiển thị trang đầu tiên
            visible_pages.append(1)
            
            # Xác định các trang xung quanh trang hiện tại
            if self.current_page <= 4:
                # Khi trang hiện tại gần đầu, hiển thị các trang đầu
                visible_pages.extend(range(2, 6))
                visible_pages.append("...")
                visible_pages.append(self.total_pages)
            elif self.current_page >= self.total_pages - 3:
                # Khi trang hiện tại gần cuối
                visible_pages.append("...")
                visible_pages.extend(range(self.total_pages - 4, self.total_pages + 1))
            else:
                # Trang hiện tại ở giữa
                visible_pages.append("...")
                visible_pages.extend([self.current_page - 1, self.current_page, self.current_page + 1])
                visible_pages.append("...")
                visible_pages.append(self.total_pages)
            
            return visible_pages
            
        except Exception as e:
            logger.error(f"Lỗi tính toán trang hiển thị: {str(e)}")
            # Trả về giá trị mặc định an toàn
            return list(range(1, min(8, self.total_pages + 1)))
    
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
            
            # Clear lists
            self.page_buttons = []
            self.ellipsis_labels = []
            
        except Exception as e:
            logger.error(f"Lỗi xóa nút trang: {str(e)}")
    
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
            logger.error(f"Lỗi cập nhật trạng thái nút điều hướng: {str(e)}")
    
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
        """
        Go to a specific page.
        
        Args:
            page: Target page number
        """
        try:
            # Validate request
            if page == self.current_page:
                return
                
            # Keep current page for logging
            old_page = self.current_page
            
            # Ensure valid page number
            page = max(1, min(page, self.total_pages))
            
            # Update current page
            self.current_page = page
            
            logger.debug(f"Chuyển trang: {old_page} -> {page}")
            
            # Call the callback
            if self.on_page_change_callback:
                self.on_page_change_callback(page)
            
            # Update UI
            self.update_pagination(page, self.total_pages)
            
        except Exception as e:
            logger.error(f"Lỗi chuyển trang: {str(e)}")
    
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