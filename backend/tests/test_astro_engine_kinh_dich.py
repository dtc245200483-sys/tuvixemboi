# -*- coding: utf-8 -*-
"""
Bộ 8 Test Cases kiểm thử toàn diện Kinh Dich Astro Engine
theo chuẩn Chu Dịch và Mai Hoa Dịch Số (Thiệu Khang Tiết).
Nguồn tham khảo: Chu Dịch Bản Nghĩa, Mai Hoa Dịch Số Toàn Thư.
"""

import pytest
from astro_engine.kinh_dich.core import (
    gieo_que_dong_xu,
    gieo_que_theo_thoi_gian,
    xac_dinh_que_tu_hao,
    tinh_que_bien,
    gieo_va_lap_que
)
from astro_engine.kinh_dich.constants import QUE_64, QUE_BY_CODE


def test_case_1_seed_determinism():
    """
    Test 1: Test gieo_que_dong_xu với seed cố định.
    Xác nhận luôn ra đúng 6 hào giống hệt nhau mỗi lần chạy (tính lặp lại khi kiểm thử).
    """
    run1 = gieo_que_dong_xu(seed=12345)
    run2 = gieo_que_dong_xu(seed=12345)
    assert run1 == run2
    assert len(run1) == 6
    for hao in run1:
        assert hao["tong_diem"] in [6, 7, 8, 9]
        assert hao["gia_tri"] in [0, 1]


def test_case_2_no_seed_randomness():
    """
    Test 2: Test gieo_que_dong_xu không truyền seed.
    Xác nhận tính ngẫu nhiên thực sự: chạy nhiều lần tạo ra các kết quả khác nhau.
    """
    results = [tuple(h["tong_diem"] for h in gieo_que_dong_xu()) for _ in range(20)]
    # Xác suất 20 lần tung 3 đồng xu giống hệt nhau là cực kỳ thấp (4^-114)
    assert len(set(results)) > 1, "Các lần gieo không seed phải có sự biến thiên ngẫu nhiên."


def test_case_3_all_yang_hexagram_qian():
    """
    Test 3: Test xac_dinh_que_tu_hao với bộ 6 hào toàn Dương [1, 1, 1, 1, 1, 1].
    Xác nhận nhận diện đúng Quẻ số 1: Thuần Càn (Càn vi Thiên).
    """
    hao_toan_duong = [
        {"vi_tri": i, "tong_diem": 7, "gia_tri": 1, "la_hao_dong": False}
        for i in range(1, 7)
    ]
    res = xac_dinh_que_tu_hao(hao_toan_duong)
    assert res["que_chinh"]["so_thu_tu"] == 1
    assert res["que_chinh"]["ten_que"] == "Càn vi Thiên"
    assert res["que_chinh"]["ma_nhi_phan"] == "111111"
    assert res["hao_dong"] == []


def test_case_4_all_yin_hexagram_kun():
    """
    Test 4: Test xac_dinh_que_tu_hao với bộ 6 hào toàn Âm [0, 0, 0, 0, 0, 0].
    Xác nhận nhận diện đúng Quẻ số 2: Thuần Khôn (Khôn vi Địa).
    """
    hao_toan_am = [
        {"vi_tri": i, "tong_diem": 8, "gia_tri": 0, "la_hao_dong": False}
        for i in range(1, 7)
    ]
    res = xac_dinh_que_tu_hao(hao_toan_am)
    assert res["que_chinh"]["so_thu_tu"] == 2
    assert res["que_chinh"]["ten_que"] == "Khôn vi Địa"
    assert res["que_chinh"]["ma_nhi_phan"] == "000000"
    assert res["hao_dong"] == []


def test_case_5_tinh_que_bien_with_moving_lines():
    """
    Test 5: Test tinh_que_bien với trường hợp có hào động.
    Ví dụ: Quẻ Càn ("111111"), có hào 1 động -> đảo hào 1 thành 0:
    Mã biến: "011111" (Hạ quái Tốn "011", Thượng quái Càn "111").
    Xác nhận quẻ biến là Quẻ số 44: Thiên Phong Cấu.
    """
    que_can = QUE_BY_CODE["111111"]
    que_bien = tinh_que_bien(que_can, [1])

    assert que_bien is not None
    assert que_bien["so_thu_tu"] == 44
    assert que_bien["ten_que"] == "Thiên Phong Cấu"
    assert que_bien["ma_nhi_phan"] == "011111"
    assert que_bien["quai_tren"] == "Càn"
    assert que_bien["quai_duoi"] == "Tốn"


def test_case_6_tinh_que_bien_without_moving_lines():
    """
    Test 6: Test tinh_que_bien với trường hợp KHÔNG có hào động nào.
    Xác nhận trả về None (quẻ tĩnh không biến), không bị lỗi exception.
    """
    que_can = QUE_BY_CODE["111111"]
    que_bien = tinh_que_bien(que_can, [])
    assert que_bien is None


def test_case_7_mai_hoa_time_determinism():
    """
    Test 7: Test gieo_que_theo_thoi_gian theo phương pháp Mai Hoa Dịch Số.
    Xác nhận gọi 2 lần với cùng 1 ngày/giờ sinh -> luôn cho ra CÙNG 1 kết quả xác định.
    """
    res1 = gieo_que_theo_thoi_gian(
        ngay_duong=10,
        thang_duong=2,
        nam_duong=2024,
        gio_chi="Tý"
    )
    res2 = gieo_que_theo_thoi_gian(
        ngay_duong=10,
        thang_duong=2,
        nam_duong=2024,
        gio_chi="Tý"
    )
    assert res1 == res2
    assert len(res1) == 6

    # Test hàm tổng hợp gieo_va_lap_que
    lap1 = gieo_va_lap_que("theo_thoi_gian", ngay_duong=10, thang_duong=2, nam_duong=2024, gio_chi="Tý")
    lap2 = gieo_va_lap_que("theo_thoi_gian", ngay_duong=10, thang_duong=2, nam_duong=2024, gio_chi="Tý")
    assert lap1["que_chinh"] == lap2["que_chinh"]
    assert lap1["hao_dong"] == lap2["hao_dong"]
    assert lap1["que_bien"] == lap2["que_bien"]


def test_case_8_table_64_integrity():
    """
    Test 8: Kiểm tra tính toàn vẹn của bảng 64 quẻ (64_que.py):
    - Đủ chính xác 64 quẻ.
    - Không trùng mã nhị phân giữa 2 quẻ bất kỳ (đúng 64 mã phân biệt).
    - Số thứ tự liên tục từ 1 đến 64.
    """
    assert len(QUE_64) == 64
    ma_set = {q["ma_nhi_phan"] for q in QUE_64}
    assert len(ma_set) == 64, "Phải có đúng 64 mã nhị phân không trùng lặp"

    stt_set = {q["so_thu_tu"] for q in QUE_64}
    assert stt_set == set(range(1, 65)), "Số thứ tự các quẻ phải từ 1 đến 64 đầy đủ"
