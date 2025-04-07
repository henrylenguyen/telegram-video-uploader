"""
Functions to integrate the PyQt5 gallery with the main Tkinter application
"""
import os
import sys
import logging
import tempfile
import threading
import subprocess
from tkinter import messagebox

logger = logging.getLogger(__name__)

def open_gallery_modal(image_paths, initial_index=0):
    """
    Open the gallery modal in a separate process
    
    Args:
        image_paths: List of paths to the images to display
        initial_index: Index of the initial image to display
    """
    try:
        # Validate paths
        valid_paths = []
        for path in image_paths:
            if os.path.exists(path) and os.path.isfile(path):
                valid_paths.append(path)
        
        if not valid_paths:
            logger.error("No valid image paths provided")
            return False
        
        # Create a temporary file to store the paths
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file_path = temp_file.name
        
        # Write paths to the file
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            f.write(f"{initial_index}\n")  # First line is initial index
            for path in valid_paths:
                f.write(f"{path}\n")
        
        # Create and run the PyQt5 process
        def run_gallery():
            try:
                # Create a separate Python script to run the gallery
                script_content = '''
import sys
import os
from PyQt5.QtWidgets import QApplication, QShortcut
from PyQt5.QtGui import QKeySequence

# Import GalleryModal class
try:
    # First try to import from installed module
    from ui.components.gallery_modal_pyqt5 import GalleryModal
except ImportError:
    # Then try relative import
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ui.components.gallery_modal_pyqt5 import GalleryModal

def main():
    # Read paths from file
    if len(sys.argv) < 2:
        print("No path file provided")
        return 1
    
    path_file = sys.argv[1]
    if not os.path.exists(path_file):
        print(f"Path file does not exist: {path_file}")
        return 1
    
    with open(path_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if not lines:
        print("No paths in file")
        return 1
    
    # First line is initial index
    try:
        initial_index = int(lines[0].strip())
    except:
        initial_index = 0
    
    # Rest of lines are paths
    image_paths = [line.strip() for line in lines[1:] if line.strip()]
    
    if not image_paths:
        print("No valid paths found")
        return 1
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show gallery
    gallery = GalleryModal(image_paths, initial_index=initial_index)
    gallery.show()
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
'''
                
                # Create a temporary script file
                script_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py')
                script_path = script_file.name
                
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                
                # Run the script
                subprocess.run([sys.executable, script_path, temp_file_path])
                
                # Clean up
                try:
                    os.unlink(temp_file_path)
                    os.unlink(script_path)
                except:
                    pass
                
            except Exception as e:
                logger.error(f"Error running gallery: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Run in a separate thread
        gallery_thread = threading.Thread(target=run_gallery)
        gallery_thread.daemon = True
        gallery_thread.start()
        
        return True
        
    except Exception as e:
        logger.error(f"Error opening gallery: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        messagebox.showerror("Lỗi", f"Không thể mở gallery: {str(e)}")
        return False