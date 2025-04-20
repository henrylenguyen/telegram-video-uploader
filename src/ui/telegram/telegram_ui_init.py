"""
Khởi tạo UI cho các thành phần Telegram
"""
import os
import logging
import tempfile
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtCore import Qt
import traceback

logger = logging.getLogger(__name__)

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

def load_ui_components(self):
    """Tải UI từ file UI"""
    ui_path = os.path.join(self.get_ui_dir(), "config_modal.ui")
    
    # Fix UI file trước khi tải
    fixed_ui_path = self.fix_ui_file(ui_path)
    
    try:
        # Tải UI từ file đã sửa
        uic.loadUi(fixed_ui_path, self)
        logger.info("Đã tải UI config_modal thành công")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi tải UI: {str(e)}")
        return False

def get_ui_dir(self):
    """Lấy thư mục chứa file UI"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "qt_designer")

def fix_ui_file(self, ui_path):
    """Sửa các vấn đề tương thích trong file UI"""
    # Kiểm tra file tồn tại
    if not os.path.exists(ui_path):
        logger.error(f"File UI không tồn tại: {ui_path}")
        return ui_path
        
    try:
        with open(ui_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Các thay thế cơ bản
        # Sửa các thuộc tính orientation
        content = content.replace('Qt::Orientation::Horizontal', 'Horizontal')
        content = content.replace('Qt::Orientation::Vertical', 'Vertical')
        
        # Sửa tham chiếu không có Orientation:: prefix
        content = content.replace('Qt::Horizontal', 'Horizontal')
        content = content.replace('Qt::Vertical', 'Vertical')
        
        # Sửa thuộc tính cursor
        content = content.replace('property="cursor"', 'property="cursorShape"')
        
        # Sửa thuộc tính alignment cho các nút
        content = content.replace('property="alignment"', 'property="alignmentProperty"')
        
        # Sửa các vấn đề với Qt::AlignmentFlag
        content = content.replace('Qt::AlignmentFlag::', '')
        content = content.replace('Qt::AlignLeading', 'AlignLeading')
        content = content.replace('Qt::AlignLeft', 'AlignLeft')
        content = content.replace('Qt::AlignRight', 'AlignRight')
        content = content.replace('Qt::AlignCenter', 'AlignCenter')
        content = content.replace('Qt::AlignTop', 'AlignTop')
        content = content.replace('Qt::AlignBottom', 'AlignBottom')
        content = content.replace('Qt::AlignHCenter', 'AlignHCenter')
        content = content.replace('Qt::AlignVCenter', 'AlignVCenter')
        content = content.replace('Qt::AlignJustify', 'AlignJustify')
        
        # Sửa các vấn đề với Qt::WidgetAttribute
        content = content.replace('Qt::WidgetAttribute::', '')
        content = content.replace('Qt::WA_DeleteOnClose', 'WA_DeleteOnClose')
        
        # Sửa các vấn đề với Qt::WindowModality
        content = content.replace('Qt::WindowModality::', '')
        content = content.replace('Qt::WindowModal', 'WindowModal')
        content = content.replace('Qt::ApplicationModal', 'ApplicationModal')
        
        # Sửa các vấn đề với Qt::FocusPolicy
        content = content.replace('Qt::FocusPolicy::', '')
        content = content.replace('Qt::StrongFocus', 'StrongFocus')
        content = content.replace('Qt::TabFocus', 'TabFocus')
        content = content.replace('Qt::NoFocus', 'NoFocus')
        content = content.replace('Qt::ClickFocus', 'ClickFocus')
        content = content.replace('Qt::WheelFocus', 'WheelFocus')
        
        # Sửa các vấn đề với Qt::WindowFlags
        content = content.replace('Qt::WindowFlags::', '')
        content = content.replace('Qt::Dialog', 'Dialog')
        content = content.replace('Qt::Window', 'Window')
        
        # Thêm xử lý cho EchoMode của QLineEdit
        content = content.replace('QLineEdit::EchoMode::', '')
        content = content.replace('QLineEdit::EchoMode::Normal', 'Normal')
        content = content.replace('QLineEdit::EchoMode::Password', 'Password')
        content = content.replace('QLineEdit::EchoMode::NoEcho', 'NoEcho')
        content = content.replace('QLineEdit::EchoMode::PasswordEchoOnEdit', 'PasswordEchoOnEdit')
        content = content.replace('QLineEdit::Normal', 'Normal')
        content = content.replace('QLineEdit::Password', 'Password')
        content = content.replace('QLineEdit::NoEcho', 'NoEcho')
        content = content.replace('QLineEdit::PasswordEchoOnEdit', 'PasswordEchoOnEdit')
        
        # Thêm xử lý cho SizeAdjustPolicy của QComboBox
        content = content.replace('QComboBox::SizeAdjustPolicy::', '')
        content = content.replace('QComboBox::AdjustToContents', 'AdjustToContents')
        content = content.replace('QComboBox::AdjustToContentsOnFirstShow', 'AdjustToContentsOnFirstShow')
        content = content.replace('QComboBox::AdjustToMinimumContentsLength', 'AdjustToMinimumContentsLength')
        
        # Thêm xử lý cho InsertPolicy của QComboBox
        content = content.replace('QComboBox::InsertPolicy::', '')
        content = content.replace('QComboBox::InsertAtTop', 'InsertAtTop')
        content = content.replace('QComboBox::InsertAtBottom', 'InsertAtBottom')
        content = content.replace('QComboBox::InsertAtCurrent', 'InsertAtCurrent')
        
        # Sửa các enum khác của Qt
        content = content.replace('Qt::ScrollBarAsNeeded', 'ScrollBarAsNeeded')
        content = content.replace('Qt::ScrollBarAlwaysOff', 'ScrollBarAlwaysOff')
        content = content.replace('Qt::ScrollBarAlwaysOn', 'ScrollBarAlwaysOn')
        
        # Sửa các thuộc tính Qt::ItemFlag
        content = content.replace('Qt::ItemIsSelectable', 'ItemIsSelectable')
        content = content.replace('Qt::ItemIsEditable', 'ItemIsEditable')
        content = content.replace('Qt::ItemIsDragEnabled', 'ItemIsDragEnabled')
        content = content.replace('Qt::ItemIsDropEnabled', 'ItemIsDropEnabled')
        content = content.replace('Qt::ItemIsUserCheckable', 'ItemIsUserCheckable')
        content = content.replace('Qt::ItemIsEnabled', 'ItemIsEnabled')
        
        # Sửa các thuộc tính TextFormat
        content = content.replace('Qt::TextFormat::', '')
        content = content.replace('Qt::PlainText', 'PlainText')
        content = content.replace('Qt::RichText', 'RichText')
        content = content.replace('Qt::AutoText', 'AutoText')
        
        # Tạo file tạm với nội dung đã sửa
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ui')
        temp_path = temp_file.name
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        logger.info(f"Đã sửa file UI {ui_path} -> {temp_path}")
        return temp_path
    except Exception as e:
        logger.error(f"Lỗi khi sửa file UI {ui_path}: {str(e)}")
        logger.error(traceback.format_exc())
        return ui_path

def update_cursor_properties(self):
    """Cập nhật thuộc tính con trỏ cho các thành phần tương tác"""
    # Đặt con trỏ tay cho các nút
    buttons = self.findChildren(QtWidgets.QPushButton)
    for button in buttons:
        button.setCursor(QtCore.Qt.PointingHandCursor)
        
    # Đặt con trỏ tay cho các tab
    tab_bar = self.findChild(QtWidgets.QTabBar)
    if tab_bar:
        tab_bar.setCursor(QtCore.Qt.PointingHandCursor)

def load_config_modal(self):
    """Tải UI cho ConfigModal từ file UI"""
    return load_ui_components(self)

def load_otp_modal(self):
    """Tải UI cho OTPModal từ file UI"""
    ui_path = os.path.join(self.get_ui_dir(), "otp_modal.ui")
    
    # Fix UI file trước khi tải
    fixed_ui_path = self.fix_ui_file(ui_path)
    
    try:
        # Tải UI từ file đã sửa
        uic.loadUi(fixed_ui_path, self)
        logger.info("Đã tải UI otp_modal thành công")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi tải UI OTP modal: {str(e)}")
        return False
