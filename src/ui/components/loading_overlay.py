"""
LoadingOverlay component for the UI
"""
import logging
import os
import tempfile
import math
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)

class LoadingOverlay(QtWidgets.QWidget):
    """Loading overlay với animation hiệu ứng tốt hơn"""
    
    def __init__(self, parent=None):
        super(LoadingOverlay, self).__init__(parent)
        
        # Làm cho overlay bán trong suốt với màu nền đẹp
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 150);
            border-radius: 10px;
        """)
        
        # Tạo layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Tạo container cho spinner và label
        self.container = QtWidgets.QWidget()
        self.container.setFixedSize(400, 200)
        self.container.setStyleSheet("""
            background-color: rgba(255, 255, 255, 90%);
            border-radius: 10px;
            border: 1px solid #3498DB;
        """)
        
        # Layout cho container
        container_layout = QtWidgets.QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Tạo label cho spinner
        self.spinner_label = QtWidgets.QLabel()
        self.spinner_label.setAlignment(QtCore.Qt.AlignCenter)
        self.spinner_label.setFixedSize(50, 50)
        self.spinner_label.setStyleSheet("background-color: transparent;")
        
        # Tạo spinner animation
        self.spinner_movie = QtGui.QMovie()
        self.spinner_movie.setFileName(self.get_spinner_path())
        self.spinner_movie.setScaledSize(QtCore.QSize(50, 50))
        self.spinner_label.setMovie(self.spinner_movie)
        
        # Tạo label cho message
        self.message_label = QtWidgets.QLabel("Đang tải...")
        self.message_label.setAlignment(QtCore.Qt.AlignCenter)
        self.message_label.setStyleSheet("""
            color: #333333;
            font-size: 16px;
            font-weight: bold;
            background-color: transparent;
        """)
        self.message_label.setWordWrap(True)
        
        # Thêm các widget vào container
        container_layout.addWidget(self.spinner_label, alignment=QtCore.Qt.AlignCenter)
        container_layout.addWidget(self.message_label, alignment=QtCore.Qt.AlignCenter)
        
        # Thêm container vào layout chính
        self.layout.addWidget(self.container, alignment=QtCore.Qt.AlignCenter)
        
        # Ẩn mặc định
        self.hide()
        
        # Timer để cập nhật spinner khi không có file
        self.dots_count = 0
        self.dots_timer = None

    def get_spinner_path(self):
        """Tạo hoặc tìm spinner GIF ở thư mục tạm"""
        try:
            # Sử dụng spinner có sẵn nếu có
            import os
            import tempfile
            import math
            import numpy as np
            
            # Kiểm tra thư mục tạm cho spinner
            temp_dir = os.path.join(tempfile.gettempdir(), "telegram_uploader")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            spinner_path = os.path.join(temp_dir, "spinner.gif")
            
            # Kiểm tra nếu spinner đã tồn tại
            if os.path.exists(spinner_path):
                return spinner_path
            
            # Tạo spinner đơn giản bằng PyQt
            from PyQt5.QtCore import Qt, QSize
            from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QImage
            
            # Tạo spinner GIF giả lập đơn giản
            size = 40
            frames = 8
            images = []
            
            for i in range(frames):
                # Tạo QImage mới cho mỗi frame
                img = QImage(size, size, QImage.Format_ARGB32)
                img.fill(Qt.transparent)
                
                # Tạo painter và vẽ spinner
                painter = QPainter(img)
                painter.setRenderHint(QPainter.Antialiasing)
                
                # Tính toán các thông số cho spinner
                center = size / 2
                radius = size / 2 - 5
                start_angle = i * (360 / frames) * 16  # QPainter sử dụng 1/16 độ
                
                # Vẽ đường tròn nền mờ
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(200, 200, 200, 50)))
                painter.drawEllipse(5, 5, size - 10, size - 10)
                
                # Vẽ phần spinner quay
                gradient_colors = [(33, 150, 243, 50), (33, 150, 243, 255)]
                for j in range(5):  # 5 chấm gradient
                    angle = start_angle - j * 30 * 16
                    x = center + radius * 0.8 * math.cos(math.radians(angle / 16))
                    y = center + radius * 0.8 * math.sin(math.radians(angle / 16))
                    
                    alpha = 255 - j * 40  # Giảm dần độ mờ
                    color = QColor(33, 150, 243, max(50, alpha))
                    
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QBrush(color))
                    painter.drawEllipse(int(x - 5 + j), int(y - 5 + j), 10 - j, 10 - j)
                
                painter.end()
                images.append(img)
            
            # Lưu spinner thành GIF
            import imageio
            
            # Chuyển đổi QImage sang numpy array
            numpy_images = []
            for img in images:
                buffer = img.bits().asstring(img.width() * img.height() * 4)
                numpy_img = np.frombuffer(buffer, dtype=np.uint8).reshape((img.height(), img.width(), 4))
                numpy_img = numpy_img[:, :, [2, 1, 0, 3]]  # BGRA to RGBA
                numpy_images.append(numpy_img)
            
            # Lưu thành GIF
            imageio.mimsave(spinner_path, numpy_images, duration=0.1, loop=0)
            
            return spinner_path
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo spinner: {str(e)}")
            # Trả về None để sử dụng hiệu ứng chấm thay thế
            return None
    
    def set_message(self, message):
        """Thiết lập thông báo hiển thị"""
        self.message_label.setText(message)
    
    def show_spinner(self, show=True):
        """Hiển thị hoặc ẩn spinner"""
        if show:
            # Hiển thị spinner nếu có file
            if self.spinner_movie.fileName():
                self.spinner_movie.start()
                self.spinner_label.show()
            else:
                # Sử dụng hiệu ứng chấm nếu không có file
                if self.dots_timer is None:
                    self.dots_timer = self.startTimer(500)  # Cập nhật mỗi 0.5 giây
                self.spinner_label.setText("⏳")
                self.spinner_label.setStyleSheet("font-size: 24px; color: #3498DB;")
                self.spinner_label.show()
        else:
            # Dừng spinner
            if self.spinner_movie.fileName():
                self.spinner_movie.stop()
            
            # Dừng timer hiệu ứng chấm
            if self.dots_timer is not None:
                self.killTimer(self.dots_timer)
                self.dots_timer = None
            
            self.spinner_label.hide()
    
    def timerEvent(self, event):
        """Xử lý sự kiện timer cho hiệu ứng chấm"""
        if self.dots_timer is not None and event.timerId() == self.dots_timer:
            self.dots_count = (self.dots_count + 1) % 4
            dots = "." * self.dots_count
            
            # Thay đổi biểu tượng spinner
            if self.dots_count % 2 == 0:
                self.spinner_label.setText("⏳")
            else:
                self.spinner_label.setText("⌛")
    
    def showEvent(self, event):
        """Xử lý sự kiện hiện overlay"""
        # Bắt đầu spinner nếu có
        self.show_spinner(True)
        super(LoadingOverlay, self).showEvent(event)
    
    def hideEvent(self, event):
        """Xử lý sự kiện ẩn overlay"""
        # Dừng spinner
        self.show_spinner(False)
        super(LoadingOverlay, self).hideEvent(event)
    
    def resizeEvent(self, event):
        """Xử lý sự kiện thay đổi kích thước"""
        # Cập nhật kích thước cho container
        self.container.setFixedSize(min(self.width() - 40, 400), 200)
        super(LoadingOverlay, self).resizeEvent(event)
