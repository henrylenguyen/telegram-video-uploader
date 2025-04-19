"""
Module tạo và hiển thị màn hình chào khi khởi động ứng dụng.
"""
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtCore import Qt
import os
import sys
import logging

logger = logging.getLogger("SplashScreen")

class SplashScreen(QtWidgets.QWidget):
    """
    Màn hình chào hiện đại với thanh cuộn và các indicator tròn
    """
    def __init__(self, parent=None, app=None):
        super(SplashScreen, self).__init__(parent, Qt.Window | Qt.FramelessWindowHint)
        
        # Lưu tham chiếu đến ứng dụng chính
        self.app = app
        
        # Nạp giao diện từ file UI
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file = os.path.join(current_dir, "splash_screen.ui")
        
        # Nếu không tìm thấy file UI, sử dụng đường dẫn khác
        if not os.path.exists(ui_file):
            ui_file = os.path.join(current_dir, "..", "qt_designer", "splash_screen.ui")
        
        # Nếu vẫn không tìm thấy, tạo giao diện trực tiếp
        if not os.path.exists(ui_file):
            self.setup_ui_manually()
        else:
            uic.loadUi(ui_file, self)
        
        # Căn giữa màn hình
        self.center_on_screen()
        
        # Tạo logo
        self.setup_logo()
        
        # Thiết lập các indicator trạng thái
        self.setup_indicators()
        
        # Khởi tạo tiến trình
        self.current_step = 0
        self.total_steps = 8  # Tổng số bước
        
        # Thiết lập giá trị ban đầu cho thanh tiến trình
        self.progressBar.setValue(0)
        
        # Tín hiệu hoàn thành
        self.finished = QtCore.pyqtSignal()
        
    def center_on_screen(self):
        """Đặt cửa sổ vào giữa màn hình"""
        rect = QtWidgets.QApplication.desktop().availableGeometry()
        self.move((rect.width() - self.width()) // 2, (rect.height() - self.height()) // 2)
        
    def setup_ui_manually(self):
        """Thiết lập UI theo cách thủ công nếu không tìm thấy file UI"""
        # Thiết lập kích thước
        self.setObjectName("SplashScreen")
        self.resize(600, 400)
        self.setWindowTitle("Đang khởi động...")
        
        # Thiết lập stylesheet
        self.setStyleSheet("""
            QWidget#SplashScreen {
              background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8f9fa, stop:1 #e9ecef);
              border-radius: 15px;
            }
            
            QLabel#titleLabel {
              font-family: Arial, sans-serif;
              font-size: 24px;
              font-weight: bold;
              color: #2c3e50;
            }
            
            QLabel#statusLabel {
              font-family: Arial, sans-serif;
              font-size: 12px;
              color: #7f8c8d;
            }
            
            QScrollArea {
              background-color: transparent;
              border: none;
            }
            
            QWidget#scrollAreaContents {
              background-color: white;
              border-radius: 8px;
            }
            
            QScrollBar:vertical {
              background: #E2E8F0;
              width: 6px;
              border-radius: 3px;
              margin: 0px;
            }
            
            QScrollBar::handle:vertical {
              background: #CBD5E1;
              border-radius: 3px;
              min-height: 30px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
              height: 0px;
            }
            
            QProgressBar {
              background-color: #e0e0e0;
              border: none;
              height: 10px;
              border-radius: 5px;
              text-align: center;
            }
            
            QProgressBar::chunk {
              background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498DB, stop:1 #2ECC71);
              border-radius: 5px;
            }
            
            QLabel.statusItem {
              font-family: Arial, sans-serif;
              font-size: 14px;
              color: #2c3e50;
            }
            
            QLabel.statusItemPending {
              font-family: Arial, sans-serif;
              font-size: 14px;
              color: #7f8c8d;
            }
            
            QFrame.statusItemFrame {
              background-color: white;
            }
        """)
        
        # Tạo layout chính
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(30, 30, 30, 30)
        self.verticalLayout.setSpacing(15)
        
        # Layout logo
        self.logoLayout = QtWidgets.QVBoxLayout()
        self.logoLayout.setSpacing(15)
        
        # Logo
        self.logoLabel = QtWidgets.QLabel()
        self.logoLabel.setMinimumSize(70, 70)
        self.logoLabel.setMaximumSize(70, 70)
        self.logoLabel.setScaledContents(True)
        self.logoLayout.addWidget(self.logoLabel, 0, QtCore.Qt.AlignHCenter)
        
        # Tiêu đề
        self.titleLabel = QtWidgets.QLabel("Telegram Video Uploader")
        self.titleLabel.setObjectName("titleLabel")
        self.logoLayout.addWidget(self.titleLabel, 0, QtCore.Qt.AlignHCenter)
        
        self.verticalLayout.addLayout(self.logoLayout)
        
        # Layout nội dung
        self.contentLayout = QtWidgets.QVBoxLayout()
        self.contentLayout.setSpacing(20)
        
        # Khung cuộn trạng thái
        self.statusScrollArea = QtWidgets.QScrollArea()
        self.statusScrollArea.setObjectName("statusScrollArea")
        self.statusScrollArea.setMinimumHeight(150)
        self.statusScrollArea.setMaximumHeight(150)
        self.statusScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.statusScrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.statusScrollArea.setWidgetResizable(True)
        
        # Nội dung khung cuộn
        self.scrollAreaContents = QtWidgets.QWidget()
        self.scrollAreaContents.setObjectName("scrollAreaContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaContents)
        
        # Tạo các mục trạng thái
        self.status_items = []
        self.indicator_labels = []
        self.status_labels = []
        
        setup_items = [
            "Kiểm tra cấu hình hệ thống",
            "Khởi tạo tài nguyên ứng dụng",
            "Chuẩn bị bộ phân tích video",
            "Kiểm tra kết nối",
            "Tải các thành phần giao diện",
            "Kiểm tra không gian lưu trữ",
            "Tìm kiếm cập nhật",
            "Tối ưu hóa hiệu suất"
        ]
        
        for i, item_text in enumerate(setup_items):
            # Frame cho mục
            status_item = QtWidgets.QFrame()
            status_item.setObjectName(f"statusItem{i+1}")
            status_item.setFrameShape(QtWidgets.QFrame.StyledPanel)
            status_item.setFrameShadow(QtWidgets.QFrame.Raised)
            status_item.setProperty("class", "statusItemFrame")
            
            # Layout cho mục
            horizontalLayout = QtWidgets.QHBoxLayout(status_item)
            horizontalLayout.setContentsMargins(10, 5, 10, 5)
            
            # Indicator
            indicator = QtWidgets.QLabel()
            indicator.setObjectName(f"indicator{i+1}")
            indicator.setMinimumSize(20, 20)
            indicator.setMaximumSize(20, 20)
            horizontalLayout.addWidget(indicator)
            self.indicator_labels.append(indicator)
            
            # Label
            label = QtWidgets.QLabel(item_text)
            label.setObjectName(f"label{i+1}")
            if i < 3:
                label.setProperty("class", "statusItem")
            else:
                label.setProperty("class", "statusItemPending")
            horizontalLayout.addWidget(label)
            self.status_labels.append(label)
            
            # Thêm vào layout
            self.verticalLayout_2.addWidget(status_item)
            self.status_items.append(status_item)
        
        self.statusScrollArea.setWidget(self.scrollAreaContents)
        self.contentLayout.addWidget(self.statusScrollArea)
        
        # Thanh tiến trình
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setValue(0)
        self.contentLayout.addWidget(self.progressBar)
        
        # Nhãn trạng thái
        self.statusLabel = QtWidgets.QLabel("Đang chuẩn bị...")
        self.statusLabel.setObjectName("statusLabel")
        self.contentLayout.addWidget(self.statusLabel, 0, QtCore.Qt.AlignHCenter)
        
        self.verticalLayout.addLayout(self.contentLayout)
    
    def setup_logo(self):
        """Tạo logo với biểu tượng play"""
        # Tạo pixmap trống với kích thước 70x70
        pixmap = QtGui.QPixmap(70, 70)
        pixmap.fill(Qt.transparent)
        
        # Tạo painter để vẽ
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Vẽ hình tròn xanh dương
        painter.setPen(Qt.NoPen)
        painter.setBrush(QtGui.QColor("#3498DB"))
        painter.drawEllipse(0, 0, 70, 70)
        
        # Vẽ biểu tượng play màu trắng
        painter.setBrush(QtGui.QColor("white"))
        triangle = QtGui.QPolygon([
            QtCore.QPoint(50, 35),
            QtCore.QPoint(25, 50),
            QtCore.QPoint(25, 20)
        ])
        painter.drawPolygon(triangle)
        painter.end()
        
        # Gán pixmap vào label
        self.logoLabel.setPixmap(pixmap)
    
    def setup_indicators(self):
        """Thiết lập indicators cho trạng thái"""
        for i in range(len(self.indicator_labels)):
            # Tạo pixmap trống với kích thước 20x20
            pixmap = QtGui.QPixmap(20, 20)
            pixmap.fill(Qt.transparent)
            
            painter = QtGui.QPainter(pixmap)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            
            # Vẽ indicator tùy theo trạng thái
            if i <= 1:  # Các mục đã hoàn thành
                # Vẽ vòng tròn màu xanh lá
                painter.setPen(Qt.NoPen)
                painter.setBrush(QtGui.QColor("#2ECC71"))
                painter.drawEllipse(2, 2, 16, 16)
                
                # Vẽ dấu tích
                painter.setPen(QtGui.QPen(QtGui.QColor("white"), 2))
                painter.drawLine(6, 10, 9, 13)
                painter.drawLine(9, 13, 14, 7)
            elif i == 2:  # Mục đang thực hiện
                # Vẽ vòng tròn màu xanh dương
                painter.setPen(Qt.NoPen)
                painter.setBrush(QtGui.QColor("#3498DB"))
                painter.drawEllipse(2, 2, 16, 16)
            else:  # Các mục chờ
                # Vẽ vòng tròn màu xám
                painter.setPen(Qt.NoPen)
                painter.setBrush(QtGui.QColor("#e0e0e0"))
                painter.drawEllipse(2, 2, 16, 16)
            
            painter.end()
            
            # Gán pixmap vào indicator
            self.indicator_labels[i].setPixmap(pixmap)
    
    def update_indicator(self, index, status):
        """
        Cập nhật trạng thái của một indicator
        
        Args:
            index: Chỉ số của indicator (bắt đầu từ 0)
            status: Trạng thái ("completed", "current", "pending")
        """
        # Kiểm tra chỉ số hợp lệ
        if index < 0 or index >= len(self.indicator_labels):
            return
            
        # Tạo pixmap mới
        pixmap = QtGui.QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Vẽ vòng tròn và nội dung tùy thuộc vào trạng thái
        if status == "completed":
            # Vẽ vòng tròn màu xanh lá (đã hoàn thành)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QtGui.QColor("#2ECC71"))
            painter.drawEllipse(2, 2, 16, 16)
            
            # Vẽ dấu tích
            painter.setPen(QtGui.QPen(QtGui.QColor("white"), 2))
            painter.drawLine(6, 10, 9, 13)
            painter.drawLine(9, 13, 14, 7)
            
            # Cập nhật style của label
            self.status_labels[index].setProperty("class", "statusItem")
        elif status == "current":
            # Vẽ vòng tròn màu xanh dương (đang thực hiện)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QtGui.QColor("#3498DB"))
            painter.drawEllipse(2, 2, 16, 16)
            
            # Cập nhật style của label
            self.status_labels[index].setProperty("class", "statusItem")
        else:  # pending
            # Vẽ vòng tròn màu xám (chờ thực hiện)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QtGui.QColor("#e0e0e0"))
            painter.drawEllipse(2, 2, 16, 16)
            
            # Cập nhật style của label
            self.status_labels[index].setProperty("class", "statusItemPending")
        
        painter.end()
        
        # Cập nhật pixmap
        self.indicator_labels[index].setPixmap(pixmap)
        
        # Cập nhật style
        style = self.style()
        style.unpolish(self.status_labels[index])
        style.polish(self.status_labels[index])
    
    def next_step(self):
        """Chuyển sang bước tiếp theo"""
        if self.current_step < self.total_steps:
            # Đánh dấu bước trước là hoàn thành nếu có
            if self.current_step > 0:
                self.update_indicator(self.current_step - 1, "completed")
            
            # Đánh dấu bước hiện tại là đang thực hiện
            self.update_indicator(self.current_step, "current")
            
            # Cuộn đến mục hiện tại
            current_item = self.status_items[self.current_step]
            self.statusScrollArea.ensureWidgetVisible(current_item)
            
            # Cập nhật nhãn trạng thái
            status_text = self.status_labels[self.current_step].text()
            self.statusLabel.setText(f"Đang {status_text.lower()}...")
            
            # Cập nhật thanh tiến trình
            progress = int((self.current_step + 1) / self.total_steps * 100)
            self.progressBar.setValue(progress)
            
            # Tăng bước
            self.current_step += 1
            
            return True
        else:
            # Hoàn thành tất cả các bước
            self.statusLabel.setText("Đã sẵn sàng khởi động...")
            self.progressBar.setValue(100)
            return False

def show_splash_screen(app):
    """
    Hiển thị splash screen khi khởi động ứng dụng
    
    Args:
        app: Đối tượng TelegramUploaderApp
    """
    # Tạo splash screen
    splash = SplashScreen(app=app)
    splash.show()
    
    # Cập nhật giao diện
    QtCore.QCoreApplication.processEvents()
    
    # Mô phỏng các bước khởi động
    simulate_setup(app, splash)
    
def simulate_setup(app, splash):
    """
    Mô phỏng quá trình cài đặt
    
    Args:
        app: Đối tượng TelegramUploaderApp
        splash: SplashScreen instance
    """
    total_steps = len(splash.status_items)
    
    # Tạo timer cho từng bước
    timers = []
    for i in range(total_steps):
        timer = QtCore.QTimer(splash)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: process_step(i))
        timers.append(timer)
    
    # Hàm xử lý từng bước
    def process_step(step_index):
        # Chuyển sang bước tiếp theo
        has_more = splash.next_step()
        
        # Nếu còn bước tiếp theo, xử lý
        if has_more and step_index < total_steps - 1:
            # Thời gian mô phỏng cho bước tiếp theo (300-800ms)
            delay = 300 + (step_index * 50)
            timers[step_index + 1].start(delay)
        elif not has_more or step_index >= total_steps - 1:
            # Đã hoàn thành, đóng splash sau 1 giây
            QtCore.QTimer.singleShot(1000, splash.close)
    
    # Bắt đầu bước đầu tiên
    timers[0].start(300)
    
    # Hiển thị splash và xử lý sự kiện
    while splash.isVisible():
        app.root.update()
        QtCore.QCoreApplication.processEvents()

if __name__ == "__main__":
    # Test splash screen
    app = QtWidgets.QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    
    # Mô phỏng xử lý
    timer = QtCore.QTimer()
    timer.timeout.connect(splash.next_step)
    timer.start(300)
    
    sys.exit(app.exec_())