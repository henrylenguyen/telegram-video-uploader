"""
Cài đặt ứng dụng Telegram Video Uploader
"""
from setuptools import setup, find_packages
import os

# Đọc các thư viện từ file requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    # Loại bỏ các comment
    requirements = [r for r in requirements if not r.startswith('#')]

# Đọc README.md làm description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="telegram-video-uploader",
    version="1.0.0",
    author="Telegram Video Uploader Team",
    author_email="example@email.com",
    description="Ứng dụng tự động tải video lên Telegram",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/telegram-video-uploader",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'telegram-uploader=src.telegram_uploader:main',
            'telegram-config=src.telegram_uploader:config_main',
        ],
    },
    include_package_data=True,
    package_data={
        'src': ['icon.ico'],
    },
)