"""
UI helper utilities for displaying video information and frames.
"""
import os
import cv2
import logging
import tempfile
from PyQt5 import QtWidgets, QtCore, QtGui

logger = logging.getLogger("UIHelpers")

def display_video_info(main_ui, video_path):
    """
    Displays information about a video in the UI
    
    Args:
        main_ui: MainUI instance
        video_path: Path to video file
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file does not exist: {video_path}")
        return
    
    # Get video information
    info = get_video_info(video_path)
    if not info:
        return
    
    # If we can access app's VideoAnalyzer, use it
    if hasattr(main_ui, 'app') and hasattr(main_ui.app, 'video_analyzer'):
        try:
            app_info = main_ui.app.video_analyzer.get_video_info(video_path)
            if app_info:
                info.update(app_info)
        except Exception as e:
            logger.error(f"Error getting video info from app: {str(e)}")
    
    # Update UI with video info
    if hasattr(main_ui, 'video_preview'):
        # Update file name
        file_name_label = main_ui.video_preview.findChild(QtWidgets.QLabel, "fileNameValueLabel")
        if file_name_label:
            file_name_label.setText(info.get("file_name", os.path.basename(video_path)))
        
        # Update duration
        duration_label = main_ui.video_preview.findChild(QtWidgets.QLabel, "durationValueLabel")
        if duration_label:
            duration_str = info.get("duration_str", "00:00:00")
            duration_label.setText(duration_str)
        
        # Update resolution
        resolution_label = main_ui.video_preview.findChild(QtWidgets.QLabel, "resolutionValueLabel")
        if resolution_label:
            resolution_label.setText(info.get("resolution", "Không rõ"))
        
        # Update file size
        size_label = main_ui.video_preview.findChild(QtWidgets.QLabel, "sizeValueLabel")
        if size_label:
            size_label.setText(info.get("file_size", "Không rõ"))
        
        # Update codec
        codec_label = main_ui.video_preview.findChild(QtWidgets.QLabel, "codecValueLabel")
        if codec_label:
            codec_label.setText(info.get("codec", "H.264"))
        
        # Update status based on upload history
        status_label = main_ui.video_preview.findChild(QtWidgets.QLabel, "statusValueLabel")
        if status_label:
            video_hash = info.get("hash")
            if not video_hash and hasattr(main_ui, 'app') and hasattr(main_ui.app, 'video_analyzer'):
                video_hash = main_ui.app.video_analyzer.calculate_video_hash(video_path)
            
            is_uploaded = False
            is_duplicate = False
            
            # Check upload history
            if video_hash and hasattr(main_ui, 'app') and hasattr(main_ui.app, 'upload_history'):
                upload_info = main_ui.app.upload_history.get_upload_by_hash(video_hash)
                is_uploaded = upload_info is not None
            
            # Check duplicate status
            if hasattr(main_ui, 'all_videos'):
                video_name = os.path.basename(video_path)
                for video in main_ui.all_videos:
                    if video.get("name") == video_name and video.get("status") == "duplicate":
                        is_duplicate = True
                        break
            
            # Set status text and color
            if is_uploaded:
                status_label.setText("Đã tải lên")
                status_label.setStyleSheet("color: #FF8C00;")  # Orange color
                
                # Disable upload button if it exists
                upload_btn = main_ui.video_preview.findChild(QtWidgets.QPushButton, "uploadThisVideoButton")
                if upload_btn:
                    upload_btn.setEnabled(False)
            elif is_duplicate:
                status_label.setText("Video trùng lặp")
                status_label.setStyleSheet("color: #FF0000;")  # Red color
                
                # Disable upload button if it exists
                upload_btn = main_ui.video_preview.findChild(QtWidgets.QPushButton, "uploadThisVideoButton")
                if upload_btn:
                    upload_btn.setEnabled(False)
            else:
                status_label.setText("Chưa tải lên")
                status_label.setStyleSheet("color: #10B981;")  # Green color
                
                # Enable upload button if it exists
                upload_btn = main_ui.video_preview.findChild(QtWidgets.QPushButton, "uploadThisVideoButton")
                if upload_btn:
                    upload_btn.setEnabled(True)
    
    # Update preview frame if available
    update_preview_frame(main_ui, video_path)

def get_video_info(video_path):
    """
    Gets information about a video file
    
    Args:
        video_path: Path to video file
        
    Returns:
        dict: Video information
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file does not exist: {video_path}")
        return {}
    
    try:
        # Use OpenCV to get video properties
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return {}
        
        # Get basic properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        # Get file size
        file_size = os.path.getsize(video_path)
        
        # Format file size
        if file_size < 1024:
            file_size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            file_size_str = f"{file_size / 1024:.1f} KB"
        elif file_size < 1024 * 1024 * 1024:
            file_size_str = f"{file_size / (1024 * 1024):.1f} MB"
        else:
            file_size_str = f"{file_size / (1024 * 1024 * 1024):.2f} GB"
        
        # Format duration string
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Release the video capture
        cap.release()
        
        return {
            "file_name": os.path.basename(video_path),
            "resolution": f"{width}x{height}",
            "duration": duration,
            "duration_str": duration_str,
            "fps": fps,
            "file_size": file_size_str,
            "file_size_bytes": file_size,
            "codec": "H.264",  # Default, would need more analysis for accurate codec
            "format": os.path.splitext(video_path)[1].upper().replace(".", "")
        }
    except Exception as e:
        logger.error(f"Error getting video info for {video_path}: {str(e)}")
        return {}

