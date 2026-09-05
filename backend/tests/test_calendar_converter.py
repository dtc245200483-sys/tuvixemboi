# -*- coding: utf-8 -*-
"""
Bộ 10 Test Cases kiểm thử toàn diện độ chính xác của Calendar Converter
theo đúng yêu cầu của Prompt 2.3.
"""

import pytest
from calendar_converter.lunar_calendar import (
    solar_to_lunar,
    lunar_to_solar,
    xac_dinh_gio_sinh_theo_canh_gio
)


def test_case_1_normal_solar_date():
    """
    Test 1: Một ngày dương lịch thông thường (không rơi vào ngày đầu/cuối tháng âm).
    Ngày 20/10/2023 Dương lịch -> 06/09/2023 Âm lịch (Quý Mão).
    """
    res = solar_to_lunar(20, 10, 2023)
    assert res["ngay_am"] == 6
    assert res["thang_am"] == 9
    assert res["nam_am"] == 2023
    assert res["la_thang_nhuan"] is False
    assert res["can_nam"] == "Quý"
    assert res["chi_nam"] == "Mão"


def test_case_2_new_year_day_solar():
    """
    Test 2: Ngày 1/1 dương lịch của 1 năm bất kỳ.
    Ngày 01/01/2024 Dương lịch -> 20/11/2023 Âm lịch (Quý Mão), rơi vào cuối tháng 11 năm trước.
    """
    res = solar_to_lunar(1, 1, 2024)
    assert res["ngay_am"] == 20
    assert res["thang_am"] == 11
    assert res["nam_am"] == 2023
    assert res["la_thang_nhuan"] is False
    assert res["can_nam"] == "Quý"
    assert res["chi_nam"] == "Mão"


def test_case_3_leap_month_year():
    """
    Test 3: Một năm CÓ tháng nhuận âm lịch.
    Năm 2023 (Quý Mão) có tháng 2 nhuận.
    Ngày 22/03/2023 Dương lịch là ngày mùng 1 tháng 2 Nhuận năm Quý Mão.
    """
    res = solar_to_lunar(22, 3, 2023)
    assert res["ngay_am"] == 1
    assert res["thang_am"] == 2
    assert res["nam_am"] == 2023
    assert res["la_thang_nhuan"] is True
    assert res["can_nam"] == "Quý"
    assert res["chi_nam"] == "Mão"


def test_case_4_short_lunar_month_29_days():
    """
    Test 4: Ngày cuối cùng của 1 tháng âm lịch thiếu (29 ngày).
    Tháng 1 âm lịch năm Quý Mão 2023 là tháng thiếu chỉ có 29 ngày (22/01/2023 đến 19/02/2023).
    Ngày 19/02/2023 là 29/01/2023 ÂL, ngày 20/02/2023 sang ngay 01/02/2023 ÂL.
    Xác nhận lunar_to_solar từ chối ngày 30/01/2023 ÂL không tồn tại.
    """
    # Ngày 19/02/2023 dương lịch -> ngày 29/01 âm lịch
    res_29 = solar_to_lunar(19, 2, 2023)
    assert res_29["ngay_am"] == 29
    assert res_29["thang_am"] == 1

    # Ngày 20/02/2023 dương lịch -> sang mùng 01/02 âm lịch (không có ngày 30)
    res_next = solar_to_lunar(20, 2, 2023)
    assert res_next["ngay_am"] == 1
    assert res_next["thang_am"] == 2

    # Gọi lunar_to_solar với ngày 30/1/2023 ÂL phải báo lỗi tháng thiếu không có ngày 30
    with pytest.raises(ValueError, match="chỉ có 29 ngày"):
        lunar_to_solar(ngay_am=30, thang_am=1, nam_am=2023, la_thang_nhuan=False)


def test_case_5_born_at_23h30_midnight_rule():
    """
    Test 5: Sinh giờ 23h30 (thuộc giờ Tý gần nửa đêm).
    Xác nhận xac_dinh_gio_sinh_theo_canh_gio trả về đúng 'Tý' và
    ngày âm lịch được tính là NGÀY HÔM SAU theo quy tắc giờ Tý đầu ngày mới.
    """
    canh_gio = xac_dinh_gio_sinh_theo_canh_gio(23, 30)
    assert canh_gio["ten_gio_can_chi"] == "Tý"
    assert canh_gio["chi_gio"] == "Tý"
    assert canh_gio["chuyen_sang_ngay_hom_sau"] is True

    # Sinh lúc 23h30 ngày 15/05/2024 -> ngày âm lịch tính theo 16/05/2024
    res_23h30 = solar_to_lunar(15, 5, 2024, gio=23)
    assert res_23h30["ngay_am"] == 9
    assert res_23h30["thang_am"] == 4
    assert res_23h30["nam_am"] == 2024
    assert res_23h30["ten_gio"] == "Tý"


