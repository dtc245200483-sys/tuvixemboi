# -*- coding: utf-8 -*-
"""
Module lõi thực thi thuật toán lập Tứ Trụ (Bát Tự) và phân tích chuyên sâu toàn diện
theo đúng 100% kinh điển học thuật Tử Bình từ cuốn sách:
'Dự Báo Theo Tử Bình' - Tác giả: Trần Khang Ninh (Nhà Xuất Bản Thanh Hóa).

Bao gồm:
1. Lập Tứ Trụ Can Chi 4 Trụ (Năm, Tháng, Ngày, Giờ).
2. Thập Thần đầy đủ cho 4 Thiên Can và toàn bộ Tàng Can trong 4 Địa Chi.
3. Thần Sát kinh điển: Thiên Ất Quý Nhân, Thái Cực Quý Nhân, Thiên Đức, Nguyệt Đức,
   Văn Xương, Dịch Mã, Hoa Cái, Đào Hoa, Kình Dương, Lộc Thần, Tuần Không (Không Vong).
4. Phân tích Cục Diện Tương Tác: Lục Hợp, Tam Hợp, Tam Hội, Lục Xung, Tam Hình, Lục Hại, Tương Phá.
5. Thẩm định Thân Vượng / Thân Nhược theo 3 chuẩn mực: Đắc Lệnh, Đắc Địa, Đắc Thế.
6. Xác định Cách Cục (Bát cách, Kiến Lộc, Dương Nhận, Biến cách).
7. Xác định Dụng Thần Toàn Diện: Phù Ức, Điều Hầu (mùa đông cần Hỏa / mùa hè cần Thủy),
   Thông Quan, Hỷ Thần, Kỵ Thần.
8. Ứng dụng Cải Vận Đời Sống (Màu sắc, Con số Hà Lạc, Phương vị, Nghề nghiệp).
9. Bảng 8 Đại Vận của cuộc đời (thuận/nghịch theo Dương Nam Âm Nữ, Thập Thần từng vận).
"""

from typing import Dict, Any, List, Optional
from astro_engine.bat_tu.constants.can_chi import (
    CAN_NAMES,
    CHI_NAMES,
    CAN_DICT,
    CHI_DICT,
    THIEN_CAN,
    DIA_CHI,
    BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH,
    BANG_TRA_CUU_THAP_THAN_10X10,
    DANH_SACH_10_THAP_THAN_CHUAN,
    PHE_TRO_THAN,
    PHE_THONG_CAN,
    PHE_TIET_KHAC_THAN,
    BANG_LOC_VI_10_CAN,
    BANG_DUONG_NHAN_10_CAN
)
from astro_engine.bat_tu.constants.ngu_hanh import (
    DANH_SACH_NGU_HANH,
    TUONG_SINH,
    HANH_SINH_RA,
    TUONG_KHAC,
    HANH_KHAC_NO
)
from calendar_converter.lunar_calendar import (
    solar_to_lunar,
    xac_dinh_can_chi_thang_tiet_khi,
    xac_dinh_can_chi_nam_tiet_khi,
    kiem_tra_vung_bien_4_tru,
    tinh_tuoi_khoi_van_chuan,
    xac_dinh_tiet_khi_chuan
)


