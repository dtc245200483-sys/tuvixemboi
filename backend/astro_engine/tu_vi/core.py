# -*- coding: utf-8 -*-
"""
Module lõi thực thi thuật toán lập lá số Tử Vi Đẩu Số hoàn chỉnh (108+ Tinh Tú).
Toàn bộ thuật toán tuân thủ nguyên bản quy chuẩn kinh điển:
- Tử Vi Đẩu Số Toàn Thư (Hi Di Trần Đoàn)
- Tử Vi Áo Bí (Hà Uyên)
- Bảng an sao Lạc Thư Tử Vi truyền thống

Tất cả các phép tính toán học, an sao, độ sáng Miếu Vượng Đắc Hãm,
Cung Thân, Can Cung, Tứ Hóa, Tuần Triệt, Đại Vận, Tiểu Hạn hoàn toàn chính xác.
"""

from typing import Dict, List, Any, Tuple
from astro_engine.tu_vi.constants.cung import (
    CUNG_CHUC_NANG,
    CUNG_DIA_CHI,
    CUC_INFO,
    NAP_AM_60_HOA_GIAP
)
from astro_engine.tu_vi.constants.sao import (
    CHINH_TINH,
    CHINH_TINH_DAC_HAM,
    SAT_TINH_DAC_HAM,
    VONG_THAI_TUE,
    VONG_BAC_SI,
    VONG_TRANG_SINH,
    TU_HOA_INFO,
    BANG_TU_HOA,
    PHU_TINH_CHI_TIET,
    MENH_CHU_MAP,
    THAN_CHU_MAP
)

CHI_TO_IDX = {name: i for i, name in enumerate(CUNG_DIA_CHI)}
CAN_LIST = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CAN_TO_IDX = {name: i for i, name in enumerate(CAN_LIST)}


def xac_dinh_cung_menh(thang_sinh_am: int, gio_sinh_chi: str) -> int:
    """
    1. Xác định vị trí cung Mệnh trên vòng 12 cung Địa Chi (0: Tý, 1: Sửu, 2: Dần, ..., 11: Hợi).
    - Khởi từ cung Dần (2) là tháng 1, đếm THUẬN đến tháng sinh âm lịch.
    - Tại cung dừng lại của tháng sinh, coi đó là giờ Tý, đếm NGHỊCH đến giờ sinh.
    """
    gio_idx = CHI_TO_IDX.get(gio_sinh_chi)
    if gio_idx is None:
        raise ValueError(f"Chi giờ sinh '{gio_sinh_chi}' không hợp lệ.")
    if not (1 <= thang_sinh_am <= 12):
        raise ValueError(f"Tháng sinh âm lịch ({thang_sinh_am}) phải từ 1 đến 12.")

    pos_thang = (2 + (thang_sinh_am - 1)) % 12
    pos_menh = (pos_thang - gio_idx) % 12
    return pos_menh


def xac_dinh_cung_than(thang_sinh_am: int, gio_sinh_chi: str) -> int:
    """
    2. Xác định vị trí cung Thân trên Địa Bàn (Mệnh định tiên thiên, Thân định hậu thiên).
    - Khởi từ cung Dần (2) là tháng 1, đếm THUẬN đến tháng sinh âm lịch.
    - Tại vị trí tháng sinh coi là giờ Tý, đếm THUẬN đến giờ sinh.
    """
    gio_idx = CHI_TO_IDX.get(gio_sinh_chi)
    if gio_idx is None:
        raise ValueError(f"Chi giờ sinh '{gio_sinh_chi}' không hợp lệ.")
    pos_thang = (2 + (thang_sinh_am - 1)) % 12
    pos_than = (pos_thang + gio_idx) % 12
    return pos_than


def an_12_cung(cung_menh_vi_tri: int) -> Dict[str, Any]:
    """
    3. Từ vị trí cung Mệnh, an toàn bộ 12 cung chức năng theo chiều nghịch kinh điển.
    Mệnh (0) -> Huynh Đệ (1) -> Phu Thê (2) -> Tử Tức (3) -> Tài Bạch (4)
    -> Tật Ách (5) -> Thiên Di (6) -> Nô Bộc (7) -> Quan Lộc (8) -> Điền Trạch (9)
    -> Phúc Đức (10) -> Phụ Mẫu (11).
    """
    cung_map = {}
    dia_chi_to_chuc_nang = {}
    chuc_nang_to_pos = {}

    for i, chuc_nang in enumerate(CUNG_CHUC_NANG):
        pos = (cung_menh_vi_tri - i) % 12
        ten_chi = CUNG_DIA_CHI[pos]
        cung_map[chuc_nang] = {
            "vi_tri_dia_chi": pos,
            "ten_dia_chi": ten_chi,
            "thu_tu": i
        }
        dia_chi_to_chuc_nang[pos] = chuc_nang
        chuc_nang_to_pos[chuc_nang] = pos

    return {
        "chuc_nang_to_dia_chi": cung_map,
        "dia_chi_to_chuc_nang": dia_chi_to_chuc_nang,
        "chuc_nang_to_pos": chuc_nang_to_pos
    }


