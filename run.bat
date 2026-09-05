@echo off
title Khai Tam Huyen Hoc - Tu Vi & Xem Boi AI
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================================================
echo       KHAI TÂM HUYỀN HỌC — TỬ VI & XEM BÓI TRÍ TUỆ NHÂN TẠO
echo ========================================================================
echo Đang khởi động hệ thống và mở trình duyệt web...
python run/run_app.py
pause
