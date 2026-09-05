# -*- coding: utf-8 -*-
"""
Bộ 10 Test Cases kiểm thử toàn diện Tu Vi Astro Engine
theo chuẩn khoa học và các công thức Tử Vi Đẩu Số Toàn Thư.
Nguồn đối chiếu: Tử Vi Đẩu Số Toàn Thư (Trần Đoàn), Lạc Thư Tử Vi, lasotuvi.
"""

import pytest
from astro_engine.tu_vi.core import (
    lap_la_so,
    xac_dinh_cung_menh,
    an_12_cung,
    xac_dinh_cuc,
    an_sao_tu_vi,
    an_14_chinh_tinh,
    tinh_dai_van
)
from calendar_converter.lunar_calendar import solar_to_lunar


def test_case_1_sample_chart_1():
    """
    Test 1: Lá số mẫu 1 - Nam mạng sinh ngày 15/04/1990 Âm lịch (Canh Ngọ), giờ Thìn.
    - Cung Mệnh: Sửu (index 1).
    - Can Chi cung Mệnh: Kỷ Sửu (Ngũ Hổ Độn từ Mậu Dần đếm thuận đến Sửu).
    - Cục: Hỏa Lục Cục (Hoa giáp cung Mệnh: Kỷ Sửu -> Tích Lịch Hỏa).
    - Tử Vi: cư Sửu (index 1).
    """
    ls = lap_la_so(
        ngay_sinh_am=15,
        thang_sinh_am=4,
        nam_sinh_am=1990,
        gio_sinh_chi="Thìn",
        gioi_tinh="nam"
    )
    assert ls["ten_cung_menh"] == "Sửu"
    assert ls["cuc"]["ten"] == "Hỏa Lục Cục"
    assert ls["cuc"]["so_cuc"] == 6
    assert ls["chinh_tinh_vi_tri"]["Tử Vi"] == 1


def test_case_2_sample_chart_2():
    """
    Test 2: Lá số mẫu 2 - Nam mạng sinh ngày 01/01/2024 Âm lịch (Giáp Thìn), giờ Tý.
    - Cung Mệnh: Dần (index 2).
    - Cục: Hỏa Lục Cục (Hoa giáp cung Mệnh: Bính Dần -> Lư Trung Hỏa).
    - Tử Vi: cư Dậu (index 9) -> Thái Dương + Thiên Lương tại Dậu.
    """
    ls = lap_la_so(
        ngay_sinh_am=1,
        thang_sinh_am=1,
        nam_sinh_am=2024,
        gio_sinh_chi="Tý",
        gioi_tinh="nam"
    )
    assert ls["ten_cung_menh"] == "Dần"
    assert ls["cuc"]["ten"] == "Hỏa Lục Cục"
    assert ls["cuc"]["so_cuc"] == 6
    chinh_tinh = ls["chinh_tinh_vi_tri"]
    assert chinh_tinh["Tử Vi"] == 9        # Dậu
    assert chinh_tinh["Thiên Phủ"] == 7    # Mùi


def test_case_3_sample_chart_3():
    """
    Test 3: Lá số mẫu 3 - Nữ mạng sinh ngày 06/09/2023 Âm lịch (Quý Mão), giờ Mão.
    - Cung Mệnh: Mùi (index 7).
    - Cục: Hỏa Lục Cục.
    - Tử Vi: cư Dần (index 2) -> Tử Vi - Thiên Phủ đồng cung tại Dần.
    """
    ls = lap_la_so(
        ngay_sinh_am=6,
        thang_sinh_am=9,
        nam_sinh_am=2023,
        gio_sinh_chi="Mão",
        gioi_tinh="nu"
    )
    assert ls["ten_cung_menh"] == "Mùi"
    assert ls["cuc"]["so_cuc"] == 6
    chinh_tinh = ls["chinh_tinh_vi_tri"]
    assert chinh_tinh["Tử Vi"] == 2        # Dần
    assert chinh_tinh["Thiên Phủ"] == 2    # Dần (đồng cung tại Dần)
    assert chinh_tinh["Thất Sát"] == 8     # Thân


