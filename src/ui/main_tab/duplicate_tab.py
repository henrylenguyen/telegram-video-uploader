"""
Duplicate videos tab module
"""
import tkinter as tk
from tkinter import ttk

def create_duplicate_tab(app, parent):
    """
    Tạo giao diện tab danh sách video trùng
    
    Args:
        app: Đối tượng TelegramUploaderApp
        parent: Frame cha
    """
    # Hiển thị thông báo "Đang phát triển"
    ttk.Label(parent, text="Nội dung của tab Danh sách video trùng").pack(pady=20)
    # Ở đây sẽ hiển thị danh sách các video trùng lặp đã phát hiện