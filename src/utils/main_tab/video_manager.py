"""
Video management utilities for the main tab in PyQt5 UI.
"""
import os
import logging
import cv2
import hashlib
from PyQt5 import QtWidgets, QtCore, QtGui

logger = logging.getLogger("VideoManager")

def refresh_video_list(main_ui, folder_path):
    """
    Refreshes the list of videos from the specified folder
    
    Args:
        main_ui: MainUI instance
        folder_path: Path to folder containing videos
        
    Returns:
        list: List of video file info dictionaries
    """
    if not folder_path or not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        logger.error(f"Invalid folder path: {folder_path}")
        QtWidgets.QMessageBox.warning(main_ui, "Lỗi", "Thư mục không hợp lệ hoặc không tồn tại!")
        return []
    
    # Scan folder for videos
    videos = scan_folder_for_videos(folder_path)
    
    if not videos:
        # Update UI to show no videos
        logger.info("No videos found in folder")
        # Update folder stats in UI
        if hasattr(main_ui, 'folder_stats_label'):
            main_ui.folder_stats_label.setText(f"Tổng dung lượng: 0 B | 0 videos")
        return []
    
    # Check for duplicates if enabled
    if hasattr(main_ui, 'duplicate_check_box') and main_ui.duplicate_check_box is not None and main_ui.duplicate_check_box.isChecked():
        videos = check_duplicates(main_ui, videos)
    
    # Check upload history if enabled
    if hasattr(main_ui, 'history_check_box') and main_ui.history_check_box is not None and main_ui.history_check_box.isChecked():
        videos = check_upload_history(main_ui, videos)
    
    # Update folder stats in UI
    total_size = sum(video.get("file_size_bytes", 0) for video in videos)
    size_str = format_file_size(total_size)
    
    if hasattr(main_ui, 'folder_stats_label'):
        main_ui.folder_stats_label.setText(f"Tổng dung lượng: {size_str} | {len(videos)} videos")
    
    logger.info(f"Found {len(videos)} videos in {folder_path}")
    return videos

