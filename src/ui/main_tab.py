"""
Module tạo và quản lý tab tải lên chính.
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from PIL import Image, ImageTk
import cv2
import math

logger = logging.getLogger("MainTab")

class CustomCheckbox(tk.Frame):
    """Widget tạo checkbox tùy chỉnh thay thế cho emoji"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(height=24, width=24, bg=parent.cget("bg"))
        self.pack_propagate(False)  # Giữ kích thước
        
        # Biến lưu trạng thái
        self.checked = tk.BooleanVar(value=False)
        
        # Canvas để vẽ checkbox
        self.canvas = tk.Canvas(self, height=24, width=24, 
                             highlightthickness=0, bg=parent.cget("bg"))
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Vẽ checkbox
        self._draw_checkbox()
        
        # Xử lý click
        self.canvas.bind("<Button-1>", self.toggle)
        
    def _draw_checkbox(self):
        """Vẽ checkbox dựa trên trạng thái"""
        self.canvas.delete("all")
        
        # Vẽ khung
        self.canvas.create_rectangle(2, 2, 22, 22, 
                                  outline="#4a7ebb", width=2)
        
        # Nếu đã chọn, vẽ dấu tích
        if self.checked.get():
            # Vẽ nền
            self.canvas.create_rectangle(4, 4, 20, 20, 
                                      fill="#4a7ebb", outline="")
            # Vẽ dấu tích
            self.canvas.create_line(6, 12, 10, 16, width=2, fill="white")
            self.canvas.create_line(10, 16, 18, 8, width=2, fill="white")
    
    def toggle(self, event=None):
        """Đảo trạng thái checkbox"""
        self.checked.set(not self.checked.get())
        self._draw_checkbox()
        
        # Get associated treeview item
        for item_id, var in self.master.app.video_checkboxes.items():
            bbox = self.master.bbox(item_id, "#1")
            if bbox and self.winfo_y() >= bbox[1] and self.winfo_y() <= bbox[1] + 30:
                var.set(self.checked.get())
                break
        
    def get(self):
        """Lấy trạng thái hiện tại"""
        return self.checked.get()
        
    def set(self, value):
        """Đặt trạng thái"""
        self.checked.set(bool(value))
        self._draw_checkbox()
def create_checkbox_cell(tree, item_id, column):
    """Tạo cell chứa custom checkbox cho treeview"""
    # Lấy vị trí của cell
    bbox = tree.bbox(item_id, column)
    if not bbox:
        return None
    
    # Tạo checkbox trong frame
    checkbox = CustomCheckbox(tree)
    checkbox.place(x=bbox[0] + 5, y=bbox[1] + 3)
    
    return checkbox

def render_checkboxes(app):
    """Vẽ lại tất cả checkbox trên treeview - LUÔN hiển thị chúng"""
    # Xóa tất cả checkbox hiện tại
    if hasattr(app, 'checkbox_widgets'):
        for checkbox in app.checkbox_widgets:
            checkbox.destroy()
    
    app.checkbox_widgets = []
    
    # Update sau một giây để đảm bảo treeview đã render xong
    def delayed_render():
        # Tạo checkbox cho tất cả hàng
        for item_id in app.video_tree.get_children():
            if item_id not in app.video_checkboxes:
                app.video_checkboxes[item_id] = tk.BooleanVar(value=False)
            
            checkbox = create_checkbox_cell(app.video_tree, item_id, "#1")
            if checkbox:
                checkbox.set(app.video_checkboxes[item_id].get())
                app.checkbox_widgets.append(checkbox)
    
    app.root.after(50, delayed_render)
    
