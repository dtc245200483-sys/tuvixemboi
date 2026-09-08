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
    assert tt["tru_nam"]["can"] == "Canh" and tt["tru_nam"]["chi"] == "Ngọ"
    assert tt["tru_thang"]["can"] == "Tân" and tt["tru_thang"]["chi"] == "Tỵ"
    assert tt["tru_ngay"]["can"] == "Canh" and tt["tru_ngay"]["chi"] == "Thìn"
    assert tt["tru_gio"]["can"] == "Canh" and tt["tru_gio"]["chi"] == "Thìn"

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
    assert tt["tru_nam"]["can"] == "Giáp" and tt["tru_nam"]["chi"] == "Thìn"
    assert tt["tru_thang"]["can"] == "Bính" and tt["tru_thang"]["chi"] == "Dần"
    assert tt["tru_ngay"]["can"] == "Giáp" and tt["tru_ngay"]["chi"] == "Thìn"
    assert tt["tru_gio"]["can"] == "Giáp" and tt["tru_gio"]["chi"] == "Tý"

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
    assert tt["tru_nam"]["can"] == "Ất" and tt["tru_nam"]["chi"] == "Dậu"
    assert tt["tru_thang"]["can"] == "Giáp" and tt["tru_thang"]["chi"] == "Thân"
    assert tt["tru_ngay"]["can"] == "Giáp" and tt["tru_ngay"]["chi"] == "Tuất"
    assert tt["tru_gio"]["can"] == "Canh" and tt["tru_gio"]["chi"] == "Ngọ"

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
    Test 8: Test biên ranh giới chuyển tiết khí của Trụ Tháng theo Tử Bình:
    - 05/03/2023 vẫn thuộc tiết Lập Xuân/Vũ Thủy -> Nguyệt lệnh Dần (Giáp Dần).
    - 06/03/2023 đã bước sang tiết Kinh Trập -> Nguyệt lệnh Mão (Ất Mão).
    """
    tt_truoc_kinh_trap = lap_tu_tru(5, 3, 2023, "Tý")
    tt_sau_kinh_trap = lap_tu_tru(6, 3, 2023, "Tý")

    # Trước Kinh Trập: Tháng 1 là Giáp Dần
    assert tt_truoc_kinh_trap["tru_thang"]["can"] == "Giáp" and tt_truoc_kinh_trap["tru_thang"]["chi"] == "Dần"

    # Sau Kinh Trập: Tháng 2 là Ất Mão
    assert tt_sau_kinh_trap["tru_thang"]["can"] == "Ất" and tt_sau_kinh_trap["tru_thang"]["chi"] == "Mão"


def test_case_9_thap_than_and_pillar_details():
    """
    Test 9: Kiểm tra tính Thập Thần và chi tiết 4 trụ theo sách Trần Khang Ninh.
    """
    tt = lap_tu_tru(15, 5, 1990, "Thìn", gioi_tinh="nam")
    assert "chi_tiet_tru" in tt
    assert "tru_nam" in tt["chi_tiet_tru"]
    assert "tru_thang" in tt["chi_tiet_tru"]
    assert "tru_ngay" in tt["chi_tiet_tru"]
    assert "tru_gio" in tt["chi_tiet_tru"]

    # Canh Kim ngày gặp Canh Kim năm -> Tỷ Kiên
    assert tt["chi_tiet_tru"]["tru_nam"]["thap_than"]["ten"] == "Tỷ Kiên"
    # Canh Kim ngày gặp Tân Kim tháng -> Kiếp Tài
    assert tt["chi_tiet_tru"]["tru_thang"]["thap_than"]["ten"] == "Kiếp Tài"


def test_case_10_cach_cuc_and_dieu_hau():
    """
    Test 10: Kiểm tra xác định Cách Cục và Dụng Thần Điều Hầu.
    """
    # Sinh mùa Đông (tháng 12 DL / tháng 11 AL): Cần Hỏa Điều Hầu
    tt_dong = lap_tu_tru(20, 12, 1995, "Tý")
    assert tt_dong["dung_than_detail"]["dieu_hau"] is not None
    assert tt_dong["dung_than_detail"]["dieu_hau"]["ngu_hanh"] == "Hỏa"

    # Kiểm tra có cấu trúc cách cục rõ ràng
    assert "cach_cuc" in tt_dong
    assert "ten_cach" in tt_dong["cach_cuc"]


def test_case_11_dai_van_direction():
    """
    Test 11: Kiểm tra chiều Đại Vận (Dương Nam thuận, Âm Nam nghịch).
    Năm 1990 là Canh Ngọ (Canh = Dương Kim) -> Nam đi THUẬN, Nữ đi NGHỊCH.
    """
    tt_nam = lap_tu_tru(15, 5, 1990, "Thìn", gioi_tinh="nam")
    tt_nu = lap_tu_tru(15, 5, 1990, "Thìn", gioi_tinh="nu")

    dv_nam = tt_nam["dai_van"]
    dv_nu = tt_nu["dai_van"]

    assert len(dv_nam) == 8
    assert len(dv_nu) == 8
    # Vận 1 của Nam và Nữ phải khác nhau do 1 bên thuận 1 bên nghịch
    assert dv_nam[0]["can_chi"] != dv_nu[0]["can_chi"]


def test_case_12_than_sat_and_cai_menh():
    """
    Test 12: Kiểm tra Thần Sát và Cải Vận Đời Sống.
    """
    tt = lap_tu_tru(10, 2, 2024, "Tý")
    assert "cai_menh" in tt
    assert "mau_sac" in tt["cai_menh"]
    assert "con_so" in tt["cai_menh"]
    assert "phuong_huong" in tt["cai_menh"]
    assert "khong_vong" in tt


def test_case_13_vuong_nhuoc_chuan_tu_binh_and_validator():
    """
    Test 13: Kiểm tra tính chuẩn xác của Thẩm Định Thân Vượng Nhược theo sách Trần Khang Ninh:
    Lá số 29/05/2006, 9h15 (Bính Tuất - Quý Tỵ - Mậu Ngọ - Đinh Tỵ):
    1. Đắc Thế: CHỈ CÓ Bính (Thiên Ấn) và Đinh (Chính Ấn). TUYỆT ĐỐI KHÔNG CÓ Quý (Chính Tài).
       Quý phải nằm ở cans_tiet_khac.
    2. Đắc Lệnh: Nêu đích danh Bính (Thiên Ấn) và Mậu (Tỷ Kiên).
    3. Đắc Địa: Chỉ tính tàng can Tỷ Kiên, Kiếp Tài; tuyệt đối không tính Ấn.
    4. Validator & Mục IV: Không có 40/35/20, không có luận chung chung 'Hỏa sinh Thổ'.
    """
    from astro_engine.bat_tu.validator import (
        tao_noi_dung_chuan_muc_4,
        kiem_tra_va_chuan_hoa_luan_giai_bat_tu
    )

    tt = lap_tu_tru(29, 5, 2006, "Tỵ", "Nam", 9, 15)
    vn = tt["vuong_nhuoc_detail"]

    # 1. Kiểm tra Đắc Thế
    assert vn["dac_the"] is True
    bang_chung_the_str = " ".join(vn["bang_chung_the"])
    assert "Bính" in bang_chung_the_str
    assert "Đinh" in bang_chung_the_str
    assert "Quý" not in bang_chung_the_str  # BỎ HẲN Quý khỏi Đắc Thế!

    cans_loai_tru_str = " ".join(vn["cans_tiet_khac"])
    assert "Quý" in cans_loai_tru_str
    assert "Chính Tài" in cans_loai_tru_str

    # 2. Kiểm tra Đắc Lệnh
    assert vn["dac_lenh"] is True
    bc_lenh_str = " ".join(vn["bang_chung_lenh"])
    assert "Bính (Thiên Ấn)" in bc_lenh_str
    assert "Mậu (Tỷ Kiên)" in bc_lenh_str

    # 3. Kiểm tra Đắc Địa
    assert vn["dac_dia"] is True
    bc_dia_str = " ".join(vn["bang_chung_dia"])
    assert "Tỷ Kiên" in bc_dia_str or "Kiếp Tài" in bc_dia_str
    assert "Chính Ấn" not in bc_dia_str and "Thiên Ấn" not in bc_dia_str

    # 4. Kiểm tra Validator sinh Mục IV
    m4 = tao_noi_dung_chuan_muc_4(tt)
    assert "Thân Vượng" in m4
    assert "40" not in m4 and "35" not in m4 and "20" not in m4
    assert "Hỏa sinh Thổ, nên Đắc Lệnh" not in m4
    assert "các Chi đều chứa Thần hỗ trợ" not in m4

    # 5. Kiểm tra kiem_tra_va_chuan_hoa_luan_giai_bat_tu sửa sạch lỗi cũ
    raw_ai_loi = '''• Mục I. An toàn vùng biên
• Mục II. Tứ Trụ
- Mục IV. Đánh giá Khí Lực Bản Thân (Thân Vượng):
  • Kết luận: Thân Vượng
  • Bằng chứng:
    - Đắc Lệnh: Ngày Mậu (Thổ) sinh trong tháng Tỵ (Hỏa) – Hỏa sinh Thổ, nên Đắc Lệnh (điểm Lệnh 40).
    - Đắc Địa: Ngày Mậu có gốc rễ thông căn vững vàng ở các Chi Năm, Tháng, Giờ (các Chi đều chứa Thần hỗ trợ), nên Đắc Địa (điểm Địa 35).
    - Đắc Thế: Các Thiên Can còn lại (Bính, Quý, Đinh) đều có Thiên Ấn hoặc Tỷ Kiên hỗ trợ, nên Đắc Thế (điểm Thế 20).
• Mục V. Định danh Cách Cục
'''
    cleaned = kiem_tra_va_chuan_hoa_luan_giai_bat_tu(raw_ai_loi, tt)
    assert "điểm Lệnh 40" not in cleaned
    assert "điểm Địa 35" not in cleaned
    assert "điểm Thế 20" not in cleaned
    assert "Các Thiên Can còn lại (Bính, Quý, Đinh)" not in cleaned
    assert "Hỏa sinh Thổ, nên Đắc Lệnh" not in cleaned
    assert "các Chi đều chứa Thần hỗ trợ" not in cleaned


