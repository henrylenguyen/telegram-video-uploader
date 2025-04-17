"""
UI helper utilities for displaying video information and frames.
"""
import os
import cv2
import logging
import tempfile  # Thêm import thiếu sót
import traceback
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

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
        
        # Update status based on upload history or duplicates
        status_label = main_ui.video_preview.findChild(QtWidgets.QLabel, "statusValueLabel")
        if status_label:
            video_hash = info.get("hash")
            if not video_hash and hasattr(main_ui, 'app') and hasattr(main_ui.app, 'video_analyzer'):
                video_hash = main_ui.app.video_analyzer.calculate_video_hash(video_path)
            
            is_uploaded = False
            is_duplicate = False
            duplicate_info = ""
            
            # Check upload history
            if video_hash and hasattr(main_ui, 'app') and hasattr(main_ui.app, 'upload_history'):
                upload_info = main_ui.app.upload_history.get_upload_by_hash(video_hash)
                is_uploaded = upload_info is not None
            
            # Check duplicate status
            if hasattr(main_ui, 'all_videos'):
                video_name = os.path.basename(video_path)
                for video in main_ui.all_videos:
                    if video.get("name") == video_name:
                        if video.get("status") == "duplicate":
                            is_duplicate = True
                            if "info" in video and video["info"] and video["info"].startswith("Trùng với:"):
                                duplicate_info = video["info"]
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
                if duplicate_info:
                    status_text = f"Video trùng lặp\n{duplicate_info}"
                    status_label.setText(status_text)
                    # Hiển thị tooltip với thông tin chi tiết
                    status_label.setToolTip(status_text)
                else:
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
            
            # Try to get basic file info at least
            file_size = os.path.getsize(video_path)
            file_size_str = format_file_size(file_size)
            file_name = os.path.basename(video_path)
            
            # Return minimal info
            return {
                "file_name": file_name,
                "resolution": "Không rõ",
                "duration": 0,
                "duration_str": "00:00:00",
                "fps": 0,
                "file_size": file_size_str,
                "file_size_bytes": file_size,
                "codec": "Không rõ",
                "format": os.path.splitext(video_path)[1].upper().replace(".", "")
            }
        
        # Get basic properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        # Get file size
        file_size = os.path.getsize(video_path)
        
        # Format file size
        file_size_str = format_file_size(file_size)
        
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
        logger.error(traceback.format_exc())
        
        # Try to get basic file info at least
        try:
            file_size = os.path.getsize(video_path)
            file_size_str = format_file_size(file_size)
            file_name = os.path.basename(video_path)
            
            # Return minimal info
            return {
                "file_name": file_name,
                "resolution": "Không rõ",
                "duration": 0,
                "duration_str": "00:00:00",
                "fps": 0,
                "file_size": file_size_str,
                "file_size_bytes": file_size,
                "codec": "Không rõ",
                "format": os.path.splitext(video_path)[1].upper().replace(".", "")
            }
        except:
            return {}

def format_file_size(size_in_bytes):
    """Format file size in bytes to human-readable string"""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} GB"