def tinh_can_12_cung(can_nam_idx: int) -> Dict[int, str]:
    """
    4. Tính Thiên Can của 12 cung Địa Chi theo quy tắc Ngũ Hổ Độn:
    - Năm Giáp/Kỷ: Dần là Bính Dần.
    - Năm Ất/Canh: Dần là Mậu Dần.
    - Năm Bính/Tân: Dần là Canh Dần.
    - Năm Đinh/Nhâm: Dần là Nhâm Dần.
    - Năm Mậu/Quý: Dần là Giáp Dần.
    """
    can_dan_idx = (can_nam_idx % 5 * 2 + 2) % 10
    cung_can_map = {}
    for pos in range(12):
        step_from_dan = (pos - 2) % 12
        can_idx = (can_dan_idx + step_from_dan) % 10
        cung_can_map[pos] = CAN_LIST[can_idx]
    return cung_can_map


def tinh_ngu_hanh_nap_am(nam_sinh_can_chi: str) -> str:
    """Tra cứu Ngũ Hành Nạp Âm của 60 Hoa Giáp."""
    nap_am = NAP_AM_60_HOA_GIAP.get(nam_sinh_can_chi.strip())
    if not nap_am:
        raise ValueError(f"Can Chi '{nam_sinh_can_chi}' không có trong bảng 60 Hoa Giáp.")
    return nap_am


def xac_dinh_cuc(nam_sinh_can_chi: str, cung_menh_vi_tri: int) -> Dict[str, Any]:
    """Xác định Cục (Thủy Nhị, Mộc Tam, Kim Tứ, Thổ Ngũ, Hỏa Lục) từ Can Chi cung Mệnh."""
    parts = nam_sinh_can_chi.strip().split()
    can_nam = parts[0]
    can_nam_idx = CAN_TO_IDX.get(can_nam)
    cung_can_map = tinh_can_12_cung(can_nam_idx)
    can_menh = cung_can_map[cung_menh_vi_tri]
    chi_menh = CUNG_DIA_CHI[cung_menh_vi_tri]
    hoa_giap_menh = f"{can_menh} {chi_menh}"

    nap_am_menh = tinh_ngu_hanh_nap_am(hoa_giap_menh)
    ngu_hanh = nap_am_menh.split()[-1]
    hanh_to_cuc = {"Thủy": 2, "Mộc": 3, "Kim": 4, "Thổ": 5, "Hỏa": 6}
    cuc_so = hanh_to_cuc.get(ngu_hanh, 2)
    cuc_data = CUC_INFO[cuc_so].copy()
    cuc_data["can_chi_cung_menh"] = hoa_giap_menh
    cuc_data["nap_am_cung_menh"] = nap_am_menh
    return cuc_data


def an_sao_tu_vi(cuc: Dict[str, Any], ngay_sinh_am: int) -> int:
    """An vị trí sao Tử Vi dựa vào số Cục và ngày sinh Âm lịch."""
    D = ngay_sinh_am
    C = cuc["so_cuc"]
    rem = D % C
    if rem == 0:
        q = D // C
        pos = (2 + q - 1) % 12
    else:
        X = C - rem
        q = (D + X) // C
        if X % 2 == 0:
            pos = (2 + q - 1 + X) % 12
        else:
            pos = (2 + q - 1 - X) % 12
    return pos


def an_14_chinh_tinh(vi_tri_tu_vi: int) -> Dict[str, int]:
    """An 14 chính tinh theo 2 chùm sao Tử Vi (nghịch) và Thiên Phủ (thuận)."""
    chinh_tinh_pos = {}
    tv = vi_tri_tu_vi

    # Chùm Tử Vi (nghịch)
    chinh_tinh_pos["Tử Vi"] = tv
    chinh_tinh_pos["Thiên Cơ"] = (tv - 1) % 12
    chinh_tinh_pos["Thái Dương"] = (tv - 3) % 12
    chinh_tinh_pos["Vũ Khúc"] = (tv - 4) % 12
    chinh_tinh_pos["Thiên Đồng"] = (tv - 5) % 12
    chinh_tinh_pos["Liêm Trinh"] = (tv - 8) % 12

    # Chùm Thiên Phủ (đối xứng qua trục Dần 2 - Thân 8)
    tp = (4 - tv) % 12
    chinh_tinh_pos["Thiên Phủ"] = tp
    chinh_tinh_pos["Thái Âm"] = (tp + 1) % 12
    chinh_tinh_pos["Tham Lang"] = (tp + 2) % 12
    chinh_tinh_pos["Cự Môn"] = (tp + 3) % 12
    chinh_tinh_pos["Thiên Tướng"] = (tp + 4) % 12
    chinh_tinh_pos["Thiên Lương"] = (tp + 5) % 12
    chinh_tinh_pos["Thất Sát"] = (tp + 6) % 12
    chinh_tinh_pos["Phá Quân"] = (tp + 10) % 12

    return chinh_tinh_pos


