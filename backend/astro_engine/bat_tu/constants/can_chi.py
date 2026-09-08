# -*- coding: utf-8 -*-
"""
Hằng số 10 Thiên Can và 12 Địa Chi cùng Ngũ Hành, Âm Dương và Địa Chi Tàng Can
dành riêng cho module Bát Tự (Tứ Trụ).
Độc lập hoàn toàn với module Tử Vi.
"""

THIEN_CAN = [
    {"ten": "Giáp", "ngu_hanh": "Mộc", "am_duong": "Dương", "idx": 0},
    {"ten": "Ất", "ngu_hanh": "Mộc", "am_duong": "Âm", "idx": 1},
    {"ten": "Bính", "ngu_hanh": "Hỏa", "am_duong": "Dương", "idx": 2},
    {"ten": "Đinh", "ngu_hanh": "Hỏa", "am_duong": "Âm", "idx": 3},
    {"ten": "Mậu", "ngu_hanh": "Thổ", "am_duong": "Dương", "idx": 4},
    {"ten": "Kỷ", "ngu_hanh": "Thổ", "am_duong": "Âm", "idx": 5},
    {"ten": "Canh", "ngu_hanh": "Kim", "am_duong": "Dương", "idx": 6},
    {"ten": "Tân", "ngu_hanh": "Kim", "am_duong": "Âm", "idx": 7},
    {"ten": "Nhâm", "ngu_hanh": "Thủy", "am_duong": "Dương", "idx": 8},
    {"ten": "Quý", "ngu_hanh": "Thủy", "am_duong": "Âm", "idx": 9}
]

CAN_NAMES = [c["ten"] for c in THIEN_CAN]
CAN_DICT = {c["ten"]: c for c in THIEN_CAN}

# ==============================================================================
# BẢNG GỐC DUY NHẤT: ĐỊA CHI TÀNG ĐỘN (SÁCH 'DỰ BÁO THEO TỬ BÌNH' - TRẦN KHANG NINH, TRANG 30)
# Toàn bộ hệ thống lấy bảng này làm Single Source of Truth duy nhất cho tàng can.
# ==============================================================================
BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH = {
    "Tý": ["Quý"],
    "Sửu": ["Kỷ", "Tân", "Quý"],
    "Dần": ["Giáp", "Bính", "Mậu"],
    "Mão": ["Ất"],
    "Thìn": ["Mậu", "Quý", "Ất"],
    "Tỵ": ["Bính", "Canh", "Mậu"],
    "Ngọ": ["Đinh", "Kỷ"],
    "Mùi": ["Kỷ", "Ất", "Đinh"],
    "Thân": ["Canh", "Nhâm", "Mậu"],
    "Dậu": ["Tân"],
    "Tuất": ["Mậu", "Đinh", "Tân"],
    "Hợi": ["Nhâm", "Giáp"],
}

# ==============================================================================
# BẢNG TRA CỨU THẬP THẦN CỐ ĐỊNH 10x10 (TRẦN KHANG NINH, TRANG 31)
# 10 Nhật Can (Hàng) x 10 Can Đang Xét (Cột) -> Đúng 1 trong 10 Thập Thần chuẩn
# Tuyệt đối không sinh nhãn tự do. 10 tên chuẩn:
# Tỷ Kiên, Kiếp Tài, Thực Thần, Thương Quan, Chính Tài, Thiên Tài, Chính Quan, Thất Sát, Chính Ấn, Thiên Ấn
# ==============================================================================
DANH_SACH_10_THAP_THAN_CHUAN = [
    "Tỷ Kiên", "Kiếp Tài",
    "Thực Thần", "Thương Quan",
    "Chính Tài", "Thiên Tài",
    "Chính Quan", "Thất Sát",
    "Chính Ấn", "Thiên Ấn"
]