def create_main_tab(app, parent):
    """
    Tạo giao diện cho tab tải lên chính
    
    Args:
        app: Đối tượng TelegramUploaderApp
        parent: Frame cha
    """
    # Tạo canvas để hỗ trợ cuộn
    main_canvas = tk.Canvas(parent)
    main_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=main_canvas.yview)
    
    # Thiết lập canvas
    main_canvas.configure(yscrollcommand=main_scrollbar.set)
    
    # Sắp xếp canvas và thanh cuộn
    main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Tạo frame chứa nội dung
    content_frame = ttk.Frame(main_canvas)
    content_window = main_canvas.create_window((0, 0), window=content_frame, anchor="nw", width=main_canvas.winfo_width())
    
    # Cấu hình cuộn
    def on_frame_configure(event):
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        # Đảm bảo frame nội dung có chiều rộng phù hợp
        main_canvas.itemconfig(content_window, width=main_canvas.winfo_width())
    
    content_frame.bind("<Configure>", on_frame_configure)
    
    # Kích hoạt cuộn bằng chuột
    def on_mousewheel(event):
        main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    main_canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    # Frame chọn thư mục
    folder_frame = ttk.LabelFrame(content_frame, text="Thư mục chứa video")
    folder_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Đường dẫn thư mục
    app.folder_path = tk.StringVar()
    app.folder_path.set(app.config['SETTINGS']['video_folder'])
    
    # Ô input và nút duyệt cải thiện layout
    input_frame = ttk.Frame(folder_frame)
    input_frame.pack(fill=tk.X, padx=5, pady=5)

    # Container for entry with fixed height
    entry_container = ttk.Frame(input_frame, height=50)
    entry_container.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
    entry_container.pack_propagate(False)  # Maintain fixed height

    # Ô nhập liệu với font lớn hơn
    folder_entry = tk.Entry(entry_container, textvariable=app.folder_path, 
                        font=("Arial", 14),
                        relief="groove", bg="white",
                        highlightthickness=1,
                        highlightbackground="#cccccc")
    folder_entry.pack(fill=tk.BOTH, expand=True)

    # Container for browse button with fixed height
    button_container = ttk.Frame(input_frame, height=50, width=100)
    button_container.pack(side=tk.RIGHT, padx=5, pady=5)
    button_container.pack_propagate(False)  # Maintain fixed height

    # Nút "Duyệt..." - với màu xanh để nổi bật và chiều cao cố định
    browse_btn = tk.Button(button_container, text="Duyệt...", 
                        bg="#3498db", fg="white",  # Màu xanh giống nút tải lên
                        font=("Arial", 11), 
                        relief="flat")           # Kiểu dáng phẳng, hiện đại
    browse_btn.pack(fill=tk.BOTH, expand=True)
    browse_btn.config(command=lambda: browse_folder(app))
    
    # Frame kiểm soát
    control_top_frame = ttk.Frame(content_frame)
    control_top_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # Nút làm mới danh sách
    refresh_btn = ttk.Button(control_top_frame, text="Làm mới danh sách", 
                           command=lambda: refresh_video_list(app))
    refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Frame cho các checkbox bên phải - xếp theo dòng
    checkbox_frame = ttk.Frame(control_top_frame)
    checkbox_frame.pack(side=tk.RIGHT, padx=5, pady=5)
    
    # Tạo style cho checkbox
    style = ttk.Style()
    style.configure("Custom.TCheckbutton", 
                  font=("Arial", 10),
                  indicatorsize=20)
    
    # Checkbox kiểm tra với lịch sử - đồng bộ style
    app.check_history_var = tk.IntVar(value=1)
    history_check = ttk.Checkbutton(
        checkbox_frame, 
        text="Kiểm tra với lịch sử đã tải lên", 
        variable=app.check_history_var,
        command=lambda: refresh_video_list(app),
        style="Custom.TCheckbutton"
    )
    history_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
    
    # Checkbox kiểm tra trùng lặp - đồng bộ style
    app.check_duplicates_var = tk.IntVar(value=app.config['SETTINGS'].getboolean('check_duplicates', True))
    duplicates_check = ttk.Checkbutton(
        checkbox_frame, 
        text="Kiểm tra video trùng lặp", 
        variable=app.check_duplicates_var,
        command=lambda: refresh_video_list(app),
        style="Custom.TCheckbutton"
    )
    duplicates_check.grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
    
    # Container cho tabs
    tab_container = ttk.Frame(content_frame)
    tab_container.pack(fill=tk.X, padx=10, pady=5)
    
    # Tạo style cho các tab button
    tab_style = ttk.Style()
    tab_style.configure("Tab.TFrame", background="#f0f0f0")
    
    # Tab frame
    tab_frame = ttk.Frame(tab_container, style="Tab.TFrame")
    tab_frame.pack(fill=tk.X)
    
    # Các tab với padding và font phù hợp
    tab_names = [
        ("manual", "Tải lên thủ công"),
        ("auto", "Tải lên tự động"),
        ("duplicate", "Danh sách video trùng"),
        ("uploaded", "Danh sách video đã tải lên")
    ]
    
    app.sub_tab_buttons = {}
    
    # Tạo các tab button với style như hình ảnh
    for i, (code, name) in enumerate(tab_names):
        btn = tk.Button(
            tab_frame, 
            text=name,
            font=("Arial", 11),
            padx=15, pady=8,
            relief="raised",
            borderwidth=1,
            bg="#4a7ebb" if code == "manual" else "#f0f0f0",
            fg="white" if code == "manual" else "black",
            command=lambda c=code: switch_tab(app, c)
        )
        btn.pack(side=tk.LEFT)
        app.sub_tab_buttons[code] = btn
    
    # Frame chứa nội dung tab
    app.tab_content_frame = ttk.Frame(content_frame)
    app.tab_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Hiển thị tab đầu tiên
    create_manual_tab(app, app.tab_content_frame)
    
    # Thanh tiến trình và nút ở cuối
    app.bottom_space_frame = ttk.Frame(content_frame, height=100)
    app.bottom_space_frame.pack(fill=tk.X)
    
    # Lưu trữ các checkbox trên tree
    app.checkbox_widgets = []

