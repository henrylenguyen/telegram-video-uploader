# Hướng dẫn cài đặt Telegram Video Uploader

## 1. Cài đặt từ file .exe (dành cho người dùng)

### 1.1. Yêu cầu hệ thống
- Windows 7/8/10/11
- Kết nối internet ổn định
- Đã tạo Bot Telegram và lấy được Token

### 1.2. Các bước cài đặt
1. Tải xuống file cài đặt từ [trang phát hành](https://github.com/username/telegram-video-uploader/releases)
2. Giải nén file ZIP vào thư mục bất kỳ
3. Chạy file `SETUP.bat` để bắt đầu quá trình cài đặt
4. Làm theo hướng dẫn trên màn hình để cấu hình ứng dụng

### 1.3. Cấu hình Telegram Bot

Để sử dụng ứng dụng, bạn cần tạo một bot Telegram và lấy thông tin cần thiết:

#### Tạo Bot Telegram và lấy Bot Token
1. Mở ứng dụng Telegram, tìm kiếm `@BotFather`
2. Gửi lệnh `/newbot` để tạo bot mới
3. Đặt tên cho bot (ví dụ: "My Video Uploader")
4. Đặt username cho bot (phải kết thúc bằng "bot", ví dụ: "my_video_uploader_bot")
5. BotFather sẽ gửi cho bạn một token API. Lưu lại token này để sử dụng trong ứng dụng.

![Tạo Bot với BotFather](images/botfather-create.png)

#### Lấy Chat ID

1. **Lấy Chat ID của kênh/nhóm:**
   - Thêm bot vào kênh/nhóm và đặt làm admin
   - Gửi một tin nhắn bất kỳ trong kênh/nhóm đó
   - Truy cập URL: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Tìm phần "chat" > "id" trong kết quả JSON (đối với kênh, ID thường có dạng -100xxxxxxxxxx)

![Lấy Chat ID Nhóm/Kênh](images/get-chat-id.png)

2. **Lấy Chat ID cá nhân:**
   - Tìm kiếm `@userinfobot` trên Telegram
   - Gửi bất kỳ tin nhắn nào và bot sẽ trả về ID của bạn

![Lấy Chat ID Cá nhân](images/get-personal-id.png)

## 2. Cài đặt từ mã nguồn (dành cho nhà phát triển)

### 2.1. Yêu cầu hệ thống
- Python 3.7 trở lên
- Git (tùy chọn)
- Windows, macOS hoặc Linux

### 2.2. Cài đặt các thư viện cần thiết

1. Clone repository (hoặc tải xuống mã nguồn):
```bash
git clone https://github.com/username/telegram-video-uploader.git
cd telegram-video-uploader
```

2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

3. (Tùy chọn) Tạo môi trường ảo:
```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
# Trên Windows
venv\Scripts\activate
# Trên macOS/Linux
source venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 2.3. Chạy ứng dụng từ mã nguồn

```bash
python src/telegram_uploader.py
```

Hoặc sử dụng script cài đặt:
```bash
pip install -e .
telegram-uploader
```

### 2.4. Đóng gói ứng dụng thành file .exe

1. Chạy script đóng gói:
```bash
python build/build.py
```

2. Sau khi hoàn tất, các file thực thi sẽ được tạo trong thư mục `output/`

## 3. Cấu hình ứng dụng

### 3.1. Cấu hình qua công cụ cấu hình

1. Chạy công cụ cấu hình:
   - Nếu cài đặt từ file .exe: Chạy file `config/Telegram_Uploader_Config.exe`
   - Nếu cài đặt từ mã nguồn: Chạy `python src/telegram_uploader.py --config`

2. Nhập các thông tin sau:
   - **Bot Token**: Token nhận được từ BotFather
   - **Chat ID đích**: ID kênh/nhóm nơi bạn muốn tải video lên
   - **Chat ID thông báo**: ID của bạn để nhận thông báo về trạng thái tải lên

3. Nhấn "Kiểm tra kết nối" để xác nhận thông tin chính xác
4. Nhấn "Lưu và thoát" để lưu cấu hình

### 3.2. Cấu hình thủ công

Nếu cần thiết, bạn có thể chỉnh sửa file `config.ini` trực tiếp:

```ini
[TELEGRAM]
bot_token = YOUR_BOT_TOKEN
chat_id = TARGET_CHAT_ID
notification_chat_id = YOUR_PERSONAL_CHAT_ID

[SETTINGS]
video_folder = C:\path\to\videos
video_extensions = .mp4,.avi,.mkv,.mov,.wmv
delay_between_uploads = 5
auto_mode = false
check_duplicates = true
auto_check_interval = 60
```

## 4. Xử lý sự cố

### 4.1. Vấn đề kết nối
- **Lỗi "Không thể kết nối với bot Telegram"**: Kiểm tra lại Bot Token và kết nối internet
- **Lỗi "Forbidden"**: Đảm bảo bot có quyền gửi tin nhắn/media trong kênh/nhóm

### 4.2. Vấn đề phát hiện video
- **Không tìm thấy video**: Kiểm tra đường dẫn thư mục và định dạng video được hỗ trợ
- **Lỗi phân tích video**: Đảm bảo video không bị hỏng và có thể phát được

### 4.3. Khôi phục cài đặt mặc định
Nếu muốn khôi phục toàn bộ cài đặt:
1. Xóa file `config.ini` trong thư mục ứng dụng
2. Khởi động lại ứng dụng, chương trình sẽ tạo lại file cấu hình mặc định

## 5. Tài nguyên bổ sung

- [Hướng dẫn sử dụng](user-manual.md)
- [Hướng dẫn cho nhà phát triển](developer-guide.md)
- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)ết

1. Clone repository (hoặc tải xuống mã nguồn):
```bash
git clone https://github.com/username/telegram-video-uploader.git
cd telegram-video-uploader
```

2. Cài đặt các thư viện cần thi