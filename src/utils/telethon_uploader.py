"""
Module xử lý tải lên video sử dụng Telethon.
Telethon cho phép tải lên file lớn hơn giới hạn 50MB của Bot API.
"""
import os
import time
import logging
import asyncio
from telethon import TelegramClient
from telethon.tl.types import InputPeerChannel
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.errors import *

logger = logging.getLogger("TelethonUploader")

class TelethonUploader:
    """
    Quản lý tải lên video không giới hạn kích thước sử dụng Telethon.
    
    Sử dụng user account API (MTProto) thay vì Bot API để tải lên file lớn.
    """
    
    def __init__(self, session_name='telegram_uploader'):
        """
        Khởi tạo TelethonUploader
        
        Args:
            session_name (str): Tên session để lưu phiên đăng nhập
        """
        self.client = None
        self.session_name = session_name
        self.api_id = None
        self.api_hash = None
        self.phone = None
        self.connected = False
        self.loop = None
        
        # Tạo loop riêng cho asyncio
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
    
    def login(self, api_id, api_hash, phone, interactive=True):
        """
        Đăng nhập vào Telegram
        
        Args:
            api_id (int): API ID từ my.telegram.org
            api_hash (str): API Hash từ my.telegram.org
            phone (str): Số điện thoại đăng ký Telegram (+84123456789)
            interactive (bool): True nếu cho phép nhập mã xác thực
            
        Returns:
            bool: True nếu đăng nhập thành công
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        
        # Tạo client mới
        try:
            self.client = TelegramClient(self.session_name, api_id, api_hash, loop=self.loop)
            
            # Đăng nhập
            if interactive:
                self.loop.run_until_complete(self._interactive_login())
            else:
                self.loop.run_until_complete(self.client.connect())
                if not self.loop.run_until_complete(self.client.is_user_authorized()):
                    logger.error("Không thể đăng nhập tự động. Cần phiên đăng nhập tương tác.")
                    return False
            
            self.connected = True
            logger.info("Đã đăng nhập thành công vào Telegram")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi đăng nhập Telegram: {str(e)}")
            if self.client:
                self.loop.run_until_complete(self.client.disconnect())
                self.client = None
            return False
    
    async def _interactive_login(self):
        """Hàm hỗ trợ đăng nhập tương tác"""
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            # Gửi mã xác thực qua SMS/Telegram
            await self.client.send_code_request(self.phone)
            
            # Cách tương tác với người dùng sẽ phụ thuộc vào giao diện của bạn
            # Đây là ví dụ đơn giản với input
            code = input(f"Nhập mã xác thực Telegram gửi đến {self.phone}: ")
            
            # Đăng nhập với mã
            await self.client.sign_in(self.phone, code)
    
    def disconnect(self):
        """Ngắt kết nối với Telegram"""
        if self.client:
            try:
                # Check if client has disconnect method and it's a coroutine
                if hasattr(self.client, 'disconnect') and self.loop and self.loop.is_running():
                    self.loop.run_until_complete(self.client.disconnect())
                elif hasattr(self.client, 'disconnect'):
                    # Create a new event loop if needed
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    # Run the disconnect coroutine
                    loop.run_until_complete(self.client.disconnect())
            except Exception as e:
                logger.error(f"Error during Telethon disconnect: {str(e)}")
            
            self.client = None
        
        self.connected = False
        logger.info("Đã ngắt kết nối khỏi Telegram")
    
    def get_entity(self, chat_id):
        """
        Lấy entity từ chat_id
        
        Args:
            chat_id (str/int): ID của kênh/nhóm
            
        Returns:
            Entity hoặc None nếu không tìm thấy
        """
        try:
            # Chuyển đổi ID kênh từ định dạng Bot API sang định dạng MTProto
            if isinstance(chat_id, str) and chat_id.startswith('-100'):
                chat_id = int(chat_id[4:])
            
            # Nếu là ID số
            if isinstance(chat_id, int) or chat_id.isdigit():
                chat_id = int(chat_id)
                entity = self.loop.run_until_complete(self.client.get_entity(chat_id))
            else:
                # Thử với username
                entity = self.loop.run_until_complete(self.client.get_entity(chat_id))
            
            return entity
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy entity: {str(e)}")
            return None
    
    def upload_video(self, chat_id, video_path, caption=None, progress_callback=None):
        """
        Tải lên video không giới hạn kích thước
        
        Args:
            chat_id (str/int): ID của kênh/nhóm
            video_path (str): Đường dẫn đến file video
            caption (str): Chú thích cho video
            progress_callback (function): Hàm callback nhận tiến trình (0-100)
            
        Returns:
            bool: True nếu tải lên thành công
        """
        if not self.connected or not self.client:
            logger.error("Chưa đăng nhập vào Telegram")
            return False
            
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            logger.error(f"File video không tồn tại: {video_path}")
            return False
        
        try:
            # Lấy entity
            entity = self.get_entity(chat_id)
            if not entity:
                logger.error(f"Không tìm thấy chat ID: {chat_id}")
                return False
            
            # Chuẩn bị caption
            if not caption:
                file_name = os.path.basename(video_path)
                caption = f"📹 {file_name}"
            
            # Hàm theo dõi tiến trình
            def progress_callback_wrapper(current, total):
                progress = int(current * 100 / total)
                logger.info(f"Tiến trình tải lên: {progress}%")
                if progress_callback:
                    progress_callback(progress)
            
            # Tải lên video
            message = self.loop.run_until_complete(
                self.client.send_file(
                    entity,
                    video_path,
                    caption=caption,
                    supports_streaming=True,
                    progress_callback=progress_callback_wrapper
                )
            )
            
            if message:
                logger.info(f"Đã tải lên thành công: {os.path.basename(video_path)}")
                return True
            else:
                logger.error(f"Tải lên thất bại: {os.path.basename(video_path)}")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi tải lên video {os.path.basename(video_path)}: {str(e)}")
            return False
    
    def send_message(self, chat_id, message):
        """
        Gửi tin nhắn văn bản
        
        Args:
            chat_id (str/int): ID của kênh/nhóm
            message (str): Nội dung tin nhắn
            
        Returns:
            bool: True nếu gửi thành công
        """
        if not self.connected or not self.client:
            logger.error("Chưa đăng nhập vào Telegram")
            return False
        
        try:
            # Lấy entity
            entity = self.get_entity(chat_id)
            if not entity:
                logger.error(f"Không tìm thấy chat ID: {chat_id}")
                return False
            
            # Gửi tin nhắn
            result = self.loop.run_until_complete(
                self.client.send_message(entity, message)
            )
            
            if result:
                logger.info(f"Đã gửi tin nhắn thành công")
                return True
            else:
                logger.error(f"Gửi tin nhắn thất bại")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi gửi tin nhắn: {str(e)}")
            return False
    
    def show_login_dialog(self, parent_window):
        """
        Hiển thị dialog nhập thông tin đăng nhập
        
        Args:
            parent_window: Cửa sổ cha
            
        Returns:
            bool: True nếu đăng nhập thành công
        """
        import tkinter as tk
        from tkinter import ttk, messagebox
        
        login_success = [False]  # Sử dụng list để có thể sửa đổi từ inner function
        
        dialog = tk.Toplevel(parent_window)
        dialog.title("Đăng nhập Telegram API")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.transient(parent_window)
        dialog.grab_set()
        
        # Đặt vị trí cửa sổ
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Frame chính
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        ttk.Label(
            main_frame, 
            text="Đăng nhập Telegram API", 
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 20))
        
        # Hướng dẫn
        ttk.Label(
            main_frame,
            text="Nhập thông tin API từ my.telegram.org",
            wraplength=350
        ).pack(pady=(0, 10))
        
        # Khung nhập thông tin
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # API ID
        ttk.Label(form_frame, text="API ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        api_id_var = tk.StringVar()
        api_id_entry = ttk.Entry(form_frame, textvariable=api_id_var, width=30)
        api_id_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # API Hash
        ttk.Label(form_frame, text="API Hash:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        api_hash_var = tk.StringVar()
        api_hash_entry = ttk.Entry(form_frame, textvariable=api_hash_var, width=30)
        api_hash_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Số điện thoại
        ttk.Label(form_frame, text="Số điện thoại:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        phone_var = tk.StringVar()
        phone_entry = ttk.Entry(form_frame, textvariable=phone_var, width=30)
        phone_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_frame, text="(Định dạng: +84123456789)").grid(row=3, column=1, sticky=tk.W, padx=5)
        
        # Frame cho code verification
        code_frame = ttk.Frame(main_frame)
        code_frame.pack(fill=tk.X, pady=10)
        code_frame.grid_remove()  # Ẩn ban đầu
        
        ttk.Label(code_frame, text="Mã xác thực:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        code_var = tk.StringVar()
        code_entry = ttk.Entry(code_frame, textvariable=code_var, width=20)
        code_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Các nút
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        status_var = tk.StringVar()
        status_label = ttk.Label(main_frame, textvariable=status_var, foreground="blue")
        status_label.pack(pady=10)
        
        def on_login():
            try:
                api_id = int(api_id_var.get())
                api_hash = api_hash_var.get()
                phone = phone_var.get()
                
                if not api_id or not api_hash or not phone:
                    messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
                    return
                
                # Đặt trạng thái
                status_var.set("Đang kết nối...")
                dialog.update_idletasks()
                
                # Khởi tạo client
                self.client = TelegramClient(self.session_name, api_id, api_hash, loop=self.loop)
                
                # Kết nối và gửi mã xác thực
                async def send_code():
                    await self.client.connect()
                    if not await self.client.is_user_authorized():
                        await self.client.send_code_request(phone)
                        return False
                    else:
                        # Đã đăng nhập sẵn
                        return True
                
                already_authorized = self.loop.run_until_complete(send_code())
                
                if already_authorized:
                    # Đã đăng nhập sẵn
                    status_var.set("Đăng nhập thành công!")
                    self.api_id = api_id
                    self.api_hash = api_hash
                    self.phone = phone
                    self.connected = True
                    
                    # Đóng dialog sau 1 giây
                    login_success[0] = True
                    dialog.after(1000, dialog.destroy)
                else:
                    # Cần nhập mã xác thực
                    status_var.set("Vui lòng nhập mã xác thực được gửi đến điện thoại/Telegram")
                    code_frame.pack(fill=tk.X, pady=10)  # Hiển thị khung nhập mã
                    login_btn.grid_remove()  # Ẩn nút đăng nhập
                    verify_btn.grid(row=0, column=0, padx=5)  # Hiển thị nút xác thực
                    code_entry.focus()
            
            except Exception as e:
                status_var.set(f"Lỗi: {str(e)}")
                messagebox.showerror("Lỗi", f"Không thể kết nối: {str(e)}")
        
        def on_verify():
            try:
                code = code_var.get()
                
                if not code:
                    messagebox.showerror("Lỗi", "Vui lòng nhập mã xác thực!")
                    return
                
                # Đặt trạng thái
                status_var.set("Đang xác thực...")
                dialog.update_idletasks()
                
                # Xác thực với mã
                async def sign_in():
                    try:
                        await self.client.sign_in(phone_var.get(), code)
                        return True
                    except Exception as e:
                        status_var.set(f"Lỗi xác thực: {str(e)}")
                        return False
                
                success = self.loop.run_until_complete(sign_in())
                
                if success:
                    status_var.set("Đăng nhập thành công!")
                    self.api_id = int(api_id_var.get())
                    self.api_hash = api_hash_var.get()
                    self.phone = phone_var.get()
                    self.connected = True
                    
                    # Đóng dialog sau 1 giây
                    login_success[0] = True
                    dialog.after(1000, dialog.destroy)
                
            except Exception as e:
                status_var.set(f"Lỗi: {str(e)}")
                messagebox.showerror("Lỗi", f"Không thể xác thực: {str(e)}")
        
        login_btn = ttk.Button(btn_frame, text="Đăng nhập", command=on_login)
        login_btn.grid(row=0, column=0, padx=5)
        
        verify_btn = ttk.Button(btn_frame, text="Xác thực", command=on_verify)
        # verify_btn sẽ được hiển thị khi cần nhập mã xác thực
        
        cancel_btn = ttk.Button(btn_frame, text="Hủy", command=dialog.destroy)
        cancel_btn.grid(row=0, column=1, padx=5)
        
        # Hiển thị trợ giúp
        help_text = (
            "Để lấy API ID và API Hash, bạn cần:\n"
            "1. Truy cập my.telegram.org\n"
            "2. Đăng nhập với tài khoản Telegram\n"
            "3. Chọn 'API development tools'\n"
            "4. Tạo ứng dụng mới và lấy thông tin"
        )
        
        help_label = ttk.Label(
            main_frame, 
            text=help_text, 
            wraplength=350, 
            justify=tk.LEFT,
            foreground="gray"
        )
        help_label.pack(pady=(20, 0), fill=tk.X)
        
        # Đặt focus vào ô đầu tiên
        api_id_entry.focus()
        
        # Đợi dialog đóng
        parent_window.wait_window(dialog)
        
        return login_success[0]

if __name__ == "__main__":
    # Mã kiểm thử
    logging.basicConfig(level=logging.DEBUG)
    uploader = TelethonUploader()
    
    # Thay thế với thông tin API và số điện thoại thật
    API_ID = 12345
    API_HASH = "your_api_hash"
    PHONE = "+84123456789"
    
    if uploader.login(API_ID, API_HASH, PHONE):
        print("Đăng nhập thành công")
        
        # Thử nghiệm gửi tin nhắn
        CHAT_ID = "your_chat_id"
        uploader.send_message(CHAT_ID, "Tin nhắn kiểm tra từ TelethonUploader")
        
        # Thử nghiệm tải lên video lớn
        # uploader.upload_video(CHAT_ID, "/path/to/large/video.mp4")
        
        uploader.disconnect()
    else:
        print("Đăng nhập thất bại")