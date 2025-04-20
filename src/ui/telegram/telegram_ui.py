"""
Module giao diện Telegram cho Telegram Video Uploader
"""
import sys
import os
import logging
import traceback
from PyQt5 import QtWidgets, QtCore, QtGui, uic

# Import các module con
from ui.telegram.telegram_ui_init import (
    apply_global_stylesheet,
    load_ui_components,
    get_ui_dir,
    fix_ui_file,
    update_cursor_properties,
    load_config_modal,
    load_otp_modal
)

# Import fallback UI
from ui.telegram.telegram_ui_fallbacks import (
    create_fallback_config_modal,
    create_fallback_otp_modal
)

# Import xử lý sự kiện
from ui.telegram.telegram_ui_events import (
    connect_signals,
    on_check_connection_clicked,
    on_save_config_clicked,
    request_otp,
    on_tab_changed
)

# Import quản lý cấu hình 
from ui.telegram.telegram_ui_config import (
    load_existing_config,
    save_config,
    save_draft,
    validate_config
)

# Import các hàm xử lý OTP
from ui.telegram.telegram_ui_otp import (
    verify_otp_code,
    request_telethon_code,
    on_otp_verification_success
)

# Configure logging
logger = logging.getLogger("TelegramUI")

class TelegramTestThread(QtCore.QThread):
    """Thread kiểm tra kết nối Telegram"""
    resultReady = QtCore.pyqtSignal(bool, str)
    
    def __init__(self, bot_token, chat_id, app):
        super(TelegramTestThread, self).__init__()
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.app = app
    
    def run(self):
        """Thực hiện kiểm tra kết nối"""
        try:
            # Lấy telegram_api từ ứng dụng
            telegram_api = self.app.telegram_api
            
            # Kết nối với token mới
            if telegram_api.connect(self.bot_token):
                # Thử gửi một tin nhắn kiểm tra
                result = telegram_api.test_connection(self.chat_id)
                
                if result and 'username' in result:
                    # Thành công, trả về username của bot
                    self.resultReady.emit(True, result['username'])
                else:
                    # Kết nối thành công nhưng thử nghiệm thất bại
                    self.resultReady.emit(False, "Không thể gửi tin nhắn kiểm tra")
            else:
                # Kết nối thất bại
                self.resultReady.emit(False, "Token không hợp lệ hoặc bot không hoạt động")
        except Exception as e:
            # Lỗi không xác định
            self.resultReady.emit(False, str(e))