def create_manual_tab(app, parent):
    """
    Tạo giao diện tab tải lên thủ công
    
    Args:
        app: Đối tượng TelegramUploaderApp
        parent: Frame cha
    """
    # Biến lưu trữ trang hiện tại
    app.current_page = 1
    app.items_per_page = 10  # Số lượng video trên mỗi trang
    
    # Frame hiển thị danh sách video
    videos_frame = ttk.LabelFrame(parent, text="Danh sách video")
    videos_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=5)
    
    # Tạo frame cho danh sách và thanh cuộn
    list_frame = ttk.Frame(videos_frame)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Tạo style cho treeview
    style = ttk.Style()
    style.configure("Treeview", rowheight=30, font=("Arial", 10))
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
    
    # Cấu hình cột
    app.video_tree = ttk.Treeview(list_frame, columns=("select", "filename", "status", "info"), show="headings", height=10)
    app.video_tree.heading("select", text="")
    app.video_tree.heading("filename", text="Tên file")
    app.video_tree.heading("status", text="Trạng thái")
    app.video_tree.heading("info", text="Thông tin thêm")
    
    # Thiết lập độ rộng cột
    app.video_tree.column("select", width=30, anchor=tk.CENTER)
    app.video_tree.column("filename", width=400, anchor=tk.W)
    app.video_tree.column("status", width=150, anchor=tk.CENTER)
    app.video_tree.column("info", width=300, anchor=tk.W)
    
    # Tạo thanh cuộn ngang và dọc cho treeview
    tree_y_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=app.video_tree.yview)
    tree_x_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=app.video_tree.xview)
    app.video_tree.configure(yscrollcommand=tree_y_scrollbar.set, xscrollcommand=tree_x_scrollbar.set)
    
    # Sắp xếp treeview và thanh cuộn
    tree_y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    app.video_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    tree_x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Make horizontal scrollbar always visible
    def configure_scrollbar(event=None):
        tree_x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        app.video_tree.configure(xscrollcommand=tree_x_scrollbar.set)
        
    app.video_tree.bind('<Map>', configure_scrollbar)
    
    # Tạo dictionary để lưu các checkbutton
    app.video_checkboxes = {}
    app.video_items = []
    
    # Cấu hình bề mặt cho các trạng thái
    app.video_tree.tag_configure("duplicate", background="#FFD2D2")
    app.video_tree.tag_configure("uploaded", background="#D2F0FF")
    
    # Xử lý sự kiện khi click vào bảng
    app.video_tree.bind("<ButtonRelease-1>", lambda event: on_video_tree_click(app, event))
    app.video_tree.bind("<<TreeviewSelect>>", lambda event: on_video_select(app, event))
    
    # Frame cho phân trang và thông tin tổng số
    pagination_frame = ttk.Frame(videos_frame)
    pagination_frame.pack(fill=tk.X, pady=5)
    
    # Thông tin tổng số video
    app.total_info_var = tk.StringVar(value="Tổng: 0 video, 0 video trùng, 0 video đã tải lên")
    total_info_label = ttk.Label(pagination_frame, textvariable=app.total_info_var)
    total_info_label.pack(side=tk.LEFT, padx=5)
    
    # Frame cho các nút phân trang
    page_control_frame = ttk.Frame(pagination_frame)
    page_control_frame.pack(side=tk.RIGHT, padx=5)
    
    # Nút trang trước
    app.prev_page_btn = tk.Button(page_control_frame, text="←", width=3,
                               command=lambda: change_page(app, -1))
    app.prev_page_btn.pack(side=tk.LEFT, padx=2)
    
    # Hiển thị trang hiện tại
    app.page_info_var = tk.StringVar(value="Trang 1/1")
    page_label = ttk.Label(page_control_frame, textvariable=app.page_info_var, width=10)
    page_label.pack(side=tk.LEFT, padx=2)
    
    # Nút trang tiếp
    app.next_page_btn = tk.Button(page_control_frame, text="→", width=3,
                               command=lambda: change_page(app, 1))
    app.next_page_btn.pack(side=tk.LEFT, padx=2)
    
    # Frame cho các nút chọn
    selection_frame = ttk.Frame(videos_frame)
    selection_frame.pack(fill=tk.X, pady=5)
    
    # Nút chọn/bỏ chọn
    select_all_btn = tk.Button(selection_frame, text="Chọn tất cả", 
                            bg="#3498db", fg="white",
                            font=("Arial", 11),
                            padx=10, pady=5,
                            relief="flat",
                            command=lambda: select_all_videos(app))
    select_all_btn.pack(side=tk.LEFT, padx=5)

    deselect_all_btn = tk.Button(selection_frame, text="Bỏ chọn tất cả", 
                            bg="#3498db", fg="white",
                            font=("Arial", 11),
                            padx=10, pady=5,
                            relief="flat",
                            command=lambda: deselect_all_videos(app))
    deselect_all_btn.pack(side=tk.LEFT, padx=5)
    
    # Thanh tiến trình - đặt sau các nút chọn/bỏ chọn
    progress_frame = ttk.Frame(videos_frame)
    progress_frame.pack(fill=tk.X, padx=5, pady=5)
    
    app.progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
    app.progress.pack(fill=tk.X, padx=5, pady=5)
    
    # Nhãn trạng thái
    app.status_var = tk.StringVar()
    app.status_var.set("Sẵn sàng")
    status_label = ttk.Label(progress_frame, textvariable=app.status_var)
    status_label.pack(pady=5)
    
    # Frame thông tin video
    info_frame = ttk.LabelFrame(parent, text="Thông tin video đã chọn")
    info_frame.pack(fill=tk.X, padx=0, pady=5)
    
    # Tạo 2 phần bên trái và bên phải
    info_layout = ttk.Frame(info_frame)
    info_layout.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Frame bên trái - hình thu nhỏ và nút
    info_left_frame = ttk.Frame(info_layout)
    info_left_frame.pack(side=tk.LEFT, fill=tk.Y)
    
    # Frame bao quanh thumbnail để tạo viền - đảm bảo kích thước cân đối
    thumbnail_frame = ttk.Frame(info_left_frame, width=350, height=210)
    thumbnail_frame.pack(padx=5, pady=5)
    thumbnail_frame.pack_propagate(False)  # Giữ kích thước cố định
    
    # Hiển thị hình thu nhỏ - với thông báo "Bạn hãy nhấn vào tên file bất kỳ"
    app.thumbnail_label = tk.Label(thumbnail_frame, text="Bạn hãy nhấn vào tên file bất kỳ", 
                                bg="white", relief="solid", bd=1)
    app.thumbnail_label.pack(fill=tk.BOTH, expand=True)
    
    # Frame nút bên dưới hình thu nhỏ - đảm bảo kích thước phù hợp
    button_container = ttk.Frame(info_left_frame, width=200)
    button_container.pack(padx=5, pady=5, fill=tk.X)
    
    # Các nút cân đối với thumbnail
    btn_frame = ttk.Frame(button_container)
    btn_frame.pack(anchor=tk.CENTER)
    
    app.play_video_btn = tk.Button(btn_frame, text="Xem video", 
                            bg="#3498db", fg="white", 
                            font=("Arial", 11),
                            padx=10, pady=5,
                            relief="flat",
                            command=lambda: play_selected_video(app))
    app.play_video_btn.pack(side=tk.LEFT, padx=5, pady=5)

    app.upload_single_btn = tk.Button(btn_frame, text="Tải lên video đang chọn", 
                                bg="#3498db", fg="white", 
                                font=("Arial", 11),
                                padx=10, pady=5,
                                relief="flat",
                                command=lambda: upload_selected_video(app))
    app.upload_single_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Frame thông tin bên phải
    info_right_frame = ttk.Frame(info_layout)
    info_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
    
    # Frame thông tin chi tiết
    info_details_frame = ttk.Frame(info_right_frame)
    info_details_frame.pack(fill=tk.BOTH, expand=True)
    
    # Thông tin chi tiết - hiển thị các thông tin cụ thể hơn
    info_details = [
        ("Thông tin video", ""),
        ("Tên file:", ""),
        ("Thời lượng:", ""),
        ("Độ phân giải:", ""),
        ("Kích thước:", ""),
        ("Codec:", ""),
        ("Định dạng:", "")
    ]
    
    # Lưu các biến hiển thị thông tin
    app.info_vars = {}
    row = 0
    
    # Header
    header_label = ttk.Label(info_details_frame, text=info_details[0][0], font=("Arial", 11, "bold"))
    header_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
    row += 1
    
    # Các thông tin chi tiết
    for label_text, value in info_details[1:]:
        ttk.Label(info_details_frame, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=2)
        
        var = tk.StringVar(value=value)
        app.info_vars[label_text] = var
        
        ttk.Label(info_details_frame, textvariable=var).grid(row=row, column=1, sticky=tk.W, pady=2)
        row += 1
    
    # Frame hiển thị các frame từ video
    frames_frame = ttk.LabelFrame(parent, text="Các khung hình từ video")
    frames_frame.pack(fill=tk.X, padx=0, pady=5)
    
    # Frame chứa các hình thu nhỏ
    app.frames_container = ttk.Frame(frames_frame)
    app.frames_container.pack(fill=tk.X, padx=5, pady=5)
    
    # Configure grid columns to be equal
    for i in range(5):
        app.frames_container.columnconfigure(i, weight=1, uniform="equal")
    
    # Tạo 5 label cho các frame
    app.frame_labels = []
    for i in range(5):
        frame_container = ttk.Frame(app.frames_container, height=210)
        frame_container.grid(row=0, column=i, padx=4, sticky="ew")
        frame_container.pack_propagate(False)  # Giữ kích thước cố định
        
        # Sử dụng Label thông thường 
        label = tk.Label(frame_container, text=f"Frame {i+1}", 
                       bg="white", relief="solid", bd=1)
        label.pack(fill=tk.BOTH, expand=True)
        
        app.frame_labels.append(label)
    
    # Cập nhật danh sách khi tab được tạo
    folder_path = app.folder_path.get()
    if folder_path and os.path.exists(folder_path) and os.path.isdir(folder_path):
        refresh_video_list(app)
    
    # Disable buttons until video is selected
    app.play_video_btn.config(state=tk.DISABLED)
    app.upload_single_btn.config(state=tk.DISABLED)

