"""
Kiểm thử cho splash_screen.py (PyQt6 version)
"""
import os
import sys
import pytest
import unittest
from unittest.mock import MagicMock, patch

# Thêm thư mục gốc vào path để import các module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Sử dụng PyQt6 thay vì PyQt5
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from src.ui.splash_screen import SplashScreen, show_splash_screen

# Kiểm tra xem có QApplication tồn tại không
app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

class TestSplashScreen(unittest.TestCase):
    """Test cho SplashScreen"""
    
    def setUp(self):
        """Thiết lập trước mỗi test case"""
        # Mock FFmpegManager
        self.ffmpeg_manager = MagicMock()
        self.ffmpeg_manager.is_available = True
        self.ffmpeg_manager.is_downloading = False
        self.ffmpeg_manager.download_progress = 0
        self.ffmpeg_manager.download_status = "Sẵn sàng"
        
        # Tạo splash screen
        self.splash = SplashScreen(app)
        
        # Ẩn splash screen để không hiển thị trong khi chạy test
        self.splash.hide()
    
    def tearDown(self):
        """Dọn dẹp sau mỗi test case"""
        if hasattr(self, 'splash'):
            # Dừng tất cả timer
            if hasattr(self.splash, 'process_timer') and self.splash.process_timer.isActive():
                self.splash.process_timer.stop()
            
            if hasattr(self.splash, 'ffmpeg_status_timer') and self.splash.ffmpeg_status_timer.isActive():
                self.splash.ffmpeg_status_timer.stop()
            
            # Đóng splash screen
            self.splash.close()
            self.splash = None
    
    def test_init(self):
        """Kiểm tra khởi tạo splash screen"""
        # Kiểm tra các thuộc tính cơ bản
        self.assertEqual(self.splash.current_step, 0)
        self.assertEqual(self.splash.total_steps, 10)
        self.assertEqual(len(self.splash.setup_items), 10)
        self.assertEqual(len(self.splash.indicator_labels), 10)
        self.assertEqual(len(self.splash.status_labels), 10)
        
        # Kiểm tra các widget chính
        self.assertTrue(hasattr(self.splash, 'logoLabel'))
        self.assertTrue(hasattr(self.splash, 'progressBar'))
        self.assertTrue(hasattr(self.splash, 'statusLabel'))
    
    @patch('src.ui.splash_screen.SplashScreen.check_internet_connection')
    def test_process_step_1(self, mock_check_internet):
        """Kiểm tra bước 1: Kiểm tra kết nối Internet"""
        # Giả lập kết quả kiểm tra internet
        mock_check_internet.return_value = True
        
        # Gọi hàm xử lý bước đầu tiên
        self.splash.process_next_step()
        
        # Kiểm tra kết quả
        mock_check_internet.assert_called_once()
        self.assertEqual(self.splash.current_step, 1)  # Đã tăng lên bước 2
    
    @patch('src.ui.splash_screen.SplashScreen.check_pip_installation')
    def test_process_step_2(self, mock_check_pip):
        """Kiểm tra bước 2: Kiểm tra cấu hình hệ thống"""
        # Giả lập kết quả kiểm tra pip
        mock_check_pip.return_value = True
        
        # Thiết lập bước hiện tại là 1
        self.splash.current_step = 1
        
        # Gọi hàm xử lý bước tiếp theo
        self.splash.process_next_step()
        
        # Kiểm tra kết quả
        mock_check_pip.assert_called_once()
        self.assertEqual(self.splash.current_step, 2)  # Đã tăng lên bước 3
    
    @patch('src.ui.splash_screen.SplashScreen.setup_ssl_automatically')
    def test_process_step_3(self, mock_setup_ssl):
        """Kiểm tra bước 3: Thiết lập SSL cho Telethon"""
        # Giả lập kết quả thiết lập SSL
        mock_setup_ssl.return_value = True
        
        # Thiết lập bước hiện tại là 2
        self.splash.current_step = 2
        
        # Gọi hàm xử lý bước tiếp theo
        self.splash.process_next_step()
        
        # Kiểm tra kết quả
        self.assertEqual(self.splash.current_step, 3)  # Đã tăng lên bước 4
    
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='[]')
    def test_process_step_4(self, mock_open, mock_exists, mock_makedirs):
        """Kiểm tra bước 4: Khởi tạo tài nguyên ứng dụng"""
        # Giả lập kết quả kiểm tra file tồn tại
        mock_exists.return_value = True
        
        # Thiết lập bước hiện tại là 3
        self.splash.current_step = 3
        
        # Gọi hàm xử lý bước tiếp theo
        with patch('configparser.ConfigParser') as mock_config:
            config_instance = mock_config.return_value
            config_instance.__getitem__.return_value = {}
            config_instance.has_section.return_value = True
            
            self.splash.process_next_step()
        
        # Kiểm tra kết quả
        mock_makedirs.assert_called()
        self.assertEqual(self.splash.current_step, 4)  # Đã tăng lên bước 5
    
    @patch('src.ui.splash_screen.SplashScreen.check_internet_connection')
    def test_process_step_5(self, mock_check_internet):
        """Kiểm tra bước 5: Chuẩn bị bộ phân tích video"""
        # Giả lập kết quả kiểm tra internet
        mock_check_internet.return_value = True
        
        # Thiết lập ffmpeg_manager và bước hiện tại
        self.splash.ffmpeg_manager = self.ffmpeg_manager
        self.splash.current_step = 4
        
        # Gọi hàm xử lý bước tiếp theo
        self.splash.process_next_step()
        
        # Kiểm tra kết quả
        self.assertEqual(self.splash.current_step, 5)  # Đã tăng lên bước 6
    
    @patch('configparser.ConfigParser')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_process_step_6(self, mock_open, mock_exists, mock_config):
        """Kiểm tra bước 6: Kiểm tra kết nối Telegram"""
        # Bỏ qua mock cho ConfigModal vì phức tạp
        self.splash.current_step = 5
        self.splash.config_completed = True
        
        # Giả lập ConfigParser
        config_instance = mock_config.return_value
        config_instance.has_section.return_value = True
        config_instance.has_option.return_value = True
        config_instance.get.return_value = "test_value"
        config_instance.getboolean.return_value = True
        
        # Mock ui.telegram.telegram_ui_otp_modal
        with patch('src.ui.telegram.telegram_ui_otp_modal.OTPModal'):
            # Mock telegram_ui module
            with patch('src.ui.telegram.telegram_ui.ConfigModal'):
                # Gọi hàm xử lý bước tiếp theo
                self.splash.process_next_step()
        
        # Kiểm tra kết quả - nếu config_completed là True, nó sẽ tăng bước
        self.assertEqual(self.splash.current_step, 6)  # Đã tăng lên bước 7
    
    def test_process_step_7(self):
        """Kiểm tra bước 7: Tải các thành phần giao diện"""
        # Thiết lập bước hiện tại
        self.splash.current_step = 6
        
        # Thay thế time.sleep để tránh làm chậm test
        with patch('time.sleep'):
            # Gọi hàm xử lý bước tiếp theo
            self.splash.process_next_step()
        
        # Kiểm tra kết quả
        self.assertEqual(self.splash.current_step, 7)  # Đã tăng lên bước 8
    
    @patch('src.utils.disk_space_checker.DiskSpaceChecker')
    def test_process_step_8(self, mock_disk_checker_class):
        """Kiểm tra bước 8: Kiểm tra không gian lưu trữ"""
        # Thiết lập bước hiện tại
        self.splash.current_step = 7
        
        # Giả lập kết quả kiểm tra không gian
        mock_instance = mock_disk_checker_class.return_value
        mock_instance.check_all.return_value = {
            'disk_space': {
                'free': 10 * 1024 * 1024 * 1024,  # 10GB
                'formatted': {'free': '10 GB'},
                'percent_free': 50
            },
            'has_sufficient_space': True,
            'write_permission': True
        }
        
        # Gọi hàm xử lý bước tiếp theo
        with patch('PyQt6.QtWidgets.QMessageBox'):
            self.splash.process_next_step()
        
        # Kiểm tra kết quả
        mock_instance.check_all.assert_called_once()
        self.assertEqual(self.splash.current_step, 8)  # Đã tăng lên bước 9
    
    @patch('src.utils.update_checker.UpdateChecker')
    def test_process_step_9(self, mock_update_checker_class):
        """Kiểm tra bước 9: Tìm kiếm cập nhật"""
        # Thiết lập bước hiện tại
        self.splash.current_step = 8
        
        # Giả lập đối tượng UpdateChecker
        mock_instance = mock_update_checker_class.return_value
        
        # Tạo hàm fake cho check_for_updates_async
        def fake_check_async(callback):
            # Giả lập kết quả kiểm tra cập nhật
            callback({
                'has_update': False,
                'current_version': '1.0.0',
                'latest_version': '1.0.0',
                'last_check': '2023-01-01T00:00:00'
            })
        
        mock_instance.check_for_updates_async.side_effect = fake_check_async
        
        # Gọi hàm xử lý bước tiếp theo
        self.splash.process_next_step()
        
        # Kiểm tra kết quả
        mock_instance.check_for_updates_async.assert_called_once()
        # Bước tiếp theo được xử lý trong callback, nên không kiểm tra current_step ở đây
    
    @patch('src.utils.performance_optimizer.PerformanceOptimizer')
    def test_process_step_10(self, mock_optimizer_class):
        """Kiểm tra bước 10: Tối ưu hóa hiệu suất"""
        # Thiết lập bước hiện tại
        self.splash.current_step = 9
        
        # Giả lập đối tượng PerformanceOptimizer
        mock_instance = mock_optimizer_class.return_value
        
        # Tạo hàm fake cho optimize_async
        def fake_optimize_async(callback):
            # Giả lập kết quả tối ưu hóa
            callback({
                'success': True,
                'message': 'Đã tối ưu hóa thành công',
                'memory': {'freed': {'formatted': '50 MB'}},
                'cache': {'message': 'Đã dọn dẹp cache'},
                'logs': {'message': 'Đã dọn dẹp logs'},
                'temp': {'message': 'Đã dọn dẹp temp'}
            })
        
        mock_instance.optimize_async.side_effect = fake_optimize_async
        
        # Gọi hàm xử lý bước tiếp theo
        self.splash.process_next_step()
        
        # Kiểm tra kết quả
        mock_instance.optimize_async.assert_called_once()
        # Bước tiếp theo được xử lý trong callback, nên không kiểm tra current_step ở đây
    
    @patch('src.ui.splash_screen.SplashScreen')
    def test_show_splash_screen(self, mock_splash_screen_class):
        """Kiểm tra hàm show_splash_screen"""
        # Mock cho splash screen instance
        mock_instance = mock_splash_screen_class.return_value
        
        # Gọi hàm show_splash_screen
        with patch('PyQt6.QtWidgets.QApplication.processEvents'):
            show_splash_screen(app, self.ffmpeg_manager)
        
        # Kiểm tra kết quả
        mock_instance.setWindowFlag.assert_any_call(Qt.WindowType.WindowStaysOnTopHint)
        mock_instance.setWindowFlag.assert_any_call(Qt.WindowType.FramelessWindowHint)
        mock_instance.start_setup_process.assert_called_once_with(self.ffmpeg_manager)


if __name__ == '__main__':
    unittest.main()