"""
Module tạo và quản lý tab hướng dẫn.
"""
import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger("GuideTab")

def create_guide_tab(app, parent):
    """
    Tạo giao diện cho tab hướng dẫn
    
    Args:
        app: Đối tượng TelegramUploaderApp
        parent: Frame cha
    """
    # Tiêu đề
    ttk.Label(
        parent, 
        text="Hướng dẫn sử dụng", 
        style="Heading.TLabel"
    ).pack(pady=10)
    
    # Tạo frame cho text có thể cuộn
    guide_frame = ttk.Frame(parent)
    guide_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Text widget với thanh cuộn
    guide_text = tk.Text(guide_frame, wrap=tk.WORD, padx=15, pady=15, font=("Arial", 10))
    guide_scrollbar = ttk.Scrollbar(guide_frame, orient=tk.VERTICAL, command=guide_text.yview)
    guide_text.configure(yscrollcommand=guide_scrollbar.set)
    
    # Sắp xếp
    guide_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    guide_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Nội dung hướng dẫn
    guide_content = """
# Hướng dẫn sử dụng Telegram Video Uploader

## Giới thiệu
Telegram Video Uploader là ứng dụng giúp bạn dễ dàng tải lên nhiều video lên Telegram, với các tính năng kiểm tra trùng lặp, theo dõi lịch sử tải lên, và tự động tải lên video mới.

## Các tính năng chính

### 1. Tải lên video
- Chọn thư mục chứa video
- Kiểm tra video trùng lặp
- Kiểm tra video đã tải lên trước đó
- Tải lên thủ công một hoặc nhiều video
- Xem thông tin chi tiết về video đã chọn

### 2. Tự động tải lên
- Thiết lập thư mục giám sát
- Tự động tải lên video mới
- Tải lên hàng loạt các video trong thư mục

### 3. Quản lý lịch sử
- Theo dõi các video đã tải lên
- Tìm kiếm video trong lịch sử
- Xem thông tin chi tiết về video đã tải

### 4. Xử lý video lớn
- Tự động chia nhỏ video lớn hơn 50MB
- Hỗ trợ tải lên video không giới hạn kích thước qua Telethon API

## Hướng dẫn chi tiết

### Cài đặt ban đầu
1. Vào tab "Cài đặt" để thiết lập thông tin Bot Telegram
2. Nhập Bot Token và Chat ID
3. Kiểm tra kết nối để đảm bảo thông tin chính xác

### Tải lên video
1. Chọn thư mục chứa video qua nút "Duyệt..."
2. Danh sách video sẽ hiển thị với các thông tin trạng thái
3. Đánh dấu chọn các video cần tải lên
4. Nhấn "Bắt đầu tải lên" để tải các video đã chọn

### Xem thông tin video
1. Chọn một video trong danh sách
2. Thông tin chi tiết sẽ hiển thị ở phần "Thông tin video đã chọn"
3. Các khung hình từ video sẽ hiển thị bên dưới
4. Bạn có thể xem video bằng cách nhấn nút "Xem video"

### Sử dụng tự động tải lên
1. Chuyển đến tab "Tự động"
2. Chọn thư mục cần giám sát
3. Thiết lập các tùy chọn kiểm tra
4. Nhấn "Bắt đầu tự động" để bắt đầu theo dõi và tải lên

## Lưu ý

- Các video đã tải lên sẽ được đánh dấu màu xanh nhạt
- Các video trùng lặp sẽ được đánh dấu màu đỏ nhạt
- Bot Telegram có giới hạn tải file tối đa 50MB, video lớn hơn sẽ được tự động xử lý
- Để tải video lớn hơn 50MB mà không chia nhỏ, hãy sử dụng Telethon API (được cấu hình trong tab Cài đặt)

## Liên hệ hỗ trợ

Nếu bạn cần hỗ trợ thêm, vui lòng liên hệ:
- Email: support@henlladev.com
- Telegram: @HenlladevSupport
"""
    
    # Chèn văn bản vào widget
    guide_text.insert(tk.END, guide_content)
    
    # Thiết lập các tag để định dạng
    guide_text.tag_configure("heading1", font=("Arial", 16, "bold"))
    guide_text.tag_configure("heading2", font=("Arial", 14, "bold"))
    guide_text.tag_configure("heading3", font=("Arial", 12, "bold"))
    guide_text.tag_configure("normal", font=("Arial", 10))
    guide_text.tag_configure("bullet", font=("Arial", 10), lmargin1=20, lmargin2=30)
    
    # Đặt thành chỉ đọc
    guide_text.config(state=tk.DISABLED)