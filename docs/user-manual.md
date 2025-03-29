# Hướng dẫn sử dụng Telegram Video Uploader

## 1. Tổng quan giao diện

Giao diện chính của Telegram Video Uploader gồm 4 tab chính:

1. **Tab Tải lên**: Tải video lên Telegram một cách thủ công
2. **Tab Tự động**: Thiết lập tự động theo dõi và tải lên video từ thư mục
3. **Tab Cài đặt**: Cấu hình thông tin Telegram và các tùy chọn khác
4. **Tab Nhật ký**: Hiển thị log hoạt động của ứng dụng

![Giao diện chính](images/main-interface.png)

## 2. Hướng dẫn sử dụng cơ bản

### 2.1. Tải video lên thủ công

1. **Chọn thư mục video**:
   - Trong tab "Tải lên", nhấn nút "Duyệt..." để chọn thư mục chứa video
   - Hoặc nhập trực tiếp đường dẫn vào ô nhập liệu

2. **Làm mới danh sách**:
   - Nhấn nút "Làm mới danh sách" để hiển thị các video trong thư mục
   - Hệ thống sẽ quét và hiển thị các video có định dạng được hỗ trợ

3. **Chọn video cần tải lên**:
   - Nhấp vào video cần tải lên trong danh sách
   - Giữ phím Ctrl và nhấp để chọn nhiều video
   - Khi chọn video, thông tin chi tiết và hình thu nhỏ sẽ hiển thị ở phần thông tin video

4. **Tải lên video**:
   - Nhấn nút "Bắt đầu tải lên" để bắt đầu quá trình tải lên
   - Thanh tiến trình sẽ hiển thị trạng thái tải lên
   - Thông báo kết quả sẽ được gửi đến chat ID thông báo (nếu đã cấu hình)

5. **Dừng quá trình tải lên**:
   - Nhấn nút "Dừng lại" để dừng quá trình tải lên đang diễn ra
   - Các video đã được tải lên sẽ không bị ảnh hưởng

### 2.2. Kiểm tra và xử lý video trùng lặp

1. **Bật tính năng kiểm tra trùng lặp**:
   - Đánh dấu vào ô "Kiểm tra video trùng lặp" trong tab "Tải lên"
   - Làm mới danh sách video để quét và phân tích

2. **Xem video trùng lặp**:
   - Các video trùng lặp sẽ được đánh dấu trong danh sách
   - Thông tin chi tiết về trùng lặp sẽ hiển thị khi chọn video

3. **Loại bỏ video trùng lặp**:
   - Nhấn nút "Loại bỏ trùng lặp" để tự động loại bỏ các video trùng lặp khỏi danh sách
   - Ứng dụng sẽ giữ lại video có chất lượng tốt nhất trong mỗi nhóm trùng lặp

## 3. Tự động tải lên video

### 3.1. Thiết lập tự động tải lên

1. **Chuyển đến tab "Tự động"**

2. **Cấu hình thư mục giám sát**:
   - Nhấn nút "Duyệt..." để chọn thư mục cần giám sát
   - Hoặc nhập trực tiếp đường dẫn vào ô nhập liệu

3. **Cấu hình tùy chọn tự động**:
   - **Thời gian kiểm tra**: Đặt thời gian giữa các lần kiểm tra thư mục (giây)
   - **Tự động loại bỏ trùng lặp**: Đánh dấu để tự động loại bỏ video trùng lặp
   - **Ghi nhật ký**: Đánh dấu để ghi nhật ký hoạt động tự động

4. **Bắt đầu tự động tải lên**:
   - Nhấn nút "Bắt đầu tự động" để bắt đầu quá trình giám sát và tải lên
   - Trạng thái giám sát sẽ hiển thị trong khung "Trạng thái giám sát"

5. **Dừng tự động tải lên**:
   - Nhấn nút "Dừng tự động" để dừng quá trình giám sát và tải lên
   - Trạng thái sẽ được cập nhật tương ứng

### 3.2. Cách hoạt động của chế độ tự động

- Hệ thống sẽ tự động quét thư mục đã chọn theo chu kỳ thời gian đã đặt
- Khi phát hiện video mới, hệ thống sẽ tự động thêm vào hàng đợi tải lên
- Nếu bật tính năng kiểm tra trùng lặp, hệ thống sẽ so sánh với các video đã tải lên trước đó
- Quá trình tải lên diễn ra trong nền, cho phép bạn tiếp tục sử dụng ứng dụng
- Trạng thái và log sẽ được cập nhật trong tab "Tự động" và "Nhật ký"