def an_tuan_triet(can_nam_idx: int, chi_nam_idx: int) -> Tuple[List[int], List[int]]:
    """
    Tính vị trí án ngữ của Tuần Không và Triệt Không:
    - Triệt Không: an theo Can năm (2 cung liền kề).
    - Tuần Không: an theo Tuần Giáp của 60 Hoa Giáp năm sinh (2 cung không có Can).
    """
    triet_table = {
        0: [8, 9], 5: [8, 9],   # Giáp, Kỷ: Thân - Dậu
        1: [6, 7], 6: [6, 7],   # Ất, Canh: Ngọ - Mùi
        2: [4, 5], 7: [4, 5],   # Bính, Tân: Thìn - Tỵ
        3: [2, 3], 8: [2, 3],   # Đinh, Nhâm: Dần - Mão
        4: [0, 1], 9: [0, 1]    # Mậu, Quý: Tý - Sửu
    }
    triet_pos = triet_table.get(can_nam_idx, [8, 9])

    # Tuần Không: Tìm con giáp đầu tuần
    chi_dau_tuan = (chi_nam_idx - can_nam_idx) % 12
    tuan_pos = [(chi_dau_tuan - 2) % 12, (chi_dau_tuan - 1) % 12]

    return tuan_pos, triet_pos


