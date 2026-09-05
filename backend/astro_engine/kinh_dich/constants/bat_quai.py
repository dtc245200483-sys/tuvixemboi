# -*- coding: utf-8 -*-
"""
8 Quái đơn (Bát Quái / Trigrams): Càn, Đoài, Ly, Chấn, Tốn, Khảm, Cấn, Khôn.
Mỗi quái gồm 3 hào (Âm: 0, Dương: 1) tính từ dưới lên trên (hào 1 đến hào 3).
Đánh số theo Tiên Thiên Bát Quái (Chuẩn Mai Hoa Dịch Số - Thiệu Ung).
"""

BAT_QUAI = {
    1: {
        "so_tien_thien": 1,
        "ten": "Càn",
        "ten_chu_han": "乾",
        "tuong": "Trời (Thiên)",
        "ngu_hanh": "Kim",
        "ma_nhi_phan": "111",
        "hao": [1, 1, 1],
        "mo_ta": "Thuần Dương, cương kiện, khởi đầu"
    },
    2: {
        "so_tien_thien": 2,
        "ten": "Đoài",
        "ten_chu_han": "兌",
        "tuong": "Đầm (Trạch)",
        "ngu_hanh": "Kim",
        "ma_nhi_phan": "110",
        "hao": [1, 1, 0],
        "mo_ta": "Vui vẻ, hòa duyệt, khẩu thiệt"
    },
    3: {
        "so_tien_thien": 3,
        "ten": "Ly",
        "ten_chu_han": "離",
        "tuong": "Lửa (Hỏa)",
        "ngu_hanh": "Hỏa",
        "ma_nhi_phan": "101",
        "hao": [1, 0, 1],
        "mo_ta": "Sáng sủa, bám víu, văn minh"
    },
    4: {
        "so_tien_thien": 4,
        "ten": "Chấn",
        "ten_chu_han": "震",
        "tuong": "Sấm (Lôi)",
        "ngu_hanh": "Mộc",
        "ma_nhi_phan": "100",
        "hao": [1, 0, 0],
        "mo_ta": "Chấn động, khởi phát, hành động"
    },
    5: {
        "so_tien_thien": 5,
        "ten": "Tốn",
        "ten_chu_han": "巽",
        "tuong": "Gió (Phong)",
        "ngu_hanh": "Mộc",
        "ma_nhi_phan": "011",
        "hao": [0, 1, 1],
        "mo_ta": "Thuận nhập, uyển chuyển, thâm nhập"
    },
    6: {
        "so_tien_thien": 6,
        "ten": "Khảm",
        "ten_chu_han": "坎",
        "tuong": "Nước (Thủy)",
        "ngu_hanh": "Thủy",
        "ma_nhi_phan": "010",
        "hao": [0, 1, 0],
        "mo_ta": "Hiểm trở, trắc trở, trí tuệ thâm sâu"
    },
    7: {
        "so_tien_thien": 7,
        "ten": "Cấn",
        "ten_chu_han": "艮",
        "tuong": "Núi (Sơn)",
        "ngu_hanh": "Thổ",
        "ma_nhi_phan": "001",
        "hao": [0, 0, 1],
        "mo_ta": "Dừng lại, tĩnh lặng, vững vàng"
    },
    8: {
        "so_tien_thien": 8,
        "ten": "Khôn",
        "ten_chu_han": "坤",
        "tuong": "Đất (Địa)",
        "ngu_hanh": "Thổ",
        "ma_nhi_phan": "000",
        "hao": [0, 0, 0],
        "mo_ta": "Thuần Âm, nhu thuận, bao dung, nuôi dưỡng"
    }
}

BAT_QUAI_BY_NAME = {q["ten"]: q for q in BAT_QUAI.values()}
BAT_QUAI_BY_CODE = {q["ma_nhi_phan"]: q for q in BAT_QUAI.values()}