BANG_TRA_CUU_THAP_THAN_10X10 = {
    # 1. Nhật Can Giáp (Mộc Dương)
    "Giáp": {
        "Giáp": "Tỷ Kiên", "Ất": "Kiếp Tài",
        "Bính": "Thực Thần", "Đinh": "Thương Quan",
        "Mậu": "Thiên Tài", "Kỷ": "Chính Tài",
        "Canh": "Thất Sát", "Tân": "Chính Quan",
        "Nhâm": "Thiên Ấn", "Quý": "Chính Ấn"
    },
    # 2. Nhật Can Ất (Mộc Âm)
    "Ất": {
        "Giáp": "Kiếp Tài", "Ất": "Tỷ Kiên",
        "Bính": "Thương Quan", "Đinh": "Thực Thần",
        "Mậu": "Chính Tài", "Kỷ": "Thiên Tài",
        "Canh": "Chính Quan", "Tân": "Thất Sát",
        "Nhâm": "Chính Ấn", "Quý": "Thiên Ấn"
    },
    # 3. Nhật Can Bính (Hỏa Dương)
    "Bính": {
        "Giáp": "Thiên Ấn", "Ất": "Chính Ấn",
        "Bính": "Tỷ Kiên", "Đinh": "Kiếp Tài",
        "Mậu": "Thực Thần", "Kỷ": "Thương Quan",
        "Canh": "Thiên Tài", "Tân": "Chính Tài",
        "Nhâm": "Thất Sát", "Quý": "Chính Quan"
    },
    # 4. Nhật Can Đinh (Hỏa Âm)
    "Đinh": {
        "Giáp": "Chính Ấn", "Ất": "Thiên Ấn",
        "Bính": "Kiếp Tài", "Đinh": "Tỷ Kiên",
        "Mậu": "Thương Quan", "Kỷ": "Thực Thần",
        "Canh": "Chính Tài", "Tân": "Thiên Tài",
        "Nhâm": "Chính Quan", "Quý": "Thất Sát"
    },
    # 5. Nhật Can Mậu (Thổ Dương)
    "Mậu": {
        "Giáp": "Thất Sát", "Ất": "Chính Quan",
        "Bính": "Thiên Ấn", "Đinh": "Chính Ấn",
        "Mậu": "Tỷ Kiên", "Kỷ": "Kiếp Tài",
        "Canh": "Thực Thần", "Tân": "Thương Quan",
        "Nhâm": "Thiên Tài", "Quý": "Chính Tài"
    },
    # 6. Nhật Can Kỷ (Thổ Âm)
    "Kỷ": {
        "Giáp": "Chính Quan", "Ất": "Thất Sát",
        "Bính": "Chính Ấn", "Đinh": "Thiên Ấn",
        "Mậu": "Kiếp Tài", "Kỷ": "Tỷ Kiên",
        "Canh": "Thương Quan", "Tân": "Thực Thần",
        "Nhâm": "Chính Tài", "Quý": "Thiên Tài"
    },
    # 7. Nhật Can Canh (Kim Dương)
    "Canh": {
        "Giáp": "Thiên Tài", "Ất": "Chính Tài",
        "Bính": "Thất Sát", "Đinh": "Chính Quan",
        "Mậu": "Thiên Ấn", "Kỷ": "Chính Ấn",
        "Canh": "Tỷ Kiên", "Tân": "Kiếp Tài",
        "Nhâm": "Thực Thần", "Quý": "Thương Quan"
    },
    # 8. Nhật Can Tân (Kim Âm)
    "Tân": {
        "Giáp": "Chính Tài", "Ất": "Thiên Tài",
        "Bính": "Chính Quan", "Đinh": "Thất Sát",
        "Mậu": "Chính Ấn", "Kỷ": "Thiên Ấn",
        "Canh": "Kiếp Tài", "Tân": "Tỷ Kiên",
        "Nhâm": "Thương Quan", "Quý": "Thực Thần"
    },
    # 9. Nhật Can Nhâm (Thủy Dương)
    "Nhâm": {
        "Giáp": "Thực Thần", "Ất": "Thương Quan",
        "Bính": "Thiên Tài", "Đinh": "Chính Tài",
        "Mậu": "Thất Sát", "Kỷ": "Chính Quan",
        "Canh": "Thiên Ấn", "Tân": "Chính Ấn",
        "Nhâm": "Tỷ Kiên", "Quý": "Kiếp Tài"
    },
    # 10. Nhật Can Quý (Thủy Âm)
    "Quý": {
        "Giáp": "Thương Quan", "Ất": "Thực Thần",
        "Bính": "Chính Tài", "Đinh": "Thiên Tài",
        "Mậu": "Chính Quan", "Kỷ": "Thất Sát",
        "Canh": "Chính Ấn", "Tân": "Thiên Ấn",
        "Nhâm": "Kiếp Tài", "Quý": "Tỷ Kiên"
    }
}

