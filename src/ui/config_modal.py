"""
Module for the initial configuration modal that appears when no Telegram configuration exists.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import os
import sys
import asyncio
import threading

logger = logging.getLogger("ConfigModal")

class TelegramConfigModal:
    """
    Modal dialog for initial Telegram configuration when app starts with no configuration.
    """
    
    def __init__(self, app):
        """
        Initialize the configuration modal
        
        Args:
            app: The main application instance
        """
        self.app = app
        self.modal = None
        self.telethon_verification_in_progress = False
        
        # Create modal window
        self.create_modal()
        
    def create_modal(self):
        """Create the configuration modal UI"""
        self.modal = tk.Toplevel(self.app.root)
        self.modal.title("Cấu hình Telegram")
        self.modal.transient(self.app.root)
        self.modal.grab_set()
        
        # Set size and position
        window_width = 800
        window_height = 600
        x = (self.modal.winfo_screenwidth() // 2) - (window_width // 2)
        y = (self.modal.winfo_screenheight() // 2) - (window_height // 2)
        self.modal.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Prevent closing the window with X button
        self.modal.protocol("WM_DELETE_WINDOW", self.prevent_close)
        
        # Main title
        title_label = ttk.Label(
            self.modal, 
            text="Cấu hình Telegram",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Main content frame with grid (2 columns)
        content_frame = ttk.Frame(self.modal)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Configure grid columns to be equal width
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        
        # Left column - Telegram Bot configuration
        bot_frame = ttk.LabelFrame(content_frame, text="Cấu hình Telegram Bot")
        bot_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Token input
        ttk.Label(bot_frame, text="Token Telegram - (Tìm trong @BotFather)").pack(anchor=tk.W, padx=10, pady=(10, 5))
        self.token_var = tk.StringVar()
        token_entry = ttk.Entry(bot_frame, textvariable=self.token_var, width=40)
        token_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Chat ID input
        ttk.Label(bot_frame, text="Chat ID - (Có định dạng: -100xxxxxxxxxx)").pack(anchor=tk.W, padx=10, pady=(10, 5))
        self.chat_id_var = tk.StringVar()
        chat_id_entry = ttk.Entry(bot_frame, textvariable=self.chat_id_var, width=40)
        chat_id_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Right column - Telethon API configuration
        api_frame = ttk.LabelFrame(content_frame, text="Cấu hình Telethon API")
        api_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # API ID input
        ttk.Label(api_frame, text="API ID - (Có định dạng: 2xxxxxxx)").pack(anchor=tk.W, padx=10, pady=(10, 5))
        self.api_id_var = tk.StringVar()
        api_id_entry = ttk.Entry(api_frame, textvariable=self.api_id_var, width=40)
        api_id_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # API Hash input
        ttk.Label(api_frame, text="API Hash - (Có định dạng: 7xxxxxe)").pack(anchor=tk.W, padx=10, pady=(10, 5))
        self.api_hash_var = tk.StringVar()
        api_hash_entry = ttk.Entry(api_frame, textvariable=self.api_hash_var, width=40)
        api_hash_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Phone number input
        ttk.Label(api_frame, text="Số điện thoại - (Có định dạng: +84123456789)").pack(anchor=tk.W, padx=10, pady=(10, 5))
        self.phone_var = tk.StringVar()
        phone_entry = ttk.Entry(api_frame, textvariable=self.phone_var, width=40)
        phone_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # OTP verification group
        otp_frame = ttk.LabelFrame(api_frame, text="Xác thực OTP")
        otp_frame.pack(fill=tk.X, padx=10, pady=(10, 10))
        
        # OTP code input and button
        otp_input_frame = ttk.Frame(otp_frame)
        otp_input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(otp_input_frame, text="Mã OTP").pack(side=tk.LEFT)
        self.otp_var = tk.StringVar()
        otp_entry = ttk.Entry(otp_input_frame, textvariable=self.otp_var, width=20)
        otp_entry.pack(side=tk.LEFT, padx=10)
        
        self.otp_button = ttk.Button(otp_input_frame, text="Lấy", command=self.request_otp)
        self.otp_button.pack(side=tk.LEFT)
        
        # Footer with buttons
        footer_frame = ttk.Frame(self.modal)
        footer_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Test connection button
        test_button = ttk.Button(
            footer_frame, 
            text="Kiểm tra kết nối", 
            command=self.test_connection
        )
        test_button.pack(side=tk.LEFT, padx=10)
        
        # Save settings button
        save_button = ttk.Button(
            footer_frame, 
            text="Lưu cài đặt", 
            command=self.save_settings
        )
        save_button.pack(side=tk.RIGHT, padx=10)
        
        # Focus on first input
        token_entry.focus_set()
        
    def prevent_close(self):
        """Prevent closing the modal if no configuration exists"""
        messagebox.showwarning(
            "Cấu hình bắt buộc", 
            "Bạn cần phải cấu hình Telegram để sử dụng ứng dụng.\n"
            "Vui lòng điền thông tin và nhấn 'Lưu cài đặt'."
        )
    
    def request_otp(self):
        """Request OTP for Telethon verification"""
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
            
            # Initialize Telethon client and request verification code
            def request_code():
                try:
                    # Initialize Telethon client
                    from telethon import TelegramClient
                    session_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'telegram_uploader')
                    client = TelegramClient(session_path, api_id, api_hash)
                    
                    async def request_code_async():
                        await client.connect()
                        if not await client.is_user_authorized():
                            await client.send_code_request(phone)
                            return True
                        else:
                            # Already authorized
                            return True
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    success = loop.run_until_complete(request_code_async())
                    
                    if success:
                        self.telethon_verification_in_progress = True
                        self.app.root.after(0, lambda: messagebox.showinfo(
                            "Mã xác thực", 
                            f"Mã xác thực đã được gửi đến {phone}. Vui lòng nhập mã vào ô OTP."
                        ))
                    
                except Exception as e:
                    self.app.root.after(0, lambda: messagebox.showerror(
                        "Lỗi", 
                        f"Không thể gửi mã xác thực: {str(e)}"
                    ))
                finally:
                    # Re-enable OTP button
                    self.app.root.after(0, lambda: self.otp_button.config(text="Lấy", state=tk.NORMAL))
            
            # Run in a separate thread to avoid blocking UI
            threading.Thread(target=request_code, daemon=True).start()
            
        except ValueError:
            messagebox.showerror("Lỗi", "API ID phải là một số nguyên!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi yêu cầu mã OTP: {str(e)}")
            self.otp_button.config(text="Lấy", state=tk.NORMAL)
    
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
            
            # Initialize Telethon client and verify code
            from telethon import TelegramClient
            session_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'telegram_uploader')
            client = TelegramClient(session_path, api_id, api_hash)
            
            async def verify_code_async():
                await client.connect()
                try:
                    await client.sign_in(phone, otp_code)
                    return True
                except Exception as e:
                    self.app.root.after(0, lambda: messagebox.showerror(
                        "Lỗi", 
                        f"Không thể xác thực: {str(e)}"
                    ))
                    return False
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(verify_code_async())
            
            return success
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xác thực OTP: {str(e)}")
            return False
    
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
        # Get and validate Bot API settings
        bot_token = self.token_var.get().strip()
        chat_id = self.chat_id_var.get().strip()
        
        if not bot_token or not chat_id:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ Token và Chat ID!")
            return
        
        # Get Telethon API settings
        api_id = self.api_id_var.get().strip()
        api_hash = self.api_hash_var.get().strip()
        phone = self.phone_var.get().strip()
        
        # If Telethon verification is in progress, verify OTP
        if self.telethon_verification_in_progress and api_id and api_hash and phone:
            if not self.verify_otp():
                return  # OTP verification failed
        
        # Save settings to config
        self.app.config['TELEGRAM']['bot_token'] = bot_token
        self.app.config['TELEGRAM']['chat_id'] = chat_id
        self.app.config['TELEGRAM']['notification_chat_id'] = chat_id  # Use same chat ID for notifications
        
        # Save Telethon settings if provided
        if api_id and api_hash and phone:
            try:
                api_id_int = int(api_id)  # Validate API ID
                self.app.config['TELETHON']['api_id'] = api_id
                self.app.config['TELETHON']['api_hash'] = api_hash
                self.app.config['TELETHON']['phone'] = phone
                self.app.config['TELETHON']['use_telethon'] = 'true'
            except ValueError:
                messagebox.showerror("Lỗi", "API ID phải là một số nguyên!")
                return
        
        # Save configuration
        self.app.config_manager.save_config(self.app.config)
        
        # Reconnect with new settings
        self.app.telegram_connector.connect_telegram(self.app)
        
        # Show success message
        messagebox.showinfo("Thành công", "Cài đặt đã được lưu thành công!")
        
        # Close modal
        self.modal.destroy()