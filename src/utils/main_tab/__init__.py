"""
Main tab module utils for Telegram Video Uploader PyQt5 version.
"""
from .video_manager import (
    refresh_video_list,
    scan_folder_for_videos,
    get_video_info,
    check_duplicates,
    check_upload_history,
    select_all_videos,
    deselect_all_videos,
    select_unuploaded_videos
)

from .upload_manager import (
    upload_selected_videos,
    upload_single_video,
    check_duplicates_and_uploaded,
    show_upload_confirmation,
    show_upload_progress
)

from .ui_helpers import (
    display_video_frames,
    display_video_info,
    update_video_status,
    display_error_message,
    create_progress_dialog,
    clear_video_preview,
    clear_video_frames,
    update_video_preview_ui
)

__all__ = [
    'refresh_video_list',
    'scan_folder_for_videos',
    'get_video_info',
    'check_duplicates',
    'check_upload_history',
    'select_all_videos',
    'deselect_all_videos',
    'select_unuploaded_videos',
    'upload_selected_videos',
    'upload_single_video',
    'check_duplicates_and_uploaded',
    'show_upload_confirmation',
    'show_upload_progress',
    'display_video_frames',
    'display_video_info',
    'update_video_status',
    'display_error_message',
    'create_progress_dialog',
    'clear_video_preview',
    'clear_video_frames',
    'update_video_preview_ui'
]