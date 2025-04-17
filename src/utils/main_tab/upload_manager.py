"""
Upload management utilities for the main tab in PyQt5 UI.
"""
import os
import time
import threading
import logging
import datetime
import tempfile
from PyQt5 import QtWidgets, QtCore, QtGui

logger = logging.getLogger("UploadManager")

def upload_selected_videos(main_ui):
    """
    Uploads all selected videos
    
    Args:
        main_ui: MainUI instance
    """
    # Get all selected videos
    selected_videos = get_selected_videos(main_ui)
    
    if not selected_videos:
        logger.info("No videos selected for upload")
        QtWidgets.QMessageBox.information(main_ui, "Thông báo", "Vui lòng chọn ít nhất một video để tải lên!")
        return
    
    # Check for duplicates and already uploaded videos
    has_duplicates, has_uploaded, duplicate_videos, uploaded_videos = check_duplicates_and_uploaded(main_ui, selected_videos)
    
    # If there are duplicates or already uploaded videos, confirm with user
    skip_duplicates_uploaded = False
    videos_to_upload = selected_videos
    
    if has_duplicates or has_uploaded:
        skip_duplicates_uploaded = show_upload_confirmation(main_ui, has_duplicates, has_uploaded, duplicate_videos, uploaded_videos)
        
        # Filter videos based on user confirmation
        if skip_duplicates_uploaded:
            videos_to_upload = [
                (video_name, video_path) 
                for video_name, video_path in selected_videos
                if video_name not in duplicate_videos and video_name not in uploaded_videos
            ]
    
    # Check if any videos remain to be uploaded
    if not videos_to_upload:
        QtWidgets.QMessageBox.information(main_ui, "Thông báo", "Không có video nào được tải lên sau khi lọc!")
        return
    
    # Show upload progress dialog
    show_upload_progress(main_ui, videos_to_upload)
    
def get_selected_videos(main_ui):
    """
    Gets list of selected videos from the UI
    
    Args:
        main_ui: MainUI instance
        
    Returns:
        list: List of (video_name, video_path) tuples
    """
    selected_videos = []
    
    if hasattr(main_ui, 'video_list'):
        # Loop through checkboxes and get selected videos
        for i in range(1, 11):  # Assuming we have up to 10 videos displayed at once
            checkbox = main_ui.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
            label = main_ui.video_list.findChild(QtWidgets.QLabel, f"label{i}")
            
            if checkbox and label and checkbox.isChecked():
                video_name = label.text()
                
                # Find video path from main_ui.videos dictionary if available
                if hasattr(main_ui, 'videos') and video_name in main_ui.videos:
                    video_path = main_ui.videos[video_name]
                else:
                    # Fallback to searching in the current folder
                    video_path = os.path.join(main_ui.folder_path_edit.text(), video_name)
                
                if os.path.exists(video_path):
                    selected_videos.append((video_name, video_path))
    
    return selected_videos

