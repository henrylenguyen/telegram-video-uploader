"""
Build script for Telegram Video Uploader
========================================

This script builds the application into a standalone executable for Windows, macOS, or Linux.
It handles:
- Cleaning old builds
- Setting up resources (FFmpeg, configs, etc.)
- Building with PyInstaller
- Creating distribution packages
"""
import PyInstaller.__main__
import os
import sys
import shutil
import configparser
import urllib.request
import zipfile
import tarfile
import argparse
import platform
import subprocess
import logging
import datetime
import tempfile
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('build')

# Define constants
SCRIPT_DIR = Path(__file__).parent.absolute()
BASE_DIR = SCRIPT_DIR.parent
SRC_DIR = BASE_DIR / 'src'
DIST_DIR = BASE_DIR / 'dist'
BUILD_DIR = BASE_DIR / 'build'
OUTPUT_DIR = BASE_DIR / 'output'
DOCS_DIR = BASE_DIR / 'docs'
TEMP_DIR = Path(tempfile.gettempdir()) / 'telegram_uploader_build'
VERSION = "1.0"

# FFmpeg download URLs
FFMPEG_URLS = {
    'windows': "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
    'darwin': "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip",  # macOS
    'linux': "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
}

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Build Telegram Video Uploader')
    parser.add_argument('--clean-only', action='store_true', help='Only clean build directories')
    parser.add_argument('--skip-ffmpeg', action='store_true', help='Skip FFmpeg download')
    parser.add_argument('--skip-zip', action='store_true', help='Skip creating ZIP archive')
    parser.add_argument('--platform', choices=['auto', 'windows', 'macos', 'linux'], 
                        default='auto', help='Target platform (default: auto-detect)')
    
    return parser.parse_args()

def get_platform(args):
    """Determine target platform"""
    if args.platform != 'auto':
        platform_map = {'windows': 'windows', 'macos': 'darwin', 'linux': 'linux'}
        return platform_map[args.platform]
    
    system = platform.system().lower()
    if system not in ('windows', 'darwin', 'linux'):
        logger.error(f"Unsupported platform: {system}")
        sys.exit(1)
    return system

