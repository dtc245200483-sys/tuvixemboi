# -*- coding: utf-8 -*-
"""
Module chuyển đổi Dương lịch <-> Âm lịch và xác định Can Chi chính xác
theo thuật toán thiên văn chuẩn cho múi giờ Việt Nam (GMT+7).

Các thuật toán dựa trên nghiên cứu thiên văn của Jean Meeus và tác giả Hồ Ngọc Đức,
xử lý chính xác từng ngày Sóc (New Moon), Trung khí và quy tắc tháng nhuận.
"""

import math
from datetime import date, datetime, timezone, timedelta
from typing import Dict, Any, Tuple, Optional, List

from calendar_converter.constants import (
    THIEN_CAN,
    DIA_CHI,
    EPOCH_2000,
    SYNODIC_MONTH,
    DR,
    PI
)


def jdn(d: int, m: int, y: int) -> int:
    """Tính số ngày Julius (Julian Day Number) từ ngày, tháng, năm Dương lịch."""
    a = (14 - m) // 12
    y2 = y + 4800 - a
    m2 = m + 12 * a - 3
    return d + ((153 * m2 + 2) // 5) + 365 * y2 + (y2 // 4) - (y2 // 100) + (y2 // 400) - 32045


def jd_to_date(jd: int) -> Tuple[int, int, int]:
    """Chuyển đổi số ngày Julius (JDN) ngược lại thành (ngày, tháng, năm) Dương lịch."""
    a = jd + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - ((153 * m + 2) // 5) + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + (m // 10)
    return day, month, year


def get_new_moon_day(k: int, time_zone: float = 7.0) -> int:
    """
    Tính số ngày Julius của ngày Sóc (New Moon - thời điểm mùng 1 âm lịch) thứ k tính từ năm 2000.
    
    Args:
        k: Chỉ số tuần trăng mới tính từ Epoch 2000.
        time_zone: Múi giờ địa phương (mặc định 7.0 cho Việt Nam).
        
    Returns:
        int: Julian Day Number của ngày có trăng mới (mùng 1 âm lịch).
    """
    T = k / 1236.85
    T2 = T * T
    T3 = T2 * T
    
    Jd1 = 2451550.09765 + SYNODIC_MONTH * k + 0.0001337 * T2 - 0.000000150 * T3 + 0.00000000073 * T3 * T
    M = 2.5534 + 29.10535669 * k - 0.0000218 * T2 - 0.00000011 * T3
    Mprime = 201.5643 + 385.81693528 * k + 0.0107438 * T2 + 0.00001239 * T3 - 0.000000058 * T3 * T
    F = 160.7108 + 390.67050274 * k - 0.0016341 * T2 - 0.00000227 * T3 + 0.000000011 * T3 * T
    
    # Hiệu chỉnh nhiễu loạn vị trí của mặt trăng và các hành tinh
    dJ = (
        (0.1734 - 0.000393 * T) * math.sin(M * DR)
        + 0.0021 * math.sin(2 * DR * M)
        - 0.4068 * math.sin(Mprime * DR)
        + 0.0161 * math.sin(2 * DR * Mprime)
        - 0.0004 * math.sin(3 * DR * Mprime)
        + 0.0104 * math.sin(2 * DR * F)
        - 0.0051 * math.sin((M + Mprime) * DR)
        - 0.0074 * math.sin((M - Mprime) * DR)
        + 0.0004 * math.sin((2 * F + M) * DR)
        - 0.0004 * math.sin((2 * F - M) * DR)
        - 0.0006 * math.sin((2 * F + Mprime) * DR)
        + 0.0010 * math.sin((2 * F - Mprime) * DR)
        + 0.0005 * math.sin((2 * Mprime + M) * DR)
    )
    Jd = Jd1 + dJ
    return math.floor(Jd + 0.5 + time_zone / 24.0)


def get_sun_longitude(jdn_val: int, time_zone: float = 7.0) -> int:
    """
    Tính kinh độ Mặt Trời (tương ứng với các cung / Trung khí trong năm).
    Mỗi cung tương đương 30 độ (trả về giá trị 0..11).
    """
    T = (jdn_val - 0.5 - time_zone / 24.0 - 2451545.0) / 36525.0
    T2 = T * T
    M = 357.52910 + 35999.05029 * T - 0.0001537 * T2
    C = (1.914602 - 0.004817 * T - 0.000014 * T2) * math.sin(M * DR) + (0.019993 - 0.000101 * T) * math.sin(2 * M * DR) + 0.000289 * math.sin(3 * M * DR)
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T2
    lambda_deg = (L0 + C) % 360.0
    return math.floor(lambda_deg / 30.0)


def get_lunar_month_11(yy: int, time_zone: float = 7.0) -> int:
    """
    Tìm ngày bắt đầu của tháng 11 âm lịch (tháng chứa Đông chí) của năm yy.
    """
    off = jdn(31, 12, yy) - EPOCH_2000
    k = math.floor(off / SYNODIC_MONTH)
    nm = get_new_moon_day(k, time_zone)
    sun_long = get_sun_longitude(nm, time_zone)
    if sun_long >= 9:
        nm = get_new_moon_day(k - 1, time_zone)
    return nm


def get_leap_month_offset(a11: int, time_zone: float = 7.0) -> int:
    """
    Xác định vị trí tháng nhuận sau tháng 11 âm lịch theo nguyên lý:
    Tháng âm lịch đầu tiên không chứa Trung khí (kinh độ Mặt Trời không đổi cung) là tháng nhuận.
    """
    k = math.floor((a11 - EPOCH_2000) / SYNODIC_MONTH + 0.5)
    arc = get_sun_longitude(a11, time_zone)
    i = 1
    while True:
        k += 1
        d = get_new_moon_day(k, time_zone)
        new_arc = get_sun_longitude(d, time_zone)
        if new_arc == arc:
            return i - 1
        arc = new_arc
        i += 1
        if arc == 8 or i > 14:
            break
    return 0


def xac_dinh_gio_sinh_theo_canh_gio(gio: int, phut: int = 0) -> Dict[str, Any]:
    """
    Xác định canh giờ Can Chi từ giờ/phút sinh hiện đại (0-23h).
    
    Quy tắc đặc biệt quan trọng:
    - Mỗi giờ Can Chi = 2 giờ hiện đại (Tý: 23h-1h, Sửu: 1h-3h,...).
    - Khung giờ 23h00 - 23h59 đêm thuộc GIỜ TÝ CỦA NGÀY HÔM SAU theo lịch phương Đông.
    - Khung giờ 00h00 - 00h59 sáng cũng thuộc GIỜ TÝ (đầu ngày hôm đó).
    
    Args:
        gio: Giờ sinh (0-23).
        phut: Phút sinh (0-59).
        
    Returns:
        dict: {
            "ten_gio_can_chi": "Tý",
            "chi_gio": "Tý",
            "chi_gio_idx": 0,
            "chuyen_sang_ngay_hom_sau": True/False
        }
    """
    if not (0 <= gio <= 23):
        raise ValueError(f"Giờ sinh ({gio}) không hợp lệ, phải nằm trong khoảng 0 đến 23.")
    if not (0 <= phut <= 59):
        raise ValueError(f"Phút sinh ({phut}) không hợp lệ, phải nằm trong khoảng 0 đến 59.")

    total_minutes = gio * 60 + phut

    # Khung giờ 23h00 đến 23h59: Giờ Tý của ngày hôm sau
    if total_minutes >= 1380:
        return {
            "ten_gio_can_chi": "Tý",
            "chi_gio": "Tý",
            "chi_gio_idx": 0,
            "chuyen_sang_ngay_hom_sau": True
        }
    elif total_minutes < 60:
        # Khung giờ 00h00 đến 00h59: Giờ Tý của ngày hiện tại
        return {
            "ten_gio_can_chi": "Tý",
            "chi_gio": "Tý",
            "chi_gio_idx": 0,
            "chuyen_sang_ngay_hom_sau": False
        }
    else:
        chi_idx = ((gio + 1) // 2) % 12
        ten_chi = DIA_CHI[chi_idx]
        return {
            "ten_gio_can_chi": ten_chi,
            "chi_gio": ten_chi,
            "chi_gio_idx": chi_idx,
            "chuyen_sang_ngay_hom_sau": False
        }


def solar_to_lunar(ngay: int, thang: int, nam: int, gio: int = 12, mui_gio: int = 7) -> Dict[str, Any]:
    """
    Chuyển đổi ngày Dương lịch sang Âm lịch và xác định đầy đủ Can Chi năm, tháng, ngày.
    
    Lưu ý về giờ sinh:
    - Nếu sinh từ 23h00 đến 23h59, theo quy tắc phương Đông sẽ được tính vào giờ Tý của NGÀY HÔM SAU.
    
    Args:
        ngay: Ngày Dương lịch (1-31).
        thang: Tháng Dương lịch (1-12).
        nam: Năm Dương lịch.
        gio: Giờ sinh (0-23, mặc định 12h trưa).
        mui_gio: Múi giờ địa phương (mặc định GMT+7).
        
    Returns:
        dict: {
            "ngay_am": int,
            "thang_am": int,
            "nam_am": int,
            "la_thang_nhuan": bool,
            "can_nam": str,
            "chi_nam": str,
            "can_thang": str,
            "chi_thang": str,
            "can_ngay": str,
            "chi_ngay": str,
            "ten_gio": str
        }
    """
    # 1. Rà soát tính hợp lệ của ngày tháng Dương lịch
    try:
        date(nam, thang, ngay)
    except ValueError as e:
        raise ValueError(f"Ngày Dương lịch {ngay}/{thang}/{nam} không tồn tại hoặc không hợp lệ: {str(e)}")

    if not (0 <= gio <= 23):
        raise ValueError(f"Giờ ({gio}) không hợp lệ, phải nằm trong khoảng 0-23.")

    # 2. Xử lý quy tắc chuyển ngày nếu sinh trong giờ Tý đêm (23h00 - 24h00)
    info_gio = xac_dinh_gio_sinh_theo_canh_gio(gio, 0)
    cal_day, cal_month, cal_year = ngay, thang, nam
    if info_gio["chuyen_sang_ngay_hom_sau"]:
        cal_day, cal_month, cal_year = jd_to_date(jdn(ngay, thang, nam) + 1)

    # 3. Tính toán Âm lịch theo thuật toán thiên văn
    day_number = jdn(cal_day, cal_month, cal_year)
    k = math.floor((day_number - EPOCH_2000) / SYNODIC_MONTH)
    month_start = get_new_moon_day(k + 1, float(mui_gio))
    if month_start > day_number:
        month_start = get_new_moon_day(k, float(mui_gio))
    else:
        k += 1

    a11 = get_lunar_month_11(cal_year, float(mui_gio))
    b11 = a11
    if a11 >= month_start:
        lunar_year = cal_year
        a11 = get_lunar_month_11(cal_year - 1, float(mui_gio))
    else:
        lunar_year = cal_year + 1
        b11 = get_lunar_month_11(cal_year + 1, float(mui_gio))

    lunar_day = day_number - month_start + 1
    diff = math.floor((month_start - a11) / 29.0)
    lunar_leap = False
    lunar_month = diff + 11

    if (b11 - a11) > 365:
        leap_month_diff = get_leap_month_offset(a11, float(mui_gio))
        if diff >= leap_month_diff:
            lunar_month = diff + 10
            if diff == leap_month_diff:
                lunar_leap = True

    if lunar_month > 12:
        lunar_month -= 12
    if lunar_month >= 11 and diff < 4:
        lunar_year -= 1

    # 4. Tính Can Chi Năm
    can_nam_idx = (lunar_year + 6) % 10
    chi_nam_idx = (lunar_year + 8) % 12
    can_nam = THIEN_CAN[can_nam_idx]
    chi_nam = DIA_CHI[chi_nam_idx]

    # 5. Tính Can Chi Tháng (theo quy tắc Ngũ Hổ Độn)
    # Tháng 1 luôn là Dần (index 2)
    can_thang_1 = (can_nam_idx % 5 * 2 + 2) % 10
    can_thang_idx = (can_thang_1 + lunar_month - 1) % 10
    chi_thang_idx = (2 + lunar_month - 1) % 12
    can_thang = THIEN_CAN[can_thang_idx]
    chi_thang = DIA_CHI[chi_thang_idx]

    # 6. Tính Can Chi Ngày (theo Julian Day Number)
    can_ngay_idx = (day_number + 9) % 10
    chi_ngay_idx = (day_number + 1) % 12
    can_ngay = THIEN_CAN[can_ngay_idx]
    chi_ngay = DIA_CHI[chi_ngay_idx]

    return {
        "ngay_am": lunar_day,
        "thang_am": lunar_month,
        "nam_am": lunar_year,
        "la_thang_nhuan": lunar_leap,
        "can_nam": can_nam,
        "chi_nam": chi_nam,
        "can_thang": can_thang,
        "chi_thang": chi_thang,
        "can_ngay": can_ngay,
        "chi_ngay": chi_ngay,
        "ten_gio": info_gio["ten_gio_can_chi"]
    }


def lunar_to_solar(ngay_am: int, thang_am: int, nam_am: int, la_thang_nhuan: bool = False, mui_gio: int = 7) -> Dict[str, int]:
    """
    Chuyển đổi từ ngày Âm lịch sang ngày Dương lịch tương ứng.
    
    Args:
        ngay_am: Ngày Âm lịch (1-30).
        thang_am: Tháng Âm lịch (1-12).
        nam_am: Năm Âm lịch.
        la_thang_nhuan: True nếu là tháng nhuận, False nếu là tháng chính.
        mui_gio: Múi giờ (mặc định 7).
        
    Returns:
        dict: {"ngay": int, "thang": int, "nam": int}
        
    Raises:
        ValueError: Nếu ngày/tháng âm lịch không hợp lệ hoặc tháng nhuận không tồn tại.
    """
    if not (1 <= thang_am <= 12):
        raise ValueError(f"Tháng âm lịch ({thang_am}) không hợp lệ, phải nằm trong khoảng 1-12.")
    if not (1 <= ngay_am <= 30):
        raise ValueError(f"Ngày âm lịch ({ngay_am}) không hợp lệ, phải nằm trong khoảng 1-30.")

    tz = float(mui_gio)
    if thang_am < 11:
        a11 = get_lunar_month_11(nam_am - 1, tz)
        b11 = get_lunar_month_11(nam_am, tz)
    else:
        a11 = get_lunar_month_11(nam_am, tz)
        b11 = get_lunar_month_11(nam_am + 1, tz)

    off = thang_am - 11
    if off < 0:
        off += 12

    if (b11 - a11) > 365:
        leap_off = get_leap_month_offset(a11, tz)
        leap_month = leap_off - 2
        if leap_month < 0:
            leap_month += 12

        if la_thang_nhuan:
            if thang_am != leap_month:
                raise ValueError(f"Năm âm lịch {nam_am} không có tháng {thang_am} nhuận (tháng nhuận năm này là tháng {leap_month}).")
            off += 1
        elif off >= leap_off:
            off += 1
    else:
        if la_thang_nhuan:
            raise ValueError(f"Năm âm lịch {nam_am} là năm thường, không có tháng nhuận nào.")

    k = math.floor(0.5 + (a11 - EPOCH_2000) / SYNODIC_MONTH)
    month_start = get_new_moon_day(k + off, tz)
    next_month_start = get_new_moon_day(k + off + 1, tz)
    so_ngay_trong_thang = next_month_start - month_start

    if ngay_am > so_ngay_trong_thang:
        raise ValueError(f"Tháng {thang_am}{' nhuận' if la_thang_nhuan else ''} năm {nam_am} chỉ có {so_ngay_trong_thang} ngày (tháng thiếu), không có ngày {ngay_am}.")

    d, m, y = jd_to_date(month_start + ngay_am - 1)
    return {
        "ngay": d,
        "thang": m,
        "nam": y
    }


# ==============================================================================
# BÁT TỰ TỬ BÌNH - XÁC ĐỊNH 12 NGUYỆT LỆNH THEO LỊCH TIẾT KHÍ (BƯỚC 0 & 0b)
# Căn cứ: Sách "Dự Báo Theo Tử Bình" - Trần Khang Ninh (2006), trang 15, 58-60.
# ==============================================================================

TIET_12_CHINH = [
    {"ten": "Lập Xuân", "kinh_do": 315.0, "chi": "Dần", "thang_idx": 1},
    {"ten": "Kinh Trập", "kinh_do": 345.0, "chi": "Mão", "thang_idx": 2},
    {"ten": "Thanh Minh", "kinh_do": 15.0,  "chi": "Thìn", "thang_idx": 3},
    {"ten": "Lập Hạ",    "kinh_do": 45.0,  "chi": "Tỵ",  "thang_idx": 4},
    {"ten": "Mang Chủng", "kinh_do": 75.0,  "chi": "Ngọ", "thang_idx": 5},
    {"ten": "Tiểu Thử",  "kinh_do": 105.0, "chi": "Mùi", "thang_idx": 6},
    {"ten": "Lập Thu",   "kinh_do": 135.0, "chi": "Thân", "thang_idx": 7},
    {"ten": "Bạch Lộ",   "kinh_do": 165.0, "chi": "Dậu", "thang_idx": 8},
    {"ten": "Hàn Lộ",    "kinh_do": 195.0, "chi": "Tuất", "thang_idx": 9},
    {"ten": "Lập Đông",  "kinh_do": 225.0, "chi": "Hợi", "thang_idx": 10},
    {"ten": "Đại Tuyết", "kinh_do": 255.0, "chi": "Tý",  "thang_idx": 11},
    {"ten": "Tiểu Hàn",  "kinh_do": 285.0, "chi": "Sửu", "thang_idx": 12},
]


def tinh_kinh_do_mat_troi_chinh_xac(dt_utc: datetime) -> float:
    """Tính kinh độ hoàng đạo Mặt Trời (độ 0..360) tại thời khắc UTC chuẩn xác theo Jean Meeus."""
    epoch_2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    diff_days = (dt_utc - epoch_2000).total_seconds() / 86400.0
    jd = 2451545.0 + diff_days
    T = (jd - 2451545.0) / 36525.0
    M = 357.52910 + 35999.05029 * T - 0.0001537 * T * T
    C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M * DR) + (0.019993 - 0.000101 * T) * math.sin(2 * M * DR) + 0.000289 * math.sin(3 * M * DR)
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
    return (L0 + C) % 360.0


def tim_thoi_diem_tiet_khi(target_deg: float, approx_dt_utc: datetime) -> datetime:
    """Dùng phương pháp chia đôi tìm thời khắc đạt kinh độ tiết khí chính xác đến phút."""
    t_start = approx_dt_utc - timedelta(days=7)
    t_end = approx_dt_utc + timedelta(days=7)
    for _ in range(50):
        t_mid = t_start + (t_end - t_start) / 2
        deg = tinh_kinh_do_mat_troi_chinh_xac(t_mid)
        diff = (deg - target_deg + 180) % 360 - 180
        if diff < 0:
            t_start = t_mid
        else:
            t_end = t_mid
    return t_mid


def xac_dinh_tiet_khi_chuan(
    ngay: int, thang: int, nam: int,
    gio: int = 12, phut: int = 0,
    mui_gio: float = 7.0
) -> Dict[str, Any]:
    """
    Xác định tiết khí chính xác và Nguyệt Lệnh (Chi tháng Bát Tự) theo đúng Lịch Tiết Khí.
    """
    tz_local = timezone(timedelta(hours=mui_gio))
    dt_local = datetime(nam, thang, ngay, gio, phut, tzinfo=tz_local)
    dt_utc = dt_local.astimezone(timezone.utc)

    deg = tinh_kinh_do_mat_troi_chinh_xac(dt_utc)
    term_idx = int(((deg - 315.0) % 360.0) // 30)
    current_term = TIET_12_CHINH[term_idx]
    next_term = TIET_12_CHINH[(term_idx + 1) % 12]

    # Tìm thời điểm tiết khí trước và sau
    t_prev_utc = tim_thoi_diem_tiet_khi(current_term["kinh_do"], dt_utc - timedelta(days=15))
    t_next_utc = tim_thoi_diem_tiet_khi(next_term["kinh_do"], dt_utc + timedelta(days=15))

    t_prev_local = t_prev_utc.astimezone(tz_local)
    t_next_local = t_next_utc.astimezone(tz_local)

    dist_from_prev_days = (dt_utc - t_prev_utc).total_seconds() / 86400.0
    dist_to_next_days = (t_next_utc - dt_utc).total_seconds() / 86400.0

    return {
        "kinh_do_mat_troi": round(deg, 4),
        "tiet_hien_tai": current_term["ten"],
        "chi_thang": current_term["chi"],
        "thang_idx": current_term["thang_idx"],
        "tiet_ke_tiep": next_term["ten"],
        "thoi_diem_tiet_truoc": t_prev_local.strftime("%Y-%m-%d %H:%M"),
        "thoi_diem_tiet_ke_tiep": t_next_local.strftime("%Y-%m-%d %H:%M"),
        "khoang_cach_ngay_tu_tiet_truoc": round(dist_from_prev_days, 2),
        "khoang_cach_ngay_toi_tiet_ke_tiep": round(dist_to_next_days, 2),
        "raw_dist_prev_days": dist_from_prev_days,
        "raw_dist_next_days": dist_to_next_days,
    }


def xac_dinh_can_chi_thang_tiet_khi(
    nam_can: str,
    ngay_duong: int, thang_duong: int, nam_duong: int,
    gio_sinh: int = 12, phut_sinh: int = 0,
    mui_gio: float = 7.0
) -> Dict[str, Any]:
    """
    Xác định Can Chi tháng sinh theo đúng 100% LỊCH TIẾT KHÍ và quy tắc Ngũ Hổ Độn.
    """
    tiet_info = xac_dinh_tiet_khi_chuan(ngay_duong, thang_duong, nam_duong, gio_sinh, phut_sinh, mui_gio)
    chi_thang = tiet_info["chi_thang"]
    thang_idx = tiet_info["thang_idx"]  # 1=Dần, 2=Mão, 3=Thìn, 4=Tỵ...

    can_nam_idx = THIEN_CAN.index(nam_can)
    can_thang_1_idx = (can_nam_idx % 5 * 2 + 2) % 10
    can_thang_idx = (can_thang_1_idx + thang_idx - 1) % 10

    return {
        "can": THIEN_CAN[can_thang_idx],
        "chi": chi_thang,
        "tiet_khi": tiet_info["tiet_hien_tai"],
        "chi_tiet": f"Nguyệt lệnh {chi_thang} khởi từ tiết {tiet_info['tiet_hien_tai']}"
    }


def xac_dinh_can_chi_nam_tiet_khi(
    ngay_duong: int, thang_duong: int, nam_duong: int,
    gio_sinh: int = 12, phut_sinh: int = 0,
    mui_gio: float = 7.0
) -> Dict[str, Any]:
    """
    Xác định Can Chi năm sinh theo Lập Xuân (tiết 315 độ).
    Nếu sinh trước Lập Xuân thì tính theo năm trước (nam_duong - 1).
    """
    tz_local = timezone(timedelta(hours=mui_gio))
    dt_local = datetime(nam_duong, thang_duong, ngay_duong, gio_sinh, phut_sinh, tzinfo=tz_local)
    dt_utc = dt_local.astimezone(timezone.utc)
    t_lap_xuan_utc = tim_thoi_diem_tiet_khi(315.0, datetime(nam_duong, 2, 4, 12, 0, tzinfo=timezone.utc))

    nam_tinh = nam_duong if dt_utc >= t_lap_xuan_utc else (nam_duong - 1)
    can_idx = (nam_tinh + 6) % 10
    chi_idx = (nam_tinh + 8) % 12
    return {
        "can": THIEN_CAN[can_idx],
        "chi": DIA_CHI[chi_idx],
        "nam_tinh": nam_tinh
    }


def kiem_tra_vung_bien_4_tru(
    nam_duong: int, thang_duong: int, ngay_duong: int,
    gio_sinh: int = 12, phut_sinh: int = 0,
    mui_gio: float = 7.0
) -> Dict[str, Any]:
    """
    BƯỚC 0b: Khái quát hóa kiểm tra vùng biên rủi ro cho cả 4 Trụ (Năm, Tháng, Ngày, Giờ).
    """
    tz_local = timezone(timedelta(hours=mui_gio))
    dt_local = datetime(nam_duong, thang_duong, ngay_duong, gio_sinh, phut_sinh, tzinfo=tz_local)
    dt_utc = dt_local.astimezone(timezone.utc)

    # 1. TRỤ NĂM (Ranh giới Lập Xuân 315 độ)
    t_lap_xuan_utc = tim_thoi_diem_tiet_khi(315.0, datetime(nam_duong, 2, 4, 12, 0, tzinfo=timezone.utc))
    t_lap_xuan_local = t_lap_xuan_utc.astimezone(tz_local)
    dist_lap_xuan_days = (dt_utc - t_lap_xuan_utc).total_seconds() / 86400.0

    nam_vung_bien = abs(dist_lap_xuan_days) <= 3.0
    nam_status = "VÙNG BIÊN (Cách Lập Xuân <= 3 ngày)" if nam_vung_bien else "An toàn"
    nam_desc = f"Lập Xuân năm {nam_duong} lúc {t_lap_xuan_local.strftime('%H:%M ngày %d/%m/%Y')}. Cách giờ sinh {abs(dist_lap_xuan_days):.1f} ngày."

    # 2. TRỤ THÁNG (Ranh giới 12 tiết)
    tiet_info = xac_dinh_tiet_khi_chuan(ngay_duong, thang_duong, nam_duong, gio_sinh, phut_sinh, mui_gio)
    min_dist_month_days = min(tiet_info["raw_dist_prev_days"], tiet_info["raw_dist_next_days"])
    thang_vung_bien = min_dist_month_days <= 2.0
    thang_status = "VÙNG BIÊN (Cách mốc đổi tiết <= 2 ngày)" if thang_vung_bien else "An toàn"
    thang_desc = (
        f"Nằm giữa tiết {tiet_info['tiet_hien_tai']} ({tiet_info['thoi_diem_tiet_truoc']}) "
        f"và {tiet_info['tiet_ke_tiep']} ({tiet_info['thoi_diem_tiet_ke_tiep']}). "
        f"Cách tiết trước {tiet_info['khoang_cach_ngay_tu_tiet_truoc']} ngày, cách tiết sau {tiet_info['khoang_cach_ngay_toi_tiet_ke_tiep']} ngày."
    )

    # 3. TRỤ NGÀY (Chu kỳ 60 ngày, ranh giới giờ Tý 23h-24h)
    ngay_vung_bien = (gio_sinh == 23 or (gio_sinh == 0 and phut_sinh < 60))
    ngay_status = "VÙNG BIÊN (Giờ Tý sớm/muộn 23h00-00h59)" if ngay_vung_bien else "An toàn"
    ngay_desc = (
        "Giờ sinh thuộc khung 23h-24h (áp dụng quy ước Tý đổi ngày mới phương Đông)" if gio_sinh == 23
        else "Chu kỳ 60 ngày liên tục, không phụ thuộc tiết khí, an toàn."
    )

    # 4. TRỤ GIỜ (Khung 2 tiếng, cảnh báo nếu cách ranh giới <= 10 phút)
    min_total = gio_sinh * 60 + phut_sinh
    moc_gio = [60, 180, 300, 420, 540, 660, 780, 900, 1020, 1140, 1260, 1380]
    min_dist_hour = min(abs(min_total - m) for m in moc_gio)
    gio_vung_bien = min_dist_hour <= 10
    gio_status = f"VÙNG BIÊN (Cách ranh giới khung giờ {min_dist_hour} phút)" if gio_vung_bien else "An toàn"
    gio_desc = f"Cách ranh giới chuyển chi giờ gần nhất {min_dist_hour} phút."

    return {
        "tru_nam": {"trang_thai": nam_status, "la_vung_bien": nam_vung_bien, "chi_tiet": nam_desc},
        "tru_thang": {"trang_thai": thang_status, "la_vung_bien": thang_vung_bien, "chi_tiet": thang_desc},
        "tru_ngay": {"trang_thai": ngay_status, "la_vung_bien": ngay_vung_bien, "chi_tiet": ngay_desc},
        "tru_gio": {"trang_thai": gio_status, "la_vung_bien": gio_vung_bien, "chi_tiet": gio_desc},
        "co_tru_nao_vung_bien": any([nam_vung_bien, thang_vung_bien, ngay_vung_bien, gio_vung_bien]),
        "tiet_khi": tiet_info
    }


def tinh_tuoi_khoi_van_chuan(
    ngay_duong: int, thang_duong: int, nam_duong: int,
    gio_sinh: int, phut_sinh: int,
    di_thuan: bool,
    mui_gio: float = 7.0
) -> int:
    """
    Tính tuổi khởi vận theo sách Trần Khang Ninh (tr.58-60):
    - Đếm số ngày thực tế từ giờ sinh đến tiết kế tiếp (nếu thuận) hoặc tiết trước (nếu nghịch).
    - Chia cho 3, lấy phần nguyên (floor), bỏ số dư.
    """
    tiet_info = xac_dinh_tiet_khi_chuan(ngay_duong, thang_duong, nam_duong, gio_sinh, phut_sinh, mui_gio)
    so_ngay = tiet_info["raw_dist_next_days"] if di_thuan else tiet_info["raw_dist_prev_days"]
    tuoi = math.floor(so_ngay / 3.0)
    return max(1, int(tuoi))

