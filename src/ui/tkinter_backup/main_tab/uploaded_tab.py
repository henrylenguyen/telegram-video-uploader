"""
Uploaded videos tab module
"""
import tkinter as tk
from tkinter import ttk

def create_uploaded_tab(app, parent):
    """
    Tạo giao diện tab danh sách video đã tải lên
    
    Args:
        app: Đối tượng TelegramUploaderApp
        parent: Frame cha
    """
    # Hiển thị thông báo "Đang phát triển"
    ttk.Label(parent, text="Nội dung của tab Danh sách video đã tải lên").pack(pady=20)
    # Ở đây sẽ hiển thị danh sách video đã tải lên từ lịch sử