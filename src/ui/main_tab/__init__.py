"""
Main tab module for Telegram Video Uploader
"""
from .main_tab_ui import create_main_tab
from .main_tab_func import (
    refresh_video_list,
    update_table_content,
    browse_folder,
    on_video_tree_click,
    on_video_select,
    select_all_videos,
    deselect_all_videos,
    select_unuploaded_videos,  # Add this new function
    change_page,
    play_selected_video,
    upload_selected_video
)