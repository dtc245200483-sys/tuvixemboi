# -*- coding: utf-8 -*-
"""
Module chuyển đổi Dương lịch <-> Âm lịch và xác định Can Chi chính xác
theo thuật toán thiên văn chuẩn cho múi giờ Việt Nam (GMT+7).

Các thuật toán dựa trên nghiên cứu thiên văn của Jean Meeus và tác giả Hồ Ngọc Đức,
xử lý chính xác từng ngày Sóc (New Moon), Trung khí và quy tắc tháng nhuận.
"""

import math
from datetime import date
from typing import Dict, Any, Tuple

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
