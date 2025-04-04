"""
Logic for the Upload button with duplicate/already uploaded check
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
import datetime
import logging

logger = logging.getLogger("UploadButtonLogic")

def check_duplicates_and_uploaded(app):
    """
    Kiểm tra xem có video trùng lặp hoặc đã tải lên trong những video được chọn không
    
    Args:
        app: Đối tượng TelegramUploaderApp
        
    Returns:
        tuple: (has_duplicates, has_uploaded, duplicate_videos, uploaded_videos)
    """
    has_duplicates = False
    has_uploaded = False
    duplicate_videos = []
    uploaded_videos = []
    
    # Lấy danh sách video đã chọn
    selected_videos = []
    
    for item_id, var in app.video_checkboxes.items():
        if var.get():  # Nếu checkbox được chọn
            # Lấy tên video
            try:
                video_name = app.video_tree.item(item_id, "values")[1]
                video_path = app.videos.get(video_name)
                
                if video_path and os.path.exists(video_path):
                    selected_videos.append((video_name, video_path))
            except Exception as e:
                logger.error(f"Lỗi khi lấy thông tin video: {str(e)}")
                continue
    
    # Kiểm tra từng video đã chọn
    for video_name, video_path in selected_videos:
        # Kiểm tra trạng thái và nhãn của video trong tree
        for item in app.video_items:
            if item["name"] == video_name:
                # Kiểm tra video trùng lặp
                if "duplicate" in item["tags"] or item["status"] == "Trùng lặp":
                    has_duplicates = True
                    if video_name not in duplicate_videos:
                        duplicate_videos.append(video_name)
                
                # Kiểm tra video đã tải lên
                if "uploaded" in item["tags"] or item["status"] == "Đã tải lên":
                    has_uploaded = True
                    if video_name not in uploaded_videos:
                        uploaded_videos.append(video_name)
                
                break
        
        # Kiểm tra trực tiếp với lịch sử tải lên
        if not has_uploaded:
            video_hash = app.video_analyzer.calculate_video_hash(video_path)
            if video_hash and app.upload_history.is_uploaded(video_hash):
                has_uploaded = True
                if video_name not in uploaded_videos:
                    uploaded_videos.append(video_name)
    
    return has_duplicates, has_uploaded, duplicate_videos, uploaded_videos

def show_upload_confirmation(app, has_duplicates, has_uploaded, duplicate_videos, uploaded_videos):
    """
    Hiển thị modal xác nhận tải lên khi có video trùng lặp hoặc đã tải lên
    
    Args:
        app: Đối tượng TelegramUploaderApp
        has_duplicates: Có video trùng lặp
        has_uploaded: Có video đã tải lên
        duplicate_videos: Danh sách tên video trùng lặp
        uploaded_videos: Danh sách tên video đã tải lên
        
    Returns:
        bool: True nếu người dùng đồng ý, False nếu không đồng ý
    """
    # Tạo thông báo
    message = "Lưu ý:\n\n"
    
    if has_duplicates:
        message += f"- Có {len(duplicate_videos)} video trùng lặp đã được chọn:\n"
        for name in duplicate_videos[:3]:
            message += f"  • {name}\n"
        if len(duplicate_videos) > 3:
            message += f"  • và {len(duplicate_videos) - 3} video khác\n"
    
    if has_uploaded:
        message += f"\n- Có {len(uploaded_videos)} video đã tải lên trước đây:\n"
        for name in uploaded_videos[:3]:
            message += f"  • {name}\n"
        if len(uploaded_videos) > 3:
            message += f"  • và {len(uploaded_videos) - 3} video khác\n"
    
    message += "\nBạn có đồng ý bỏ các video trùng và đã tải lên trước đây không?"
    
    # Hiển thị hộp thoại
    result = messagebox.askquestion("Xác nhận tải lên", message, icon='warning')
    
    # Trả về kết quả (True nếu đồng ý, False nếu không đồng ý)
    return result == "yes"

def start_upload(app):
    """
    Bắt đầu quá trình tải lên với kiểm tra video trùng lặp và đã tải lên
    
    Args:
        app: Đối tượng TelegramUploaderApp
    """
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
    
    # Kiểm tra xem có video nào được chọn không
    selected_videos = []
    
    for item_id, var in app.video_checkboxes.items():
        if var.get():  # Nếu checkbox được chọn
            # Lấy tên video
            try:
                video_name = app.video_tree.item(item_id, "values")[1]
                video_path = app.videos.get(video_name)
                
                if video_path and os.path.exists(video_path):
                    selected_videos.append((video_name, video_path))
            except Exception as e:
                logger.error(f"Lỗi khi lấy thông tin video: {str(e)}")
                continue
    
    if not selected_videos:
        messagebox.showinfo("Thông báo", "Vui lòng chọn ít nhất một video để tải lên!")
        return
    
    # Kiểm tra video trùng lặp hoặc đã tải lên
    has_duplicates, has_uploaded, duplicate_videos, uploaded_videos = check_duplicates_and_uploaded(app)
    
    # LUÔN hiển thị modal xác nhận nếu có video trùng lặp hoặc đã tải lên
    skip_duplicates_uploaded = False
    
    if has_duplicates or has_uploaded:
        skip_duplicates_uploaded = show_upload_confirmation(app, has_duplicates, has_uploaded, duplicate_videos, uploaded_videos)
    
    # Lọc danh sách video sẽ tải lên dựa vào kết quả xác nhận
    videos_to_upload = []
    
    for video_name, video_path in selected_videos:
        should_skip = False
        
        # Nếu người dùng chọn bỏ qua video trùng lặp và đã tải lên
        if skip_duplicates_uploaded:
            if video_name in duplicate_videos or video_name in uploaded_videos:
                should_skip = True
        
        if not should_skip:
            videos_to_upload.append((video_name, video_path))
    
    # Kiểm tra nếu không còn video nào sau khi lọc
    if not videos_to_upload:
        messagebox.showinfo("Thông báo", "Không có video nào được tải lên sau khi lọc!")
        return
    
    # Hiển thị modal tiến trình tải lên thay vì dùng progressbar
    show_upload_progress_modal(app, videos_to_upload)

def show_upload_progress_modal(app, videos_to_upload):
    """
    Hiển thị modal hiển thị tiến trình tải lên
    
    Args:
        app: Đối tượng TelegramUploaderApp
        videos_to_upload: Danh sách (video_name, video_path) cần tải lên
    """
    # Tạo modal window
    modal = tk.Toplevel(app.root)
    modal.title("Tiến trình tải lên video lên Telegram")
    modal.transient(app.root)
    modal.grab_set()
    
    # Đặt kích thước và vị trí
    window_width = 500
    window_height = 450
    screen_width = modal.winfo_screenwidth()
    screen_height = modal.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    modal.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Ngăn chặn thay đổi kích thước
    modal.resizable(False, False)
    
    # Thiết lập protocol WM_DELETE_WINDOW - để người dùng không đóng modal khi đang tải lên
    def on_close():
        if upload_completed[0]:
            modal.destroy()
        else:
            if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn hủy quá trình tải lên không?"):
                is_cancelled[0] = True
                cancel_btn.config(text="Đang hủy...", state=tk.DISABLED)
    
    modal.protocol("WM_DELETE_WINDOW", on_close)
    
    # Tạo nội dung
    main_frame = tk.Frame(modal, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Label tiêu đề
    title_label = tk.Label(main_frame, text="Tiến trình tổng thể:", font=("Arial", 12, "bold"))
    title_label.pack(anchor=tk.W, pady=(0, 5))
    
    # Progress bar tổng thể
    total_progress_frame = tk.Frame(main_frame)
    total_progress_frame.pack(fill=tk.X, pady=(0, 10))
    
    total_progress = ttk.Progressbar(total_progress_frame, orient=tk.HORIZONTAL, length=460, mode='determinate')
    total_progress.pack(fill=tk.X, side=tk.LEFT, expand=True)
    
    # Label hiển thị phần trăm
    percent_var = tk.StringVar(value="0%")
    percent_label = tk.Label(total_progress_frame, textvariable=percent_var, width=5)
    percent_label.pack(side=tk.RIGHT, padx=(5, 0))
    
    # Label thông tin tổng thể
    total_info_var = tk.StringVar(value=f"0/{len(videos_to_upload)} video hoàn thành")
    total_info_label = tk.Label(main_frame, textvariable=total_info_var, font=("Arial", 10))
    total_info_label.pack(anchor=tk.W, pady=(0, 10))
    
    # Tạo frame cho danh sách video với border
    list_container = tk.Frame(main_frame, bd=1, relief=tk.SOLID)
    list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    # Canvas cho danh sách có thể cuộn
    canvas = tk.Canvas(list_container, highlightthickness=0)
    scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=canvas.yview)
    scroll_frame = tk.Frame(canvas)
    
    # Configure scrolling
    def configure_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    scroll_frame.bind("<Configure>", configure_scroll_region)
    canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor=tk.NW, width=window_width-60)
    
    def configure_canvas_window(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    canvas.bind("<Configure>", configure_canvas_window)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack scrolling elements
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Biến để theo dõi trạng thái và widgets
    video_labels = []
    icon_labels = []
    progress_bars = []
    progress_labels = []
    
    # Các biểu tượng trạng thái
    icon_pending = "⏳"
    icon_processing = "🔄"
    icon_success = "✅"
    icon_error = "❌"
    
    # Tạo widget cho từng video
    for i, (video_name, _) in enumerate(videos_to_upload):
        # Frame cho mỗi video
        video_frame = tk.Frame(scroll_frame, pady=5, padx=5)
        video_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Frame header với tên và icon
        header_frame = tk.Frame(video_frame)
        header_frame.pack(fill=tk.X)
        
        # Frame cho tên video
        name_frame = tk.Frame(header_frame)
        name_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Tên video với giới hạn độ dài và tooltip
        name_text = video_name
        if len(name_text) > 40:
            name_text = name_text[:37] + "..."
        
        # Biểu tượng trạng thái
        icon_label = tk.Label(header_frame, text=icon_pending, font=("Arial", 16), padx=5)
        icon_label.pack(side=tk.RIGHT)
        icon_labels.append(icon_label)
        
        # Tên video
        name_label = tk.Label(name_frame, text=name_text, anchor=tk.W, justify=tk.LEFT, font=("Arial", 9, "bold"))
        name_label.pack(anchor=tk.W, fill=tk.X)
        video_labels.append(name_label)
        
        # Tooltip cho tên đầy đủ
        def show_tooltip(event, text=video_name):
            tooltip = tk.Toplevel(modal)
            tooltip.overrideredirect(True)
            tooltip.geometry(f"+{event.x_root+10}+{event.y_root+10}")
            tk.Label(tooltip, text=text, bg="lightyellow", padx=5, pady=2).pack()
            
            def hide_tooltip(event=None, top=tooltip):
                top.destroy()
            
            name_label.bind("<Leave>", hide_tooltip)
            modal.after(3000, lambda top=tooltip: top.destroy() if top.winfo_exists() else None)
        
        if len(video_name) > 40:
            name_label.bind("<Enter>", show_tooltip)
        
        # Progress bar và frame thông tin
        info_frame = tk.Frame(video_frame)
        info_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Frame progress chứa cả progress bar và label phần trăm
        progress_frame = tk.Frame(info_frame)
        progress_frame.pack(fill=tk.X)
        
        # Progress bar
        progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        progress_bars.append(progress_bar)
        
        # Label phần trăm
        progress_percent = tk.Label(progress_frame, text="0%", width=5)
        progress_percent.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Label hiển thị trạng thái
        progress_label = tk.Label(info_frame, text="Đang chờ...", anchor=tk.W, justify=tk.LEFT, font=("Arial", 8))
        progress_label.pack(anchor=tk.W, fill=tk.X)
        progress_labels.append(progress_label)
        
        # Lưu label phần trăm
        progress_bar.percent_label = progress_percent
    
    # Frame cho các nút
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(10, 0))
    
    # Nút hủy/đóng
    cancel_btn = tk.Button(button_frame, text="Hủy", width=15, height=2)
    cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    # Biến theo dõi đã hủy chưa
    is_cancelled = [False]
    upload_completed = [False]
    
    # Thiết lập callback cho nút hủy
    def cancel_upload():
        if upload_completed[0]:
            modal.destroy()
        else:
            is_cancelled[0] = True
            cancel_btn.config(text="Đang hủy...", state=tk.DISABLED)
    
    cancel_btn.config(command=cancel_upload)
    
    # Cập nhật giao diện
    modal.update_idletasks()
    
    # Tạo đối tượng theo dõi tiến trình
    class UploadTracker:
        def __init__(self, modal, video_count):
            self.modal = modal
            self.is_valid = True
            self.total_videos = video_count
            self.successful_uploads = 0
            self.failed_uploads = 0
            
        def update_ui(self, index, status, progress_value=None, text=None):
            # Check if modal still exists
            if not self.is_valid or not self.modal.winfo_exists():
                self.is_valid = False
                return
                
            try:
                # Update video progress
                if progress_value is not None and index < len(progress_bars):
                    progress_bars[index]['value'] = progress_value
                    # Update percent label
                    percent_text = f"{int(progress_value)}%"
                    progress_bars[index].percent_label.config(text=percent_text)
                
                # Update text
                if text is not None and index < len(progress_labels):
                    progress_labels[index].config(text=text)
                
                # Update status icon
                if status == "pending" and index < len(icon_labels):
                    icon_labels[index].config(text=icon_pending)
                elif status == "processing" and index < len(icon_labels):
                    icon_labels[index].config(text=icon_processing)
                elif status == "success" and index < len(icon_labels):
                    icon_labels[index].config(text=icon_success)
                    self.successful_uploads += 1
                elif status == "error" and index < len(icon_labels):
                    icon_labels[index].config(text=icon_error)
                    self.failed_uploads += 1
                    
                # Update total progress
                completed = self.successful_uploads + self.failed_uploads
                progress_percent = (completed / self.total_videos) * 100
                total_progress['value'] = progress_percent
                percent_var.set(f"{int(progress_percent)}%")
                total_info_var.set(f"{completed}/{self.total_videos} video hoàn thành " +
                              f"({self.successful_uploads} thành công, {self.failed_uploads} thất bại)")
                
                # Update UI
                self.modal.update_idletasks()
                
                # If all uploads finished, change button to "Close"
                if completed == self.total_videos:
                    upload_completed[0] = True
                    cancel_btn.config(text="Đóng", state=tk.NORMAL, command=self.modal.destroy)
            except Exception as e:
                logger.error(f"Error updating UI: {str(e)}")
                self.is_valid = False
    
    # Tạo tracker
    tracker = UploadTracker(modal, len(videos_to_upload))
    
    # Bắt đầu tải lên trong một luồng mới
    upload_thread = threading.Thread(target=upload_videos_thread, 
                                  args=(app, videos_to_upload, tracker, is_cancelled))
    upload_thread.daemon = True
    upload_thread.start()

def upload_videos_thread(app, videos_to_upload, tracker, is_cancelled):
    """
    Luồng thực hiện việc tải lên video
    
    Args:
        app: Đối tượng TelegramUploaderApp
        videos_to_upload: Danh sách (video_name, video_path) cần tải lên
        tracker: Đối tượng theo dõi và hiển thị tiến trình
        is_cancelled: List có phần tử đánh dấu hủy tải lên [bool]
    """
    # Lấy thông tin Telegram
    bot_token = app.config['TELEGRAM']['bot_token']
    chat_id = app.config['TELEGRAM']['chat_id']
    
    # Kết nối lại với Telegram nếu cần
    if not app.telegram_api.connected:
        if not app.telegram_api.connect(bot_token):
            # Không thể kết nối với Telegram API
            for i in range(len(videos_to_upload)):
                tracker.update_ui(i, "error", 0, "Không thể kết nối với Telegram API!")
            return
    
    # Tải lên từng video
    for i, (video_name, video_path) in enumerate(videos_to_upload):
        # Kiểm tra nếu đã hủy tải lên
        if is_cancelled[0]:
            tracker.update_ui(i, "error", 0, "Đã hủy tải lên")
            continue
        
        # Cập nhật trạng thái
        tracker.update_ui(i, "processing", 0, "Đang chuẩn bị tải lên...")
        
        # Tải lên video
        try:
            def progress_callback(current, total):
                if is_cancelled[0]:
                    return False  # Báo hiệu hủy tải lên
                    
                percent = (current / total) * 100
                tracker.update_ui(i, "processing", percent, f"Đang tải lên... {current/1024/1024:.1f}/{total/1024/1024:.1f} MB ({percent:.1f}%)")
                return True  # Tiếp tục tải lên
            
            success = app.telegram_api.send_video(chat_id, video_path, progress_callback=progress_callback)
            
            if success:
                # Thêm vào lịch sử
                video_hash = app.video_analyzer.calculate_video_hash(video_path)
                if video_hash:
                    file_size = os.path.getsize(video_path)
                    # Lưu thời gian tải lên
                    now = datetime.datetime.now().isoformat()
                    app.upload_history.add_upload(video_hash, video_name, video_path, file_size, upload_time=now)
                    
                    # Cập nhật trạng thái
                    tracker.update_ui(i, "success", 100, "Tải lên thành công")
                    
                    # Cập nhật trạng thái trong treeview
                    if app.root.winfo_exists():
                        app.root.after(0, lambda name=video_name: update_video_status(app, name))
            else:
                # Tải lên thất bại
                tracker.update_ui(i, "error", 0, "Tải lên thất bại")
                
        except Exception as e:
            # Hiển thị thông báo lỗi
            error_msg = f"Lỗi: {str(e)[:50]}"
            tracker.update_ui(i, "error", 0, error_msg)
            logger.error(f"Lỗi khi tải lên video {video_name}: {str(e)}")
    
    # Cập nhật trạng thái kết thúc
    if tracker.is_valid:
        # Đổi nút Hủy thành Đóng
        successful = tracker.successful_uploads
        failed = tracker.failed_uploads
        
        if is_cancelled[0]:
            app.root.after(0, lambda: messagebox.showinfo("Tải lên đã hủy", 
                                            f"Đã hủy tải lên. Kết quả: {successful} thành công, {failed} thất bại"))
        else:
            app.root.after(0, lambda: messagebox.showinfo("Tải lên hoàn tất", 
                                            f"Đã tải lên: {successful} thành công, {failed} thất bại"))
        
        # Làm mới danh sách video sau khi tải lên
        from .main_tab_func import refresh_video_list
        app.root.after(100, lambda: refresh_video_list(app))

def update_video_status(app, video_name):
    """
    Cập nhật trạng thái video trong treeview sau khi tải lên
    
    Args:
        app: Đối tượng TelegramUploaderApp
        video_name: Tên video cần cập nhật
    """
    try:
        # Cập nhật trong danh sách video_items
        for i, item in enumerate(app.video_items):
            if item["name"] == video_name:
                app.video_items[i]["status"] = "Đã tải lên"
                app.video_items[i]["tags"] = ("uploaded",)
                break
        
        # Cập nhật trong treeview
        for item_id in app.video_tree.get_children():
            try:
                tree_video_name = app.video_tree.item(item_id, "values")[1]
                if tree_video_name == video_name:
                    app.video_tree.item(item_id, values=(" ", video_name, "Đã tải lên", ""), tags=("uploaded",))
                    break
            except Exception:
                continue
                
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật trạng thái video: {str(e)}")