def update_preview_frame(main_ui, video_path):
    """
    Updates the preview frame in the UI with the first frame from the video
    
    Args:
        main_ui: MainUI instance
        video_path: Path to video file
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file does not exist: {video_path}")
        return
    
    try:
        # Use OpenCV to get the first frame
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return
        
        # Read the first frame
        ret, frame = cap.read()
        if not ret:
            logger.error(f"Could not read frame from video: {video_path}")
            cap.release()
            return
        
        # Convert from BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Get preview frame dimensions
        preview_frame = main_ui.video_preview.findChild(QtWidgets.QFrame, "previewFrame")
        if preview_frame:
            width = preview_frame.width()
            height = preview_frame.height()
            
            # Resize frame to fit preview frame
            frame_resized = cv2.resize(frame_rgb, (width, height))
            
            # Convert to QImage
            h, w, ch = frame_resized.shape
            bytes_per_line = ch * w
            image = QtGui.QImage(frame_resized.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            
            # Set as background for preview frame
            preview_frame.setStyleSheet(f"""
                background-image: url({tempfile.gettempdir()}/preview.png);
                background-position: center;
                background-repeat: no-repeat;
                background-size: cover;
            """)
            
            # Save image to temp file for background
            image.save(f"{tempfile.gettempdir()}/preview.png")
        
        # Release video capture
        cap.release()
        
    except Exception as e:
        logger.error(f"Error updating preview frame: {str(e)}")

def display_video_frames(main_ui, video_path):
    """
    Displays video frames in the UI
    
    Args:
        main_ui: MainUI instance
        video_path: Path to video file
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file does not exist: {video_path}")
        return
    
    try:
        # Use OpenCV to get frames
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return
        
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        if total_frames <= 0 or duration <= 0:
            logger.error(f"Invalid video: {video_path}, frames={total_frames}, fps={fps}")
            cap.release()
            return
        
        # Choose 5 positions for frames
        positions = [0.1, 0.3, 0.5, 0.7, 0.9]  # 10%, 30%, 50%, 70%, 90%
        
        # Create temp directory for frames if it doesn't exist
        temp_dir = os.path.join(tempfile.gettempdir(), "telegram_uploader_frames")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Store frame paths
        frame_paths = []
        
        # Get frames from video frames UI container
        if hasattr(main_ui, 'video_frames'):
            for i, pos in enumerate(positions):
                if i < 5:  # We have 5 frame containers
                    # Get frame widget
                    frame_widget = main_ui.video_frames.findChild(QtWidgets.QFrame, f"frame{i+1}")
                    if not frame_widget:
                        continue
                    
                    # Calculate frame position
                    frame_pos = int(total_frames * pos)
                    if frame_pos >= total_frames:
                        frame_pos = total_frames - 1
                    
                    # Seek to position and read frame
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                    ret, frame = cap.read()
                    
                    if ret:
                        # Convert BGR to RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        
                        # Save frame to file
                        frame_path = os.path.join(temp_dir, f"frame_{i}.png")
                        cv2.imwrite(frame_path, frame)
                        frame_paths.append(frame_path)
                        
                        # Set frame as background of frame widget
                        frame_widget.setStyleSheet(f"""
                            background-image: url({frame_path});
                            background-position: center;
                            background-repeat: no-repeat;
                            background-size: contain;
                        """)
                        
                        # Make frame clickable to view in larger size
                        frame_widget.mousePressEvent = lambda event, path=frame_path: show_frame_fullscreen(main_ui, path)
                        
                        # Set cursor to pointing hand
                        frame_widget.setCursor(QtCore.Qt.PointingHandCursor)
        
        # Store frame paths for future reference
        main_ui.frame_paths = frame_paths
        
        # Release video capture
        cap.release()
        
    except Exception as e:
        logger.error(f"Error displaying video frames: {str(e)}")

