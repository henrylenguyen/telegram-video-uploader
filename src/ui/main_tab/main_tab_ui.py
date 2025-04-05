"""
UI module for the main tab with optimized checkbox handling
"""
import tkinter as tk
from tkinter import ttk
import os
import logging
import math

from .main_tab_func import (
    refresh_video_list,
    browse_folder,
    on_video_tree_click, 
    on_video_select,
    select_all_videos,
    deselect_all_videos,
    change_page,
    play_selected_video,
    upload_selected_video
)

logger = logging.getLogger("MainTabUI")

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

    # Ô nhập liệu với font lớn hơn và có padding
    folder_entry = tk.Entry(entry_container, textvariable=app.folder_path, 
                          font=("Arial", 14),
                          relief="groove", bg="white",
                          highlightthickness=1,
                          highlightbackground="#cccccc",
                          bd=5)  # Sử dụng border để tạo padding
    folder_entry.pack(fill=tk.BOTH, expand=True)

    # Cài đặt văn bản có khoảng trống bên trái để tạo padding
    def pad_text(event=None):
        """Thêm padding bằng cách thêm khoảng trống vào đầu text"""
        current_text = folder_entry.get()
        # Chỉ thêm nếu không có sẵn
        if not current_text.startswith("  "):
            folder_entry.delete(0, tk.END)
            folder_entry.insert(0, "  " + current_text.lstrip())

    # Áp dụng padding ban đầu và khi focus
    folder_entry.bind("<FocusIn>", pad_text)
    app.root.after(100, pad_text)  # Áp dụng padding sau khi khởi tạo

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
    
    # Tab frame - Make more prominent
    tab_frame = tk.Frame(tab_container, bg="#F0F0F0", bd=1, relief="raised")
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
        # First tab is active by default
        if code == "manual":
            btn = tk.Button(
                tab_frame, 
                text=name,
                font=("Arial", 11, "bold"),
                padx=15, pady=8,
                relief="flat",
                bg="#2E86C1",  # Blue color for active tab
                fg="white",
                bd=1,
                command=lambda c=code: switch_tab(app, c)
            )
        else:
            btn = tk.Button(
                tab_frame, 
                text=name,
                font=("Arial", 11),
                padx=15, pady=8,
                relief="flat",
                bg="#F0F0F0",
                fg="#2C3E50",  # Dark blue text
                bd=0,
                command=lambda c=code: switch_tab(app, c)
            )
            # Add hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#E0E0E0"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#F0F0F0"))
            
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

    # Thêm phương thức render_checkboxes vào app
    app.render_checkboxes = lambda: render_checkboxes(app)

def create_manual_tab(app, parent):
    """
    Tạo giao diện tab tải lên thủ công
    
    Args:
        app: Đối tượng TelegramUploaderApp
        parent: Frame cha
    """
    # Khởi tạo info_vars nếu chưa có
    if not hasattr(app, 'info_vars'):
        app.info_vars = {}
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
    app.video_tree.heading("select", text="Chọn")  # Add text to the first column heading
    app.video_tree.heading("filename", text="Tên file")
    app.video_tree.heading("status", text="Trạng thái")
    app.video_tree.heading("info", text="Thông tin thêm")

    # Thiết lập độ rộng cột
    app.video_tree.column("select", width=60, anchor=tk.CENTER)  # Increase width for checkbox+text
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
    
    # Bỏ thanh tiến trình vì đã có modal progress
    
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
        ("Định dạng:", ""),
    ]

    row = 0
    # Header
    header_label = ttk.Label(info_details_frame, text=info_details[0][0], font=("Arial", 11, "bold"))
    header_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
    row += 1

    # Các thông tin chi tiết
    for label_text, value in info_details[1:]:
        label = ttk.Label(info_details_frame, text=label_text)
        label.grid(row=row, column=0, sticky=tk.W, pady=2)
        
        var = tk.StringVar(value=value)
        app.info_vars[label_text] = var
        
        value_label = ttk.Label(info_details_frame, textvariable=var)
        value_label.grid(row=row, column=1, sticky=tk.W, pady=2)
        
        row += 1

    # Thêm trường trạng thái với tk.Label thay vì ttk.Label để hỗ trợ màu sắc
    status_label = ttk.Label(info_details_frame, text="Trạng thái:")
    status_label.grid(row=row, column=0, sticky=tk.W, pady=2)

    # Sử dụng tk.Label thông thường thay vì ttk.Label để có thể thay đổi màu
    # Không cố gắng lấy background từ ttk.Frame, sử dụng màu mặc định của hệ thống
    app.status_value_label = tk.Label(info_details_frame, text="", anchor=tk.W)
    app.status_value_label.grid(row=row, column=1, sticky=tk.W, pady=2)
  
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
        frame_container = ttk.Frame(app.frames_container, height=280, width=170)  # Chiều cao cố định 280px
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
    
    def initialize_checkboxes():
      """Khởi tạo checkbox sau khi UI đã được render"""
      # Import render_checkboxes từ main_tab_func
      try:
          from ui.main_tab.main_tab_func import render_checkboxes
      except ImportError:
          try:
              from .main_tab_func import render_checkboxes
          except ImportError:
              from src.ui.main_tab.main_tab_func import render_checkboxes
      
      # Đảm bảo UI đã cập nhật
      app.root.update_idletasks()
      
      # Vẽ lại checkbox
      render_checkboxes(app)
      
      # Vẽ checkbox khi chuyển tab hoặc mở dialog
      def add_tab_callbacks():
          if hasattr(app, 'notebook'):
              app.notebook.bind("<<NotebookTabChanged>>", lambda e: render_checkboxes(app))
      
      # Force UI update trước khi vẽ checkbox
      app.root.after(200, add_tab_callbacks)
      app.root.after(100, render_checkboxes, app)

    # Khởi tạo checkbox từ đầu
    app.root.after(300, initialize_checkboxes)