def switch_tab(app, tab_code):
    """
    Chuyển đổi giữa các tab nội dung
    
    Args:
        app: Đối tượng TelegramUploaderApp
        tab_code: Mã tab cần chuyển đến
    """
    # Cập nhật trạng thái nút
    for code, btn in app.sub_tab_buttons.items():
        if code == tab_code:
            btn.config(bg="#4a7ebb", fg="white", relief="sunken")
        else:
            btn.config(bg="#f0f0f0", fg="black", relief="raised")
    
    # Lưu tab hiện tại
    app.current_tab = tab_code
    
    # Xóa nội dung hiện tại
    for widget in app.tab_content_frame.winfo_children():
        widget.destroy()
    
    # Hiển thị nội dung tab mới
    if tab_code == "manual":
        create_manual_tab(app, app.tab_content_frame)
    elif tab_code == "auto":
        create_auto_tab(app, app.tab_content_frame)
    elif tab_code == "duplicate":
        create_duplicate_tab(app, app.tab_content_frame)
    elif tab_code == "uploaded":
        create_uploaded_tab(app, app.tab_content_frame)

def create_auto_tab(app, parent):
    """
    Tạo giao diện tab tải lên tự động
    
    Args:
        app: Đối tượng TelegramUploaderApp
        parent: Frame cha
    """
    # Hiển thị thông báo "Đang phát triển"
    ttk.Label(parent, text="Nội dung của tab Tải lên tự động").pack(pady=20)
    # Tương tự như trong module auto_tab.py

