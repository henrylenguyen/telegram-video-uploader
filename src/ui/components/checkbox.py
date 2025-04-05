import tkinter as tk

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

    def get(self):
        """Lấy giá trị checkbox"""
        return self._var.get()
    
    def set(self, value):
        """Đặt giá trị checkbox"""
        return self._var.set(value)

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
    # Lấy vị trí của cell
    tree.update_idletasks()  # Force update UI
    bbox = tree.bbox(item_id, column)
    if not bbox:
        return None
    
    # Tạo checkbox với kích thước 30x30px
    try:
        checkbox = CustomCheckbox(tree)
        
        # Đặt vị trí để căn giữa trong cell
        x = bbox[0] + 5  # Lề trái 5px
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
                app.video_checkboxes[item_id].set(checkbox.get())
            
            checkbox.config(command=update_var)
        
        return checkbox
    except Exception as e:
        import logging
        logging.getLogger().error(f"Error creating checkbox: {e}")
        return None