"""
Module for uploading videos using Telethon API
"""

import os
import logging
import asyncio
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeVideo
import time

logger = logging.getLogger("TelethonUploader")

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
                    self.loop.run_until_complete(self.client.disconnect())
                except:
                    pass
                self.client = None
            
            # Tạo client mới
            self.client = TelegramClient(self.session_name, api_id, api_hash, loop=self.loop)
            
            # Kết nối trước
            self.loop.run_until_complete(self.client.connect())
            
            # Kiểm tra nếu đã được ủy quyền
            is_authorized = self.loop.run_until_complete(self.client.is_user_authorized())
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
                    # THAY ĐỔI: Vẫn đặt connected = True để ưu tiên dùng Telethon
                    self.connected = True
                    logger.info("Đặt connected = True dù đăng nhập thất bại để ưu tiên dùng Telethon")
                    return False
            else:
                # Đăng nhập không tương tác thất bại
                logger.error("Không thể đăng nhập tự động. Cần phiên đăng nhập tương tác.")
                # THAY ĐỔI: Vẫn đặt connected = True để ưu tiên dùng Telethon
                self.connected = True
                logger.info("Đặt connected = True dù đăng nhập thất bại để ưu tiên dùng Telethon")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi đăng nhập Telegram: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            if self.client:
                try:
                    self.loop.run_until_complete(self.client.disconnect())
                except:
                    pass
                self.client = None
            # THAY ĐỔI: Vẫn đặt connected = True để ưu tiên dùng Telethon
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
    
    def upload_video(self, chat_id, video_path, caption=None, disable_notification=False, progress_callback=None):
        """
        Tải lên video lên Telegram sử dụng Telethon API
        
        Args:
            chat_id (str/int): ID của chat/kênh
            video_path (str): Đường dẫn đến file video
            caption (str): Chú thích cho video
            disable_notification (bool): Tắt thông báo cho tin nhắn
            progress_callback (function): Callback cho tiến trình tải lên
            
        Returns:
            bool: True nếu tải lên thành công
        """
        logger.info(f"Bắt đầu tải lên video qua Telethon: {os.path.basename(video_path)}")
        
        if not self.connected or not self.client:
            logger.error("Chưa kết nối Telethon API")
            return False
        
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            logger.error(f"File video không tồn tại: {video_path}")
            return False
            
        try:
            # Chuẩn bị biến
            video_size = os.path.getsize(video_path)
            video_name = os.path.basename(video_path)
            
            # Chuyển đổi chat_id thành int nếu là chuỗi số
            try:
                chat_id = int(chat_id)
            except ValueError:
                pass
            
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
            
            # Sử dụng asyncio để tải lên video
            async def _upload_video():
                try:
                    # Lấy entity trước để đảm bảo nó tồn tại
                    entity = await self.client.get_entity(chat_id)
                    
                    # Tải lên file với tiến trình
                    result = await self.client.send_file(
                        entity,
                        video_path,
                        caption=caption,
                        progress_callback=progress,
                        supports_streaming=True,
                        silent=disable_notification,
                        attributes=[DocumentAttributeVideo(
                            supports_streaming=True
                        )]
                    )
                    
                    # Đặt tiến trình thành 100% nếu thành công
                    if progress_callback:
                        progress_callback(100)
                    
                    return result is not None
                except Exception as e:
                    logger.error(f"Lỗi khi tải lên video qua Telethon: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    return False
            
            # Chạy tải lên trong event loop
            result = self.loop.run_until_complete(_upload_video())
            
            if result:
                logger.info(f"✅ Đã tải lên thành công qua Telethon: {video_name} ({video_size / (1024 * 1024):.2f} MB)")
                return True
            else:
                logger.error(f"❌ Tải lên thất bại qua Telethon: {video_name}")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi tải lên video qua Telethon: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def is_connected(self):
        """Kiểm tra xem client có kết nối và được ủy quyền không"""
        if not self.client:
            logger.info("is_connected: Client chưa được khởi tạo")
            return False
        
        try:
            # Kiểm tra kết nối vật lý
            is_connected = self.loop.run_until_complete(self.client.is_connected())
            if not is_connected:
                logger.info("is_connected: Client không có kết nối vật lý")
                return False
            
            # Kiểm tra ủy quyền
            is_authorized = self.loop.run_until_complete(self.client.is_user_authorized())
            logger.info(f"is_connected: Client có kết nối vật lý và trạng thái ủy quyền: {is_authorized}")
            return is_authorized
        except Exception as e:
            logger.error(f"is_connected: Lỗi khi kiểm tra kết nối: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
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