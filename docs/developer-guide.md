# Hướng dẫn phát triển Telegram Video Uploader

Tài liệu này cung cấp thông tin chi tiết về cấu trúc mã nguồn, quy trình phát triển, và hướng dẫn mở rộng ứng dụng Telegram Video Uploader.

## 1. Cấu trúc mã nguồn

```
telegram-video-uploader/
│
├── src/                            # Thư mục mã nguồn
│   ├── telegram_uploader.py        # File chính của ứng dụng
│   ├── icon.ico                    # Biểu tượng ứng dụng
│   └── utils/                      # Thư mục chứa các tiện ích
│       ├── __init__.py
│       ├── video_analyzer.py       # Phân tích và so sánh video
│       ├── auto_uploader.py        # Tự động tải lên
│       └── telegram_api.py         # Xử lý tương tác với Telegram
│
├── build/                          # Scripts đóng gói
│   ├── build.py                    # Script đóng gói chính
│   └── icon.ico                    # Biểu tượng cho ứng dụng đóng gói
│
├── docs/                           # Tài liệu hướng dẫn
│   ├── images/                     # Hình ảnh minh họa
│   ├── installation.md             # Hướng dẫn cài đặt
│   ├── user-manual.md              # Hướng dẫn sử dụng
│   └── developer-guide.md          # Hướng dẫn cho nhà phát triển
│
├── requirements.txt                # Danh sách các thư viện cần thiết
├── setup.py                        # Script cài đặt
├── README.md                       # Thông tin tổng quan về dự án
└── LICENSE                         # Giấy phép sử dụng
```

## 2. Các thành phần chính

### 2.1. File chính: `telegram_uploader.py`

File này chứa ứng dụng chính, cung cấp giao diện người dùng đồ họa (GUI) và kết nối các thành phần khác của hệ thống.

Cấu trúc chính của file:

- **Lớp TelegramUploaderApp**: Quản lý ứng dụng chính
  - Tạo và quản lý giao diện người dùng
  - Xử lý các sự kiện người dùng
  - Tích hợp các module khác

- **Chế độ cấu hình**: Cung cấp giao diện cấu hình độc lập khi chạy với đối số `--config`

### 2.2. Module `video_analyzer.py`

Module này chịu trách nhiệm phân tích video và phát hiện nội dung trùng lặp.

Cấu trúc chính:

- **Lớp VideoAnalyzer**: 
  - Phân tích video để tạo hash đặc trưng
  - So sánh hash để phát hiện video trùng lặp
  - Tạo thumbnail và trích xuất metadata từ video

### 2.3. Module `auto_uploader.py`

Module này cung cấp tính năng tự động theo dõi thư mục và tải lên video mới.

Cấu trúc chính:

- **Lớp FileWatcher**: Theo dõi thư mục để phát hiện file mới
- **Lớp AutoUploader**: Quản lý việc tự động tải lên

### 2.4. Module `telegram_api.py`

Module này xử lý tương tác với Telegram Bot API.

Cấu trúc chính:

- **Lớp TelegramAPI**: 
  - Kết nối với bot Telegram
  - Gửi tin nhắn và video
  - Xử lý lỗi và giới hạn tốc độ

## 3. Quy trình phát triển

### 3.1. Thiết lập môi trường phát triển

1. Clone repository:
```bash
git clone https://github.com/username/telegram-video-uploader.git
cd telegram-video-uploader
```

2. Tạo và kích hoạt môi trường ảo:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Cài đặt các thư viện phát triển:
```bash
pip install -r requirements.txt
pip install -e .  # Cài đặt dự án ở chế độ phát triển
```

### 3.2. Quy trình làm việc

1. **Phát triển tính năng**:
   - Tạo nhánh mới cho tính năng hoặc sửa lỗi
   - Phát triển và kiểm thử cục bộ
   - Tạo pull request để xem xét mã nguồn

2. **Kiểm thử**:
   - Kiểm thử thủ công tính năng mới
   - Viết và chạy unit test nếu cần thiết

3. **Đóng gói và phát hành**:
   - Cập nhật phiên bản trong các file liên quan
   - Chạy script đóng gói: `python build/build.py`
   - Tạo tag phiên bản mới và phát hành