def test_case_6_born_at_0h30_same_lunar_day_as_case_5():
    """
    Test 6: Sinh giờ 0h30 (sau nửa đêm dương lịch nhưng vẫn giờ Tý).
    Xác nhận vẫn nhận diện đúng 'Tý' và thuộc CÙNG ngày âm lịch với case 5.
    """
    canh_gio = xac_dinh_gio_sinh_theo_canh_gio(0, 30)
    assert canh_gio["ten_gio_can_chi"] == "Tý"
    assert canh_gio["chi_gio"] == "Tý"
    assert canh_gio["chuyen_sang_ngay_hom_sau"] is False

    # Sinh lúc 0h30 ngày 16/05/2024
    res_0h30 = solar_to_lunar(16, 5, 2024, gio=0)
    assert res_0h30["ngay_am"] == 9
    assert res_0h30["thang_am"] == 4
    assert res_0h30["nam_am"] == 2024
    assert res_0h30["ten_gio"] == "Tý"

    # Xác nhận khớp hoàn toàn ngày âm và giờ với case 5
    res_case_5 = solar_to_lunar(15, 5, 2024, gio=23)
    assert res_0h30["ngay_am"] == res_case_5["ngay_am"]
    assert res_0h30["thang_am"] == res_case_5["thang_am"]
    assert res_0h30["nam_am"] == res_case_5["nam_am"]
    assert res_0h30["ten_gio"] == res_case_5["ten_gio"]


def test_case_7_lunar_to_solar_conversion():
    """
    Test 7: Chuyển đổi ngược: lấy 1 ngày âm lịch đã biết -> lunar_to_solar -> ra đúng ngày dương lịch.
    Ví dụ: Rằm Trung Thu 15/08/2023 Âm lịch -> Ngày 29/09/2023 Dương lịch.
    """
    solar = lunar_to_solar(ngay_am=15, thang_am=8, nam_am=2023, la_thang_nhuan=False)
    assert solar["ngay"] == 29
    assert solar["thang"] == 9
    assert solar["nam"] == 2023


def test_case_8_round_trip_two_way_conversion():
    """
    Test 8: Test 2 chiều: solar_to_lunar rồi lunar_to_solar lại.
    Xác nhận ra đúng ngày dương lịch ban đầu trên nhiều mốc lịch sử và hiện đại.
    """
    sample_dates = [
        (10, 2, 2024),  # Mùng 1 Tết Giáp Thìn
        (22, 1, 2023),  # Mùng 1 Tết Quý Mão
        (22, 3, 2023),  # Mùng 1 tháng 2 Nhuận Quý Mão
        (1, 1, 2024),   # Đầu năm dương
        (30, 4, 1975),  # Ngày 30/4/1975
        (2, 9, 1945),   # Ngày 2/9/1945
        (15, 7, 2022),  # Ngày thường
    ]

    for d, m, y in sample_dates:
        lunar = solar_to_lunar(d, m, y)
        solar = lunar_to_solar(
            ngay_am=lunar["ngay_am"],
            thang_am=lunar["thang_am"],
            nam_am=lunar["nam_am"],
            la_thang_nhuan=lunar["la_thang_nhuan"]
        )
        assert (solar["ngay"], solar["thang"], solar["nam"]) == (d, m, y), (
            f"Round-trip failed for {d}/{m}/{y}"
        )


def test_case_9_first_day_of_lunar_month_new_year():
    """
    Test 9: Một ngày rơi đúng vào mùng 1 âm lịch (Tết Nguyên Đán).
    Xác nhận độ chính xác tuyệt đối:
    - 10/02/2024 Dương lịch = Mùng 01/01/2024 Âm lịch (Tết Giáp Thìn).
    - Can ngày = Giáp, Chi ngày = Thìn.
    - Can năm = Giáp, Chi năm = Thìn.
    """
    res = solar_to_lunar(10, 2, 2024)
    assert res["ngay_am"] == 1
    assert res["thang_am"] == 1
    assert res["nam_am"] == 2024
    assert res["la_thang_nhuan"] is False
    assert res["can_nam"] == "Giáp"
    assert res["chi_nam"] == "Thìn"
    assert res["can_ngay"] == "Giáp"
    assert res["chi_ngay"] == "Thìn"


def test_case_10_invalid_inputs_raise_exception():
    """
    Test 10: Input không hợp lệ (VD: ngày 32/1, 30/2, giờ 25).
    Xác nhận raise exception đúng như thiết kế, không trả kết quả sai âm thầm.
    """
    # Ngày 32 tháng 1
    with pytest.raises(ValueError):
        solar_to_lunar(32, 1, 2024)

    # Ngày 30 tháng 2 (kể cả năm nhuận 2024 tháng 2 chỉ có 29 ngày)
    with pytest.raises(ValueError):
        solar_to_lunar(30, 2, 2024)

    # Tháng 13
    with pytest.raises(ValueError):
        solar_to_lunar(15, 13, 2024)

    # Giờ 25
    with pytest.raises(ValueError):
        solar_to_lunar(15, 5, 2024, gio=25)

    # lunar_to_solar với tháng 15 âm lịch
    with pytest.raises(ValueError):
        lunar_to_solar(15, 15, 2024)

    # lunar_to_solar với tháng nhuận không tồn tại (năm 2024 không có tháng nhuận nào)
    with pytest.raises(ValueError):
        lunar_to_solar(15, 4, 2024, la_thang_nhuan=True)