def test_case_4_sample_chart_4():
    """
    Test 4: Lá số mẫu 4 - Nam mạng sinh ngày 15/08/1985 Âm lịch (Ất Sửu), giờ Ngọ.
    - Cung Mệnh: Mão (index 3).
    - Cục: Thổ Ngũ Cục.
    - Tử Vi: cư Thìn (index 4) -> Tử Vi - Thiên Tướng tại Thìn.
    """
    ls = lap_la_so(
        ngay_sinh_am=15,
        thang_sinh_am=8,
        nam_sinh_am=1985,
        gio_sinh_chi="Ngọ",
        gioi_tinh="nam"
    )
    assert ls["ten_cung_menh"] == "Mão"
    assert ls["cuc"]["ten"] == "Thổ Ngũ Cục"
    assert ls["chinh_tinh_vi_tri"]["Tử Vi"] == 4   # Thìn
    assert ls["chinh_tinh_vi_tri"]["Thiên Phủ"] == 0 # Tý


def test_case_5_sample_chart_5():
    """
    Test 5: Lá số mẫu 5 - Nữ mạng sinh ngày 20/11/1995 Âm lịch (Ất Hợi), giờ Dần.
    - Cung Mệnh: Tuất (index 10).
    - Cục: Thổ Ngũ Cục.
    - Tử Vi: cư Tỵ (index 5) -> Tử Vi - Thất Sát đồng cung tại Tỵ.
    """
    ls = lap_la_so(
        ngay_sinh_am=20,
        thang_sinh_am=11,
        nam_sinh_am=1995,
        gio_sinh_chi="Dần",
        gioi_tinh="nu"
    )
    assert ls["ten_cung_menh"] == "Tuất"
    assert ls["cuc"]["ten"] == "Thổ Ngũ Cục"
    assert ls["chinh_tinh_vi_tri"]["Tử Vi"] == 5    # Tỵ
    assert ls["chinh_tinh_vi_tri"]["Thất Sát"] == 5 # Tỵ (đồng cung với Tử Vi)


def test_case_6_born_at_midnight_rule_consistency():
    """
    Test 6: Case đặc biệt sinh giờ Tý (23h-1h) giao ngày.
    Xác nhận cung Mệnh và toàn bộ lá số tính theo ĐÚNG ngày âm lịch đã điều chỉnh
    từ calendar_converter (Prompt 3.1), không bị lệch 1 ngày giữa 23h30 hôm nay và 0h30 hôm sau.
    """
    # 23h30 ngày 15/05/2024 dương lịch
    cal_23h30 = solar_to_lunar(15, 5, 2024, gio=23)
    # 00h30 ngày 16/05/2024 dương lịch
    cal_00h30 = solar_to_lunar(16, 5, 2024, gio=0)

    # Cả hai cùng thuộc ngày âm lịch 09/04/2024
    assert cal_23h30["ngay_am"] == cal_00h30["ngay_am"]
    assert cal_23h30["thang_am"] == cal_00h30["thang_am"]

    # Lập lá số từ 2 thời điểm này
    ls_a = lap_la_so(
        ngay_sinh_am=cal_23h30["ngay_am"],
        thang_sinh_am=cal_23h30["thang_am"],
        nam_sinh_am=cal_23h30["nam_am"],
        gio_sinh_chi="Tý",
        gioi_tinh="nam"
    )
    ls_b = lap_la_so(
        ngay_sinh_am=cal_00h30["ngay_am"],
        thang_sinh_am=cal_00h30["thang_am"],
        nam_sinh_am=cal_00h30["nam_am"],
        gio_sinh_chi="Tý",
        gioi_tinh="nam"
    )

    assert ls_a["cung_menh_vi_tri"] == ls_b["cung_menh_vi_tri"]
    assert ls_a["cuc"]["ten"] == ls_b["cuc"]["ten"]
    assert ls_a["chinh_tinh_vi_tri"] == ls_b["chinh_tinh_vi_tri"]


