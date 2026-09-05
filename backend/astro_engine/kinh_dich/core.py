# -*- coding: utf-8 -*-
"""
Module lõi thuật toán Kinh Dịch: gieo quẻ 3 đồng xu, gieo quẻ Mai Hoa Dịch Số theo thời gian,
xác định quẻ chính, tìm hào động và suy diễn quẻ biến.
Logic toán học thuần túy, không dùng AI, đảm bảo chuẩn xác và tái lặp được khi cần kiểm thử.

Tham khảo chính:
- Chu Dịch Bản Nghĩa (Chu Hy)
- Mai Hoa Dịch Số Toàn Thư (Thiệu Khang Tiết)
"""

import random
from typing import List, Dict, Any, Optional

from astro_engine.kinh_dich.constants import (
    BAT_QUAI,
    BAT_QUAI_BY_NAME,
    QUE_64,
    QUE_BY_CODE,
    QUE_BY_STT
)
from calendar_converter.lunar_calendar import solar_to_lunar

# Địa Chi gắn với số thứ tự 1-12 trong Mai Hoa Dịch Số
CHI_TO_NUMBER = {
    "Tý": 1, "Sửu": 2, "Dần": 3, "Mão": 4, "Thìn": 5, "Tỵ": 6,
    "Ngọ": 7, "Mùi": 8, "Thân": 9, "Dậu": 10, "Tuất": 11, "Hợi": 12
}