def create_duplicate_tab(app, parent):
    """
    Tạo giao diện tab danh sách video trùng
    
    Args:
        app: Đối tượng TelegramUploaderApp
        parent: Frame cha
    """
    # Hiển thị thông báo "Đang phát triển"
    ttk.Label(parent, text="Nội dung của tab Danh sách video trùng").pack(pady=20)
    # Ở đây sẽ hiển thị danh sách các video trùng lặp đã phát hiện

def create_uploaded_tab(app, parent):
    """
    Tạo giao diện tab danh sách video đã tải lên
    
    Args:
        app: Đối tượng TelegramUploaderApp
        parent: Frame cha
    """
    # Hiển thị thông báo "Đang phát triển"
    ttk.Label(parent, text="Nội dung của tab Danh sách video đã tải lên").pack(pady=20)
    # Ở đây sẽ hiển thị danh sách video đã tải lên từ lịch sử

def change_page(app, delta):
    """
    Thay đổi trang hiển thị
    
    Args:
        app: Đối tượng TelegramUploaderApp
        delta: -1 để trở về trang trước, 1 để đến trang tiếp
    """
    total_items = len(app.video_items)
    total_pages = max(1, math.ceil(total_items / app.items_per_page))
    
    # Tính trang mới
    new_page = app.current_page + delta
    
    # Kiểm tra giới hạn
    if new_page < 1 or new_page > total_pages:
        return
    
    # Cập nhật trang hiện tại
    app.current_page = new_page
    
    # Cập nhật thông tin trang
    app.page_info_var.set(f"Trang {app.current_page}/{total_pages}")
    
    # Cập nhật trạng thái nút
    app.prev_page_btn["state"] = tk.NORMAL if app.current_page > 1 else tk.DISABLED
    app.next_page_btn["state"] = tk.NORMAL if app.current_page < total_pages else tk.DISABLED
    
    # Cập nhật nội dung bảng
    update_table_content(app)

def update_table_content(app):
    """Cập nhật nội dung bảng theo trang hiện tại"""
    # Xóa tất cả các mục trong bảng
    for item in app.video_tree.get_children():
        app.video_tree.delete(item)
    
    # Tính chỉ số bắt đầu và kết thúc
    start_idx = (app.current_page - 1) * app.items_per_page
    end_idx = min(start_idx + app.items_per_page, len(app.video_items))
    
    # Thêm các mục của trang hiện tại vào bảng
    for i in range(start_idx, end_idx):
        item_data = app.video_items[i]
        video_name = item_data["name"]
        status = item_data["status"]
        info = item_data["info"]
        tags = item_data["tags"]
        
        # Thêm vào treeview với ô checkbox (rỗng, sẽ được vẽ sau)
        item_id = app.video_tree.insert("", tk.END, values=(" ", video_name, status, info), tags=tags)
        
        # Tạo biến checkbox mới nếu chưa có
        if item_id not in app.video_checkboxes:
            app.video_checkboxes[item_id] = tk.BooleanVar(value=False)
    
    # Vẽ các checkbox sau khi đã thêm vào bảng
    app.render_checkboxes()

def browse_folder(app, auto=False):
    """
    Mở hộp thoại chọn thư mục
    
    Args:
        app: Đối tượng TelegramUploaderApp
        auto (bool): True nếu chọn thư mục cho tab tự động
    """
    folder_path = filedialog.askdirectory(title="Chọn thư mục chứa video")
    
    if folder_path:
        if auto:
            app.auto_folder_path.set(folder_path)
            # Lưu vào cấu hình
            app.config['SETTINGS']['video_folder'] = folder_path
            app.config_manager.save_config(app.config)
        else:
            app.folder_path.set(folder_path)
            # Làm mới danh sách video
            refresh_video_list(app)
            # Lưu vào cấu hình
            app.config['SETTINGS']['video_folder'] = folder_path
            app.config_manager.save_config(app.config)

