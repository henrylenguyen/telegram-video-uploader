import tkinter as tk
import logging

logger = logging.getLogger("CustomCheckbox")

class CustomCheckbox(tk.Checkbutton):
    """
    Custom checkbox widget dùng cho Treeview
    """
    def __init__(self, master=None, **kwargs):
        self._var = tk.BooleanVar(value=False)
        
        # Tăng kích thước lên 30px x 30px
        kwargs.update({
            'variable': self._var,
            'onvalue': True,
            'offvalue': False,
            'background': '#ffffff',  # Màu nền trắng
            'highlightthickness': 0,
            'bd': 0,
            'padx': 0,
            'pady': 0,
            'width': 2,  # Tăng chiều rộng
            'height': 2,  # Tăng chiều cao
            'indicatoron': True,  # Hiển thị chỉ báo checkbox
            'font': ('Arial', 14)  # Tăng kích thước font
        })
        super().__init__(master, **kwargs)
        self.item_id = None  # ID của item trong Treeview
        self._original_command = None
        self._last_value = self._var.get()
        
        # Add trace to catch any changes to the variable
        self._var.trace_add("write", self._on_var_change)
    
    def _on_var_change(self, *args):
        """Called when the variable changes value"""
        current_value = self._var.get()
        if current_value != self._last_value:
            self._last_value = current_value
            logger.info(f"Checkbox for item {self.item_id} changed to {current_value}")
            if self._original_command:
                self._original_command()
    
    def get(self):
        """Lấy giá trị checkbox"""
        return self._var.get()
    
    def set(self, value):
        """Đặt giá trị checkbox"""
        self._last_value = value  # Update last value to avoid triggering callback
        return self._var.set(value)
    
    def config(self, **kwargs):
        """Override config to capture command"""
        if 'command' in kwargs:
            self._original_command = kwargs['command']
        return super().config(**kwargs)
    
    def configure(self, **kwargs):
        """Override configure to capture command"""
        if 'command' in kwargs:
            self._original_command = kwargs['command']
        return super().configure(**kwargs)

def create_checkbox_cell(tree, item_id, column="#1"):
    """
    Tạo cell chứa custom checkbox cho treeview
    
    Args:
        tree: Treeview widget
        item_id: ID của item trong treeview
        column: Cột cần tạo checkbox (mặc định là cột đầu tiên)
        
    Returns:
        CustomCheckbox: Đối tượng checkbox đã tạo hoặc None nếu không thể tạo
    """
    try:
        # Lấy vị trí của cell
        tree.update_idletasks()  # Force update UI
        bbox = tree.bbox(item_id, column)
        if not bbox:
            logger.warning(f"Could not get bbox for item {item_id}, column {column}")
            # Try to wait a bit and retry
            app = tree.winfo_toplevel()
            if hasattr(app, 'root'):
                app.root.after(50, lambda: tree.update_idletasks())
                tree.update_idletasks()
                bbox = tree.bbox(item_id, column)
                if not bbox:
                    return None
            else:
                return None
        
        # Tạo checkbox với kích thước 30x30px
        checkbox = CustomCheckbox(tree)
        
        # Đặt vị trí để căn giữa trong cell
        x = bbox[0] + 15  # Increased left margin for better visibility
        y = bbox[1] + (bbox[3] - 30) // 2  # Căn giữa với kích thước 30px
        checkbox.place(x=x, y=y, width=30, height=30)  # Chỉ định kích thước 30x30px
        
        # Lưu trữ item_id trực tiếp trên checkbox
        checkbox.item_id = item_id
        
        # Kết nối với video_checkboxes nếu có
        app = tree.winfo_toplevel()
        if hasattr(app, 'video_checkboxes') and item_id in app.video_checkboxes:
            checkbox.set(app.video_checkboxes[item_id].get())
            
            # Thêm callback để cập nhật giá trị khi click
            def update_var():
                new_value = checkbox.get()
                app.video_checkboxes[item_id].set(new_value)
                # Log change for debugging
                logger.info(f"Checkbox {item_id} changed to {new_value}")
            
            checkbox.config(command=update_var)
        
        return checkbox
    except Exception as e:
        logger.error(f"Error creating checkbox: {e}", exc_info=True)
        return None