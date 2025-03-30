"""
Script kiểm tra các dependency cần thiết và gợi ý sửa lỗi
cho ứng dụng Telegram Video Uploader
"""
import os
import sys
import importlib.util
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

def check_module(module_name):
    """Kiểm tra xem module đã được cài đặt chưa"""
    return importlib.util.find_spec(module_name) is not None

def install_module(module_name):
    """Cài đặt module bằng pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
        return True
    except subprocess.CalledProcessError:
        return False

def check_all_dependencies():
    """Kiểm tra tất cả các dependency cần thiết"""
    required_modules = [
        "telebot",
        "telethon",
        "pillow",
        "opencv-python",
        "imagehash",
        "tqdm",
        "configparser"
    ]
    
    missing_modules = []
    for module in required_modules:
        if not check_module(module):
            missing_modules.append(module)
    
    return missing_modules

def check_config_file():
    """Kiểm tra file config.ini có tồn tại không"""
    if not os.path.exists("config.ini"):
        return False
    return True

def create_default_config():
    """Tạo file config.ini mặc định"""
    import configparser
    
    config = configparser.ConfigParser()
    config['TELEGRAM'] = {
        'bot_token': '',
        'chat_id': '',
        'notification_chat_id': ''
    }
    config['SETTINGS'] = {
        'video_folder': '',
        'video_extensions': '.mp4,.avi,.mkv,.mov,.wmv',
        'delay_between_uploads': '5',
        'auto_mode': 'false',
        'check_duplicates': 'true',
        'auto_check_interval': '60'
    }
    config['TELETHON'] = {
        'api_id': '',
        'api_hash': '',
        'phone': '',
        'use_telethon': 'false'
    }
    
    with open('config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    
    return True

def check_utils_dir():
    """Kiểm tra thư mục utils có tồn tại không"""
    return os.path.exists("src/utils") and os.path.isdir("src/utils")

def main():
    # Kiểm tra dependencies
    missing_modules = check_all_dependencies()
    
    if missing_modules:
        # Tạo giao diện để thông báo và đề xuất cài đặt
        root = tk.Tk()
        root.title("Kiểm tra Dependencies")
        root.geometry("600x400")
        
        # Thiết lập vị trí cửa sổ vào giữa màn hình
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Frame chính
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        ttk.Label(
            main_frame, 
            text="Phát hiện thiếu các thư viện Python", 
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 10))
        
        # Thông báo
        ttk.Label(
            main_frame,
            text=f"Ứng dụng Telegram Video Uploader cần các thư viện sau nhưng chưa được cài đặt:",
            wraplength=500
        ).pack(pady=5)
        
        # Frame danh sách module
        module_frame = ttk.Frame(main_frame)
        module_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Tạo Listbox hiển thị các module thiếu
        module_list = tk.Listbox(module_frame, width=50, height=10)
        module_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Thêm thanh cuộn
        scrollbar = ttk.Scrollbar(module_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Liên kết
        module_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=module_list.yview)
        
        # Thêm các module vào listbox
        for module in missing_modules:
            module_list.insert(tk.END, module)
        
        # Label hướng dẫn
        ttk.Label(
            main_frame,
            text="Bạn có muốn cài đặt các thư viện này ngay bây giờ không?",
            wraplength=500
        ).pack(pady=10)
        
        # Frame nút
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        def install_dependencies():
            # Hiển thị thông báo đang cài đặt
            status_var.set("Đang cài đặt các thư viện...")
            progress['value'] = 0
            root.update_idletasks()
            
            total_modules = len(missing_modules)
            success_count = 0
            
            for i, module in enumerate(missing_modules):
                status_var.set(f"Đang cài đặt {module}...")
                progress['value'] = (i / total_modules) * 100
                root.update_idletasks()
                
                if install_module(module):
                    success_count += 1
                
                # Cập nhật thanh tiến trình
                progress['value'] = ((i + 1) / total_modules) * 100
                root.update_idletasks()
            
            if success_count == total_modules:
                messagebox.showinfo("Thành công", "Đã cài đặt tất cả các thư viện!")
                root.destroy()
            else:
                messagebox.showwarning(
                    "Cảnh báo", 
                    f"Đã cài đặt {success_count}/{total_modules} thư viện. "
                    "Vui lòng tự cài đặt các thư viện còn lại bằng lệnh: "
                    f"pip install {' '.join(missing_modules)}"
                )
        
        def open_manual():
            # Hiển thị hướng dẫn cài đặt thủ công
            manual_text = (
                "Để cài đặt thủ công các thư viện thiếu, mở Command Prompt (hoặc Terminal) "
                "và chạy lệnh sau:\n\n"
                f"pip install {' '.join(missing_modules)}\n\n"
                "Hoặc sử dụng file requirements.txt:\n\n"
                "pip install -r requirements.txt"
            )
            
            # Tạo cửa sổ mới
            manual_window = tk.Toplevel(root)
            manual_window.title("Hướng dẫn cài đặt thủ công")
            manual_window.geometry("500x300")
            manual_window.transient(root)
            
            # Frame chính
            manual_frame = ttk.Frame(manual_window, padding=20)
            manual_frame.pack(fill=tk.BOTH, expand=True)
            
            # Text widget
            text = tk.Text(manual_frame, wrap=tk.WORD, width=60, height=10)
            text.pack(fill=tk.BOTH, expand=True)
            text.insert(tk.END, manual_text)
            text.config(state=tk.DISABLED)
            
            # Nút sao chép
            def copy_to_clipboard():
                command = f"pip install {' '.join(missing_modules)}"
                root.clipboard_clear()
                root.clipboard_append(command)
                copy_btn.config(text="Đã sao chép!")
                manual_window.after(1500, lambda: copy_btn.config(text="Sao chép lệnh"))
            
            copy_btn = ttk.Button(manual_frame, text="Sao chép lệnh", command=copy_to_clipboard)
            copy_btn.pack(pady=10)
            
            # Nút đóng
            ttk.Button(manual_frame, text="Đóng", command=manual_window.destroy).pack(pady=5)
        
        # Nút cài đặt
        install_btn = ttk.Button(btn_frame, text="Cài đặt", command=install_dependencies)
        install_btn.pack(side=tk.LEFT, padx=5)
        
        # Nút cài đặt thủ công
        manual_btn = ttk.Button(btn_frame, text="Hướng dẫn cài đặt thủ công", command=open_manual)
        manual_btn.pack(side=tk.RIGHT, padx=5)
        
        # Thanh tiến trình
        progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        progress.pack(fill=tk.X, pady=10)
        
        # Nhãn trạng thái
        status_var = tk.StringVar(value="Chờ thao tác...")
        status_label = ttk.Label(main_frame, textvariable=status_var)
        status_label.pack(pady=5)
        
        root.mainloop()
        return False
    
    # Kiểm tra thư mục utils
    if not check_utils_dir():
        print("ERROR: Không tìm thấy thư mục src/utils. Vui lòng đảm bảo bạn đang chạy script từ thư mục gốc của dự án.")
        return False
    
    # Kiểm tra file config
    if not check_config_file():
        print("WARNING: Không tìm thấy file config.ini. Đang tạo file config mặc định...")
        if create_default_config():
            print("SUCCESS: Đã tạo file config.ini mặc định.")
        else:
            print("ERROR: Không thể tạo file config.ini.")
            return False
    
    return True

if __name__ == "__main__":
    if main():
        print("SUCCESS: Đã kiểm tra tất cả các dependency và sẵn sàng khởi động ứng dụng.")
        print("Hãy chạy: python src/telegram_uploader.py")
    else:
        print("WARNING: Vui lòng giải quyết các vấn đề trên trước khi khởi động ứng dụng.")