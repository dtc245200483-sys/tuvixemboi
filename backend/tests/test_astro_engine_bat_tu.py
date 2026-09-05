# -*- coding: utf-8 -*-
"""
Bộ 8 Test Cases kiểm thử toàn diện Bat Tu Astro Engine (Tứ Trụ)
theo chuẩn học thuật Tử Bình kinh điển.
Nguồn đối chiếu: Tử Bình Chân Thuyên, Trích Thiên Tủy, Lịch Vạn Niên.
"""

import pytest
from astro_engine.bat_tu.core import (
    lap_tu_tru,
    xac_dinh_can_chi_nam,
    xac_dinh_can_chi_thang,
    xac_dinh_can_chi_ngay,
    xac_dinh_can_chi_gio,
    dem_ngu_hanh,
    xac_dinh_nhat_chu,
    phan_tich_vuong_nhuoc,
    xac_dinh_dung_than
)
from astro_engine.bat_tu.constants.can_chi import CHI_DICT


def test_case_1_sample_chart_1():
    """
    Test 1: Lá số mẫu 1 - Sinh ngày 15/05/1990 Dương lịch, giờ Thìn.
    Âm lịch: Ngày 21/04/1990 (tháng 4 ÂL).
    Đối chiếu Tứ Trụ chuẩn:
    - Năm: Canh Ngọ
    - Tháng: Tân Tỵ (Năm Canh -> tháng 1 Mậu Dần, tháng 4 Tân Tỵ)
    - Ngày: Canh Thìn
    - Giờ: Canh Thìn (Ngày Canh -> giờ Tý Bính Tý, giờ Thìn Canh Thìn)
    Nhật Chủ: Canh (Kim).
    """
    tt = lap_tu_tru(15, 5, 1990, "Thìn")
    assert tt["tru_nam"] == {"can": "Canh", "chi": "Ngọ"}
    assert tt["tru_thang"] == {"can": "Tân", "chi": "Tỵ"}
    assert tt["tru_ngay"] == {"can": "Canh", "chi": "Thìn"}
    assert tt["tru_gio"] == {"can": "Canh", "chi": "Thìn"}

    nhat_chu = xac_dinh_nhat_chu(tt)
    assert nhat_chu == "Canh"

    ngu_hanh = dem_ngu_hanh(tt)
    # Kiểm tra ngũ hành có đủ 5 phần tử
    assert set(ngu_hanh.keys()) == {"Kim", "Mộc", "Thủy", "Hỏa", "Thổ"}
    vuong_nhuoc = phan_tich_vuong_nhuoc(tt, ngu_hanh)
    assert vuong_nhuoc in ["Vượng", "Nhược"]
    dung_than = xac_dinh_dung_than(nhat_chu, vuong_nhuoc, ngu_hanh)
    assert dung_than in ["Kim", "Mộc", "Thủy", "Hỏa", "Thổ"]


def test_case_2_sample_chart_2():
    """
    Test 2: Lá số mẫu 2 - Sinh ngày 10/02/2024 Dương lịch (Tết Giáp Thìn), giờ Tý.
    Âm lịch: Mùng 01/01/2024 (tháng 1 ÂL).
    Đối chiếu Tứ Trụ chuẩn:
    - Năm: Giáp Thìn
    - Tháng: Bính Dần (Năm Giáp -> tháng 1 Bính Dần)
    - Ngày: Giáp Thìn
    - Giờ: Giáp Tý (Ngày Giáp -> giờ Tý Giáp Tý)
    Nhật Chủ: Giáp (Mộc).
    """
    tt = lap_tu_tru(10, 2, 2024, "Tý")
    assert tt["tru_nam"] == {"can": "Giáp", "chi": "Thìn"}
    assert tt["tru_thang"] == {"can": "Bính", "chi": "Dần"}
    assert tt["tru_ngay"] == {"can": "Giáp", "chi": "Thìn"}
    assert tt["tru_gio"] == {"can": "Giáp", "chi": "Tý"}

    assert xac_dinh_nhat_chu(tt) == "Giáp"


def test_case_3_sample_chart_3():
    """
    Test 3: Lá số mẫu 3 - Sinh ngày 02/09/1945 Dương lịch, giờ Ngọ.
    Âm lịch: 26/07/1945 (tháng 7 ÂL).
    Đối chiếu Tứ Trụ chuẩn:
    - Năm: Ất Dậu
    - Tháng: Giáp Thân (Năm Ất -> tháng 1 Mậu Dần, tháng 7 Giáp Thân)
    - Ngày: Giáp Tuất
    - Giờ: Canh Ngọ (Ngày Giáp -> giờ Ngọ Canh Ngọ)
    Nhật Chủ: Giáp (Mộc).
    """
    tt = lap_tu_tru(2, 9, 1945, "Ngọ")
    assert tt["tru_nam"] == {"can": "Ất", "chi": "Dậu"}
    assert tt["tru_thang"] == {"can": "Giáp", "chi": "Thân"}
    assert tt["tru_ngay"] == {"can": "Giáp", "chi": "Tuất"}
    assert tt["tru_gio"] == {"can": "Canh", "chi": "Ngọ"}

    assert xac_dinh_nhat_chu(tt) == "Giáp"