def test_case_7_leap_month_chart():
    """
    Test 7: Case đặc biệt năm có tháng nhuận, sinh đúng tháng nhuận.
    Xác nhận hàm lập lá số tính toán trơn tru không phát sinh lỗi.
    Ví dụ: Tháng 2 nhuận năm Quý Mão 2023.
    """
    ls_nhuan = lap_la_so(
        ngay_sinh_am=15,
        thang_sinh_am=2,
        nam_sinh_am=2023,
        gio_sinh_chi="Ngọ",
        gioi_tinh="nu"
    )
    assert ls_nhuan["thong_tin_co_ban"]["nam_am"] == 2023
    assert len(ls_nhuan["chinh_tinh_vi_tri"]) == 14
    assert len(ls_nhuan["cac_cung"]) == 12


def test_case_8_gender_reversal_dai_van():
    """
    Test 8: So sánh 2 lá số cùng ngày/giờ/tháng sinh nhưng khác giới tính (nam/nữ).
    Xác nhận tinh_dai_van cho ra chiều thuận/nghịch khác nhau đúng quy tắc:
    - Năm Giáp Thìn (Can Dương):
      + Nam (Dương Nam): Đại Vận đi THUẬN (+1).
      + Nữ (Dương Nữ): Đại Vận đi NGHỊCH (-1).
    """
    cuc_test = {"so_cuc": 4, "ten": "Kim Tứ Cục"}
    menh_pos = 2  # Cung Dần

    dv_nam = tinh_dai_van(cuc_test, "nam", menh_pos, "Giáp Thìn")
    dv_nu = tinh_dai_van(cuc_test, "nu", menh_pos, "Giáp Thìn")

    # Đại vận đầu tiên luôn bắt đầu từ số Cục (4 tuổi) tại cung Mệnh (Dần - 2)
    assert dv_nam[0]["cung_vi_tri"] == 2
    assert dv_nu[0]["cung_vi_tri"] == 2

    # Đại vận thứ 2:
    # Nam đi thuận: Dần (2) -> Mão (3)
    assert dv_nam[1]["cung_vi_tri"] == 3
    # Nữ đi nghịch: Dần (2) -> Sửu (1)
    assert dv_nu[1]["cung_vi_tri"] == 1

    # Kiểm tra tuổi nối tiếp: 4-13, 14-23, 24-33...
    assert dv_nam[0]["giai_doan"] == "4 - 13"
    assert dv_nam[1]["giai_doan"] == "14 - 23"