def switch_tab(app, tab_code):
    """
    Chuyển đổi giữa các tab nội dung
    
    Args:
        app: Đối tượng TelegramUploaderApp
        tab_code: Mã tab cần chuyển đến
    """
    # Cập nhật trạng thái nút - Cải thiện nổi bật
    for code, btn in app.sub_tab_buttons.items():
        if code == tab_code:
            # Active tab styling
            btn.config(
                bg="#2E86C1",  # Blue color for active tab
                fg="white",
                relief="flat",
                font=("Arial", 11, "bold"),
                bd=1
            )
            # Remove hover bindings
            btn.unbind("<Enter>")
            btn.unbind("<Leave>")
        else:
            # Inactive tab styling
            btn.config(
                bg="#F0F0F0", 
                fg="#2C3E50",  # Dark blue text
                relief="flat",
                font=("Arial", 11),
                bd=0
            )
            # Add hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#E0E0E0"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#F0F0F0"))
    
    # Lưu tab hiện tại
    app.current_tab = tab_code
    
    # Xóa nội dung hiện tại
    for widget in app.tab_content_frame.winfo_children():
        widget.destroy()
    
    # Hiển thị nội dung tab mới
    if tab_code == "manual":
        create_manual_tab(app, app.tab_content_frame)
    elif tab_code == "auto":
        from .auto_tab import create_auto_tab
        create_auto_tab(app, app.tab_content_frame)
    elif tab_code == "duplicate":
        from .duplicate_tab import create_duplicate_tab
        create_duplicate_tab(app, app.tab_content_frame)
    elif tab_code == "uploaded":
        from .uploaded_tab import create_uploaded_tab
        create_uploaded_tab(app, app.tab_content_frame)

def render_checkboxes(app):
    """Vẽ lại tất cả checkbox trên treeview - LUÔN hiển thị chúng"""
    # Import CustomCheckbox từ components
    try:
        from ui.components.checkbox import create_checkbox_cell
    except ImportError:
        try:
            from .components.checkbox import create_checkbox_cell
        except ImportError:
            from src.ui.components.checkbox import create_checkbox_cell
    
    # Xóa tất cả checkbox hiện tại
    if hasattr(app, 'checkbox_widgets'):
        for checkbox in app.checkbox_widgets:
            try:
                checkbox.destroy()
            except:
                pass
    
    app.checkbox_widgets = []
    
    # LUÔN tạo checkbox cho tất cả hàng
    for item_id in app.video_tree.get_children():
        if item_id not in app.video_checkboxes:
            # Lấy thông tin video để quyết định có nên chọn mặc định không
            video_values = app.video_tree.item(item_id, "values")
            tags = app.video_tree.item(item_id, "tags")
            status = video_values[2] if len(video_values) > 2 else ""
            
            # Mặc định chọn những video không phải đã tải lên hoặc trùng lặp
            should_check = not (status == "Đã tải lên" or status == "Trùng lặp" or "uploaded" in tags or "duplicate" in tags)
            app.video_checkboxes[item_id] = tk.BooleanVar(value=should_check)
        
        checkbox = create_checkbox_cell(app.video_tree, item_id, "#1")
        if checkbox:
            # Đặt trạng thái của checkbox
            checkbox.set(app.video_checkboxes[item_id].get())
            app.checkbox_widgets.append(checkbox)
    
    # Cập nhật UI để đảm bảo checkbox hiển thị
    app.root.after(50, app.root.update_idletasks)
    """Vẽ lại tất cả checkbox trên treeview - LUÔN hiển thị chúng"""
    # Import CustomCheckbox từ components
    try:
        from ui.components.checkbox import create_checkbox_cell
    except ImportError:
        try:
            from .components.checkbox import create_checkbox_cell
        except ImportError:
            from src.ui.components.checkbox import create_checkbox_cell
    
    # Xóa tất cả checkbox hiện tại
    if hasattr(app, 'checkbox_widgets'):
        for checkbox in app.checkbox_widgets:
            checkbox.destroy()
    
    app.checkbox_widgets = []
    
    # Tạo checkbox cho tất cả hàng - LUÔN tạo checkbox cho mỗi hàng
    for item_id in app.video_tree.get_children():
        if item_id not in app.video_checkboxes:
            # Lấy thông tin video để quyết định có nên chọn mặc định không
            video_values = app.video_tree.item(item_id, "values")
            tags = app.video_tree.item(item_id, "tags")
            status = video_values[2] if len(video_values) > 2 else ""
            
            # Mặc định chọn những video không phải đã tải lên hoặc trùng lặp
            should_check = not (status == "Đã tải lên" or status == "Trùng lặp" or "uploaded" in tags or "duplicate" in tags)
            app.video_checkboxes[item_id] = tk.BooleanVar(value=should_check)
        
        checkbox = create_checkbox_cell(app.video_tree, item_id, "#1")
        if checkbox:
            checkbox.set(app.video_checkboxes[item_id].get())
            app.checkbox_widgets.append(checkbox)