def refresh_video_list(app):
    """
    Làm mới danh sách video từ thư mục đã chọn
    
    Args:
        app: Đối tượng TelegramUploaderApp
    """
    folder_path = app.folder_path.get()
    
    if not folder_path or not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        messagebox.showerror("Lỗi", "Thư mục không hợp lệ hoặc không tồn tại!")
        return
    
    # Xóa danh sách hiện tại
    for item in app.video_tree.get_children():
        app.video_tree.delete(item)
    app.videos = {}
    app.duplicate_groups = []
    app.video_checkboxes = {}
    app.video_items = []
    
    # Xóa các checkbox widget hiện tại
    if hasattr(app, 'checkbox_widgets'):
        for checkbox in app.checkbox_widgets:
            checkbox.destroy()
    app.checkbox_widgets = []
    
    # Lấy danh sách phần mở rộng video hợp lệ
    extensions = app.config['SETTINGS']['video_extensions'].split(',')
    
    # Cập nhật trạng thái
    app.status_var.set("Đang quét thư mục...")
    app.root.update_idletasks()
    
    # Quét thư mục
    video_files = []
    for file in os.listdir(folder_path):
        file_ext = os.path.splitext(file)[1].lower()
        if file_ext in extensions:
            video_files.append(file)
    
    # Kiểm tra nếu không có video nào
    if not video_files:
        app.status_var.set(f"Không tìm thấy video trong thư mục (định dạng hỗ trợ: {', '.join(extensions)})")
        app.total_info_var.set("Tổng: 0 video, 0 video trùng, 0 video đã tải lên")
        
        # Cập nhật phân trang
        app.current_page = 1
        app.page_info_var.set("Trang 1/1")
        app.prev_page_btn["state"] = tk.DISABLED
        app.next_page_btn["state"] = tk.DISABLED
        return
    
    # Tạo danh sách video đã tải lên để so sánh
    already_uploaded_videos = set()
    
    # Tạo danh sách các mục video
    for video in video_files:
        # Đường dẫn đầy đủ
        video_path = os.path.join(folder_path, video)
        app.videos[video] = video_path
        
        # Thêm vào danh sách
        app.video_items.append({
            "name": video,
            "path": video_path,
            "status": "",
            "info": "",
            "tags": ()
        })
    
    # Nếu có yêu cầu kiểm tra với lịch sử
    if app.check_history_var.get():
        app.status_var.set("Đang kiểm tra với lịch sử tải lên...")
        app.root.update_idletasks()
        
        # Lấy lịch sử đã tải lên
        upload_history = app.upload_history.get_all_uploads()
        
        # Kiểm tra từng video
        for i, item in enumerate(app.video_items):
            video_path = item["path"]
            
            if video_path:
                video_hash = app.video_analyzer.calculate_video_hash(video_path)
                if video_hash and app.upload_history.is_uploaded(video_hash):
                    # Đánh dấu đã tải lên
                    app.video_items[i]["status"] = "Đã tải lên"
                    app.video_items[i]["tags"] = ("uploaded",)
                    already_uploaded_videos.add(item["name"])
    
    # Nếu có yêu cầu kiểm tra trùng lặp
    duplicate_count = 0
    if app.check_duplicates_var.get() and len(video_files) > 1:
        app.status_var.set("Đang phân tích video để tìm trùng lặp...")
        app.root.update_idletasks()
        
        # Tìm các video trùng lặp
        video_paths = [os.path.join(folder_path, video) for video in video_files]
        app.duplicate_groups = app.video_analyzer.find_duplicates(video_paths)
        
        # Đánh dấu các video trùng lặp
        if app.duplicate_groups:
            # Danh sách video đã đánh dấu trùng lặp
            marked_videos = set()
            
            for group in app.duplicate_groups:
                # Chỉ đánh dấu nếu có từ 2 video trở lên trong nhóm
                if len(group) > 1:
                    for video_path in group:
                        video_name = os.path.basename(video_path)
                        
                        # Tìm video trong danh sách
                        for i, item in enumerate(app.video_items):
                            if item["name"] == video_name:
                                # Trạng thái hiện tại
                                current_status = item["status"] or "Trùng lặp"
                                
                                # Tìm tên video trùng lặp khác trong nhóm
                                dup_names = [os.path.basename(v) for v in group if v != video_path]
                                info = f"Trùng với: {', '.join(dup_names[:2])}"
                                if len(dup_names) > 2:
                                    info += f" và {len(dup_names)-2} video khác"
                                
                                # Cập nhật thông tin
                                app.video_items[i]["status"] = current_status
                                app.video_items[i]["info"] = info
                                app.video_items[i]["tags"] = ("duplicate",)
                                marked_videos.add(video_name)
                                break
            
            duplicate_count = len(marked_videos)
    
    # Cập nhật thông tin tổng số
    app.total_info_var.set(f"Tổng: {len(video_files)} video, {duplicate_count} video trùng, {len(already_uploaded_videos)} video đã tải lên")
    app.status_var.set(f"Đã tìm thấy {len(video_files)} video")
    
    # Cập nhật phân trang
    total_pages = max(1, math.ceil(len(app.video_items) / app.items_per_page))
    app.current_page = 1
    app.page_info_var.set(f"Trang 1/{total_pages}")
    
    # Cập nhật trạng thái nút phân trang
    app.prev_page_btn["state"] = tk.DISABLED
    app.next_page_btn["state"] = tk.NORMAL if total_pages > 1 else tk.DISABLED
    
    # Cập nhật nội dung bảng
    update_table_content(app)

def on_video_tree_click(app, event):
    """
    Xử lý khi click vào bảng
    
    Args:
        app: Đối tượng TelegramUploaderApp
        event: Sự kiện click
    """
    region = app.video_tree.identify("region", event.x, event.y)
    item = app.video_tree.identify("item", event.x, event.y)
    column = app.video_tree.identify("column", event.x, event.y)
    
    if region == "heading" and column == "#1":
        # Toggle tất cả các checkbox khi click vào heading
        toggle_all_checkboxes(app)
        return
    
    if not item:
        return  # Bỏ qua nếu không click vào item nào
    
    # Nếu click vào ô checkbox hoặc tên file
    if column == "#1" or column == "#2":
        # Nếu click vào ô checkbox, toggle trạng thái checkbox
        if column == "#1":
            check_var = app.video_checkboxes.get(item)
            if check_var:
                check_var.set(not check_var.get())
                app.render_checkboxes()
        
        # Dù click vào checkbox hay tên file, đều chọn video để hiển thị thông tin
        app.video_tree.selection_set(item)
        on_video_select(app, None)  # Gọi hàm hiển thị thông tin video

