"""
Telegram Video Uploader Application
==================================

Main application to upload videos to Telegram with advanced features.
"""
import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from queue import Queue

# Define variable to decide whether to use Qt or Tkinter
USE_QT_UI = True  # True = use Qt, False = use Tkinter

# Import PyQt5 if using Qt UI
if USE_QT_UI:
    try:
        from PyQt5 import QtWidgets
    except ImportError:
        USE_QT_UI = False
        logging.warning("Could not import PyQt5, switching to Tkinter")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("telegram_uploader.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TelegramUploader")

# Import UI modules conditionally
from ui.splash_screen import show_splash_screen

# Import core modules
from core.config_manager import ConfigManager
from core.telegram_connector import TelegramConnector

# Import utilities
from utils.video_analyzer import VideoAnalyzer
from utils.upload_history import UploadHistory
from utils.ffmpeg_manager import FFmpegManager

class TelegramUploaderApp:
    """
    Main application for uploading videos to Telegram.
    """
    def __init__(self, root=None):
        """
        Initialize the application.
        
        Args:
            root: Tkinter root window (optional, only used in Tkinter mode)
        """
        self.root = root
        self.qt_app = None
        self.qt_main_window = None
        
        # Set up components
        self._initialize_components()
        
        # Set up UI based on mode
        if USE_QT_UI:
            self._setup_qt_ui()
        else:
            self._setup_tkinter_ui()
    
    def _initialize_components(self):
        """Initialize core components"""
        logger.info("Initializing application components")
        
        # Initialize configuration
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # Initialize FFmpeg manager
        self.ffmpeg_manager = FFmpegManager()
        
        # Initialize video analyzer
        self.video_analyzer = VideoAnalyzer()
        
        # Initialize upload history
        history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload_history.json')
        self.upload_history = UploadHistory(history_file)
        
        # Initialize Telegram connection
        self.telegram_connector = TelegramConnector(self)
        self.telegram_api = self.telegram_connector.telegram_api
        self.telethon_uploader = self.telegram_connector.telethon_uploader
    
    def _setup_qt_ui(self):
        """Set up the Qt UI"""
        logger.info("Setting up Qt UI")
        
        try:
            # Import the Qt UI
            from ui.main_tab.main_ui import MainUI
            
            # Create Qt application instance if needed
            if QtWidgets.QApplication.instance() is None:
                self.qt_app = QtWidgets.QApplication(sys.argv)
            else:
                self.qt_app = QtWidgets.QApplication.instance()
            
            # Create main window
            self.qt_main_window = MainUI(self)
            
            # Show the window
            self.qt_main_window.show()
            
        except Exception as e:
            logger.error(f"Error setting up Qt UI: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Fall back to Tkinter if Qt fails
            if self.root:
                self._setup_tkinter_ui()
    
    def _setup_tkinter_ui(self):
        """Set up the Tkinter UI"""
        logger.info("Setting up Tkinter UI")
        
        if not self.root:
            logger.error("No Tkinter root window provided")
            return
        
        # Set up Tkinter window
        self.root.title("Telegram Video Uploader")
        
        # Set window size and position
        self._setup_window()
        
        # Set up TTK styles
        self._setup_styles()
        
        # Show splash screen
        show_splash_screen(self)
        
        # Create UI
        self._create_tkinter_ui()
        
        # Set close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_window(self):
        """Set up window size and position"""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window size (90% of screen)
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # Center window
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        # Apply size and position
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.root.minsize(1024, 768)
        
        # Maximize on Windows
        self.root.state('zoomed')
        
        # Set icon if available
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            logger.warning(f"Could not set icon: {e}")
    
    def _setup_styles(self):
        """Set up TTK styles"""
        if not hasattr(self, 'root') or not self.root:
            return
            
        style = ttk.Style()
        
        # Common fonts
        default_font = ("Segoe UI", 10)
        heading_font = ("Segoe UI", 11, "bold")
        
        # Button style
        style.configure("TButton", padding=(10, 5), font=default_font)
        
        # Label styles
        style.configure("TLabel", font=default_font)
        style.configure("Heading.TLabel", font=heading_font)
        
        # Frame styles
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabelframe", background="#f0f0f0", font=default_font)
        style.configure("TLabelframe.Label", font=heading_font)
        
        # Treeview styles
        style.configure("Treeview", font=default_font, rowheight=30)
        style.configure("Treeview.Heading", font=heading_font)
        
        # Status label
        style.configure("Status.TLabel", font=default_font, foreground="#0066CC")
        
        # Blue button
        style.configure("Blue.TButton", font=default_font)
        style.map("Blue.TButton",
                background=[("active", "#2980b9"), ("!active", "#3498db")],
                foreground=[("active", "white"), ("!active", "white")])
    
    def _create_tkinter_ui(self):
        """Create Tkinter UI"""
        if not hasattr(self, 'root') or not self.root:
            return
            
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add message that Qt UI should be used
        message_frame = ttk.Frame(main_frame, padding=20)
        message_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            message_frame, 
            text="The Tkinter UI is deprecating for the main tab", 
            font=("Arial", 16, "bold"),
            style="Heading.TLabel"
        ).pack(pady=(100, 20))
        
        ttk.Label(
            message_frame, 
            text="Please use the PyQt5 version for the best experience", 
            font=("Arial", 14),
            style="Heading.TLabel"
        ).pack(pady=10)
        
        ttk.Button(
            message_frame,
            text="Switch to PyQt5 UI",
            command=self._try_switch_to_qt,
            style="Blue.TButton"
        ).pack(pady=20)
    
    def _try_switch_to_qt(self):
        """Try to switch to Qt UI"""
        try:
            # Hide Tkinter window
            if hasattr(self, 'root') and self.root:
                self.root.withdraw()
            
            # Set up Qt UI
            self._setup_qt_ui()
            
            # Destroy Tkinter window if Qt UI was created successfully
            if self.qt_main_window:
                if hasattr(self, 'root') and self.root:
                    self.root.destroy()
                    self.root = None
        except Exception as e:
            logger.error(f"Error switching to Qt UI: {str(e)}")
            messagebox.showerror("Error", f"Could not switch to Qt UI: {str(e)}")
            
            # Show Tkinter window again
            if hasattr(self, 'root') and self.root:
                self.root.deiconify()
    
    def run(self):
        """Run the application"""
        if USE_QT_UI and self.qt_app:
            # Run Qt application
            return self.qt_app.exec_()
        elif hasattr(self, 'root') and self.root:
            # Run Tkinter application
            self.root.mainloop()
    
    def _on_closing(self):
        """Handle application closing"""
        # Ask for confirmation if uploading
        is_uploading = False
        if hasattr(self, 'qt_main_window') and self.qt_main_window:
            is_uploading = getattr(self.qt_main_window, 'is_uploading', False)
        
        if is_uploading:
            if not messagebox.askyesno("Confirm", "Videos are being uploaded. Are you sure you want to exit?"):
                return
        
        # Save configuration
        self.config_manager.save_config(self.config)
        
        # Disconnect APIs
        if hasattr(self, 'telegram_api'):
            self.telegram_api.disconnect()
        
        if hasattr(self, 'telethon_uploader'):
            self.telethon_uploader.disconnect()
        
        # Close window
        if hasattr(self, 'root') and self.root:
            self.root.destroy()