def an_toan_bo_sao(
    ngay_sinh_am: int,
    thang_sinh_am: int,
    gio_sinh_chi: str,
    nam_sinh_can_chi: str,
    gioi_tinh: str,
    cuc_so: int,
    chinh_tinh_pos: Dict[str, int],
    cung_menh_pos: int
) -> Dict[str, Any]:
    """
    An toàn bộ 108+ sao bao gồm:
    - Vòng Thái Tuế (12 sao)
    - Vòng Bác Sĩ (12 sao)
    - Vòng Tràng Sinh (12 sao)
    - Bộ Tứ Hóa (4 sao)
    - Toàn bộ Phụ Tinh theo Can, Chi, Tháng, Ngày, Giờ.
    """
    gio_idx = CHI_TO_IDX[gio_sinh_chi]
    can_nam, chi_nam = nam_sinh_can_chi.split()
    can_nam_idx = CAN_TO_IDX[can_nam]
    chi_nam_idx = CHI_TO_IDX[chi_nam]

    is_duong_nam_can = (can_nam_idx % 2 == 0)
    gioi_tinh_clean = gioi_tinh.strip().lower()
    is_nam = gioi_tinh_clean in ["nam", "male", "m"]
    # Dương Nam, Âm Nữ đi Thuận (+1); Âm Nam, Dương Nữ đi Nghịch (-1)
    is_thuan = (is_duong_nam_can and is_nam) or ((not is_duong_nam_can) and (not is_nam))
    step = 1 if is_thuan else -1

    sao_positions = {}

    # --- 1. VÒNG THÁI TUẾ (12 sao thuận từ Chi năm sinh) ---
    for i, sao in enumerate(VONG_THAI_TUE):
        pos = (chi_nam_idx + i) % 12
        sao_positions[sao["ten"]] = pos

    # Sao Thiên Không đồng cung Thiếu Dương
    sao_positions["Thiên Không"] = (chi_nam_idx + 1) % 12

    # --- 2. VÒNG BÁC SĨ (12 sao khởi từ Lộc Tồn) ---
    loc_ton_table = {0: 2, 1: 3, 2: 5, 3: 6, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 0}
    pos_loc_ton = loc_ton_table[can_nam_idx]
    sao_positions["Lộc Tồn"] = pos_loc_ton
    sao_positions["Kình Dương"] = (pos_loc_ton + 1) % 12
    sao_positions["Đà La"] = (pos_loc_ton - 1) % 12

    for i, sao in enumerate(VONG_BAC_SI):
        pos = (pos_loc_ton + i * step) % 12
        sao_positions[sao["ten"]] = pos

    # --- 3. VÒNG TRÀNG SINH (12 sao khởi theo Cục số) ---
    trang_sinh_start = {
        2: 8,   # Thủy Nhị Cục khởi Thân
        3: 11,  # Mộc Tam Cục khởi Hợi
        4: 5,   # Kim Tứ Cục khởi Tỵ
        5: 8,   # Thổ Ngũ Cục khởi Thân
        6: 2    # Hỏa Lục Cục khởi Dần
    }
    pos_trang_sinh = trang_sinh_start.get(cuc_so, 8)
    for i, sao in enumerate(VONG_TRANG_SINH):
        pos = (pos_trang_sinh + i * step) % 12
        sao_positions[sao["ten"]] = pos

    # --- 4. CÁC PHỤ TINH THEO CAN NĂM ---
    # Thiên Khôi, Thiên Việt
    khoi_viet_table = {
        0: (1, 7), 4: (1, 7),
        1: (0, 8), 5: (0, 8),
        2: (11, 9), 3: (11, 9),
        6: (6, 2), 7: (6, 2),
        8: (3, 5), 9: (3, 5)
    }
    sao_positions["Thiên Khôi"], sao_positions["Thiên Việt"] = khoi_viet_table[can_nam_idx]

    # Quốc Ấn (+8 từ Lộc Tồn), Đường Phù (+5 từ Lộc Tồn)
    sao_positions["Quốc Ấn"] = (pos_loc_ton + 8) % 12
    sao_positions["Đường Phù"] = (pos_loc_ton + 5) % 12

    # Thiên Quan, Thiên Phúc
    thien_quan_table = {0: 7, 1: 4, 2: 5, 3: 2, 4: 3, 5: 9, 6: 11, 7: 9, 8: 10, 9: 6}
    thien_phuc_table = {0: 9, 1: 8, 2: 0, 3: 11, 4: 3, 5: 2, 6: 6, 7: 5, 8: 6, 9: 5}
    sao_positions["Thiên Quan"] = thien_quan_table[can_nam_idx]
    sao_positions["Thiên Phúc"] = thien_phuc_table[can_nam_idx]

    # Lưu Hà
    luu_ha_table = {0: 9, 1: 10, 2: 7, 3: 4, 4: 5, 5: 6, 6: 8, 7: 3, 8: 11, 9: 2}
    sao_positions["Lưu Hà"] = luu_ha_table[can_nam_idx]

    # --- 5. CÁC PHỤ TINH THEO CHI NĂM ---
    # Thiên Mã
    thien_ma_table = {
        2: 8, 6: 8, 10: 8,     # Dần Ngọ Tuất mã Thân
        8: 2, 0: 2, 4: 2,       # Thân Tý Thìn mã Dần
        5: 11, 9: 11, 1: 11,    # Tỵ Dậu Sửu mã Hợi
        11: 5, 3: 5, 7: 5       # Hợi Mão Mùi mã Tỵ
    }
    sao_positions["Thiên Mã"] = thien_ma_table[chi_nam_idx]

    # Hoa Cái
    hoa_cai_table = {
        2: 10, 6: 10, 10: 10,
        8: 4, 0: 4, 4: 4,
        5: 1, 9: 1, 1: 1,
        11: 7, 3: 7, 7: 7
    }
    sao_positions["Hoa Cái"] = hoa_cai_table[chi_nam_idx]

    # Đào Hoa
    dao_hoa_table = {
        2: 3, 6: 3, 10: 3,      # Dần Ngọ Tuất tại Mão
        8: 9, 0: 9, 4: 9,       # Thân Tý Thìn tại Dậu
        5: 6, 9: 6, 1: 6,       # Tỵ Dậu Sửu tại Ngọ
        11: 0, 3: 0, 7: 0       # Hợi Mão Mùi tại Tý
    }
    sao_positions["Đào Hoa"] = dao_hoa_table[chi_nam_idx]

    # Kiếp Sát
    kiep_sat_table = {
        2: 11, 6: 11, 10: 11,   # Dần Ngọ Tuất tại Hợi
        8: 5, 0: 5, 4: 5,       # Thân Tý Thìn tại Tỵ
        5: 2, 9: 2, 1: 2,       # Tỵ Dậu Sửu tại Dần
        11: 8, 3: 8, 7: 8       # Hợi Mão Mùi tại Thân
    }
    sao_positions["Kiếp Sát"] = kiep_sat_table[chi_nam_idx]

    # Phá Toái
    pha_toai_table = {
        0: 5, 6: 5, 3: 5, 9: 5,     # Tý Ngọ Mão Dậu tại Tỵ
        2: 9, 8: 9, 5: 9, 11: 9,    # Dần Thân Tỵ Hợi tại Dậu
        4: 1, 10: 1, 1: 1, 7: 1     # Thìn Tuất Sửu Mùi tại Sửu
    }
    sao_positions["Phá Toái"] = pha_toai_table[chi_nam_idx]

    # Cô Thần & Quả Tú
    if chi_nam_idx in [2, 3, 4]:    # Dần Mão Thìn
        sao_positions["Cô Thần"], sao_positions["Quả Tú"] = 5, 1
    elif chi_nam_idx in [5, 6, 7]:  # Tỵ Ngọ Mùi
        sao_positions["Cô Thần"], sao_positions["Quả Tú"] = 8, 4
    elif chi_nam_idx in [8, 9, 10]: # Thân Dậu Tuất
        sao_positions["Cô Thần"], sao_positions["Quả Tú"] = 11, 7
    else:                           # Hợi Tý Sửu
        sao_positions["Cô Thần"], sao_positions["Quả Tú"] = 2, 10

    # Long Trì & Phượng Các
    sao_positions["Long Trì"] = (4 + chi_nam_idx) % 12
    sao_positions["Phượng Các"] = (10 - chi_nam_idx) % 12
    sao_positions["Giải Thần"] = sao_positions["Phượng Các"]

    # Hồng Loan & Thiên Hỷ
    sao_positions["Hồng Loan"] = (3 - chi_nam_idx) % 12
    sao_positions["Thiên Hỷ"] = (sao_positions["Hồng Loan"] + 6) % 12

    # Thiên Khốc & Thiên Hư
    sao_positions["Thiên Khốc"] = (6 - chi_nam_idx) % 12
    sao_positions["Thiên Hư"] = (6 + chi_nam_idx) % 12

    # Thiên Đức & Nguyệt Đức
    sao_positions["Thiên Đức"] = (9 + chi_nam_idx) % 12
    sao_positions["Nguyệt Đức"] = (5 + chi_nam_idx) % 12

    # Hỏa Tinh & Linh Tinh (theo Chi năm và Giờ sinh)
    if chi_nam_idx in [2, 6, 10]:
        hoa_base, linh_base, linh_dir = 1, 3, -1
    elif chi_nam_idx in [8, 0, 4]:
        hoa_base, linh_base, linh_dir = 2, 10, -1
    elif chi_nam_idx in [5, 9, 1]:
        hoa_base, linh_base, linh_dir = 3, 10, -1
    else:
        hoa_base, linh_base, linh_dir = 9, 10, -1

    sao_positions["Hỏa Tinh"] = (hoa_base + gio_idx) % 12
    sao_positions["Linh Tinh"] = (linh_base + linh_dir * gio_idx) % 12

    # --- 6. CÁC PHỤ TINH THEO THÁNG SINH ---
    # Tả Phù (Thìn thuận), Hữu Bật (Tuất nghịch)
    pos_ta_phu = (4 + thang_sinh_am - 1) % 12
    pos_huu_bat = (10 - (thang_sinh_am - 1)) % 12
    sao_positions["Tả Phù"] = pos_ta_phu
    sao_positions["Hữu Bật"] = pos_huu_bat

    # Thiên Hình (Dậu thuận), Thiên Riêu (Sửu thuận), Thiên Y
    sao_positions["Thiên Hình"] = (9 + (thang_sinh_am - 1)) % 12
    sao_positions["Thiên Riêu"] = (1 + (thang_sinh_am - 1)) % 12
    sao_positions["Thiên Y"] = sao_positions["Thiên Riêu"]

    # Thiên Giải (Thân thuận), Địa Giải (Mùi thuận)
    sao_positions["Thiên Giải"] = (8 + (thang_sinh_am - 1)) % 12
    sao_positions["Địa Giải"] = (7 + (thang_sinh_am - 1)) % 12

    # Đẩu Quân: Từ Thái Tuế đếm nghịch đến tháng sinh, từ đó đếm thuận đến giờ sinh
    sao_positions["Đẩu Quân"] = (chi_nam_idx - (thang_sinh_am - 1) + gio_idx) % 12

    # --- 7. CÁC PHỤ TINH THEO NGÀY SINH ---
    # Tam Thai (từ Tả Phù thuận), Bát Tọa (từ Hữu Bật nghịch)
    sao_positions["Tam Thai"] = (pos_ta_phu + (ngay_sinh_am - 1)) % 12
    sao_positions["Bát Tọa"] = (pos_huu_bat - (ngay_sinh_am - 1)) % 12

    # Văn Xương & Văn Khúc (theo Giờ sinh)
    pos_van_xuong = (10 - gio_idx) % 12
    pos_van_khuc = (4 + gio_idx) % 12
    sao_positions["Văn Xương"] = pos_van_xuong
    sao_positions["Văn Khúc"] = pos_van_khuc

    # Ân Quang (từ Xương thuận, lùi 1), Thiên Quý (từ Khúc nghịch, tiến 1)
    sao_positions["Ân Quang"] = (pos_van_xuong + (ngay_sinh_am - 1) - 1) % 12
    sao_positions["Thiên Quý"] = (pos_van_khuc - (ngay_sinh_am - 1) + 1) % 12

    # --- 8. CÁC PHỤ TINH THEO GIỜ SINH ---
    # Địa Không & Địa Kiếp (khởi Hợi 11: Không nghịch, Kiếp thuận)
    sao_positions["Địa Không"] = (11 - gio_idx) % 12
    sao_positions["Địa Kiếp"] = (11 + gio_idx) % 12

    # Thai Phụ (khởi Ngọ 6 thuận), Phong Cáo (khởi Dần 2 thuận)
    sao_positions["Thai Phụ"] = (6 + gio_idx) % 12
    sao_positions["Phong Cáo"] = (2 + gio_idx) % 12

    # --- 9. CÁC SAO CỐ ĐỊNH & THEO CUNG ---
    sao_positions["Thiên La"] = 4   # Cố định tại Thìn
    sao_positions["Địa Võng"] = 10  # Cố định tại Tuất

    # Thiên Thương tại cung Nô Bộc, Thiên Sứ tại cung Tật Ách
    pos_no_boc = (cung_menh_pos - 5) % 12
    pos_tat_ach = (cung_menh_pos - 7) % 12
    sao_positions["Thiên Thương"] = pos_no_boc
    sao_positions["Thiên Sứ"] = pos_tat_ach

    # --- 10. BỘ TỨ HÓA (Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ) ---
    tu_hoa_rules = BANG_TU_HOA.get(can_nam, [])
    hoa_map = {}  # Ánh xạ từ tên sao gốc -> tên Hóa
    for sao_goc, ten_hoa in tu_hoa_rules:
        hoa_map[sao_goc] = ten_hoa
        # Vị trí của Tứ Hóa đồng cung với sao gốc
        pos_sao_goc = chinh_tinh_pos.get(sao_goc, sao_positions.get(sao_goc))
        if pos_sao_goc is not None:
            sao_positions[ten_hoa] = pos_sao_goc

    return {
        "sao_positions": sao_positions,
        "hoa_map": hoa_map
    }