class ConfigModal(QtWidgets.QDialog):
    """
    Modal cấu hình Telegram
    """
    # Tín hiệu khi cấu hình được lưu
    configSaved = QtCore.pyqtSignal(bool)
    
    def __init__(self, parent=None, app=None, force_manual_ui=False):
        super(ConfigModal, self).__init__(parent)
        
        # Lưu tham chiếu đến ứng dụng
        self.app = app
        self.telegram_connected = False
        self.telethon_connected = False
        
        # Đặt tiêu đề cho dialog
        self.setWindowTitle("Cấu hình Telegram")
        
        # Tạo layout chính
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.layout)
        
        # Xác định file UI
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file = os.path.join(ui_dir, "..", "qt_designer", "config_modal.ui")
        
        # Kiểm tra xem người dùng có yêu cầu sử dụng UI thủ công không
        if force_manual_ui:
            logger.info("Đã chọn ưu tiên UI thủ công.")
            self.setup_ui_manually()
        else:
            # Tải UI từ file nếu tồn tại
            if not os.path.exists(ui_file):
                logger.warning(f"Không tìm thấy file UI: {ui_file}. Sử dụng UI thủ công.")
                self.setup_ui_manually()
            else:
                try:
                    # Sửa file UI để xử lý các vấn đề tương thích
                    fixed_ui_path = self.fix_ui_file(ui_file)
                    logger.info(f"Đang tải UI từ file: {fixed_ui_path}")
                    
                    # Tải UI từ file đã được sửa
                    uic.loadUi(fixed_ui_path, self)
                    logger.info("Đã tải UI từ file thành công")
                    
                    # Tìm các thành phần UI
                    self._collect_ui_components()
                    
                    # Kết nối các sự kiện
                    self._connect_signals()
                except Exception as e:
                    logger.error(f"Lỗi khi tải UI từ file: {str(e)}")
                    logger.error(f"Chi tiết lỗi:")
                    logger.error(traceback.format_exc())
                    
                    # Chuyển sang sử dụng UI thủ công
                    logger.info("Đang tạo UI thủ công do lỗi khi tải file UI")
                    self.setup_ui_manually()
        
        # Tải cấu hình hiện có
        self.load_existing_config()
        
        # Căn giữa và thiết lập kích thước
        self.resize(600, 700)
        self.center_on_screen()
        
        # Kích hoạt bước wizard đầu tiên
        self.activate_wizard_step(1)
    
    # Import methods from modules
    load_ui_components = load_ui_components
    get_ui_dir = get_ui_dir
    fix_ui_file = fix_ui_file
    update_cursor_properties = update_cursor_properties
    
    # Thêm phương thức apply_global_stylesheet trực tiếp
    def apply_global_stylesheet(self):
        """Áp dụng stylesheet toàn cầu cho các thành phần Telegram"""
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                font-family: Arial;
            }
            
            QLabel {
                color: #1E293B;
            }
            
            QLabel.titleLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1E293B;
            }
            
            QLabel.stepLabel {
                font-size: 16px;
                font-weight: bold;
            }
            
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background-color: #2563EB;
            }
            
            QPushButton:disabled {
                background-color: #CBD5E1;
                color: #94A3B8;
            }
            
            QLineEdit {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                background-color: #F8FAFC;
            }
            
            QTabWidget::pane {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 10px;
            }
            
            QTabBar::tab {
                background-color: #F1F5F9;
                color: #64748B;
                padding: 10px 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            
            QTabBar::tab:selected {
                background-color: #3B82F6;
                color: white;
            }
        """)
    
    # Thêm phương thức check_telegram_connection
    def check_telegram_connection(self):
        """
        Kiểm tra kết nối với Telegram Bot API
        """
        # Lấy thông tin token và chat ID
        bot_token = self.botTokenEdit.text().strip()
        chat_id = self.chatIdEdit.text().strip()
        
        # Kiểm tra dữ liệu đầu vào
        if not bot_token:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Vui lòng nhập Bot Token!")
            return
        
        if not chat_id:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Vui lòng nhập Chat ID!")
            return
        
        # Vô hiệu hóa nút và thay đổi text
        self.btnCheckConnection.setEnabled(False)
        self.btnCheckConnection.setText("Đang kiểm tra...")
        
        # Tạo thread kiểm tra kết nối
        self.test_thread = TelegramTestThread(bot_token, chat_id, self.app)
        self.test_thread.resultReady.connect(self.on_telegram_check_result)
        self.test_thread.start()
    
    # Config handling
    load_existing_config = load_existing_config
    save_config = save_config
    save_draft = save_draft
    validate_config = validate_config
    
    # Event handlers
    connect_signals = connect_signals
    on_check_connection_clicked = on_check_connection_clicked
    on_save_config_clicked = on_save_config_clicked
    request_otp = request_otp
    on_tab_changed = on_tab_changed
    
    # OTP handling
    verify_otp_code = verify_otp_code
    request_telethon_code = request_telethon_code
    on_otp_verification_success = on_otp_verification_success
    
    def _collect_ui_components(self):
        """Tìm và lưu tham chiếu đến các thành phần UI"""
        # Tab control
        self.tabWidget = self.findChild(QtWidgets.QTabWidget, "tabWidget")
        
        # Wizard steps
        self.step1Label = self.findChild(QtWidgets.QLabel, "step1Label")
        self.step2Label = self.findChild(QtWidgets.QLabel, "step2Label")
        self.step1Text = self.findChild(QtWidgets.QLabel, "step1Text")
        self.step2Text = self.findChild(QtWidgets.QLabel, "step2Text")
        
        # Bot API controls
        self.botTokenEdit = self.findChild(QtWidgets.QLineEdit, "botTokenEdit")
        self.chatIdEdit = self.findChild(QtWidgets.QLineEdit, "chatIdEdit")
        self.btnCheckConnection = self.findChild(QtWidgets.QPushButton, "btnCheckConnection")
        
        # Telethon controls
        self.apiIdEdit = self.findChild(QtWidgets.QLineEdit, "apiIdEdit")
        self.apiHashEdit = self.findChild(QtWidgets.QLineEdit, "apiHashEdit")
        self.phoneEdit = self.findChild(QtWidgets.QLineEdit, "phoneEdit")
        self.requestOtpButton = self.findChild(QtWidgets.QPushButton, "requestOtpButton")
        
        # Kết quả check
        self.connectionResultLabel = self.findChild(QtWidgets.QLabel, "connectionResultLabel")
    
    def _connect_signals(self):
        """Kết nối các sự kiện"""
        # Kết nối nút kiểm tra kết nối
        if self.btnCheckConnection:
            self.btnCheckConnection.clicked.connect(self.check_telegram_connection)
        
        # Kết nối nút yêu cầu OTP
        if self.requestOtpButton:
            self.requestOtpButton.clicked.connect(self.request_telethon_code)
    
    def center_on_screen(self):
        """Căn giữa cửa sổ trên màn hình"""
        frame_geometry = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(
            QtWidgets.QApplication.desktop().cursor().pos()
        )
        center_point = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
    
    def setup_ui_manually(self):
        """Tạo UI thủ công khi không thể tải từ file UI"""
        # Áp dụng stylesheet toàn cục
        self.apply_global_stylesheet()
        
        # Xóa tất cả các widget trong layout hiện tại
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Thêm tiêu đề
        title_label = QtWidgets.QLabel("Cấu hình Telegram")
        title_label.setProperty("class", "titleLabel")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(title_label)
        
        # Tạo wizard steps
        wizard_container = QtWidgets.QWidget()
        wizard_layout = QtWidgets.QHBoxLayout(wizard_container)
        
        # Step 1
        step1_container = QtWidgets.QWidget()
        step1_layout = QtWidgets.QVBoxLayout(step1_container)
        self.step1Label = QtWidgets.QLabel("1")
        self.step1Label.setStyleSheet("""
            background-color: #3B82F6;
            color: white;
            border-radius: 15px;
            font-weight: bold;
        """)
        self.step1Label.setAlignment(QtCore.Qt.AlignCenter)
        self.step1Label.setFixedSize(30, 30)
        
        self.step1Text = QtWidgets.QLabel("Cấu hình Telegram Bot API")
        self.step1Text.setStyleSheet("color: #1E40AF; font-weight: bold;")
        
        step1_layout.addWidget(self.step1Label, alignment=QtCore.Qt.AlignCenter)
        step1_layout.addWidget(self.step1Text, alignment=QtCore.Qt.AlignCenter)
        
        # Step 2
        step2_container = QtWidgets.QWidget()
        step2_layout = QtWidgets.QVBoxLayout(step2_container)
        self.step2Label = QtWidgets.QLabel("2")
        self.step2Label.setStyleSheet("""
            background-color: #CBD5E1;
            color: #64748B;
            border-radius: 15px;
            font-weight: normal;
        """)
        self.step2Label.setAlignment(QtCore.Qt.AlignCenter)
        self.step2Label.setFixedSize(30, 30)
        
        self.step2Text = QtWidgets.QLabel("Cấu hình Telethon API")
        self.step2Text.setStyleSheet("color: #64748B; font-weight: normal;")
        
        step2_layout.addWidget(self.step2Label, alignment=QtCore.Qt.AlignCenter)
        step2_layout.addWidget(self.step2Text, alignment=QtCore.Qt.AlignCenter)
        
        # Thêm các steps vào wizard layout
        wizard_layout.addWidget(step1_container)
        wizard_layout.addWidget(QtWidgets.QLabel("―――"), alignment=QtCore.Qt.AlignCenter)
        wizard_layout.addWidget(step2_container)
        
        # Thêm wizard vào layout chính
        self.layout.addWidget(wizard_container)
        
        # Tạo tab widget
        self.tabWidget = QtWidgets.QTabWidget()
        
        # Tab 1: Telegram Bot API
        tab1 = QtWidgets.QWidget()
        tab1_layout = QtWidgets.QVBoxLayout(tab1)
        
        # Thêm hướng dẫn
        guide_label = QtWidgets.QLabel("Để sử dụng ứng dụng, bạn cần cấu hình Telegram Bot API bằng cách tạo bot với @BotFather và cung cấp token cùng với chat ID của nhóm nơi bạn muốn tải video lên.")
        guide_label.setWordWrap(True)
        tab1_layout.addWidget(guide_label)
        
        # Thêm form
        form_layout = QtWidgets.QFormLayout()
        
        # Token Telegram Bot
        token_label = QtWidgets.QLabel("Token Telegram Bot")
        self.botTokenEdit = QtWidgets.QLineEdit()
        self.botTokenEdit.setPlaceholderText("Nhập token bot (vd: 123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw)")
        form_layout.addRow(token_label, self.botTokenEdit)
        
        # Chat ID
        chat_id_label = QtWidgets.QLabel("Chat ID")
        self.chatIdEdit = QtWidgets.QLineEdit()
        self.chatIdEdit.setPlaceholderText("Nhập chat ID (vd: -1001234567890)")
        form_layout.addRow(chat_id_label, self.chatIdEdit)
        
        # Thêm kết quả kiểm tra
        self.connectionResultLabel = QtWidgets.QLabel("")
        form_layout.addRow("", self.connectionResultLabel)
        
        # Thêm form vào layout
        tab1_layout.addLayout(form_layout)
        
        # Thêm nút kiểm tra kết nối
        self.btnCheckConnection = QtWidgets.QPushButton("Kiểm tra kết nối")
        tab1_layout.addWidget(self.btnCheckConnection)
        
        # Thêm khoảng trống
        tab1_layout.addStretch()
        
        # Tab 2: Telethon API
        tab2 = QtWidgets.QWidget()
        tab2_layout = QtWidgets.QVBoxLayout(tab2)
        
        # Thêm hướng dẫn
        telethon_guide = QtWidgets.QLabel("Để tải video lớn hơn 50MB, bạn cần cấu hình Telethon API. Đăng ký ứng dụng tại my.telegram.org.")
        telethon_guide.setWordWrap(True)
        tab2_layout.addWidget(telethon_guide)
        
        # Thêm form Telethon
        telethon_form = QtWidgets.QFormLayout()
        
        # API ID
        api_id_label = QtWidgets.QLabel("API ID")
        self.apiIdEdit = QtWidgets.QLineEdit()
        self.apiIdEdit.setPlaceholderText("Nhập API ID (vd: 123456)")
        telethon_form.addRow(api_id_label, self.apiIdEdit)
        
        # API Hash
        api_hash_label = QtWidgets.QLabel("API Hash")
        self.apiHashEdit = QtWidgets.QLineEdit()
        self.apiHashEdit.setPlaceholderText("Nhập API Hash (vd: 0123456789abcdef0123456789abcdef)")
        telethon_form.addRow(api_hash_label, self.apiHashEdit)
        
        # Số điện thoại
        phone_label = QtWidgets.QLabel("Số điện thoại")
        self.phoneEdit = QtWidgets.QLineEdit()
        self.phoneEdit.setPlaceholderText("Nhập số điện thoại (vd: +84123456789)")
        telethon_form.addRow(phone_label, self.phoneEdit)
        
        # Thêm form vào layout
        tab2_layout.addLayout(telethon_form)
        
        # Nút yêu cầu OTP
        self.requestOtpButton = QtWidgets.QPushButton("Gửi mã xác thực")
        tab2_layout.addWidget(self.requestOtpButton)
        
        # Thêm khoảng trống
        tab2_layout.addStretch()
        
        # Thêm tabs vào tab widget
        self.tabWidget.addTab(tab1, "Telegram Bot API")
        self.tabWidget.addTab(tab2, "Telethon API")
        
        # Thêm tab widget vào layout chính
        self.layout.addWidget(self.tabWidget)
        
        # Kết nối sự kiện
        self._connect_signals()
    
    def on_telegram_check_result(self, success, message):
        """
        Xử lý kết quả kiểm tra kết nối Telegram
        
        Args:
            success: Kết nối thành công hay không
            message: Thông báo kết quả
        """
        # Enable lại nút kiểm tra
        self.btnCheckConnection.setEnabled(True)
        
        if success:
            # Cập nhật giao diện khi kết nối thành công
            self.btnCheckConnection.setText("Lưu cài đặt")
            self.btnCheckConnection.setStyleSheet("""
                QPushButton {
                    background-color: #1E40AF;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 15px;
                    font-size: 16px;
                    font-weight: bold;
                }
                
                QPushButton:hover {
                    background-color: #1E3A8A;
                }
            """)
            
            # Ngắt kết nối sự kiện click cũ và kết nối mới
            try:
                self.btnCheckConnection.clicked.disconnect(self.check_telegram_connection)
            except TypeError:
                # Có thể signal chưa được kết nối
                pass
                
            self.btnCheckConnection.clicked.connect(self.save_bot_and_switch_tab)
            self.telegram_connected = True
            
            # Hiển thị thông báo thành công
            QtWidgets.QMessageBox.information(self, "Thành công", 
                f"Kết nối thành công đến bot @{message}!\nNhấn 'Lưu cài đặt' để tiếp tục với bước tiếp theo.")
        else:
            # Hiển thị lỗi nếu kết nối thất bại
            QtWidgets.QMessageBox.critical(self, "Lỗi kết nối", 
                f"Không thể kết nối đến Telegram Bot API: {message}")
            
            # Giữ nguyên text của nút
            self.btnCheckConnection.setText("Kiểm tra kết nối")
            
        # Cập nhật trạng thái UI
        if hasattr(self, 'connectionResultLabel') and self.connectionResultLabel:
            if success:
                self.connectionResultLabel.setText(f"✅ Đã kết nối tới bot @{message}")
                self.connectionResultLabel.setStyleSheet("color: green;")
            else:
                self.connectionResultLabel.setText(f"❌ Lỗi kết nối: {message}")
                self.connectionResultLabel.setStyleSheet("color: red;")
    
    def activate_wizard_step(self, step):
        """
        Kích hoạt bước wizard
        
        Args:
            step: Bước cần kích hoạt (1 hoặc 2)
        """
        if step == 1:
            # Kích hoạt bước 1, vô hiệu hóa bước 2
            if self.step1Label:
                self.step1Label.setStyleSheet("""
                    background-color: #3B82F6;
                    color: white;
                    border-radius: 15px;
                    font-weight: bold;
                """)
                self.step1Label.setText("1")
                
            if self.step1Text:
                self.step1Text.setStyleSheet("color: #1E40AF; font-weight: bold;")
                
            if self.step2Label:
                self.step2Label.setStyleSheet("""
                    background-color: #CBD5E1;
                    color: #64748B;
                    border-radius: 15px;
                    font-weight: normal;
                """)
                self.step2Label.setText("2")
                
            if self.step2Text:
                self.step2Text.setStyleSheet("color: #64748B; font-weight: normal;")
                
        elif step == 2:
            # Đánh dấu bước 1 hoàn thành, kích hoạt bước 2
            if self.step1Label:
                self.step1Label.setStyleSheet("""
                    background-color: #10B981;
                    color: white;
                    border-radius: 15px;
                    font-weight: bold;
                """)
                self.step1Label.setText("✓")
                
            if self.step1Text:
                self.step1Text.setStyleSheet("color: #059669; font-weight: bold;")
                
            if self.step2Label:
                self.step2Label.setStyleSheet("""
                    background-color: #3B82F6;
                    color: white;
                    border-radius: 15px;
                    font-weight: bold;
                """)
                self.step2Label.setText("2")
                
            if self.step2Text:
                self.step2Text.setStyleSheet("color: #1E40AF; font-weight: bold;")