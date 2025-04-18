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
            
            # Tìm hoặc tạo layout cho paginator frame
            pagination_layout = pagination_frame.layout()
            if not pagination_layout:
                pagination_layout = QtWidgets.QHBoxLayout(pagination_frame)
                pagination_layout.setContentsMargins(15, 10, 15, 10)
                pagination_layout.setSpacing(5)
            
            # Tạo container riêng cho các nút trang số
            self.button_container = QtWidgets.QWidget(pagination_frame)
            self.button_container.setObjectName("paginationButtonContainer")
            # Đặt kích thước cho container để đảm bảo nó có đủ không gian
            self.button_container.setMinimumWidth(200)
            self.button_container.setMinimumHeight(40)
            
            # Tạo layout ngang cho container nút
            self.button_layout = QtWidgets.QHBoxLayout(self.button_container)
            self.button_layout.setContentsMargins(0, 0, 0, 0)
            self.button_layout.setSpacing(5)
            self.button_layout.setAlignment(Qt.AlignCenter)
            
            # Định vị container giữa prev_button và next_button
            # Tìm vị trí của prev_button trong layout
            for i in range(pagination_layout.count()):
                if pagination_layout.itemAt(i).widget() == prev_button:
                    # Chèn container vào sau prev_button
                    pagination_layout.insertWidget(i+1, self.button_container)
                    break
            else:
                # Nếu không tìm thấy, thử chèn vào vị trí phù hợp
                info_label = None
                for i in range(pagination_layout.count()):
                    widget = pagination_layout.itemAt(i).widget()
                    if widget and isinstance(widget, QtWidgets.QLabel):
                        info_label = widget
                        break
                
                if info_label:
                    # Sắp xếp lại toàn bộ layout
                    for i in range(pagination_layout.count()):
                        widget = pagination_layout.itemAt(0).widget()
                        if widget:
                            pagination_layout.removeWidget(widget)
                    
                    # Thêm lại các widget theo thứ tự đúng
                    pagination_layout.addWidget(info_label)  # Info label
                    pagination_layout.addStretch(1)          # Spacer
                    pagination_layout.addWidget(first_button)
                    pagination_layout.addWidget(prev_button)
                    pagination_layout.addWidget(self.button_container)
                    pagination_layout.addWidget(next_button)
                    pagination_layout.addWidget(last_button)
                else:
                    # Thêm vào cuối nếu không tìm thấy
                    pagination_layout.addWidget(self.button_container)
            
            # Đảm bảo container hiển thị
            self.button_container.setVisible(True)
            
            logger.info("Đã thiết lập pagination manager thành công")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi thiết lập pagination manager: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
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
            # Xóa các nút cũ
            self._clear_page_buttons()
            
            # Đảm bảo total_pages ít nhất là 1
            total_pages = max(1, total_pages)
            
            # Tạo container cho các nút nếu chưa tồn tại
            if not hasattr(self, 'button_container') or not self.button_container:
                self.button_container = QtWidgets.QWidget(parent)
                self.button_container.setObjectName("paginationButtonContainer")
                self.button_container.setMinimumWidth(200)
                self.button_container.setMinimumHeight(40)
                
                # Tạo layout cho container
                self.button_layout = QtWidgets.QHBoxLayout(self.button_container)
                self.button_layout.setContentsMargins(0, 0, 0, 0)
                self.button_layout.setSpacing(5)
                self.button_layout.setAlignment(Qt.AlignCenter)
            
            # Tạo nút số trang (tạo nhiều hơn để dự phòng)
            max_buttons = min(100, max(10, total_pages))
            for i in range(1, max_buttons + 1):
                btn = QtWidgets.QPushButton(str(i), self.button_container)
                btn.setFixedSize(40, 40)
                btn.setStyleSheet(self.inactive_page_style)
                btn.setCursor(QtCore.Qt.PointingHandCursor)
                btn.setVisible(False)  # Ẩn ban đầu
                btn.setObjectName(f"pageButton{i}")
                
                # Kết nối sự kiện với tham số cố định
                btn.clicked.connect(lambda checked=False, page=i: self.go_to_page(page))
                self.page_buttons.append(btn)
                
            # Tạo nút dấu chấm lửng
            for i in range(2):  # Chỉ cần tối đa 2 dấu chấm lửng
                label = QtWidgets.QPushButton("...", self.button_container)
                label.setFixedSize(40, 40)
                label.setStyleSheet(self.inactive_page_style)
                label.setCursor(QtCore.Qt.PointingHandCursor)
                label.setVisible(False)  # Ẩn ban đầu
                label.setObjectName(f"ellipsisLabel{i}")
                self.ellipsis_labels.append(label)
            
            # Kết nối sự kiện cho dấu chấm lửng
            if len(self.ellipsis_labels) >= 2:
                # Dấu chấm lửng bên trái nhảy lùi 5 trang
                self.ellipsis_labels[0].clicked.connect(lambda: self.go_to_page(max(1, self.current_page - 5)))
                # Dấu chấm lửng bên phải nhảy tới 5 trang
                self.ellipsis_labels[1].clicked.connect(lambda: self.go_to_page(min(self.total_pages, self.current_page + 5)))
            
            # Log để debug
            logger.info(f"Đã tạo {len(self.page_buttons)} nút trang cho tổng số {total_pages} trang")
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo các nút trang: {str(e)}")
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
            # Đảm bảo giá trị hợp lệ
            self.current_page = max(1, min(current_page, max(1, total_pages)))
            self.total_pages = max(1, total_pages)
            
            logger.info(f"Cập nhật phân trang: current={self.current_page}, total={self.total_pages}")
            
            # Tính toán các trang hiển thị
            visible_pages = self._calculate_visible_pages()
            logger.info(f"Các trang sẽ hiển thị: {visible_pages}")
            
            # Ẩn tất cả các nút
            self._hide_all_buttons()
            
            # Cập nhật layout nút
            self._update_button_layout(visible_pages)
            
            # Cập nhật trạng thái các nút điều hướng
            self._update_navigation_button_states()
            
            # Đảm bảo container hiển thị
            if hasattr(self, 'button_container'):
                self.button_container.setVisible(True)
                self.button_container.raise_()
            
        except Exception as e:
            logger.error(f"Lỗi cập nhật phân trang: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
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
    
    def _update_button_layout(self, visible_pages):
        """
        Update button layout with visible page buttons and ellipsis labels.
        
        Args:
            visible_pages: List of page numbers and ellipses to show
        """
        try:
            if not self.button_layout:
                logger.error("Button layout is not initialized")
                return
            
            # Xóa tất cả widget hiện tại từ layout
            while self.button_layout.count():
                item = self.button_layout.takeAt(0)
                if item.widget():
                    item.widget().setVisible(False)
            
            # Log các trang sẽ hiển thị
            logger.info(f"Cập nhật layout nút với các trang: {visible_pages}")
            
            # Thêm các nút trang và dấu chấm lửng vào layout
            for i, item in enumerate(visible_pages):
                if item == "...":
                    # Hiển thị dấu chấm lửng
                    ellipsis_index = 0 if i < len(visible_pages)/2 else 1
                    if ellipsis_index < len(self.ellipsis_labels):
                        label = self.ellipsis_labels[ellipsis_index]
                        label.setVisible(True)
                        self.button_layout.addWidget(label)
                else:
                    # Hiển thị nút số trang
                    page_num = item
                    btn_index = page_num - 1  # Chỉ số 0-based
                    
                    if btn_index < len(self.page_buttons):
                        btn = self.page_buttons[btn_index]
                        btn.setText(str(page_num))
                        
                        # Đặt kiểu cho trang hiện tại
                        if page_num == self.current_page:
                            btn.setStyleSheet(self.active_page_style)
                        else:
                            btn.setStyleSheet(self.inactive_page_style)
                        
                        # Hiển thị nút
                        btn.setVisible(True)
                        self.button_layout.addWidget(btn)
                        logger.debug(f"Hiển thị nút trang {page_num}")
                    else:
                        logger.warning(f"Chỉ số nút trang vượt quá: {btn_index} >= {len(self.page_buttons)}")
            
            # Đảm bảo các nút hiển thị đúng cách
            self.button_container.updateGeometry()
            self.button_container.update()
            
        except Exception as e:
            logger.error(f"Lỗi cập nhật layout nút: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
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
            
            # Kết nối các tín hiệu cho các nút điều hướng
            if self.first_page_button:
                try:
                    self.first_page_button.clicked.disconnect()  # Ngắt kết nối cũ
                except:
                    pass  # Bỏ qua nếu không có kết nối
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
            
            # Thêm container nút trang vào layout
            if hasattr(self, 'button_container') and self.button_container:
                pag_layout = pagination_frame.layout()
                if pag_layout:
                    # Tìm vị trí chèn giữa prev và next button
                    placeholder = None
                    for i in range(pag_layout.count()):
                        widget = pag_layout.itemAt(i).widget()
                        if widget and widget.objectName() == "page_buttons_placeholder":
                            placeholder = widget
                            break
                    
                    if placeholder:
                        idx = pag_layout.indexOf(placeholder)
                        pag_layout.removeWidget(placeholder)
                        placeholder.deleteLater()
                        pag_layout.insertWidget(idx, self.button_container)
                    else:
                        # Tìm vị trí chèn sau prev_button
                        for i in range(pag_layout.count()):
                            widget = pag_layout.itemAt(i).widget()
                            if widget == prev_button:
                                pag_layout.insertWidget(i+1, self.button_container)
                                break
                        else:
                            # Nếu không tìm thấy, thêm vào sau info_label
                            pag_layout.insertWidget(1, self.button_container)
            
            # Đảm bảo container hiển thị
            if hasattr(self, 'button_container'):
                self.button_container.setVisible(True)
            
            logger.info("Thiết lập pagination manager thành công")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi thiết lập pagination manager: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
                
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