# -*- coding: utf-8 -*-
"""
Định nghĩa 12 Cung chức năng và 12 Cung Địa Chi trên Địa Bàn lá số Tử Vi.
"""

# Danh sách 12 Cung chức năng theo chiều nghịch Địa Chi chuẩn cổ thư (từ Mệnh -> Huynh Đệ -> Phu Thê...)
# Đi theo chiều nghịch (ngược chiều kim đồng hồ từ Mệnh):
CUNG_CHUC_NANG = [
    "Mệnh",        # 0: Mệnh (Bản cung)
    "Huynh Đệ",    # 1: Huynh Đệ (nghịch 1 cung - đối Nô Bộc, tam hợp Huynh - Điền - Tật)
    "Phu Thê",     # 2: Phu Thê (nghịch 2 cung - đối Quan Lộc, tam hợp Phúc - Phối - Di)
    "Tử Tức",      # 3: Tử Tức (nghịch 3 cung - đối Điền Trạch, tam hợp Phụ - Tử - Nô)
    "Tài Bạch",    # 4: Tài Bạch (nghịch 4 cung - đối Phúc Đức, tam hợp Mệnh - Tài - Quan)
    "Tật Ách",     # 5: Tật Ách (nghịch 5 cung - đối Phụ Mẫu, tam hợp Huynh - Điền - Tật)
    "Thiên Di",    # 6: Thiên Di (nghịch 6 cung - đối Mệnh, tam hợp Phúc - Phối - Di)
    "Nô Bộc",      # 7: Nô Bộc (nghịch 7 cung - đối Huynh Đệ, tam hợp Phụ - Tử - Nô)
    "Quan Lộc",    # 8: Quan Lộc (nghịch 8 cung - đối Phu Thê, tam hợp Mệnh - Tài - Quan)
    "Điền Trạch",  # 9: Điền Trạch (nghịch 9 cung - đối Tử Tức, tam hợp Huynh - Điền - Tật)
    "Phúc Đức",    # 10: Phúc Đức (nghịch 10 cung - đối Tài Bạch, tam hợp Phúc - Phối - Di)
    "Phụ Mẫu"      # 11: Phụ Mẫu (nghịch 11 cung - đối Tật Ách, tam hợp Phụ - Tử - Nô)
]

# 12 Cung Địa Chi cố định trên Địa Bàn (0: Tý, 1: Sửu, 2: Dần, ..., 11: Hợi)
CUNG_DIA_CHI = [
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
    "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"
]

# Tên Cục tương ứng với ngũ hành và số Cục
CUC_INFO = {
    2: {"ten": "Thủy Nhị Cục", "ngu_hanh": "Thủy", "so_cuc": 2},
    3: {"ten": "Mộc Tam Cục", "ngu_hanh": "Mộc", "so_cuc": 3},
    4: {"ten": "Kim Tứ Cục", "ngu_hanh": "Kim", "so_cuc": 4},
    5: {"ten": "Thổ Ngũ Cục", "ngu_hanh": "Thổ", "so_cuc": 5},
    6: {"ten": "Hỏa Lục Cục", "ngu_hanh": "Hỏa", "so_cuc": 6},
}

# 60 Hoa Giáp Nạp Âm
NAP_AM_60_HOA_GIAP = {
    "Giáp Tý": "Hải Trung Kim", "Ất Sửu": "Hải Trung Kim",
    "Bính Dần": "Lư Trung Hỏa", "Đinh Mão": "Lư Trung Hỏa",
    "Mậu Thìn": "Đại Lâm Mộc", "Kỷ Tỵ": "Đại Lâm Mộc",
    "Canh Ngọ": "Lộ Bàng Thổ", "Tân Mùi": "Lộ Bàng Thổ",
    "Nhâm Thân": "Kiếm Phong Kim", "Quý Dậu": "Kiếm Phong Kim",
    "Giáp Tuất": "Sơn Đầu Hỏa", "Ất Hợi": "Sơn Đầu Hỏa",
    "Bính Tý": "Giản Hạ Thủy", "Đinh Sửu": "Giản Hạ Thủy",
    "Mậu Dần": "Thành Đầu Thổ", "Kỷ Mão": "Thành Đầu Thổ",
    "Canh Thìn": "Bạch Lạp Kim", "Tân Tỵ": "Bạch Lạp Kim",
    "Nhâm Ngọ": "Dương Liễu Mộc", "Quý Mùi": "Dương Liễu Mộc",
    "Giáp Thân": "Tuyền Trung Thủy", "Ất Dậu": "Tuyền Trung Thủy",
    "Bính Tuất": "Ốc Thượng Thổ", "Đinh Hợi": "Ốc Thượng Thổ",
    "Mậu Tý": "Tích Lịch Hỏa", "Kỷ Sửu": "Tích Lịch Hỏa",
    "Canh Dần": "Tùng Bách Mộc", "Tân Mão": "Tùng Bách Mộc",
    "Nhâm Thìn": "Trường Lưu Thủy", "Quý Tỵ": "Trường Lưu Thủy",
    "Giáp Ngọ": "Sa Trung Kim", "Ất Mùi": "Sa Trung Kim",
    "Bính Thân": "Sơn Hạ Hỏa", "Đinh Dậu": "Sơn Hạ Hỏa",
    "Mậu Tuất": "Bình Địa Mộc", "Kỷ Hợi": "Bình Địa Mộc",
    "Canh Tý": "Bích Thượng Thổ", "Tân Sửu": "Bích Thượng Thổ",
    "Nhâm Dần": "Kim Bạch Kim", "Quý Mão": "Kim Bạch Kim",
    "Giáp Thìn": "Phúc Đăng Hỏa", "Ất Tỵ": "Phúc Đăng Hỏa",
    "Bính Ngọ": "Thiên Hà Thủy", "Đinh Mùi": "Thiên Hà Thủy",
    "Mậu Thân": "Đại Trạch Thổ", "Kỷ Dậu": "Đại Trạch Thổ",
    "Canh Tuất": "Thoa Xuyến Kim", "Tân Hợi": "Thoa Xuyến Kim",
    "Nhâm Tý": "Tang Đố Mộc", "Quý Sửu": "Tang Đố Mộc",
    "Giáp Dần": "Đại Khê Thủy", "Ất Mão": "Đại Khê Thủy",
    "Bính Thìn": "Sa Trung Thổ", "Đinh Tỵ": "Sa Trung Thổ",
    "Mậu Ngọ": "Thiên Thượng Hỏa", "Kỷ Mùi": "Thiên Thượng Hỏa",
    "Canh Thân": "Thạch Lựu Mộc", "Tân Dậu": "Thạch Lựu Mộc",
    "Nhâm Tuất": "Đại Hải Thủy", "Quý Hợi": "Đại Hải Thủy"
}
