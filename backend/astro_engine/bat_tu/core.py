# -*- coding: utf-8 -*-
"""
Module lõi thực thi thuật toán lập Tứ Trụ (Bát Tự) và phân tích Vượng Nhược / Dụng Thần.
Áp dụng trường phái Tử Bình kinh điển (Trích Thiên Tủy, Tử Bình Chân Thuyên).
Mọi kết quả là dữ liệu JSON có cấu trúc, không chứa câu chữ diễn giải tự do.
"""

from typing import Dict, Any, List
from astro_engine.bat_tu.constants.can_chi import (
    CAN_NAMES,
    CHI_NAMES,
    CAN_DICT,
    CHI_DICT
)
from astro_engine.bat_tu.constants.ngu_hanh import (
    DANH_SACH_NGU_HANH,
    TUONG_SINH,
    HANH_SINH_RA,
    TUONG_KHAC,
    HANH_KHAC_NO
)
from calendar_converter.lunar_calendar import solar_to_lunar


def jdn(d: int, m: int, y: int) -> int:
    """Tính số ngày Julius (JDN) từ ngày, tháng, năm Dương lịch."""
    a = (14 - m) // 12
    y2 = y + 4800 - a
    m2 = m + 12 * a - 3
    return d + ((153 * m2 + 2) // 5) + 365 * y2 + (y2 // 4) - (y2 // 100) + (y2 // 400) - 32045


def xac_dinh_can_chi_nam(nam_duong: int) -> Dict[str, str]:
    """
    1. Xác định Can-Chi năm sinh dựa trên năm dương lịch (chu kỳ 60 Hoa Giáp).
    
    Công thức:
    - Thiên Can: (nam_duong + 6) % 10
    - Địa Chi:   (nam_duong + 8) % 12
    
    Nguồn: Bảng tra Hoa Giáp Lịch Pháp Á Đông.
    """
    can_idx = (nam_duong + 6) % 10
    chi_idx = (nam_duong + 8) % 12
    return {
        "can": CAN_NAMES[can_idx],
        "chi": CHI_NAMES[chi_idx]
    }


def xac_dinh_can_chi_thang(nam_can: str, thang_am: int) -> Dict[str, str]:
    """
    2. Xác định Can-Chi tháng sinh.
    
    Quy tắc:
    - Địa Chi tháng cố định theo tháng âm lịch:
      Tháng 1: Dần, Tháng 2: Mão, ..., Tháng 11: Tý, Tháng 12: Sửu.
    - Thiên Can tháng tính theo quy tắc 'Ngũ Hổ Độn' khởi từ Can của năm:
      + Năm Giáp/Kỷ: Tháng 1 là Bính Dần
      + Năm Ất/Canh: Tháng 1 là Mậu Dần
      + Năm Bính/Tân: Tháng 1 là Canh Dần
      + Năm Đinh/Nhâm: Tháng 1 là Nhâm Dần
      + Năm Mậu/Quý: Tháng 1 là Giáp Dần
    """
    if not (1 <= thang_am <= 12):
        raise ValueError(f"Tháng âm lịch ({thang_am}) phải trong khoảng 1-12.")
    if nam_can not in CAN_NAMES:
        raise ValueError(f"Can năm '{nam_can}' không hợp lệ.")

    can_nam_idx = CAN_NAMES.index(nam_can)
    can_thang_1_idx = (can_nam_idx % 5 * 2 + 2) % 10
    can_thang_idx = (can_thang_1_idx + thang_am - 1) % 10
    chi_thang_idx = (2 + thang_am - 1) % 12

    return {
        "can": CAN_NAMES[can_thang_idx],
        "chi": CHI_NAMES[chi_thang_idx]
    }


def xac_dinh_can_chi_ngay(ngay_duong: int, thang_duong: int, nam_duong: int) -> Dict[str, str]:
    """
    3. Xác định Can-Chi ngày sinh bằng công thức đếm chu kỳ 60 ngày từ mốc gốc chuẩn.
    
    Mốc kiểm chứng:
    - Mốc gốc: Ngày 01/01/1900 là ngày Giáp Tuất (JDN = 2415021).
    - Kiểm chứng độc lập 1: Ngày 01/01/2024 là ngày Giáp Tý (JDN = 2460311).
    - Kiểm chứng độc lập 2: Ngày 10/02/2024 (Tết Giáp Thìn) là ngày Giáp Thìn (JDN = 2460351).
    - Kiểm chứng độc lập 3: Ngày 30/04/1975 là ngày Bính Ngọ (JDN = 2442533).
    
    Công thức thiên văn:
    Can ngày = (JDN + 9) % 10
    Chi ngày = (JDN + 1) % 12
    """
    from datetime import date
    try:
        date(nam_duong, thang_duong, ngay_duong)
    except ValueError as e:
        raise ValueError(f"Ngày Dương lịch {ngay_duong}/{thang_duong}/{nam_duong} không hợp lệ: {str(e)}")

    j = jdn(ngay_duong, thang_duong, nam_duong)
    can_idx = (j + 9) % 10
    chi_idx = (j + 1) % 12

    return {
        "can": CAN_NAMES[can_idx],
        "chi": CHI_NAMES[chi_idx]
    }


def xac_dinh_can_chi_gio(ngay_can: str, gio_chi: str) -> Dict[str, str]:
    """
    4. Xác định Can của giờ sinh theo quy tắc 'Ngũ Thử Độn' (tìm Can giờ từ Can ngày).
    
    Quy tắc:
    - Ngày Giáp/Kỷ: Giờ Tý bắt đầu là Giáp Tý
    - Ngày Ất/Canh: Giờ Tý bắt đầu là Bính Tý
    - Ngày Bính/Tân: Giờ Tý bắt đầu là Mậu Tý
    - Ngày Đinh/Nhâm: Giờ Tý bắt đầu là Canh Tý
    - Ngày Mậu/Quý: Giờ Tý bắt đầu là Nhâm Tý
    """
    if ngay_can not in CAN_NAMES:
        raise ValueError(f"Can ngày '{ngay_can}' không hợp lệ.")
    if gio_chi not in CHI_NAMES:
        raise ValueError(f"Chi giờ '{gio_chi}' không hợp lệ.")

    can_ngay_idx = CAN_NAMES.index(ngay_can)
    can_ty_idx = (can_ngay_idx % 5 * 2) % 10
    gio_idx = CHI_NAMES.index(gio_chi)
    can_gio_idx = (can_ty_idx + gio_idx) % 10

    return {
        "can": CAN_NAMES[can_gio_idx],
        "chi": gio_chi
    }


def lap_tu_tru(ngay_duong: int, thang_duong: int, nam_duong: int, gio_chi: str) -> Dict[str, Any]:
    """
    5. Lập Tứ Trụ (Bát Tự) hoàn chỉnh gồm 4 trụ: Năm, Tháng, Ngày, Giờ.
    Sử dụng kết quả chuyển đổi từ calendar_converter để đảm bảo xác định tháng âm lịch chuẩn xác.
    """
    # 1. Chuyển đổi để lấy thông tin tháng âm lịch (và năm âm nếu giáp Tết)
    lunar_info = solar_to_lunar(ngay_duong, thang_duong, nam_duong)
    thang_am = lunar_info["thang_am"]

    # 2. Xác định từng trụ
    tru_nam = xac_dinh_can_chi_nam(nam_duong)
    tru_thang = xac_dinh_can_chi_thang(tru_nam["can"], thang_am)
    tru_ngay = xac_dinh_can_chi_ngay(ngay_duong, thang_duong, nam_duong)
    tru_gio = xac_dinh_can_chi_gio(tru_ngay["can"], gio_chi)

    return {
        "tru_nam": tru_nam,
        "tru_thang": tru_thang,
        "tru_ngay": tru_ngay,
        "tru_gio": tru_gio
    }


def dem_ngu_hanh(tu_tru: Dict[str, Any]) -> Dict[str, int]:
    """
    6. Đếm số lượng mỗi Ngũ Hành xuất hiện trong Tứ Trụ (Bát Tự).
    Bao gồm cả 4 Thiên Can, 4 Địa Chi (bản khí) và toàn bộ các Can Ẩn Tàng trong Chi.
    
    Quy tắc kiểm tra toàn vẹn:
    Tổng số đếm = 4 (Can) + 4 (Chi) + Tổng số Can tàng trong 4 Chi.
    
    Returns:
        dict: {"Kim": n, "Mộc": n, "Thủy": n, "Hỏa": n, "Thổ": n}
    """
    counts = {h: 0 for h in DANH_SACH_NGU_HANH}

    trus = [tu_tru["tru_nam"], tu_tru["tru_thang"], tu_tru["tru_ngay"], tu_tru["tru_gio"]]

    for tru in trus:
        can = tru["can"]
        chi = tru["chi"]

        # 1. Ngũ hành của Can
        can_hanh = CAN_DICT[can]["ngu_hanh"]
        counts[can_hanh] += 1

        # 2. Ngũ hành của Chi (bản khí)
        chi_hanh = CHI_DICT[chi]["ngu_hanh"]
        counts[chi_hanh] += 1

        # 3. Ngũ hành của các Can ẩn tàng trong Chi
        for hidden_can in CHI_DICT[chi]["chi_tang"]:
            h_hanh = CAN_DICT[hidden_can]["ngu_hanh"]
            counts[h_hanh] += 1

    return counts


def xac_dinh_nhat_chu(tu_tru: Dict[str, Any]) -> str:
    """
    7. Xác định 'Nhật Chủ' (Thiên Can của trụ Ngày - đại diện cho bản thân thân chủ).
    """
    return tu_tru["tru_ngay"]["can"]


def phan_tich_vuong_nhuoc(tu_tru: Dict[str, Any], ngu_hanh_count: Dict[str, int]) -> str:
    """
    8. Phân tích Nhật Chủ là Vượng (mạnh) hay Nhược (yếu).
    
    Trường phái áp dụng:
    Theo trường phái Tử Bình cổ truyền (Trích Thiên Tủy & Tử Bình Chân Thuyên):
    - Nhóm Đồng Minh (Sinh/Trợ cho Nhật Chủ):
      + Tỷ Kiếp (cùng ngũ hành với Nhật Chủ - Trợ)
      + Ấn Tinh (ngũ hành sinh ra Nhật Chủ - Sinh)
    - Nhóm Tiêu Hao (Khắc/Tiết/Hao khí của Nhật Chủ):
      + Thực Thương (ngũ hành Nhật Chủ sinh ra - Tiết)
      + Tài Tinh (ngũ hành Nhật Chủ khắc - Hao)
      + Quan Sát (ngũ hành khắc Nhật Chủ - Khắc)
    - Đắc Lệnh Tháng: Chi của trụ Tháng mang hành sinh hoặc cùng hành với Nhật Chủ.
    
    Returns:
        str: "Vượng" hoặc "Nhược"
    """
    nhat_chu = xac_dinh_nhat_chu(tu_tru)
    hanh_nhat_chu = CAN_DICT[nhat_chu]["ngu_hanh"]
    hanh_sinh = HANH_SINH_RA[hanh_nhat_chu]

    # Điểm Đồng Minh = Số lượng hành bản mệnh + số lượng hành sinh bản mệnh
    diem_sinh_tro = ngu_hanh_count.get(hanh_nhat_chu, 0) + ngu_hanh_count.get(hanh_sinh, 0)

    # Điểm Tiêu Hao = Tổng các hành còn lại (Thực thương, Tài tinh, Quan sát)
    diem_tieu_hao = sum(
        ngu_hanh_count.get(h, 0) for h in DANH_SACH_NGU_HANH
        if h not in [hanh_nhat_chu, hanh_sinh]
    )

    # Xét Đắc Lệnh tháng (Chi của tháng sinh)
    chi_thang = tu_tru["tru_thang"]["chi"]
    hanh_chi_thang = CHI_DICT[chi_thang]["ngu_hanh"]
    dac_lenh = (hanh_chi_thang == hanh_nhat_chu or hanh_chi_thang == hanh_sinh)

    if diem_sinh_tro > diem_tieu_hao:
        return "Vượng"
    elif diem_sinh_tro < diem_tieu_hao:
        return "Nhược"
    else:
        return "Vượng" if dac_lenh else "Nhược"


def xac_dinh_dung_than(nhat_chu: str, vuong_nhuoc: str, ngu_hanh_count: Dict[str, int]) -> str:
    """
    9. Xác định Dụng Thần (Ngũ Hành cần thiết nhất để lập lại thế quân bình cho bản mệnh).
    
    Trường phái áp dụng:
    Quy tắc bình quân bổ khuyết kinh điển:
    - Nếu Thân 'Vượng': Cần Khắc (Quan Sát), Tiết (Thực Thương), hoặc Hao (Tài Tinh).
      Ưu tiên chọn hành có số lượng ít nhất trong nhóm Khắc/Tiết/Hao để bổ sung cân bằng.
    - Nếu Thân 'Nhược': Cần Sinh (Ấn Tinh) hoặc Trợ (Tỷ Kiếp).
      Ưu tiên chọn hành có số lượng ít hơn giữa Ấn Tinh và Tỷ Kiếp để tăng cường trợ lực.
    
    Returns:
        str: Tên một trong 5 Ngũ Hành ("Kim", "Mộc", "Thủy", "Hỏa", "Thổ").
    """
    hanh_nhat_chu = CAN_DICT[nhat_chu]["ngu_hanh"]
    hanh_sinh = HANH_SINH_RA[hanh_nhat_chu]      # Ấn tinh
    hanh_tiet = TUONG_SINH[hanh_nhat_chu]       # Thực thương
    hanh_khac = TUONG_KHAC[hanh_nhat_chu]       # Tài tinh
    hanh_khac_minh = HANH_KHAC_NO[hanh_nhat_chu] # Quan sát

    if vuong_nhuoc == "Vượng":
        # Cần nhóm Khắc/Tiết/Hao: [Quan Sát, Thực Thương, Tài Tinh]
        nhom_can_thiet = [hanh_khac_minh, hanh_tiet, hanh_khac]
        # Chọn hành có số lượng ít nhất để bồi bổ
        nhom_sorted = sorted(nhom_can_thiet, key=lambda h: ngu_hanh_count.get(h, 0))
        return nhom_sorted[0]
    else:
        # Thân Nhược: Cần nhóm Sinh/Trợ: [Ấn Tinh (Sinh), Tỷ Kiếp (Trợ)]
        nhom_can_thiet = [hanh_sinh, hanh_nhat_chu]
        nhom_sorted = sorted(nhom_can_thiet, key=lambda h: ngu_hanh_count.get(h, 0))
        return nhom_sorted[0]
