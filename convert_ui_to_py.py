#!/usr/bin/env python
"""
Script để chuyển đổi tất cả các file .ui thành file .py
Sử dụng phương pháp không dùng subprocess
"""
import os
import sys
import re
from pathlib import Path
from PyQt5 import uic

def fix_ui_file(ui_path, output_path=None):
    """Sửa file UI trước khi chuyển đổi"""
    temp_path = ui_path
    if output_path:
        temp_path = output_path
    
    with open(ui_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Sửa lỗi Qt::Orientation::Horizontal
    content = content.replace('Qt::Orientation::Horizontal', 'Horizontal')
    content = content.replace('Qt::Orientation::Vertical', 'Vertical')
    
    with open(temp_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Đã sửa file UI {ui_path}")
    return temp_path

def convert_ui_to_py(ui_dir, py_dir):
    """Chuyển đổi tất cả file .ui trong thư mục thành .py"""
    # Đảm bảo thư mục đích tồn tại
    Path(py_dir).mkdir(parents=True, exist_ok=True)
    
    for filename in os.listdir(ui_dir):
        if not filename.endswith('.ui'):
            continue
        
        ui_path = os.path.join(ui_dir, filename)
        py_filename = f"ui_{filename[:-3]}.py"
        py_path = os.path.join(py_dir, py_filename)
        
        print(f"Đang chuyển đổi {ui_path} -> {py_path}")
        
        # Sửa file UI trước khi chuyển đổi
        fixed_ui_path = fix_ui_file(ui_path)
        
        # Chuyển đổi UI sang Python trực tiếp không qua subprocess
        try:
            # Mở file Python để ghi
            with open(py_path, 'w', encoding='utf-8') as pyfile:
                # Sử dụng uic.compileUi để chuyển đổi
                uic.compileUi(fixed_ui_path, pyfile)
            
            print(f"Đã tạo file {py_path}")
            
        except Exception as e:
            print(f"Lỗi khi chuyển đổi {ui_path}: {str(e)}")

def manual_pyuic_conversion(ui_dir, py_dir):
    """Phương pháp thay thế sử dụng lệnh pyuic5 trực tiếp"""
    # Đảm bảo thư mục đích tồn tại
    Path(py_dir).mkdir(parents=True, exist_ok=True)
    
    for filename in os.listdir(ui_dir):
        if not filename.endswith('.ui'):
            continue
        
        ui_path = os.path.join(ui_dir, filename)
        py_filename = f"ui_{filename[:-3]}.py"
        py_path = os.path.join(py_dir, py_filename)
        
        print(f"Đang chuyển đổi {ui_path} -> {py_path}")
        
        # Sửa file UI trước khi chuyển đổi
        fixed_ui_path = fix_ui_file(ui_path)
        
        # Sử dụng lệnh pyuic5 trực tiếp (thông qua terminal)
        try:
            # Tạo lệnh pyuic5
            command = f"pyuic5 {fixed_ui_path} -o {py_path}"
            print(f"Thực thi lệnh: {command}")
            
            # Thực thi lệnh
            result = os.system(command)
            
            if result == 0:
                print(f"Đã tạo file {py_path}")
            else:
                print(f"Lỗi khi thực thi lệnh: {command}")
                print("Đang thử phương pháp thay thế...")
                # Thử phương pháp thay thế
                convert_ui_file_direct(fixed_ui_path, py_path)
        except Exception as e:
            print(f"Lỗi khi chuyển đổi {ui_path}: {str(e)}")
            print("Đang thử phương pháp thay thế...")
            # Thử phương pháp thay thế
            convert_ui_file_direct(fixed_ui_path, py_path)

def convert_ui_file_direct(ui_path, py_path):
    """Chuyển đổi một file UI sang Python trực tiếp bằng API PyQt5"""
    try:
        with open(py_path, 'w', encoding='utf-8') as f:
            uic.compileUi(ui_path, f)
        print(f"Đã tạo file {py_path} bằng phương pháp trực tiếp")
    except Exception as e:
        print(f"Lỗi khi chuyển đổi trực tiếp {ui_path}: {str(e)}")

if __name__ == "__main__":
    ui_directory = "src/ui/qt_designer/main_tab"
    py_output_directory = "src/ui/generated"
    
    # Cho phép người dùng chỉ định thư mục qua tham số dòng lệnh
    if len(sys.argv) > 2:
        ui_directory = sys.argv[1]
        py_output_directory = sys.argv[2]
    
    print("Sử dụng phương pháp chuyển đổi trực tiếp...")
    convert_ui_to_py(ui_directory, py_output_directory)
    
    # Nếu phương pháp trực tiếp không hoạt động, bạn có thể thử:
    # print("Sử dụng phương pháp thay thế với lệnh pyuic5...")
    # manual_pyuic_conversion(ui_directory, py_output_directory)
    
    print("Hoàn tất chuyển đổi UI sang Python!")