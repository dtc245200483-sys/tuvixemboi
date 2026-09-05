# -*- coding: utf-8 -*-
"""
Bảng ánh xạ 64 quẻ kép (Lục Thập Tứ Quái) trong Kinh Dịch theo thứ tự Văn Vương (1-64).
Mỗi quẻ gồm: số thứ tự, tên quẻ, mã nhị phân (6 ký tự từ hào 1 đến hào 6),
quái trên (thượng quái), quái dưới (hạ quái).
CHỈ lưu thông tin định danh và cấu trúc toán học — KHÔNG lưu thoán từ/hào từ (được lưu tại Knowledge Base).
"""

from astro_engine.kinh_dich.constants.bat_quai import BAT_QUAI_BY_NAME

# Danh sách 64 quẻ theo thứ tự Văn Vương
# Cấu trúc mỗi phần tử: (so_thu_tu, ten_que, quai_tren, quai_duoi)
RAW_64_QUE = [
    (1, "Càn vi Thiên", "Càn", "Càn"),
    (2, "Khôn vi Địa", "Khôn", "Khôn"),
    (3, "Thủy Lôi Truân", "Khảm", "Chấn"),
    (4, "Sơn Thủy Mông", "Cấn", "Khảm"),
    (5, "Thủy Thiên Nhu", "Khảm", "Càn"),
    (6, "Thiên Thủy Tụng", "Càn", "Khảm"),
    (7, "Địa Thủy Sư", "Khôn", "Khảm"),
    (8, "Thủy Địa Tỷ", "Khảm", "Khôn"),
    (9, "Phong Thiên Tiểu Súc", "Tốn", "Càn"),
    (10, "Thiên Trạch Lý", "Càn", "Đoài"),
    (11, "Địa Thiên Thái", "Khôn", "Càn"),
    (12, "Thiên Địa Bĩ", "Càn", "Khôn"),
    (13, "Thiên Hỏa Đồng Nhân", "Càn", "Ly"),
    (14, "Hỏa Thiên Đại Hữu", "Ly", "Càn"),
    (15, "Địa Sơn Khiêm", "Khôn", "Cấn"),
    (16, "Lôi Địa Dự", "Chấn", "Khôn"),
    (17, "Trạch Lôi Tùy", "Đoài", "Chấn"),
    (18, "Sơn Phong Cổ", "Cấn", "Tốn"),
    (19, "Địa Trạch Lâm", "Khôn", "Đoài"),
    (20, "Phong Địa Quan", "Tốn", "Khôn"),
    (21, "Hỏa Lôi Phệ Hạp", "Ly", "Chấn"),
    (22, "Sơn Hỏa Bí", "Cấn", "Ly"),
    (23, "Sơn Địa Bác", "Cấn", "Khôn"),
    (24, "Địa Lôi Phục", "Khôn", "Chấn"),
    (25, "Thiên Lôi Vô Vọng", "Càn", "Chấn"),
    (26, "Sơn Thiên Đại Súc", "Cấn", "Càn"),
    (27, "Sơn Lôi Di", "Cấn", "Chấn"),
    (28, "Trạch Phong Đại Quá", "Đoài", "Tốn"),
    (29, "Khảm vi Thủy", "Khảm", "Khảm"),
    (30, "Ly vi Hỏa", "Ly", "Ly"),
    (31, "Trạch Sơn Hàm", "Đoài", "Cấn"),
    (32, "Lôi Phong Hằng", "Chấn", "Tốn"),
    (33, "Thiên Sơn Độn", "Càn", "Cấn"),
    (34, "Lôi Thiên Đại Tráng", "Chấn", "Càn"),
    (35, "Hỏa Địa Tấn", "Ly", "Khôn"),
    (36, "Địa Hỏa Minh Di", "Khôn", "Ly"),
    (37, "Phong Hỏa Gia Nhân", "Tốn", "Ly"),
    (38, "Hỏa Trạch Khuê", "Ly", "Đoài"),
    (39, "Thủy Sơn Kiển", "Khảm", "Cấn"),
    (40, "Lôi Thủy Giải", "Chấn", "Khảm"),
    (41, "Sơn Trạch Tổn", "Cấn", "Đoài"),
    (42, "Phong Lôi Ích", "Tốn", "Chấn"),
    (43, "Trạch Thiên Quải", "Đoài", "Càn"),
    (44, "Thiên Phong Cấu", "Càn", "Tốn"),
    (45, "Trạch Địa Tụy", "Đoài", "Khôn"),
    (46, "Địa Phong Thăng", "Khôn", "Tốn"),
    (47, "Trạch Thủy Khốn", "Đoài", "Khảm"),
    (48, "Thủy Phong Tỉnh", "Khảm", "Tốn"),
    (49, "Trạch Hỏa Cách", "Đoài", "Ly"),
    (50, "Hỏa Phong Đỉnh", "Ly", "Tốn"),
    (51, "Bát Thuần Chấn", "Chấn", "Chấn"),
    (52, "Bát Thuần Cấn", "Cấn", "Cấn"),
    (53, "Phong Sơn Tiệm", "Tốn", "Cấn"),
    (54, "Lôi Trạch Quy Muội", "Chấn", "Đoài"),
    (55, "Lôi Hỏa Phong", "Chấn", "Ly"),
    (56, "Hỏa Sơn Lữ", "Ly", "Cấn"),
    (57, "Bát Thuần Tốn", "Tốn", "Tốn"),
    (58, "Bát Thuần Đoài", "Đoài", "Đoài"),
    (59, "Phong Thủy Hoán", "Tốn", "Khảm"),
    (60, "Thủy Trạch Tiết", "Khảm", "Đoài"),
    (61, "Phong Trạch Trung Phu", "Tốn", "Đoài"),
    (62, "Lôi Sơn Tiểu Quá", "Chấn", "Cấn"),
    (63, "Thủy Hỏa Ký Tế", "Khảm", "Ly"),
    (64, "Hỏa Thủy Vị Tế", "Ly", "Khảm")
]

QUE_64 = []
QUE_BY_CODE = {}
QUE_BY_STT = {}

for stt, ten, up_name, low_name in RAW_64_QUE:
    up_code = BAT_QUAI_BY_NAME[up_name]["ma_nhi_phan"]
    low_code = BAT_QUAI_BY_NAME[low_name]["ma_nhi_phan"]
    # Mã nhị phân gồm 6 hào từ hào 1 (dưới cùng) đến hào 6 (trên cùng)
    hex_code = low_code + up_code
    item = {
        "so_thu_tu": stt,
        "ten_que": ten,
        "ma_nhi_phan": hex_code,
        "quai_tren": up_name,
        "quai_duoi": low_name
    }
    QUE_64.append(item)
    QUE_BY_CODE[hex_code] = item
    QUE_BY_STT[stt] = item