def toggle_all_checkboxes(app):
    """
    Toggle tất cả các checkbox trong treeview
    
    Args:
        app: Đối tượng TelegramUploaderApp
    """
    # Kiểm tra xem có hàng nào được chọn không
    any_checked = False
    for item_id in app.video_checkboxes:
        if app.video_checkboxes[item_id].get():
            any_checked = True
            break
    
    # Đảo trạng thái - nếu có checkbox nào được chọn, bỏ chọn tất cả, ngược lại chọn tất cả
    new_state = not any_checked
    
    # Cập nhật trạng thái của tất cả checkbox
    for item_id in app.video_checkboxes:
        app.video_checkboxes[item_id].set(new_state)
    
    # Render lại các checkbox
    app.render_checkboxes()

def select_all_videos(app):
    """Chọn tất cả các video trong danh sách"""
    for item_id in app.video_checkboxes:
        app.video_checkboxes[item_id].set(True)
    app.render_checkboxes()

def deselect_all_videos(app):
    """Bỏ chọn tất cả các video trong danh sách"""
    for item_id in app.video_checkboxes:
        app.video_checkboxes[item_id].set(False)
    app.render_checkboxes()

def on_video_select(app, event):
    """
    Xử lý khi chọn video từ treeview
    
    Args:
        app: Đối tượng TelegramUploaderApp
        event: Sự kiện chọn
    """
    # Lấy video đã chọn
    selected_items = app.video_tree.selection()
    
    if not selected_items:
        # Không có video nào được chọn
        app.thumbnail_label.config(text="Bạn hãy nhấn vào tên file bất kỳ")
        # Xóa thông tin hiển thị
        reset_video_info(app)
        app.play_video_btn.config(state=tk.DISABLED)
        app.upload_single_btn.config(state=tk.DISABLED)
        
        # Xóa các frame
        for label in app.frame_labels:
            label.config(text="", image="")
        
        return
    
    # Lấy tên video
    video_name = app.video_tree.item(selected_items[0], "values")[1]
    video_path = app.videos.get(video_name)
    
    if not video_path or not os.path.exists(video_path):
        return
    
    # Bật nút phát video và tải lên
    app.play_video_btn.config(state=tk.NORMAL)
    app.upload_single_btn.config(state=tk.NORMAL)
    
    # Hiển thị thông tin video
    display_video_info(app, video_path)
    
    # Hiển thị các frame từ video
    display_video_frames(app, video_path)

def reset_video_info(app):
    """Xóa thông tin video hiển thị"""
    for key, var in app.info_vars.items():
        var.set("")

def play_selected_video(app):
    """
    Phát video đã chọn bằng trình phát mặc định của hệ thống
    
    Args:
        app: Đối tượng TelegramUploaderApp
    """
    # Lấy video đã chọn
    selected_items = app.video_tree.selection()
    if not selected_items:
        return
    
    # Lấy tên video
    video_name = app.video_tree.item(selected_items[0], "values")[1]
    video_path = app.videos.get(video_name)
    
    if not video_path or not os.path.exists(video_path):
        messagebox.showerror("Lỗi", "Không tìm thấy file video!")
        return
    
    try:
        # Mở video bằng ứng dụng mặc định
        if os.name == 'nt':  # Windows
            os.startfile(video_path)
        elif os.name == 'posix':  # Linux, macOS
            import subprocess
            subprocess.call(('xdg-open' if os.uname().sysname == 'Linux' else 'open', video_path))
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể mở video: {str(e)}")

def upload_selected_video(app):
    """
    Tải lên video đã chọn
    
    Args:
        app: Đối tượng TelegramUploaderApp
    """
    # Lấy video đã chọn
    selected_items = app.video_tree.selection()
    if not selected_items:
        return
    
    # Lấy tên video
    video_name = app.video_tree.item(selected_items[0], "values")[1]
    video_path = app.videos.get(video_name)
    
    if not video_path or not os.path.exists(video_path):
        messagebox.showerror("Lỗi", "Không tìm thấy file video!")
        return
    
    # Kiểm tra cấu hình Telegram
    bot_token = app.config['TELEGRAM']['bot_token']
    chat_id = app.config['TELEGRAM']['chat_id']
    
    if not bot_token or not chat_id:
        messagebox.showerror("Lỗi", "Vui lòng cấu hình Bot Token và Chat ID trong tab Cài đặt!")
        app.notebook.select(1)  # Chuyển đến tab Cài đặt
        return
    
    # Kết nối lại với Telegram nếu cần
    if not app.telegram_api.connected:
        if not app.telegram_api.connect(bot_token):
            messagebox.showerror("Lỗi", "Không thể kết nối với Telegram API. Vui lòng kiểm tra Bot Token và kết nối internet!")
            return
    
    # Cập nhật trạng thái
    app.status_var.set(f"Đang tải lên video: {video_name}")
    app.root.update_idletasks()
    
    # Tải lên video
    try:
        success = app.telegram_api.send_video(chat_id, video_path)
        
        if success:
            app.status_var.set(f"Đã tải lên thành công: {video_name}")
            
            # Thêm vào lịch sử
            video_hash = app.video_analyzer.calculate_video_hash(video_path)
            if video_hash:
                file_size = os.path.getsize(video_path)
                app.upload_history.add_upload(video_hash, video_name, video_path, file_size)
                
                # Cập nhật trạng thái trong treeview
                for i, item in enumerate(app.video_items):
                    if item["name"] == video_name:
                        app.video_items[i]["status"] = "Đã tải lên"
                        app.video_items[i]["tags"] = ("uploaded",)
                        break
                
                # Cập nhật hiển thị
                update_table_content(app)
        else:
            app.status_var.set(f"Tải lên thất bại: {video_name}")
    
    except Exception as e:
        app.status_var.set(f"Lỗi khi tải lên: {str(e)}")

