"""
Logic for the Upload button with duplicate/already uploaded check
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
import datetime
import logging
import time
from ui.main_tab.main_tab_func import refresh_video_list
from ui.components.progress_animation import (
    create_animation_for_progress_bar,
    ICON_PENDING, ICON_PROCESSING, ICON_SUCCESS, ICON_ERROR
)

logger = logging.getLogger("UploadButtonLogic")

def check_duplicates_and_uploaded(app):
    """
    Kiểm tra xem có video trùng lặp hoặc đã tải lên trong những video được chọn không
    
    Args:
        app: Đối tượng TelegramUploaderApp
        
    Returns:
        tuple: (has_duplicates, has_uploaded, duplicate_videos, uploaded_videos)
    """
    try:
        has_duplicates = False
        has_uploaded = False
        duplicate_videos = []
        uploaded_videos = []
        
        # Lấy danh sách video đã chọn
        selected_videos = []
        
        # Get all valid items
        valid_items = [item for item in app.video_tree.get_children()]
        
        for item_id in list(app.video_checkboxes.keys()):
            if item_id not in valid_items:
                continue
                
            try:
                if app.video_checkboxes[item_id].get():  # Nếu checkbox được chọn
                    # Lấy tên video
                    video_values = app.video_tree.item(item_id, "values")
                    if len(video_values) >= 2:
                        video_name = video_values[1]
                        video_path = app.videos.get(video_name)
                        
                        if video_path and os.path.exists(video_path):
                            selected_videos.append((video_name, video_path, item_id))
            except Exception as e:
                logger.error(f"Lỗi khi lấy thông tin video: {str(e)}")
                continue
        
        # Kiểm tra từng video đã chọn
        for video_name, video_path, item_id in selected_videos:
            try:
                # Kiểm tra trạng thái và nhãn của video trong tree
                video_values = app.video_tree.item(item_id, "values")
                tags = app.video_tree.item(item_id, "tags")
                status = video_values[2] if len(video_values) > 2 else ""
                
                # Kiểm tra video trùng lặp
                if "duplicate" in tags or status == "Trùng lặp":
                    has_duplicates = True
                    if video_name not in duplicate_videos:
                        duplicate_videos.append(video_name)
                
                # Kiểm tra video đã tải lên
                if "uploaded" in tags or status == "Đã tải lên":
                    has_uploaded = True
                    if video_name not in uploaded_videos:
                        uploaded_videos.append(video_name)
            except Exception as e:
                logger.error(f"Error checking video status for {video_name}: {str(e)}")
        
        # Kiểm tra trực tiếp với lịch sử tải lên nếu chưa phát hiện qua UI
        if not has_uploaded:
            for video_name, video_path, _ in selected_videos:
                try:
                    video_hash = app.video_analyzer.calculate_video_hash(video_path)
                    if video_hash and app.upload_history.is_uploaded(video_hash):
                        has_uploaded = True
                        if video_name not in uploaded_videos:
                            uploaded_videos.append(video_name)
                except Exception as e:
                    logger.error(f"Error checking upload history for {video_name}: {str(e)}")
        
        return has_duplicates, has_uploaded, duplicate_videos, uploaded_videos
        
    except Exception as e:
        logger.error(f"Error in check_duplicates_and_uploaded: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Return safe default values
        return False, False, [], []

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
    try:
        # Kiểm tra cấu hình Telegram
        bot_token = app.config['TELEGRAM']['bot_token']
        chat_id = app.config['TELEGRAM']['chat_id']
        
        if not bot_token or not chat_id:
            messagebox.showerror("Lỗi", "Vui lòng cấu hình Bot Token và Chat ID trong tab Cài đặt!")
            app.switch_tab(1)  # Chuyển đến tab Cài đặt (index 1)
            return
        
        # Kết nối lại với Telegram nếu cần
        if not app.telegram_api.connected:
            if not app.telegram_api.connect(bot_token):
                messagebox.showerror("Lỗi", "Không thể kết nối với Telegram API. Vui lòng kiểm tra Bot Token và kết nối internet!")
                return
        
        # Kiểm tra xem có video nào được chọn không
        selected_videos = []
        
        # Get all valid tree items
        valid_items = [item for item in app.video_tree.get_children()]
        
        # Debug log for checkboxes state
        for item_id in valid_items:
            if item_id in app.video_checkboxes:
                state = app.video_checkboxes[item_id].get()
                logger.info(f"Checkbox state for {item_id}: {state}")
                
                # Also check the widget's state directly if available
                for checkbox in app.checkbox_widgets:
                    if hasattr(checkbox, 'item_id') and checkbox.item_id == item_id:
                        widget_state = checkbox.get()
                        logger.info(f"Widget state for {item_id}: {widget_state}")
                        # Update BooleanVar to match widget state
                        app.video_checkboxes[item_id].set(widget_state)
                        break
        
        # Use the widget state first, then fall back to stored variables
        for checkbox in app.checkbox_widgets:
            if hasattr(checkbox, 'item_id') and checkbox.item_id in valid_items:
                if checkbox.get():  # Check widget directly
                    item_id = checkbox.item_id
                    try:
                        # Update variable to match widget
                        app.video_checkboxes[item_id].set(True)
                        
                        # Get video info
                        values = app.video_tree.item(item_id, "values")
                        if len(values) >= 2:
                            video_name = values[1]  # Index 1 is the filename column
                            video_path = app.videos.get(video_name)
                            
                            if video_path and os.path.exists(video_path):
                                selected_videos.append((video_name, video_path))
                                logger.info(f"Selected video from widget: {video_name}")
                    except Exception as e:
                        logger.error(f"Error processing selection for {item_id}: {str(e)}")
        
        # Fall back to checking BooleanVars if no videos were found
        if not selected_videos:
            for item_id in valid_items:
                if item_id in app.video_checkboxes and app.video_checkboxes[item_id].get():
                    try:
                        values = app.video_tree.item(item_id, "values")
                        if len(values) >= 2:
                            video_name = values[1]
                            video_path = app.videos.get(video_name)
                            
                            if video_path and os.path.exists(video_path):
                                selected_videos.append((video_name, video_path))
                                logger.info(f"Selected video from var: {video_name}")
                    except Exception as e:
                        logger.error(f"Error processing fallback selection for {item_id}: {str(e)}")
        
        # Log the final count of selected videos
        logger.info(f"Total selected videos: {len(selected_videos)}")
        
        if not selected_videos:
            # Show selection dialog when no videos are selected
            messagebox.showinfo("Thông báo", "Vui lòng chọn ít nhất một video để tải lên!")
            # Attempt to reload checkboxes to ensure they're visible
            app.render_checkboxes()
            return
        
        # Changed logic for duplicate/uploaded checks:
        # 1. If only one video is selected, just check if it's already uploaded
        # 2. If multiple videos are selected, check both duplicates and already uploaded
        
        if len(selected_videos) == 1:
            # Only one video selected - check if it's already uploaded
            video_name, video_path = selected_videos[0]
            video_hash = app.video_analyzer.calculate_video_hash(video_path)
            
            if video_hash and app.upload_history.is_uploaded(video_hash):
                # Video already uploaded - confirm re-upload
                if not messagebox.askyesno(
                    "Xác nhận tải lên lại", 
                    f"Video này đã được tải lên trước đây. Bạn có muốn tải lên lại không?"
                ):
                    return
            
            # For single video, no need to check for duplicates
            # Just proceed with upload
            videos_to_upload = selected_videos
            
        else:
            # Multiple videos - check for duplicates and already uploaded
            has_duplicates = False
            has_uploaded = False
            duplicate_videos = []
            uploaded_videos = []
            
            # Check each selected video
            for video_name, video_path in selected_videos:
                try:
                    # Check status and tags in the tree
                    for item_id in valid_items:
                        values = app.video_tree.item(item_id, "values")
                        if len(values) >= 2 and values[1] == video_name:
                            tags = app.video_tree.item(item_id, "tags")
                            status = values[2] if len(values) > 2 else ""
                            
                            if "duplicate" in tags or status == "Trùng lặp":
                                has_duplicates = True
                                if video_name not in duplicate_videos:
                                    duplicate_videos.append(video_name)
                            
                            if "uploaded" in tags or status == "Đã tải lên":
                                has_uploaded = True
                                if video_name not in uploaded_videos:
                                    uploaded_videos.append(video_name)
                            
                            break
                    
                    # Double-check directly with upload history
                    if not has_uploaded:
                        video_hash = app.video_analyzer.calculate_video_hash(video_path)
                        if video_hash and app.upload_history.is_uploaded(video_hash):
                            has_uploaded = True
                            if video_name not in uploaded_videos:
                                uploaded_videos.append(video_name)
                                
                except Exception as e:
                    logger.error(f"Error checking video status for {video_name}: {str(e)}")
            
            # If there are duplicates or already uploaded videos, confirm with user
            skip_duplicates_uploaded = False
            if has_duplicates or has_uploaded:
                skip_duplicates_uploaded = show_upload_confirmation(
                    app, has_duplicates, has_uploaded, duplicate_videos, uploaded_videos
                )
            
            # Filter videos based on user confirmation
            if skip_duplicates_uploaded:
                videos_to_upload = [
                    (video_name, video_path) 
                    for video_name, video_path in selected_videos
                    if video_name not in duplicate_videos and video_name not in uploaded_videos
                ]
            else:
                videos_to_upload = selected_videos
            
            # Check if any videos remain to be uploaded
            if not videos_to_upload:
                messagebox.showinfo("Thông báo", "Không có video nào được tải lên sau khi lọc!")
                return
        
        # Hiển thị modal tiến trình tải lên
        show_upload_progress_modal(app, videos_to_upload)
        
    except Exception as e:
        # Catch all exceptions to prevent the app from crashing
        logger.error(f"Error in start_upload: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        messagebox.showerror("Lỗi không mong muốn", 
                           f"Đã xảy ra lỗi khi bắt đầu tải lên: {str(e)}\n\nỨng dụng vẫn hoạt động bình thường.")

def select_unuploaded_videos(app):
    """Chọn tất cả các video chưa tải lên trong trang hiện tại"""
    # Get current page items
    items = app.video_tree.get_children()
    
    # Check each item on the current page
    for item_id in items:
        # Get status and tags
        values = app.video_tree.item(item_id, "values")
        tags = app.video_tree.item(item_id, "tags")
        status = values[2] if len(values) > 2 else ""
        
        # Select if not uploaded (no "uploaded" tag and not "Đã tải lên" status)
        is_uploaded = ("uploaded" in tags or status == "Đã tải lên")
        
        # Set checkbox state based on upload status
        if item_id in app.video_checkboxes:
            app.video_checkboxes[item_id].set(not is_uploaded)
    
    # Render checkboxes to update UI
    app.render_checkboxes()

def show_upload_progress_modal(app, videos_to_upload):
    """
    Hiển thị modal hiển thị tiến trình tải lên (phiên bản cải tiến)
    
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
    window_width = 600  # Rộng hơn để hiển thị đủ nội dung
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
    
    total_progress_var = tk.DoubleVar(value=0)
    total_progress = ttk.Progressbar(
        total_progress_frame, 
        orient=tk.HORIZONTAL, 
        length=500, 
        mode='determinate',
        variable=total_progress_var
    )
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
    progress_vars = []  # Thêm để lưu trữ biến DoubleVar
    progress_animations = []  # Đối tượng quản lý animation
    
    # Các biểu tượng trạng thái
    icon_pending = ICON_PENDING
    icon_processing = ICON_PROCESSING
    icon_success = ICON_SUCCESS
    icon_error = ICON_ERROR
    
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
        
        # Progress bar với biến theo dõi
        progress_var = tk.DoubleVar(value=0)
        progress_vars.append(progress_var)
        
        # Progress bar
        progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=450, mode='determinate',
                                     variable=progress_var)
        progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        progress_bars.append(progress_bar)
        
        # Label phần trăm
        progress_percent = tk.Label(progress_frame, text="0%", width=5)
        progress_percent.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Label hiển thị trạng thái
        progress_label = tk.Label(info_frame, text="Đang chờ...", anchor=tk.W, justify=tk.LEFT, font=("Arial", 8))
        progress_label.pack(anchor=tk.W, fill=tk.X)
        progress_labels.append(progress_label)
        
        # Tạo đối tượng animation manager
        animation = create_animation_for_progress_bar(
            parent=modal, 
            progress_var=progress_var, 
            status_label=progress_label,
            percent_label=progress_percent
        )
        progress_animations.append(animation)
    
    # Frame cho nút - Đảm bảo nút đủ lớn để hiển thị text đầy đủ
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(10, 0))
    
    # Container cho nút với kích thước cố định
    button_container = tk.Frame(button_frame, height=40, width=150)  # Lớn hơn nhiều để đảm bảo đủ chỗ
    button_container.pack_propagate(False)  # Giữ kích thước
    button_container.pack(side=tk.RIGHT)
    
    # Nút hủy/đóng
    cancel_btn = tk.Button(button_container, text="Hủy tải lên", font=("Arial", 11))
    cancel_btn.pack(fill=tk.BOTH, expand=True)
    
    # Biến theo dõi đã hủy chưa
    is_cancelled = [False]
    upload_completed = [False]
    
    # Thiết lập callback cho nút hủy
    def cancel_upload():
        if upload_completed[0]:
            # Hủy tất cả animation trước khi đóng
            for animation in progress_animations:
                animation.cleanup()
            
            modal.destroy()
        else:
            is_cancelled[0] = True
            cancel_btn.config(text="Đang hủy...", state=tk.DISABLED)
            
            # Dừng tất cả animation
            for animation in progress_animations:
                animation.cancel()
    
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
            self.current_video_index = -1
            
        def start_new_video(self, index):
            """Bắt đầu tải lên video mới với index cụ thể"""
            try:
                if not self.is_valid or not self.modal.winfo_exists():
                    self.is_valid = False
                    return
                
                # Lưu index video hiện tại
                self.current_video_index = index
                
                if 0 <= index < len(icon_labels):
                    # Cập nhật icon
                    icon_labels[index].config(text=icon_processing)
                    
                    # Bắt đầu animation
                    progress_animations[index].start_animation(0, "Đang tải lên... ")
                    
                # Cập nhật UI
                self.modal.update_idletasks()
            except Exception as e:
                logger.error(f"Error in start_new_video: {str(e)}")
                
        def update_ui(self, index, status, progress_value=None, text=None):
            """Cập nhật UI cho một video cụ thể"""
            # Check if modal still exists
            if not self.is_valid or not self.modal.winfo_exists():
                self.is_valid = False
                return
                
            try:
                # Nếu là kết thúc thành công, đặt progress = 100%
                if status == "success" and 0 <= index < len(progress_animations):
                    # Đánh dấu hoàn thành đối tượng animation
                    progress_animations[index].set_completed(True, "Tải lên thành công")
                    
                    # Cập nhật icon
                    icon_labels[index].config(text=icon_success)
                    self.successful_uploads += 1
                
                # Nếu là kết thúc lỗi
                elif status == "error" and 0 <= index < len(progress_animations):
                    # Đánh dấu lỗi đối tượng animation
                    error_text = text or "Tải lên thất bại"
                    progress_animations[index].set_completed(False, error_text)
                    
                    # Cập nhật icon
                    icon_labels[index].config(text=icon_error)
                    self.failed_uploads += 1
                    
                # Cập nhật tổng thể
                completed = self.successful_uploads + self.failed_uploads
                progress_percent = (completed / self.total_videos) * 100
                total_progress_var.set(progress_percent)
                percent_var.set(f"{int(progress_percent)}%")
                total_info_var.set(f"{completed}/{self.total_videos} video hoàn thành " +
                              f"({self.successful_uploads} thành công, {self.failed_uploads} thất bại)")
                
                # Cập nhật UI
                self.modal.update_idletasks()
                
                # Nếu tất cả đã hoàn thành, đổi nút thành "Đóng"
                if completed == self.total_videos:
                    upload_completed[0] = True
                    cancel_btn.config(text="Đóng cửa sổ", state=tk.NORMAL, command=self.modal.destroy)
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
    Luồng thực hiện việc tải lên video (phiên bản cải tiến)
    
    Args:
        app: Đối tượng TelegramUploaderApp
        videos_to_upload: Danh sách (video_name, video_path) cần tải lên
        tracker: Đối tượng theo dõi và hiển thị tiến trình
        is_cancelled: List có phần tử đánh dấu hủy tải lên [bool]
    """
    # Lấy thông tin Telegram
    bot_token = app.config['TELEGRAM']['bot_token']
    chat_id = app.config['TELEGRAM']['chat_id']
    
    # Thiết lập thời gian chờ giữa các video
    upload_delay = int(app.config['SETTINGS'].get('delay_between_uploads', '5'))
    rate_limit_delay = max(8, upload_delay)  # Tối thiểu 8 giây
    
    # Kết nối lại với Telegram API nếu cần
    if not app.telegram_api.connected:
        if not app.telegram_api.connect(bot_token):
            # Không thể kết nối với Telegram API
            for i in range(len(videos_to_upload)):
                tracker.update_ui(i, "error", 0, "Không thể kết nối với Telegram API!")
            return
    
    # Kiểm tra cấu hình Telethon
    use_telethon = app.config.getboolean('TELETHON', 'use_telethon', fallback=False)
    
    # Tải lên từng video
    for i, (video_name, video_path) in enumerate(videos_to_upload):
        # Kiểm tra nếu đã hủy tải lên
        if is_cancelled[0]:
            tracker.update_ui(i, "error", 0, "Đã hủy tải lên")
            continue
        
        # Báo hiệu bắt đầu tải video mới
        tracker.start_new_video(i)
        
        # Kiểm tra video có tồn tại không
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            tracker.update_ui(i, "error", 0, "File không tồn tại")
            continue
            
        # Tính kích thước video
        video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        
        # Chuẩn bị caption
        caption = f"📹 {video_name}\n📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # THÊM MỚI: Retry logic
        max_retries = 5
        retry_count = 0
        upload_success = False
        
        while retry_count < max_retries and not upload_success and not is_cancelled[0]:
            if retry_count > 0:
                # Nếu là lần retry, hiển thị thông báo và đợi
                tracker.update_ui(i, "processing", 0, f"Đang thử lại... (lần {retry_count}/{max_retries})")
                
                # Chờ trước khi thử lại (tăng dần thời gian chờ)
                retry_delay = rate_limit_delay * (1 + retry_count * 0.5)
                time.sleep(retry_delay)
            
            try:
                # Sử dụng phương thức tải lên phù hợp dựa trên kích thước và cấu hình
                if use_telethon and video_size_mb > 50:
                    # Sử dụng Telethon cho video lớn
                    success = app.telegram_api.send_video_with_telethon(
                        chat_id, 
                        video_path,
                        caption=caption
                    )
                else:
                    # Sử dụng Bot API
                    success = app.telegram_api.send_video(
                        chat_id, 
                        video_path,
                        caption=caption
                    )
                
                if success:
                    # Tải lên thành công
                    upload_success = True
                    
                    # Thêm vào lịch sử
                    video_hash = app.video_analyzer.calculate_video_hash(video_path)
                    if video_hash:
                        file_size = os.path.getsize(video_path)
                        # Lưu thời gian tải lên
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        app.upload_history.add_upload(video_hash, video_name, video_path, file_size, upload_date=now)
                    
                    # Cập nhật UI
                    tracker.update_ui(i, "success")
                    
                    # Cập nhật trạng thái video trong tree nếu có
                    app.root.after(0, lambda name=video_name: update_video_status(app, name))
                else:
                    # Tải lên thất bại
                    retry_count += 1
                    if retry_count >= max_retries:
                        tracker.update_ui(i, "error", 0, "Tất cả các lần thử đều thất bại")
            except Exception as e:
                # Xử lý lỗi
                retry_count += 1
                if retry_count >= max_retries:
                    tracker.update_ui(i, "error", 0, f"Lỗi: {str(e)[:50]}")
                    logger.error(f"Lỗi khi tải lên video {video_name}: {str(e)}")
        
        # Đợi giữa các video (nếu không phải video cuối cùng)
        if i < len(videos_to_upload) - 1 and not is_cancelled[0] and upload_success:
            time.sleep(rate_limit_delay)
    
    # Làm mới danh sách video sau khi tải lên
    app.root.after(500, lambda: refresh_video_list(app))


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
                    
                    # Cập nhật trạng thái checkbox nếu có
                    if item_id in app.video_checkboxes:
                        app.video_checkboxes[item_id].set(False)
                    break
            except Exception:
                continue
                
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật trạng thái video: {str(e)}")