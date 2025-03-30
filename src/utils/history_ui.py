"""
Module giao diện cho lịch sử tải lên.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import time

class UploadHistoryDialog:
    """
    Hiển thị giao diện xem lịch sử tải lên.
    """
    
    def __init__(self, parent, upload_history, video_analyzer=None):
        """
        Khởi tạo dialog lịch sử tải lên
        
        Args:
            parent: Widget cha
            upload_history: Đối tượng quản lý lịch sử tải lên
            video_analyzer: Đối tượng phân tích video (tùy chọn)
        """
        self.parent = parent
        self.upload_history = upload_history
        self.video_analyzer = video_analyzer
        
        # Tạo cửa sổ dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Lịch sử tải lên")
        self.dialog.geometry("900x600")
        self.dialog.minsize(800, 500)
        self.dialog.transient(parent)
        self.dialog.grab_set()  # Khóa cửa sổ chính
        
        # Đặt vị trí cửa sổ vào giữa màn hình
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Biến lưu trữ thông tin hiện tại
        self.current_hash = None
        self.current_thumbnail = None
        
        # Tạo giao diện
        self.create_ui()
        
        # Tải dữ liệu lịch sử
        self.load_history_data()
    
    def create_ui(self):
        """Tạo giao diện dialog"""
        # Frame chính
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Split pane - Chia đôi giao diện
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Khung trái - Danh sách video
        left_frame = ttk.Frame(paned_window, width=400)
        paned_window.add(left_frame, weight=1)
        
        # Phần tiêu đề và tìm kiếm
        header_frame = ttk.Frame(left_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(header_frame, text="Danh sách video đã tải lên", 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT, pady=5)
        
        # Phần tìm kiếm
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_history)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Danh sách video
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview với thanh cuộn
        columns = ("filename", "size", "upload_date")
        self.history_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Thiết lập cột
        self.history_tree.heading("filename", text="Tên file")
        self.history_tree.heading("size", text="Kích thước")
        self.history_tree.heading("upload_date", text="Ngày tải lên")
        
        self.history_tree.column("filename", width=200, anchor="w")
        self.history_tree.column("size", width=80, anchor="e")
        self.history_tree.column("upload_date", width=120, anchor="center")
        
        # Thêm thanh cuộn
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Đặt vị trí
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Liên kết sự kiện chọn item
        self.history_tree.bind('<<TreeviewSelect>>', self.on_select_item)
        
        # Thêm menu chuột phải
        self.context_menu = tk.Menu(self.history_tree, tearoff=0)
        self.context_menu.add_command(label="Xóa khỏi lịch sử", command=self.remove_selected)
        
        self.history_tree.bind("<Button-3>", self.show_context_menu)
        
        # Frame điều khiển bên dưới danh sách
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Nhãn hiển thị tổng số video
        self.total_label = ttk.Label(control_frame, text="Tổng số: 0 video")
        self.total_label.pack(side=tk.LEFT, padx=5)
        
        # Nút xóa lịch sử
        clear_btn = ttk.Button(control_frame, text="Xóa lịch sử", command=self.confirm_clear_history)
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Khung phải - Thông tin chi tiết
        right_frame = ttk.Frame(paned_window, width=400)
        paned_window.add(right_frame, weight=1)
        
        # Chi tiết video
        detail_frame = ttk.LabelFrame(right_frame, text="Thông tin chi tiết")
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Phần hình thu nhỏ
        thumbnail_frame = ttk.Frame(detail_frame)
        thumbnail_frame.pack(fill=tk.X, pady=10)
        
        self.thumbnail_label = ttk.Label(thumbnail_frame, text="Chọn video để xem chi tiết")
        self.thumbnail_label.pack(anchor=tk.CENTER)
        
        # Phần thông tin cơ bản
        info_frame = ttk.Frame(detail_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        # Tạo grid 2 cột
        info_frame.columnconfigure(0, weight=0)
        info_frame.columnconfigure(1, weight=1)
        
        # Các trường thông tin
        ttk.Label(info_frame, text="Tên file:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.filename_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.filename_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Đường dẫn:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.path_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.path_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Kích thước:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.size_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.size_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Ngày tải lên:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.date_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.date_var).grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Hash:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.hash_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.hash_var).grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Phần danh sách video trùng lặp
        duplicate_frame = ttk.LabelFrame(right_frame, text="Video trùng lặp")
        duplicate_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tạo listbox hiển thị các video trùng lặp
        self.duplicate_listbox = tk.Listbox(duplicate_frame, height=6)
        self.duplicate_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Nút đóng
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        close_btn = ttk.Button(btn_frame, text="Đóng", command=self.dialog.destroy, width=15)
        close_btn.pack(side=tk.RIGHT, padx=5)
    
    def load_history_data(self):
        """Tải dữ liệu lịch sử vào treeview"""
        # Xóa dữ liệu cũ
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Lấy danh sách tất cả video đã tải lên
        uploads = self.upload_history.get_all_uploads()
        
        # Thêm vào treeview
        for hash_value, info in uploads.items():
            filename = info.get('filename', 'Không rõ')
            file_size = info.get('file_size', 0)
            upload_date = info.get('upload_date', 'Không rõ')
            
            # Định dạng kích thước
            size_text = self.format_size(file_size)
            
            # Thêm vào treeview
            self.history_tree.insert("", tk.END, iid=hash_value, values=(filename, size_text, upload_date))
        
        # Cập nhật tổng số
        self.total_label.config(text=f"Tổng số: {len(uploads)} video")
    
    def filter_history(self, *args):
        """Lọc danh sách lịch sử theo tìm kiếm"""
        search_term = self.search_var.get().lower()
        
        # Xóa danh sách hiện tại
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Lấy danh sách tất cả video đã tải lên
        uploads = self.upload_history.get_all_uploads()
        
        filtered_count = 0
        for hash_value, info in uploads.items():
            filename = info.get('filename', 'Không rõ').lower()
            file_path = info.get('path', '').lower()
            upload_date = info.get('upload_date', '').lower()
            
            # Lọc theo từ khóa
            if (search_term in filename or 
                search_term in file_path or 
                search_term in upload_date):
                
                file_size = info.get('file_size', 0)
                size_text = self.format_size(file_size)
                
                # Thêm vào treeview
                self.history_tree.insert("", tk.END, iid=hash_value, values=(info['filename'], size_text, info['upload_date']))
                filtered_count += 1
        
        # Cập nhật tổng số
        if search_term:
            self.total_label.config(text=f"Kết quả: {filtered_count}/{len(uploads)} video")
        else:
            self.total_label.config(text=f"Tổng số: {len(uploads)} video")
    
    def on_select_item(self, event):
        """Xử lý khi chọn một mục trong treeview"""
        selected_items = self.history_tree.selection()
        if not selected_items:
            return
        
        # Lấy hash của mục được chọn
        selected_hash = selected_items[0]
        self.current_hash = selected_hash
        
        # Lấy thông tin chi tiết
        info = self.upload_history.get_upload_info(selected_hash)
        if not info:
            return
        
        # Cập nhật thông tin hiển thị
        self.filename_var.set(info.get('filename', 'Không rõ'))
        self.path_var.set(info.get('path', 'Không rõ'))
        self.size_var.set(self.format_size(info.get('file_size', 0)))
        self.date_var.set(info.get('upload_date', 'Không rõ'))
        self.hash_var.set(f"{selected_hash[:12]}...")
        
        # Tạo hình thu nhỏ nếu có video_analyzer
        if self.video_analyzer and os.path.exists(info.get('path', '')):
            # Hiển thị "Đang tải..." 
            self.thumbnail_label.config(text="Đang tạo hình thu nhỏ...")
            
            # Sử dụng after để không chặn giao diện
            self.dialog.after(100, lambda: self.load_thumbnail(info.get('path', '')))
        else:
            self.thumbnail_label.config(text="Không thể tạo hình thu nhỏ", image="")
            self.current_thumbnail = None
        
        # Hiển thị danh sách video trùng lặp
        self.show_duplicates(selected_hash)
    
    def load_thumbnail(self, video_path):
        """Tải hình thu nhỏ của video"""
        try:
            thumbnail = self.video_analyzer.get_thumbnail(video_path)
            if thumbnail:
                # Lưu tham chiếu để tránh bị thu hồi bởi garbage collector
                self.current_thumbnail = thumbnail
                self.thumbnail_label.config(image=thumbnail, text="")
            else:
                self.thumbnail_label.config(text="Không thể tạo hình thu nhỏ", image="")
                self.current_thumbnail = None
        except Exception as e:
            self.thumbnail_label.config(text=f"Lỗi: {str(e)}", image="")
            self.current_thumbnail = None
    
    def show_duplicates(self, video_hash):
        """Hiển thị danh sách video trùng lặp"""
        # Xóa danh sách hiện tại
        self.duplicate_listbox.delete(0, tk.END)
        
        # Lấy danh sách hash của các video trùng lặp
        duplicate_hashes = self.upload_history.get_duplicates_of(video_hash)
        
        # Thêm các video mà video hiện tại trùng lặp với
        for hash_list in self.upload_history.duplicates.values():
            if video_hash in hash_list and hash_list != duplicate_hashes:
                for h in hash_list:
                    if h != video_hash and h not in duplicate_hashes:
                        duplicate_hashes.append(h)
        
        if not duplicate_hashes:
            self.duplicate_listbox.insert(tk.END, "Không có video trùng lặp")
            return
        
        # Thêm vào listbox
        for hash_value in duplicate_hashes:
            info = self.upload_history.get_upload_info(hash_value)
            if info:
                filename = info.get('filename', 'Không rõ')
                upload_date = info.get('upload_date', 'Không rõ')
                self.duplicate_listbox.insert(tk.END, f"{filename} (tải lên: {upload_date})")
    
    def show_context_menu(self, event):
        """Hiển thị menu chuột phải"""
        if self.history_tree.identify_row(event.y):
            self.history_tree.selection_set(self.history_tree.identify_row(event.y))
            self.context_menu.post(event.x_root, event.y_root)
    
    def remove_selected(self):
        """Xóa mục đã chọn khỏi lịch sử"""
        selected_items = self.history_tree.selection()
        if not selected_items:
            return
        
        # Xác nhận từ người dùng
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa mục này khỏi lịch sử?"):
            for item in selected_items:
                # Xóa khỏi lịch sử
                self.upload_history.remove_upload(item)
                
                # Xóa khỏi treeview
                self.history_tree.delete(item)
            
            # Cập nhật tổng số
            uploads = self.upload_history.get_all_uploads()
            self.total_label.config(text=f"Tổng số: {len(uploads)} video")
            
            # Xóa thông tin chi tiết
            self.clear_details()
    
    def confirm_clear_history(self):
        """Xác nhận và xóa toàn bộ lịch sử"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa toàn bộ lịch sử tải lên?"):
            # Xóa toàn bộ lịch sử
            self.upload_history.clear_history()
            
            # Cập nhật giao diện
            self.load_history_data()
            self.clear_details()
    
    def clear_details(self):
        """Xóa thông tin chi tiết"""
        self.current_hash = None
        self.current_thumbnail = None
        
        self.filename_var.set("")
        self.path_var.set("")
        self.size_var.set("")
        self.date_var.set("")
        self.hash_var.set("")
        
        self.thumbnail_label.config(text="Chọn video để xem chi tiết", image="")
        
        self.duplicate_listbox.delete(0, tk.END)
    
    @staticmethod
    def format_size(size_bytes):
        """Định dạng kích thước file thành chuỗi dễ đọc"""
        if not size_bytes:
            return "Không rõ"
            
        if isinstance(size_bytes, str):
            try:
                size_bytes = float(size_bytes)
            except:
                return size_bytes
                
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.2f} {units[unit_index]}"

if __name__ == "__main__":
    # Mã kiểm thử
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    from utils.upload_history import UploadHistory
    
    # Tạo cửa sổ gốc
    root = tk.Tk()
    root.title("Kiểm thử Dialog Lịch sử")
    root.geometry("300x200")
    
    # Tạo đối tượng UploadHistory
    history = UploadHistory("test_history.json")
    
    # Thêm vài mục test
    history.add_upload("hash1", "video1.mp4", "C:/videos/video1.mp4", 15000000)
    history.add_upload("hash2", "video2.mp4", "C:/videos/video2.mp4", 25000000)
    history.add_upload("hash3", "video3.mp4", "C:/videos/video3.mp4", 35000000)
    
    history.add_duplicate("hash3", "hash1")
    
    # Tạo nút mở dialog
    def show_dialog():
        dialog = UploadHistoryDialog(root, history)
    
    btn = ttk.Button(root, text="Mở Lịch sử", command=show_dialog)
    btn.pack(padx=20, pady=20)
    
    root.mainloop()