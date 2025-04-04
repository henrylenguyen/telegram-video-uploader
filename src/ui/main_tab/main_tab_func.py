"""
Functionality module for the main tab
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import math
import logging
from PIL import Image, ImageTk
import cv2
import datetime
import threading

logger = logging.getLogger("MainTabFunc")

# ----- Checkbox and Selection Logic -----



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
    if hasattr(app, 'status_var'):
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
        if hasattr(app, 'status_var'):
            app.status_var.set("")
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
        if hasattr(app, 'status_var'):
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
        if hasattr(app, 'status_var'):
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
    if hasattr(app, 'status_var'):
        app.status_var.set("") # Bỏ "Đã tìm thấy ... video"
    
    # Cập nhật phân trang
    total_pages = max(1, math.ceil(len(app.video_items) / app.items_per_page))
    app.current_page = 1
    app.page_info_var.set(f"Trang 1/{total_pages}")
    
    # Cập nhật trạng thái nút phân trang
    app.prev_page_btn["state"] = tk.DISABLED
    app.next_page_btn["state"] = tk.NORMAL if total_pages > 1 else tk.DISABLED
    
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
        
        # Xác định trước nếu video này cần được chọn
        should_check = not (status == "Đã tải lên" or status == "Trùng lặp" or "uploaded" in tags or "duplicate" in tags)
        
        # Thêm vào treeview với ô checkbox (rỗng, sẽ được vẽ sau)
        item_id = app.video_tree.insert("", tk.END, values=(" ", video_name, status, info), tags=tags)
        
        # Tạo biến checkbox với trạng thái mặc định
        app.video_checkboxes[item_id] = tk.BooleanVar(value=should_check)
    
    # Đảm bảo UI được cập nhật
    app.root.update_idletasks()
    
    # Vẽ các checkbox mà không gọi set_default_selection
    try:
        from ui.components.checkbox import create_checkbox_cell
    except ImportError:
        try:
            from .components.checkbox import create_checkbox_cell
        except ImportError:
            from src.ui.components.checkbox import create_checkbox_cell
    
    # Xóa các checkbox hiện tại
    if hasattr(app, 'checkbox_widgets'):
        for checkbox in app.checkbox_widgets:
            checkbox.destroy()
    
    app.checkbox_widgets = []
    
    # Tạo mới các checkbox
    for item_id in app.video_tree.get_children():
        checkbox = create_checkbox_cell(app.video_tree, item_id, "#1")
        if checkbox:
            # Thiết lập trạng thái checkbox từ biến đã tạo ở trên
            checkbox.set(app.video_checkboxes[item_id].get())
            app.checkbox_widgets.append(checkbox)
            
def set_default_selection(app):
    """
    Thiết lập trạng thái mặc định cho các checkbox - chọn tất cả video
    ngoại trừ video đã tải lên và video trùng lặp
    """
    # Đảm bảo checkboxes đã được render
    app.render_checkboxes()
    
    # Chọn tất cả các video ngoại trừ video đã tải lên và video trùng lặp
    for item_id in app.video_tree.get_children():
        # Lấy thông tin video
        video_values = app.video_tree.item(item_id, "values")
        tags = app.video_tree.item(item_id, "tags")
        
        # Mặc định là chọn
        should_select = True
        
        # Nếu có thông tin trạng thái, kiểm tra
        if len(video_values) > 2:
            status = video_values[2]
            
            # Không chọn video đã tải lên và video trùng lặp
            if status == "Đã tải lên" or status == "Trùng lặp":
                should_select = False
        
        # Kiểm tra tags
        if "uploaded" in tags or "duplicate" in tags:
            should_select = False
        
        # Cập nhật trạng thái checkbox
        if item_id in app.video_checkboxes:
            app.video_checkboxes[item_id].set(should_select)
    
    # Render lại các checkbox
    app.render_checkboxes()

def update_table_content(app):
    """Cập nhật nội dung bảng theo trang hiện tại và đảm bảo checkboxes hiển thị"""
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
    
    # Đảm bảo UI được cập nhật trước khi vẽ checkboxes
    app.root.update_idletasks()

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
    app.render_checkboxes()  # LUÔN gọi render để đảm bảo checkbox vẫn hiển thị

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
    
    # Bật nút phát video
    app.play_video_btn.config(state=tk.NORMAL)
    
    # Kiểm tra trạng thái video để quyết định bật/tắt nút tải lên
    video_status = app.video_tree.item(selected_items[0], "values")[2]
    video_tags = app.video_tree.item(selected_items[0], "tags")
    
    # Tắt nút tải lên nếu video đã tải lên hoặc trùng lặp
    if video_status == "Đã tải lên" or video_status == "Trùng lặp" or "uploaded" in video_tags or "duplicate" in video_tags:
        app.upload_single_btn.config(state=tk.DISABLED)
    else:
        app.upload_single_btn.config(state=tk.NORMAL)
    
    # Hiển thị thông tin video
    display_video_info(app, video_path)
    
    # Hiển thị các frame từ video
    display_video_frames(app, video_path)

def reset_video_info(app):
    """Xóa thông tin video hiển thị"""
    for key, var in app.info_vars.items():
        var.set("")
    
    # Xóa trạng thái tải lên nếu có
    if hasattr(app, 'upload_status_label'):
        app.upload_status_label.config(text="")

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
    
    # Kiểm tra xem video có phải là trùng lặp hoặc đã tải lên không
    video_status = app.video_tree.item(selected_items[0], "values")[2]
    video_tags = app.video_tree.item(selected_items[0], "tags")
    
    if video_status == "Đã tải lên" or "uploaded" in video_tags:
        messagebox.showwarning("Cảnh báo", "Video này đã được tải lên trước đó!")
        return
    
    if video_status == "Trùng lặp" or "duplicate" in video_tags:
        if not messagebox.askyesno("Xác nhận", "Video này trùng lặp với video khác. Bạn có chắc chắn muốn tải lên không?"):
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
    
    # Tải lên video bằng modal progress
    from .upload_button_logic import show_upload_progress_modal
    show_upload_progress_modal(app, [(video_name, video_path)])

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
            logger.error(f"Không thể mở video: {video_path}")
            # Hiển thị thông báo trong các frame
            for i, label in enumerate(app.frame_labels):
                label.config(image="", text=f"Không thể mở video")
            return
        
        # Lấy thông tin video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        if total_frames <= 0 or duration <= 0:
            logger.error(f"Video không hợp lệ: {video_path}, frames={total_frames}, fps={fps}")
            for i, label in enumerate(app.frame_labels):
                label.config(image="", text=f"Video không hợp lệ")
            return
        
        # Chọn 5 vị trí frame để hiển thị
        positions = [0.1, 0.3, 0.5, 0.7, 0.9]  # 10%, 30%, 50%, 70%, 90%
        frames = []
        
        # Tính toán kích thước frame để hiển thị
        frame_width = 170  # Kích thước cố định
        frame_height = 120
        
        # Lưu các frame thành công
        successful_frames = 0
        
        # Xử lý từng vị trí
        for i, pos in enumerate(positions):
            if i >= len(app.frame_labels):
                break
                
            # Tính vị trí frame theo thời gian
            frame_position = int(total_frames * pos) 
            if frame_position >= total_frames:
                frame_position = total_frames - 1
            
            # Seek đến vị trí và đọc frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)
            success, frame = cap.read()
            
            if success:
                # Chuyển frame sang định dạng PIL
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Resize theo kích thước đã định
                try:
                    pil_image = pil_image.resize((frame_width, frame_height), Image.LANCZOS)
                except Exception:
                    pil_image = pil_image.resize((frame_width, frame_height), Image.BICUBIC)
                
                # Chuyển sang định dạng Tkinter
                tk_image = ImageTk.PhotoImage(pil_image)
                frames.append(tk_image)  # Lưu reference để tránh bị thu hồi bởi garbage collector
                
                # Hiển thị lên label
                app.frame_labels[i].config(image=tk_image, text="")
                successful_frames += 1
            else:
                app.frame_labels[i].config(image="", text=f"Không thể đọc frame tại {pos*100:.0f}%")
                
        # Giải phóng tài nguyên
        cap.release()
        
        # Lưu các frame để tránh bị thu hồi bởi garbage collector
        app.current_frames = frames
        
        if successful_frames == 0:
            logger.warning(f"Không thể đọc frame nào từ video: {video_path}")
    
    except Exception as e:
        logger.error(f"Lỗi hiển thị frame: {str(e)}")
        # Hiển thị thông báo lỗi trong các frame
        for i, label in enumerate(app.frame_labels):
            label.config(image="", text=f"Lỗi: {str(e)[:30]}")

def display_video_info(app, video_path):
    """
    Hiển thị thông tin chi tiết của video với trạng thái tải lên
    
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
    
    # Kiểm tra trạng thái tải lên và trùng lặp
    video_hash = app.video_analyzer.calculate_video_hash(video_path)
    upload_info = None
    is_duplicate = False
    
    # Kiểm tra đã tải lên
    if hasattr(app.upload_history, 'get_upload_by_hash'):
        upload_info = app.upload_history.get_upload_by_hash(video_hash) if video_hash else None
    else:
        # Fallback to manual search if method doesn't exist
        uploads = app.upload_history.get_all_uploads()
        if video_hash and video_hash in uploads:
            upload_info = uploads[video_hash]
    
    # Kiểm tra trùng lặp
    video_name = os.path.basename(video_path)
    for item in app.video_items:
        if item["name"] == video_name and ("duplicate" in item["tags"] or item["status"] == "Trùng lặp"):
            is_duplicate = True
            break
    
    # Tìm frame chứa thông tin chi tiết
    info_details_frame = None
    for child in app.info_vars["Tên file:"].master.winfo_children():
        if isinstance(child, tk.Label) and child.cget("textvariable") == str(app.info_vars["Tên file:"]):
            info_details_frame = child.master
            break
    
    if not info_details_frame:
        logger.error("Không tìm thấy frame thông tin chi tiết")
        return
    
    # Tạo hoặc cập nhật label trạng thái tải lên
    # Tìm row cuối cùng trong info_details_frame
    last_row = 0
    for child in info_details_frame.winfo_children():
        info = child.grid_info()
        if info and 'row' in info:
            last_row = max(last_row, info['row'])
    
    # Tạo frame mới cho trạng thái
    if hasattr(app, 'status_frame'):
        try:
            app.status_frame.destroy()
        except:
            pass
    
    app.status_frame = tk.Frame(info_details_frame)
    app.status_frame.grid(row=last_row + 1, column=0, columnspan=2, sticky=tk.W, pady=(10, 2))
    
    app.upload_status_label = tk.Label(app.status_frame, anchor=tk.W, justify=tk.LEFT, 
                                    font=("Arial", 10))
    app.upload_status_label.pack(fill=tk.X)
    
    # Hiển thị trạng thái tải lên và trùng lặp
    if upload_info:
        # Định dạng ngày giờ tải lên
        try:
            upload_time = datetime.datetime.fromisoformat(upload_info.get('upload_time', ''))
            formatted_time = upload_time.strftime("%d/%m/%Y %H:%M:%S")
        except (ValueError, TypeError):
            formatted_time = "thời gian không xác định"
        
        # Hiển thị với màu đỏ, in đậm
        app.upload_status_label.config(
            text=f"Người dùng đã tải lên vào {formatted_time}",
            fg="red",
            font=("Arial", 10, "bold")
        )
        
        # Disable nút tải lên video đang chọn
        if hasattr(app, 'upload_single_btn'):
            app.upload_single_btn.config(state=tk.DISABLED)
    elif is_duplicate:
        # Hiển thị trạng thái trùng lặp
        app.upload_status_label.config(
            text="Video này trùng lặp với video khác",
            fg="#FF6600",  # Màu cam
            font=("Arial", 10, "bold")
        )
        
        # Disable nút tải lên video đang chọn
        if hasattr(app, 'upload_single_btn'):
            app.upload_single_btn.config(state=tk.DISABLED)
    else:
        # Hiển thị trạng thái chưa tải lên
        app.upload_status_label.config(
            text="Video chưa được tải lên",
            fg="black",
            font=("Arial", 10)
        )
        
        # Enable nút tải lên video đang chọn
        if hasattr(app, 'upload_single_btn'):
            app.upload_single_btn.config(state=tk.NORMAL)

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
    
    # Đảm bảo checkboxes hiển thị sau khi chuyển trang
    app.root.after(100, app.render_checkboxes)