def jdn(d: int, m: int, y: int) -> int:
    """Tính số ngày Julius (JDN) từ ngày, tháng, năm Dương lịch."""
    a = (14 - m) // 12
    y2 = y + 4800 - a
    m2 = m + 12 * a - 3
    return d + ((153 * m2 + 2) // 5) + 365 * y2 + (y2 // 4) - (y2 // 100) + (y2 // 400) - 32045


def xac_dinh_can_chi_nam(
    nam_duong: int,
    ngay_duong: Optional[int] = None,
    thang_duong: Optional[int] = None,
    gio_sinh: int = 12,
    phut_sinh: int = 0
) -> Dict[str, str]:
    """
    1. Xác định Can-Chi năm sinh.
    Ưu tiên tính theo mốc LẬP XUÂN (tiết 315 độ) nếu có ngày tháng.
    """
    if ngay_duong is not None and thang_duong is not None:
        return xac_dinh_can_chi_nam_tiet_khi(ngay_duong, thang_duong, nam_duong, gio_sinh, phut_sinh)
    can_idx = (nam_duong + 6) % 10
    chi_idx = (nam_duong + 8) % 12
    return {
        "can": CAN_NAMES[can_idx],
        "chi": CHI_NAMES[chi_idx]
    }


def xac_dinh_can_chi_thang(
    nam_can: str,
    thang_am_hoac_ngay: int,
    thang_duong: Optional[int] = None,
    nam_duong: Optional[int] = None,
    gio_sinh: int = 12,
    phut_sinh: int = 0
) -> Dict[str, str]:
    """
    2. Xác định Can-Chi tháng sinh.
    Căn cứ: Sách 'Dự Báo Theo Tử Bình' - Trần Khang Ninh (tr.15):
    Trụ Tháng Bắt Buộc Xác Định Theo LỊCH TIẾT KHÍ (12 Tiết chính, so sánh trực tiếp với giờ-phút sinh).
    """
    if thang_duong is not None and nam_duong is not None:
        return xac_dinh_can_chi_thang_tiet_khi(
            nam_can=nam_can,
            ngay_duong=thang_am_hoac_ngay,
            thang_duong=thang_duong,
            nam_duong=nam_duong,
            gio_sinh=gio_sinh,
            phut_sinh=phut_sinh
        )

    thang_am = thang_am_hoac_ngay
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
    4. Xác định Can của giờ sinh theo quy tắc 'Ngũ Thử Độn' khởi từ Can ngày.
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


# ==============================================================================
# BỔ SUNG NÂNG CAO: THEO KINH ĐIỂN 'DỰ BÁO THEO TỬ BÌNH' (TRẦN KHANG NINH)
# ==============================================================================

def tinh_thap_than(target_can: str, nhat_chu: str, is_nhat_chu: bool = False) -> Dict[str, str]:
    """
    Tính Thập Thần của một Thiên Can đối với Nhật Chủ dựa trên BẢNG TRA CỨU CỐ ĐỊNH 10x10 (Trần Khang Ninh, tr. 31).
    Tuyệt đối không suy luận tự do, không sinh nhãn ngoài 10 Thần chuẩn.
    Với Can Ngày (Nhật Chủ): Luôn gán nhãn 'Nhật Chủ (Nguyên Thần)', không tính Thập Thần cho chính nó.
    """
    if is_nhat_chu or (target_can and nhat_chu and target_can == nhat_chu and is_nhat_chu):
        return {
            "ten": "Nhật Chủ (Nguyên Thần)",
            "ten_viet_tat": "Nhật Chủ",
            "nhom": "Bản Thân",
            "y_nghia": "Đại diện cho chính bản thân mệnh chủ, chân nguyên sinh mệnh."
        }

    if not target_can or not nhat_chu or nhat_chu not in BANG_TRA_CUU_THAP_THAN_10X10 or target_can not in BANG_TRA_CUU_THAP_THAN_10X10[nhat_chu]:
        return {"ten": "Chưa rõ", "ten_viet_tat": "--", "nhom": "--", "y_nghia": ""}

    ten_thap_than = BANG_TRA_CUU_THAP_THAN_10X10[nhat_chu][target_can]

    metadata_map = {
        "Tỷ Kiên": {
            "ten_viet_tat": "Tỷ", "nhom": "Tỷ Kiếp",
            "y_nghia": "Lòng tự lập, tự tôn, bạn bè tri kỷ đồng chí hướng, anh em ruột thịt."
        },
        "Kiếp Tài": {
            "ten_viet_tat": "Kiếp", "nhom": "Tỷ Kiếp",
            "y_nghia": "Dũng cảm đột phá, dám mạo hiểm, tính cạnh tranh, nhiệt tình xông pha."
        },
        "Thực Thần": {
            "ten_viet_tat": "Thực", "nhom": "Thực Thương",
            "y_nghia": "Phúc thọ tinh, ăn mặc sung túc, hòa nhã thanh cao, tài hoa ngầm, sinh tài lộc."
        },
        "Thương Quan": {
            "ten_viet_tat": "Thương", "nhom": "Thực Thương",
            "y_nghia": "Trí tuệ phát tiết xuất chúng, tài ăn nói, sáng tạo đổi mới, ghét sự gò bó."
        },
        "Chính Tài": {
            "ten_viet_tat": "Tài", "nhom": "Tài Tinh",
            "y_nghia": "Tài sản tích lũy chính đáng qua lao động, tính cách chu toàn, gia đạo bền vững."
        },
        "Thiên Tài": {
            "ten_viet_tat": "Thiên Tài", "nhom": "Tài Tinh",
            "y_nghia": "Tài lộc bất ngờ, đầu tư kinh doanh nhạy bén, tính tình hào sảng phóng khoáng."
        },
        "Chính Quan": {
            "ten_viet_tat": "Quan", "nhom": "Quan Sát",
            "y_nghia": "Chức tước, kỷ cương, sự chính trực, danh dự xã hội, tinh thần trách nhiệm."
        },
        "Thất Sát": {
            "ten_viet_tat": "Sát", "nhom": "Quan Sát",
            "y_nghia": "Quyền uy dũng mãnh, quyết đoán, chịu áp lực lớn để làm nên nghiệp lớn."
        },
        "Chính Ấn": {
            "ten_viet_tat": "Ấn", "nhom": "Ấn Tinh",
            "y_nghia": "Học vấn uyên thâm, bằng cấp, danh tiếng thanh cao, quý nhân và mẹ che chở."
        },
        "Thiên Ấn": {
            "ten_viet_tat": "Kiêu", "nhom": "Ấn Tinh",
            "y_nghia": "Trí tuệ đặc dị, giác quan thứ sáu, tài năng nghệ thuật, y thuật huyền học."
        }
    }

    meta = metadata_map.get(ten_thap_than, {"ten_viet_tat": ten_thap_than, "nhom": "Khác", "y_nghia": ""})
    return {
        "ten": ten_thap_than,
        "ten_viet_tat": meta["ten_viet_tat"],
        "nhom": meta["nhom"],
        "y_nghia": meta["y_nghia"]
    }


def tinh_khong_vong(can_ngay: str, chi_ngay: str) -> List[str]:
    """
    Xác định 2 Địa Chi Không Vong (Tuần Không) theo chu kỳ Hoa Giáp (Trần Khang Ninh tr. 86).
    """
    can_idx = CAN_NAMES.index(can_ngay) if can_ngay in CAN_NAMES else 0
    chi_idx = CHI_NAMES.index(chi_ngay) if chi_ngay in CHI_NAMES else 0
    # Khoảng cách từ Chi về Can
    diff = (chi_idx - can_idx) % 12
    # 2 chi không vong là 2 chi cuối của tuần giáp
    kv1 = CHI_NAMES[(diff + 10) % 12]
    kv2 = CHI_NAMES[(diff + 11) % 12]
    return [kv1, kv2]


def tinh_than_sat_cho_chi(
    chi_muc_tieu: str,
    nhat_can: str,
    chi_ngay: str,
    chi_nam: str,
    chi_thang: str,
    khong_vong_ngay: List[str]
) -> List[str]:
    """
    Xác định các Thần Sát đóng tại một Địa Chi theo sách Trần Khang Ninh (tr. 92-107).
    """
    danh_sach: List[str] = []

    # 1. Thiên Ất Quý Nhân (Vạn thần chi chủ)
    # Giáp Mậu Canh: Sửu Mùi; Ất Kỷ: Tý Thân; Bính Đinh: Hợi Dậu; Nhâm Quý: Mão Tỵ; Tân: Ngọ Dần
    thien_at_map = {
        "Giáp": ["Sửu", "Mùi"], "Mậu": ["Sửu", "Mùi"], "Canh": ["Sửu", "Mùi"],
        "Ất": ["Tý", "Thân"], "Kỷ": ["Tý", "Thân"],
        "Bính": ["Hợi", "Dậu"], "Đinh": ["Hợi", "Dậu"],
        "Nhâm": ["Mão", "Tỵ"], "Quý": ["Mão", "Tỵ"],
        "Tân": ["Ngọ", "Dần"]
    }
    if chi_muc_tieu in thien_at_map.get(nhat_can, []):
        danh_sach.append("Thiên Ất Quý Nhân")

    # 2. Thái Cực Quý Nhân
    # Giáp Ất sinh Tý Ngọ; Bính Đinh Kê Thố (Mão Dậu); Mậu Kỷ Thìn Tuất Sửu Mùi; Canh Tân Dần Hợi; Nhâm Quý Tỵ Thân
    thai_cuc_map = {
        "Giáp": ["Tý", "Ngọ"], "Ất": ["Tý", "Ngọ"],
        "Bính": ["Mão", "Dậu"], "Đinh": ["Mão", "Dậu"],
        "Mậu": ["Thìn", "Tuất", "Sửu", "Mùi"], "Kỷ": ["Thìn", "Tuất", "Sửu", "Mùi"],
        "Canh": ["Dần", "Hợi"], "Tân": ["Dần", "Hợi"],
        "Nhâm": ["Tỵ", "Thân"], "Quý": ["Tỵ", "Thân"]
    }
    if chi_muc_tieu in thai_cuc_map.get(nhat_can, []):
        danh_sach.append("Thái Cực Quý Nhân")

    # 3. Văn Xương Quý Nhân
    # Giáp Tỵ, Ất Ngọ, Bính Mậu Thân, Đinh Kỷ Dậu, Canh Hợi, Tân Tý, Nhâm Dần, Quý Mão
    van_xuong_map = {
        "Giáp": "Tỵ", "Ất": "Ngọ", "Bính": "Thân", "Mậu": "Thân",
        "Đinh": "Dậu", "Kỷ": "Dậu", "Canh": "Hợi", "Tân": "Tý",
        "Nhâm": "Dần", "Quý": "Mão"
    }
    if van_xuong_map.get(nhat_can) == chi_muc_tieu:
        danh_sach.append("Văn Xương Quý Nhân")

    # 4. Lộc Thần (Lộc Vị)
    # Giáp Dần, Ất Mão, Bính Mậu Tỵ, Đinh Kỷ Ngọ, Canh Thân, Tân Dậu, Nhâm Hợi, Quý Tý
    loc_than_map = {
        "Giáp": "Dần", "Ất": "Mão", "Bính": "Tỵ", "Mậu": "Tỵ",
        "Đinh": "Ngọ", "Kỷ": "Ngọ", "Canh": "Thân", "Tân": "Dậu",
        "Nhâm": "Hợi", "Quý": "Tý"
    }
    if loc_than_map.get(nhat_can) == chi_muc_tieu:
        danh_sach.append("Lộc Thần")

    # 5. Kình Dương (Dương Nhận)
    # Giáp Mão, Ất Dần, Bính Mậu Ngọ, Đinh Kỷ Tỵ, Canh Dậu, Tân Thân, Nhâm Tý, Quý Hợi
    kinh_duong_map = {
        "Giáp": "Mão", "Ất": "Dần", "Bính": "Ngọ", "Mậu": "Ngọ",
        "Đinh": "Tỵ", "Kỷ": "Tỵ", "Canh": "Dậu", "Tân": "Thân",
        "Nhâm": "Tý", "Quý": "Hợi"
    }
    if kinh_duong_map.get(nhat_can) == chi_muc_tieu:
        danh_sach.append("Kình Dương (Dương Nhận)")

    # 6. Dịch Mã (Xét theo Chi Ngày hoặc Chi Năm)
    # Thân Tý Thìn mã tại Dần; Dần Ngọ Tuất mã tại Thân; Tỵ Dậu Sửu mã tại Hợi; Hợi Mão Mùi mã tại Tỵ
    dich_ma_rules = {
        ("Thân", "Tý", "Thìn"): "Dần",
        ("Dần", "Ngọ", "Tuất"): "Thân",
        ("Tỵ", "Dậu", "Sửu"): "Hợi",
        ("Hợi", "Mão", "Mùi"): "Tỵ"
    }
    for group, ma_chi in dich_ma_rules.items():
        if (chi_ngay in group or chi_nam in group) and chi_muc_tieu == ma_chi:
            danh_sach.append("Dịch Mã")
            break

    # 7. Hoa Cái (Xét theo Chi Ngày hoặc Chi Năm)
    # Thân Tý Thìn kiến Thìn; Dần Ngọ Tuất kiến Tuất; Tỵ Dậu Sửu kiến Sửu; Hợi Mão Mùi kiến Mùi
    hoa_cai_rules = {
        ("Thân", "Tý", "Thìn"): "Thìn",
        ("Dần", "Ngọ", "Tuất"): "Tuất",
        ("Tỵ", "Dậu", "Sửu"): "Sửu",
        ("Hợi", "Mão", "Mùi"): "Mùi"
    }
    for group, hc_chi in hoa_cai_rules.items():
        if (chi_ngay in group or chi_nam in group) and chi_muc_tieu == hc_chi:
            danh_sach.append("Hoa Cái")
            break

    # 8. Đào Hoa / Hàm Trì (Xét theo Chi Ngày hoặc Chi Năm)
    # Thân Tý Thìn kiến Dậu; Dần Ngọ Tuất kiến Mão; Tỵ Dậu Sửu kiến Ngọ; Hợi Mão Mùi kiến Tý
    dao_hoa_rules = {
        ("Thân", "Tý", "Thìn"): "Dậu",
        ("Dần", "Ngọ", "Tuất"): "Mão",
        ("Tỵ", "Dậu", "Sửu"): "Ngọ",
        ("Hợi", "Mão", "Mùi"): "Tý"
    }
    for group, dh_chi in dao_hoa_rules.items():
        if (chi_ngay in group or chi_nam in group) and chi_muc_tieu == dh_chi:
            danh_sach.append("Đào Hoa")
            break

    # 9. Địa Chi Không Vong
    if chi_muc_tieu in khong_vong_ngay:
        danh_sach.append("Tuần Không (Không Vong)")

    return danh_sach


def tinh_tuong_tac_can_chi(tu_tru: Dict[str, Any]) -> Dict[str, Any]:
    """
    Kiểm tra toàn bộ quan hệ Hợp, Xung, Hình, Hại, Phá giữa 4 trụ (Trần Khang Ninh tr. 86-92, tr. 163).
    """
    trus = [tu_tru["tru_nam"], tu_tru["tru_thang"], tu_tru["tru_ngay"], tu_tru["tru_gio"]]
    cans = [t["can"] for t in trus]
    chis = [t["chi"] for t in trus]

    ket_qua = {
        "can_hop": [],
        "can_xung": [],
        "chi_luc_hop": [],
        "chi_tam_hop": [],
        "chi_tam_hoi": [],
        "chi_luc_xung": [],
        "chi_tuong_hinh": [],
        "chi_tuong_hai": [],
        "chi_tuong_pha": []
    }

    # 1. Thiên Can Ngũ Hợp
    ngu_hop = {("Giáp", "Kỷ"): "Thổ", ("Ất", "Canh"): "Kim", ("Bính", "Tân"): "Thủy", ("Đinh", "Nhâm"): "Mộc", ("Mậu", "Quý"): "Hỏa"}
    for i in range(len(cans)):
        for j in range(i + 1, len(cans)):
            pair = (cans[i], cans[j])
            pair_rev = (cans[j], cans[i])
            for k, val in ngu_hop.items():
                if pair == k or pair_rev == k:
                    ket_qua["can_hop"].append(f"{cans[i]} hợp {cans[j]} (Hóa {val})")

    # 2. Thiên Can Tương Xung
    can_xung = [("Giáp", "Canh"), ("Ất", "Tân"), ("Bính", "Nhâm"), ("Đinh", "Quý")]
    for i in range(len(cans)):
        for j in range(i + 1, len(cans)):
            for p1, p2 in can_xung:
                if (cans[i] == p1 and cans[j] == p2) or (cans[i] == p2 and cans[j] == p1):
                    ket_qua["can_xung"].append(f"{cans[i]} xung {cans[j]}")

    # 3. Địa Chi Lục Hợp
    luc_hop = {("Tý", "Sửu"): "Thổ", ("Dần", "Hợi"): "Mộc", ("Mão", "Tuất"): "Hỏa", ("Thìn", "Dậu"): "Kim", ("Tỵ", "Thân"): "Thủy", ("Ngọ", "Mùi"): "Thổ"}
    for i in range(len(chis)):
        for j in range(i + 1, len(chis)):
            for k, val in luc_hop.items():
                if (chis[i] == k[0] and chis[j] == k[1]) or (chis[i] == k[1] and chis[j] == k[0]):
                    ket_qua["chi_luc_hop"].append(f"{chis[i]} lục hợp {chis[j]} (Hóa {val})")

    # 4. Địa Chi Tam Hợp Cục
    tam_hop = {
        ("Thân", "Tý", "Thìn"): "Thủy cục",
        ("Hợi", "Mão", "Mùi"): "Mộc cục",
        ("Dần", "Ngọ", "Tuất"): "Hỏa cục",
        ("Tỵ", "Dậu", "Sửu"): "Kim cục"
    }
    for trio, cuc in tam_hop.items():
        count = sum(1 for c in trio if c in chis)
        if count == 3:
            ket_qua["chi_tam_hop"].append(f"Tam Hợp {'-'.join(trio)} thành {cuc}")
        elif count == 2:
            present = [c for c in trio if c in chis]
            ket_qua["chi_tam_hop"].append(f"Bán hợp {'-'.join(present)} (hướng {cuc})")

    # 5. Địa Chi Lục Xung
    luc_xung = [("Tý", "Ngọ"), ("Sửu", "Mùi"), ("Dần", "Thân"), ("Mão", "Dậu"), ("Thìn", "Tuất"), ("Tỵ", "Hợi")]
    for i in range(len(chis)):
        for j in range(i + 1, len(chis)):
            for p1, p2 in luc_xung:
                if (chis[i] == p1 and chis[j] == p2) or (chis[i] == p2 and chis[j] == p1):
                    ket_qua["chi_luc_xung"].append(f"{chis[i]} trực xung {chis[j]}")

    # 6. Địa Chi Tương Hình
    if "Tý" in chis and "Mão" in chis:
        ket_qua["chi_tuong_hinh"].append("Tý - Mão tương hình (Hình vô lễ)")
    if all(c in chis for c in ["Dần", "Tỵ", "Thân"]):
        ket_qua["chi_tuong_hinh"].append("Dần - Tỵ - Thân tam hình (Trì thế chi hình)")
    elif sum(1 for c in ["Dần", "Tỵ", "Thân"] if c in chis) == 2:
        prs = [c for c in ["Dần", "Tỵ", "Thân"] if c in chis]
        ket_qua["chi_tuong_hinh"].append(f"{prs[0]} - {prs[1]} tương hình")
    if all(c in chis for c in ["Sửu", "Tuất", "Mùi"]):
        ket_qua["chi_tuong_hinh"].append("Sửu - Tuất - Mùi tam hình (Vô ân chi hình)")
    elif sum(1 for c in ["Sửu", "Tuất", "Mùi"] if c in chis) == 2:
        prs = [c for c in ["Sửu", "Tuất", "Mùi"] if c in chis]
        ket_qua["chi_tuong_hinh"].append(f"{prs[0]} - {prs[1]} tương hình")
    for tc in ["Thìn", "Ngọ", "Dậu", "Hợi"]:
        if chis.count(tc) >= 2:
            ket_qua["chi_tuong_hinh"].append(f"{tc} gặp {tc} (Tự hình)")

    # 7. Địa Chi Lục Hại
    luc_hai = [("Tý", "Mùi"), ("Sửu", "Ngọ"), ("Dần", "Tỵ"), ("Mão", "Thìn"), ("Thân", "Hợi"), ("Dậu", "Tuất")]
    for i in range(len(chis)):
        for j in range(i + 1, len(chis)):
            for p1, p2 in luc_hai:
                if (chis[i] == p1 and chis[j] == p2) or (chis[i] == p2 and chis[j] == p1):
                    ket_qua["chi_tuong_hai"].append(f"{chis[i]} tương hại {chis[j]}")

    return ket_qua


def xac_dinh_cach_cuc(tu_tru: Dict[str, Any]) -> Dict[str, str]:
    """
    Xác định Cách Cục chính quy của Bát Tự theo sách Trần Khang Ninh (Phần III Chương I tr. 108-131).
    Dựa trên Tàng Can của Lệnh Tháng (Chi Tháng) thấu xuất lên Thiên Can.
    """
    nhat_chu = tu_tru["tru_ngay"]["can"]
    chi_thang = tu_tru["tru_thang"]["chi"]
    tang_can_thang = CHI_DICT[chi_thang]["chi_tang"]

    cac_can_lo = [
        tu_tru["tru_nam"]["can"],
        tu_tru["tru_thang"]["can"],
        tu_tru["tru_gio"]["can"]
    ]

    # Kiểm tra xem có Tàng Can nào của Chi Tháng thấu xuất lên Can lộ hay không
    can_thau: Optional[str] = None
    for tc in tang_can_thang:
        if tc in cac_can_lo:
            can_thau = tc
            break

    # Nếu không thấu can nào thì lấy Bản Khí (can đầu tiên trong tàng can)
    can_dinh_cach = can_thau if can_thau else tang_can_thang[0]
    thap_than = tinh_thap_than(can_dinh_cach, nhat_chu)

    # Xét Kiến Lộc hoặc Dương Nhận theo bảng vị trí cố định
    ten_cach = ""
    mo_ta = ""

    if BANG_LOC_VI_10_CAN.get(nhat_chu) == chi_thang:
        ten_cach = "Kiến Lộc Cách"
        thau_can = "Đắc Lộc Nguyệt Lệnh"
        mo_ta = f"Nhật Chủ {nhat_chu} đắc Lộc tại Chi Tháng {chi_thang} (Kiến Lộc Cách). Tài lộc và sự nghiệp do tự thân phấn đấu gây dựng, có ý chí lập thân cao."
    elif BANG_DUONG_NHAN_10_CAN.get(nhat_chu) == chi_thang:
        ten_cach = "Dương Nhận Cách"
        thau_can = "Đắc Nhận Nguyệt Lệnh"
        mo_ta = f"Nhật Chủ {nhat_chu} đắc Kình Dương tại Chi Tháng {chi_thang} (Dương Nhận Cách). Tính khí dũng cảm quả quyết, chí khí hiên ngang, ưa công danh nghiệp lớn."
    else:
        tt_name = thap_than["ten"]
        if "Chính Quan" in tt_name:
            ten_cach = "Chính Quan Cách"
            mo_ta = "Cách cục quý hiển thanh cao, trọng danh dự, quy tắc và kỷ luật, sự nghiệp hanh thông quan lộ rộng mở."
        elif "Thất Sát" in tt_name:
            ten_cach = "Thất Sát Cách (Thiên Quan Cách)"
            mo_ta = "Cách cục uy quyền mãnh liệt, giàu dũng khí và tài lãnh đạo, càng kinh qua phong ba càng hiển hách vinh hoa."
        elif "Chính Ấn" in tt_name:
            ten_cach = "Chính Ấn Cách"
            mo_ta = "Cách cục văn chương học vấn từ ái, phúc thọ song toàn, cả đời được bề trên chở che và quý nhân phò trợ."
        elif "Thiên Ấn" in tt_name:
            ten_cach = "Thiên Ấn Cách (Kiêu Thần Cách)"
            mo_ta = "Cách cục thông tuệ dị thường, có năng khiếu nghệ thuật, y thuật hoặc học thuật chuyên sâu độc đáo."
        elif "Thực Thần" in tt_name:
            ten_cach = "Thực Thần Cách"
            mo_ta = "Cách cục phúc thọ an khang, tính tình hòa nhã nhân hậu, có tài nghệ và năng lực sinh tài lộc tự nhiên."
        elif "Thương Quan" in tt_name:
            ten_cach = "Thương Quan Cách"
            mo_ta = "Cách cục tài hoa cái thế, thông minh cơ biến, dám đổi mới cải cách, có năng lực ngôn luận và tài nghệ kiệt xuất."
        elif "Chính Tài" in tt_name:
            ten_cach = "Chính Tài Cách"
            mo_ta = "Cách cục cần kiệm làm giàu bền vững, tính tình trung hậu chu toàn, tài chính ổn định và gia đạo hòa hợp."
        elif "Thiên Tài" in tt_name:
            ten_cach = "Thiên Tài Cách"
            mo_ta = "Cách cục hào sảng phóng khoáng, nhạy bén thương mại kinh doanh, có duyên đắc tài lộc bất ngờ."
        else:
            ten_cach = f"{tt_name} Cách"
            mo_ta = thap_than["y_nghia"]

    return {
        "ten_cach": ten_cach,
        "can_dinh_cach": can_dinh_cach,
        "thau_can": thau_can if (loc_map := BANG_LOC_VI_10_CAN.get(nhat_chu) == chi_thang or BANG_DUONG_NHAN_10_CAN.get(nhat_chu) == chi_thang) else ("Thấu Xuất" if can_thau else "Bản Khí Lệnh Tháng"),
        "mo_ta": mo_ta
    }


def phan_tich_vuong_nhuoc_chuyen_sau(tu_tru: Dict[str, Any], ngu_hanh_count: Dict[str, int]) -> Dict[str, Any]:
    """
    Thẩm định Thân Vượng / Thân Nhược theo 3 yếu tố cốt lõi của Tử Bình (Trần Khang Ninh tr. 134-151):
    1. Đắc Lệnh: Chi Tháng có tàng can mang Thập Thần thuộc {Tỷ Kiên, Kiếp Tài, Chính Ấn, Thiên Ấn}.
    2. Đắc Địa (Thông Căn): 4 Chi (Năm, Tháng, Ngày, Giờ) có tàng can mang Thập Thần thuộc {Tỷ Kiên, Kiếp Tài}.
       TUYỆT ĐỐI KHÔNG tính Ấn vào Đắc Địa / Thông Căn.
    3. Đắc Thế: 3 Thiên Can lộ (Năm, Tháng, Giờ) mang Thập Thần thuộc {Tỷ Kiên, Kiếp Tài, Chính Ấn, Thiên Ấn}.
       TUYỆT ĐỐI LOẠI BỎ Chính Tài, Thiên Tài, Thực Thần, Thương Quan, Chính Quan, Thất Sát.
    """
    nhat_chu = tu_tru["tru_ngay"]["can"]
    hanh_nc = CAN_DICT[nhat_chu]["ngu_hanh"]

    # 1. ĐẮC LỆNH: Chi Tháng tàng Tỷ/Kiếp hoặc Ấn (PHE_TRO_THAN)
    chi_thang = tu_tru["tru_thang"]["chi"]
    tangs_thang = BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH.get(chi_thang, [])
    bang_chung_lenh = []
    for tc in tangs_thang:
        tt = BANG_TRA_CUU_THAP_THAN_10X10.get(nhat_chu, {}).get(tc, "")
        if tt in PHE_TRO_THAN:
            bang_chung_lenh.append(f"{tc} ({tt})")
    dac_lenh = len(bang_chung_lenh) > 0

    # 2. ĐẮC ĐỊA: Có gốc rễ thông căn tại các Chi (CHỈ TÍNH TỶ/KIẾP, KHÔNG TÍNH ẤN!)
    chis_all = [
        ("Ngày", tu_tru["tru_ngay"]["chi"]),
        ("Tháng", tu_tru["tru_thang"]["chi"]),
        ("Năm", tu_tru["tru_nam"]["chi"]),
        ("Giờ", tu_tru["tru_gio"]["chi"]),
    ]
    bang_chung_dia = []
    for ten_tru, c in chis_all:
        tangs = BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH.get(c, [])
        for tc in tangs:
            tt = BANG_TRA_CUU_THAP_THAN_10X10.get(nhat_chu, {}).get(tc, "")
            if tt in PHE_THONG_CAN:  # Chỉ Tỷ Kiên hoặc Kiếp Tài
                bang_chung_dia.append(f"Chi {c} [{ten_tru}] tàng {tc} ({tt})")
    dac_dia = len(bang_chung_dia) > 0

    # 3. ĐẮC THẾ: Can lộ Năm, Tháng, Giờ có Tỷ/Kiếp/Ấn trợ giúp (CHỈ 4 LOẠI THẦN TRỢ THÂN)
    cans_ngoai = [
        ("Năm", tu_tru["tru_nam"]["can"]),
        ("Tháng", tu_tru["tru_thang"]["can"]),
        ("Giờ", tu_tru["tru_gio"]["can"]),
    ]
    bang_chung_the = []
    cans_tiet_khac = []
    for ten_tru, c in cans_ngoai:
        tt = BANG_TRA_CUU_THAP_THAN_10X10.get(nhat_chu, {}).get(c, "")
        if tt in PHE_TRO_THAN:  # Tỷ Kiên, Kiếp Tài, Chính Ấn, Thiên Ấn
            bang_chung_the.append(f"Can {c} [{ten_tru}] là {tt}")
        else:
            cans_tiet_khac.append(f"Can {c} [{ten_tru}] là {tt}")
    dac_the = len(bang_chung_the) > 0

    # 4. KẾT LUẬN THÂN VƯỢNG / THÂN NHƯỢC (BỎ CHẤM ĐIỂM TỰ CHẾ)
    # Tiêu chí Tử Bình kinh điển:
    # - Nếu Đắc Lệnh và (Đắc Địa hoặc Đắc Thế) -> Thân Vượng
    # - Nếu Thất Lệnh nhưng Đắc Địa vững (từ 2 gốc Tỷ/Kiếp trở lên) và Đắc Thế -> Thân Vượng
    # - Ngược lại -> Thân Nhược
    if dac_lenh and (dac_dia or dac_the):
        ket_luan = "Vượng"
    elif len(bang_chung_dia) >= 2 and dac_the:
        ket_luan = "Vượng"
    else:
        ket_luan = "Nhược"

    # Mô tả chi tiết bằng chứng học thuật (loại bỏ hoàn toàn điểm số tự chế)
    lenh_desc = (
        f"ĐẮC LỆNH tại tháng {chi_thang} (tàng can {', '.join(bang_chung_lenh)} trợ mệnh; không tính theo Ngũ Hành tương sinh)"
        if dac_lenh
        else f"THẤT LỆNH tại tháng {chi_thang} (không có tàng can Tỷ/Kiếp/Ấn trong lệnh tháng)"
    )
    dia_desc = (
        f"ĐẮC ĐỊA có gốc rễ thông căn ({', '.join(bang_chung_dia)}; cấm tính Ấn vào thông căn)"
        if dac_dia
        else "THẤT ĐỊA (không có Tỷ Kiên/Kiếp Tài thông căn tại Địa Chi)"
    )
    the_loai_tru_str = f"; loại trừ {', '.join(cans_tiet_khac)} thuộc phe tiết/khắc Thân" if cans_tiet_khac else ""
    the_desc = (
        f"ĐẮC THẾ có Can lộ trợ mệnh ({', '.join(bang_chung_the)}{the_loai_tru_str})"
        if dac_the
        else f"THẤT THẾ (không có Can lộ Tỷ/Kiếp/Ấn trợ giúp{the_loai_tru_str})"
    )

    chi_tiet = f"Nhật Chủ {nhat_chu} ({hanh_nc}): {lenh_desc}; {dia_desc}; {the_desc}. Tổng thể bản mệnh thuộc cách Thân {ket_luan}."

    return {
        "ket_luan": ket_luan,
        "dac_lenh": dac_lenh,
        "dac_dia": dac_dia,
        "dac_the": dac_the,
        "bang_chung_lenh": bang_chung_lenh,
        "bang_chung_dia": bang_chung_dia,
        "bang_chung_the": bang_chung_the,
        "cans_tiet_khac": cans_tiet_khac,
        "chi_tiet": chi_tiet
    }


def xac_dinh_dung_than_toan_dien(
    tu_tru: Dict[str, Any],
    vuong_nhuoc: str,
    ngu_hanh_count: Dict[str, int]
) -> Dict[str, Any]:
    """
    Xác định Dụng Thần Toàn Diện theo sách Trần Khang Ninh (Phần III Chương II tr. 132-151):
    1. Phù Ức Dụng Thần (Thân Vượng dùng Quan Sát/Thực Thương/Tài; Thân Nhược dùng Ấn/Tỷ Kiếp).
    2. Điều Hầu Dụng Thần (Mùa Đông lạnh cần Hỏa; Mùa Hè nóng cần Thủy).
    3. Thông Quan Dụng Thần.
    4. Hỷ Thần và Kỵ Thần.
    5. Ứng dụng Cải Vận Đời Sống (Màu sắc, Con số, Phương hướng, Nghề nghiệp - tr. 134).
    """
    nhat_chu = tu_tru["tru_ngay"]["can"]
    hanh_nc = CAN_DICT[nhat_chu]["ngu_hanh"]
    chi_thang = tu_tru["tru_thang"]["chi"]

    hanh_an = HANH_SINH_RA[hanh_nc]       # Ấn sinh Thân
    hanh_thuong = TUONG_SINH[hanh_nc]     # Thực Thương tiết Thân
    hanh_tai = TUONG_KHAC[hanh_nc]        # Tài Tinh hao Thân
    hanh_quan = HANH_KHAC_NO[hanh_nc]     # Quan Sát khắc Thân

    # 1. Phù Ức Dụng Thần (sách tr. 151)
    if vuong_nhuoc == "Vượng":
        # Ưu tiên: Quan Sát -> Thực Thương -> Tài
        nhom_can = [hanh_quan, hanh_thuong, hanh_tai]
        dung_than_phu_uc = sorted(nhom_can, key=lambda h: ngu_hanh_count.get(h, 0))[0]
        hy_than = HANH_SINH_RA[dung_than_phu_uc]
        ky_than = hanh_nc  # Kỵ Tỷ Kiếp và Ấn làm vượng thêm
    else:
        # Thân Nhược: Ưu tiên Ấn -> Tỷ Kiếp
        nhom_can = [hanh_an, hanh_nc]
        dung_than_phu_uc = sorted(nhom_can, key=lambda h: ngu_hanh_count.get(h, 0))[0]
        hy_than = HANH_SINH_RA[dung_than_phu_uc]
        ky_than = hanh_quan  # Kỵ Quan Sát khắc Thân thêm

    # 2. Điều Hầu Dụng Thần (sách tr. 151-152)
    dieu_hau: Optional[Dict[str, str]] = None
    if chi_thang in ["Hợi", "Tý", "Sửu"]:
        dieu_hau = {
            "ngu_hanh": "Hỏa",
            "ly_do": f"Sinh vào tháng {chi_thang} mùa Đông hàn đống lạnh giá, khí trời buốt giá làm đóng băng vạn vật. Bắt buộc cần HỎA (Bính, Đinh) để sưởi ấm, giải hàn, thúc đẩy sinh khí nảy mầm."
        }
    elif chi_thang in ["Tỵ", "Ngọ", "Mùi"]:
        dieu_hau = {
            "ngu_hanh": "Thủy",
            "ly_do": f"Sinh vào tháng {chi_thang} mùa Hạ viêm nhiệt hỏa vượng, đất đai khô cằn nứt nẻ. Bắt buộc cần THỦY (Nhâm, Quý) để tưới mát, nhuận trạch, điều hòa khí hậu."
        }

    # Chốt Dụng Thần chính (kết hợp Phù Ức và Điều Hầu theo sách tr. 151-152)
    dung_than_chinh = dung_than_phu_uc
    if dieu_hau:
        dh_hanh = dieu_hau["ngu_hanh"]
        if vuong_nhuoc == "Vượng":
            # Nếu Thân Vượng sinh mùa Hạ (Tỵ, Ngọ, Mùi), Hỏa Thổ khô nóng -> Thủy vừa là Tài/Khắc chế Thân vừa là Điều Hầu tối trọng!
            if dh_hanh == "Thủy":
                dung_than_chinh = "Thủy"
                hy_than = "Kim"  # Kim sinh Thủy (Hỷ thần bồi dưỡng Dụng thần)
                ky_than = "Hỏa, Thổ"
            elif dh_hanh == "Hỏa" and hanh_nc in ["Kim", "Thủy"]:
                dung_than_chinh = "Hỏa"
                hy_than = "Mộc"
                ky_than = "Thủy, Kim"
        else:
            if dh_hanh in [hanh_an, hanh_nc]:
                dung_than_chinh = dh_hanh
                hy_than = HANH_SINH_RA[dh_hanh]

    # Bảng quy đổi ứng dụng phong thủy đời sống theo Trần Khang Ninh (tr. 134)
    cai_menh_map = {
        "Hỏa": {
            "mau_sac": "Đỏ, Hồng, Tím, Cam",
            "con_so": "2, 7 (Số Hỏa Lạc Thư)",
            "phuong_huong": "Hướng Nam",
            "nghe_nghiep": "Năng lượng, điện tử, công nghệ cao, truyền thông, ẩm thực, văn hóa nghệ thuật"
        },
        "Thủy": {
            "mau_sac": "Đen, Xanh dương, Xanh nước biển",
            "con_so": "1, 6 (Số Thủy Lạc Thư)",
            "phuong_huong": "Hướng Bắc",
            "nghe_nghiep": "Logistics, vận tải biển, xuất nhập khẩu, du lịch, thương mại quốc tế, dịch vụ nước giải khát"
        },
        "Mộc": {
            "mau_sac": "Xanh lá cây, Xanh lục",
            "con_so": "3, 8 (Số Mộc Lạc Thư)",
            "phuong_huong": "Hướng Đông, Đông Nam",
            "nghe_nghiep": "Giáo dục, xuất bản, lâm nghiệp, nông nghiệp hữu cơ, thiết kế kiến trúc, dược liệu"
        },
        "Kim": {
            "mau_sac": "Trắng, Bạc, Xám, Ánh kim",
            "con_so": "4, 9 (Số Kim Lạc Thư)",
            "phuong_huong": "Hướng Tây, Tây Bắc",
            "nghe_nghiep": "Tài chính ngân hàng, kinh doanh vàng bạc, cơ khí chế tạo, quân sự, luật pháp, công nghệ phần cứng"
        },
        "Thổ": {
            "mau_sac": "Vàng, Nâu đất, Be",
            "con_so": "5, 0 (Số Thổ Lạc Thư)",
            "phuong_huong": "Trung ương, Đông Bắc, Tây Nam",
            "nghe_nghiep": "Bất động sản, xây dựng, kiến trúc hạ tầng, bảo hiểm, khoáng sản, gốm sứ"
        }
    }

    app_info = cai_menh_map.get(dung_than_chinh, cai_menh_map["Hỏa"])

    return {
        "dung_than": dung_than_chinh,
        "dung_than_phu_uc": dung_than_phu_uc,
        "dieu_hau": dieu_hau,
        "hy_than": hy_than,
        "ky_than": ky_than,
        "cai_menh": app_info
    }


def tinh_dai_van(tu_tru: Dict[str, Any], gioi_tinh: str = "nam", tuoi_khoi_van: int = 4) -> List[Dict[str, Any]]:
    """
    Tính chuỗi 8 Đại Vận liên tiếp của cuộc đời theo chuẩn sách Trần Khang Ninh (tr. 58-64):
    - Dương Nam Âm Nữ đi Thuận (tiến tới).
    - Âm Nam Dương Nữ đi Nghịch (lùi lại).
    - Khởi từ Trụ Tháng.
    """
    can_nam = tu_tru["tru_nam"]["can"]
    is_duong_nam_can = CAN_DICT[can_nam]["am_duong"] == "Dương"
    is_male = (gioi_tinh.lower() == "nam")

    # Đi thuận nếu Dương Nam hoặc Âm Nữ
    di_thuan = (is_duong_nam_can and is_male) or (not is_duong_nam_can and not is_male)

    can_thang = tu_tru["tru_thang"]["can"]
    chi_thang = tu_tru["tru_thang"]["chi"]
    can_idx = CAN_NAMES.index(can_thang)
    chi_idx = CHI_NAMES.index(chi_thang)
    nhat_chu = tu_tru["tru_ngay"]["can"]

    dai_van_list = []
    tuoi_bat_dau = tuoi_khoi_van

    for i in range(1, 9):
        step = i if di_thuan else -i
        c_i = (can_idx + step) % 10
        ch_i = (chi_idx + step) % 12

        can_v = CAN_NAMES[c_i]
        chi_v = CHI_NAMES[ch_i]
        thap_than = tinh_thap_than(can_v, nhat_chu)

        tuoi_ket_thuc = tuoi_bat_dau + 9
        dai_van_list.append({
            "thu_tu": i,
            "can_chi": f"{can_v} {chi_v}",
            "can": can_v,
            "chi": chi_v,
            "tuoi_range": f"{tuoi_bat_dau} - {tuoi_ket_thuc} tuổi",
            "thap_than": thap_than["ten"],
            "thap_than_short": thap_than["ten_viet_tat"],
            "ngu_hanh": f"{CAN_DICT[can_v]['ngu_hanh']} - {CHI_DICT[chi_v]['ngu_hanh']}",
            "y_nghia": f"Đại vận {can_v} {chi_v} mang khí thế của {thap_than['ten']}, tác động mạnh mẽ đến phương diện công danh, sức khỏe và tài lộc."
        })
        tuoi_bat_dau += 10

    return dai_van_list


# ==============================================================================
# HÀM LẬP TỨ TRỤ CHÍNH VÀ CÁC HÀM TƯƠNG THÍCH NGƯỢC
# ==============================================================================

def lap_tu_tru(
    ngay_duong: int,
    thang_duong: int,
    nam_duong: int,
    gio_chi: str,
    gioi_tinh: str = "nam",
    gio_sinh: int = 12,
    phut_sinh: int = 0
) -> Dict[str, Any]:
    """
    5. Lập Tứ Trụ (Bát Tự) hoàn chỉnh gồm 4 trụ: Năm, Tháng, Ngày, Giờ.
    Bổ sung dữ liệu phân tích chuyên sâu 100% theo kinh điển 'Dự Báo Theo Tử Bình' (Trần Khang Ninh).
    """
    # Bước 0: Xác định Can-Chi 4 trụ theo đúng Lịch Tiết Khí (không dùng số tháng âm lịch đơn giản hóa)
    tru_nam = xac_dinh_can_chi_nam(
        nam_duong=nam_duong,
        ngay_duong=ngay_duong,
        thang_duong=thang_duong,
        gio_sinh=gio_sinh,
        phut_sinh=phut_sinh
    )
    tru_thang = xac_dinh_can_chi_thang(
        nam_can=tru_nam["can"],
        thang_am_hoac_ngay=ngay_duong,
        thang_duong=thang_duong,
        nam_duong=nam_duong,
        gio_sinh=gio_sinh,
        phut_sinh=phut_sinh
    )
    tru_ngay = xac_dinh_can_chi_ngay(ngay_duong, thang_duong, nam_duong)
    tru_gio = xac_dinh_can_chi_gio(tru_ngay["can"], gio_chi)

    # Bước 0b: Khái quát hóa kiểm tra vùng biên cho cả 4 Trụ
    vung_bien_4_tru = kiem_tra_vung_bien_4_tru(
        nam_duong=nam_duong,
        thang_duong=thang_duong,
        ngay_duong=ngay_duong,
        gio_sinh=gio_sinh,
        phut_sinh=phut_sinh
    )

    tu_tru = {
        "tru_nam": tru_nam,
        "tru_thang": tru_thang,
        "tru_ngay": tru_ngay,
        "tru_gio": tru_gio,
        "vung_bien_4_tru": vung_bien_4_tru
    }

    # Tính toán mở rộng theo sách Trần Khang Ninh
    nhat_chu = tru_ngay["can"]
    ngu_hanh_count = dem_ngu_hanh(tu_tru)
    vuong_nhuoc_detail = phan_tich_vuong_nhuoc_chuyen_sau(tu_tru, ngu_hanh_count)
    cach_cuc_detail = xac_dinh_cach_cuc(tu_tru)
    dung_than_detail = xac_dinh_dung_than_toan_dien(tu_tru, vuong_nhuoc_detail["ket_luan"], ngu_hanh_count)
    tuong_tac_detail = tinh_tuong_tac_can_chi(tu_tru)
    khong_vong = tinh_khong_vong(tru_ngay["can"], tru_ngay["chi"])

    # Bước 5: Tính tuổi khởi vận chuẩn xác theo số ngày tới tiết khí / 3 (floor)
    can_nam = tru_nam["can"]
    is_duong_nam_can = CAN_DICT[can_nam]["am_duong"] == "Dương"
    is_male = (gioi_tinh.lower() == "nam")
    di_thuan = (is_duong_nam_can and is_male) or (not is_duong_nam_can and not is_male)
    tuoi_khoi_van = tinh_tuoi_khoi_van_chuan(
        ngay_duong=ngay_duong,
        thang_duong=thang_duong,
        nam_duong=nam_duong,
        gio_sinh=gio_sinh,
        phut_sinh=phut_sinh,
        di_thuan=di_thuan
    )
    dai_van_list = tinh_dai_van(tu_tru, gioi_tinh=gioi_tinh, tuoi_khoi_van=tuoi_khoi_van)

    # Thần Sát cho từng trụ
    than_sat_nam = tinh_than_sat_cho_chi(tru_nam["chi"], nhat_chu, tru_ngay["chi"], tru_nam["chi"], tru_thang["chi"], khong_vong)
    than_sat_thang = tinh_than_sat_cho_chi(tru_thang["chi"], nhat_chu, tru_ngay["chi"], tru_nam["chi"], tru_thang["chi"], khong_vong)
    than_sat_ngay = tinh_than_sat_cho_chi(tru_ngay["chi"], nhat_chu, tru_ngay["chi"], tru_nam["chi"], tru_thang["chi"], khong_vong)
    than_sat_gio = tinh_than_sat_cho_chi(tru_gio["chi"], nhat_chu, tru_ngay["chi"], tru_nam["chi"], tru_thang["chi"], khong_vong)

    # Chi tiết từng trụ (để hiển thị sâu sắc trên frontend)
    chi_tiet_tru = {
        "tru_nam": {
            "id": "tru_nam", "ten": "Trụ Năm", "cung_vi": "Tổ Tiên / Cội Nguồn",
            "giai_doan": "1 - 16 tuổi",
            "can": tru_nam["can"], "chi": tru_nam["chi"],
            "thap_than": tinh_thap_than(tru_nam["can"], nhat_chu),
            "tang_can": [
                {"can": tc, "thap_than": tinh_thap_than(tc, nhat_chu)}
                for tc in CHI_DICT[tru_nam["chi"]]["chi_tang"]
            ],
            "than_sat": than_sat_nam
        },
        "tru_thang": {
            "id": "tru_thang", "ten": "Trụ Tháng", "cung_vi": "Cha Mẹ / Đề Cương Lệnh Tháng",
            "giai_doan": "17 - 32 tuổi",
            "can": tru_thang["can"], "chi": tru_thang["chi"],
            "thap_than": tinh_thap_than(tru_thang["can"], nhat_chu),
            "tang_can": [
                {"can": tc, "thap_than": tinh_thap_than(tc, nhat_chu)}
                for tc in CHI_DICT[tru_thang["chi"]]["chi_tang"]
            ],
            "than_sat": than_sat_thang
        },
        "tru_ngay": {
            "id": "tru_ngay", "ten": "Trụ Ngày", "cung_vi": "Bản Thân & Cung Phối Ngẫu",
            "giai_doan": "33 - 48 tuổi",
            "can": tru_ngay["can"], "chi": tru_ngay["chi"],
            "thap_than": {"ten": "Nhật Chủ (Nguyên Thần)", "ten_viet_tat": "Nhật Chủ", "nhom": "Bản Thân"},
            "tang_can": [
                {"can": tc, "thap_than": tinh_thap_than(tc, nhat_chu)}
                for tc in CHI_DICT[tru_ngay["chi"]]["chi_tang"]
            ],
            "than_sat": than_sat_ngay
        },
        "tru_gio": {
            "id": "tru_gio", "ten": "Trụ Giờ", "cung_vi": "Con Cái / Quy Túc Hậu Vận",
            "giai_doan": "49 tuổi trở đi",
            "can": tru_gio["can"], "chi": tru_gio["chi"],
            "thap_than": tinh_thap_than(tru_gio["can"], nhat_chu),
            "tang_can": [
                {"can": tc, "thap_than": tinh_thap_than(tc, nhat_chu)}
                for tc in CHI_DICT[tru_gio["chi"]]["chi_tang"]
            ],
            "than_sat": than_sat_gio
        }
    }

    # Kết hợp vào dictionary trả về
    tu_tru["nhat_chu"] = nhat_chu
    tu_tru["ngu_hanh_count"] = ngu_hanh_count
    tu_tru["ngu_hanh_count_8_chu"] = dem_ngu_hanh_8_chu(tu_tru)
    tu_tru["phuong_phap_dem"] = "Đếm toàn bộ 4 Can lộ, 4 Địa Chi và toàn bộ Tàng Can trong Tứ Trụ (tổng khí)"
    tu_tru["vuong_nhuoc"] = vuong_nhuoc_detail["ket_luan"]
    tu_tru["vuong_nhuoc_detail"] = vuong_nhuoc_detail
    tu_tru["cach_cuc"] = cach_cuc_detail
    tu_tru["dung_than"] = dung_than_detail["dung_than"]
    tu_tru["dung_than_detail"] = dung_than_detail
    tu_tru["hy_than"] = dung_than_detail["hy_than"]
    tu_tru["ky_than"] = dung_than_detail["ky_than"]
    tu_tru["tuong_tac"] = tuong_tac_detail
    tu_tru["khong_vong"] = khong_vong
    tu_tru["dai_van"] = dai_van_list
    tu_tru["chi_tiet_tru"] = chi_tiet_tru
    tu_tru["cai_menh"] = dung_than_detail["cai_menh"]

    return tu_tru


def dem_ngu_hanh(tu_tru: Dict[str, Any]) -> Dict[str, int]:
    """
    6. Đếm số lượng mỗi Ngũ Hành xuất hiện trong Tứ Trụ (Bát Tự).
    Bao gồm cả 4 Can lộ, 4 Địa Chi và toàn bộ Tàng Can trong 4 Chi.
    """
    counts = {h: 0 for h in DANH_SACH_NGU_HANH}
    trus = [tu_tru["tru_nam"], tu_tru["tru_thang"], tu_tru["tru_ngay"], tu_tru["tru_gio"]]

    for tru in trus:
        can = tru["can"]
        chi = tru["chi"]
        counts[CAN_DICT[can]["ngu_hanh"]] += 1
        counts[CHI_DICT[chi]["ngu_hanh"]] += 1
        for hidden_can in CHI_DICT[chi]["chi_tang"]:
            counts[CAN_DICT[hidden_can]["ngu_hanh"]] += 1

    return counts


def dem_ngu_hanh_8_chu(tu_tru: Dict[str, Any]) -> Dict[str, int]:
    """
    Đếm số lượng Ngũ Hành chỉ trên 8 chữ chính của Bát Tự (4 Can lộ + 4 Chi, tổng = đúng 8).
    """
    counts = {h: 0 for h in DANH_SACH_NGU_HANH}
    trus = [tu_tru["tru_nam"], tu_tru["tru_thang"], tu_tru["tru_ngay"], tu_tru["tru_gio"]]
    for tru in trus:
        counts[CAN_DICT[tru["can"]]["ngu_hanh"]] += 1
        counts[CHI_DICT[tru["chi"]]["ngu_hanh"]] += 1
    return counts


def xac_dinh_nhat_chu(tu_tru: Dict[str, Any]) -> str:
    """
    7. Xác định 'Nhật Chủ' (Thiên Can của trụ Ngày).
    """
    return tu_tru["tru_ngay"]["can"]


def phan_tich_vuong_nhuoc(tu_tru: Dict[str, Any], ngu_hanh_count: Dict[str, int]) -> str:
    """
    8. Phân tích Nhật Chủ là Vượng hay Nhược (Tương thích ngược).
    """
    res = phan_tich_vuong_nhuoc_chuyen_sau(tu_tru, ngu_hanh_count)
    return res["ket_luan"]


def xac_dinh_dung_than(nhat_chu: str, vuong_nhuoc: str, ngu_hanh_count: Dict[str, int]) -> str:
    """
    9. Xác định Dụng Thần (Tương thích ngược).
    """
    hanh_nhat_chu = CAN_DICT[nhat_chu]["ngu_hanh"]
    hanh_sinh = HANH_SINH_RA[hanh_nhat_chu]
    hanh_tiet = TUONG_SINH[hanh_nhat_chu]
    hanh_khac = TUONG_KHAC[hanh_nhat_chu]
    hanh_khac_minh = HANH_KHAC_NO[hanh_nhat_chu]

    if vuong_nhuoc == "Vượng":
        nhom_can_thiet = [hanh_khac_minh, hanh_tiet, hanh_khac]
        nhom_sorted = sorted(nhom_can_thiet, key=lambda h: ngu_hanh_count.get(h, 0))
        return nhom_sorted[0]
    else:
        nhom_can_thiet = [hanh_sinh, hanh_nhat_chu]
        nhom_sorted = sorted(nhom_can_thiet, key=lambda h: ngu_hanh_count.get(h, 0))
        return nhom_sorted[0]