def update_preview_frame(main_ui, video_path):
    """
    Updates the preview frame in the UI with a frame from the video
    
    Args:
        main_ui: MainUI instance
        video_path: Path to video file
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file does not exist: {video_path}")
        return
    
    logger.debug(f"Updating preview frame for: {video_path}")
    
    try:
        # Use OpenCV to get the frame
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return
        
        # Get total frames
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            logger.error(f"Video has no frames: {video_path}")
            cap.release()
            return
        
        # Seek to middle frame for preview
        middle_frame = total_frames // 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
        
        # Read the frame
        ret, frame = cap.read()
        if not ret:
            logger.error(f"Could not read frame from video: {video_path}")
            cap.release()
            return
        
        # Create temp directory for frames if it doesn't exist
        temp_dir = os.path.join(tempfile.gettempdir(), "telegram_uploader_frames")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Save frame to temp file
        preview_path = os.path.join(temp_dir, "preview.jpg")
        cv2.imwrite(preview_path, frame)
        
        # Get preview frame widget
        preview_frame = main_ui.video_preview.findChild(QtWidgets.QFrame, "previewFrame")
        if preview_frame:
            # Check if layout already exists
            layout = preview_frame.layout()
            if layout is None:
                # Create new layout if it doesn't exist
                layout = QtWidgets.QVBoxLayout(preview_frame)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setAlignment(Qt.AlignCenter)
            else:
                # Clear existing layout
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget and type(widget).__name__ != "PlayButton":
                        widget.deleteLater()
            
            # Create label for the image
            image_label = QtWidgets.QLabel()
            image_label.setObjectName("previewImageLabel")
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("background: transparent;")
            
            # Load image and scale it to fit the preview frame
            pixmap = QtGui.QPixmap(preview_path)
            if not pixmap.isNull():
                logger.debug(f"Preview image loaded successfully: {preview_path}")
                # Get the size of the preview frame
                frame_size = preview_frame.size()
                # Scale the image to fit the frame while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    frame_size.width(), 
                    frame_size.height(),
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                image_label.setPixmap(scaled_pixmap)
            else:
                logger.error(f"Failed to load preview image: {preview_path}")
                image_label.setText("Không thể tải hình ảnh")
            
            # Add the label to the layout
            layout.addWidget(image_label)
            
            # Find play button if it exists and bring it to front
            play_button_container = main_ui.video_preview.findChild(QtWidgets.QWidget, "playButtonContainer")
            if play_button_container:
                play_button_container.raise_()
                # Make it semi-transparent
                play_button = play_button_container.findChild(QtWidgets.QPushButton)
                if play_button:
                    play_button.setStyleSheet("background-color: rgba(52, 152, 219, 0.5);")
            
            logger.debug(f"Preview frame updated successfully")
        else:
            logger.error("Preview frame widget not found")
        
        # Release video capture
        cap.release()
        
    except Exception as e:
        logger.error(f"Error updating preview frame: {str(e)}")
        logger.error(traceback.format_exc())

def clear_video_preview(main_ui):
    """
    Clear video preview and information
    
    Args:
        main_ui: MainUI instance
    """
    try:
        logger.debug("Clearing video preview")
        
        # Clear video preview
        preview_frame = main_ui.video_preview.findChild(QtWidgets.QFrame, "previewFrame")
        if preview_frame and preview_frame.layout():
            # Clear existing layout except for play button
            layout = preview_frame.layout()
            items_to_remove = []
            
            # First gather all items to remove
            for i in range(layout.count()):
                item = layout.itemAt(i)
                widget = item.widget()
                if widget and type(widget).__name__ != "PlayButton" and widget.parent() != main_ui.play_button:
                    items_to_remove.append(widget)
            
            # Then remove them
            for widget in items_to_remove:
                widget.deleteLater()
        
        # Reset play button if exists
        if hasattr(main_ui, 'play_button'):
            main_ui.play_button.setStyleSheet("")
        
        # Clear information fields
        fields = ['fileNameValueLabel', 'durationValueLabel', 'resolutionValueLabel', 
                  'sizeValueLabel', 'statusValueLabel', 'codecValueLabel']
        
        for field in fields:
            label = main_ui.video_preview.findChild(QtWidgets.QLabel, field)
            if label:
                label.setText("")
        
        # Clear video frames
        clear_video_frames(main_ui)
        
        logger.debug("Video preview cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing video preview: {str(e)}")
        logger.error(traceback.format_exc())

def clear_video_frames(main_ui):
    """
    Clear video frames
    
    Args:
        main_ui: MainUI instance
    """
    try:
        logger.debug("Clearing video frames")
        
        if not hasattr(main_ui, 'video_frames'):
            logger.debug("No video frames widget found")
            return
            
        # Clear frame paths
        if hasattr(main_ui, 'frame_paths'):
            main_ui.frame_paths = []
        
        # Clear each frame
        for i in range(1, 6):
            frame_widget = main_ui.video_frames.findChild(QtWidgets.QFrame, f"frame{i}")
            if frame_widget and frame_widget.layout():
                # Clear existing layout
                layout = frame_widget.layout()
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
                
                # Reset cursor and event handlers
                frame_widget.setCursor(QtCore.Qt.ArrowCursor)
                frame_widget.mousePressEvent = lambda event: None
    
        logger.debug("Video frames cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing video frames: {str(e)}")
        logger.error(traceback.format_exc())

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
    
    logger.debug(f"Displaying video frames for: {video_path}")
    
    try:
        # Use OpenCV to get frames
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            # Try FFmpeg or other method for unsupported formats
            try:
                import subprocess
                
                # Create temp directory for frames
                temp_dir = os.path.join(tempfile.gettempdir(), "telegram_uploader_frames")
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                # Generate 5 frames using FFmpeg
                logger.debug("Attempting to extract frames using FFmpeg")
                for i in range(5):
                    percentage = i * 20 + 10  # 10%, 30%, 50%, 70%, 90%
                    output_path = os.path.join(temp_dir, f"frame_{i}_ffmpeg.jpg")
                    
                    # Use FFmpeg to extract the frame
                    ffmpeg_cmd = [
                        "ffmpeg", "-y", "-i", video_path, 
                        "-ss", f"percentage:{percentage}", 
                        "-frames:v", "1", output_path
                    ]
                    
                    subprocess.run(ffmpeg_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                    
                    # Check if file was created
                    if os.path.exists(output_path):
                        logger.debug(f"Frame extracted successfully: {output_path}")
                        if hasattr(main_ui, 'frame_paths'):
                            main_ui.frame_paths.append(output_path)
                
                # If frames were generated, display them
                if hasattr(main_ui, 'frame_paths') and main_ui.frame_paths:
                    logger.debug(f"Displaying {len(main_ui.frame_paths)} frames from FFmpeg")
                    display_video_frames_from_paths(main_ui, main_ui.frame_paths)
                    return
                else:
                    logger.error("No frames generated by FFmpeg")
            
            except Exception as ffmpeg_error:
                logger.error(f"FFmpeg extraction failed: {str(ffmpeg_error)}")
                logger.error(traceback.format_exc())
            
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
        
        # Clear previous frame paths
        if hasattr(main_ui, 'frame_paths'):
            main_ui.frame_paths = []
        else:
            main_ui.frame_paths = []
        
        # Extract frames
        frame_paths = []
        for i, pos in enumerate(positions):
            # Calculate frame position
            frame_pos = int(total_frames * pos)
            if frame_pos >= total_frames:
                frame_pos = total_frames - 1
            
            # Seek to position and read frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = cap.read()
            
            if ret:
                # Save frame to file
                frame_path = os.path.join(temp_dir, f"frame_{i}.jpg")
                cv2.imwrite(frame_path, frame)
                frame_paths.append(frame_path)
                main_ui.frame_paths.append(frame_path)
                logger.debug(f"Frame {i} extracted successfully: {frame_path}")
            else:
                logger.error(f"Failed to read frame at position {frame_pos}")
        
        # Release video capture
        cap.release()
        
        # Display frames
        if frame_paths:
            logger.debug(f"Displaying {len(frame_paths)} frames from OpenCV")
            display_video_frames_from_paths(main_ui, frame_paths)
        else:
            logger.error("No frames were extracted from the video")
        
    except Exception as e:
        logger.error(f"Error displaying video frames: {str(e)}")
        logger.error(traceback.format_exc())

def display_video_frames_from_paths(main_ui, frame_paths):
    """
    Display video frames from a list of image paths
    
    Args:
        main_ui: MainUI instance
        frame_paths: List of paths to frame images
    """
    if not hasattr(main_ui, 'video_frames') or not frame_paths:
        logger.debug("No video frames widget or frame paths found")
        return
    
    try:
        logger.debug(f"Displaying {len(frame_paths)} frames from paths")
        
        # Get frames from video frames UI container
        for i in range(min(5, len(frame_paths))):
            # Get frame widget
            frame_widget = main_ui.video_frames.findChild(QtWidgets.QFrame, f"frame{i+1}")
            if not frame_widget:
                logger.error(f"Frame widget {i+1} not found")
                continue
            
            # Get frame path
            frame_path = frame_paths[i]
            logger.debug(f"Loading frame {i+1} from: {frame_path}")
            
            # Create or get layout for frame widget
            layout = frame_widget.layout()
            if layout is None:
                layout = QtWidgets.QVBoxLayout(frame_widget)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setAlignment(Qt.AlignCenter)
            else:
                # Clear existing layout
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
            
            # Create label for frame image
            label = QtWidgets.QLabel()
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("background: transparent;")
            
            # Load image into pixmap
            pixmap = QtGui.QPixmap(frame_path)
            if not pixmap.isNull():
                logger.debug(f"Frame image loaded successfully: {frame_path}")
                # Scale pixmap to fit frame size while maintaining aspect ratio
                frame_size = frame_widget.size()
                scaled_pixmap = pixmap.scaled(
                    frame_size.width(),
                    frame_size.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                label.setPixmap(scaled_pixmap)
                label.setMinimumSize(frame_size)
            else:
                logger.error(f"Failed to load frame image: {frame_path}")
                label.setText("Error loading")
            
            # Add label to layout
            layout.addWidget(label)
            
            # Make frame clickable
            frame_widget.mousePressEvent = lambda event, path=frame_path: show_frame_fullscreen(main_ui, path)
            
            # Set cursor to pointing hand
            frame_widget.setCursor(QtCore.Qt.PointingHandCursor)
            
            logger.debug(f"Frame {i+1} displayed successfully")
    
    except Exception as e:
        logger.error(f"Error displaying video frames from paths: {str(e)}")
        logger.error(traceback.format_exc())

def show_frame_fullscreen(main_ui, frame_path):
    """
    Shows a frame in a larger dialog
    
    Args:
        main_ui: MainUI instance
        frame_path: Path to frame image
    """
    if not os.path.exists(frame_path):
        logger.error(f"Frame file does not exist: {frame_path}")
        return
        
    try:
        # Import gallery integration if available
        try:
            from ui.components.gallery_integration import open_gallery_modal
            # Use the gallery modal to show image
            if hasattr(main_ui, 'frame_paths') and main_ui.frame_paths:
                index = main_ui.frame_paths.index(frame_path) if frame_path in main_ui.frame_paths else 0
                open_gallery_modal(main_ui.frame_paths, index)
                return
        except ImportError:
            logger.debug("Gallery integration not available, using fallback dialog")
        
        # Create dialog
        dialog = QtWidgets.QDialog(main_ui)
        dialog.setWindowTitle("Frame Preview")
        dialog.setMinimumSize(800, 600)
        
        # Create layout
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Create label for image
        label = QtWidgets.QLabel()
        label.setAlignment(Qt.AlignCenter)
        
        # Load image
        pixmap = QtGui.QPixmap(frame_path)
        
        # Scale to fit dialog
        pixmap = pixmap.scaled(
            dialog.width() - 20, 
            dialog.height() - 60, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # Set image
        label.setPixmap(pixmap)
        
        # Add to layout
        layout.addWidget(label)
        
        # Add close button
        button = QtWidgets.QPushButton("Đóng")
        button.clicked.connect(dialog.accept)
        layout.addWidget(button, alignment=Qt.AlignCenter)
        
        # Show dialog
        dialog.exec_()
        
    except Exception as e:
        logger.error(f"Error showing frame fullscreen: {str(e)}")
        logger.error(traceback.format_exc())

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
    dialog.setWindowModality(Qt.WindowModal)
    
    if not cancellable:
        dialog.setCancelButton(None)
    
    return dialog