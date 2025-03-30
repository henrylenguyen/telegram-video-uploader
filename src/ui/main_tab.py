"""
Module tạo và quản lý tab tải lên chính.
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from PIL import Image, ImageTk
import cv2

logger = logging.getLogger("MainTab")

def create_main_tab(app, parent):
    """
    Tạo giao diện cho tab tải lên chính
    
    Args:
        app: Đối tượng TelegramUploaderApp
        parent: Frame cha
    """
    # Tạo canvas và thanh cuộn để cho phép cuộn toàn bộ nội dung
    main_canvas = tk.Canvas(parent)
    main_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=main_canvas.yview)
    
    # Tạo frame con trong canvas để chứa toàn bộ nội dung
    content_frame = ttk.Frame(main_canvas)
    
    # Cấu hình canvas để cuộn
    main_canvas.configure(yscrollcommand=main_scrollbar.set)
    main_canvas.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
    
    # Tạo cửa sổ cho content_frame trong canvas
    main_canvas.create_window((0, 0), window=content_frame, anchor="nw", width=main_canvas.winfo_width())
    
    # Sắp xếp canvas và thanh cuộn
    main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Bổ sung chức năng cuộn bằng chuột
    def _on_mousewheel(event):
        main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    content_frame.bind("<MouseWheel>", _on_mousewheel)
    main_canvas.bind("<MouseWheel>", _on_mousewheel)
    
    # Frame chọn thư mục
    folder_frame = ttk.LabelFrame(content_frame, text="Thư mục chứa video")
    folder_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Đường dẫn thư mục
    app.folder_path = tk.StringVar()
    app.folder_path.set(app.config['SETTINGS']['video_folder'])
    
    folder_entry = ttk.Entry(folder_frame, textvariable=app.folder_path, width=50)
    folder_entry.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.X, expand=True)
    
    # Nút "Duyệt..."
    browse_btn = ttk.Button(folder_frame, text="Duyệt...", 
                           command=lambda: browse_folder(app))
    browse_btn.pack(side=tk.RIGHT, padx=5, pady=10)
    
    # Frame kiểm soát
    control_top_frame = ttk.Frame(content_frame)
    control_top_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # Nút làm mới danh sách
    refresh_btn = ttk.Button(control_top_frame, text="Làm mới danh sách", 
                           command=lambda: refresh_video_list(app))
    refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Checkbox kiểm tra trùng lặp
    app.check_duplicates_var = tk.BooleanVar()
    app.check_duplicates_var.set(app.config['SETTINGS'].getboolean('check_duplicates', True))
    
    check_duplicates_cb = ttk.Checkbutton(
        control_top_frame, 
        text="Kiểm tra video trùng lặp", 
        variable=app.check_duplicates_var,
        command=lambda: refresh_video_list(app)
    )
    check_duplicates_cb.pack(side=tk.RIGHT, padx=5, pady=5)
    
    # Checkbox kiểm tra với lịch sử
    app.check_history_var = tk.BooleanVar()
    app.check_history_var.set(True)
    
    check_history_cb = ttk.Checkbutton(
        control_top_frame, 
        text="Kiểm tra với lịch sử đã tải lên", 
        variable=app.check_history_var,
        command=lambda: refresh_video_list(app)
    )
    check_history_cb.pack(side=tk.RIGHT, padx=15, pady=5)
    
    # Frame hiển thị danh sách video
    videos_frame = ttk.LabelFrame(content_frame, text="Danh sách video")
    videos_frame.pack(fill=tk.BOTH, padx=10, pady=10)
    
    # Tạo frame cho danh sách và thanh cuộn
    list_frame = ttk.Frame(videos_frame)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Cấu hình cột
    app.video_tree = ttk.Treeview(list_frame, columns=("select", "filename", "status", "info"), show="headings", height=12)
    app.video_tree.heading("select", text="")
    app.video_tree.heading("filename", text="Tên file")
    app.video_tree.heading("status", text="Trạng thái")
    app.video_tree.heading("info", text="Thông tin thêm")
    
    # Thiết lập độ rộng cột
    app.video_tree.column("select", width=30, anchor=tk.CENTER)
    app.video_tree.column("filename", width=400, anchor=tk.W)
    app.video_tree.column("status", width=150, anchor=tk.CENTER)
    app.video_tree.column("info", width=200, anchor=tk.W)
    
    # Tạo thanh cuộn cho treeview
    tree_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=app.video_tree.yview)
    app.video_tree.configure(yscrollcommand=tree_scrollbar.set)
    
    # Sắp xếp treeview và thanh cuộn
    tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    app.video_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Biến lưu trữ checkbox
    app.video_checkboxes = {}  # {item_id: BooleanVar}
    
    # Xử lý sự kiện khi click vào cột checkbox
    app.video_tree.bind("<ButtonRelease-1>", lambda event: on_video_tree_click(app, event))
    
    # Xử lý sự kiện khi chọn video
    app.video_tree.bind("<<TreeviewSelect>>", lambda event: on_video_select(app, event))
    
    # Tạo 3 nút dưới danh sách
    tree_buttons_frame = ttk.Frame(videos_frame)
    tree_buttons_frame.pack(fill=tk.X, pady=5)
    
    select_all_btn = ttk.Button(tree_buttons_frame, text="Chọn tất cả", 
                               command=lambda: select_all_videos(app))
    select_all_btn.pack(side=tk.LEFT, padx=5)
    
    deselect_all_btn = ttk.Button(tree_buttons_frame, text="Bỏ chọn tất cả", 
                                 command=lambda: deselect_all_videos(app))
    deselect_all_btn.pack(side=tk.LEFT, padx=5)
    
    invert_selection_btn = ttk.Button(tree_buttons_frame, text="Đảo chọn", 
                                     command=lambda: invert_video_selection(app))
    invert_selection_btn.pack(side=tk.LEFT, padx=5)
    
    # Frame thông tin video
    info_frame = ttk.LabelFrame(content_frame, text="Thông tin video đã chọn")
    info_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # Frame thông tin bên trái
    info_left_frame = ttk.Frame(info_frame)
    info_left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
    
    # Hiển thị hình thu nhỏ
    app.thumbnail_label = ttk.Label(info_left_frame, text="Không có video nào được chọn")
    app.thumbnail_label.pack(padx=5, pady=5)
    
    # Thêm nút để xem video
    app.play_video_btn = ttk.Button(info_left_frame, text="Xem video", 
                                   command=lambda: play_selected_video(app),
                                   state=tk.DISABLED)
    app.play_video_btn.pack(padx=5, pady=5)
    
    # Frame thông tin bên phải
    info_right_frame = ttk.Frame(info_frame)
    info_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Thông tin chi tiết với thanh cuộn
    info_text_frame = ttk.Frame(info_right_frame)
    info_text_frame.pack(fill=tk.BOTH, expand=True)
    
    app.info_text = tk.Text(info_text_frame, height=6, width=40, wrap=tk.WORD, font=("Arial", 10))
    
    # Thanh cuộn cho thông tin
    info_scrollbar = ttk.Scrollbar(info_text_frame, orient=tk.VERTICAL, command=app.info_text.yview)
    app.info_text.configure(yscrollcommand=info_scrollbar.set)
    
    info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    app.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    app.info_text.config(state=tk.DISABLED)
    
    # Frame hiển thị các frame từ video
    frames_frame = ttk.LabelFrame(content_frame, text="Các khung hình từ video")
    frames_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # Frame chứa các hình thu nhỏ
    app.frames_container = ttk.Frame(frames_frame)
    app.frames_container.pack(fill=tk.X, padx=5, pady=5)
    
    # Tạo 5 label cho các frame
    app.frame_labels = []
    for i in range(5):
        frame = ttk.Frame(app.frames_container)
        frame.pack(side=tk.LEFT, padx=5, expand=True)
        
        label = ttk.Label(frame, text=f"Frame {i+1}")
        label.pack(pady=2)
        
        app.frame_labels.append(label)
    
    # Frame trạng thái và điều khiển
    control_frame = ttk.Frame(content_frame)
    control_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Thanh tiến trình
    app.progress = ttk.Progressbar(control_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
    app.progress.pack(fill=tk.X, padx=5, pady=5)
    
    # Nhãn trạng thái
    app.status_var = tk.StringVar()
    app.status_var.set("Sẵn sàng")
    status_label = ttk.Label(control_frame, textvariable=app.status_var, style="Status.TLabel")
    status_label.pack(pady=5)
    
    # Frame chứa các nút điều khiển
    btn_frame = ttk.Frame(control_frame)
    btn_frame.pack(fill=tk.X, pady=10)
    
    # Nút tải lên
    app.upload_btn = ttk.Button(btn_frame, text="Bắt đầu tải lên", 
                              command=lambda: app.uploader.start_upload(app))
    app.upload_btn.pack(side=tk.LEFT, padx=5)
    
    # Nút dừng
    app.stop_btn = ttk.Button(btn_frame, text="Dừng lại", 
                           command=lambda: app.uploader.stop_upload(app), 
                           state=tk.DISABLED)
    app.stop_btn.pack(side=tk.LEFT, padx=5)
    
    # Nút xóa video trùng lặp
    app.remove_duplicates_btn = ttk.Button(btn_frame, text="Loại bỏ trùng lặp", 
                                         command=lambda: remove_duplicates(app))
    app.remove_duplicates_btn.pack(side=tk.RIGHT, padx=5)
    
    # Cập nhật kích thước content_frame khi parent thay đổi kích thước
    def update_canvas_width(event):
        # Thiết lập width của canvas là width của parent trừ đi width của thanh cuộn
        canvas_width = parent.winfo_width() - main_scrollbar.winfo_width() - 10
        main_canvas.itemconfig(main_canvas.find_withtag("all")[0], width=canvas_width)
        
    parent.bind("<Configure>", update_canvas_width)
    
    # Thiết lập style cho treeview
    style = ttk.Style()
    style.configure("Treeview", rowheight=25)
    
    # Kết nối sự kiện MouseWheel từ tất cả các widget đến canvas
    def bind_mousewheel_to_canvas(widget):
        widget.bind("<MouseWheel>", _on_mousewheel)
        for child in widget.winfo_children():
            bind_mousewheel_to_canvas(child)
    
    bind_mousewheel_to_canvas(content_frame)

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
        return
    
    # Tạo danh sách video đã tải lên để so sánh
    already_uploaded_videos = set()
    
    # Thêm video vào treeview
    for video in video_files:
        # Đường dẫn đầy đủ
        video_path = os.path.join(folder_path, video)
        app.videos[video] = video_path
        
        # Tạo checkbox var
        check_var = tk.BooleanVar(value=False)
        
        # Thêm vào treeview với checkbox
        item_id = app.video_tree.insert("", tk.END, values=("☐", video, "", ""))
        
        # Lưu biến checkbox
        app.video_checkboxes[item_id] = check_var
    
    # Nếu có yêu cầu kiểm tra với lịch sử
    if app.check_history_var.get():
        app.status_var.set("Đang kiểm tra với lịch sử tải lên...")
        app.root.update_idletasks()
        
        # Lấy lịch sử đã tải lên
        upload_history = app.upload_history.get_all_uploads()
        
        # Kiểm tra từng video
        for item in app.video_tree.get_children():
            video_name = app.video_tree.item(item, "values")[1]
            video_path = app.videos.get(video_name)
            
            if video_path:
                video_hash = app.video_analyzer.calculate_video_hash(video_path)
                if video_hash and app.upload_history.is_uploaded(video_hash):
                    # Đánh dấu đã tải lên
                    app.video_tree.item(item, values=(app.video_tree.item(item, "values")[0], 
                                                    video_name, 
                                                    "Đã tải lên", 
                                                    ""))
                    already_uploaded_videos.add(video_name)
    
    # Nếu có yêu cầu kiểm tra trùng lặp
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
                        
                        # Tìm video trong treeview
                        for item in app.video_tree.get_children():
                            tree_video_name = app.video_tree.item(item, "values")[1]
                            
                            if tree_video_name == video_name:
                                current_values = app.video_tree.item(item, "values")
                                status = current_values[2] or "Trùng lặp"
                                
                                # Tìm tên video trùng lặp khác trong nhóm
                                dup_names = [os.path.basename(v) for v in group if v != video_path]
                                info = f"Trùng với: {', '.join(dup_names[:2])}"
                                if len(dup_names) > 2:
                                    info += f" và {len(dup_names)-2} video khác"
                                
                                # Cập nhật trạng thái
                                app.video_tree.item(item, values=(current_values[0], 
                                                                 tree_video_name, 
                                                                 status, 
                                                                 info))
                                app.video_tree.item(item, tags=("duplicate",))
                                marked_videos.add(video_name)
                                break
            
            # Đặt style cho video trùng lặp
            app.video_tree.tag_configure("duplicate", background="#FFD2D2")  # Màu đỏ nhạt
            
            app.status_var.set(f"Đã tìm thấy {len(video_files)} video ({len(marked_videos)} video trùng lặp)")
        else:
            app.status_var.set(f"Đã tìm thấy {len(video_files)} video (không có trùng lặp)")
    
    # Đánh dấu các video đã tải lên trước đó
    if already_uploaded_videos:
        # Đặt style cho video đã tải lên
        app.video_tree.tag_configure("uploaded", background="#D2F0FF")  # Màu xanh nhạt
        
        for item in app.video_tree.get_children():
            video_name = app.video_tree.item(item, "values")[1]
            if video_name in already_uploaded_videos:
                # Đánh dấu video đã tải lên
                current_values = app.video_tree.item(item, "values")
                app.video_tree.item(item, values=(current_values[0], 
                                                video_name, 
                                                "Đã tải lên", 
                                                current_values[3]))
                app.video_tree.item(item, tags=("uploaded",))
        
        app.status_var.set(f"Đã tìm thấy {len(video_files)} video ({len(already_uploaded_videos)} đã tải lên trước đó)")

def on_video_tree_click(app, event):
    """
    Xử lý khi click vào cột checkbox
    
    Args:
        app: Đối tượng TelegramUploaderApp
        event: Sự kiện click
    """
    region = app.video_tree.identify("region", event.x, event.y)
    if region == "heading":
        return  # Bỏ qua nếu click vào tiêu đề
    
    item = app.video_tree.identify("item", event.x, event.y)
    if not item:
        return  # Bỏ qua nếu không click vào item nào
    
    column = app.video_tree.identify("column", event.x, event.y)
    if column == "#1":  # Cột checkbox
        # Lấy biến checkbox
        check_var = app.video_checkboxes.get(item)
        if check_var:
            # Đảo trạng thái checkbox
            check_var.set(not check_var.get())
            
            # Cập nhật hiển thị
            current_values = app.video_tree.item(item, "values")
            checkbox_text = "☑" if check_var.get() else "☐"
            
            app.video_tree.item(item, values=(checkbox_text, 
                                            current_values[1], 
                                            current_values[2], 
                                            current_values[3]))

def select_all_videos(app):
    """
    Chọn tất cả video trong danh sách
    
    Args:
        app: Đối tượng TelegramUploaderApp
    """
    for item in app.video_tree.get_children():
        check_var = app.video_checkboxes.get(item)
        if check_var:
            check_var.set(True)
            
            # Cập nhật hiển thị
            current_values = app.video_tree.item(item, "values")
            app.video_tree.item(item, values=("☑", 
                                            current_values[1], 
                                            current_values[2], 
                                            current_values[3]))

def deselect_all_videos(app):
    """
    Bỏ chọn tất cả video trong danh sách
    
    Args:
        app: Đối tượng TelegramUploaderApp
    """
    for item in app.video_tree.get_children():
        check_var = app.video_checkboxes.get(item)
        if check_var:
            check_var.set(False)
            
            # Cập nhật hiển thị
            current_values = app.video_tree.item(item, "values")
            app.video_tree.item(item, values=("☐", 
                                            current_values[1], 
                                            current_values[2], 
                                            current_values[3]))

def invert_video_selection(app):
    """
    Đảo trạng thái chọn tất cả video
    
    Args:
        app: Đối tượng TelegramUploaderApp
    """
    for item in app.video_tree.get_children():
        check_var = app.video_checkboxes.get(item)
        if check_var:
            # Đảo trạng thái
            check_var.set(not check_var.get())
            
            # Cập nhật hiển thị
            current_values = app.video_tree.item(item, "values")
            checkbox_text = "☑" if check_var.get() else "☐"
            
            app.video_tree.item(item, values=(checkbox_text, 
                                            current_values[1], 
                                            current_values[2], 
                                            current_values[3]))

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
        app.thumbnail_label.config(text="Không có video nào được chọn")
        app.info_text.config(state=tk.NORMAL)
        app.info_text.delete(1.0, tk.END)
        app.info_text.config(state=tk.DISABLED)
        app.play_video_btn.config(state=tk.DISABLED)
        
        # Xóa các frame
        for label in app.frame_labels:
            label.config(text="", image="")
        
        return
    
    # Lấy tên video
    video_name = app.video_tree.item(selected_items[0], "values")[1]
    video_path = app.videos.get(video_name)
    
    if not video_path or not os.path.exists(video_path):
        return
    
    # Bật nút phát video
    app.play_video_btn.config(state=tk.NORMAL)
    
    # Hiển thị thông tin video
    display_video_info(app, video_path)
    
    # Hiển thị các frame từ video
    display_video_frames(app, video_path)

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
        
        # Chọn 5 vị trí ngẫu nhiên
        import random
        positions = sorted([random.uniform(0.1, 0.9) for _ in range(5)])
        
        # Lưu các frame
        frames = []
        
        for pos in positions:
            frame_pos = int(frame_count * pos)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = cap.read()
            
            if ret:
                # Chuyển frame sang định dạng PIL
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_pil = Image.fromarray(frame)
                
                # Thay đổi kích thước
                frame_pil = frame_pil.resize((120, 90), Image.LANCZOS)
                
                # Chuyển sang định dạng Tkinter
                frame_tk = ImageTk.PhotoImage(frame_pil)
                frames.append(frame_tk)
        
        cap.release()
        
        # Lưu tham chiếu để tránh bị thu hồi bởi garbage collector
        app.current_frames = frames
        
        # Hiển thị các frame
        for i, frame in enumerate(frames):
            if i < len(app.frame_labels):
                pos_percent = int(positions[i] * 100)
                app.frame_labels[i].config(text=f"Frame {pos_percent}%", image=frame)
    
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
    
    # Tạo hình thu nhỏ
    thumbnail = app.video_analyzer.get_thumbnail(video_path)
    
    if thumbnail:
        # Lưu tham chiếu để tránh bị thu hồi bởi garbage collector
        app.current_thumbnail = thumbnail
        app.thumbnail_label.config(image=thumbnail, text="")
    else:
        app.thumbnail_label.config(text="Không thể tạo hình thu nhỏ", image="")
    
    # Tính hash video để kiểm tra với lịch sử
    video_hash = info.get('hash', None)
    
    # Hiển thị thông tin
    file_name = info.get('file_name', os.path.basename(video_path))
    duration = info.get('duration', 0)
    resolution = info.get('resolution', 'Không rõ')
    file_size = info.get('file_size', 'Không rõ')
    
    # Kiểm tra trùng lặp
    duplicate_info = ""
    history_info = ""
    
    # Kiểm tra với lịch sử tải lên
    if video_hash and app.check_history_var.get():
        if app.upload_history.is_uploaded(video_hash):
            upload_info = app.upload_history.get_upload_info(video_hash)
            if upload_info:
                history_info = f"\n\nĐã tải lên trước đó vào: {upload_info.get('upload_date', 'Không rõ')}"
    
    # Kiểm tra trùng lặp trong thư mục hiện tại
    if app.check_duplicates_var.get() and app.duplicate_groups:
        for group in app.duplicate_groups:
            if video_path in group:
                # Video này nằm trong một nhóm trùng lặp
                if len(group) > 1:
                    other_videos = [os.path.basename(v) for v in group if v != video_path]
                    duplicate_info = f"\n\nTrùng lặp với: {', '.join(other_videos)}"
                break
    
    # Định dạng thông tin
    info_text = (
        f"Tên file: {file_name}\n"
        f"Thời lượng: {duration:.2f} giây\n"
        f"Độ phân giải: {resolution}\n"
        f"Kích thước: {file_size}{duplicate_info}{history_info}"
    )
    
    # Hiển thị thông tin
    app.info_text.config(state=tk.NORMAL)
    app.info_text.delete(1.0, tk.END)
    app.info_text.insert(tk.END, info_text)
    app.info_text.config(state=tk.DISABLED)

def remove_duplicates(app):
    """
    Loại bỏ video trùng lặp khỏi danh sách
    
    Args:
        app: Đối tượng TelegramUploaderApp
    """
    if not app.duplicate_groups and not app.check_history_var.get():
        messagebox.showinfo("Thông báo", "Không có video trùng lặp nào để loại bỏ!")
        return
    
    # Tập hợp các video cần giữ lại (một video từ mỗi nhóm trùng lặp)
    keep_videos = set()
    # Tập hợp các video cần loại bỏ
    remove_videos = set()
    
    # Xử lý trùng lặp trong thư mục hiện tại
    for group in app.duplicate_groups:
        if len(group) > 1:
            # Chọn video có kích thước lớn nhất trong nhóm để giữ lại
            best_video = max(group, key=os.path.getsize)
            
            # Thêm vào danh sách giữ lại
            keep_videos.add(best_video)
            
            # Thêm các video còn lại vào danh sách loại bỏ
            for video in group:
                if video != best_video:
                    remove_videos.add(video)
    
    # Xử lý trùng lặp với lịch sử nếu có yêu cầu
    if app.check_history_var.get():
        # Lấy video trong thư mục
        for video_name, video_path in app.videos.items():
            # Tính hash của video
            video_hash = app.video_analyzer.calculate_video_hash(video_path)
            
            # Kiểm tra nếu đã tồn tại trong lịch sử
            if video_hash and app.upload_history.is_uploaded(video_hash):
                # Thêm vào danh sách loại bỏ nếu không phải là video tốt nhất
                if video_path not in keep_videos:
                    remove_videos.add(video_path)
    
    if not remove_videos:
        messagebox.showinfo("Thông báo", "Không có video trùng lặp nào để loại bỏ!")
        return
    
    # Loại bỏ các video trùng lặp khỏi treeview
    video_names_to_remove = [os.path.basename(video) for video in remove_videos]
    
    # Xóa từ treeview
    for item in list(app.video_tree.get_children()):
        video_name = app.video_tree.item(item, "values")[1]
        if video_name in video_names_to_remove:
            app.video_tree.delete(item)
            # Xóa khỏi dict videos
            if video_name in app.videos:
                del app.videos[video_name]
            # Xóa khỏi video_checkboxes
            if item in app.video_checkboxes:
                del app.video_checkboxes[item]
    
    # Cập nhật trạng thái
    removed_count = len(video_names_to_remove)
    logger.info(f"Đã loại bỏ {removed_count} video trùng lặp")
    app.status_var.set(f"Đã loại bỏ {removed_count} video trùng lặp")