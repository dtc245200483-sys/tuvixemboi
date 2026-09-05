# -*- coding: utf-8 -*-
"""
Quy luật tương sinh, tương khắc và trợ lực Ngũ Hành trong Tứ Trụ Bát Tự.
Định nghĩa riêng biệt, tuyệt đối không dùng chung với Tử Vi.
"""

DANH_SACH_NGU_HANH = ["Kim", "Thủy", "Mộc", "Hỏa", "Thổ"]

# Mối quan hệ Tương Sinh: A sinh B
TUONG_SINH = {
    "Kim": "Thủy",   # Kim sinh Thủy
    "Thủy": "Mộc",   # Thủy sinh Mộc
    "Mộc": "Hỏa",    # Mộc sinh Hỏa
    "Hỏa": "Thổ",    # Hỏa sinh Thổ
    "Thổ": "Kim"     # Thổ sinh Kim
}

# Mối quan hệ Mẹ Sinh Con (Ai sinh ra hành này) - Ấn Tinh
HANH_SINH_RA = {
    "Thủy": "Kim",   # Kim sinh Thủy
    "Mộc": "Thủy",   # Thủy sinh Mộc
    "Hỏa": "Mộc",    # Mộc sinh Hỏa
    "Thổ": "Hỏa",    # Hỏa sinh Thổ
    "Kim": "Thổ"     # Thổ sinh Kim
}

# Mối quan hệ Tương Khắc: A khắc B
TUONG_KHAC = {
    "Kim": "Mộc",    # Kim khắc Mộc
    "Mộc": "Thổ",    # Mộc khắc Thổ
    "Thổ": "Thủy",   # Thổ khắc Thủy
    "Thủy": "Hỏa",   # Thủy khắc Hỏa
    "Hỏa": "Kim"     # Hỏa khắc Kim
}

# Mối quan hệ Bị Khắc: Ai khắc hành này - Quan Sát
HANH_KHAC_NO = {
    "Mộc": "Kim",
    "Thổ": "Mộc",
    "Thủy": "Thổ",
    "Hỏa": "Thủy",
    "Kim": "Hỏa"
}