def test_case_9_round_trip_12_cung():
    """
    Test 9: Test tính toàn vẹn và chuẩn xác cổ thư của an_12_cung.
    Đối chiếu 100% với:
    - Tử Vi Đẩu Số Toàn Thư (Trần Đoàn)
    - Tử Vi Tổng Hợp (Nguyễn Phát Lộc, trang 9)
    - Các Sao Trong Tử Vi (888451701-Cac-sao-trong-Tử-Vi.txt, trang 1)

    Quy chuẩn chiều nghịch (ngược chiều kim đồng hồ từ Mệnh):
    0: Mệnh -> 1: Huynh Đệ -> 2: Phu Thê -> 3: Tử Tức -> 4: Tài Bạch -> 5: Tật Ách
    -> 6: Thiên Di -> 7: Nô Bộc -> 8: Quan Lộc -> 9: Điền Trạch -> 10: Phúc Đức -> 11: Phụ Mẫu.
    """
    for pos_menh in range(12):
        cung_res = an_12_cung(pos_menh)
        chuc_nang_map = cung_res["chuc_nang_to_dia_chi"]
        dia_chi_map = cung_res["dia_chi_to_chuc_nang"]

        assert len(chuc_nang_map) == 12
        assert len(dia_chi_map) == 12

        # 1. Xác nhận tập hợp địa chi đúng bằng {0, 1, 2, ..., 11}
        allocated_chi = {val["vi_tri_dia_chi"] for val in chuc_nang_map.values()}
        assert allocated_chi == set(range(12))

        # 2. Xác nhận đúng thứ tự nghịch từng cung
        expected_order = [
            "Mệnh", "Huynh Đệ", "Phu Thê", "Tử Tức", "Tài Bạch", "Tật Ách",
            "Thiên Di", "Nô Bộc", "Quan Lộc", "Điền Trạch", "Phúc Đức", "Phụ Mẫu"
        ]
        for i, name in enumerate(expected_order):
            expected_pos = (pos_menh - i) % 12
            assert chuc_nang_map[name]["vi_tri_dia_chi"] == expected_pos
            assert dia_chi_map[expected_pos] == name

        # 3. Xác nhận 4 bộ Tam Hợp kinh điển (cách đều 4 cung)
        # - Bộ Mệnh - Tài - Quan:
        p_menh = chuc_nang_map["Mệnh"]["vi_tri_dia_chi"]
        p_tai = chuc_nang_map["Tài Bạch"]["vi_tri_dia_chi"]
        p_quan = chuc_nang_map["Quan Lộc"]["vi_tri_dia_chi"]
        assert (p_menh + 4) % 12 == p_quan or (p_menh + 8) % 12 == p_quan
        assert (p_menh + 4) % 12 == p_tai or (p_menh + 8) % 12 == p_tai
        assert {p_menh, p_tai, p_quan} == {pos_menh, (pos_menh + 4) % 12, (pos_menh + 8) % 12}

        # - Bộ Phúc - Phối (Phu Thê) - Di:
        p_phuc = chuc_nang_map["Phúc Đức"]["vi_tri_dia_chi"]
        p_the = chuc_nang_map["Phu Thê"]["vi_tri_dia_chi"]
        p_di = chuc_nang_map["Thiên Di"]["vi_tri_dia_chi"]
        assert {p_phuc, p_the, p_di} == {p_phuc, (p_phuc + 4) % 12, (p_phuc + 8) % 12}

        # - Bộ Huynh - Điền - Tật:
        p_huynh = chuc_nang_map["Huynh Đệ"]["vi_tri_dia_chi"]
        p_dien = chuc_nang_map["Điền Trạch"]["vi_tri_dia_chi"]
        p_tat = chuc_nang_map["Tật Ách"]["vi_tri_dia_chi"]
        assert {p_huynh, p_dien, p_tat} == {p_huynh, (p_huynh + 4) % 12, (p_huynh + 8) % 12}

        # - Bộ Phụ - Tử - Nô:
        p_phu = chuc_nang_map["Phụ Mẫu"]["vi_tri_dia_chi"]
        p_tu = chuc_nang_map["Tử Tức"]["vi_tri_dia_chi"]
        p_no = chuc_nang_map["Nô Bộc"]["vi_tri_dia_chi"]
        assert {p_phu, p_tu, p_no} == {p_phu, (p_phu + 4) % 12, (p_phu + 8) % 12}

        # 4. Xác nhận 6 cặp Xung Chiếu trực diện (cách 6 cung, đối xứng qua tâm lá số)
        assert (p_menh + 6) % 12 == p_di           # Mệnh xung Thiên Di
        assert (p_the + 6) % 12 == p_quan          # Phu Thê xung Quan Lộc
        assert (p_tai + 6) % 12 == p_phuc          # Tài Bạch trực chiếu Phúc Đức (Nguyễn Phát Lộc, tr. 9)
        assert (p_tu + 6) % 12 == p_dien           # Tử Tức xung Điền Trạch
        assert (p_tat + 6) % 12 == p_phu           # Tật Ách xung Phụ Mẫu
        assert (p_huynh + 6) % 12 == p_no          # Huynh Đệ xung Nô Bộc


