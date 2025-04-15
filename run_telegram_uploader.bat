@echo off
chcp 65001 > nul
@echo off
echo ===================================================
echo Telegram Video Uploader - Auto Setup and Run Script
echo ===================================================
echo.

:: Kiểm tra Python đã được cài đặt chưa
echo Kiểm tra cài đặt Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LỖII] Python không được tìm thấy. Vui lòng cài đặt Python 3.8 hoặc cao hơn.
    echo Bạn có thể tải Python tại: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Kiểm tra pip
echo Kiểm tra pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [CẢNH BÁO] Pip không được tìm thấy. Đang thử cài đặt pip...
    python -m ensurepip --default-pip
    if %errorlevel% neq 0 (
        echo [LỖI] Không thể cài đặt pip. Vui lòng cài đặt pip thủ công.
        pause
        exit /b 1
    )
)

:: Kiểm tra file requirements.txt
echo Kiểm tra file requirements.txt...
if not exist src\requirements.txt (
    echo [LỖI] Không tìm thấy file src\requirements.txt
    echo Đảm bảo bạn đang chạy script này từ thư mục chứa thư mục 'src'.
    pause
    exit /b 1
)

:: Cài đặt các gói từ requirements.txt
echo.
echo Cài đặt các gói cần thiết...
echo.
python -m pip install -r src\requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [LỖI] Không thể cài đặt các gói cần thiết. Vui lòng kiểm tra lỗi bên trên.
    pause
    exit /b 1
)

:: Chạy ứng dụng
echo.
echo Cài đặt hoàn tất! Đang khởi động Telegram Video Uploader...
echo.
python src\main.py
if %errorlevel% neq 0 (
    echo.
    echo [LỖI] Ứng dụng kết thúc với lỗi. Vui lòng kiểm tra lỗi bên trên.
    pause
    exit /b 1
)

echo.
echo Ứng dụng đã đóng. Cảm ơn bạn đã sử dụng Telegram Video Uploader!
pause