def show_frame_fullscreen(main_ui, frame_path):
    """
    Shows a frame in a larger dialog
    
    Args:
        main_ui: MainUI instance
        frame_path: Path to frame image
    """
    try:
        # Create dialog
        dialog = QtWidgets.QDialog(main_ui)
        dialog.setWindowTitle("Frame Preview")
        dialog.setMinimumSize(800, 600)
        
        # Create layout
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Create label for image
        label = QtWidgets.QLabel()
        label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Load image
        pixmap = QtGui.QPixmap(frame_path)
        
        # Scale to fit dialog
        pixmap = pixmap.scaled(800, 600, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        
        # Set image
        label.setPixmap(pixmap)
        
        # Add to layout
        layout.addWidget(label)
        
        # Add close button
        button = QtWidgets.QPushButton("Close")
        button.clicked.connect(dialog.accept)
        layout.addWidget(button, alignment=QtCore.Qt.AlignCenter)
        
        # Show dialog
        dialog.exec_()
        
    except Exception as e:
        logger.error(f"Error showing frame fullscreen: {str(e)}")

def update_video_status(main_ui, video_name, status="uploaded"):
    """
    Updates the status of a video in the UI
    
    Args:
        main_ui: MainUI instance
        video_name: Name of the video
        status: New status
    """
    try:
        # Update in video list if available
        if hasattr(main_ui, 'video_list'):
            for i in range(1, 11):  # Assuming up to 10 videos displayed at once
                label = main_ui.video_list.findChild(QtWidgets.QLabel, f"label{i}")
                status_label = main_ui.video_list.findChild(QtWidgets.QLabel, f"status{i}")
                
                if label and label.text() == video_name and status_label:
                    if status == "uploaded":
                        status_label.setText("Đã tải")
                        status_label.setProperty("class", "statusUploaded")
                    elif status == "duplicate":
                        status_label.setText("Trùng")
                        status_label.setProperty("class", "statusDuplicate")
                    else:
                        status_label.setText("Mới")
                        status_label.setProperty("class", "statusNew")
                    
                    # Force style update
                    status_label.style().unpolish(status_label)
                    status_label.style().polish(status_label)
                    break
        
        # Update in videos array if available
        if hasattr(main_ui, 'all_videos'):
            for i, video in enumerate(main_ui.all_videos):
                if video.get("name") == video_name:
                    main_ui.all_videos[i]["status"] = status
                    
                    if status == "uploaded":
                        main_ui.all_videos[i]["info"] = "Đã tải lên mới đây"
                    elif status == "duplicate":
                        # Keep existing duplicate info
                        if not main_ui.all_videos[i].get("info"):
                            main_ui.all_videos[i]["info"] = "Video trùng lặp"
                    else:
                        main_ui.all_videos[i]["info"] = ""
                    
                    break
    except Exception as e:
        logger.error(f"Error updating video status: {str(e)}")

def display_error_message(main_ui, title, message):
    """
    Displays an error message dialog
    
    Args:
        main_ui: MainUI instance
        title: Dialog title
        message: Error message
    """
    QtWidgets.QMessageBox.critical(main_ui, title, message)

def create_progress_dialog(main_ui, title, message, cancellable=True):
    """
    Creates a progress dialog
    
    Args:
        main_ui: MainUI instance
        title: Dialog title
        message: Dialog message
        cancellable: Whether the dialog can be cancelled
        
    Returns:
        tuple: (dialog, progress_bar)
    """
    dialog = QtWidgets.QProgressDialog(message, "Cancel" if cancellable else None, 0, 100, main_ui)
    dialog.setWindowTitle(title)
    dialog.setAutoClose(False)
    dialog.setAutoReset(False)
    dialog.setMinimumDuration(0)
    dialog.setWindowModality(QtCore.Qt.WindowModal)
    
    if not cancellable:
        dialog.setCancelButton(None)
    
    return dialog