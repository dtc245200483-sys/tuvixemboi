# -*- coding: utf-8 -*-
"""
Hằng số thiên văn, bảng tra 10 Thiên Can, 12 Địa Chi và 24 Tiết Khí
chuẩn cho hệ thống Lịch Vạn Niên và Tử Vi Việt Nam (Múi giờ GMT+7).
"""

import math

# 10 Thiên Can
THIEN_CAN = [
    "Giáp", "Ất", "Bính", "Đinh", "Mậu",
    "Kỷ", "Canh", "Tân", "Nhâm", "Quý"
]

# 12 Địa Chi
DIA_CHI = [
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
    "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"
]

# 12 Canh Giờ trong ngày (mỗi canh 2 tiếng đồng hồ hiện đại)
# Giờ Tý bắt đầu từ 23h đêm đến 0h59
CANH_GIO_CHI = [
    {"chi": "Tý", "start_hour": 23, "end_hour": 1, "description": "23h00 - 0h59"},
    {"chi": "Sửu", "start_hour": 1, "end_hour": 3, "description": "1h00 - 2h59"},
    {"chi": "Dần", "start_hour": 3, "end_hour": 5, "description": "3h00 - 4h59"},
    {"chi": "Mão", "start_hour": 5, "end_hour": 7, "description": "5h00 - 6h59"},
    {"chi": "Thìn", "start_hour": 7, "end_hour": 9, "description": "7h00 - 8h59"},
    {"chi": "Tỵ", "start_hour": 9, "end_hour": 11, "description": "9h00 - 10h59"},
    {"chi": "Ngọ", "start_hour": 11, "end_hour": 13, "description": "11h00 - 12h59"},
    {"chi": "Mùi", "start_hour": 13, "end_hour": 15, "description": "13h00 - 14h59"},
    {"chi": "Thân", "start_hour": 15, "end_hour": 17, "description": "15h00 - 16h59"},
    {"chi": "Dậu", "start_hour": 17, "end_hour": 19, "description": "17h00 - 18h59"},
    {"chi": "Tuất", "start_hour": 19, "end_hour": 21, "description": "19h00 - 20h59"},
    {"chi": "Hợi", "start_hour": 21, "end_hour": 23, "description": "21h00 - 22h59"}
]

# 24 Tiết Khí trong năm
TIET_KHI = [
    "Xuân phân", "Thanh minh", "Cốc vũ", "Lập hạ", "Tiểu mãn", "Mang chủng",
    "Hạ chí", "Tiểu thử", "Đại thử", "Lập thu", "Xử thử", "Bạch lộ",
    "Thu phân", "Hàn lộ", "Sương giáng", "Lập đông", "Tiểu tuyết", "Đại tuyết",
    "Đông chí", "Tiểu hàn", "Đại hàn", "Lập xuân", "Vũ thủy", "Kinh trập"
]

# Hằng số mốc tính toán thiên văn (Epoch 2000-01-01 12h UT = JDN 2451550.09765)
EPOCH_2000 = 2451550.09765
SYNODIC_MONTH = 29.530588853  # Độ dài trung bình của 1 tháng giao hội (tuần trăng)
PI = math.pi
DR = math.pi / 180.0