## 4. Cấu hình ứng dụng

### 4.1. Cấu hình Telegram

1. **Chuyển đến tab "Cài đặt"**

2. **Cấu hình thông tin Telegram**:
   - **Bot Token**: Nhập token bot Telegram đã lấy từ BotFather
   - **Chat ID đích**: Nhập ID kênh/nhóm nơi bạn muốn tải video lên
   - **Chat ID thông báo**: Nhập ID của bạn để nhận thông báo

3. **Kiểm tra kết nối**:
   - Nhấn nút "Kiểm tra kết nối Telegram" để xác minh thông tin đã nhập
   - Thông báo kết quả sẽ hiển thị sau khi kiểm tra

4. **Lưu cài đặt**:
   - Nhấn nút "Lưu cài đặt" để lưu thông tin cấu hình
   - Các thay đổi sẽ có hiệu lực ngay lập tức

### 4.2. Cấu hình tải lên

1. **Thời gian chờ giữa các lần tải**:
   - Điều chỉnh thời gian chờ giữa các lần tải lên để tránh bị giới hạn bởi Telegram API
   - Giá trị mặc định là 5 giây

2. **Định dạng video hỗ trợ**:
   - Điều chỉnh danh sách phần mở rộng video được hỗ trợ (ngăn cách bởi dấu phẩy)
   - Mặc định: `.mp4,.avi,.mkv,.mov,.wmv`

## 5. Theo dõi nhật ký hoạt động

1. **Chuyển đến tab "Nhật ký"**:
   - Tab này hiển thị tất cả hoạt động của ứng dụng bao gồm: tải lên, lỗi, thông báo trạng thái...

2. **Xóa nhật ký**:
   - Nhấn nút "Xóa nhật ký" để xóa nội dung log hiện tại
   - Điều này chỉ xóa log trong giao diện, không ảnh hưởng đến file log được lưu trên ổ cứng

3. **Xem log chi tiết**:
   - File log chi tiết được lưu tại: `telegram_uploader.log` trong thư mục ứng dụng
   - Bạn có thể mở file này bằng bất kỳ trình soạn thảo văn bản nào

## 6. Mẹo và thủ thuật

### 6.1. Tối ưu hiệu suất tải lên

- **Điều chỉnh thời gian chờ**: Nếu kết nối internet ổn định, bạn có thể giảm thời gian chờ xuống 3-4 giây
- **Xử lý file lớn**: Telegram Bot API giới hạn kích thước file tối đa là 50MB. Với file lớn hơn, bạn nên chia nhỏ trước khi tải lên

### 6.2. Kiểm tra trùng lặp hiệu quả

- **Thời gian phân tích**: Quá trình phân tích video để kiểm tra trùng lặp có thể mất thời gian với thư viện lớn
- **Tối ưu hóa**: Khi làm việc với thư viện lớn, chỉ nên kiểm tra trùng lặp trước khi tải lên thủ công, không nên bật liên tục

### 6.3. Xử lý sự cố phổ biến

- **Bot không gửi được video**: Đảm bảo bot có quyền admin trong kênh/nhóm đích
- **Video không hiển thị**: Một số định dạng video có thể không được Telegram hỗ trợ xem trực tuyến. Hãy sử dụng định dạng MP4 với codec H.264 để đảm bảo tương thích tốt nhất
- **Ứng dụng không phản hồi**: Nếu ứng dụng bị treo khi xử lý nhiều video, hãy khởi động lại và giảm số lượng video xử lý cùng lúc

## 7. Hỗ trợ và phản hồi

Nếu bạn gặp bất kỳ vấn đề nào khi sử dụng ứng dụng, vui lòng:

1. Kiểm tra phần [Xử lý sự cố](installation.md#4-xử-lý-sự-cố) trong hướng dẫn cài đặt
2. Tạo [issue trên GitHub](https://github.com/username/telegram-video-uploader/issues) để nhận hỗ trợ
3. Hoặc liên hệ qua email: example@email.com

---

Chúc bạn sử dụng Telegram Video Uploader hiệu quả!