def display_video_frames(app, video_path):
    """
    Hiển thị các frame từ video
    
    Args:
        app: Đối tượng TelegramUploaderApp
        video_path (str): Đường dẫn đến file video
    """
    try:
        # Sử dụng OpenCV để lấy các frame
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return
        
        # Lấy tổng số frame
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Chọn 5 vị trí cho các frame
        positions = [0.1, 0.3, 0.5, 0.7, 0.9]  # 10%, 30%, 50%, 70%, 90%
        
        # Calculate frame container sizes
        frame_containers = [label.master for label in app.frame_labels]
        
        # Get the width of the frames container
        total_width = app.frames_container.winfo_width()
        if total_width <= 1:  # If container not yet realized
            total_width = 1000  # Default assumption
        
        # Calculate the width for each frame (5 equal parts)
        frame_width = (total_width - 40) // 5  # Account for padding
        frame_height = 210  # Fixed height we want
        
        # Lưu các frame
        frames = []
        
        for i, pos in enumerate(positions):
            frame_pos = int(frame_count * pos)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = cap.read()
            
            if ret and i < len(app.frame_labels):
                # Chuyển frame sang định dạng PIL
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_pil = Image.fromarray(frame)
                
                # Resize to fill the container completely
                frame_pil = frame_pil.resize((frame_width, frame_height), Image.LANCZOS)
                
                # Chuyển sang định dạng Tkinter
                frame_tk = ImageTk.PhotoImage(frame_pil)
                frames.append(frame_tk)
                
                # Set the image in the label
                app.frame_labels[i].config(text="", image=frame_tk)
        
        cap.release()
        
        # Lưu tham chiếu để tránh bị thu hồi bởi garbage collector
        app.current_frames = frames
    
    except Exception as e:
        logger.error(f"Lỗi khi lấy frame từ video: {str(e)}")

def display_video_info(app, video_path):
    """
    Hiển thị thông tin chi tiết của video
    
    Args:
        app: Đối tượng TelegramUploaderApp
        video_path (str): Đường dẫn đến file video
    """
    # Lấy thông tin video
    info = app.video_analyzer.get_video_info(video_path)
    
    if not info:
        return
    
    # Get the thumbnail frame dimensions
    thumbnail_frame = app.thumbnail_label.master
    frame_width = thumbnail_frame.winfo_width()
    frame_height = thumbnail_frame.winfo_height()
    
    # If frame not yet realized, use configured dimensions
    if frame_width <= 1:
        frame_width = 350
    if frame_height <= 1:
        frame_height = 210
    
    try:
        # Create thumbnail directly from the video file
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                # Convert to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Create PIL image and resize to fill the frame exactly
                pil_img = Image.fromarray(frame)
                pil_img = pil_img.resize((frame_width, frame_height), Image.LANCZOS)
                
                # Create PhotoImage for display
                thumbnail = ImageTk.PhotoImage(pil_img)
                
                # Store reference and update label
                app.current_thumbnail = thumbnail
                app.thumbnail_label.config(image=thumbnail, text="")
            else:
                app.thumbnail_label.config(text="Không thể đọc video", image="")
            
            cap.release()
        else:
            app.thumbnail_label.config(text="Không thể mở video", image="")
    except Exception as e:
        logger.error(f"Lỗi khi tạo thumbnail: {str(e)}")
        app.thumbnail_label.config(text="Lỗi khi tạo thumbnail", image="")
    
    # Lấy thông tin cần hiển thị
    file_name = info.get('file_name', os.path.basename(video_path))
    duration = info.get('duration', 0)
    resolution = info.get('resolution', 'Không rõ')
    file_size = info.get('file_size', 'Không rõ')
    
    # Định dạng thời lượng (giây -> HH:MM:SS)
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)
    formatted_duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # Cập nhật thông tin hiển thị
    app.info_vars["Tên file:"].set(file_name)
    app.info_vars["Thời lượng:"].set(formatted_duration)
    app.info_vars["Độ phân giải:"].set(resolution)
    app.info_vars["Kích thước:"].set(file_size)
    app.info_vars["Codec:"].set(info.get('codec', 'H.264'))
    app.info_vars["Định dạng:"].set(info.get('format', 'MP4'))