"""
Module for editing Telegram configurations
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import os
import sys
import threading
import json

logger = logging.getLogger("EditConfigModal")

class TelegramEditModal:
    """
    Modal dialog for editing Telegram Bot configuration
    """
    
    def __init__(self, app):
        """
        Initialize the edit modal
        
        Args:
            app: The main application instance
        """
        self.app = app
        self.modal = None
        
        # Create modal window
        self.create_modal()
    
    def create_fixed_height_entry(self, parent, textvariable, width=40):
        """Create an entry widget with fixed height of 40px"""
        # Create a container frame with fixed height
        container = ttk.Frame(parent, height=40)
        container.pack_propagate(False)  # Prevent the frame from shrinking
        
        # Create the entry widget within the container
        entry = ttk.Entry(container, textvariable=textvariable, width=width)
        entry.pack(fill=tk.BOTH, expand=True)
        
        return container, entry
        
    def create_modal(self):
        """Create the edit configuration modal UI"""
        self.modal = tk.Toplevel(self.app.root)
        self.modal.title("Chỉnh sửa cấu hình Telegram Bot")
        self.modal.transient(self.app.root)
        self.modal.grab_set()
        
        # Set window size
        screen_width = self.modal.winfo_screenwidth()
        screen_height = self.modal.winfo_screenheight()
        
        # Adjust to keep some margin
        window_width = min(800, screen_width - 100)
        window_height = min(600, screen_height - 100)
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.modal.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Main content frame
        content_frame = ttk.Frame(self.modal, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Bot Token
        ttk.Label(content_frame, text="Token Telegram - (Tìm trong @BotFather)").pack(anchor=tk.W, pady=(0, 5))
        self.token_var = tk.StringVar(value=self.app.config['TELEGRAM']['bot_token'])
        token_container, token_entry = self.create_fixed_height_entry(content_frame, self.token_var, width=60)
        token_container.pack(fill=tk.X, pady=(0, 15))
        
        # Chat ID
        ttk.Label(content_frame, text="Chat ID - (Có định dạng: -100xxxxxxxxx)").pack(anchor=tk.W, pady=(0, 5))
        self.chat_id_var = tk.StringVar(value=self.app.config['TELEGRAM']['chat_id'])
        chat_id_container, chat_id_entry = self.create_fixed_height_entry(content_frame, self.chat_id_var, width=60)
        chat_id_container.pack(fill=tk.X, pady=(0, 15))
        
        # Footer with buttons
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Test connection button
        test_btn = ttk.Button(
            btn_frame, 
            text="Kiểm tra kết nối", 
            command=self.test_connection,
            width=20  # Wider button
        )
        test_btn.pack(side=tk.LEFT)
        
        # Cancel button
        cancel_btn = ttk.Button(
            btn_frame, 
            text="Hủy", 
            command=self.modal.destroy,
            width=15  # Wider button
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Save button
        save_btn = ttk.Button(
            btn_frame, 
            text="Lưu cài đặt", 
            command=self.save_settings,
            width=15  # Wider button
        )
        save_btn.pack(side=tk.RIGHT)
        
        # Focus on token entry
        token_entry.focus_set()
    
    def test_connection(self):
        """Test Telegram connection with provided settings"""
        # Test Bot API connection
        bot_token = self.token_var.get().strip()
        chat_id = self.chat_id_var.get().strip()
        
        if not bot_token or not chat_id:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ Token và Chat ID!")
            return
        
        try:
            # Try to connect to Telegram Bot API
            import telebot
            bot = telebot.TeleBot(bot_token)
            
            # Test if bot info can be retrieved
            bot_info = bot.get_me()
            
            if bot_info:
                # Try to send a test message
                try:
                    message = bot.send_message(
                        chat_id=chat_id,
                        text="✅ Kiểm tra kết nối thành công! Tin nhắn này sẽ tự động bị xóa."
                    )
                    
                    # Try to delete the test message
                    try:
                        bot.delete_message(chat_id, message.message_id)
                    except:
                        pass  # Ignore if can't delete
                    
                    messagebox.showinfo(
                        "Thành công", 
                        f"Kết nối thành công với bot @{bot_info.username}!"
                    )
                except Exception as e:
                    messagebox.showerror(
                        "Lỗi", 
                        f"Kết nối đến bot thành công nhưng không thể gửi tin nhắn đến chat ID: {str(e)}"
                    )
            else:
                messagebox.showerror("Lỗi", "Không thể kết nối đến Telegram Bot API!")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kết nối đến Telegram: {str(e)}")
    
    def save_settings(self):
        """Save the configuration settings"""
        # Get and validate settings
        bot_token = self.token_var.get().strip()
        chat_id = self.chat_id_var.get().strip()
        
        if not bot_token or not chat_id:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ Token và Chat ID!")
            return
        
        # Save settings to config
        self.app.config['TELEGRAM']['bot_token'] = bot_token
        self.app.config['TELEGRAM']['chat_id'] = chat_id
        self.app.config['TELEGRAM']['notification_chat_id'] = chat_id  # Use same chat ID for notifications
        
        # Save configuration
        self.app.config_manager.save_config(self.app.config)
        
        # Update the values in the settings tab
        self.app.bot_token_var.set(bot_token)
        self.app.chat_id_var.set(chat_id)
        
        # Reconnect with new settings
        self.app.telegram_connector.connect_telegram(self.app)
        
        # Show success message
        messagebox.showinfo("Thành công", "Đã lưu cài đặt Bot Telegram thành công!")
        
        # Close modal
        self.modal.destroy()
        
        # Refresh current tab - Compatible with custom tab navigation
        if hasattr(self.app, 'switch_tab') and hasattr(self.app, 'tab_buttons'):
            # Find which tab is currently active by checking button colors
            current_tab = 0  # Default to first tab
            for i, btn in enumerate(self.app.tab_buttons):
                if btn.cget("bg") == "#2E86C1" or btn.cget("bg") == "#4a7ebb":  # Active tab color
                    current_tab = i
                    break
            
            # Refresh the current tab
            self.app.switch_tab(current_tab)


class TelethonEditModal:
    """
    Modal dialog for editing Telethon API configuration
    """
    
    def __init__(self, app):
        """
        Initialize the edit modal
        
        Args:
            app: The main application instance
        """
        self.app = app
        self.modal = None
        self.telethon_verification_in_progress = False
        self.phone_code_hash = None
        
        # Create modal window
        self.create_modal()
    
    def create_fixed_height_entry(self, parent, textvariable, width=40):
        """Create an entry widget with fixed height of 40px"""
        # Create a container frame with fixed height
        container = ttk.Frame(parent, height=40)
        container.pack_propagate(False)  # Prevent the frame from shrinking
        
        # Create the entry widget within the container
        entry = ttk.Entry(container, textvariable=textvariable, width=width)
        entry.pack(fill=tk.BOTH, expand=True)
        
        return container, entry
        
    def create_modal(self):
        """Create the edit configuration modal UI"""
        self.modal = tk.Toplevel(self.app.root)
        self.modal.title("Chỉnh sửa cấu hình Telethon API")
        self.modal.transient(self.app.root)
        self.modal.grab_set()
        
        # Set window size
        screen_width = self.modal.winfo_screenwidth()
        screen_height = self.modal.winfo_screenheight()
        
        # Adjust to keep some margin
        window_width = min(800, screen_width - 100)
        window_height = min(700, screen_height - 100)
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.modal.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Main content frame
        content_frame = ttk.Frame(self.modal, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # API ID
        ttk.Label(content_frame, text="API ID - (Có định dạng: 2xxxxxx)").pack(anchor=tk.W, pady=(0, 5))
        self.api_id_var = tk.StringVar(value=self.app.config['TELETHON']['api_id'])
        api_id_container, api_id_entry = self.create_fixed_height_entry(content_frame, self.api_id_var, width=30)
        api_id_container.pack(fill=tk.X, pady=(0, 15))
        
        # API Hash
        ttk.Label(content_frame, text="API Hash - (Có định dạng: 7xxxxe)").pack(anchor=tk.W, pady=(0, 5))
        self.api_hash_var = tk.StringVar(value=self.app.config['TELETHON']['api_hash'])
        api_hash_container, api_hash_entry = self.create_fixed_height_entry(content_frame, self.api_hash_var, width=60)
        api_hash_container.pack(fill=tk.X, pady=(0, 15))
        
        # Phone number
        ttk.Label(content_frame, text="Số điện thoại - (Có định dạng: +84123456789)").pack(anchor=tk.W, pady=(0, 5))
        self.phone_var = tk.StringVar(value=self.app.config['TELETHON']['phone'])
        phone_container, phone_entry = self.create_fixed_height_entry(content_frame, self.phone_var, width=30)
        phone_container.pack(fill=tk.X, pady=(0, 15))
        
        # OTP verification group
        otp_frame = ttk.LabelFrame(content_frame, text="Xác thực OTP")
        otp_frame.pack(fill=tk.X, pady=(10, 15))
        
        # OTP field label
        ttk.Label(otp_frame, text="Mã OTP").pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # OTP input and button in a horizontal container
        otp_container = ttk.Frame(otp_frame)
        otp_container.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # OTP input with fixed height
        self.otp_var = tk.StringVar()
        otp_entry_container, otp_entry = self.create_fixed_height_entry(otp_container, self.otp_var)
        otp_entry_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # OTP button with fixed height and increased width
        btn_container = ttk.Frame(otp_container, height=40, width=150)  # Increased width
        btn_container.pack_propagate(False)
        btn_container.pack(side=tk.RIGHT)
        
        self.otp_button = ttk.Button(btn_container, text="Lấy mã xác thực", width=20)  # Wider button with clearer text
        self.otp_button.config(command=self.request_otp)
        self.otp_button.pack(fill=tk.BOTH, expand=True)
        
        # Footer with buttons
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Cancel button
        cancel_btn = ttk.Button(
            btn_frame, 
            text="Hủy", 
            command=self.modal.destroy,
            width=15  # Wider button
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Save button
        self.save_button = ttk.Button(
            btn_frame, 
            text="Lưu cài đặt", 
            command=self.save_settings,
            width=15  # Wider button
        )
        self.save_button.pack(side=tk.RIGHT)
        
        # Focus on API ID entry
        api_id_entry.focus_set()
    
    def request_otp(self):
        """Request OTP for Telethon verification or verify OTP"""
        # Nếu nút đang ở trạng thái "Xác thực", thực hiện xác thực OTP
        if self.otp_button.cget("text") == "Xác thực mã OTP":
            self.verify_otp_directly()
            return
            
        # Nếu không, thì đây là request OTP
        # Get the API ID, API Hash, and phone number
        api_id = self.api_id_var.get().strip()
        api_hash = self.api_hash_var.get().strip()
        phone = self.phone_var.get().strip()
        
        if not api_id or not api_hash or not phone:
            messagebox.showerror(
                "Lỗi", 
                "Vui lòng nhập đầy đủ API ID, API Hash và số điện thoại!"
            )
            return
            
        try:
            # Convert API ID to integer
            api_id = int(api_id)
            
            # Disable OTP button during verification
            self.otp_button.config(text="Đang gửi...", state=tk.DISABLED)
            
            # Sử dụng approach khác để gửi code
            def request_telethon_code():
                try:
                    # Thực hiện yêu cầu code bằng subprocess
                    import subprocess
                    
                    # Tạo script Python tạm thời để yêu cầu code
                    temp_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'request_code.py')
                    with open(temp_script, 'w', encoding='utf-8') as f:
                        f.write("""