def test_case_10_data_integrity_all_14_stars():
    """
    Test 10: Test toàn vẹn dữ liệu: với bất kỳ input hợp lệ nào,
    xác nhận lap_la_so() luôn an đủ 14 chính tinh vào đúng 1 trong 12 cung,
    không có sao nào bị bỏ sót hay ngoài phạm vi [0, 11].
    """
    for day in [1, 7, 15, 22, 30]:
        for month in [1, 6, 12]:
            ls = lap_la_so(
                ngay_sinh_am=day,
                thang_sinh_am=month,
                nam_sinh_am=1995,
                gio_sinh_chi="Tý",
                gioi_tinh="nam"
            )
            chinh_tinh = ls["chinh_tinh_vi_tri"]
            assert len(chinh_tinh) == 14
            for star_name, pos in chinh_tinh.items():
                assert 0 <= pos <= 11, f"Sao {star_name} bị an ngoài phạm vi 0-11: {pos}"
            assert len(ls["cac_cung"]) == 12
            assert len(ls["dai_van"]) in [10, 12]


def test_case_11_khau_quyet_than_cu():
    """
    Test 11: Khẩu quyết bất di bất dịch của mọi sách Tử Vi về Thân Cư theo 12 giờ sinh:
    - Giờ Tý, Ngọ: Thân cư Mệnh
    - Giờ Sửu, Mùi: Thân cư Phúc Đức
    - Giờ Dần, Thân: Thân cư Quan Lộc
    - Giờ Mão, Dậu: Thân cư Thiên Di
    - Giờ Thìn, Tuất: Thân cư Tài Bạch
    - Giờ Tỵ, Hợi: Thân cư Phu Thê
    """
    expected_than_cu = {
        "Tý": "Thân cư Mệnh",
        "Ngọ": "Thân cư Mệnh",
        "Sửu": "Thân cư Phúc Đức",
        "Mùi": "Thân cư Phúc Đức",
        "Dần": "Thân cư Quan Lộc",
        "Thân": "Thân cư Quan Lộc",
        "Mão": "Thân cư Thiên Di",
        "Dậu": "Thân cư Thiên Di",
        "Thìn": "Thân cư Tài Bạch",
        "Tuất": "Thân cư Tài Bạch",
        "Tỵ": "Thân cư Phu Thê",
        "Hợi": "Thân cư Phu Thê",
    }

    # Kiểm thử cho mọi tháng sinh từ 1 đến 12 với mọi giờ sinh
    for month in range(1, 13):
        for chi_gio, expected_str in expected_than_cu.items():
            ls = lap_la_so(
                ngay_sinh_am=15,
                thang_sinh_am=month,
                nam_sinh_am=1990,
                gio_sinh_chi=chi_gio,
                gioi_tinh="nam"
            )
            assert ls["than_cu"] == expected_str, (
                f"Tháng {month}, giờ {chi_gio}: kỳ vọng '{expected_str}', thực tế ra '{ls['than_cu']}'"
            )


