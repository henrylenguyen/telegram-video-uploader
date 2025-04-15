"""
Auto upload tab module
"""
import tkinter as tk
from tkinter import ttk

def create_auto_tab(app, parent):
    """
    Tạo giao diện tab tải lên tự động
    
    Args:
        app: Đối tượng TelegramUploaderApp
        parent: Frame cha
    """
    # Hiển thị thông báo "Đang phát triển"
    ttk.Label(parent, text="Nội dung của tab Tải lên tự động").pack(pady=20)
    # Ở đây sẽ hiển thị cấu hình và trạng thái tải lên tự động