def test_case_4_cycle_60_years_nam():
    """
    Test 4: Kiểm tra tính lặp lại của chu kỳ 60 Hoa Giáp của xac_dinh_can_chi_nam.
    2 năm cách nhau đúng 60 năm phải cho ra cùng 1 Can-Chi năm.
    """
    years = [1900, 1924, 1945, 1960, 1975, 1984, 2000]
    for y in years:
        res1 = xac_dinh_can_chi_nam(y)
        res2 = xac_dinh_can_chi_nam(y + 60)
        res3 = xac_dinh_can_chi_nam(y + 120)
        assert res1 == res2 == res3, f"Chu kỳ 60 năm bị sai tại năm {y}"


def test_case_5_known_day_milestone_check():
    """
    Test 5: Kiểm tra xac_dinh_can_chi_ngay với các mốc lịch sử đã biết chắc chắn đáp án đúng:
    - 01/01/1900: Ngày Giáp Tuất (mốc chuẩn gốc lịch pháp)
    - 01/01/2024: Ngày Giáp Tý
    - 10/02/2024: Ngày Giáp Thìn (Mùng 1 Tết Giáp Thìn)
    - 30/04/1975: Ngày Bính Ngọ
    """
    assert xac_dinh_can_chi_ngay(1, 1, 1900) == {"can": "Giáp", "chi": "Tuất"}
    assert xac_dinh_can_chi_ngay(1, 1, 2024) == {"can": "Giáp", "chi": "Tý"}
    assert xac_dinh_can_chi_ngay(10, 2, 2024) == {"can": "Giáp", "chi": "Thìn"}
    assert xac_dinh_can_chi_ngay(30, 4, 1975) == {"can": "Bính", "chi": "Ngọ"}


def test_case_6_ngu_hanh_count_integrity():
    """
    Test 6: Kiểm tra tính toàn vẹn của dem_ngu_hanh.
    Xác nhận tổng số lượng đếm được luôn bằng đúng số lượng chữ có mặt trong 8 chữ
    cộng với tổng số Can tàng trong 4 Địa Chi (không thừa, không thiếu).
    """
    test_cases = [
        (15, 5, 1990, "Thìn"),
        (10, 2, 2024, "Tý"),
        (2, 9, 1945, "Ngọ"),
        (1, 1, 2020, "Dần")
    ]

    for d, m, y, gio in test_cases:
        tt = lap_tu_tru(d, m, y, gio)
        counts = dem_ngu_hanh(tt)

        # 4 Thiên Can + 4 Địa Chi = 8 chữ
        # Số Can ẩn tàng trong 4 Chi:
        hidden_cans_count = sum(len(CHI_DICT[tt[t]["chi"]]["chi_tang"]) for t in ["tru_nam", "tru_thang", "tru_ngay", "tru_gio"])
        expected_total = 4 + 4 + hidden_cans_count

        assert sum(counts.values()) == expected_total, (
            f"Đếm sai tổng số ngũ hành cho ngày {d}/{m}/{y}: thực tế {sum(counts.values())} vs kỳ vọng {expected_total}"
        )


def test_case_7_round_trip_determinism():
    """
    Test 7: Tính xác định (determinism).
    Chạy lap_tu_tru() nhiều lần trên cùng 1 input -> luôn ra kết quả giống hệt nhau 100%.
    """
    first_res = lap_tu_tru(15, 8, 1995, "Thân")
    for _ in range(50):
        next_res = lap_tu_tru(15, 8, 1995, "Thân")
        assert first_res == next_res


def test_case_8_boundary_month_transition():
    """
    Test 8: Test biên: ngày sinh ở đúng ranh giới chuyển tháng âm lịch (ngày đầu/cuối tháng).
    Xác nhận Can-Chi tháng được xác định đúng, không bị lệch do lấy nhầm tháng:
    - 19/02/2023 là ngày 29/01 ÂL (cuối tháng 1 ÂL) -> Chi tháng là Dần (tháng 1).
    - 20/02/2023 là ngày 01/02 ÂL (đầu tháng 2 ÂL) -> Chi tháng là Mão (tháng 2).
    """
    tt_cuoi_thang_1 = lap_tu_tru(19, 2, 2023, "Tý")
    tt_dau_thang_2 = lap_tu_tru(20, 2, 2023, "Tý")

    # Năm 2023 là Quý Mão (Can Quý)
    # Tháng 1 là Giáp Dần
    assert tt_cuoi_thang_1["tru_thang"] == {"can": "Giáp", "chi": "Dần"}

    # Tháng 2 là Ất Mão
    assert tt_dau_thang_2["tru_thang"] == {"can": "Ất", "chi": "Mão"}