def test_case_12_profile_pham_vu_quang_hung():
    """
    Test 12: Kiểm thử chính xác theo hồ sơ thực tế của đương số Phạm Vũ Quang Hưng:
    Sinh ngày 29/05/2006 (Dương lịch), 09:15 sáng (Giờ Tỵ), Nam mạng.
    - Chuyển đổi Âm lịch: ngày 03/05/2006 (Bính Tuất).
    - Cung Mệnh: Sửu (index 1).
    - Cung Thân: Hợi (index 11).
    - Thân Cư: chuẩn 100% "Thân cư Phu Thê" (không bao giờ là Thân cư Phúc Đức).
    - Cung Phu Thê tại Hợi (11).
    - Cung Phúc Đức tại Mão (3).
    - Cung Tài Bạch tại Dậu (9) -> Cung Tài trực chiếu vào cung Phúc (Mão - Dậu xung chiếu).
    """
    ls = lap_la_so(
        ngay_sinh_am=3,
        thang_sinh_am=5,
        nam_sinh_am=2006,
        gio_sinh_chi="Tỵ",
        gioi_tinh="nam"
    )

    assert ls["ten_cung_menh"] == "Sửu"
    assert ls["cung_menh_vi_tri"] == 1
    assert ls["ten_cung_than"] == "Hợi"
    assert ls["cung_than_vi_tri"] == 11
    assert ls["than_cu"] == "Thân cư Phu Thê"

    cung_map = {c["vi_tri_dia_chi"]: c["ten_cung_chuc_nang"] for c in ls["cac_cung"]}
    assert cung_map[1] == "Mệnh"
    assert cung_map[11] == "Phu Thê"
    assert cung_map[3] == "Phúc Đức"
    assert cung_map[9] == "Tài Bạch"
    assert cung_map[5] == "Quan Lộc"
    assert cung_map[7] == "Thiên Di"
    assert cung_map[0] == "Huynh Đệ"
    assert cung_map[6] == "Nô Bộc"
    assert cung_map[2] == "Phụ Mẫu"
    assert cung_map[8] == "Tật Ách"
    assert cung_map[4] == "Điền Trạch"
    assert cung_map[10] == "Tử Tức"

    # Kiểm tra Cục chuẩn xác: Thổ Ngũ Cục (Cục 5)
    assert ls["cuc"]["ten"] == "Thổ Ngũ Cục"
    assert ls["cuc"]["so_cuc"] == 5
    assert ls["cuc"]["can_chi_cung_menh"] == "Tân Sửu"
    assert ls["cuc"]["nap_am_cung_menh"] == "Bích Thượng Thổ"

    # Kiểm tra Tử Vi tại Thìn và 14 chính tinh chuẩn tuvi.vn
    ct = ls["chinh_tinh_vi_tri"]
    assert ct["Tử Vi"] == 4 and ct["Thiên Tướng"] == 4      # Thìn
    assert ct["Thái Dương"] == 1 and ct["Thái Âm"] == 1    # Sửu (tại Mệnh)
    assert ct["Vũ Khúc"] == 0 and ct["Thiên Phủ"] == 0      # Tý
    assert ct["Tham Lang"] == 2                             # Dần
    assert ct["Thiên Cơ"] == 3 and ct["Cự Môn"] == 3        # Mão
    assert ct["Thiên Lương"] == 5                           # Tỵ
    assert ct["Thất Sát"] == 6                              # Ngọ
    assert ct["Liêm Trinh"] == 8                            # Thân
    assert ct["Phá Quân"] == 10                             # Tuất
    assert ct["Thiên Đồng"] == 11                           # Hợi

    # Kiểm tra Đại Vận 12 cung (khởi từ 5 tại Mệnh Sửu, đi thuận)
    dv_map = {c["vi_tri_dia_chi"]: c["dai_van_tuoi"] for c in ls["cac_cung"]}
    assert dv_map[1] == 5
    assert dv_map[2] == 15
    assert dv_map[3] == 25
    assert dv_map[4] == 35
    assert dv_map[5] == 45
    assert dv_map[6] == 55
    assert dv_map[7] == 65
    assert dv_map[8] == 75
    assert dv_map[9] == 85
    assert dv_map[10] == 95
    assert dv_map[11] == 105
    assert dv_map[0] == 115

    # Kiểm tra Tuần Triệt
    assert 6 in ls["tuan_khong_vi_tri"] and 7 in ls["tuan_khong_vi_tri"]
    assert 4 in ls["triet_khong_vi_tri"] and 5 in ls["triet_khong_vi_tri"]