import os
import sys
import json
from telethon import TelegramClient

api_id = int(sys.argv[1])
api_hash = sys.argv[2]
phone = sys.argv[3]

async def main():
    # Sử dụng cùng session_path
    session_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'telegram_uploader')
    client = TelegramClient(session_path, api_id, api_hash)
    
    await client.connect()
    if not await client.is_user_authorized():
        result = await client.send_code_request(phone)
        result_dict = {
            'phone_code_hash': result.phone_code_hash,
            'status': 'SUCCESS'
        }
        print(json.dumps(result_dict))
    else:
        print(json.dumps({'status': 'ALREADY_AUTHORIZED'}))
    
    await client.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
""")
                    
                    # Chạy script với Python
                    python_executable = sys.executable
                    result = subprocess.run(
                        [python_executable, temp_script, str(api_id), api_hash, phone],
                        capture_output=True,
                        text=True
                    )
                    
                    # Xóa file tạm
                    try:
                        os.remove(temp_script)
                    except:
                        pass
                    
                    # Kiểm tra kết quả
                    stdout = result.stdout.strip()
                    if stdout:
                        try:
                            response = json.loads(stdout)
                            if response.get('status') in ['SUCCESS', 'ALREADY_AUTHORIZED']:
                                self.telethon_verification_in_progress = True
                                # Lưu phone_code_hash nếu có
                                if 'phone_code_hash' in response:
                                    self.phone_code_hash = response['phone_code_hash']
                                
                                # Đổi nút "Lấy mã xác thực" thành "Xác thực mã OTP"
                                self.app.root.after(0, lambda: self.otp_button.config(
                                    text="Xác thực mã OTP", 
                                    state=tk.NORMAL,
                                    width=20  # Maintain wider button
                                ))
                                
                                # Vô hiệu hóa nút Lưu cài đặt cho đến khi xác thực xong
                                self.app.root.after(0, lambda: self.save_button.config(state=tk.DISABLED))
                                
                                self.app.root.after(0, lambda: messagebox.showinfo(
                                    "Mã xác thực", 
                                    f"Mã xác thực đã được gửi đến {phone}. Vui lòng nhập mã vào ô OTP và nhấn 'Xác thực mã OTP'."
                                ))
                                return
                        except json.JSONDecodeError:
                            pass
                    
                    # Nếu không thành công
                    error_msg = result.stderr or "Không rõ lỗi"
                    self.app.root.after(0, lambda: messagebox.showerror(
                        "Lỗi", 
                        f"Không thể gửi mã xác thực: {error_msg}"
                    ))
                    # Nút trở lại là "Lấy mã xác thực"
                    self.app.root.after(0, lambda: self.otp_button.config(
                        text="Lấy mã xác thực", 
                        state=tk.NORMAL, 
                        width=20  # Maintain wider button
                    ))
                    
                except Exception as e:
                    self.app.root.after(0, lambda: messagebox.showerror(
                        "Lỗi", 
                        f"Không thể gửi mã xác thực: {str(e)}"
                    ))
                    # Nút trở lại là "Lấy mã xác thực"
                    self.app.root.after(0, lambda: self.otp_button.config(
                        text="Lấy mã xác thực", 
                        state=tk.NORMAL, 
                        width=20  # Maintain wider button
                    ))
            
            # Run in a separate thread to avoid blocking UI
            threading.Thread(target=request_telethon_code, daemon=True).start()
            
        except ValueError:
            messagebox.showerror("Lỗi", "API ID phải là một số nguyên!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi yêu cầu mã OTP: {str(e)}")
            self.otp_button.config(text="Lấy mã xác thực", state=tk.NORMAL, width=20)
    
    def verify_otp_directly(self):
        """Xác thực OTP được gọi trực tiếp từ nút"""
        otp_code = self.otp_var.get().strip()
        if not otp_code:
            messagebox.showerror("Lỗi", "Vui lòng nhập mã OTP!")
            return
            
        # Disable button during verification
        self.otp_button.config(text="Đang xác thực...", state=tk.DISABLED)
        
        # Verify in a separate thread
        threading.Thread(target=lambda: self.verify_otp_thread(otp_code), daemon=True).start()
    
    def verify_otp_thread(self, otp_code):
      """Verify OTP code for Telethon in a separate thread"""
      success = self.verify_otp()
      
      if success:
          # Re-enable Save button
          self.app.root.after(0, lambda: self.save_button.config(state=tk.NORMAL))
          # Change button text to show completion
          self.app.root.after(0, lambda: self.otp_button.config(
              text="✓ Đã xác thực thành công", 
              state=tk.DISABLED,
              width=25  # Wider for longer text
          ))
          
          # THÊM MỚI: Cập nhật trạng thái kết nối thực tế
          try:
              logger.info("Đang cập nhật trạng thái kết nối Telethon sau khi xác thực OTP thành công")
              is_connected = self.app.telethon_uploader.is_connected()
              self.app.telethon_uploader.connected = is_connected
              logger.info(f"Trạng thái kết nối Telethon sau xác thực OTP: {is_connected}")
          except Exception as e:
              logger.error(f"Lỗi khi cập nhật trạng thái kết nối Telethon: {str(e)}")
          
          # Show success message
          self.app.root.after(0, lambda: messagebox.showinfo(
              "Thành công", 
              "Xác thực thành công! Bạn có thể Lưu cài đặt."
          ))
      else:
          # Reset button
          self.app.root.after(0, lambda: self.otp_button.config(
              text="Xác thực mã OTP", 
              state=tk.NORMAL,
              width=20  # Maintain wider button
          ))

    def verify_otp(self):
        """Verify OTP code for Telethon"""
        if not self.telethon_verification_in_progress:
            return True  # Skip verification if not in progress
            
        # Get OTP code
        otp_code = self.otp_var.get().strip()
        if not otp_code:
            messagebox.showerror("Lỗi", "Vui lòng nhập mã OTP!")
            return False
        
        try:
            # Get necessary values
            api_id = int(self.api_id_var.get().strip())
            api_hash = self.api_hash_var.get().strip()
            phone = self.phone_var.get().strip()
            
            # Sử dụng approach khác để xác minh code
            import subprocess
            
            # Tạo script Python tạm thời để xác thực code
            temp_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'verify_code.py')
            with open(temp_script, 'w', encoding='utf-8') as f:
                f.write("""
