"""
Module tùy chỉnh checkbox cho giao diện.
"""
import tkinter as tk

class CustomCheckbox(tk.Frame):
    """Widget tạo checkbox tùy chỉnh thay thế cho emoji"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        # Use a standard background color instead of trying to get it from parent
        self.configure(height=24, width=24, background="#ffffff")  # Use white background for better visibility
        self.pack_propagate(False)  # Giữ kích thước
        
        # Biến lưu trạng thái
        self.checked = tk.BooleanVar(value=False)
        
        # Canvas để vẽ checkbox
        self.canvas = tk.Canvas(self, height=24, width=24, 
                             highlightthickness=0, background="#ffffff")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Vẽ checkbox
        self._draw_checkbox()
        
        # Xử lý click
        self.canvas.bind("<Button-1>", self.toggle)
        
    def _draw_checkbox(self):
        """Vẽ checkbox dựa trên trạng thái"""
        self.canvas.delete("all")
        
        # Vẽ khung rõ ràng hơn
        self.canvas.create_rectangle(2, 2, 22, 22, 
                                  outline="#2E86C1", width=2)
        
        # Nếu đã chọn, vẽ dấu tích rõ ràng hơn
        if self.checked.get():
            # Vẽ nền
            self.canvas.create_rectangle(4, 4, 20, 20, 
                                      fill="#2E86C1", outline="")
            # Vẽ dấu tích
            self.canvas.create_line(6, 12, 10, 16, width=2, fill="white")
            self.canvas.create_line(10, 16, 18, 8, width=2, fill="white")
    
    def toggle(self, event=None):
        """Đảo trạng thái checkbox"""
        self.checked.set(not self.checked.get())
        self._draw_checkbox()
        
        # Tìm item_id tương ứng trong tree và cập nhật giá trị trong dictionary
        try:
            tree = self.master
            app = tree.winfo_toplevel()
            
            for item_id in tree.get_children():
                bbox = tree.bbox(item_id, "#1")
                if bbox:
                    # Kiểm tra xem checkbox có nằm trong bbox không
                    x = self.winfo_x()
                    y = self.winfo_y()
                    if (x >= bbox[0] and x <= bbox[0] + bbox[2] and 
                        y >= bbox[1] and y <= bbox[1] + bbox[3]):
                        # Tìm thấy item_id tương ứng
                        if hasattr(app, 'video_checkboxes') and item_id in app.video_checkboxes:
                            app.video_checkboxes[item_id].set(self.checked.get())
                        break
        except Exception as e:
            import logging
            logging.getLogger().error(f"Error in checkbox toggle: {e}")
        
    def get(self):
        """Lấy trạng thái hiện tại"""
        return self.checked.get()
        
    def set(self, value):
        """Đặt trạng thái"""
        self.checked.set(bool(value))
        self._draw_checkbox()

def create_checkbox_cell(tree, item_id, column):
    """
    Tạo cell chứa custom checkbox cho treeview
    
    Args:
        tree: Treeview widget
        item_id: ID của item trong treeview
        column: Cột cần tạo checkbox
        
    Returns:
        CustomCheckbox: Đối tượng checkbox đã tạo hoặc None nếu không thể tạo
    """
    # Lấy vị trí của cell
    bbox = tree.bbox(item_id, column)
    if not bbox:
        return None
    
    # Tạo checkbox trong frame
    checkbox = CustomCheckbox(tree)
    
    # Set its position - center it in the cell
    x = bbox[0] + (bbox[2] - 24) // 2  # Center horizontally
    y = bbox[1] + (bbox[3] - 24) // 2  # Center vertically
    checkbox.place(x=x, y=y)
    
    # Store the item_id directly on the checkbox for easier reference
    checkbox.item_id = item_id
    
    # If tree has a reference to app's video_checkboxes, use it
    app = tree.winfo_toplevel()
    if hasattr(app, 'video_checkboxes') and item_id in app.video_checkboxes:
        checkbox.set(app.video_checkboxes[item_id].get())
    
    return checkbox