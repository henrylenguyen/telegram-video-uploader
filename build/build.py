"""
Script đóng gói ứng dụng Telegram Video Uploader thành file .exe.
"""
import PyInstaller.__main__
import os
import shutil
import configparser
import sys
import zipfile
import datetime
import urllib.request
import subprocess
import tempfile
import platform

# Thêm thư mục gốc vào đường dẫn
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Đường dẫn các thư mục
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, 'src')
DIST_DIR = os.path.join(BASE_DIR, 'dist')
BUILD_DIR = os.path.join(BASE_DIR, 'build')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'telegram_uploader_build')

# URL tải FFmpeg cho Windows
FFMPEG_WIN_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
# Thư mục FFmpeg bên trong ứng dụng
FFMPEG_APP_DIR = os.path.join(OUTPUT_DIR, 'ffmpeg')

def clean_build_dirs():
    """Xóa các thư mục build cũ"""
    print("Đang xóa thư mục build cũ...")
    
    # Xóa thư mục build và dist cũ nếu tồn tại
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        
    # Tạo thư mục output và temp
    os.makedirs(OUTPUT_DIR)
    os.makedirs(os.path.join(OUTPUT_DIR, 'config'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'docs'), exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

def download_ffmpeg():
    """Tải và chuẩn bị FFmpeg để tích hợp vào ứng dụng"""
    print("Đang tải và chuẩn bị FFmpeg...")
    
    # Tạo thư mục FFmpeg trong ứng dụng
    os.makedirs(FFMPEG_APP_DIR, exist_ok=True)
    
    # Đường dẫn tải về
    zip_path = os.path.join(TEMP_DIR, "ffmpeg.zip")
    
    try:
        # Tải FFmpeg
        print("Đang tải FFmpeg từ GitHub...")
        urllib.request.urlretrieve(FFMPEG_WIN_URL, zip_path)
        
        # Giải nén
        print("Đang giải nén FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(TEMP_DIR)
        
        # Tìm thư mục ffmpeg (thư mục có tên bắt đầu bằng ffmpeg)
        for item in os.listdir(TEMP_DIR):
            if os.path.isdir(os.path.join(TEMP_DIR, item)) and item.startswith('ffmpeg'):
                ffmpeg_dir = os.path.join(TEMP_DIR, item)
                
                # Sao chép các file cần thiết (chỉ bin)
                bin_dir = os.path.join(ffmpeg_dir, 'bin')
                for file in os.listdir(bin_dir):
                    if file in ['ffmpeg.exe', 'ffprobe.exe']:
                        src = os.path.join(bin_dir, file)
                        dst = os.path.join(FFMPEG_APP_DIR, file)
                        shutil.copy2(src, dst)
                        print(f"Đã sao chép {file} vào thư mục ffmpeg")
                break
        
        # Xóa file tạm
        if os.path.exists(zip_path):
            os.remove(zip_path)
            
        print("Đã chuẩn bị FFmpeg thành công")
    except Exception as e:
        print(f"Lỗi khi tải FFmpeg: {e}")
        # Tạo file readme để hướng dẫn cài đặt thủ công
        with open(os.path.join(FFMPEG_APP_DIR, 'README.txt'), 'w', encoding='utf-8') as f:
            f.write("Không thể tải tự động FFmpeg.\n")
            f.write("Vui lòng tải thủ công từ: https://ffmpeg.org/download.html\n")
            f.write("Sau đó sao chép ffmpeg.exe và ffprobe.exe vào thư mục này.\n")

def create_config_template():
    """Tạo file config.ini mẫu"""
    print("Đang tạo file config.ini mẫu...")
    
    # Tạo file config.ini trống hoặc mẫu nếu chưa tồn tại
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
    
    # Lưu vào thư mục output
    with open(os.path.join(OUTPUT_DIR, 'config.ini'), 'w') as configfile:
        config.write(configfile)

def build_main_application():
    """Đóng gói ứng dụng chính"""
    print("Đang đóng gói ứng dụng chính...")
    
    # Icon cho ứng dụng
    icon_path = os.path.join(SRC_DIR, 'icon.ico')
    if not os.path.exists(icon_path):
        icon_path = os.path.join(BUILD_DIR, 'icon.ico')
    
    # Kiểm tra xem icon có tồn tại không
    icon_param = f'--icon={icon_path}' if os.path.exists(icon_path) else ''
    
    # Đường dẫn tới file chính
    main_py = os.path.join(SRC_DIR, 'telegram_uploader.py')
    
    # Tìm thư viện python
    python_lib = os.path.dirname(os.__file__)
    
    # Sử dụng PyInstaller để đóng gói
    PyInstaller.__main__.run([
        main_py,  # Tên file chính của ứng dụng
        '--name=Telegram_Video_Uploader',  # Tên ứng dụng
        '--onefile',  # Đóng gói thành một file duy nhất
        '--windowed',  # Chế độ cửa sổ (không hiển thị console)
        icon_param,  # Icon cho ứng dụng
        '--hidden-import=telebot',  # Import ẩn
        '--hidden-import=PIL',  # Import ẩn
        '--hidden-import=cv2',  # Import ẩn
        '--hidden-import=imagehash',  # Import ẩn
        '--add-data=src/utils/*.py;utils',  # Thêm các modules
        '--clean',  # Xóa các file tạm
    ])

def build_config_tool():
    """Đóng gói công cụ cấu hình"""
    print("Đang đóng gói công cụ cấu hình...")
    
    # Icon cho ứng dụng
    icon_path = os.path.join(SRC_DIR, 'icon.ico')
    if not os.path.exists(icon_path):
        icon_path = os.path.join(BUILD_DIR, 'icon.ico')
        
    # Kiểm tra xem icon có tồn tại không
    icon_param = f'--icon={icon_path}' if os.path.exists(icon_path) else ''
    
    # Đường dẫn tới file chính
    main_py = os.path.join(SRC_DIR, 'telegram_uploader.py')
    
    # Tạo thư mục đầu ra riêng
    config_dist = os.path.join(DIST_DIR, 'config')
    os.makedirs(config_dist, exist_ok=True)
    
    # Sử dụng PyInstaller để đóng gói
    PyInstaller.__main__.run([
        main_py,  # Tên file chính của ứng dụng
        '--name=Telegram_Uploader_Config',  # Tên ứng dụng
        '--onefile',  # Đóng gói thành một file duy nhất
        '--windowed',  # Chế độ cửa sổ (không hiển thị console)
        icon_param,  # Icon cho ứng dụng
        '--hidden-import=telebot',  # Import ẩn
        '--add-data=src/utils/*.py;utils',  # Thêm các modules
        '--clean',  # Xóa các file tạm
        f'--distpath={config_dist}',  # Thư mục đầu ra khác
        '--add-data=README.md;.',  # Thêm file README
    ])

def create_additional_files():
    """Tạo các file bổ sung"""
    print("Đang tạo các file bổ sung...")
    
    # Tạo file README.txt
    readme_content = """
TELEGRAM VIDEO UPLOADER
=======================

Phiên bản: 1.0
(c) 2025 - All rights reserved

Hướng dẫn sử dụng:
------------------

1. THIẾT LẬP CẤU HÌNH BAN ĐẦU:
   - Chạy file "config/Telegram_Uploader_Config.exe" để cấu hình thông tin Telegram
   - Nhập Bot Token và Chat ID (xem hướng dẫn trong ứng dụng)
   - Kiểm tra kết nối và lưu cấu hình

2. SỬ DỤNG ỨNG DỤNG CHÍNH:
   - Chạy file "Telegram_Video_Uploader.exe" để mở ứng dụng chính
   - Chọn thư mục chứa video
   - Chọn video cần tải lên và nhấn "Bắt đầu tải lên"
   - Hoặc sử dụng chế độ tự động trong tab "Tự động"

Tính năng mới:
--------------
- Phát hiện và lọc video trùng lặp
- Chế độ tự động tải lên video từ thư mục
- Hỗ trợ nhiều định dạng video phổ biến
- Giao diện thân thiện và dễ sử dụng
- Hỗ trợ tải lên video không giới hạn kích thước

Lưu ý:
------
- Bot Telegram cần có quyền gửi tin nhắn và media trong kênh/nhóm đích
- Ứng dụng đã tích hợp FFmpeg để xử lý video lớn
- Xem thêm hướng dẫn chi tiết trong thư mục docs

Liên hệ hỗ trợ:
--------------
Nếu cần hỗ trợ, vui lòng liên hệ qua:
- Email: support@example.com
- GitHub: https://github.com/username/telegram-video-uploader/issues
"""

    with open(os.path.join(OUTPUT_DIR, 'README.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_content)

    # Tạo file SETUP.bat
    setup_content = """
@echo off
echo ===================================
echo  TELEGRAM VIDEO UPLOADER - SETUP
echo ===================================
echo.
echo Đang cài đặt ứng dụng...
echo.
echo 1. Thiết lập cấu hình
echo -----------------------------------
start "" "config\\Telegram_Uploader_Config.exe"
echo.
echo Sau khi cấu hình xong, bạn có thể chạy ứng dụng chính.
echo.
pause
"""

    with open(os.path.join(OUTPUT_DIR, 'SETUP.bat'), 'w', encoding='utf-8') as f:
        f.write(setup_content)
        
    # Tạo file FFmpeg-PATH.bat để đặt đường dẫn FFmpeg
    ffmpeg_path_content = """
@echo off
echo ===================================
echo  THIẾT LẬP FFMPEG PATH
echo ===================================
echo.
echo Đang thiết lập đường dẫn FFmpeg...
SET "CURRENT_DIR=%~dp0"
SET "FFMPEG_DIR=%CURRENT_DIR%ffmpeg"

REM Thêm FFmpeg vào PATH cho phiên làm việc hiện tại
SET "PATH=%FFMPEG_DIR%;%PATH%"

REM Kiểm tra cài đặt
ffmpeg -version
if %ERRORLEVEL% NEQ 0 (
    echo Lỗi: Không thể thiết lập FFmpeg. Vui lòng kiểm tra thư mục ffmpeg.
) else (
    echo Thiết lập FFmpeg thành công!
)
echo.
echo Bạn có thể chạy ứng dụng ngay bây giờ.
echo.
pause
"""

    with open(os.path.join(OUTPUT_DIR, 'FFmpeg-PATH.bat'), 'w', encoding='utf-8') as f:
        f.write(ffmpeg_path_content)

def copy_files_to_output():
    """Sao chép các file vào thư mục output"""
    print("Đang sao chép các file vào thư mục output...")
    
    # Sao chép file .exe
    if os.path.exists(os.path.join(DIST_DIR, 'Telegram_Video_Uploader.exe')):
        shutil.copy(
            os.path.join(DIST_DIR, 'Telegram_Video_Uploader.exe'),
            os.path.join(OUTPUT_DIR, 'Telegram_Video_Uploader.exe')
        )
    
    # Sao chép file config tool
    config_exe = os.path.join(DIST_DIR, 'config', 'Telegram_Uploader_Config.exe')
    if os.path.exists(config_exe):
        shutil.copy(
            config_exe,
            os.path.join(OUTPUT_DIR, 'config', 'Telegram_Uploader_Config.exe')
        )
    
    # Sao chép tài liệu
    docs_output = os.path.join(OUTPUT_DIR, 'docs')
    if os.path.exists(DOCS_DIR):
        for doc_file in os.listdir(DOCS_DIR):
            if doc_file.endswith('.md'):
                shutil.copy(
                    os.path.join(DOCS_DIR, doc_file),
                    os.path.join(docs_output, doc_file)
                )
    
    # Tạo thư mục images trong docs nếu chưa có
    images_dir = os.path.join(docs_output, 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    # Sao chép ảnh nếu có
    source_images = os.path.join(DOCS_DIR, 'images')
    if os.path.exists(source_images):
        for img_file in os.listdir(source_images):
            shutil.copy(
                os.path.join(source_images, img_file),
                os.path.join(images_dir, img_file)
            )

def create_release_zip():
    """Tạo file ZIP để phát hành"""
    print("Đang tạo file ZIP phát hành...")
    
    # Tên file ZIP
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    zip_filename = f"Telegram_Video_Uploader_v1.0_{timestamp}.zip"
    zip_path = os.path.join(BASE_DIR, zip_filename)
    
    # Tạo file ZIP
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Thêm tất cả file trong thư mục output
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, OUTPUT_DIR)
                zipf.write(file_path, arcname)
    
    print(f"Đã tạo file phát hành: {zip_path}")

def main():
    """Hàm chính để đóng gói ứng dụng"""
    # Xóa các thư mục build cũ
    clean_build_dirs()
    
    # Tạo file config.ini mẫu
    create_config_template()
    
    # Tải và chuẩn bị FFmpeg
    download_ffmpeg()
    
    # Đóng gói ứng dụng chính
    build_main_application()
    
    # Đóng gói công cụ cấu hình
    build_config_tool()
    
    # Tạo các file bổ sung
    create_additional_files()
    
    # Sao chép các file vào thư mục output
    copy_files_to_output()
    
    # Tạo file ZIP phát hành
    create_release_zip()
    
    print("\nĐã hoàn tất quá trình đóng gói ứng dụng!")
    print(f"Các file được tạo trong thư mục: {OUTPUT_DIR}")
    print("Hướng dẫn sử dụng:")
    print("1. Phân phối file ZIP cho người dùng")
    print("2. Hướng dẫn người dùng giải nén và chạy file SETUP.bat")

if __name__ == "__main__":
    main()