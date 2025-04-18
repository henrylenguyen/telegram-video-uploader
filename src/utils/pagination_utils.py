"""
Module to handle pagination utilities for the UI components.
Provides reusable pagination logic that can be used across the application.
"""
from PyQt5 import QtWidgets, QtCore, QtGui
import logging

# Configure logger
logger = logging.getLogger(__name__)

class PaginationManager:
    """
    Manager for handling pagination with an advanced display pattern.
    Follows this pattern:
    [<<] [<] [1] [2] ... [current-1] [current] [current+1] ... [last-1] [last] [>] [>>]
    
    When current page changes, updates the display accordingly.
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
        self.page_buttons = []
        self.first_page_button = None
        self.prev_page_button = None
        self.next_page_button = None
        self.last_page_button = None
        self.pagination_layout = None
        self.on_page_change_callback = None
        self.page_button_style = """
            QPushButton.pageButton {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                color: #333;
                font-weight: normal;
            }
            QPushButton.pageButtonActive {
                background-color: #3498DB;
                border: 1px solid #2980B9;
                color: white;
                font-weight: bold;
            }
        """
    
    def setup_pagination(self, pagination_frame, first_button, prev_button, next_button, last_button, on_page_change=None):
        """
        Setup pagination controls.
        
        Args:
            pagination_frame: Frame containing pagination controls
            first_button: First page button (<<)
            prev_button: Previous page button (<)
            next_button: Next page button (>)
            last_button: Last page button (>>)
            on_page_change: Callback when page changes
        """
        self.pagination_frame = pagination_frame
        self.first_page_button = first_button
        self.prev_page_button = prev_button
        self.next_page_button = next_button
        self.last_page_button = last_button
        self.on_page_change_callback = on_page_change
        
        # Find horizontal layout for pagination
        self.pagination_layout = self._find_pagination_layout()
        
        if not self.pagination_layout:
            logger.error("Không tìm thấy layout chứa nút phân trang")
            return False
        
        # Connect navigation button signals
        if self.first_page_button:
            self.first_page_button.clicked.connect(self.go_to_first_page)
        if self.prev_page_button:
            self.prev_page_button.clicked.connect(self.go_to_prev_page)
        if self.next_page_button:
            self.next_page_button.clicked.connect(self.go_to_next_page)
        if self.last_page_button:
            self.last_page_button.clicked.connect(self.go_to_last_page)
        
        # Apply style
        self.pagination_frame.setStyleSheet(self.page_button_style)
        
        return True
    
    def _find_pagination_layout(self):
        """
        Find the horizontal layout for pagination buttons.
        
        Returns:
            QHBoxLayout: Horizontal layout for pagination buttons
        """
        pagination_layout = None
        
        # Try to find existing horizontal layout
        for i in range(self.pagination_frame.layout().count()):
            item = self.pagination_frame.layout().itemAt(i)
            if isinstance(item.layout(), QtWidgets.QHBoxLayout):
                pagination_layout = item.layout()
                break
        
        # If no layout found, create one
        if not pagination_layout:
            logger.warning("No horizontal layout found for pagination, creating one")
            pagination_layout = QtWidgets.QHBoxLayout()
            pagination_layout.setContentsMargins(0, 0, 0, 0)
            pagination_layout.setSpacing(5)
            self.pagination_frame.layout().addLayout(pagination_layout)
        
        return pagination_layout
    
    def update_pagination(self, current_page, total_pages):
        """
        Update pagination based on current page and total pages.
        
        Args:
            current_page: Current active page
            total_pages: Total number of pages
        """
        # Đảm bảo trang hiện tại nằm trong giới hạn hợp lệ
        self.current_page = max(1, min(current_page, max(1, total_pages)))
        self.total_pages = max(1, total_pages)
        
        # Ghi log để debug
        logger.debug(f"Cập nhật phân trang: current_page={self.current_page}, total_pages={self.total_pages}")
        
        # Xóa tất cả các nút phân trang hiện tại
        self._clear_page_buttons()
        
        # Kiểm tra điều kiện giới hạn
        if self.total_pages <= 0:
            return
        
        # Tìm vị trí chèn nút
        insert_pos = self.pagination_layout.indexOf(self.next_page_button)
        
        # Tính toán các trang cần hiển thị
        visible_pages = self._calculate_visible_pages()
        
        # Ghi log các trang sẽ hiển thị
        logger.debug(f"Trang hiển thị: {visible_pages}")
        
        # Tạo và thêm từng nút
        for idx, page_info in enumerate(visible_pages):
            if page_info == "...":
                # Tạo nút ellipsis
                ellipsis = self._create_ellipsis_button(idx == 0)
                self.pagination_layout.insertWidget(insert_pos, ellipsis)
            else:
                # Tạo nút trang thường
                page_button = self._create_page_button(page_info)
                self.pagination_layout.insertWidget(insert_pos, page_button)
                self.page_buttons.append(page_button)
        
        # Cập nhật trạng thái các nút điều hướng
        self._update_navigation_button_states()
    
    def _clear_page_buttons(self):
        """Remove all existing page buttons from the layout."""
        buttons_to_remove = []
        
        # Find all buttons except navigation buttons
        for i in range(self.pagination_layout.count()):
            item = self.pagination_layout.itemAt(i)
            if item.widget() and isinstance(item.widget(), QtWidgets.QPushButton):
                btn = item.widget()
                if btn not in [self.first_page_button, self.prev_page_button, 
                               self.next_page_button, self.last_page_button]:
                    buttons_to_remove.append(btn)
        
        # Remove them
        for btn in buttons_to_remove:
            self.pagination_layout.removeWidget(btn)
            btn.deleteLater()
        
        self.page_buttons = []
    
    def _calculate_visible_pages(self):
        """
        Calculate which page numbers and ellipses to show.
        
        Returns:
            list: List of page numbers and ellipses to display
        """
        visible_pages = []
        
        # Xử lý trường hợp đặc biệt khi chỉ có 1 hoặc 2 trang
        if self.total_pages <= 2:
            # Hiển thị tất cả các trang có sẵn
            return list(range(1, self.total_pages + 1))
        
        # Hiển thị luôn 2 trang đầu
        visible_pages.append(1)
        visible_pages.append(2)
        
        # Hiển thị trang hiện tại (nếu không phải trong 2 trang đầu hoặc 2 trang cuối)
        if 3 <= self.current_page <= self.total_pages - 2:
            # Nếu trang hiện tại không liền kề với trang 2, thêm dấu ellipsis
            if self.current_page > 3:
                visible_pages.append("...")
            
            # Thêm trang trước trang hiện tại (nếu không phải trang 2)
            if self.current_page - 1 > 2:
                visible_pages.append(self.current_page - 1)
            
            # Thêm trang hiện tại
            visible_pages.append(self.current_page)
            
            # Thêm trang sau trang hiện tại (nếu không phải kề trang cuối - 1)
            if self.current_page + 1 < self.total_pages - 1:
                visible_pages.append(self.current_page + 1)
            
            # Nếu trang hiện tại không kề trang cuối - 1, thêm dấu ellipsis
            if self.current_page < self.total_pages - 3:
                visible_pages.append("...")
        else:
            # Nếu trang hiện tại là 1 trong 2 trang đầu hoặc 2 trang cuối
            # và total_pages > 4, thêm dấu ellipsis ở giữa
            if self.total_pages > 4:
                visible_pages.append("...")
        
        # Hiển thị 2 trang cuối
        if self.total_pages - 1 not in visible_pages:
            visible_pages.append(self.total_pages - 1)
        if self.total_pages not in visible_pages:
            visible_pages.append(self.total_pages)
        
        # Loại bỏ trùng lặp
        result = []
        for page in visible_pages:
            if page not in result:
                result.append(page)
        
        return result
    
    def _create_page_button(self, page_num):
        """
        Create a page button with proper styling.
        
        Args:
            page_num: Page number for the button
            
        Returns:
            QPushButton: Page button
        """
        page_button = QtWidgets.QPushButton(str(page_num))
        page_button.setFixedSize(30, 30)
        
        # Kiểm tra xem nút này có phải trang hiện tại không
        is_active = page_num == self.current_page
        
        # Thiết lập class và style cho nút
        page_button.setProperty("class", "pageButtonActive" if is_active else "pageButton")
        
        # Hiển thị rõ ràng trang active bằng style
        if is_active:
            page_button.setStyleSheet("background-color: #3498DB; color: white; font-weight: bold;")
        else:
            page_button.setStyleSheet("")
            
        page_button.setCursor(QtCore.Qt.PointingHandCursor)
        
        # Connect click event
        page_button.clicked.connect(lambda checked, p=page_num: self.go_to_page(p))
        
        return page_button
    
    def _create_ellipsis_button(self, is_left):
        """
        Create an ellipsis button for pagination.
        
        Args:
            is_left: True if this is the left ellipsis, False for right
            
        Returns:
            QPushButton: Ellipsis button
        """
        ellipsis = QtWidgets.QPushButton("...")
        ellipsis.setFixedSize(30, 30)
        ellipsis.setProperty("class", "pageButton")
        ellipsis.setCursor(QtCore.Qt.PointingHandCursor)
        
        # Connect click to jump multiple pages
        if is_left:
            # Left ellipsis - jump back
            jump_page = max(1, self.current_page - 5)
            ellipsis.clicked.connect(lambda: self.go_to_page(jump_page))
        else:
            # Right ellipsis - jump forward
            jump_page = min(self.total_pages, self.current_page + 5)
            ellipsis.clicked.connect(lambda: self.go_to_page(jump_page))
        
        return ellipsis
    
    def _update_navigation_button_states(self):
        """Update the enabled state of navigation buttons."""
        # Cập nhật trạng thái enabled/disabled cho các nút điều hướng
        self.prev_page_button.setEnabled(self.current_page > 1)
        self.next_page_button.setEnabled(self.current_page < self.total_pages)
        self.first_page_button.setEnabled(self.current_page > 1)
        self.last_page_button.setEnabled(self.current_page < self.total_pages)
        
        # Ghi log trạng thái nút điều hướng
        logger.debug(f"Trạng thái nút: Prev={self.current_page > 1}, Next={self.current_page < self.total_pages}")
    
    def go_to_page(self, page):
        """
        Go to a specific page.
        
        Args:
            page: Target page number
        """
        # Nếu đang yêu cầu đi đến chính trang hiện tại, không làm gì cả
        if page == self.current_page:
            return
        
        old_page = self.current_page
        
        # Đảm bảo page nằm trong giới hạn hợp lệ
        self.current_page = max(1, min(page, max(1, self.total_pages)))
        
        logger.debug(f"Chuyển trang từ {old_page} sang {self.current_page}")
        
        # Gọi callback để thông báo cho parent component
        if self.on_page_change_callback:
            self.on_page_change_callback(self.current_page)
        
        # Cập nhật UI phân trang
        self.update_pagination(self.current_page, self.total_pages)
    
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
