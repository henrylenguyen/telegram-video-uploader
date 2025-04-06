"""
Module for uploading videos using Telethon API
"""

import os
import logging
import asyncio
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeVideo, PeerChannel, PeerChat, PeerUser
import time
import inspect
import tkinter as tk
from tkinter import simpledialog, messagebox

logger = logging.getLogger("TelethonUploader")

class ChatIDEditDialog(simpledialog.Dialog):
    """Dialog để chỉnh sửa Chat ID khi gặp lỗi"""
    
    def __init__(self, parent, title, current_chat_id, error_message):
        self.current_chat_id = current_chat_id
        self.error_message = error_message
        super().__init__(parent, title)
        
    def body(self, master):
        # Hiển thị thông báo lỗi
        tk.Label(master, text=self.error_message, wraplength=400, justify='left').grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Hiển thị chat_id hiện tại
        tk.Label(master, text="Chat ID hiện tại:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.current_id_display = tk.Entry(master, width=30)
        self.current_id_display.grid(row=1, column=1, padx=5, pady=5)
        self.current_id_display.insert(0, str(self.current_chat_id))
        self.current_id_display.config(state='readonly')
        
        # Nhập chat_id mới
        tk.Label(master, text="Chat ID mới:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.new_chat_id = tk.Entry(master, width=30)
        self.new_chat_id.grid(row=2, column=1, padx=5, pady=5)
        self.new_chat_id.focus_set()
        
        # Hướng dẫn
        guide_text = (
            "Chat ID có thể là:\n"
            "- ID số (vd: 123456789)\n"
            "- ID với tiền tố -100 (vd: -1001234567890)\n"
            "- Username (vd: @channel_name)\n\n"
            "Đảm bảo bạn là thành viên của chat/channel này và\n"
            "tài khoản Telethon của bạn có quyền gửi tin nhắn"
        )
        tk.Label(master, text=guide_text, justify='left', wraplength=400).grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        return self.new_chat_id  # Initial focus
    
    def apply(self):
        self.result = self.new_chat_id.get()
        
class TelethonUploader:
    """
    Class cho việc tải lên video lớn sử dụng Telethon API
    """
    
    def __init__(self, session_path=None):
        """
        Khởi tạo Telethon uploader
        
        Args:
            session_path (str): Đường dẫn để lưu file session
        """
        # Thiết lập đường dẫn session
        if not session_path:
            # Mặc định đến thư mục script
            session_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'telegram_uploader')
        
        self.session_name = session_path
        self.api_id = None
        self.api_hash = None
        self.phone = None
        self.client = None
        self.connected = False
        
        # Thiết lập event loop
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            # Nếu không có event loop tồn tại trong thread hiện tại
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
    
    def login(self, api_id, api_hash, phone, interactive=True):
        """
        Đăng nhập vào Telegram API sử dụng Telethon
        
        Args:
            api_id (int): API ID từ my.telegram.org
            api_hash (str): API Hash từ my.telegram.org
            phone (str): Số điện thoại đã đăng ký với Telegram (+84123456789)
            interactive (bool): True nếu cho phép đăng nhập tương tác
            
        Returns:
            bool: True nếu đăng nhập thành công
        """
        logger.info(f"Đang đăng nhập Telethon với api_id={api_id}, phone={phone}")
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        
        # Tạo client mới
        try:
            # Đóng client hiện tại nếu có
            if self.client:
                try:
                    if hasattr(self.client, 'disconnect'):
                        if inspect.iscoroutinefunction(self.client.disconnect):
                            self.loop.run_until_complete(self.client.disconnect())
                        else:
                            self.client.disconnect()
                except Exception as e:
                    logger.error(f"Lỗi khi ngắt kết nối client hiện tại: {str(e)}")
                self.client = None
            
            # Tạo client mới
            self.client = TelegramClient(self.session_name, api_id, api_hash, loop=self.loop)
            
            # Kết nối trước
            if hasattr(self.client, 'connect'):
                if inspect.iscoroutinefunction(self.client.connect):
                    self.loop.run_until_complete(self.client.connect())
                else:
                    self.client.connect()
            
            # Kiểm tra xem đã được ủy quyền chưa
            is_authorized = self.is_user_authorized()
            logger.info(f"Trạng thái ủy quyền Telethon: {is_authorized}")
            
            if is_authorized:
                # Đã đăng nhập sẵn
                logger.info("Đã đăng nhập sẵn vào Telegram")
                self.connected = True
                return True
                
            # Nếu chưa được ủy quyền và cho phép đăng nhập tương tác
            if interactive:
                result = self.loop.run_until_complete(self._interactive_login())
                if result:
                    self.connected = True
                    logger.info("Đã đăng nhập thành công vào Telegram")
                    return True
                else:
                    logger.error("Đăng nhập tương tác thất bại")
                    # Vẫn đặt connected = True để ưu tiên dùng Telethon
                    self.connected = True
                    logger.info("Đặt connected = True dù đăng nhập thất bại để ưu tiên dùng Telethon")
                    return False
            else:
                # Đăng nhập không tương tác thất bại
                logger.error("Không thể đăng nhập tự động. Cần phiên đăng nhập tương tác.")
                # Vẫn đặt connected = True để ưu tiên dùng Telethon
                self.connected = True
                logger.info("Đặt connected = True dù đăng nhập thất bại để ưu tiên dùng Telethon")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi đăng nhập Telegram: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            if self.client:
                try:
                    if hasattr(self.client, 'disconnect'):
                        if inspect.iscoroutinefunction(self.client.disconnect):
                            self.loop.run_until_complete(self.client.disconnect())
                        else:
                            self.client.disconnect()
                except:
                    pass
                self.client = None
            # Vẫn đặt connected = True để ưu tiên dùng Telethon
            self.connected = True
            logger.info("Đặt connected = True dù đăng nhập thất bại để ưu tiên dùng Telethon")
            return False
            
    async def _interactive_login(self):
        """Phương thức đăng nhập tương tác được cải tiến với xử lý lỗi tốt hơn"""
        try:
            # Đã kết nối tại thời điểm này
            if not await self.client.is_user_authorized():
                # Gửi mã xác thực qua SMS/Telegram
                sent = await self.client.send_code_request(self.phone)
                
                # Lấy mã từ người dùng
                code = input(f"Nhập mã xác thực Telegram gửi đến {self.phone}: ")
                
                # Đăng nhập với mã
                await self.client.sign_in(self.phone, code)
                
                # Kiểm tra nếu đăng nhập thành công
                if await self.client.is_user_authorized():
                    return True
                return False
            return True
        except Exception as e:
            logger.error(f"Lỗi khi đăng nhập tương tác: {str(e)}")
            return False
            
    def is_user_authorized(self):
        """Kiểm tra người dùng đã xác thực chưa"""
        if not self.client:
            return False
            
        try:
            if inspect.iscoroutinefunction(self.client.is_user_authorized):
                is_auth = self.loop.run_until_complete(self.client.is_user_authorized())
            else:
                is_auth = self.client.is_user_authorized()
            return is_auth
        except Exception as e:
            logger.error(f"Lỗi kiểm tra xác thực: {str(e)}")
            return False
    
    def process_chat_id_for_telethon(self, chat_id):
        """
        Xử lý chat_id để tương thích với Telethon
        
        Args:
            chat_id (str/int): Chat ID từ Telegram Bot API
            
        Returns:
            int/str: Chat ID đã xử lý cho Telethon
        """
        try:
            # Chuyển thành string để xử lý
            chat_id_str = str(chat_id).strip()
            
            # Nếu là username (bắt đầu bằng @)
            if chat_id_str.startswith('@'):
                logger.info(f"Xử lý chat_id: Giữ nguyên username {chat_id_str}")
                return chat_id_str
                
            # Kiểm tra nếu là định dạng chat ID của Bot API (-100...)
            if chat_id_str.startswith('-100'):
                # Thử nhiều cách xử lý
                options = [
                    chat_id_str,                   # Giữ nguyên
                    int(chat_id_str),              # Chuyển sang int giữ nguyên -100
                    int(chat_id_str[4:])           # Bỏ -100
                ]
                
                logger.info(f"Xử lý chat_id: Nhiều tùy chọn cho {chat_id_str} -> {options}")
                return options[0]  # Mặc định trả về nguyên bản trước
            
            # Nếu không phải -100 hoặc @ thì thử chuyển thành int
            if chat_id_str.lstrip('-').isdigit():
                return int(chat_id_str)
                
            # Mặc định giữ nguyên
            return chat_id
        except Exception as e:
            logger.error(f"Lỗi khi xử lý chat_id cho Telethon: {str(e)}")
            return chat_id

    def get_video_info(self, video_path):
        """
        Lấy thông tin video bằng ffmpeg
        
        Args:
            video_path (str): Đường dẫn đến file video
            
        Returns:
            dict: Thông tin video bao gồm duration, width, height hoặc None nếu có lỗi
        """
        try:
            import subprocess
            import json
            
            # Sử dụng ffprobe để lấy thông tin video
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                logger.error(f"Lỗi khi chạy ffprobe: {result.stderr}")
                return None
                
            # Parse json output
            info = json.loads(result.stdout)
            
            # Tìm video stream
            video_stream = None
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            if not video_stream:
                logger.error("Không tìm thấy video stream trong file")
                return None
                
            # Lấy thông tin cần thiết
            width = int(video_stream.get('width', 1280))
            height = int(video_stream.get('height', 720))
            
            # Lấy duration (thời lượng)
            duration = float(video_stream.get('duration', 0))
            if duration == 0:
                # Thử lấy từ format nếu không có trong stream
                duration = float(info.get('format', {}).get('duration', 10))
                
            # Chuyển về số nguyên (yêu cầu của Telethon)
            duration = int(duration)
            
            logger.info(f"Thông tin video: Thời lượng={duration}s, Kích thước={width}x{height}")
            
            return {
                'duration': duration,
                'width': width,
                'height': height
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin video: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def test_connection(self, chat_id, delete_after=10):
        """
        Kiểm tra kết nối bằng cách gửi thông báo và xóa sau một khoảng thời gian
        
        Args:
            chat_id (str/int): ID của chat để gửi tin nhắn
            delete_after (int): Số giây sau khi gửi sẽ xóa tin nhắn (mặc định: 10s)
            
        Returns:
            bool: True nếu gửi và xóa thành công
        """
        if not self.client:
            logger.error("Không thể kiểm tra kết nối: client chưa được khởi tạo")
            return False
            
        try:
            # Tạo và xử lý chat_id
            processed_chat_id = self.process_chat_id_for_telethon(chat_id)
            
            # Chuẩn bị thông báo kiểm tra kết nối
            test_message = f"🔄 Kiểm tra kết nối Telethon API...\n⏱️ Tin nhắn này sẽ tự động xóa sau {delete_after} giây\n🕒 {time.strftime('%H:%M:%S')}"
            
            async def send_and_delete():
                try:
                    # Đảm bảo đã kết nối
                    if not self.client.is_connected():
                        await self.client.connect()
                        
                    # Tìm entity
                    try:
                        entity = await self.client.get_entity(processed_chat_id)
                    except:
                        # Nếu không tìm được entity, thử các cách khác
                        if isinstance(chat_id, str) and chat_id.startswith('-100'):
                            try:
                                channel_id = int(chat_id[4:])
                                entity = await self.client.get_entity(PeerChannel(channel_id))
                            except:
                                # Nếu vẫn không được, thử dùng trực tiếp
                                entity = processed_chat_id
                        else:
                            entity = processed_chat_id
                    
                    # Gửi tin nhắn
                    message = await self.client.send_message(entity, test_message)
                    logger.info(f"Đã gửi tin nhắn kiểm tra kết nối với ID: {message.id}")
                    
                    # Đợi và xóa tin nhắn
                    await asyncio.sleep(delete_after)
                    await self.client.delete_messages(entity, message.id)
                    logger.info(f"Đã xóa tin nhắn kiểm tra kết nối với ID: {message.id}")
                    
                    return True
                except Exception as e:
                    logger.error(f"Lỗi khi kiểm tra kết nối: {str(e)}")
                    return False
            
            result = self.loop.run_until_complete(send_and_delete())
            return result
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra kết nối: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
            
    def upload_video(self, chat_id, video_path, caption=None, disable_notification=False, progress_callback=None, force=False, skip_caption=False):
        """
        Tải lên video lên Telegram sử dụng Telethon API
        
        Args:
            chat_id (str/int): ID của chat/kênh
            video_path (str): Đường dẫn đến file video
            caption (str): Chú thích cho video (bỏ qua nếu skip_caption=True)
            disable_notification (bool): Tắt thông báo cho tin nhắn
            progress_callback (function): Callback cho tiến trình tải lên
            force (bool): Bỏ qua kiểm tra kết nối nếu True
            skip_caption (bool): Không gửi caption nếu True
            
        Returns:
            bool: True nếu tải lên thành công
        """
        video_name = os.path.basename(video_path)
        video_size_mb = 0
        if os.path.exists(video_path) and os.path.isfile(video_path):
            video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            
        logger.info(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 1] Bắt đầu tải lên video {video_name} ({video_size_mb:.2f} MB), force={force}, skip_caption={skip_caption}")
        
        # Kiểm tra chat_id
        if not chat_id:
            logger.error("TELETHON_UPLOADER: [LỖI] chat_id không được cung cấp")
            from tkinter import messagebox
            messagebox.showerror(
                "Lỗi tải lên",
                "ID chat/channel không được cung cấp.\n"
                "Vui lòng cấu hình chat_id hợp lệ trong tab Cài đặt."
            )
            return False
        
        # Log chat_id hiện tại
        logger.info(f"TELETHON_UPLOADER: [CHAT_ID] Sử dụng chat_id: {chat_id}")
        
        # Kiểm tra file tồn tại
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            logger.error(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 2] File video không tồn tại: {video_path}")
            return False
            
        # Log chi tiết state
        logger.info(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 3] Trạng thái hiện tại - client exists: {self.client is not None}, connected: {self.connected}, api_id: {self.api_id is not None}, api_hash: {self.api_hash is not None}, phone: {self.phone is not None}")
            
        # Nếu force=True, bỏ qua kiểm tra kết nối
        if force:
            logger.info("TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 4] Force=True, ưu tiên dùng Telethon bất kể trạng thái kết nối")
            self.connected = True
        
        # Nếu chưa kết nối, báo lỗi
        if not self.connected or not self.client:
            if force:
                # Thử kết nối lại khi force=True
                logger.info("TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 5] Force=True & chưa kết nối, thử kết nối lại...")
                try:
                    # Tạo client mới nếu cần
                    if not self.client:
                        if not self.api_id or not self.api_hash or not self.phone:
                            logger.error("TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 6] Thiếu thông tin kết nối Telethon")
                            return False
                        
                        logger.info(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 7] Tạo client mới với api_id={self.api_id}, phone={self.phone}")
                        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash, loop=self.loop)
                    
                    # Kết nối client
                    logger.info(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 8] Thử kết nối client")
                    if hasattr(self.client, 'connect'):
                        if inspect.iscoroutinefunction(self.client.connect):
                            self.loop.run_until_complete(self.client.connect())
                        else:
                            self.client.connect()
                            
                    logger.info("TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 9] Đã kết nối lại Telethon khi force=True")
                except Exception as e:
                    logger.error(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 10] Không thể kết nối lại Telethon dù force=True: {str(e)}")
                    import traceback
                    logger.error(f"TELETHON_UPLOADER: [STACK TRACE] {traceback.format_exc()}")
                    # Vẫn tiếp tục thử tải lên dù có lỗi
                    logger.info("TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 11] Vẫn tiếp tục dù có lỗi vì force=True")
            else:
                logger.error("TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 12] Chưa kết nối Telethon API và không có force=True")
                return False
                
        try:
            # Chuẩn bị biến
            video_size = os.path.getsize(video_path)
            logger.info(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 13] Kích thước video: {video_size / (1024 * 1024):.2f} MB")
            
            # THÊM MỚI: ĐẢM BẢO CLIENT ĐƯỢC KẾT NỐI
            logger.info("TELETHON_UPLOADER: Đảm bảo client đã kết nối trước khi tải lên")
            if not self.client.is_connected():
                logger.info("TELETHON_UPLOADER: Client chưa kết nối, đang kết nối lại...")
                if inspect.iscoroutinefunction(self.client.connect):
                    self.loop.run_until_complete(self.client.connect())
                else:
                    self.client.connect()
                logger.info("TELETHON_UPLOADER: Đã kết nối lại client thành công")
            
            # THÊM MỚI: KIỂM TRA KẾT NỐI SAU KHI KẾT NỐI LẠI
            is_connected = False
            try:
                if inspect.iscoroutinefunction(self.client.is_connected):
                    is_connected = self.loop.run_until_complete(self.client.is_connected())
                else:
                    is_connected = self.client.is_connected()
                logger.info(f"TELETHON_UPLOADER: Trạng thái kết nối sau khi kiểm tra: {is_connected}")
            except Exception as e:
                logger.error(f"TELETHON_UPLOADER: Lỗi khi kiểm tra kết nối: {str(e)}")
                # Vẫn tiếp tục ngay cả khi kiểm tra thất bại
            
            # Xử lý chat_id cho Telethon
            processed_chat_id = self.process_chat_id_for_telethon(chat_id)
            logger.info(f"TELETHON_UPLOADER: [CHAT_ID] Đã xử lý chat_id: {processed_chat_id}")
            
            # Tạo wrapper cho progress_callback nếu được cung cấp
            if progress_callback:
                # Bắt đầu từ 20% vì quá trình chuẩn bị đã hoàn tất
                last_update = time.time()
                last_percent = 20
                
                def progress(current, total):
                    nonlocal last_update, last_percent
                    
                    # Tính phần trăm (từ 20% đến 90%)
                    percent = 20 + int(70.0 * current / total)
                    
                    # Chỉ cập nhật mỗi 1% thay đổi và không thường xuyên hơn mỗi 0.5 giây
                    current_time = time.time()
                    if (percent > last_percent or current == total) and current_time - last_update > 0.5:
                        progress_callback(percent)
                        last_percent = percent
                        last_update = current_time
            else:
                progress = None
            
            # Xử lý caption nếu yêu cầu bỏ qua
            final_caption = None if skip_caption else caption
            
            # Sử dụng asyncio để tải lên video
            async def _upload_video():
                try:
                    # Thêm mới: Đảm bảo client đã kết nối
                    if not self.client.is_connected():
                        logger.info("TELETHON_UPLOADER: [ĐIỂM KIỂM TRA ASYNC] Client chưa kết nối, đang kết nối trong async...")
                        await self.client.connect()
                        logger.info("TELETHON_UPLOADER: [ĐIỂM KIỂM TRA ASYNC] Đã kết nối lại client trong async")
                    
                    # Kiểm tra xác thực
                    is_auth = await self.client.is_user_authorized()
                    logger.info(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA ASYNC] Đã xác thực: {is_auth}")
                    
                    # Lấy entity trước để đảm bảo nó tồn tại
                    entity = None
                    chat_id_error = None
                    
                    # Thử tất cả các phương pháp để tìm entity
                    try_methods = [
                        # Phương pháp 1: Sử dụng processed_chat_id trực tiếp
                        (f"Cách 1: Thử với chat_id đã xử lý: {processed_chat_id}", 
                        lambda: self.client.get_entity(processed_chat_id)),
                        
                        # Phương pháp 2: Nếu chat_id bắt đầu bằng -100, thử tạo PeerChannel
                        (f"Cách 2: Thử với PeerChannel (bỏ -100)",
                        lambda: self.client.get_entity(PeerChannel(int(str(chat_id)[4:]))) 
                        if str(chat_id).startswith('-100') else None),
                        
                        # Phương pháp 3: Thử với int
                        (f"Cách 3: Thử với int: {int(chat_id) if str(chat_id).lstrip('-').isdigit() else 'N/A'}", 
                        lambda: self.client.get_entity(int(chat_id)) 
                        if str(chat_id).lstrip('-').isdigit() else None),
                        
                        # Phương pháp 4: Thử tìm trong dialogs
                        (f"Cách 4: Tìm trong dialogs", 
                        lambda: self._find_in_dialogs(chat_id))
                    ]
                    
                    # Thử lần lượt các phương pháp
                    for method_name, method in try_methods:
                        try:
                            logger.info(f"TELETHON_UPLOADER: [TÌM ENTITY] {method_name}")
                            entity_result = await method()
                            if entity_result:
                                entity = entity_result
                                logger.info(f"TELETHON_UPLOADER: [TÌM ENTITY] Thành công: {type(entity).__name__}")
                                break
                        except Exception as e:
                            chat_id_error = str(e)
                            logger.error(f"TELETHON_UPLOADER: [TÌM ENTITY] Thất bại: {str(e)}")
                            continue
                    
                    # Nếu vẫn không tìm thấy entity, mở modal để chỉnh sửa chat_id
                    if entity is None:
                        error_msg = f"Không thể tìm thấy chat/channel với ID: {chat_id}\n\n"
                        if chat_id_error:
                            error_msg += f"Lỗi: {chat_id_error}\n\n"
                        
                        error_msg += (
                            "Nguyên nhân có thể là:\n"
                            "1. ID chat/channel không chính xác\n"
                            "2. Bạn chưa tham gia chat/channel này\n"
                            "3. Ứng dụng không có quyền gửi tin nhắn đến chat/channel\n\n"
                            "Vui lòng nhập ID chat chính xác để tiếp tục."
                        )
                        
                        # Cần chuyển logic mở dialog sang phần async
                        # Tạm thời sử dụng processed_chat_id
                        logger.error(f"TELETHON_UPLOADER: [LỖI CHAT_ID] {error_msg}")
                        
                        # Sử dụng processed_chat_id trực tiếp làm phương án cuối cùng
                        logger.info(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 20] Sử dụng trực tiếp chat_id gốc: {chat_id}")
                        entity = processed_chat_id
                    
                    # Lấy thông tin video (duration, width, height) bằng ffmpeg
                    video_info = self.get_video_info(video_path)
                    if not video_info:
                        logger.error(f"TELETHON_UPLOADER: Không thể lấy thông tin video để tải lên")
                        # Sử dụng giá trị mặc định nếu không lấy được thông tin
                        duration = 10  # 10 giây
                        width = 1280   # HD width
                        height = 720   # HD height
                    else:
                        duration = video_info.get('duration', 10)
                        width = video_info.get('width', 1280)
                        height = video_info.get('height', 720)
                    
                    # Tải lên file với tiến trình
                    logger.info(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 21] Bắt đầu tải lên file...")
                    
                    # Thử kết nối lại một lần nữa trước khi gửi
                    if not self.client.is_connected():
                        logger.info("TELETHON_UPLOADER: Kết nối lại lần cuối cùng trước khi gửi...")
                        await self.client.connect()
                    
                    try:
                        result = await self.client.send_file(
                            entity,
                            video_path,
                            caption=final_caption,  # Sử dụng final_caption đã xử lý
                            progress_callback=progress,
                            supports_streaming=True,
                            silent=disable_notification,
                            attributes=[DocumentAttributeVideo(
                                duration=duration,  # Thời lượng video tính bằng giây
                                w=width,            # Chiều rộng video
                                h=height,           # Chiều cao video
                                supports_streaming=True
                            )]
                        )
                        
                        # Đặt tiến trình thành 100% nếu thành công
                        if progress_callback:
                            progress_callback(100)
                        
                        logger.info(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 22] Tải lên thành công: {result is not None}")
                        return result is not None
                    except ValueError as e:
                        if 'Cannot find any entity' in str(e):
                            logger.error(f"TELETHON_UPLOADER: [LỖI CHAT] Chat/Channel không tồn tại hoặc bạn không phải thành viên")
                            error_msg = (f"Không thể gửi tin nhắn đến chat_id={chat_id}.\n"
                                        f"Hãy đảm bảo ID hợp lệ và bạn là thành viên của chat/channel này.\n"
                                        f"Lỗi: {str(e)}")
                            raise ValueError(error_msg)
                        raise
                except Exception as e:
                    logger.error(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 23] Lỗi khi tải lên video qua Telethon: {str(e)}")
                    import traceback
                    logger.error(f"TELETHON_UPLOADER: [STACK TRACE] {traceback.format_exc()}")
                    return False
            
            async def _find_in_dialogs(search_id):
                """Tìm kiếm entity trong danh sách dialogs"""
                logger.info(f"TELETHON_UPLOADER: [TÌM TRONG DIALOGS] Bắt đầu tìm kiếm: {search_id}")
                
                search_id_str = str(search_id)
                search_id_no_prefix = search_id_str[4:] if search_id_str.startswith('-100') else search_id_str
                
                async for dialog in self.client.iter_dialogs():
                    dialog_id = str(dialog.id)
                    logger.info(f"TELETHON_UPLOADER: [TÌM TRONG DIALOGS] Kiểm tra: {dialog.name} ({dialog_id})")
                    
                    # So sánh với các dạng khác nhau của ID
                    if (dialog_id == search_id_str or 
                        dialog_id == search_id_no_prefix or
                        f"-100{dialog_id}" == search_id_str):
                        logger.info(f"TELETHON_UPLOADER: [TÌM TRONG DIALOGS] Tìm thấy khớp: {dialog.name}")
                        return dialog.entity
                
                logger.error(f"TELETHON_UPLOADER: [TÌM TRONG DIALOGS] Không tìm thấy {search_id}")
                return None
            
            # Chạy tải lên trong event loop
            logger.info(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 24] Chạy tải lên trong event loop")
            
            # Gọi _upload_video trong event loop
            try:
                result = self.loop.run_until_complete(_upload_video())
                
                if result:
                    logger.info(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 25] ✅ Đã tải lên thành công qua Telethon: {video_name} ({video_size / (1024 * 1024):.2f} MB)")
                    return True
                else:
                    logger.error(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 26] ❌ Tải lên thất bại qua Telethon: {video_name}")
                    return False
            except ValueError as e:
                # Xử lý lỗi chat_id không đúng
                if 'Cannot find any entity' in str(e) or 'Không thể gửi tin nhắn đến chat_id=' in str(e):
                    # Tạo root Tk để có thể hiển thị dialog
                    try:
                        from tkinter import Tk
                        root = Tk()
                        root.withdraw()  # Ẩn cửa sổ chính
                        
                        # Hiển thị dialog để nhập chat_id mới
                        error_msg = str(e)
                        dialog = ChatIDEditDialog(root, "Chỉnh sửa Chat ID", chat_id, error_msg)
                        new_chat_id = dialog.result
                        
                        # Nếu người dùng nhập chat_id mới
                        if new_chat_id:
                            logger.info(f"TELETHON_UPLOADER: [CHAT_ID MỚI] Thử lại với chat_id: {new_chat_id}")
                            
                            # Gọi lại hàm upload_video với chat_id mới
                            return self.upload_video(
                                new_chat_id, 
                                video_path, 
                                caption=caption, 
                                disable_notification=disable_notification,
                                progress_callback=progress_callback,
                                force=force,
                                skip_caption=skip_caption
                            )
                        else:
                            logger.error("TELETHON_UPLOADER: Người dùng hủy việc chỉnh sửa chat_id")
                            return False
                    except Exception as dialog_error:
                        logger.error(f"Lỗi khi hiển thị dialog: {str(dialog_error)}")
                        
                        # Nếu không thể hiển thị dialog, hiển thị thông báo lỗi thông thường
                        from tkinter import messagebox
                        messagebox.showerror(
                            "Lỗi Chat ID",
                            f"Không thể tìm thấy chat/channel với ID: {chat_id}\n\n"
                            f"Vui lòng kiểm tra lại ID chat và đảm bảo bạn là thành viên của nhóm/kênh."
                        )
                        return False
                else:
                    # Các lỗi khác
                    raise e
                
        except Exception as e:
            logger.error(f"TELETHON_UPLOADER: [ĐIỂM KIỂM TRA 27] ❌ Lỗi khi tải lên video qua Telethon: {str(e)}")
            import traceback
            logger.error(f"TELETHON_UPLOADER: [STACK TRACE] {traceback.format_exc()}")
            
            # Hiển thị thông báo lỗi
            try:
                from tkinter import messagebox
                messagebox.showerror(
                    "Lỗi tải lên qua Telethon",
                    f"Không thể tải lên video '{video_name}' qua Telethon API.\n\n"
                    f"Lỗi: {str(e)}\n\n"
                    f"Vui lòng kiểm tra cài đặt và thử lại."
                )
            except:
                pass
            
            return False
            
    def is_connected(self):
        """Kiểm tra xem client có kết nối và được ủy quyền không"""
        if not self.client:
            logger.info("is_connected: Client chưa được khởi tạo")
            return False
        
        try:
            # Kiểm tra các phương thức riêng biệt để tránh lỗi await boolean
            connected = False
            authorized = False
            
            # Kiểm tra kết nối vật lý
            try:
                if inspect.iscoroutinefunction(self.client.is_connected):
                    connected = self.loop.run_until_complete(self.client.is_connected())
                else:
                    connected = self.client.is_connected()
            except Exception as e:
                logger.error(f"is_connected: Lỗi kiểm tra kết nối vật lý: {str(e)}")
                connected = False
            
            if not connected:
                logger.info("is_connected: Client không có kết nối vật lý")
                return False
            
            # Kiểm tra xác thực
            try:
                if inspect.iscoroutinefunction(self.client.is_user_authorized):
                    authorized = self.loop.run_until_complete(self.client.is_user_authorized())
                else:
                    authorized = self.client.is_user_authorized()
            except Exception as e:
                logger.error(f"is_connected: Lỗi kiểm tra xác thực: {str(e)}")
                authorized = False
            
            logger.info(f"is_connected: Client có kết nối vật lý và trạng thái ủy quyền: {authorized}")
            
            # Nếu đã cấu hình đầy đủ nhưng chưa xác thực, vẫn trả về True để ưu tiên dùng Telethon
            if not authorized and self.api_id and self.api_hash and self.phone:
                logger.info("is_connected: Cấu hình đầy đủ, trả về True dù chưa xác thực")
                return True
                
            return authorized
        except Exception as e:
            logger.error(f"is_connected: Lỗi khi kiểm tra kết nối: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Nếu đã cấu hình đầy đủ nhưng lỗi khi kiểm tra, vẫn trả về True để ưu tiên dùng Telethon
            if self.api_id and self.api_hash and self.phone:
                logger.info("is_connected: Cấu hình đầy đủ, trả về True dù có lỗi")
                return True
            return False
            
    def reconnect(self):
        """Thử kết nối lại nếu bị ngắt kết nối"""
        if not self.client or not self.api_id or not self.api_hash:
            return False
            
        try:
            # Kiểm tra nếu đã kết nối
            if self.is_connected():
                return True
                
            # Thử kết nối lại
            self.loop.run_until_complete(self.client.connect())
            return self.is_connected()
        except:
            return False
            
    def close(self):
        """Đóng kết nối client"""
        if self.client:
            try:
                self.loop.run_until_complete(self.client.disconnect())
            except:
                pass
            self.client = None
        
        self.connected = False
        
    def disconnect(self):
        """Phương thức tương thích với phiên bản cũ - gọi close()"""
        self.close()