DIA_CHI = [
    {
        "ten": "Tý", "ngu_hanh": "Thủy", "am_duong": "Dương", "idx": 0,
        "chi_tang": BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH["Tý"], "mo_ta": "Chính khí Quý Thủy"
    },
    {
        "ten": "Sửu", "ngu_hanh": "Thổ", "am_duong": "Âm", "idx": 1,
        "chi_tang": BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH["Sửu"], "mo_ta": "Kỷ Thổ bản khí, Tân Kim trung khí, Quý Thủy dư khí"
    },
    {
        "ten": "Dần", "ngu_hanh": "Mộc", "am_duong": "Dương", "idx": 2,
        "chi_tang": BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH["Dần"], "mo_ta": "Giáp Mộc bản khí, Bính Hỏa trường sinh, Mậu Thổ trường sinh"
    },
    {
        "ten": "Mão", "ngu_hanh": "Mộc", "am_duong": "Âm", "idx": 3,
        "chi_tang": BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH["Mão"], "mo_ta": "Chính khí Ất Mộc"
    },
    {
        "ten": "Thìn", "ngu_hanh": "Thổ", "am_duong": "Dương", "idx": 4,
        "chi_tang": BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH["Thìn"], "mo_ta": "Mậu Thổ bản khí, Quý Thủy trung khí, Ất Mộc dư khí"
    },
    {
        "ten": "Tỵ", "ngu_hanh": "Hỏa", "am_duong": "Âm", "idx": 5,
        "chi_tang": BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH["Tỵ"], "mo_ta": "Bính Hỏa bản khí, Canh Kim trường sinh, Mậu Thổ trường sinh"
    },
    {
        "ten": "Ngọ", "ngu_hanh": "Hỏa", "am_duong": "Dương", "idx": 6,
        "chi_tang": BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH["Ngọ"], "mo_ta": "Đinh Hỏa bản khí, Kỷ Thổ lộc"
    },
    {
        "ten": "Mùi", "ngu_hanh": "Thổ", "am_duong": "Âm", "idx": 7,
        "chi_tang": BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH["Mùi"], "mo_ta": "Kỷ Thổ bản khí, Ất Mộc trung khí, Đinh Hỏa dư khí"
    },
    {
        "ten": "Thân", "ngu_hanh": "Kim", "am_duong": "Dương", "idx": 8,
        "chi_tang": BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH["Thân"], "mo_ta": "Canh Kim bản khí, Nhâm Thủy trường sinh, Mậu Thổ trường sinh"
    },
    {
        "ten": "Dậu", "ngu_hanh": "Kim", "am_duong": "Âm", "idx": 9,
        "chi_tang": BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH["Dậu"], "mo_ta": "Chính khí Tân Kim"
    },
    {
        "ten": "Tuất", "ngu_hanh": "Thổ", "am_duong": "Dương", "idx": 10,
        "chi_tang": BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH["Tuất"], "mo_ta": "Mậu Thổ bản khí, Đinh Hỏa trung khí, Tân Kim dư khí"
    },
    {
        "ten": "Hợi", "ngu_hanh": "Thủy", "am_duong": "Âm", "idx": 11,
        "chi_tang": BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH["Hợi"], "mo_ta": "Nhâm Thủy bản khí, Giáp Mộc trường sinh"
    }
]

CHI_NAMES = [c["ten"] for c in DIA_CHI]
CHI_DICT = {c["ten"]: c for c in DIA_CHI}

# Bảng phân nhóm Thập Thần phục vụ thẩm định Thân Mệnh & Khí Lực (Single Source of Truth)
# Căn cứ: Sách 'Dự Báo Theo Tử Bình' - Trần Khang Ninh
PHE_TRO_THAN = {"Tỷ Kiên", "Kiếp Tài", "Chính Ấn", "Thiên Ấn"}   # Dùng cho Đắc Thế (trên Thiên Can lộ)
PHE_THONG_CAN = {"Tỷ Kiên", "Kiếp Tài"}                           # Dùng riêng cho Đắc Địa (gốc rễ thông căn, KHÔNG bao gồm Ấn)
PHE_TIET_KHAC_THAN = {"Chính Tài", "Thiên Tài", "Thực Thần", "Thương Quan", "Chính Quan", "Thất Sát"}

# Bảng Lộc vị cố định 10 dòng (Trần Khang Ninh tr. 92):
# Xác lập Kiến Lộc Cách khi Nhật Chủ đắc Lộc tại đúng Chi Tháng
BANG_LOC_VI_10_CAN = {
    "Giáp": "Dần",
    "Ất": "Mão",
    "Bính": "Tỵ",
    "Đinh": "Ngọ",
    "Mậu": "Tỵ",
    "Kỷ": "Ngọ",
    "Canh": "Thân",
    "Tân": "Dậu",
    "Nhâm": "Hợi",
    "Quý": "Tý"
}

# Bảng Dương Nhận cố định 10 Can
BANG_DUONG_NHAN_10_CAN = {
    "Giáp": "Mão",
    "Ất": "Dần",
    "Bính": "Ngọ",
    "Đinh": "Tỵ",
    "Mậu": "Ngọ",
    "Kỷ": "Tỵ",
    "Canh": "Dậu",
    "Tân": "Thân",
    "Nhâm": "Tý",
    "Quý": "Hợi"
}
