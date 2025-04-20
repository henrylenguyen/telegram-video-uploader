"""
Module quản lý tải lên video qua Telethon API
"""
import os
import logging
import asyncio
import traceback
import tempfile
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class TelethonUploader:
    """
    Lớp xử lý tải lên video qua Telethon API
    """
    
    def __init__(self, session_path=None):
        """
        Khởi tạo uploader
        
        Args:
            session_path (str): Đường dẫn đến file session
        """
        # Xác định thư mục session
        if session_path:
            self.session_path = session_path
        else:
            # Lấy thư mục ứng dụng
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.session_path = os.path.join(app_dir, "telegram_uploader")
        
        # Trạng thái kết nối
        self.connected = False
        self.client = None
        
        # Thông tin đăng nhập
        self.api_id = None
        self.api_hash = None
        self.phone = None
    
    def login(self, api_id, api_hash, phone, interactive=True):
        """
        Đăng nhập vào Telethon API
        
        Args:
            api_id (int): API ID
            api_hash (str): API Hash
            phone (str): Số điện thoại
            interactive (bool): Yêu cầu xác thực tương tác
            
        Returns:
            bool: Đăng nhập thành công hay không
        """
        # Lưu thông tin đăng nhập
        self.api_id = int(api_id)
        self.api_hash = api_hash
        self.phone = phone
        
        try:
            # Tạo client Telethon
            from telethon import TelegramClient
            
            # Nếu đã có client, đóng trước
            if self.client:
                try:
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(self.client.disconnect())
                except:
                    pass
            
            # Tạo client mới
            self.client = TelegramClient(self.session_path, self.api_id, self.api_hash)
            
            # Kiểm tra xác thực
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Kết nối
            loop.run_until_complete(self.client.connect())
            
            # Kiểm tra đã xác thực chưa
            is_authorized = loop.run_until_complete(self.client.is_user_authorized())
            
            if is_authorized:
                # Đã xác thực
                logger.info("Đã đăng nhập vào Telethon API")
                self.connected = True
                return True
            elif interactive:
                # Xác thực tương tác
                logger.info("Cần xác thực tương tác")
                return loop.run_until_complete(self._interactive_login())
            else:
                # Chưa xác thực và không yêu cầu tương tác
                logger.warning("Chưa xác thực Telethon API và không yêu cầu tương tác")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi đăng nhập Telethon: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    async def _interactive_login(self):
        """
        Đăng nhập tương tác (yêu cầu OTP)
        
        Returns:
            bool: Đăng nhập thành công hay không
        """
        try:
            # Gửi mã xác thực
            await self.client.send_code_request(self.phone)
            
            # Báo hiệu thành công - việc nhập mã sẽ được xử lý bởi UI
            return True
        except Exception as e:
            logger.error(f"Lỗi gửi mã xác thực: {str(e)}")
            return False
    
    def is_user_authorized(self):
        """
        Kiểm tra người dùng đã xác thực chưa
        
        Returns:
            bool: Đã xác thực hay chưa
        """
        if not self.client:
            return False
            
        try:
            # Tạo event loop mới
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Kết nối và kiểm tra
            loop.run_until_complete(self.client.connect())
            result = loop.run_until_complete(self.client.is_user_authorized())
            
            return result
        except Exception as e:
            logger.error(f"Lỗi kiểm tra xác thực: {str(e)}")
            return False
    
    def upload_video(self, chat_id, video_path, caption=None, progress_callback=None):
        """
        Tải lên video qua Telethon API
        
        Args:
            chat_id (str/int): ID của chat
            video_path (str): Đường dẫn đến file video
            caption (str): Chú thích cho video
            progress_callback (func): Hàm callback báo tiến độ
            
        Returns:
            dict: Kết quả tải lên
        """
        if not self.client or not self.connected:
            logger.error("Chưa kết nối với Telethon API")
            return {"success": False, "error": "Chưa kết nối với Telethon API"}
        
        # Kiểm tra file tồn tại
        if not os.path.exists(video_path):
            logger.error(f"File video không tồn tại: {video_path}")
            return {"success": False, "error": f"File video không tồn tại: {video_path}"}
        
        try:
            # Xử lý chat_id
            target_chat = self.process_chat_id_for_telethon(chat_id)
            
            # Lấy thông tin video
            video_info = self.get_video_info(video_path)
            
            # Định dạng tiến độ
            def progress(current, total):
                """Xử lý callback tiến độ"""
                percent = current / total * 100
                if progress_callback:
                    progress_callback(percent)
            
            # Tạo event loop mới
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Định nghĩa hàm upload
            async def upload_video_task():
                """Task tải lên video"""
                try:
                    # Kết nối
                    await self.client.connect()
                    
                    # Tải lên video
                    result = await self.client.send_file(
                        target_chat,
                        video_path,
                        caption=caption,
                        progress_callback=progress,
                        supports_streaming=True
                    )
                    
                    # Trả về kết quả
                    return {
                        "success": True,
                        "message_id": result.id,
                        "date": result.date.isoformat(),
                        "chat_id": target_chat
                    }
                except Exception as e:
                    logger.error(f"Lỗi tải lên video: {str(e)}")
                    return {"success": False, "error": str(e)}
            
            # Chạy task tải lên
            result = loop.run_until_complete(upload_video_task())
            
            return result
            
        except Exception as e:
            logger.error(f"Lỗi tải lên video qua Telethon: {str(e)}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
    
    def get_video_info(self, video_path):
        """
        Lấy thông tin video
        
        Args:
            video_path (str): Đường dẫn đến file video
            
        Returns:
            dict: Thông tin video
        """
        try:
            # Lấy kích thước file
            file_size = os.path.getsize(video_path)
            
            # Lấy tên file
            file_name = os.path.basename(video_path)
            
            # Lấy thời gian tạo file
            created_time = os.path.getctime(video_path)
            created_date = datetime.fromtimestamp(created_time)
            
            # Trả về thông tin
            return {
                "file_name": file_name,
                "file_size": file_size,
                "file_size_mb": file_size / (1024 * 1024),
                "created_date": created_date.isoformat()
            }
        except Exception as e:
            logger.error(f"Lỗi lấy thông tin video: {str(e)}")
            return {
                "file_name": os.path.basename(video_path),
                "file_size": 0,
                "file_size_mb": 0,
                "created_date": datetime.now().isoformat()
            }
    
    def process_chat_id_for_telethon(self, chat_id):
        """
        Xử lý chat_id cho Telethon
        
        Args:
            chat_id (str/int): ID của chat
            
        Returns:
            str/int: Chat ID đã xử lý
        """
        try:
            # Nếu là số nguyên âm, convert thành chuỗi
            if isinstance(chat_id, str) and chat_id.startswith('-'):
                try:
                    # Thử chuyển thành số nguyên
                    chat_id_int = int(chat_id)
                    
                    # Nếu là ID nhóm Telegram (bắt đầu bằng -100)
                    if chat_id.startswith('-100'):
                        # Cắt bỏ -100 phía trước
                        return int(chat_id[4:])
                    else:
                        # Trả về nguyên dạng
                        return chat_id_int
                except ValueError:
                    # Nếu không phải số, trả về nguyên dạng
                    return chat_id
            
            # Nếu là username, đảm bảo có @ ở đầu
            if isinstance(chat_id, str) and not chat_id.startswith('-') and not chat_id.startswith('@'):
                return '@' + chat_id
            
            # Các trường hợp khác trả về nguyên dạng
            return chat_id
            
        except Exception as e:
            logger.error(f"Lỗi xử lý chat_id: {str(e)}")
            return chat_id
    
    def test_connection(self, chat_id, delete_after=10):
        """
        Kiểm tra kết nối bằng cách gửi tin nhắn thử nghiệm
        
        Args:
            chat_id (str/int): ID của chat
            delete_after (int): Xóa tin nhắn sau bao nhiêu giây
            
        Returns:
            bool: Kết nối thành công hay không
        """
        if not self.client:
            logger.error("Chưa khởi tạo Telethon client")
            return False
        
        try:
            # Xử lý chat_id
            target_chat = self.process_chat_id_for_telethon(chat_id)
            
            # Tạo event loop mới
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Định nghĩa task kiểm tra
            async def test_connection_task():
                try:
                    # Kết nối
                    await self.client.connect()
                    
                    # Kiểm tra xác thực
                    if not await self.client.is_user_authorized():
                        logger.error("Chưa xác thực Telethon API")
                        return False
                    
                    # Gửi tin nhắn thử nghiệm
                    message = await self.client.send_message(
                        target_chat,
                        "✅ Kiểm tra kết nối Telethon thành công!"
                    )
                    
                    # Nếu cần xóa tin nhắn
                    if delete_after > 0:
                        # Đợi và xóa tin nhắn
                        await asyncio.sleep(delete_after)
                        await self.client.delete_messages(target_chat, [message.id])
                    
                    return True
                    
                except Exception as e:
                    logger.error(f"Lỗi kiểm tra kết nối Telethon: {str(e)}")
                    return False
            
            # Chạy task kiểm tra
            result = loop.run_until_complete(test_connection_task())
            
            return result
            
        except Exception as e:
            logger.error(f"Lỗi kiểm tra kết nối Telethon: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def disconnect(self):
        """Ngắt kết nối với Telethon API"""
        if not self.client:
            return
            
        try:
            # Tạo event loop mới
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Ngắt kết nối
            loop.run_until_complete(self.client.disconnect())
            
            # Đặt lại trạng thái
            self.connected = False
            self.client = None
            
        except Exception as e:
            logger.error(f"Lỗi ngắt kết nối Telethon: {str(e)}")
