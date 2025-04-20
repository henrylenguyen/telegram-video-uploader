"""
Các hàm fallback cho UI Telegram khi không thể tải UI từ file
"""
import logging
from PyQt5 import QtWidgets, QtCore

logger = logging.getLogger(__name__)

def create_fallback_config_modal(self):
    """Tạo UI thủ công cho ConfigModal khi không thể tải từ file UI"""
    logger.info("Đang tạo UI thủ công cho ConfigModal")
    
    # Layout chính
    main_layout = QtWidgets.QVBoxLayout()
    
    # Tiêu đề
    title_label = QtWidgets.QLabel("Cấu hình Telegram")
    title_label.setProperty("class", "titleLabel")
    main_layout.addWidget(title_label)
    
    # Tạo tab widget
    self.tabWidget = QtWidgets.QTabWidget()
    
    # Tạo tab Bot API
    bot_tab = QtWidgets.QWidget()
    bot_layout = QtWidgets.QVBoxLayout(bot_tab)
    
    # Thêm các trường nhập
    bot_token_label = QtWidgets.QLabel("Bot Token:")
    self.botTokenEdit = QtWidgets.QLineEdit()
    bot_layout.addWidget(bot_token_label)
    bot_layout.addWidget(self.botTokenEdit)
    
    chat_id_label = QtWidgets.QLabel("Chat ID:")
    self.chatIdEdit = QtWidgets.QLineEdit()
    bot_layout.addWidget(chat_id_label)
    bot_layout.addWidget(self.chatIdEdit)
    
    # Nút kiểm tra kết nối
    self.btnCheckConnection = QtWidgets.QPushButton("Kiểm tra kết nối")
    bot_layout.addWidget(self.btnCheckConnection)
    
    # Nhãn kết quả kết nối
    self.connectionResultLabel = QtWidgets.QLabel("")
    bot_layout.addWidget(self.connectionResultLabel)
    
    # Tạo tab Telethon
    telethon_tab = QtWidgets.QWidget()
    telethon_layout = QtWidgets.QVBoxLayout(telethon_tab)
    
    # Thêm các trường nhập
    api_id_label = QtWidgets.QLabel("API ID:")
    self.apiIdEdit = QtWidgets.QLineEdit()
    telethon_layout.addWidget(api_id_label)
    telethon_layout.addWidget(self.apiIdEdit)
    
    api_hash_label = QtWidgets.QLabel("API Hash:")
    self.apiHashEdit = QtWidgets.QLineEdit()
    telethon_layout.addWidget(api_hash_label)
    telethon_layout.addWidget(self.apiHashEdit)
    
    phone_label = QtWidgets.QLabel("Số điện thoại:")
    self.phoneEdit = QtWidgets.QLineEdit()
    telethon_layout.addWidget(phone_label)
    telethon_layout.addWidget(self.phoneEdit)
    
    # Nút yêu cầu OTP
    self.requestOtpButton = QtWidgets.QPushButton("Yêu cầu mã OTP")
    telethon_layout.addWidget(self.requestOtpButton)
    
    # Thêm tabs vào tabWidget
    self.tabWidget.addTab(bot_tab, "Bot API")
    self.tabWidget.addTab(telethon_tab, "Telethon")
    
    main_layout.addWidget(self.tabWidget)
    
    # Nút lưu cấu hình
    save_button = QtWidgets.QPushButton("Lưu cấu hình")
    main_layout.addWidget(save_button)
    
    # Thiết lập layout chính
    self.setLayout(main_layout)
    
    # Kết nối các sự kiện
    save_button.clicked.connect(self.on_save_config_clicked)
    self.btnCheckConnection.clicked.connect(self.on_check_connection_clicked)
    self.requestOtpButton.clicked.connect(self.request_otp)
    
    # Đặt thuộc tính con trỏ
    save_button.setCursor(QtCore.Qt.PointingHandCursor)
    self.btnCheckConnection.setCursor(QtCore.Qt.PointingHandCursor)
    self.requestOtpButton.setCursor(QtCore.Qt.PointingHandCursor)
    
    # Lưu các thành phần UI khác cần thiết
    self.step1Label = QtWidgets.QLabel("Bước 1")
    self.step2Label = QtWidgets.QLabel("Bước 2")
    self.step1Text = QtWidgets.QLabel("Cấu hình Bot API")
    self.step2Text = QtWidgets.QLabel("Cấu hình Telethon")
    
    logger.info("Đã tạo UI thủ công cho ConfigModal thành công")

def create_fallback_otp_modal(self):
    """Tạo UI thủ công cho OTPModal khi không thể tải từ file UI"""
    logger.info("Đang tạo UI thủ công cho OTPModal")
    
    # Layout chính
    main_layout = QtWidgets.QVBoxLayout()
    
    # Tiêu đề
    title_label = QtWidgets.QLabel("Xác minh OTP")
    title_label.setProperty("class", "titleLabel")
    main_layout.addWidget(title_label)
    
    # Thông báo
    message_label = QtWidgets.QLabel("Vui lòng nhập mã OTP được gửi đến thiết bị của bạn:")
    main_layout.addWidget(message_label)
    
    # Trường nhập OTP
    self.otpEdit = QtWidgets.QLineEdit()
    self.otpEdit.setPlaceholderText("Nhập mã OTP...")
    main_layout.addWidget(self.otpEdit)
    
    # Nút xác nhận
    self.verifyButton = QtWidgets.QPushButton("Xác nhận")
    main_layout.addWidget(self.verifyButton)
    
    # Nhãn trạng thái
    self.statusLabel = QtWidgets.QLabel("")
    main_layout.addWidget(self.statusLabel)
    
    # Thiết lập layout chính
    self.setLayout(main_layout)
    
    # Kết nối sự kiện
    self.verifyButton.clicked.connect(self.verify_otp)
    
    # Đặt thuộc tính con trỏ
    self.verifyButton.setCursor(QtCore.Qt.PointingHandCursor)
    
    logger.info("Đã tạo UI thủ công cho OTPModal thành công")
