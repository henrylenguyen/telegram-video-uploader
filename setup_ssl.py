#!/usr/bin/env python
"""
Script cài đặt và cấu hình SSL cho Python.
Sử dụng: python setup_ssl.py
"""
import os
import sys
import platform
import logging
import subprocess
import webbrowser
import time
import ctypes
import traceback

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("setup_ssl.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("setup_ssl")

def is_admin():
    """Kiểm tra xem script có đang chạy với quyền admin không."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def check_python_installation():
    """Kiểm tra và xác nhận cài đặt Python hiện tại."""
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python executable: {sys.executable}")
    python_path = os.path.dirname(sys.executable)
    logger.info(f"Python path: {python_path}")
    
    # Kiểm tra DLL paths
    dll_paths = []
    for path in os.environ.get('PATH', '').split(os.pathsep):
        if os.path.exists(path) and any(file.lower().startswith('python') for file in os.listdir(path) if file.lower().endswith('.dll')):
            dll_paths.append(path)
    
    if dll_paths:
        logger.info(f"Python DLL paths: {', '.join(dll_paths)}")
    else:
        logger.warning("Không tìm thấy đường dẫn DLL Python trong PATH")
    
    return python_path

def find_ssl_libraries():
    """Tìm thư viện SSL hiện có trên hệ thống."""
    ssl_paths = []
    search_paths = [
        "C:\\Program Files\\OpenSSL-Win64",
        "C:\\Program Files\\OpenSSL",
        "C:\\Program Files (x86)\\OpenSSL-Win32",
        "C:\\OpenSSL-Win64",
        "C:\\OpenSSL-Win32"
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            ssl_paths.append(path)
            
    return ssl_paths

def install_openssl_automatic():
    """Cài đặt OpenSSL tự động."""
    try:
        logger.info("Đang tải và cài đặt OpenSSL...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyopenssl", "cryptography"])
        logger.info("Đã cài đặt thành công thư viện Python cho OpenSSL")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi cài đặt OpenSSL: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def open_openssl_website():
    """Mở trang web để tải OpenSSL thủ công."""
    webbrowser.open("https://slproweb.com/products/Win32OpenSSL.html")
    logger.info("Đã mở trang tải OpenSSL. Vui lòng tải và cài đặt phiên bản phù hợp.")
    input("Nhấn Enter sau khi cài đặt xong OpenSSL...")

def copy_ssl_libraries(source_path, python_path):
    """Sao chép thư viện SSL vào thư mục Python."""
    try:
        # Tìm các file DLL cần thiết
        libssl_paths = []
        libcrypto_paths = []
        
        for root, _, files in os.walk(source_path):
            for file in files:
                lower_file = file.lower()
                if lower_file.startswith('libssl') and lower_file.endswith('.dll'):
                    libssl_paths.append(os.path.join(root, file))
                elif lower_file.startswith('libcrypto') and lower_file.endswith('.dll'):
                    libcrypto_paths.append(os.path.join(root, file))
        
        if not libssl_paths or not libcrypto_paths:
            logger.error(f"Không tìm thấy thư viện SSL cần thiết trong {source_path}")
            return False
        
        # Sao chép các thư viện
        for src_path in libssl_paths + libcrypto_paths:
            filename = os.path.basename(src_path)
            dst_path = os.path.join(python_path, filename)
            logger.info(f"Sao chép {src_path} đến {dst_path}")
            
            # Tạo bản sao lưu nếu đã tồn tại
            if os.path.exists(dst_path):
                backup_path = dst_path + ".bak"
                logger.info(f"Tạo bản sao lưu của {dst_path} tại {backup_path}")
                os.rename(dst_path, backup_path)
                
            # Sao chép file
            with open(src_path, 'rb') as fsrc:
                with open(dst_path, 'wb') as fdst:
                    fdst.write(fsrc.read())
        
        logger.info(f"Đã sao chép thành công thư viện SSL vào {python_path}")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi sao chép thư viện SSL: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_ssl():
    """Kiểm tra xem SSL có hoạt động không."""
    try:
        import ssl
        logger.info(f"SSL version: {ssl.OPENSSL_VERSION}")
        return True
    except ImportError:
        logger.error("Không thể import module ssl")
        return False
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra SSL: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Chức năng chính của script."""
    logger.info("=== Bắt đầu thiết lập SSL cho Python ===")
    
    # Kiểm tra OS
    if platform.system() != "Windows":
        logger.error("Script này chỉ hỗ trợ Windows")
        return
    
    # Kiểm tra quyền admin
    if not is_admin():
        logger.warning("Script này cần quyền admin để chạy đúng cách")
        if input("Bạn có muốn tiếp tục không? (y/n): ").lower() != 'y':
            return
    
    # Kiểm tra cài đặt Python
    python_path = check_python_installation()
    
    # Thử import SSL
    if test_ssl():
        logger.info("SSL đã được cài đặt và hoạt động bình thường")
        if input("Bạn có muốn tiếp tục cài đặt không? (y/n): ").lower() != 'y':
            return
    
    # Menu lựa chọn
    print("\n=== Menu cài đặt SSL ===")
    print("1. Cài đặt SSL tự động (pip)")
    print("2. Tải OpenSSL thủ công")
    print("3. Sao chép thư viện SSL từ vị trí có sẵn")
    print("4. Thoát")
    
    choice = input("Lựa chọn của bạn (1-4): ")
    
    if choice == '1':
        # Cài đặt tự động
        success = install_openssl_automatic()
        if success:
            logger.info("Đã cài đặt thành công các gói Python cho SSL")
        else:
            logger.error("Cài đặt tự động thất bại, vui lòng thử cách khác")
    
    elif choice == '2':
        # Tải thủ công
        open_openssl_website()
        ssl_paths = find_ssl_libraries()
        
        if not ssl_paths:
            logger.error("Không tìm thấy thư viện OpenSSL sau khi cài đặt")
            return
        
        print("\nĐã tìm thấy các thư viện OpenSSL:")
        for i, path in enumerate(ssl_paths, 1):
            print(f"{i}. {path}")
        
        idx = int(input(f"Chọn đường dẫn để sao chép thư viện (1-{len(ssl_paths)}): ")) - 1
        if 0 <= idx < len(ssl_paths):
            copy_ssl_libraries(ssl_paths[idx], python_path)
    
    elif choice == '3':
        # Sao chép từ vị trí có sẵn
        ssl_paths = find_ssl_libraries()
        
        if ssl_paths:
            print("\nĐã tìm thấy các thư viện OpenSSL:")
            for i, path in enumerate(ssl_paths, 1):
                print(f"{i}. {path}")
            
            idx = int(input(f"Chọn đường dẫn để sao chép thư viện (1-{len(ssl_paths)}) hoặc 0 để nhập thủ công: ")) - 1
            
            if idx == -1:
                custom_path = input("Nhập đường dẫn đến thư mục OpenSSL: ")
                if os.path.exists(custom_path):
                    copy_ssl_libraries(custom_path, python_path)
                else:
                    logger.error(f"Đường dẫn không tồn tại: {custom_path}")
            elif 0 <= idx < len(ssl_paths):
                copy_ssl_libraries(ssl_paths[idx], python_path)
        else:
            custom_path = input("Không tìm thấy thư viện OpenSSL. Nhập đường dẫn thủ công: ")
            if os.path.exists(custom_path):
                copy_ssl_libraries(custom_path, python_path)
            else:
                logger.error(f"Đường dẫn không tồn tại: {custom_path}")
    
    elif choice == '4':
        # Thoát
        logger.info("Đã hủy cài đặt SSL")
        return
    
    else:
        logger.error("Lựa chọn không hợp lệ")
        return
    
    # Kiểm tra lại
    time.sleep(1)  # Đợi để đảm bảo các thay đổi được áp dụng
    if test_ssl():
        logger.info("=== Thiết lập SSL thành công! ===")
    else:
        logger.error("=== Thiết lập SSL thất bại, vui lòng thử lại ===")
        logger.info("Bạn có thể cần khởi động lại ứng dụng hoặc máy tính")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Lỗi không mong muốn: {str(e)}")
        logger.error(traceback.format_exc())
    
    input("Nhấn Enter để thoát...") 