## 4. Hướng dẫn mở rộng

### 4.1. Thêm định dạng video mới

1. Cập nhật cấu hình mặc định trong `telegram_uploader.py`:
```python
config['SETTINGS'] = {
    # ...
    'video_extensions': '.mp4,.avi,.mkv,.mov,.wmv,.flv,.webm',  # Thêm định dạng mới
    # ...
}
```

2. Kiểm tra hỗ trợ trong `video_analyzer.py` để đảm bảo tương thích.

### 4.2. Cải thiện thuật toán phát hiện trùng lặp

Module `video_analyzer.py` sử dụng kết hợp perceptual hash và metadata để phát hiện video trùng lặp. Bạn có thể cải thiện bằng cách:

1. Điều chỉnh cách lấy mẫu khung hình:
```python
# Ví dụ: Thay đổi vị trí lấy mẫu khung hình
positions = [0.05, 0.25, 0.5, 0.75, 0.95]  # Vị trí mới
```

2. Thêm các thuật toán hash bổ sung:
```python
# Thêm một loại hash khác như Average Hash
avg_hash = imagehash.average_hash(pil_img)
frames.append(str(avg_hash))
```

### 4.3. Thêm tính năng mới

Để thêm một tính năng mới vào ứng dụng, làm theo các bước sau:

1. **Xác định vị trí tính năng**: 
   - Tích hợp vào module hiện có
   - Hoặc tạo module mới trong thư mục `utils/`

2. **Cập nhật giao diện người dùng**:
   - Thêm tab mới nếu cần trong `create_ui()` 
   - Hoặc thêm các điều khiển vào tab hiện có

3. **Cập nhật cấu hình**:
   - Thêm các tùy chọn cấu hình mới vào file `config.ini`
   - Cập nhật cấu hình mặc định trong `load_config()`

### 4.4. Ví dụ: Thêm tính năng nén video

1. Tạo module mới `utils/video_compressor.py`:

```python
"""
Module nén video trước khi tải lên.
"""
import os
import subprocess
import logging

logger = logging.getLogger("VideoCompressor")

class VideoCompressor:
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mkv', '.mov']
    
    def compress_video(self, input_path, output_path=None, target_size_mb=40):
        """
        Nén video để giảm kích thước file
        
        Args:
            input_path (str): Đường dẫn đến file video đầu vào
            output_path (str): Đường dẫn đầu ra (mặc định: thêm hậu tố "_compressed")
            target_size_mb (int): Kích thước đích tính bằng MB
            
        Returns:
            str: Đường dẫn đến file đã nén nếu thành công, None nếu thất bại
        """
        try:
            # Nếu không chỉ định đường dẫn đầu ra, tạo tên file mặc định
            if not output_path:
                file_name, file_ext = os.path.splitext(input_path)
                output_path = f"{file_name}_compressed{file_ext}"
            
            # Kiểm tra kích thước file đầu vào
            input_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
            
            # Nếu file đã nhỏ hơn kích thước mục tiêu, không cần nén
            if input_size <= target_size_mb:
                logger.info(f"File {os.path.basename(input_path)} đã đủ nhỏ ({input_size:.2f} MB), không cần nén")
                return input_path
            
            # Tính toán bitrate cần thiết để đạt kích thước mục tiêu
            # Công thức ước tính: bitrate (kb/s) = target_size_mb * 8192 / duration_seconds
            # Sử dụng ffprobe để lấy thời lượng video
            duration_cmd = [
                'ffprobe', 
                '-v', 'error', 
                '-show_entries', 'format=duration', 
                '-of', 'default=noprint_wrappers=1:nokey=1', 
                input_path
            ]
            
            duration = float(subprocess.check_output(duration_cmd).decode('utf-8').strip())
            target_bitrate = int((target_size_mb * 8192) / duration)
            
            # Sử dụng ffmpeg để nén video
            compress_cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', 'libx264',
                '-b:v', f'{target_bitrate}k',
                '-preset', 'medium',  # Cân bằng giữa tốc độ nén và chất lượng
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',  # Ghi đè file nếu đã tồn tại
                output_path
            ]
            
            # Thực hiện lệnh nén
            subprocess.call(compress_cmd)
            
            # Kiểm tra kết quả
            if os.path.exists(output_path):
                output_size = os.path.getsize(output_path) / (1024 * 1024)
                logger.info(f"Đã nén video {os.path.basename(input_path)}: {input_size:.2f} MB -> {output_size:.2f} MB")
                return output_path
            else:
                logger.error(f"Không thể nén video {input_path}")
                return None
                
        except Exception as e:
            logger.error(f"Lỗi khi nén video {input_path}: {str(e)}")
            return None
    
    def batch_compress(self, video_paths, target_size_mb=40):
        """
        Nén nhiều video
        
        Args:
            video_paths (list): Danh sách đường dẫn video
            target_size_mb (int): Kích thước đích tính bằng MB
            
        Returns:
            dict: Từ điển ánh xạ đường dẫn gốc -> đường dẫn đã nén
        """
        results = {}
        
        for video_path in video_paths:
            compressed_path = self.compress_video(video_path, target_size_mb=target_size_mb)
            results[video_path] = compressed_path
        
        return results
```