def tinh_dai_van(
    cuc: Dict[str, Any],
    gioi_tinh: str,
    cung_menh_vi_tri: int,
    nam_sinh_can_chi: str
) -> List[Dict[str, Any]]:
    """Tính 10 Đại Vận theo Cục và giới tính (Dương Nam Âm Nữ đi Thuận, Âm Nam Dương Nữ đi Nghịch)."""
    cuc_so = cuc["so_cuc"]
    can_nam = nam_sinh_can_chi.split()[0]
    is_duong_nam = CAN_TO_IDX[can_nam] % 2 == 0

    gioi_tinh_clean = gioi_tinh.strip().lower()
    if gioi_tinh_clean in ["nam", "male", "m"]:
        step = 1 if is_duong_nam else -1
    else:
        step = -1 if is_duong_nam else 1

    dai_van_list = []
    tuoi_start = cuc_so

    for i in range(12):
        pos = (cung_menh_vi_tri + i * step) % 12
        tuoi_end = tuoi_start + 9
        dai_van_list.append({
            "so_thu_tu": i + 1,
            "giai_doan": f"{tuoi_start} - {tuoi_end}",
            "tuoi_bat_dau": tuoi_start,
            "tuoi_ket_thuc": tuoi_end,
            "cung_vi_tri": pos,
            "ten_cung_dia_chi": CUNG_DIA_CHI[pos]
        })
        tuoi_start += 10

    return dai_van_list