import os
import sys
import json
from telethon import TelegramClient

api_id = int(sys.argv[1])
api_hash = sys.argv[2]
phone = sys.argv[3]
code = sys.argv[4]
phone_code_hash = sys.argv[5] if len(sys.argv) > 5 else None

async def main():
    # Sử dụng cùng session_path
    session_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'telegram_uploader')
    client = TelegramClient(session_path, api_id, api_hash)
    
    await client.connect()
    try:
        if phone_code_hash:
            await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
        else:
            await client.sign_in(phone, code)
        print(json.dumps({'status': 'SUCCESS'}))
    except Exception as e:
        print(json.dumps({'status': 'ERROR', 'message': str(e)}))
    
    await client.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
""")
            
            # Chạy script với Python, thêm phone_code_hash nếu có
            python_executable = sys.executable
            args = [python_executable, temp_script, str(api_id), api_hash, phone, otp_code]
            if self.phone_code_hash:
                args.append(self.phone_code_hash)
                
            result = subprocess.run(args, capture_output=True, text=True)
            
            # Xóa file tạm
            try:
                os.remove(temp_script)
            except:
                pass
            
            # Kiểm tra kết quả từ JSON
            stdout = result.stdout.strip()
            if stdout:
                try:
                    response = json.loads(stdout)
                    if response.get('status') == 'SUCCESS':
                        return True
                    elif response.get('status') == 'ERROR':
                        messagebox.showerror("Lỗi", f"Không thể xác thực: {response.get('message', 'Lỗi không xác định')}")
                        return False
                except json.JSONDecodeError:
                    pass
            
            # Hiển thị lỗi từ stderr nếu không đọc được stdout
            error_msg = result.stderr or "Không xác định được lỗi"
            messagebox.showerror("Lỗi", f"Không thể xác thực: {error_msg}")
            return False
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xác thực OTP: {str(e)}")
            return False
    
    def save_settings(self):
      """Save the configuration settings"""
      # Get and validate settings
      api_id = self.api_id_var.get().strip()
      api_hash = self.api_hash_var.get().strip()
      phone = self.phone_var.get().strip()
      
      if not api_id or not api_hash or not phone:
          messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ API ID, API Hash và số điện thoại!")
          return
      
      # If Telethon verification is in progress, check if it's completed
      if self.telethon_verification_in_progress:
          if self.otp_button.cget("text") != "✓ Đã xác thực thành công":
              messagebox.showerror("Lỗi", "Vui lòng hoàn thành xác thực OTP trước khi lưu cài đặt!")
              return
      
      # Try to convert API ID to int to validate
      try:
          api_id_int = int(api_id)
      except ValueError:
          messagebox.showerror("Lỗi", "API ID phải là một số nguyên!")
          return
      
      # Save settings to config
      self.app.config['TELETHON']['api_id'] = api_id
      self.app.config['TELETHON']['api_hash'] = api_hash
      self.app.config['TELETHON']['phone'] = phone
      self.app.config['TELETHON']['use_telethon'] = 'true'
      
      # Save configuration
      self.app.config_manager.save_config(self.app.config)
      
      # Update the values in the settings tab
      self.app.api_id_var.set(api_id)
      self.app.api_hash_var.set(api_hash)
      self.app.phone_var.set(phone)
      self.app.use_telethon_var.set(True)
      
      # THÊM MỚI: Kiểm tra trạng thái kết nối thực tế và cập nhật lại
      try:
          logger.info("Kiểm tra lại trạng thái kết nối Telethon sau khi lưu cấu hình")
          if hasattr(self.app.telethon_uploader, 'is_connected'):
              is_connected = self.app.telethon_uploader.is_connected()
              self.app.telethon_uploader.connected = is_connected
              logger.info(f"Trạng thái kết nối Telethon sau khi lưu cấu hình: {is_connected}")
      except Exception as e:
          logger.error(f"Lỗi khi kiểm tra lại kết nối Telethon: {str(e)}")
      
      # Show success message
      messagebox.showinfo("Thành công", "Đã lưu cài đặt Telethon API thành công!")
      
      # Close modal
      self.modal.destroy()
      
      # Refresh current tab - Compatible with custom tab navigation
      if hasattr(self.app, 'switch_tab') and hasattr(self.app, 'tab_buttons'):
          # Find which tab is currently active by checking button colors
          current_tab = 0  # Default to first tab
          for i, btn in enumerate(self.app.tab_buttons):
              if btn.cget("bg") == "#2E86C1" or btn.cget("bg") == "#4a7ebb":  # Active tab color
                  current_tab = i
                  break
          
          # Refresh the current tab
          self.app.switch_tab(current_tab)
