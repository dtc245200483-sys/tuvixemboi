# -*- coding: utf-8 -*-
"""
KHAI TÂM HUYỀN HỌC - TỬ VI & XEM BÓI AI
File khởi chạy nhanh: Tự động mở toàn bộ ứng dụng Backend, Frontend và Trình duyệt Web
"""
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import run_app

if __name__ == "__main__":
    run_app.main()