def gieo_que_dong_xu(seed: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    1. Mô phỏng phương pháp gieo 3 đồng xu cổ truyền, lặp lại 6 lần từ hào 1 (dưới) lên hào 6 (trên).
    
    Quy tắc 3 đồng xu:
    - Mặt Sấp (Âm) = 2 điểm, Mặt Ngửa (Dương) = 3 điểm.
    - 3 Sấp = 6 điểm: Lão Âm (giá trị 0, Hào Động -> biến thành Dương).
    - 2 Sấp + 1 Ngửa = 7 điểm: Thiếu Dương (giá trị 1, Tĩnh).
    - 1 Sấp + 2 Ngửa = 8 điểm: Thiếu Âm (giá trị 0, Tĩnh).
    - 3 Ngửa = 9 điểm: Lão Dương (giá trị 1, Hào Động -> biến thành Âm).
    
    Args:
        seed: int tùy chọn. Nếu truyền seed thì kết quả là xác định (dùng cho test).
              Nếu không truyền (mặc định), dùng ngẫu nhiên thực tế (production).
    """
    rng = random.Random(seed) if seed is not None else random.Random()
    danh_sach_hao = []

    for vi_tri in range(1, 7):
        # Tung 3 đồng xu: mỗi xu nhận 2 (sấp) hoặc 3 (ngửa) với xác suất 50%
        coin1 = rng.choice([2, 3])
        coin2 = rng.choice([2, 3])
        coin3 = rng.choice([2, 3])
        tong_diem = coin1 + coin2 + coin3

        if tong_diem == 6:
            ten_hao = "Lão Âm"
            gia_tri = 0
            la_hao_dong = True
        elif tong_diem == 7:
            ten_hao = "Thiếu Dương"
            gia_tri = 1
            la_hao_dong = False
        elif tong_diem == 8:
            ten_hao = "Thiếu Âm"
            gia_tri = 0
            la_hao_dong = False
        else:  # 9
            ten_hao = "Lão Dương"
            gia_tri = 1
            la_hao_dong = True

        danh_sach_hao.append({
            "vi_tri": vi_tri,
            "tong_diem": tong_diem,
            "ten_hao": ten_hao,
            "gia_tri": gia_tri,
            "la_hao_dong": la_hao_dong
        })

    return danh_sach_hao


def gieo_que_theo_thoi_gian(
    ngay_duong: int,
    thang_duong: int,
    nam_duong: int,
    gio_chi: str
) -> List[Dict[str, Any]]:
    """
    2. Phương pháp gieo quẻ theo Mai Hoa Dịch Số (Thiệu Khang Tiết).
    Dựa trên ngày, tháng, năm âm lịch và giờ chi (lấy từ module calendar_converter):
    
    Công thức kinh điển:
    - Thượng quái: (Chi Năm + Tháng ÂL + Ngày ÂL) % 8 (dư 0 lấy 8: Khôn).
    - Hạ quái:     (Chi Năm + Tháng ÂL + Ngày ÂL + Chi Giờ) % 8 (dư 0 lấy 8: Khôn).
    - Hào động:    (Chi Năm + Tháng ÂL + Ngày ÂL + Chi Giờ) % 6 (dư 0 lấy 6: Hào 6 động).
    
    Quy ước Bát Quái Tiên Thiên:
    1: Càn, 2: Đoài, 3: Ly, 4: Chấn, 5: Tốn, 6: Khảm, 7: Cấn, 8: Khôn.
    """
    if gio_chi not in CHI_TO_NUMBER:
        raise ValueError(f"Chi giờ '{gio_chi}' không hợp lệ.")

    # 1. Chuyển đổi Dương lịch -> Âm lịch
    lunar = solar_to_lunar(ngay_duong, thang_duong, nam_duong)
    chi_nam = lunar["chi_nam"]
    chi_nam_so = CHI_TO_NUMBER[chi_nam]
    thang_am = lunar["thang_am"]
    ngay_am = lunar["ngay_am"]
    gio_so = CHI_TO_NUMBER[gio_chi]

    # 2. Tính toán Thượng Quái, Hạ Quái và Hào Động
    tong_thuong = chi_nam_so + thang_am + ngay_am
    thuong_so = (tong_thuong % 8) or 8

    tong_ha = tong_thuong + gio_so
    ha_so = (tong_ha % 8) or 8

    hao_dong_pos = (tong_ha % 6) or 6

    # 3. Ghép 6 hào: Hạ quái (hào 1, 2, 3), Thượng quái (hào 4, 5, 6)
    ha_quai = BAT_QUAI[ha_so]
    thuong_quai = BAT_QUAI[thuong_so]

    # Hao list: 3 hào hạ quái rồi 3 hào thượng quái
    cac_hao = ha_quai["hao"] + thuong_quai["hao"]

    danh_sach_hao = []
    for i, val in enumerate(cac_hao, start=1):
        is_dong = (i == hao_dong_pos)
        if is_dong:
            ten_hao = "Lão Dương" if val == 1 else "Lão Âm"
            tong_diem = 9 if val == 1 else 6
        else:
            ten_hao = "Thiếu Dương" if val == 1 else "Thiếu Âm"
            tong_diem = 7 if val == 1 else 8

        danh_sach_hao.append({
            "vi_tri": i,
            "tong_diem": tong_diem,
            "ten_hao": ten_hao,
            "gia_tri": val,
            "la_hao_dong": is_dong
        })

    return danh_sach_hao


def xac_dinh_que_tu_hao(danh_sach_hao: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    3. Từ 6 hào đã gieo, xác định quẻ chính và danh sách hào động.
    """
    if len(danh_sach_hao) != 6:
        raise ValueError(f"Danh sách hào phải có đúng 6 phần tử, hiện có {len(danh_sach_hao)}.")

    code = "".join(str(h["gia_tri"]) for h in danh_sach_hao)
    que_info = QUE_BY_CODE.get(code)
    if not que_info:
        raise ValueError(f"Mã nhị phân '{code}' không tìm thấy trong bảng 64 quẻ.")

    hao_dong = [h["vi_tri"] for h in danh_sach_hao if h["la_hao_dong"]]

    return {
        "que_chinh": que_info,
        "hao_dong": hao_dong,
        "ma_nhi_phan": code
    }


def tinh_que_bien(que_chinh: Dict[str, Any], hao_dong: List[int]) -> Optional[Dict[str, Any]]:
    """
    4. Xác định quẻ biến.
    Nếu có hào động, đảo ngược giá trị Âm (0) <-> Dương (1) tại đúng vị trí hào đó.
    Nếu không có hào động nào (quẻ tĩnh), trả về None.
    """
    if not hao_dong:
        return None

    code_chars = list(que_chinh["ma_nhi_phan"])
    for pos in hao_dong:
        if not (1 <= pos <= 6):
            raise ValueError(f"Vị trí hào động {pos} không hợp lệ (phải từ 1 đến 6).")
        idx = pos - 1
        # Đảo ngược bit: 0 -> 1, 1 -> 0
        code_chars[idx] = "0" if code_chars[idx] == "1" else "1"

    code_bien = "".join(code_chars)
    que_bien_info = QUE_BY_CODE.get(code_bien)
    if not que_bien_info:
        raise ValueError(f"Mã quẻ biến '{code_bien}' không tìm thấy trong bảng 64 quẻ.")

    return que_bien_info


def gieo_va_lap_que(phuong_phap: str = "dong_xu", **kwargs) -> Dict[str, Any]:
    """
    5. Hàm tổng hợp thực hiện gieo và lập quẻ Kinh Dịch hoàn chỉnh.
    
    Args:
        phuong_phap: 'dong_xu' hoặc 'theo_thoi_gian'
        kwargs:
            - Nếu 'dong_xu': seed (int, tùy chọn)
            - Nếu 'theo_thoi_gian': ngay_duong, thang_duong, nam_duong, gio_chi
            
    Returns:
        dict: {
            "phuong_phap": str,
            "danh_sach_hao": list,
            "que_chinh": dict,
            "hao_dong": list,
            "que_bien": dict hoặc None
        }
    """
    if phuong_phap == "dong_xu":
        seed = kwargs.get("seed")
        danh_sach_hao = gieo_que_dong_xu(seed=seed)
    elif phuong_phap == "theo_thoi_gian":
        danh_sach_hao = gieo_que_theo_thoi_gian(
            ngay_duong=kwargs["ngay_duong"],
            thang_duong=kwargs["thang_duong"],
            nam_duong=kwargs["nam_duong"],
            gio_chi=kwargs["gio_chi"]
        )
    else:
        raise ValueError(f"Phương pháp '{phuong_phap}' không hỗ trợ. Dùng 'dong_xu' hoặc 'theo_thoi_gian'.")

    res_chinh = xac_dinh_que_tu_hao(danh_sach_hao)
    que_chinh = res_chinh["que_chinh"]
    hao_dong = res_chinh["hao_dong"]
    que_bien = tinh_que_bien(que_chinh, hao_dong)

    return {
        "phuong_phap": phuong_phap,
        "danh_sach_hao": danh_sach_hao,
        "que_chinh": {
            "so_thu_tu": que_chinh["so_thu_tu"],
            "ten_que": que_chinh["ten_que"],
            "ma_nhi_phan": que_chinh["ma_nhi_phan"],
            "quai_tren": que_chinh["quai_tren"],
            "quai_duoi": que_chinh["quai_duoi"]
        },
        "hao_dong": hao_dong,
        "que_bien": {
            "so_thu_tu": que_bien["so_thu_tu"],
            "ten_que": que_bien["ten_que"],
            "ma_nhi_phan": que_bien["ma_nhi_phan"],
            "quai_tren": que_bien["quai_tren"],
            "quai_duoi": que_bien["quai_duoi"]
        } if que_bien else None
    }