2. Tích hợp module vào `telegram_uploader.py`:

```python
# Trong hàm __init__ của TelegramUploaderApp
from utils.video_compressor import VideoCompressor
self.video_compressor = VideoCompressor()

# Thêm cài đặt mới
def load_config(self):
    # ...
    config['SETTINGS'] = {
        # Các cài đặt hiện có
        'auto_compress': 'true',
        'target_size_mb': '40'
    }
    # ...
```

3. Thêm tùy chọn nén vào giao diện:

```python
# Trong hàm create_settings_tab
compress_frame = ttk.LabelFrame(upload_frame, text="Nén video")
compress_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)

# Checkbox bật/tắt tính năng nén
self.compress_var = tk.BooleanVar()
self.compress_var.set(self.config['SETTINGS'].getboolean('auto_compress', True))

compress_cb = ttk.Checkbutton(
    compress_frame, 
    text="Tự động nén video lớn hơn 50MB", 
    variable=self.compress_var
)
compress_cb.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

# Kích thước đích
ttk.Label(compress_frame, text="Kích thước đích (MB):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
self.target_size_var = tk.StringVar()
self.target_size_var.set(self.config['SETTINGS'].get('target_size_mb', '40'))

target_size_entry = ttk.Entry(compress_frame, width=10, textvariable=self.target_size_var)
target_size_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
```

4. Triển khai tính năng trong chức năng tải lên:

```python
def upload_videos(self, folder_path, video_files, chat_id, notification_chat_id):
    # ...
    for index, video_file in enumerate(video_files):
        # ...
        try:
            # Đường dẫn đầy đủ đến file video
            video_path = os.path.join(folder_path, video_file)
            
            # Kiểm tra kích thước file
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            
            # Nén video nếu cần
            if file_size > 50 and self.compress_var.get():
                self.status_var.set(f"Đang nén video: {video_file}")
                self.root.update_idletasks()
                
                target_size = int(self.target_size_var.get())
                compressed_path = self.video_compressor.compress_video(
                    video_path, 
                    target_size_mb=target_size
                )
                
                if compressed_path and compressed_path != video_path:
                    video_path = compressed_path
                    video_file = os.path.basename(compressed_path)
                    file_size = os.path.getsize(video_path) / (1024 * 1024)
            
            # Tiếp tục với việc tải lên
            # ...
```

### 4.5. Viết mở rộng mã nguồn có cấu trúc

Khi mở rộng mã nguồn của dự án, hãy tuân thủ các nguyên tắc sau:

1. **Tách biệt trách nhiệm**: Mỗi module/lớp nên có một trách nhiệm rõ ràng
2. **Viết tài liệu**: Sử dụng docstring để mô tả chức năng của mỗi module, lớp và phương thức
3. **Xử lý ngoại lệ**: Bắt và xử lý các ngoại lệ có thể xảy ra
4. **Ghi log**: Sử dụng logging để ghi lại thông tin, cảnh báo và lỗi