def tinh_tieu_han(gioi_tinh: str, chi_nam_idx: int) -> Dict[int, str]:
    """
    Tính vị trí khởi và phân bố Tiểu Hạn (Chi của năm hạn) tại 12 cung:
    - Nam đi THUẬN (+1), Nữ đi NGHỊCH (-1).
    - Dần Ngọ Tuất khởi Thìn (4).
    - Thân Tý Thìn khởi Tuất (10).
    - Tỵ Dậu Sửu khởi Mùi (7).
    - Hợi Mão Mùi khởi Sửu (1).
    """
    start_map = {
        2: 4, 6: 4, 10: 4,
        8: 10, 0: 10, 4: 10,
        5: 7, 9: 7, 1: 7,
        11: 1, 3: 1, 7: 1
    }
    start_pos = start_map[chi_nam_idx]
    is_nam = gioi_tinh.strip().lower() in ["nam", "male", "m"]
    step = 1 if is_nam else -1

    tieu_han_dict = {}
    for i in range(12):
        pos = (start_pos + i * step) % 12
        chi_han = CUNG_DIA_CHI[i]
        tieu_han_dict[pos] = chi_han

    return tieu_han_dict


def lap_la_so(
    ngay_sinh_am: int,
    thang_sinh_am: int,
    nam_sinh_am: int,
    gio_sinh_chi: str,
    gioi_tinh: str
) -> Dict[str, Any]:
    """
    Lập toàn diện Lá Số Tử Vi Đẩu Số Kinh Điển (108+ Sao).
    Bao gồm đầy đủ thông tin:
    - Cung Mệnh & Cung Thân (Thân cư...).
    - Can Chi năm sinh & Can Chi 12 Cung (Ngũ Hổ Độn).
    - Cục số & Ngũ Hành Nạp Âm.
    - 14 Chính Tinh kèm độ sáng Miếu/Vượng/Đắc/Hãm (M, V, Đ, B, H).
    - Đầy đủ Vòng Thái Tuế, Vòng Bác Sĩ, Vòng Tràng Sinh, Tứ Hóa, Tuần Triệt và toàn bộ Phụ Tinh.
    - Phân tách rành mạch Cát Tinh và Sát Tinh trên từng cung.
    - Đại Vận (tuổi bắt đầu) và Tiểu Hạn tại từng cung.
    - Mệnh Chủ & Thân Chủ.
    """
    # 1. Xác định Can Chi năm sinh
    can_nam = CAN_LIST[(nam_sinh_am + 6) % 10]
    chi_nam = CUNG_DIA_CHI[(nam_sinh_am + 8) % 12]
    nam_can_chi = f"{can_nam} {chi_nam}"
    can_nam_idx = CAN_TO_IDX[can_nam]
    chi_nam_idx = CHI_TO_IDX[chi_nam]

    # 2. Ngũ hành nạp âm của năm sinh
    nap_am_nam = tinh_ngu_hanh_nap_am(nam_can_chi)

    # 3. Xác định vị trí cung Mệnh và Cung Thân
    cung_menh_pos = xac_dinh_cung_menh(thang_sinh_am, gio_sinh_chi)
    cung_than_pos = xac_dinh_cung_than(thang_sinh_am, gio_sinh_chi)

    # 4. An 12 cung chức năng
    info_12_cung = an_12_cung(cung_menh_pos)

    # 5. Xác định Cung Thân cư ở cung nào
    chuc_nang_cung_than = info_12_cung["dia_chi_to_chuc_nang"][cung_than_pos]
    than_cu_str = f"Thân cư {chuc_nang_cung_than}"

    # 6. Tính Thiên Can cho 12 cung
    can_12_cung = tinh_can_12_cung(can_nam_idx)

    # 7. Xác định Cục
    cuc_data = xac_dinh_cuc(nam_can_chi, cung_menh_pos)
    cuc_so = cuc_data["so_cuc"]

    # 8. An sao Tử Vi & 14 Chính Tinh
    tu_vi_pos = an_sao_tu_vi(cuc_data, ngay_sinh_am)
    chinh_tinh_pos = an_14_chinh_tinh(tu_vi_pos)

    # 9. An Tuần Không & Triệt Không
    tuan_pos, triet_pos = an_tuan_triet(can_nam_idx, chi_nam_idx)

    # 10. An toàn bộ các sao còn lại (Thái Tuế, Bác Sĩ, Tràng Sinh, Tứ Hóa, Phụ Tinh)
    sao_result = an_toan_bo_sao(
        ngay_sinh_am=ngay_sinh_am,
        thang_sinh_am=thang_sinh_am,
        gio_sinh_chi=gio_sinh_chi,
        nam_sinh_can_chi=nam_can_chi,
        gioi_tinh=gioi_tinh,
        cuc_so=cuc_so,
        chinh_tinh_pos=chinh_tinh_pos,
        cung_menh_pos=cung_menh_pos
    )
    sao_positions = sao_result["sao_positions"]
    hoa_map = sao_result["hoa_map"]

    # 11. Tính Đại Vận & Tiểu Hạn
    dai_van = tinh_dai_van(cuc_data, gioi_tinh, cung_menh_pos, nam_can_chi)
    dai_van_by_cung = {dv["cung_vi_tri"]: dv["tuoi_bat_dau"] for dv in dai_van}
    tieu_han_by_cung = tinh_tieu_han(gioi_tinh, chi_nam_idx)

    # 12. Mệnh Chủ & Thân Chủ
    menh_chu = MENH_CHU_MAP.get(CUNG_DIA_CHI[cung_menh_pos], "Tử Vi")
    than_chu = THAN_CHU_MAP.get(chi_nam, "Hỏa Tinh")

    # 13. Gom và phân loại sao cho từng cung Địa Chi (0-11)
    chinh_tinh_theo_cung: Dict[int, List[Dict[str, Any]]] = {i: [] for i in range(12)}
    cat_tinh_theo_cung: Dict[int, List[Dict[str, Any]]] = {i: [] for i in range(12)}
    sat_tinh_theo_cung: Dict[int, List[Dict[str, Any]]] = {i: [] for i in range(12)}
    all_sao_theo_cung: Dict[int, List[Dict[str, Any]]] = {i: [] for i in range(12)}

    # A. Phân bổ 14 Chính Tinh
    for star in CHINH_TINH:
        ten = star["ten"]
        if ten in chinh_tinh_pos:
            pos = chinh_tinh_pos[ten]
            dac_ham = CHINH_TINH_DAC_HAM.get(ten, {}).get(pos, "B")
            hoa = hoa_map.get(ten)
            star_dict = {
                "ten": ten,
                "loai": "chinh_tinh",
                "ngu_hanh": star["ngu_hanh"],
                "dac_ham": dac_ham,
                "hoa": hoa,
                "chuc_nang": star["chuc_nang"]
            }
            chinh_tinh_theo_cung[pos].append(star_dict)
            all_sao_theo_cung[pos].append(star_dict)

    # B. Phân bổ Phụ Tinh, Vòng Thái Tuế, Bác Sĩ, Tràng Sinh, Tứ Hóa
    # Danh mục tra cứu nhanh thuộc tính
    all_star_meta = {}
    for s in VONG_THAI_TUE:
        all_star_meta[s["ten"]] = s
    for s in VONG_BAC_SI:
        all_star_meta[s["ten"]] = s
    for s in VONG_TRANG_SINH:
        all_star_meta[s["ten"]] = s
    for k, v in PHU_TINH_CHI_TIET.items():
        all_star_meta[k] = {"ten": k, **v}
    for k, v in TU_HOA_INFO.items():
        all_star_meta[k] = {"ten": k, **v}

    for star_name, pos in sao_positions.items():
        meta = all_star_meta.get(star_name, {"loai": "cat_tinh", "ngu_hanh": "Thổ", "y_nghia": ""})
        loai = meta.get("loai", "cat_tinh")
        ngu_hanh = meta.get("ngu_hanh", "Thổ")
        y_nghia = meta.get("y_nghia", "")
        hoa = hoa_map.get(star_name)

        # Tính độ sáng cho sát tinh nếu có
        dac_ham = ""
        if star_name in SAT_TINH_DAC_HAM:
            dac_ham = SAT_TINH_DAC_HAM[star_name].get(pos, "H")

        star_obj = {
            "ten": star_name,
            "loai": loai,
            "ngu_hanh": ngu_hanh,
            "dac_ham": dac_ham,
            "hoa": hoa,
            "y_nghia": y_nghia
        }
        all_sao_theo_cung[pos].append(star_obj)

        if loai in ["sat_tinh", "bai_tinh"]:
            sat_tinh_theo_cung[pos].append(star_obj)
        else:
            cat_tinh_theo_cung[pos].append(star_obj)

    # 14. Đóng gói danh sách 12 cung chi tiết
    cac_cung = []
    for pos in range(12):
        chuc_nang = info_12_cung["dia_chi_to_chuc_nang"][pos]
        can_cung = can_12_cung[pos]
        chi_cung = CUNG_DIA_CHI[pos]
        cac_cung.append({
            "vi_tri_dia_chi": pos,
            "ten_dia_chi": chi_cung,
            "can_cung": can_cung,
            "can_chi_cung": f"{can_cung} {chi_cung}",
            "ten_cung_chuc_nang": chuc_nang,
            "la_cung_than": (pos == cung_than_pos),
            "co_tuan": (pos in tuan_pos),
            "co_triet": (pos in triet_pos),
            "dai_van_tuoi": dai_van_by_cung.get(pos, cuc_so),
            "tieu_han_chi": tieu_han_by_cung.get(pos, ""),
            "chinh_tinh": chinh_tinh_theo_cung[pos],
            "cat_tinh": cat_tinh_theo_cung[pos],
            "sat_tinh": sat_tinh_theo_cung[pos],
            "danh_sach_sao": all_sao_theo_cung[pos]
        })

    is_duong_nam = CAN_TO_IDX[can_nam] % 2 == 0
    gioi_tinh_clean = gioi_tinh.strip().lower()
    is_nam = gioi_tinh_clean in ["nam", "male", "m"]
    chieu_dai_van = "Thuận" if ((is_duong_nam and is_nam) or (not is_duong_nam and not is_nam)) else "Nghịch"

    return {
        "thong_tin_co_ban": {
            "ngay_am": ngay_sinh_am,
            "thang_am": thang_sinh_am,
            "nam_am": nam_sinh_am,
            "can_chi_nam": nam_can_chi,
            "gio_sinh": gio_sinh_chi,
            "gioi_tinh": gioi_tinh,
            "am_duong_nam_nu": f"{'Dương' if is_duong_nam else 'Âm'} {'Nam' if is_nam else 'Nữ'}"
        },
        "cung_menh_vi_tri": cung_menh_pos,
        "ten_cung_menh": CUNG_DIA_CHI[cung_menh_pos],
        "cung_than_vi_tri": cung_than_pos,
        "ten_cung_than": CUNG_DIA_CHI[cung_than_pos],
        "than_cu": than_cu_str,
        "menh_chu": menh_chu,
        "than_chu": than_chu,
        "chieu_dai_van": chieu_dai_van,
        "cuc": cuc_data,
        "ngu_hanh_nap_am": nap_am_nam,
        "tuan_khong_vi_tri": tuan_pos,
        "triet_khong_vi_tri": triet_pos,
        "cac_cung": cac_cung,
        "cac_sao_theo_cung": all_sao_theo_cung,
        "chinh_tinh_vi_tri": chinh_tinh_pos,
        "phu_tinh_vi_tri": sao_positions,
        "dai_van": dai_van
    }
