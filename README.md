# Telegram Video Uploader

![Telegram Video Uploader Banner](docs/images/banner.png)

## Giới thiệu

Telegram Video Uploader là ứng dụng desktop giúp tải video từ thư mục lên Telegram một cách tự động và hiệu quả. Ứng dụng cung cấp giao diện thân thiện, dễ sử dụng và có nhiều tính năng hữu ích.

### Tính năng chính

- **Tải lên thủ công**: Chọn và tải video một cách thủ công
- **Tự động tải lên**: Tự động quét thư mục và tải lên video mới
- **Phát hiện trùng lặp**: Phân tích và phát hiện các video có nội dung trùng lặp
- **Thông báo trạng thái**: Gửi thông báo về trạng thái tải lên qua Telegram
- **Ghi nhật ký**: Theo dõi các hoạt động và lỗi trong quá trình tải lên
- **Dễ dàng cấu hình**: Cài đặt token bot và ID chat thông qua giao diện đồ họa

## Cài đặt

### Yêu cầu hệ thống

- Windows 7/8/10/11
- Kết nối internet ổn định
- Đã tạo Bot Telegram và lấy được Token

### Phương pháp cài đặt

#### 1. Cài đặt từ file .exe (dành cho người dùng)

1. Tải xuống file cài đặt từ [Release](https://github.com/username/telegram-video-uploader/releases)
2. Giải nén file ZIP vào thư mục bất kỳ
3. Chạy file `SETUP.bat` để bắt đầu cài đặt
4. Làm theo hướng dẫn trên màn hình để cấu hình ứng dụng

#### 2. Cài đặt từ mã nguồn (dành cho nhà phát triển)

1. Clone repository:
```bash
git clone https://github.com/username/telegram-video-uploader.git
cd telegram-video-uploader
```

2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

3. Chạy ứng dụng:
```bash
python src/telegram_uploader.py
```

## Sử dụng cơ bản

1. **Khởi động ứng dụng**: Mở file `Telegram_Video_Uploader.exe`
2. **Cấu hình**: Nhập Bot Token và Chat ID (nếu chưa cấu hình)
3. **Tải lên thủ công**:
   - Chọn thư mục chứa video
   - Chọn video cần tải lên
   - Nhấn "Bắt đầu tải lên"
4. **Tải lên tự động**:
   - Chuyển đến tab "Tự động"
   - Chọn thư mục giám sát
   - Cấu hình các tùy chọn
   - Nhấn "Bắt đầu tự động"

## Tài liệu

- [Hướng dẫn cài đặt](docs/installation.md)
- [Hướng dẫn sử dụng](docs/user-manual.md)
- [Hướng dẫn cho nhà phát triển](docs/developer-guide.md)

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Nếu bạn muốn đóng góp, vui lòng:

1. Fork repository
2. Tạo nhánh tính năng mới (`git checkout -b feature/amazing-feature`)
3. Commit các thay đổi (`git commit -m 'Add some amazing feature'`)
4. Push lên nhánh (`git push origin feature/amazing-feature`)
5. Mở Pull Request

## Giấy phép

Dự án này được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm thông tin.

## Liên hệ

Nếu bạn có bất kỳ câu hỏi hoặc đề xuất nào, vui lòng tạo một [issue](https://github.com/username/telegram-video-uploader/issues) hoặc liên hệ qua email: example@email.com.

---

<p align="center">Made with ❤️ for Telegram users</p>