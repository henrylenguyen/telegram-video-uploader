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

def refresh_video_list(app):
    """
    Làm mới danh sách video từ thư mục đã chọn - with improved error handling
    
    Args:
        app: Đối tượng TelegramUploaderApp
    """
    try:
        # Get and sanitize folder path
        folder_path = app.folder_path.get().strip()
        
        # Update the UI with the sanitized path
        app.folder_path.set(folder_path)
        
        if not folder_path or not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            messagebox.showerror("Lỗi", "Thư mục không hợp lệ hoặc không tồn tại!")
            return
        
        # Save selection state before clearing the list
        selected_videos = {}
        # Only check items that actually exist in the tree
        valid_items = [item for item in app.video_tree.get_children()]
        
        for item_id in list(app.video_checkboxes.keys()):
            try:
                if item_id in valid_items:
                    if app.video_checkboxes[item_id].get():
                        values = app.video_tree.item(item_id, "values")
                        if len(values) > 1:
                            video_name = values[1]
                            selected_videos[video_name] = True
            except Exception as e:
                logger.error(f"Error accessing item {item_id}: {str(e)}")
                # Remove invalid item reference
                if item_id in app.video_checkboxes:
                    del app.video_checkboxes[item_id]
        
        # Xóa danh sách hiện tại
        for item in app.video_tree.get_children():
            app.video_tree.delete(item)
        
        # Reset data structures
        app.videos = {}
        app.duplicate_groups = []
        app.video_checkboxes = {}
        app.video_items = []
        
        # Xóa các checkbox widget hiện tại
        if hasattr(app, 'checkbox_widgets'):
            for checkbox in app.checkbox_widgets:
                try:
                    checkbox.destroy()
                except Exception:
                    pass
        app.checkbox_widgets = []
        
        # Lấy danh sách phần mở rộng video hợp lệ
        extensions = app.config['SETTINGS']['video_extensions'].split(',')
        
        # Cập nhật trạng thái
        if hasattr(app, 'status_var'):
            app.status_var.set("Đang quét thư mục...")
            app.root.update_idletasks()
        
        # Quét thư mục
        video_files = []
        try:
            for file in os.listdir(folder_path):
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in extensions:
                    video_files.append(file)
        except Exception as e:
            logger.error(f"Error scanning directory {folder_path}: {str(e)}")
            if hasattr(app, 'status_var'):
                app.status_var.set(f"Lỗi quét thư mục: {str(e)}")
            video_files = []
        
        # Kiểm tra nếu không có video nào
        if not video_files:
            if hasattr(app, 'status_var'):
                app.status_var.set("Không tìm thấy video trong thư mục")
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
        if hasattr(app, 'check_history_var') and app.check_history_var.get():
            if hasattr(app, 'status_var'):
                app.status_var.set("Đang kiểm tra với lịch sử tải lên...")
            app.root.update_idletasks()
            
            # Lấy lịch sử đã tải lên
            upload_history = app.upload_history.get_all_uploads()
            
            # Kiểm tra từng video
            for i, item in enumerate(app.video_items):
                try:
                    video_path = item["path"]
                    
                    if video_path:
                        video_hash = app.video_analyzer.calculate_video_hash(video_path)
                        if video_hash and app.upload_history.is_uploaded(video_hash):
                            # Đánh dấu đã tải lên
                            app.video_items[i]["status"] = "Đã tải lên"
                            app.video_items[i]["tags"] = ("uploaded",)
                            already_uploaded_videos.add(item["name"])
                except Exception as e:
                    logger.error(f"Error checking history for {item.get('name', 'unknown')}: {str(e)}")
        
        # Nếu có yêu cầu kiểm tra trùng lặp
        duplicate_count = 0
        if hasattr(app, 'check_duplicates_var') and app.check_duplicates_var.get() and len(video_files) > 1:
            if hasattr(app, 'status_var'):
                app.status_var.set("Đang phân tích video để tìm trùng lặp...")
            app.root.update_idletasks()
            
            try:
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
            except Exception as e:
                logger.error(f"Error checking duplicates: {str(e)}")
        
        # Cập nhật thông tin tổng số
        app.total_info_var.set(f"Tổng: {len(video_files)} video, {duplicate_count} video trùng, {len(already_uploaded_videos)} video đã tải lên")
        if hasattr(app, 'status_var'):
            app.status_var.set("Đã sẵn sàng") 
        
        # Cập nhật phân trang
        total_pages = max(1, math.ceil(len(app.video_items) / app.items_per_page))
        app.current_page = 1
        app.page_info_var.set(f"Trang 1/{total_pages}")
        
        # Cập nhật trạng thái nút phân trang
        app.prev_page_btn["state"] = tk.DISABLED
        app.next_page_btn["state"] = tk.NORMAL if total_pages > 1 else tk.DISABLED
        
        # Cập nhật nội dung bảng
        try:
            update_table_content(app)
            
            # Khôi phục lại các trạng thái của checkbox
            # Đợi UI cập nhật
            app.root.update_idletasks()
            
            # Đảm bảo render lại checkbox sau khi cập nhật
            app.root.after(200, lambda: safely_render_checkboxes(app))
        except Exception as e:
            logger.error(f"Error updating table content: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
    except Exception as e:
        logger.error(f"Error in refresh_video_list: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Do not show error message box here to prevent double errors
        if hasattr(app, 'status_var'):
            app.status_var.set(f"Lỗi làm mới danh sách: {str(e)}")
def safely_render_checkboxes(app):
    """Vẽ lại checkbox với xử lý lỗi cẩn thận hơn"""
    try:
        # Import CustomCheckbox từ components
        try:
            from ui.components.checkbox import create_checkbox_cell
        except ImportError:
            try:
                from src.ui.components.checkbox import create_checkbox_cell
            except ImportError:
                # Last resort: direct import
                import sys, os
                sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                from ui.components.checkbox import create_checkbox_cell
        
        # Xóa tất cả checkbox hiện tại
        if hasattr(app, 'checkbox_widgets'):
            for checkbox in app.checkbox_widgets:
                try:
                    checkbox.destroy()
                except Exception as e:
                    logger.error(f"Error destroying checkbox: {str(e)}")
        
        app.checkbox_widgets = []
        
        # Force cập nhật UI
        app.root.update_idletasks()
        
        # Lấy danh sách các item hiện có
        try:
            valid_items = [item for item in app.video_tree.get_children()]
        except Exception as e:
            logger.error(f"Error getting tree children: {str(e)}")
            valid_items = []
        
        # Dọn dẹp các tham chiếu không còn hợp lệ trong checkbox_vars
        invalid_keys = [key for key in app.video_checkboxes if key not in valid_items]
        for key in invalid_keys:
            if key in app.video_checkboxes:
                del app.video_checkboxes[key]
        
        # Tạo checkbox cho tất cả hàng
        for item_id in valid_items:
            try:
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
            except Exception as e:
                logger.error(f"Error creating checkbox for item {item_id}: {str(e)}")
        
        # Force cập nhật lại lần nữa để đảm bảo hiển thị
        app.root.update_idletasks()
        
    except Exception as e:
        logger.error(f"Error in safely_render_checkboxes: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
def update_table_content(app):
    """Cập nhật nội dung bảng theo trang hiện tại và đảm bảo checkboxes hiển thị"""
    try:
        # Xóa tất cả các mục trong bảng
        for item in app.video_tree.get_children():
            try:
                app.video_tree.delete(item)
            except Exception as e:
                logger.error(f"Error deleting tree item {item}: {str(e)}")
        
        # Tính chỉ số bắt đầu và kết thúc
        start_idx = (app.current_page - 1) * app.items_per_page
        end_idx = min(start_idx + app.items_per_page, len(app.video_items))
        
        # Thêm các mục của trang hiện tại vào bảng
        for i in range(start_idx, end_idx):
            try:
                if i < len(app.video_items):
                    item_data = app.video_items[i]
                    video_name = item_data["name"]
                    status = item_data.get("status", "")
                    info = item_data.get("info", "")
                    tags = item_data.get("tags", ())
                    
                    # Xác định trước nếu video này cần được chọn
                    should_check = not (status == "Đã tải lên" or status == "Trùng lặp" or "uploaded" in tags or "duplicate" in tags)
                    
                    # Thêm text "Chọn" để cải thiện hiển thị cho cột checkbox
                    item_id = app.video_tree.insert("", tk.END, values=("Chọn", video_name, status, info), tags=tags)
                    
                    # Tạo biến checkbox với trạng thái mặc định
                    app.video_checkboxes[item_id] = tk.BooleanVar(value=should_check)
            except Exception as e:
                logger.error(f"Error adding item to tree: {str(e)}")
        
        # Đảm bảo UI được cập nhật
        try:
            app.root.update_idletasks()
        except Exception as e:
            logger.error(f"Error updating UI: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error in update_table_content: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
def render_checkboxes(app):
    """Vẽ lại tất cả checkbox trên treeview"""
    # Import CustomCheckbox từ components
    try:
        from ui.components.checkbox import create_checkbox_cell, CustomCheckbox
    except ImportError:
        try:
            from ..components.checkbox import create_checkbox_cell, CustomCheckbox
        except ImportError:
            # Cố gắng import trực tiếp
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            from ui.components.checkbox import create_checkbox_cell, CustomCheckbox
    
    # Xóa tất cả checkbox hiện tại
    if hasattr(app, 'checkbox_widgets'):
        for checkbox in app.checkbox_widgets:
            try:
                checkbox.destroy()
            except:
                pass
    else:
        app.checkbox_widgets = []
    
    app.checkbox_widgets = []
    
    # Đảm bảo UI đã được cập nhật
    app.root.update_idletasks()
    
    # Tạo checkbox cho tất cả hàng
    for item_id in app.video_tree.get_children():
        if item_id not in app.video_checkboxes:
            # Kiểm tra trạng thái video
            values = app.video_tree.item(item_id, "values")
            status = values[1] if len(values) > 1 else ""
            is_uploaded = status == "Đã tải lên"
            default_checked = not is_uploaded
            
            app.video_checkboxes[item_id] = tk.BooleanVar(value=default_checked)
        
        # Tạo checkbox cho mỗi hàng
        bbox = app.video_tree.bbox(item_id, "#1")
        if bbox:
            x = bbox[0] + 5
            y = bbox[1] + (bbox[3] - 30) // 2  # Căn giữa với kích thước 30px
            
            checkbox = CustomCheckbox(app.video_tree)
            checkbox.place(x=x, y=y, width=30, height=30)  # Chỉ định kích thước 30x30px
            checkbox.item_id = item_id
            checkbox.set(app.video_checkboxes[item_id].get())
            
            # Thêm callback để cập nhật giá trị khi click
            def update_var(item=item_id, check=checkbox):
                app.video_checkboxes[item].set(check.get())
            
            checkbox.config(command=update_var)
            app.checkbox_widgets.append(checkbox)
    
    # Force update UI
    app.root.update_idletasks()          

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
            
            # Đảm bảo render lại checkboxes sau khi làm mới
            # Đợi một chút để UI cập nhật trước
            app.root.after(100, lambda: render_checkboxes(app))
            
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
      app.switch_tab(1)  # Chuyển đến tab Cài đặt (index 1)
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
        
        # Lấy thông tin cơ bản
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
        
        # Tạo mảng lưu frames và đường dẫn (QUAN TRỌNG: phải lưu tham chiếu)
        frames = []
        frame_paths = []
        
        # Tính toán kích thước cho mỗi frame - Thiết lập chiều cao 280px theo yêu cầu
        frame_height = 280
        
        # Tính tỉ lệ khung hình để giữ tỉ lệ khung hình đúng
        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Tính toán chiều rộng dựa trên tỉ lệ khung hình
        if video_height > 0:
            aspect_ratio = video_width / video_height
            frame_width = int(frame_height * aspect_ratio)
        else:
            frame_width = 170  # Giá trị mặc định
        
        # Đảm bảo frame_width không quá nhỏ hoặc quá lớn
        frame_width = max(170, min(frame_width, 450))
        
        # Tạo thư mục tạm để lưu frames
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix="telegram_uploader_frames_")
        
        # Xử lý từng vị trí
        for i, pos in enumerate(positions):
            if i >= len(app.frame_labels):
                break
                
            # Tính vị trí frame theo thời gian
            frame_pos = int(total_frames * pos) 
            if frame_pos >= total_frames:
                frame_pos = total_frames - 1
            
            # Seek đến vị trí và đọc frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = cap.read()
            
            if ret:
                # Chuyển frame sang định dạng PIL
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)
                
                # Resize theo kích thước đã định
                try:
                    pil_img = pil_img.resize((frame_width, frame_height), Image.LANCZOS)
                except Exception:
                    try:
                        # Fallback nếu LANCZOS không hoạt động
                        pil_img = pil_img.resize((frame_width, frame_height), Image.BICUBIC)
                    except Exception as e:
                        logger.error(f"Không thể resize frame: {str(e)}")
                        continue
                
                # Lưu frame vào file tạm
                frame_path = os.path.join(temp_dir, f"frame_{i}.png")
                pil_img.save(frame_path)
                frame_paths.append(frame_path)
                
                # Chuyển sang định dạng Tkinter
                tk_image = ImageTk.PhotoImage(pil_img)
                frames.append(tk_image)  # Lưu reference để tránh bị thu hồi
                
                # Hiển thị lên label
                app.frame_labels[i].config(text="")
                app.frame_labels[i].config(image=tk_image)
                
                # Thêm cursor pointer để biểu thị có thể click
                app.frame_labels[i].config(cursor="hand2")
                
                # Thêm click event để mở gallery
                app.frame_labels[i].bind("<Button-1>", 
                      lambda event, paths=frame_paths.copy(), idx=i: 
                      open_pyqt5_gallery(app, paths, idx))
                
                # Thêm tooltip để thông báo có thể click
                try:
                    # Import function to add tooltip
                    from ui.main_tab.tooltip_function import add_tooltip
                    add_tooltip(app.frame_labels[i], "Nhấn để xem phóng to")
                except ImportError:
                    # If function not available, add the tooltip here
                    def add_tooltip_here(widget, text):
                        tooltip = None
                        
                        def enter(e):
                            nonlocal tooltip
                            x = y = 0
                            x, y, _, _ = widget.bbox("insert") if hasattr(widget, "bbox") else (0, 0, 0, 0)
                            x += widget.winfo_rootx() + 25
                            y += widget.winfo_rooty() + 25
                            
                            # Create a toplevel window
                            tooltip = tk.Toplevel(widget)
                            tooltip.wm_overrideredirect(True)
                            tooltip.wm_geometry(f"+{x}+{y}")
                            
                            label = tk.Label(tooltip, text=text, background="#ffffe0", 
                                          relief="solid", borderwidth=1, font=("Arial", 9))
                            label.pack(padx=3, pady=2)
                            
                        def leave(e):
                            nonlocal tooltip
                            if tooltip:
                                tooltip.destroy()
                                tooltip = None
                                
                        widget.bind("<Enter>", enter)
                        widget.bind("<Leave>", leave)
                    
                    add_tooltip_here(app.frame_labels[i], "Nhấn để xem phóng to")
            else:
                app.frame_labels[i].config(image="", text=f"Không thể đọc frame tại {pos*100:.0f}%")
        
        # Giải phóng tài nguyên
        cap.release()
        
        # QUAN TRỌNG: Lưu frames vào đối tượng app để tránh bị thu hồi
        app.current_frames = frames
        app.frame_paths = frame_paths
        app.temp_dir = temp_dir  # Lưu để xóa sau khi đóng
    
    except Exception as e:
        logger.error(f"Lỗi hiển thị frame: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Hiển thị thông báo lỗi trong các frame
        for i, label in enumerate(app.frame_labels):
            label.config(image="", text=f"Lỗi: {str(e)[:30]}")

def open_pyqt5_gallery(app, image_paths, initial_index=0):
    """
    Mở gallery modal PyQt5 để xem các frame
    
    Args:
        app: Đối tượng TelegramUploaderApp
        image_paths: Danh sách đường dẫn đến các frame
        initial_index: Index của frame hiển thị ban đầu
    """
    try:
        # Import function to open gallery
        from ui.components.gallery_integration import open_gallery_modal
        
        # Call the function to open gallery
        success = open_gallery_modal(image_paths, initial_index)
        
        if not success:
            # Fallback to old gallery if PyQt5 gallery fails
            from ui.components.gallery_modal import GalleryModal
            gallery = GalleryModal(app.root, image_paths, initial_index)
    
    except ImportError:
        # Fallback to old gallery if import fails
        try:
            from ui.components.gallery_modal import GalleryModal
            gallery = GalleryModal(app.root, image_paths, initial_index)
        except Exception as e:
            logger.error(f"Lỗi khi mở gallery: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể mở gallery: {str(e)}")
    
    except Exception as e:
        logger.error(f"Lỗi khi mở gallery: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        messagebox.showerror("Lỗi", f"Không thể mở gallery: {str(e)}")
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
                try:
                    pil_img = pil_img.resize((frame_width, frame_height), Image.LANCZOS)
                except Exception:
                    pil_img = pil_img.resize((frame_width, frame_height), Image.BICUBIC)
                
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

    # Cập nhật trạng thái với màu sắc
    if hasattr(app, 'status_value_label'):
        if upload_info:
            upload_date = upload_info.get('upload_date', 'thời gian không xác định')
            app.status_value_label.config(
                text=f"Video đã tải lên vào {upload_date}",
                fg="#FF8C00"  # Màu vàng cam
            )
            
            # Disable nút tải lên video đang chọn
            if hasattr(app, 'upload_single_btn'):
                app.upload_single_btn.config(state=tk.DISABLED)
        elif is_duplicate:
            app.status_value_label.config(
                text="Video trùng lặp với video khác",
                fg="#FF0000"  # Màu đỏ
            )
            
            # Disable nút tải lên video đang chọn
            if hasattr(app, 'upload_single_btn'):
                app.upload_single_btn.config(state=tk.DISABLED)
        else:
            app.status_value_label.config(
                text="Video chưa tải lên",
                fg="#009900"  # Màu xanh lá
            )
            
            # Enable nút tải lên video đang chọn
            if hasattr(app, 'upload_single_btn'):
                app.upload_single_btn.config(state=tk.NORMAL)
    
    # Cập nhật biến "Trạng thái:" trong info_vars
    if "Trạng thái:" in app.info_vars:
        app.info_vars["Trạng thái:"].set(trạng_thái)
        
        # Tìm label của trạng thái để cập nhật màu sắc
        for widget in app.root.winfo_children():
            for child in widget.winfo_children():
                if hasattr(child, 'winfo_children'):
                    for frame in child.winfo_children():
                        if isinstance(frame, ttk.LabelFrame) and "Thông tin video đã chọn" in str(frame.cget("text")):
                            for inner_frame in frame.winfo_children():
                                if isinstance(inner_frame, ttk.Frame):
                                    for detail_frame in inner_frame.winfo_children():
                                        if isinstance(detail_frame, ttk.Frame):
                                            # Tìm trong các widget con của detail_frame
                                            for label in detail_frame.winfo_children():
                                                if (isinstance(label, ttk.Label) and 
                                                    hasattr(label, 'cget') and 
                                                    label.cget("text") == "Trạng thái:"):
                                                    # Tìm status label kế bên
                                                    for widget in detail_frame.winfo_children():
                                                        if (isinstance(widget, ttk.Label) and 
                                                            hasattr(widget, 'cget') and 
                                                            "textvariable" in widget.keys() and 
                                                            widget.cget("textvariable") == str(app.info_vars["Trạng thái:"])):
                                                            widget.config(foreground=color)
                                                            break
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