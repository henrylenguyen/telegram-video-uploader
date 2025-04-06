"""
Module quản lý animation tiến trình tải lên, có thể tái sử dụng ở nhiều nơi.
"""
import logging
import tkinter as tk

logger = logging.getLogger("ProgressAnimation")

class ProgressAnimationManager:
    """
    Quản lý animation tiến trình với nhiều giai đoạn tốc độ khác nhau.
    Hỗ trợ nhiều cách hiển thị (thanh tiến trình, label, v.v.)
    """
    
    def __init__(self, parent_widget, progress_var=None, label_widget=None, 
                 percent_label=None, callback=None):
        """
        Khởi tạo animation manager
        
        Args:
            parent_widget: Widget cha chứa animation (cần after method)
            progress_var: Biến DoubleVar để theo dõi giá trị tiến trình
            label_widget: Widget hiển thị text trạng thái (nếu có)
            percent_label: Widget hiển thị phần trăm (nếu có)
            callback: Hàm callback khi tiến trình thay đổi
        """
        self.parent = parent_widget
        self.progress_var = progress_var
        self.label_widget = label_widget
        self.percent_label = percent_label
        self.callback = callback
        self.timers = []  # Lưu trữ tất cả timer ID
        self.is_cancelled = False
        self.current_progress = 0
    
    def cleanup(self):
        """Hủy tất cả timer đang chạy"""
        for timer_id in self.timers:
            try:
                self.parent.after_cancel(timer_id)
            except:
                pass
        self.timers.clear()
    
    def cancel(self):
        """Đánh dấu đã hủy và dừng tất cả timer"""
        self.is_cancelled = True
        self.cleanup()
    
    def start_animation(self, initial_value=0, prefix_text="Đang tải lên... "):
        """
        Bắt đầu animation tiến trình 3 giai đoạn:
        - 0-90%: Tăng 10% mỗi 2 giây
        - 90-99%: Tăng 1% mỗi 10 giây
        - 100%: Chỉ khi hoàn thành thực sự
        
        Args:
            initial_value: Giá trị ban đầu (mặc định 0)
            prefix_text: Tiền tố cho văn bản trạng thái
        """
        # Reset trạng thái
        self.cleanup()
        self.is_cancelled = False
        self.current_progress = initial_value
        
        # Đặt giá trị ban đầu
        self._update_ui(prefix_text)
        
        # Bắt đầu với giai đoạn 1: tăng nhanh
        self._schedule_phase1(prefix_text)
    
    def _update_ui(self, prefix_text):
        """Cập nhật tất cả UI element liên quan đến tiến trình"""
        # Cập nhật biến progress
        if self.progress_var:
            self.progress_var.set(self.current_progress)
        
        # Cập nhật label phần trăm
        if self.percent_label:
            self.percent_label.config(text=f"{int(self.current_progress)}%")
        
        # Cập nhật label trạng thái
        if self.label_widget:
            if isinstance(self.label_widget, tk.Label):
                self.label_widget.config(text=f"{prefix_text}{int(self.current_progress)}%")
            elif hasattr(self.label_widget, 'set'):
                self.label_widget.set(f"{prefix_text}{int(self.current_progress)}%")
        
        # Gọi callback nếu có
        if self.callback:
            self.callback(self.current_progress)
    
    def _schedule_phase1(self, prefix_text):
        """Giai đoạn 1: Tăng nhanh từ 0-90% (10% mỗi 2 giây)"""
        if self.is_cancelled:
            return
        
        # Tăng tiến trình 10% mỗi lần
        self.current_progress += 10
        
        # Giới hạn ở 90% cho giai đoạn 1
        if self.current_progress >= 90:
            self.current_progress = 90
            self._update_ui(prefix_text)
            
            # Chuyển sang giai đoạn 2
            timer_id = self.parent.after(10000, lambda: self._schedule_phase2(prefix_text))
            self.timers.append(timer_id)
        else:
            self._update_ui(prefix_text)
            
            # Lên lịch lần tiếp theo sau 2 giây
            timer_id = self.parent.after(2000, lambda: self._schedule_phase1(prefix_text))
            self.timers.append(timer_id)
    
    def _schedule_phase2(self, prefix_text):
        """Giai đoạn 2: Tăng chậm từ 90-99% (1% mỗi 10 giây)"""
        if self.is_cancelled:
            return
        
        # Tăng tiến trình 1% mỗi lần
        self.current_progress += 1
        
        # Giới hạn ở 99% cho giai đoạn 2
        if self.current_progress >= 99:
            self.current_progress = 99
            self._update_ui(prefix_text)
            # Kết thúc giai đoạn 2, chờ set_completed để lên 100%
        else:
            self._update_ui(prefix_text)
            
            # Lên lịch lần tiếp theo sau 10 giây
            timer_id = self.parent.after(10000, lambda: self._schedule_phase2(prefix_text))
            self.timers.append(timer_id)
    
    def set_completed(self, success=True, completion_text=None):
        """
        Đánh dấu đã hoàn thành (100%)
        
        Args:
            success: True nếu thành công, False nếu thất bại
            completion_text: Văn bản hiển thị khi hoàn thành
        """
        # Hủy tất cả timer
        self.cleanup()
        
        if success:
            # Đặt tiến trình thành 100%
            self.current_progress = 100
            
            # Cập nhật UI
            if self.progress_var:
                self.progress_var.set(100)
            
            if self.percent_label:
                self.percent_label.config(text="100%")
            
            # Cập nhật text
            if self.label_widget:
                text = completion_text or "Hoàn tất"
                if isinstance(self.label_widget, tk.Label):
                    self.label_widget.config(text=text)
                elif hasattr(self.label_widget, 'set'):
                    self.label_widget.set(text)
        else:
            # Giữ nguyên giá trị tiến trình hiện tại
            # Cập nhật text lỗi
            if self.label_widget:
                text = completion_text or "Lỗi"
                if isinstance(self.label_widget, tk.Label):
                    self.label_widget.config(text=text)
                elif hasattr(self.label_widget, 'set'):
                    self.label_widget.set(text)
        
        # Gọi callback nếu có
        if self.callback and success:
            self.callback(100)

def create_animation_for_progress_bar(parent, progress_var, status_label=None, 
                                    percent_label=None, callback=None):
    """
    Tạo và trả về đối tượng quản lý animation cho thanh tiến trình
    
    Args:
        parent: Widget cha chứa animation
        progress_var: Biến DoubleVar để theo dõi tiến trình
        status_label: Label hiển thị trạng thái (tùy chọn)
        percent_label: Label hiển thị phần trăm (tùy chọn)
        callback: Hàm gọi lại khi tiến trình thay đổi
        
    Returns:
        ProgressAnimationManager: Đối tượng quản lý animation
    """
    return ProgressAnimationManager(
        parent_widget=parent,
        progress_var=progress_var,
        label_widget=status_label,
        percent_label=percent_label,
        callback=callback
    )

# Các biểu tượng tiêu chuẩn cho tiến trình
ICON_PENDING = "⏳"
ICON_PROCESSING = "⌛" 
ICON_SUCCESS = "✅"
ICON_ERROR = "❌"