## 5. Gỡ lỗi và xử lý sự cố

### 5.1. Gỡ lỗi giao diện người dùng

Các vấn đề phổ biến và cách khắc phục:

1. **Widget không hiển thị**: Kiểm tra cấu trúc của layout, đảm bảo widget được đặt trong container đúng và phương thức pack/grid được gọi
   
2. **Sự kiện không được xử lý**: Kiểm tra ràng buộc sự kiện (bindings) và trình xử lý sự kiện

3. **Giao diện không phản hồi**: Sử dụng `update_idletasks()` để cập nhật giao diện trong các hoạt động dài

### 5.2. Gỡ lỗi kết nối Telegram

1. **Lỗi kết nối**:
   - Kiểm tra Bot Token và kết nối internet
   - Xem log lỗi để biết chi tiết

2. **Lỗi quyền**:
   - Đảm bảo bot có quyền admin trong kênh/nhóm
   - Kiểm tra quyền gửi media

3. **Lỗi giới hạn tốc độ (Rate limiting)**:
   - Tăng thời gian chờ giữa các lần tải lên
   - Sử dụng cơ chế xử lý lỗi và thử lại

### 5.3. Các công cụ gỡ lỗi

1. **logging**:
   - Kiểm tra file `telegram_uploader.log` để xem log chi tiết
   - Điều chỉnh mức log trong `logging.basicConfig(level=logging.DEBUG)`

2. **pdb (Python Debugger)**:
   - Chèn `import pdb; pdb.set_trace()` vào mã nguồn để gỡ lỗi tương tác

3. **try-except**:
   - Bắt ngoại lệ cụ thể và in ra thông tin lỗi chi tiết

## 6. Quy ước mã nguồn

### 6.1. Kiểu đặt tên

- **Tên lớp**: PascalCase (ví dụ: `VideoAnalyzer`)
- **Tên hàm/phương thức**: snake_case (ví dụ: `calculate_video_hash`)
- **Tên biến**: snake_case (ví dụ: `video_path`)
- **Hằng số**: UPPER_CASE (ví dụ: `MAX_FILE_SIZE`)

### 6.2. Định dạng mã nguồn

- Sử dụng 4 dấu cách cho mỗi mức thụt đầu dòng (không sử dụng tab)
- Chiều dài dòng tối đa: 88 ký tự
- Sử dụng dấu ngoặc kép kép (`"`) cho chuỗi

### 6.3. Tài liệu mã nguồn

- Sử dụng docstring kiểu Google cho mọi module, lớp, và phương thức
- Mô tả mục đích, tham số, và giá trị trả về

```python
def calculate_video_hash(self, video_path):
    """
    Tính toán giá trị hash dựa trên nội dung video.
    
    Args:
        video_path (str): Đường dẫn đến file video
        
    Returns:
        str: Hash đại diện cho video hoặc None nếu có lỗi
    """
```

## 7. Tài liệu tham khảo

- [Python Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [pyTelegramBotAPI Documentation](https://github.com/eternnoir/pyTelegramBotAPI)
- [OpenCV-Python Documentation](https://docs.opencv.org/master/d6/d00/tutorial_py_root.html)
- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/en/stable/)

---

Tài liệu này sẽ được cập nhật liên tục khi dự án phát triển. Nếu bạn có bất kỳ câu hỏi hoặc đề xuất nào, vui lòng tạo issue trên GitHub hoặc đóng góp trực tiếp vào tài liệu này.Compressor")

class VideoCompressor:
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mkv', '.mov']
    
    def compress_video(self, input_path, output_path=None, target_size_mb=40):
        """
        Nén video để giảm kích thước file
        
        Args:
            input_path (str): Đường dẫn đến file video đầu vào
            output_path (str): Đường dẫn đầu ra (mặc định: thêm hậu tố "_compressed")
            target_size_mb (int): Kích thước đích tính bằng MB
            
        Returns:
            str: Đường dẫn đến file đã nén nếu thành công, None nếu thất bại
        """
        try:
            # Nếu không chỉ định đường dẫn đầu ra, tạo tên file mặc định
            if not output