def clean_build_dirs():
    """Clean old build directories"""
    logger.info("Cleaning old build directories...")
    
    for directory in [DIST_DIR, BUILD_DIR, OUTPUT_DIR, TEMP_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(exist_ok=True, parents=True)
    
    # Create additional directories
    (OUTPUT_DIR / 'config').mkdir(exist_ok=True)
    (OUTPUT_DIR / 'docs').mkdir(exist_ok=True)
    
    logger.info("Build directories cleaned successfully")

def download_ffmpeg(target_platform):
    """Download and prepare FFmpeg for inclusion in the application"""
    logger.info("Downloading and preparing FFmpeg...")
    
    # Create FFmpeg directory
    ffmpeg_dir = OUTPUT_DIR / 'ffmpeg'
    ffmpeg_dir.mkdir(exist_ok=True)
    
    # Get download URL for the platform
    if target_platform not in FFMPEG_URLS:
        logger.error(f"No FFmpeg download URL for platform {target_platform}")
        return False
    
    url = FFMPEG_URLS[target_platform]
    
    try:
        # Download FFmpeg
        logger.info(f"Downloading FFmpeg from {url}...")
        archive_path = TEMP_DIR / f"ffmpeg{'.zip' if target_platform in ('windows', 'darwin') else '.tar.xz'}"
        urllib.request.urlretrieve(url, archive_path)
        
        # Extract files
        logger.info("Extracting FFmpeg...")
        if target_platform in ('windows', 'darwin'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(TEMP_DIR)
        else:  # Linux
            with tarfile.open(archive_path, 'r:xz') as tar_ref:
                tar_ref.extractall(TEMP_DIR)
        
        # Find and copy the FFmpeg binaries
        ffmpeg_exe = "ffmpeg.exe" if target_platform == "windows" else "ffmpeg"
        ffprobe_exe = "ffprobe.exe" if target_platform == "windows" else "ffprobe"
        
        # Search for the binaries
        found_binaries = False
        for root, dirs, files in os.walk(TEMP_DIR):
            if ffmpeg_exe in files and ffprobe_exe in files:
                # Copy files
                for binary in [ffmpeg_exe, ffprobe_exe]:
                    src = Path(root) / binary
                    dst = ffmpeg_dir / binary
                    shutil.copy2(src, dst)
                    
                    # Make executable on Unix
                    if target_platform in ('darwin', 'linux'):
                        os.chmod(dst, 0o755)
                
                logger.info(f"Copied FFmpeg binaries to {ffmpeg_dir}")
                found_binaries = True
                break
        
        if not found_binaries:
            logger.warning("Could not find FFmpeg binaries in the downloaded package")
            create_ffmpeg_readme(ffmpeg_dir)
            return False
        
        # Clean up
        if archive_path.exists():
            os.remove(archive_path)
        
        return True
    
    except Exception as e:
        logger.error(f"Error downloading FFmpeg: {e}")
        create_ffmpeg_readme(ffmpeg_dir)
        return False

def create_ffmpeg_readme(ffmpeg_dir):
    """Create README file with instructions for manual FFmpeg installation"""
    readme_path = ffmpeg_dir / 'README.txt'
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("Could not automatically download FFmpeg.\n\n")
        f.write("Please download FFmpeg manually from: https://ffmpeg.org/download.html\n")
        f.write("Then copy ffmpeg and ffprobe executables to this directory.\n")

def create_config_template():
    """Create template config.ini file"""
    logger.info("Creating config.ini template...")
    
    config = configparser.ConfigParser()
    config['TELEGRAM'] = {
        'bot_token': '',
        'chat_id': '',
        'notification_chat_id': ''
    }
    config['SETTINGS'] = {
        'video_folder': '',
        'video_extensions': '.mp4,.avi,.mkv,.mov,.wmv',
        'delay_between_uploads': '5',
        'auto_mode': 'false',
        'check_duplicates': 'true',
        'auto_check_interval': '60'
    }
    config['TELETHON'] = {
        'api_id': '',
        'api_hash': '',
        'phone': '',
        'use_telethon': 'false'
    }
    
    config_path = OUTPUT_DIR / 'config.ini'
    with open(config_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    
    logger.info(f"Created config template at {config_path}")

def find_icon():
    """Find icon for the application"""
    icon_paths = [
        SRC_DIR / 'icon.ico',
        BUILD_DIR / 'icon.ico',
        SCRIPT_DIR / 'icon.ico'
    ]
    
    for path in icon_paths:
        if path.exists():
            return path
    
    return None

def build_application(target_platform):
    """Build the main application using PyInstaller"""
    logger.info("Building main application...")
    
    # Find icon
    icon_path = find_icon()
    icon_param = f'--icon={icon_path}' if icon_path else ''
    
    # Main script
    main_py = SRC_DIR / 'telegram_uploader.py'
    if not main_py.exists():
        main_py = SRC_DIR / 'main.py'  # Fallback to main.py if telegram_uploader.py doesn't exist
    
    # Platform-specific options
    console_option = '--windowed' if target_platform in ('windows', 'darwin') else '--console'
    
    # Base options
    options = [
        str(main_py),                    # Main script
        '--name=Telegram_Video_Uploader',  # App name
        '--onefile',                       # Single executable
        console_option,                    # UI mode
        icon_param,                        # Icon
        '--clean',                         # Clean cache
        '--noconfirm',                     # No confirmation
        # Add hidden imports
        '--hidden-import=telebot',
        '--hidden-import=PIL',
        '--hidden-import=cv2',
        '--hidden-import=imagehash',
        '--hidden-import=telethon',
        # Add data files
        f'--add-data={SRC_DIR / "utils"}/*.py;utils',
    ]
    
    # Add resources if available
    if icon_path:
        options.append(f'--add-data={icon_path};.')
    
    # Run PyInstaller
    PyInstaller.__main__.run(options)
    
    logger.info("Main application built successfully")
    return True

def build_config_tool(target_platform):
    """Build the configuration tool"""
    logger.info("Building configuration tool...")
    
    # Find icon
    icon_path = find_icon()
    icon_param = f'--icon={icon_path}' if icon_path else ''
    
    # Main script (using the same script with config mode)
    main_py = SRC_DIR / 'telegram_uploader.py'
    if not main_py.exists():
        main_py = SRC_DIR / 'main.py'  # Fallback to main.py if telegram_uploader.py doesn't exist
    
    # Create output directory
    config_dist = DIST_DIR / 'config'
    config_dist.mkdir(exist_ok=True)
    
    # Platform-specific options
    console_option = '--windowed' if target_platform in ('windows', 'darwin') else '--console'
    
    # Build options
    options = [
        str(main_py),                        # Main script
        '--name=Telegram_Uploader_Config',   # App name
        '--onefile',                         # Single executable
        console_option,                      # UI mode
        icon_param,                          # Icon
        '--clean',                           # Clean cache
        '--noconfirm',                       # No confirmation
        # Add hidden imports
        '--hidden-import=telebot',
        # Add data files
        f'--add-data={SRC_DIR / "utils"}/*.py;utils',
        f'--distpath={config_dist}',         # Custom output directory
    ]
    
    # Run PyInstaller
    PyInstaller.__main__.run(options)
    
    logger.info("Configuration tool built successfully")
    return True

def create_additional_files(target_platform):
    """Create additional files like README and startup scripts"""
    logger.info("Creating additional files...")
    
    # Create README.txt
    readme_content = """
TELEGRAM VIDEO UPLOADER
=======================

Version: 1.0
(c) 2025 - All rights reserved

Setup Instructions:
------------------

1. INITIAL CONFIGURATION:
   - Run "config/Telegram_Uploader_Config" to configure Telegram information
   - Enter your Bot Token and Chat ID (see instructions in the app)
   - Test the connection and save the configuration

2. USING THE MAIN APPLICATION:
   - Run "Telegram_Video_Uploader" to open the main application
   - Select a folder containing videos
   - Select videos to upload and click "Start Upload"
   - Or use the Auto mode in the "Auto" tab

Features:
---------
- Detect and filter duplicate videos
- Auto-upload mode for new videos in a folder
- Support for multiple common video formats
- User-friendly interface
- Support for uploading videos of unlimited size

Notes:
------
- Your Telegram Bot needs permission to send messages and media in the target channel/group
- The application includes FFmpeg for handling large videos
- See detailed instructions in the docs folder

Support Contact:
--------------
If you need assistance, please contact:
- Email: support@example.com
- GitHub: https://github.com/username/telegram-video-uploader/issues
"""

    with open(OUTPUT_DIR / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Create platform-specific setup files
    if target_platform == 'windows':
        # Create SETUP.bat for Windows
        setup_content = """
@echo off
echo ===================================
echo  TELEGRAM VIDEO UPLOADER - SETUP
echo ===================================
echo.
echo Setting up the application...
echo.
echo 1. Configure application settings
echo -----------------------------------
start "" "config\\Telegram_Uploader_Config.exe"
echo.
echo After configuration, you can run the main application.
echo.
pause
"""
        with open(OUTPUT_DIR / 'SETUP.bat', 'w', encoding='utf-8') as f:
            f.write(setup_content)
        
        # Create FFmpeg-PATH.bat for Windows
        ffmpeg_path_content = """
@echo off
echo ===================================
echo  FFMPEG PATH SETUP
echo ===================================
echo.
echo Setting up FFmpeg path...
SET "CURRENT_DIR=%~dp0"
SET "FFMPEG_DIR=%CURRENT_DIR%ffmpeg"

REM Add FFmpeg to PATH for current session
SET "PATH=%FFMPEG_DIR%;%PATH%"

REM Check installation
ffmpeg -version
if %ERRORLEVEL% NEQ 0 (
    echo Error: Could not set up FFmpeg. Please check the ffmpeg directory.
) else (
    echo FFmpeg setup successful!
)
echo.
echo You can now run the application.
echo.
pause
"""
        with open(OUTPUT_DIR / 'FFmpeg-PATH.bat', 'w', encoding='utf-8') as f:
            f.write(ffmpeg_path_content)
    
    elif target_platform in ('darwin', 'linux'):
        # Create setup.sh for macOS/Linux
        setup_content = """#!/bin/bash
echo "==================================="
echo " TELEGRAM VIDEO UPLOADER - SETUP"
echo "==================================="
echo
echo "Setting up the application..."
echo
echo "1. Configure application settings"
echo "-----------------------------------"
chmod +x config/Telegram_Uploader_Config
./config/Telegram_Uploader_Config &
echo
echo "After configuration, you can run the main application."
echo
"""
        setup_path = OUTPUT_DIR / 'setup.sh'
        with open(setup_path, 'w', encoding='utf-8') as f:
            f.write(setup_content)
        # Make executable
        os.chmod(setup_path, 0o755)
        
        # Create ffmpeg-path.sh for macOS/Linux
        ffmpeg_path_content = """#!/bin/bash
echo "==================================="
echo " FFMPEG PATH SETUP"
echo "==================================="
echo
echo "Setting up FFmpeg path..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FFMPEG_DIR="$SCRIPT_DIR/ffmpeg"

# Add FFmpeg to PATH for current session
export PATH="$FFMPEG_DIR:$PATH"

# Check installation
if ffmpeg -version &> /dev/null; then
    echo "FFmpeg setup successful!"
else
    echo "Error: Could not set up FFmpeg. Please check the ffmpeg directory."
fi
echo
echo "You can now run the application."
echo
"""
        ffmpeg_path = OUTPUT_DIR / 'ffmpeg-path.sh'
        with open(ffmpeg_path, 'w', encoding='utf-8') as f:
            f.write(ffmpeg_path_content)
        # Make executable
        os.chmod(ffmpeg_path, 0o755)
    
    logger.info("Additional files created successfully")

def copy_files_to_output(target_platform):
    """Copy built files to output directory"""
    logger.info("Copying files to output directory...")
    
    # Executable extension based on platform
    exe_ext = '.exe' if target_platform == 'windows' else ''
    
    # Copy main executable
    main_exe = DIST_DIR / f"Telegram_Video_Uploader{exe_ext}"
    if main_exe.exists():
        shutil.copy2(main_exe, OUTPUT_DIR)
    else:
        logger.error(f"Main executable not found: {main_exe}")
    
    # Copy config tool
    config_exe = DIST_DIR / 'config' / f"Telegram_Uploader_Config{exe_ext}"
    if config_exe.exists():
        shutil.copy2(config_exe, OUTPUT_DIR / 'config')
    else:
        logger.error(f"Config tool not found: {config_exe}")
    
    # Copy documentation
    docs_output = OUTPUT_DIR / 'docs'
    if DOCS_DIR.exists():
        for doc_file in DOCS_DIR.glob('*.md'):
            shutil.copy2(doc_file, docs_output)
        
        # Copy images if they exist
        images_dir = docs_output / 'images'
        images_dir.mkdir(exist_ok=True)
        
        source_images = DOCS_DIR / 'images'
        if source_images.exists():
            for img_file in source_images.glob('*'):
                shutil.copy2(img_file, images_dir)
    
    logger.info("Files copied to output successfully")

def create_release_zip():
    """Create ZIP file for release"""
    logger.info("Creating release ZIP file...")
    
    # Create ZIP filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    zip_filename = f"Telegram_Video_Uploader_v{VERSION}_{timestamp}.zip"
    zip_path = BASE_DIR / zip_filename
    
    # Create ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(OUTPUT_DIR)
                zipf.write(file_path, arcname)
    
    logger.info(f"Release ZIP created at: {zip_path}")
    return zip_path

def main():
    """Main build function"""
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Get target platform
        target_platform = get_platform(args)
        logger.info(f"Building for platform: {target_platform}")
        
        # Clean build directories
        clean_build_dirs()
        
        # If clean-only flag is set, exit
        if args.clean_only:
            logger.info("Clean-only flag set, exiting")
            return
        
        # Create config template
        create_config_template()
        
        # Download FFmpeg if required
        if not args.skip_ffmpeg:
            download_ffmpeg(target_platform)
        else:
            logger.info("Skipping FFmpeg download as requested")
        
        # Build applications
        build_application(target_platform)
        build_config_tool(target_platform)
        
        # Create additional files
        create_additional_files(target_platform)
        
        # Copy files to output directory
        copy_files_to_output(target_platform)
        
        # Create release ZIP if required
        if not args.skip_zip:
            zip_path = create_release_zip()
            logger.info(f"Build completed successfully! Release package: {zip_path}")
        else:
            logger.info(f"Build completed successfully! Output directory: {OUTPUT_DIR}")
        
        # Provide usage instructions
        logger.info("\nUsage instructions:")
        logger.info("1. Distribute the ZIP file to users")
        logger.info("2. Instruct users to extract the ZIP and run SETUP.bat (Windows) or setup.sh (macOS/Linux)")
    
    except Exception as e:
        logger.error(f"Build failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()