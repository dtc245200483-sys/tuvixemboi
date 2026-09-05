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

DIA_CHI = [
    {
        "ten": "Tý", "ngu_hanh": "Thủy", "am_duong": "Dương", "idx": 0,
        "chi_tang": ["Quý"], "mo_ta": "Chính khí Quý Thủy"
    },
    {
        "ten": "Sửu", "ngu_hanh": "Thổ", "am_duong": "Âm", "idx": 1,
        "chi_tang": ["Kỷ", "Quý", "Tân"], "mo_ta": "Kỷ Thổ bản khí, Quý Thủy dư khí, Tân Kim mộ khí"
    },
    {
        "ten": "Dần", "ngu_hanh": "Mộc", "am_duong": "Dương", "idx": 2,
        "chi_tang": ["Giáp", "Bính", "Mậu"], "mo_ta": "Giáp Mộc bản khí, Bính Hỏa trường sinh, Mậu Thổ trường sinh"
    },
    {
        "ten": "Mão", "ngu_hanh": "Mộc", "am_duong": "Âm", "idx": 3,
        "chi_tang": ["Ất"], "mo_ta": "Chính khí Ất Mộc"
    },
    {
        "ten": "Thìn", "ngu_hanh": "Thổ", "am_duong": "Dương", "idx": 4,
        "chi_tang": ["Mậu", "Ất", "Quý"], "mo_ta": "Mậu Thổ bản khí, Ất Mộc dư khí, Quý Thủy mộ khí"
    },
    {
        "ten": "Tỵ", "ngu_hanh": "Hỏa", "am_duong": "Âm", "idx": 5,
        "chi_tang": ["Bính", "Mậu", "Canh"], "mo_ta": "Bính Hỏa bản khí, Mậu Thổ trường sinh, Canh Kim trường sinh"
    },
    {
        "ten": "Ngọ", "ngu_hanh": "Hỏa", "am_duong": "Dương", "idx": 6,
        "chi_tang": ["Đinh", "Kỷ"], "mo_ta": "Đinh Hỏa bản khí, Kỷ Thổ lộc"
    },
    {
        "ten": "Mùi", "ngu_hanh": "Thổ", "am_duong": "Âm", "idx": 7,
        "chi_tang": ["Kỷ", "Đinh", "Ất"], "mo_ta": "Kỷ Thổ bản khí, Đinh Hỏa dư khí, Ất Mộc mộ khí"
    },
    {
        "ten": "Thân", "ngu_hanh": "Kim", "am_duong": "Dương", "idx": 8,
        "chi_tang": ["Canh", "Nhâm", "Mậu"], "mo_ta": "Canh Kim bản khí, Nhâm Thủy trường sinh, Mậu Thổ trường sinh"
    },
    {
        "ten": "Dậu", "ngu_hanh": "Kim", "am_duong": "Âm", "idx": 9,
        "chi_tang": ["Tân"], "mo_ta": "Chính khí Tân Kim"
    },
    {
        "ten": "Tuất", "ngu_hanh": "Thổ", "am_duong": "Dương", "idx": 10,
        "chi_tang": ["Mậu", "Tân", "Đinh"], "mo_ta": "Mậu Thổ bản khí, Tân Kim dư khí, Đinh Hỏa mộ khí"
    },
    {
        "ten": "Hợi", "ngu_hanh": "Thủy", "am_duong": "Âm", "idx": 11,
        "chi_tang": ["Nhâm", "Giáp"], "mo_ta": "Nhâm Thủy bản khí, Giáp Mộc trường sinh"
    }
]

CHI_NAMES = [c["ten"] for c in DIA_CHI]
CHI_DICT = {c["ten"]: c for c in DIA_CHI}
