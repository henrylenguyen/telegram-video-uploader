"""
Dialog cảnh báo phiên bản Python không đủ yêu cầu
"""
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtCore import Qt
import os
import sys
import logging
import subprocess
import platform
import shutil

# Thử import QtSvg, nhưng không báo lỗi nếu không tìm thấy
try:
    from PyQt5 import QtSvg
    HAS_QTSVG = True
except ImportError:
    HAS_QTSVG = False

logger = logging.getLogger("PythonVersionDialog")

class PythonVersionDialog(QtWidgets.QDialog):
    """
    Dialog thông báo phiên bản Python không đủ yêu cầu
    """
    
    # Định nghĩa các kết quả khi dialog đóng
    DOWNLOAD_PYTHON = 1
    CONTINUE_ANYWAY = 2
    EXIT_APP = 3
    CREATE_VENV = 4
    
    def __init__(self, parent=None, current_version="", min_version="3.7.0"):
        super(PythonVersionDialog, self).__init__(parent, Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint)
        
        # Nạp UI từ file
        ui_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qt_designer", "python_version_dialog.ui")
        
        # Nếu không tìm thấy file UI, sử dụng đường dẫn khác
        if not os.path.exists(ui_file):
            ui_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui", "qt_designer", "python_version_dialog.ui")
        
        if os.path.exists(ui_file):
            uic.loadUi(ui_file, self)
        else:
            # Nếu không tìm thấy file UI, tạo dialog đơn giản
            logger.error(f"Không tìm thấy file UI: {ui_file}")
            self.setup_ui_manually()
        
        # Cập nhật nhãn phiên bản
        if hasattr(self, 'versionLabel'):
            self.versionLabel.setText(f"Phiên bản hiện tại: Python {current_version}")
        
        # Cập nhật nhãn tiêu đề
        if hasattr(self, 'titleLabel'):
            self.titleLabel.setText(f"Ứng dụng yêu cầu Python {min_version} trở lên.")
        
        # Kiểm tra biểu tượng cảnh báo
        if hasattr(self, 'iconLabel'):
            warning_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons", "warning.png")
            
            if not os.path.exists(warning_icon_path):
                # Nếu chưa có, tạo biểu tượng cảnh báo mặc định
                self.create_warning_icon(warning_icon_path)
            
            # Đặt biểu tượng cảnh báo
            self.iconLabel.setPixmap(QtGui.QPixmap(warning_icon_path))
        
        # Kiểm tra xem có thể tạo virtualenv không
        has_virtualenv = self.check_virtualenv()
        
        # Ẩn nút tạo môi trường ảo nếu không có virtualenv
        if hasattr(self, 'venvButton') and not has_virtualenv:
            self.venvButton.setVisible(False)
        
        # Kết nối các nút với hành động
        if hasattr(self, 'downloadButton'):
            self.downloadButton.clicked.connect(self.on_download_clicked)
        
        if hasattr(self, 'continueButton'):
            self.continueButton.clicked.connect(self.on_continue_clicked)
        
        if hasattr(self, 'exitButton'):
            self.exitButton.clicked.connect(self.on_exit_clicked)
        
        if hasattr(self, 'venvButton'):
            self.venvButton.clicked.connect(self.on_venv_clicked)
    
    def setup_ui_manually(self):
        """Thiết lập UI thủ công nếu không tìm thấy file UI"""
        self.setWindowTitle("Phiên bản Python không hỗ trợ")
        self.resize(400, 200)
        
        # Tạo layout
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Tạo icon và nhãn
        icon_label = QtWidgets.QLabel()
        icon_label.setFixedSize(48, 48)
        self.iconLabel = icon_label
        
        # Tạo nhãn tiêu đề
        title_label = QtWidgets.QLabel("Ứng dụng yêu cầu Python 3.7.0 trở lên.")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.titleLabel = title_label
        
        # Tạo nhãn thông báo
        message_label = QtWidgets.QLabel("Bạn muốn làm gì để giải quyết vấn đề này?")
        self.messageLabel = message_label
        
        # Tạo nhãn phiên bản
        version_label = QtWidgets.QLabel("Phiên bản hiện tại: Python X.X.X")
        version_label.setAlignment(Qt.AlignCenter)
        self.versionLabel = version_label
        
        # Tạo các nút
        button_layout = QtWidgets.QHBoxLayout()
        
        download_button = QtWidgets.QPushButton("Tải Python mới")
        download_button.setStyleSheet("background-color: #3498db; color: white;")
        self.downloadButton = download_button
        
        continue_button = QtWidgets.QPushButton("Tiếp tục dù vậy")
        continue_button.setStyleSheet("color: #7f8c8d;")
        self.continueButton = continue_button
        
        exit_button = QtWidgets.QPushButton("Thoát")
        exit_button.setStyleSheet("background-color: #e74c3c; color: white;")
        self.exitButton = exit_button
        
        venv_button = QtWidgets.QPushButton("Tạo môi trường ảo")
        venv_button.setStyleSheet("background-color: #2ecc71; color: white;")
        self.venvButton = venv_button
        
        # Thêm các nút vào layout
        button_layout.addWidget(download_button)
        button_layout.addWidget(continue_button)
        button_layout.addWidget(exit_button)
        button_layout.addWidget(venv_button)
        
        # Tạo layout cho icon và text
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(icon_label)
        
        text_layout = QtWidgets.QVBoxLayout()
        text_layout.addWidget(title_label)
        text_layout.addWidget(message_label)
        
        header_layout.addLayout(text_layout)
        
        # Thêm các thành phần vào layout chính
        main_layout.addLayout(header_layout)
        main_layout.addWidget(QtWidgets.QFrame(frameShape=QtWidgets.QFrame.HLine))
        main_layout.addLayout(button_layout)
        main_layout.addWidget(version_label)
    
    def create_warning_icon(self, path):
        """Tạo biểu tượng cảnh báo nếu không tìm thấy"""
        try:
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Kiểm tra xem có file SVG không và có thể sử dụng QtSvg không
            svg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons", "warning.svg")
            if os.path.exists(svg_path) and HAS_QTSVG:
                # Chuyển đổi SVG sang pixmap
                renderer = QtSvg.QSvgRenderer(svg_path)
                pixmap = QtGui.QPixmap(48, 48)
                pixmap.fill(Qt.transparent)
                painter = QtGui.QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                pixmap.save(path, "PNG")
                return
            
            # Tạo hình ảnh cảnh báo
            pixmap = QtGui.QPixmap(48, 48)
            pixmap.fill(Qt.transparent)
            
            painter = QtGui.QPainter(pixmap)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            
            # Vẽ tam giác vàng
            warning_path = QtGui.QPainterPath()
            warning_path.moveTo(24, 4)
            warning_path.lineTo(44, 44)
            warning_path.lineTo(4, 44)
            warning_path.lineTo(24, 4)
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QtGui.QColor("#FFC107"))
            painter.drawPath(warning_path)
            
            # Vẽ dấu chấm than
            painter.setPen(QtGui.QPen(Qt.black, 4))
            painter.drawLine(24, 20, 24, 32)
            painter.drawPoint(24, 38)
            
            painter.end()
            
            # Lưu pixmap
            pixmap.save(path, "PNG")
        except Exception as e:
            logger.error(f"Lỗi khi tạo biểu tượng cảnh báo: {str(e)}")
    
    def check_virtualenv(self):
        """Kiểm tra xem virtualenv có sẵn không"""
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "show", "virtualenv"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return True
        except:
            return False
    
    def on_download_clicked(self):
        """Xử lý khi người dùng chọn tải Python mới"""
        import webbrowser
        webbrowser.open("https://www.python.org/downloads/")
        
        # Thông báo cho người dùng biết phải làm gì sau khi cài đặt
        QtWidgets.QMessageBox.information(
            self,
            "Hướng dẫn",
            "Sau khi cài đặt Python mới, vui lòng khởi động lại ứng dụng.",
            QtWidgets.QMessageBox.Ok
        )
        
        self.done(self.DOWNLOAD_PYTHON)
    
    def on_continue_clicked(self):
        """Xử lý khi người dùng chọn tiếp tục dù phiên bản Python không đủ"""
        self.done(self.CONTINUE_ANYWAY)
    
    def on_exit_clicked(self):
        """Xử lý khi người dùng chọn thoát"""
        self.done(self.EXIT_APP)
    
    def on_venv_clicked(self):
        """Xử lý khi người dùng chọn tạo môi trường ảo"""
        self.done(self.CREATE_VENV)

if __name__ == "__main__":
    # Test dialog
    app = QtWidgets.QApplication(sys.argv)
    dialog = PythonVersionDialog(current_version="3.6.5")
    result = dialog.exec_()
    print(f"Kết quả: {result}")
    sys.exit(app.exec_()) 