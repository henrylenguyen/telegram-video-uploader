"""
Utility module để cấu hình và sửa lỗi SSL trên các nền tảng khác nhau.
"""
import os
import sys
import platform
import logging
import subprocess
import shutil
from pathlib import Path
import requests
import tempfile
import zipfile
import site

logger = logging.getLogger("SSLHelper")

def fix_ssl_on_windows():
    """
    Sửa lỗi SSL trên Windows bằng cách tự động tải về và cài đặt OpenSSL nếu cần
    """
    if platform.system() != "Windows":
        logger.debug("Không phải Windows, không cần cấu hình SSL")
        return True
    
    # Kiểm tra xem OpenSSL đã được cài đặt chưa
    try:
        import ssl
        import socket
        # Thử kết nối SSL đơn giản
        context = ssl.create_default_context()
        with socket.create_connection(("www.python.org", 443)) as sock:
            with context.wrap_socket(sock, server_hostname="www.python.org") as ssock:
                if ssock.version():
                    logger.info(f"SSL đã hoạt động: {ssock.version()}")
                    return True
    except Exception as e:
        logger.warning(f"Lỗi SSL: {str(e)}")
    
    # Kiểm tra cryptg
    try:
        import cryptg
        logger.info("Module cryptg đã được cài đặt")
    except ImportError:
        logger.warning("Module cryptg chưa được cài đặt. Sử dụng pip install cryptg để tăng tốc Telethon")
    
    # Thử kiểm tra và cài đặt OpenSSL
    return install_openssl_windows()

def install_openssl_windows():
    """
    Tự động tải và cài đặt OpenSSL trên Windows
    
    Returns:
        bool: True nếu cài đặt thành công
    """
    logger.info("Đang tải OpenSSL cho Windows...")
    
    # URL OpenSSL light installer
    openssl_url = "https://slproweb.com/download/Win64OpenSSL_Light-3_1_3.exe"
    
    try:
        # Tạo thư mục tạm
        with tempfile.TemporaryDirectory() as temp_dir:
            # Tải về installer
            installer_path = os.path.join(temp_dir, "openssl_setup.exe")
            
            logger.info(f"Đang tải OpenSSL từ {openssl_url}")
            response = requests.get(openssl_url, stream=True)
            
            if response.status_code == 200:
                with open(installer_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logger.info("Đang cài đặt OpenSSL...")
                # Chạy installer ở chế độ silent
                result = subprocess.run(
                    [installer_path, "/silent", "/verysilent", "/sp-", "/suppressmsgboxes"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                if result.returncode == 0:
                    logger.info("Đã cài đặt OpenSSL thành công")
                    
                    # Cập nhật PATH để tìm DLL
                    openssl_paths = [
                        "C:\\Program Files\\OpenSSL-Win64\\bin",
                        "C:\\Program Files (x86)\\OpenSSL-Win64\\bin"
                    ]
                    
                    for path in openssl_paths:
                        if os.path.exists(path) and path not in os.environ["PATH"]:
                            os.environ["PATH"] = path + os.pathsep + os.environ["PATH"]
                            logger.info(f"Đã thêm {path} vào PATH")
                    
                    return True
                else:
                    logger.error(f"Lỗi cài đặt OpenSSL: {result.stderr.decode('utf-8', errors='ignore')}")
            else:
                logger.error(f"Không thể tải OpenSSL, mã lỗi: {response.status_code}")
    except Exception as e:
        logger.error(f"Lỗi khi cài đặt OpenSSL: {str(e)}")
    
    # Nếu không thể cài đặt tự động, hướng dẫn người dùng cài đặt thủ công
    logger.info(
        "Không thể tự động cài đặt OpenSSL. Vui lòng:"
        "\n1. Tải OpenSSL từ https://slproweb.com/products/Win32OpenSSL.html"
        "\n2. Cài đặt vào thư mục mặc định"
        "\n3. Khởi động lại ứng dụng"
    )
    return False

def copy_ssl_libs_to_python():
    """
    Sao chép thư viện SSL từ thư mục OpenSSL vào thư mục Python
    """
    if platform.system() != "Windows":
        return
    
    try:
        # Đường dẫn có thể chứa thư viện OpenSSL
        openssl_paths = [
            "C:\\Program Files\\OpenSSL-Win64",
            "C:\\Program Files (x86)\\OpenSSL-Win64"
        ]
        
        # Thư viện cần sao chép
        ssl_libs = ["libssl-3-x64.dll", "libcrypto-3-x64.dll"]
        
        # Thư mục đích
        python_dll_dir = os.path.join(sys.exec_prefix, "DLLs")
        if not os.path.exists(python_dll_dir):
            os.makedirs(python_dll_dir)
        
        # Tìm và sao chép thư viện
        for openssl_path in openssl_paths:
            if os.path.exists(openssl_path):
                bin_dir = os.path.join(openssl_path, "bin")
                if os.path.exists(bin_dir):
                    for lib in ssl_libs:
                        lib_path = os.path.join(bin_dir, lib)
                        if os.path.exists(lib_path):
                            dest_path = os.path.join(python_dll_dir, lib)
                            shutil.copy2(lib_path, dest_path)
                            logger.info(f"Đã sao chép {lib} vào {dest_path}")
    except Exception as e:
        logger.error(f"Lỗi khi sao chép thư viện SSL: {str(e)}")

def setup_ssl():
    """
    Thiết lập SSL cho ứng dụng
    
    Returns:
        bool: True nếu thành công
    """
    try:
        # Trên Windows, thực hiện các bước thêm
        if platform.system() == "Windows":
            # Kiểm tra và cài đặt OpenSSL nếu cần
            if not fix_ssl_on_windows():
                # Nếu không thể cài đặt tự động, thử sao chép thư viện
                copy_ssl_libs_to_python()
        
        # Kiểm tra lại xem SSL đã hoạt động chưa
        try:
            import ssl
            logger.info(f"SSL đã được cấu hình, phiên bản thư viện: {ssl.OPENSSL_VERSION}")
            return True
        except ImportError:
            logger.error("Không thể import module ssl sau khi cấu hình")
            return False
    except Exception as e:
        logger.error(f"Lỗi khi thiết lập SSL: {str(e)}")
        return False

if __name__ == "__main__":
    # Kiểm tra trực tiếp
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    setup_ssl() 