def scan_folder_for_videos(folder_path):
    """
    Scans a folder for video files
    
    Args:
        folder_path: Path to folder
        
    Returns:
        list: List of video file info dictionaries
    """
    if not folder_path or not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        logger.error(f"Invalid folder path: {folder_path}")
        return []
    
    # List of common video extensions
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg']
    
    video_files = []
    
    try:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in video_extensions:
                    # Get file size
                    file_size = os.path.getsize(file_path)
                    
                    # Get video info
                    video_info = {
                        "name": file,
                        "path": file_path,
                        "status": "new",  # Default status (new, duplicate, uploaded)
                        "info": "",
                        "selected": False,
                        "file_size_bytes": file_size
                    }
                    
                    # Try to get more info with OpenCV
                    try:
                        cap = cv2.VideoCapture(file_path)
                        if cap.isOpened():
                            # Get video properties
                            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            fps = cap.get(cv2.CAP_PROP_FPS)
                            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                            duration = frame_count / fps if fps > 0 else 0
                            
                            # Format duration string
                            hours = int(duration // 3600)
                            minutes = int((duration % 3600) // 60)
                            seconds = int(duration % 60)
                            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                            
                            # Update video info
                            video_info.update({
                                "width": width,
                                "height": height,
                                "resolution": f"{width}x{height}",
                                "fps": fps,
                                "frame_count": frame_count,
                                "duration": duration,
                                "duration_str": duration_str,
                            })
                            
                            # Release capture
                            cap.release()
                    except Exception as e:
                        logger.error(f"Error getting video info for {file_path}: {str(e)}")
                    
                    # Format file size
                    video_info["file_size"] = format_file_size(file_size)
                    
                    # Add to video list
                    video_files.append(video_info)
    except Exception as e:
        logger.error(f"Error scanning folder {folder_path}: {str(e)}")
    
    return video_files

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
        file_size_str = format_file_size(file_size)
        
        # Format duration string
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Calculate hash for duplication/upload history check
        video_hash = calculate_video_hash(video_path)
        
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
            "format": os.path.splitext(video_path)[1].upper().replace(".", ""),
            "hash": video_hash
        }
    except Exception as e:
        logger.error(f"Error getting video info for {video_path}: {str(e)}")
        return {}

def calculate_video_hash(video_path, sample_size=64*1024):
    """
    Calculates a hash for a video file using sampling to speed up the process
    
    Args:
        video_path: Path to the video file
        sample_size: Size of the sample to use for hashing (in bytes)
        
    Returns:
        str: Hash string
    """
    if not os.path.exists(video_path):
        return None
    
    try:
        file_size = os.path.getsize(video_path)
        
        # For very small files, just hash the whole file
        if file_size <= sample_size * 3:
            with open(video_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        
        # For larger files, sample from beginning, middle and end
        hash_md5 = hashlib.md5()
        
        with open(video_path, 'rb') as f:
            # Read from the beginning
            hash_md5.update(f.read(sample_size))
            
            # Read from the middle
            f.seek(file_size // 2)
            hash_md5.update(f.read(sample_size))
            
            # Read from the end
            f.seek(max(0, file_size - sample_size))
            hash_md5.update(f.read(sample_size))
        
        return hash_md5.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating video hash: {str(e)}")
        return None

def format_file_size(size_in_bytes):
    """
    Formats a file size in bytes to a human-readable string
    
    Args:
        size_in_bytes: File size in bytes
        
    Returns:
        str: Formatted file size string
    """
    # Convert to KB
    size_kb = size_in_bytes / 1024.0
    
    # Less than 1MB
    if size_kb < 1024:
        return f"{size_kb:.1f} KB"
    
    # Convert to MB
    size_mb = size_kb / 1024.0
    
    # Less than 1GB
    if size_mb < 1024:
        return f"{size_mb:.1f} MB"
    
    # Convert to GB
    size_gb = size_mb / 1024.0
    return f"{size_gb:.2f} GB"

def check_duplicates(main_ui, videos):
    """
    Checks for duplicate videos in the list
    
    Args:
        main_ui: MainUI instance
        videos: List of video info dictionaries
        
    Returns:
        list: Updated list of video info dictionaries
    """
    logger.info("Checking for duplicate videos")
    
    # Create a dictionary to track video hashes for duplicates
    video_hashes = {}
    duplicate_groups = []
    
    # First pass: generate hashes and find duplicates
    for i, video in enumerate(videos):
        video_path = video["path"]
        video_hash = calculate_video_hash(video_path)
        
        if video_hash:
            # Store hash in video info
            videos[i]["hash"] = video_hash
            
            # Check if this hash already exists
            if video_hash in video_hashes:
                # This is a duplicate
                videos[i]["status"] = "duplicate"
                videos[i]["duplicate_of"] = video_hashes[video_hash]
                
                # Find or create a duplicate group
                found_group = False
                for group in duplicate_groups:
                    if video_hashes[video_hash] in group:
                        group.append(video_path)
                        found_group = True
                        break
                
                if not found_group:
                    duplicate_groups.append([video_hashes[video_hash], video_path])
            else:
                # This is the first occurrence
                video_hashes[video_hash] = video_path
    
    # Second pass: update duplicate info
    for i, video in enumerate(videos):
        if video["status"] == "duplicate":
            # Find the duplicate group containing this video
            for group in duplicate_groups:
                if video["path"] in group:
                    # Find other videos in the same group
                    other_videos = [os.path.basename(path) for path in group if path != video["path"]]
                    
                    # Create info text
                    info = f"Trùng với: {', '.join(other_videos[:2])}"
                    if len(other_videos) > 2:
                        info += f" và {len(other_videos)-2} video khác"
                    
                    videos[i]["info"] = info
                    break
    
    logger.info(f"Found {sum(1 for v in videos if v['status'] == 'duplicate')} duplicate videos")
    return videos

def check_upload_history(main_ui, videos):
    """
    Checks which videos have already been uploaded
    
    Args:
        main_ui: MainUI instance
        videos: List of video info dictionaries
        
    Returns:
        list: Updated list of video info dictionaries
    """
    logger.info("Checking upload history")
    
    # If app instance has upload_history, use it
    if hasattr(main_ui, 'app') and hasattr(main_ui.app, 'upload_history'):
        upload_history = main_ui.app.upload_history
        
        for i, video in enumerate(videos):
            video_hash = video.get("hash")
            if not video_hash:
                video_hash = calculate_video_hash(video["path"])
                videos[i]["hash"] = video_hash
            
            if video_hash and upload_history.is_uploaded(video_hash):
                videos[i]["status"] = "uploaded"
                
                # Get upload date if available
                upload_info = upload_history.get_upload_by_hash(video_hash)
                if upload_info and "upload_date" in upload_info:
                    videos[i]["info"] = f"Đã tải lên vào {upload_info['upload_date']}"
                else:
                    videos[i]["info"] = "Đã tải lên trước đó"
    
    logger.info(f"Found {sum(1 for v in videos if v['status'] == 'uploaded')} previously uploaded videos")
    return videos

def select_all_videos(main_ui):
    """
    Selects all videos in the list
    
    Args:
        main_ui: MainUI instance
    """
    if hasattr(main_ui, 'video_list'):
        # Update all checkboxes in the UI
        for i in range(1, 11):  # Assuming we have up to 10 videos displayed at once
            checkbox = main_ui.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
            row = main_ui.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
            if checkbox and row and row.isVisible():
                checkbox.setChecked(True)
    logger.info("Selected all videos")

def deselect_all_videos(main_ui):
    """
    Deselects all videos in the list
    
    Args:
        main_ui: MainUI instance
    """
    if hasattr(main_ui, 'video_list'):
        # Update all checkboxes in the UI
        for i in range(1, 11):
            checkbox = main_ui.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
            if checkbox:
                checkbox.setChecked(False)
    logger.info("Deselected all videos")

def select_unuploaded_videos(main_ui):
    """
    Selects only videos that haven't been uploaded yet
    
    Args:
        main_ui: MainUI instance
    """
    if hasattr(main_ui, 'video_list'):
        # Update checkboxes based on upload status
        for i in range(1, 11):
            status_label = main_ui.video_list.findChild(QtWidgets.QLabel, f"status{i}")
            checkbox = main_ui.video_list.findChild(QtWidgets.QCheckBox, f"checkBox{i}")
            row = main_ui.video_list.findChild(QtWidgets.QFrame, f"videoItem{i}")
            
            if status_label and checkbox and row and row.isVisible():
                # Check if the status is not "uploaded" (Đã tải)
                is_uploaded = status_label.text() == "Đã tải"
                checkbox.setChecked(not is_uploaded)
    logger.info("Selected unuploaded videos")