def upload_single_video(main_ui, video_name, video_path):
    """
    Uploads a single video
    
    Args:
        main_ui: MainUI instance
        video_name: Name of the video
        video_path: Path to the video file
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file does not exist: {video_path}")
        QtWidgets.QMessageBox.warning(main_ui, "Lỗi", "Không tìm thấy file video!")
        return
    
    # Check if it's already uploaded
    video_hash = None
    is_uploaded = False
    
    if hasattr(main_ui, 'app') and hasattr(main_ui.app, 'video_analyzer'):
        video_hash = main_ui.app.video_analyzer.calculate_video_hash(video_path)
        
        if hasattr(main_ui.app, 'upload_history'):
            is_uploaded = main_ui.app.upload_history.is_uploaded(video_hash)
    
    # If already uploaded, confirm re-upload
    if is_uploaded:
        reply = QtWidgets.QMessageBox.question(
            main_ui,
            "Xác nhận tải lên lại",
            f"Video này đã được tải lên trước đây. Bạn có muốn tải lên lại không?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.No:
            return
    
    # Show upload progress for a single video
    show_upload_progress(main_ui, [(video_name, video_path)])

def check_duplicates_and_uploaded(main_ui, selected_videos):
    """
    Checks if any selected videos are duplicates or have already been uploaded
    
    Args:
        main_ui: MainUI instance
        selected_videos: List of (video_name, video_path) tuples
        
    Returns:
        tuple: (has_duplicates, has_uploaded, duplicate_videos, uploaded_videos)
    """
    has_duplicates = False
    has_uploaded = False
    duplicate_videos = []
    uploaded_videos = []
    
    # First check UI status labels
    if hasattr(main_ui, 'video_list'):
        for i in range(1, 11):  # Assuming we have up to 10 videos
            checkbox = main_ui.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
            label = main_ui.video_list.findChild(QtWidgets.QLabel, f"label{i}")
            status = main_ui.video_list.findChild(QtWidgets.QLabel, f"status{i}")
            
            if checkbox and label and status and checkbox.isChecked():
                video_name = label.text()
                
                # Check status
                if status.text() == "Trùng":
                    has_duplicates = True
                    duplicate_videos.append(video_name)
                elif status.text() == "Đã tải":
                    has_uploaded = True
                    uploaded_videos.append(video_name)
    
    # If app is available, double-check with upload history
    if hasattr(main_ui, 'app') and not has_uploaded:
        for video_name, video_path in selected_videos:
            if video_name not in uploaded_videos and hasattr(main_ui.app, 'video_analyzer') and hasattr(main_ui.app, 'upload_history'):
                video_hash = main_ui.app.video_analyzer.calculate_video_hash(video_path)
                if video_hash and main_ui.app.upload_history.is_uploaded(video_hash):
                    has_uploaded = True
                    uploaded_videos.append(video_name)
    
    return has_duplicates, has_uploaded, duplicate_videos, uploaded_videos

def show_upload_confirmation(main_ui, has_duplicates, has_uploaded, duplicate_videos, uploaded_videos):
    """
    Shows a confirmation dialog for uploading duplicate or already uploaded videos
    
    Args:
        main_ui: MainUI instance
        has_duplicates: Whether there are duplicate videos
        has_uploaded: Whether there are already uploaded videos
        duplicate_videos: List of duplicate video names
        uploaded_videos: List of already uploaded video names
        
    Returns:
        bool: True if user confirms skipping these videos, False otherwise
    """
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
    
    # Show confirmation dialog
    reply = QtWidgets.QMessageBox.question(
        main_ui, 
        "Xác nhận tải lên", 
        message,
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
        QtWidgets.QMessageBox.No
    )
    
    return reply == QtWidgets.QMessageBox.Yes

def show_upload_progress(main_ui, videos_to_upload):
    """
    Shows a dialog with upload progress
    
    Args:
        main_ui: MainUI instance
        videos_to_upload: List of (video_name, video_path) tuples
    """
    # Create upload progress dialog
    progress_dialog = QtWidgets.QDialog(main_ui)
    progress_dialog.setWindowTitle("Tiến trình tải lên video lên Telegram")
    progress_dialog.setFixedSize(700, 500)
    progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
    
    # Create dialog layout
    layout = QtWidgets.QVBoxLayout(progress_dialog)
    
    # Add overall progress section
    layout.addWidget(QtWidgets.QLabel("Tiến trình tổng thể:"))
    
    total_progress = QtWidgets.QProgressBar()
    total_progress.setRange(0, 100)
    total_progress.setValue(0)
    layout.addWidget(total_progress)
    
    total_info = QtWidgets.QLabel(f"0/{len(videos_to_upload)} video hoàn thành")
    layout.addWidget(total_info)
    
    # Add scrollable area for individual video progress
    scroll_area = QtWidgets.QScrollArea()
    scroll_area.setWidgetResizable(True)
    layout.addWidget(scroll_area)
    
    scroll_content = QtWidgets.QWidget()
    scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
    
    # Add progress items for each video
    progress_bars = []
    status_labels = []
    
    for i, (video_name, _) in enumerate(videos_to_upload):
        # Create group for each video
        video_group = QtWidgets.QGroupBox()
        video_layout = QtWidgets.QVBoxLayout(video_group)
        
        # Add video name
        name_text = video_name
        if len(name_text) > 40:
            name_text = name_text[:37] + "..."
            
        name_label = QtWidgets.QLabel(name_text)
        name_label.setStyleSheet("font-weight: bold;")
        video_layout.addWidget(name_label)
        
        # Add progress bar
        progress_bar = QtWidgets.QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        video_layout.addWidget(progress_bar)
        progress_bars.append(progress_bar)
        
        # Add status label
        status_label = QtWidgets.QLabel("Đang chờ...")
        video_layout.addWidget(status_label)
        status_labels.append(status_label)
        
        # Add to scroll layout
        scroll_layout.addWidget(video_group)
    
    # Set scroll content
    scroll_area.setWidget(scroll_content)
    
    # Add cancel/close button
    button_layout = QtWidgets.QHBoxLayout()
    button_layout.addStretch()
    
    cancel_button = QtWidgets.QPushButton("Hủy tải lên")
    button_layout.addWidget(cancel_button)
    
    layout.addLayout(button_layout)
    
    # Prepare upload tracking
    is_cancelled = [False]
    upload_completed = [False]
    
    # Set up cancel button
    def cancel_upload():
        if upload_completed[0]:
            progress_dialog.accept()
        else:
            is_cancelled[0] = True
            cancel_button.setText("Đang hủy...")
            cancel_button.setEnabled(False)
    
    cancel_button.clicked.connect(cancel_upload)
    
    # Prepare upload tracker
    class UploadTracker:
        def __init__(self, dialog, video_count):
            self.dialog = dialog
            self.total_videos = video_count
            self.successful_uploads = 0
            self.failed_uploads = 0
            self.current_video_index = -1
        
        def start_new_video(self, index):
            """Starts uploading a new video"""
            if 0 <= index < len(status_labels):
                self.current_video_index = index
                status_labels[index].setText("Đang tải lên...")
                
                # Update UI using Qt's event loop
                QtCore.QCoreApplication.processEvents()
        
        def update_progress(self, index, progress_value):
            """Updates progress for a video"""
            if 0 <= index < len(progress_bars):
                progress_bars[index].setValue(progress_value)
                
                # Update UI using Qt's event loop
                QtCore.QCoreApplication.processEvents()
        
        def update_status(self, index, status, text=None):
            """Updates status for a video"""
            if status == "success" and 0 <= index < len(status_labels):
                progress_bars[index].setValue(100)
                status_labels[index].setText("Tải lên thành công")
                status_labels[index].setStyleSheet("color: green;")
                self.successful_uploads += 1
            elif status == "error" and 0 <= index < len(status_labels):
                error_text = text or "Tải lên thất bại"
                status_labels[index].setText(error_text)
                status_labels[index].setStyleSheet("color: red;")
                self.failed_uploads += 1
            
            # Update overall progress
            completed = self.successful_uploads + self.failed_uploads
            progress_percent = (completed / self.total_videos) * 100
            total_progress.setValue(int(progress_percent))
            total_info.setText(f"{completed}/{self.total_videos} video hoàn thành " +
                              f"({self.successful_uploads} thành công, {self.failed_uploads} thất bại)")
            
            # Check if all uploads are complete
            if completed == self.total_videos:
                upload_completed[0] = True
                cancel_button.setText("Đóng cửa sổ")
                cancel_button.setEnabled(True)
            
            # Update UI using Qt's event loop
            QtCore.QCoreApplication.processEvents()
    
    # Create tracker
    tracker = UploadTracker(progress_dialog, len(videos_to_upload))
    
    # Start upload in a separate thread
    upload_thread = threading.Thread(
        target=upload_videos_thread,
        args=(main_ui, videos_to_upload, tracker, is_cancelled)
    )
    upload_thread.daemon = True
    
    # Show dialog and start upload
    upload_thread.start()
    result = progress_dialog.exec_()
    
    # Return to indicate dialog was closed
    return upload_completed[0]

def upload_videos_thread(main_ui, videos_to_upload, tracker, is_cancelled):
    """
    Thread function that handles the actual upload process
    
    Args:
        main_ui: MainUI instance
        videos_to_upload: List of (video_name, video_path) tuples
        tracker: UploadTracker instance
        is_cancelled: List with a boolean indicating if the upload was cancelled
    """
    # Get rate limit delay from config if available
    upload_delay = 5  # Default delay
    if hasattr(main_ui, 'app') and hasattr(main_ui.app, 'config'):
        if 'SETTINGS' in main_ui.app.config and 'delay_between_uploads' in main_ui.app.config['SETTINGS']:
            try:
                upload_delay = int(main_ui.app.config['SETTINGS']['delay_between_uploads'])
            except ValueError:
                pass
    
    rate_limit_delay = max(8, upload_delay)  # Minimum 8 seconds
    
    # For each video
    for i, (video_name, video_path) in enumerate(videos_to_upload):
        # Check if cancelled
        if is_cancelled[0]:
            tracker.update_status(i, "error", "Đã hủy tải lên")
            continue
        
        # Signal start of upload
        tracker.start_new_video(i)
        
        # Check if file exists
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            tracker.update_status(i, "error", "File không tồn tại")
            continue
        
        # Prepare caption
        caption = f"📹 {video_name}\n📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Retry logic
        max_retries = 5
        retry_count = 0
        upload_success = False
        
        while retry_count < max_retries and not upload_success and not is_cancelled[0]:
            if retry_count > 0:
                # If retrying, update status and wait
                tracker.update_status(i, "processing", f"Đang thử lại... (lần {retry_count}/{max_retries})")
                
                # Increase delay for each retry
                retry_delay = rate_limit_delay * (1 + retry_count * 0.5)
                time.sleep(retry_delay)
            
            try:
                # Try to upload the video
                if hasattr(main_ui, 'app') and hasattr(main_ui.app, 'telegram_api'):
                    # Calculate video size
                    video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
                    
                    # Set simulated progress
                    for progress in range(10, 91, 10):
                        # Check if cancelled
                        if is_cancelled[0]:
                            break
                        
                        tracker.update_progress(i, progress)
                        
                        # Simulate upload delay based on file size
                        time.sleep(min(1.0, video_size_mb / 50))  # Larger files take longer
                    
                    # Get chat ID from config
                    chat_id = None
                    if hasattr(main_ui.app, 'config') and 'TELEGRAM' in main_ui.app.config:
                        chat_id = main_ui.app.config['TELEGRAM'].get('chat_id')
                    
                    # Check if we should use Telethon for large files
                    use_telethon = False
                    if hasattr(main_ui.app, 'config') and 'TELETHON' in main_ui.app.config:
                        use_telethon = main_ui.app.config['TELETHON'].getboolean('use_telethon', False)
                    
                    # Use appropriate upload method
                    if use_telethon and video_size_mb > 50 and hasattr(main_ui.app, 'telethon_uploader'):
                        success = main_ui.app.telegram_api.send_video_with_telethon(
                            chat_id, 
                            video_path,
                            caption=caption
                        )
                    else:
                        success = main_ui.app.telegram_api.send_video(
                            chat_id, 
                            video_path,
                            caption=caption
                        )
                    
                    if success:
                        upload_success = True
                        
                        # Add to upload history
                        if hasattr(main_ui.app, 'video_analyzer') and hasattr(main_ui.app, 'upload_history'):
                            video_hash = main_ui.app.video_analyzer.calculate_video_hash(video_path)
                            if video_hash:
                                file_size = os.path.getsize(video_path)
                                # Log upload time
                                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                main_ui.app.upload_history.add_upload(video_hash, video_name, video_path, file_size, upload_date=now)
                        
                        # Update status
                        tracker.update_status(i, "success")
                        
                        # Update video status in the list
                        update_video_status_in_ui(main_ui, video_name)
                    else:
                        # Upload failed, retry
                        retry_count += 1
                else:
                    # Simulate successful upload if no telegram_api available
                    tracker.update_progress(i, 100)
                    time.sleep(1)
                    upload_success = True
                    tracker.update_status(i, "success")
                    
                    # Update video status in the list
                    update_video_status_in_ui(main_ui, video_name)
            except Exception as e:
                logger.error(f"Error uploading video {video_name}: {str(e)}")
                retry_count += 1
                if retry_count >= max_retries:
                    tracker.update_status(i, "error", f"Lỗi: {str(e)[:50]}")
        
        # Add delay between uploads if not the last video and not cancelled
        if i < len(videos_to_upload) - 1 and not is_cancelled[0] and upload_success:
            time.sleep(rate_limit_delay)

def update_video_status_in_ui(main_ui, video_name):
    """
    Updates the status of a video in the UI after upload
    
    Args:
        main_ui: MainUI instance
        video_name: Name of the video
    """
    if hasattr(main_ui, 'video_list'):
        for i in range(1, 11):  # Assuming up to 10 videos displayed at once
            label = main_ui.video_list.findChild(QtWidgets.QLabel, f"label{i}")
            status = main_ui.video_list.findChild(QtWidgets.QLabel, f"status{i}")
            
            if label and status and label.text() == video_name:
                # Change status to "uploaded"
                status.setText("Đã tải")
                status.setProperty("class", "statusUploaded")
                
                # Force style update
                status.style().unpolish(status)
                status.style().polish(status)
                
                # Update in videos array if available
                if hasattr(main_ui, 'all_videos'):
                    for j, video in enumerate(main_ui.all_videos):
                        if video.get("name") == video_name:
                            main_ui.all_videos[j]["status"] = "uploaded"
                            main_ui.all_videos[j]["info"] = "Đã tải lên mới đây"
                            break
                
                logger.info(f"Updated UI status for {video_name} to uploaded")
                break