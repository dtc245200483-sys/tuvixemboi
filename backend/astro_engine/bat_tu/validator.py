# -*- coding: utf-8 -*-
"""
Module Kiểm Định & Chuẩn Hóa Toàn Diện Luận Giải Bát Tự Tứ Trụ
Căn cứ bắt buộc: Sách 'Dự Báo Theo Tử Bình' - Trần Khang Ninh (2006):
- Trang 30: Bảng Địa Chi Tàng Độn duy nhất (Single Source of Truth) cho 12 Địa Chi.
- Trang 31: Bảng Tra Cứu Thập Thần 10x10 cố định & Quy tắc Nhật Chủ không gán Thập Thần.
"""

import re
from typing import Dict, Any, List
from astro_engine.bat_tu.constants.can_chi import (
    BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH,
    BANG_TRA_CUU_THAP_THAN_10X10,
    DANH_SACH_10_THAP_THAN_CHUAN,
    CAN_DICT,
    CHI_DICT,
    PHE_TRO_THAN,
    PHE_THONG_CAN,
    PHE_TIET_KHAC_THAN,
    BANG_LOC_VI_10_CAN,
    BANG_DUONG_NHAN_10_CAN
)

# Ý nghĩa đời thường phong phú cho người mới học (thuần Việt, không chữ Hán, không tiếng Anh)
Y_NGHIA_THAP_THAN_DOI_THUONG: Dict[str, str] = {
    "Tỷ Kiên": "Ý chí tự lập, tính tình thẳng thắn, có bạn bè tri kỷ và anh em đồng lòng trợ giúp.",
    "Kiếp Tài": "Bản lĩnh xông pha, dám nghĩ dám làm, tinh thần cạnh tranh cao, thích thử thách mới.",
    "Thực Thần": "Phúc lộc tự nhiên, tính hòa nhã, có năng khiếu ẩm thực, nghệ thuật, khả năng sinh tài bền vững.",
    "Thương Quan": "Tư duy sáng tạo vượt trội, tài ăn nói lưu loát, năng động, ghét sự gò bó rập khuôn.",
    "Chính Tài": "Tài chính ổn định, tích lũy từ công sức lao động chân chính, tính tình cẩn trọng, chu toàn.",
    "Thiên Tài": "Nhạy bén với cơ hội kinh doanh, có duyên đắc tài lộc bất ngờ, tính phóng khoáng, hào sảng.",
    "Chính Quan": "Tinh thần trách nhiệm, trọng kỷ cương, danh dự thanh cao, có uy tín và năng lực quản lý.",
    "Thất Sát": "Khí phách kiên cường, quyết đoán, dám đương đầu áp lực, có tố chất lãnh đạo và quyền uy.",
    "Chính Ấn": "Được gia đình và bề trên bao bọc, có quý nhân phò trợ, coi trọng học vấn và danh tiếng.",
    "Thiên Ấn": "Trí tuệ đặc biệt, trực giác nhạy bén, đam mê nghiên cứu chuyên sâu, nghệ thuật hoặc huyền học."
}


def tao_noi_dung_chuan_muc_2(tu_tru: Dict[str, Any]) -> str:
    """
    Sinh chuẩn xác 100% nội dung Mục II (Tứ Trụ & Thập Thần) trực tiếp từ bảng tra cứu
    cố định trang 30-31 sách Trần Khang Ninh, không phụ thuộc vào việc AI có bịa hay không.
    """
    tru_nam = tu_tru.get("tru_nam") or {}
    tru_thang = tu_tru.get("tru_thang") or {}
    tru_ngay = tu_tru.get("tru_ngay") or {}
    tru_gio = tu_tru.get("tru_gio") or {}
    nhat_chu = tru_ngay.get("can", "")

    lines = ["• Mục II. Tứ Trụ & Ý nghĩa các Thần (Thập Thần lộ và tàng)"]

    trus_info = [
        ("Trụ Năm", tru_nam, "Tổ tiên, cội nguồn và thời niên thiếu (1 - 16 tuổi)"),
        ("Trụ Tháng", tru_thang, "Cha mẹ, lệnh tháng đắc thời và thời thanh niên (17 - 32 tuổi)"),
        ("Trụ Ngày", tru_ngay, "Bản thân người mang mệnh & hôn nhân gia đạo (33 - 48 tuổi)"),
        ("Trụ Giờ", tru_gio, "Con cái, sự nghiệp hậu vận và tuổi già (49 tuổi trở đi)")
    ]

    for ten_tru, tr, mo_ta_tru in trus_info:
        c_lo = tr.get("can", "")
        ch_lo = tr.get("chi", "")
        lines.append(f"  - {ten_tru} ({c_lo} {ch_lo}) – Đại diện cho {mo_ta_tru}:")

        # 1. Can lộ
        if ten_tru == "Trụ Ngày":
            lines.append(
                f"    * Can lộ: **{c_lo} (Nhật Chủ / Nguyên Thần)** – Đại diện cho chính bản thân người mang mệnh. "
                f"Đặc trưng tính cách kiên định, chịu đựng bền bỉ và giữ vai trò trung tâm điều phối toàn bộ lá số."
            )
        else:
            tt_lo = BANG_TRA_CUU_THAP_THAN_10X10.get(nhat_chu, {}).get(c_lo, "")
            y_nghia_lo = Y_NGHIA_THAP_THAN_DOI_THUONG.get(tt_lo, "")
            lines.append(
                f"    * Can lộ: **{c_lo}** – Đóng vai trò là **{tt_lo}**: {y_nghia_lo}"
            )

        # 2. Chi tàng (đúng 100% nguyên văn trang 30)
        tangs = BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH.get(ch_lo, [])
        tang_strs = []
        for tc in tangs:
            tt_tang = BANG_TRA_CUU_THAP_THAN_10X10.get(nhat_chu, {}).get(tc, "")
            y_nghia_tang = Y_NGHIA_THAP_THAN_DOI_THUONG.get(tt_tang, "")
            tang_strs.append(f"**{tc} ({tt_tang})**: {y_nghia_tang}")

        lines.append(f"    * Chi tàng trong **{ch_lo}** (theo sách Trần Khang Ninh, tr.30):")
        for ts in tang_strs:
            lines.append(f"      + {ts}")

    return "\n".join(lines)


def tao_noi_dung_chuan_muc_4(tu_tru: Dict[str, Any]) -> str:
    """
    Sinh chuẩn xác 100% nội dung Mục IV (Đánh giá Khí Lực Bản Thân Thân Vượng/Nhược):
    - Tuyệt đối không dùng điểm số tự chế (CẤM 40/35/20, CẤM điểm Lệnh/Địa/Thế).
    - Đắc Lệnh: Nêu đích danh tàng can Chi Tháng trợ Thân, cấm nói chung chung theo Ngũ Hành tương sinh.
    - Đắc Địa: Nêu đích danh từng Chi nào tàng can nào cùng hành làm gốc rễ thông căn (Tỷ/Kiếp), TUYỆT ĐỐI KHÔNG TÍNH ẤN!
    - Đắc Thế: Chỉ liệt kê Can lộ Năm, Tháng, Giờ thuộc PHE_TRO_THAN (Tỷ/Kiếp/Ấn), TUYỆT ĐỐI CẤM Tài/Quan/Sát/Thực/Thương (loại bỏ hoàn toàn Quý)!
    """
    tru_ngay = tu_tru.get("tru_ngay") or {}
    tru_thang = tu_tru.get("tru_thang") or {}
    tru_nam = tu_tru.get("tru_nam") or {}
    tru_gio = tu_tru.get("tru_gio") or {}
    nhat_chu = tru_ngay.get("can", "")

    vn_detail = tu_tru.get("vuong_nhuoc_detail") or {}
    ket_luan = vn_detail.get("ket_luan") or tu_tru.get("vuong_nhuoc", "Vượng")

    # 1. Đắc Lệnh (Bằng chứng cụ thể theo tàng can lệnh tháng)
    chi_thang = tru_thang.get("chi", "")
    tangs_thang = BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH.get(chi_thang, [])
    bang_chung_lenh = [
        f"{tc} ({BANG_TRA_CUU_THAP_THAN_10X10.get(nhat_chu, {}).get(tc, '')})"
        for tc in tangs_thang
        if BANG_TRA_CUU_THAP_THAN_10X10.get(nhat_chu, {}).get(tc) in PHE_TRO_THAN
    ]
    dac_lenh = len(bang_chung_lenh) > 0

    # 2. Đắc Địa (Thông Căn: CHỈ TÍNH TỶ/KIẾP CÙNG HÀNH, KHÔNG BAO GIỜ TÍNH ẤN!)
    chis_all = [
        ("Năm", tru_nam.get("chi", "")),
        ("Tháng", tru_thang.get("chi", "")),
        ("Ngày", tru_ngay.get("chi", "")),
        ("Giờ", tru_gio.get("chi", "")),
    ]
    bang_chung_dia = []
    for ten_tru, c in chis_all:
        if not c:
            continue
        tangs = BANG_DIA_CHI_TANG_CAN_TRAN_KHANG_NINH.get(c, [])
        for tc in tangs:
            tt = BANG_TRA_CUU_THAP_THAN_10X10.get(nhat_chu, {}).get(tc, "")
            if tt in PHE_THONG_CAN:  # Chỉ Tỷ Kiên hoặc Kiếp Tài
                bang_chung_dia.append(f"Chi {c} [{ten_tru}] tàng {tc} ({tt})")
    dac_dia = len(bang_chung_dia) > 0

    # 3. Đắc Thế (CHỈ TÍNH 4 LOẠI THẦN TRỢ THÂN, CẤM TÀI/QUAN/THỰC/THƯƠNG!)
    cans_ngoai = [
        ("Năm", tru_nam.get("can", "")),
        ("Tháng", tru_thang.get("can", "")),
        ("Giờ", tru_gio.get("can", "")),
    ]
    bang_chung_the = []
    cans_tiet_khac = []
    for ten_tru, c in cans_ngoai:
        if not c:
            continue
        tt = BANG_TRA_CUU_THAP_THAN_10X10.get(nhat_chu, {}).get(c, "")
        if tt in PHE_TRO_THAN:  # Tỷ Kiên, Kiếp Tài, Chính Ấn, Thiên Ấn
            bang_chung_the.append(f"Can {c} [{ten_tru}] là {tt}")
        else:
            cans_tiet_khac.append(f"Can {c} [{ten_tru}] là {tt}")
    dac_the = len(bang_chung_the) > 0

    lines = [
        "• Mục IV. Đánh giá Khí Lực Bản Thân (Thân Vượng hay Thân Nhược)",
        f"  - Kết luận: **Thân {ket_luan}** (theo chuẩn mực thẩm định Tử Bình Trần Khang Ninh).",
        "  - Bằng chứng đối chiếu 3 tiêu chuẩn cốt lõi (tuyệt đối không dùng điểm số tự chế):"
    ]

    # Dòng Đắc Lệnh
    if dac_lenh:
        lines.append(f"    * **Đắc Lệnh: CÓ** – Chi Tháng **{chi_thang}** tàng can {', '.join(bang_chung_lenh)} trợ mệnh (bằng chứng cụ thể theo tàng can lệnh tháng, không suy diễn chung chung theo Ngũ Hành tương sinh).")
    else:
        lines.append(f"    * **Đắc Lệnh: KHÔNG (Thất Lệnh)** – Chi Tháng **{chi_thang}** không có tàng can Tỷ/Kiếp hoặc Ấn của Nhật Chủ.")

    # Dòng Đắc Địa
    if dac_dia:
        lines.append(f"    * **Đắc Địa: CÓ GỐC RỄ THÔNG CĂN** – Nhật Chủ **{nhat_chu}** tìm thấy gốc rễ Tỷ/Kiếp cùng hành tại: {', '.join(bang_chung_dia)} (chỉ tính đích danh tàng can Tỷ Kiên, Kiếp Tài; Ấn Tinh không tính vào thông căn; tuyệt đối không nói chung chung 'các Chi đều chứa thần hỗ trợ').")
    else:
        lines.append(f"    * **Đắc Địa: KHÔNG (Thất Địa)** – Không có Tỷ Kiên hoặc Kiếp Tài cùng hành thông căn tại các Địa Chi (gốc rễ chưa sâu).")

    # Dòng Đắc Thế
    if dac_the:
        the_str = f"    * **Đắc Thế: CÓ THIÊN CAN TRỢ GIÚP** – Trên các Thiên Can lộ có thần trợ thân: {', '.join(bang_chung_the)} (chỉ tính Tỷ Kiên, Kiếp Tài, Chính Ấn, Thiên Ấn)."
        if cans_tiet_khac:
            the_str += f" Các Can còn lại ({', '.join(cans_tiet_khac)}) thuộc phe tiết/khắc Thân, tuyệt đối không tính vào Đắc Thế."
        lines.append(the_str)
    else:
        the_str = "    * **Đắc Thế: KHÔNG (Thất Thế)** – Các Thiên Can lộ không có Tỷ/Kiếp/Ấn trợ giúp."
        if cans_tiet_khac:
            the_str += f" Toàn bộ các Can lộ ({', '.join(cans_tiet_khac)}) đều thuộc phe tiết/khắc Thân."
        lines.append(the_str)

    # Ý nghĩa tính cách và sức chịu đựng
    if ket_luan == "Vượng":
        lines.append(
            f"  - Ý nghĩa thực tế: Người mang bản mệnh Thân Vượng sở hữu nội lực dồi dào, tính cách kiên định, quyết đoán, "
            f"có sức chịu đựng áp lực rất lớn trong cuộc sống và sự nghiệp. Bản mệnh đủ sức gánh vác Tài lộc và Quan chức lớn, "
            f"thích hợp làm người tiên phong, mở lối lập nghiệp."
        )
    else:
        lines.append(
            f"  - Ý nghĩa thực tế: Người mang bản mệnh Thân Nhược có tính tình mềm mỏng, linh hoạt, trực giác nhạy cảm, "
            f"giàu lòng nhân ái. Khi đối diện áp lực lớn cần dựa vào sự trợ giúp của tập thể, bạn bè (Tỷ Kiếp) và sự chỉ dẫn "
            f"của bề trên, học vấn (Ấn Tinh) để đón nhận tài lộc vững chắc."
        )

    return "\n".join(lines)


def tao_noi_dung_chuan_muc_5(tu_tru: Dict[str, Any]) -> str:
    """
    Sinh chuẩn xác 100% nội dung Mục V (Định danh Cách Cục lá số):
    - Kiến Lộc Cách: Nhật Chủ [Can] đắc Lộc tại Chi Tháng [Chi] (theo bảng Lộc vị 10 dòng cố định).
      TUYỆT ĐỐI KHÔNG dùng cụm 'Tỷ Kiên thấu lên Thiên Can'.
    - Dương Nhận Cách: Nhật Chủ [Can] đắc Kình Dương tại Chi Tháng [Chi].
    """
    tru_ngay = tu_tru.get("tru_ngay") or {}
    tru_thang = tu_tru.get("tru_thang") or {}
    nhat_chu = tru_ngay.get("can", "")
    chi_thang = tru_thang.get("chi", "")

    cach_cuc = tu_tru.get("cach_cuc") or {}
    ten_cach = cach_cuc.get("ten_cach", "")

    # Kiểm tra Lộc vị
    if BANG_LOC_VI_10_CAN.get(nhat_chu) == chi_thang:
        return (
            f"• Mục V. Định danh Cách Cục lá số\n"
            f"  - Tên cách cục: **Kiến Lộc Cách** (thuộc hàng thượng cách trong Tử Bình).\n"
            f"  - Căn cứ xác lập: Nhật Chủ **{nhat_chu}** đắc Lộc tại Chi Tháng **{chi_thang}** "
            f"(đối chiếu đúng bảng Lộc vị 10 dòng kinh điển Tử Bình Trần Khang Ninh).\n"
            f"  - Ý nghĩa tài năng & sự nghiệp: Thân thể tráng kiện, tài lộc và công danh do tự thân nỗ lực phấn đấu "
            f"gây dựng nên, có chí tự lập rất cao, không trông chờ ỷ lại vào phúc ấm sẵn có."
        )

    if BANG_DUONG_NHAN_10_CAN.get(nhat_chu) == chi_thang:
        return (
            f"• Mục V. Định danh Cách Cục lá số\n"
            f"  - Tên cách cục: **Dương Nhận Cách**.\n"
            f"  - Căn cứ xác lập: Nhật Chủ **{nhat_chu}** đắc Kình Dương tại Chi Tháng **{chi_thang}**.\n"
            f"  - Ý nghĩa tài năng & sự nghiệp: Tính khí dũng cảm, quả quyết, có khí phách hiên ngang, dám nghĩ dám làm, "
            f"thích hợp với môi trường kỷ luật, lãnh đạo hoặc kinh doanh quyết liệt."
        )

    mo_ta = cach_cuc.get("mo_ta", "Cách cục điều phối vận mệnh đời người.")
    thau = cach_cuc.get("thau_can", "Chính Cách")
    return (
        f"• Mục V. Định danh Cách Cục lá số\n"
        f"  - Tên cách cục: **{ten_cach or 'Chính Cách Bát Tự'}** ({thau}).\n"
        f"  - Căn cứ xác lập: Được định từ Đề Cương Lệnh Tháng **{chi_thang}** phối chiếu Thiên Can.\n"
        f"  - Ý nghĩa tài năng & sự nghiệp: {mo_ta}"
    )


def kiem_tra_va_chuan_hoa_luan_giai_bat_tu(noi_dung_ai: str, tu_tru: Dict[str, Any]) -> str:
    """
    Kiểm tra và tự động chuẩn hóa bài luận giải Bát Tự trước khi lưu vào Cache hoặc trả về cho client:
    1. Chuẩn hóa Mục II (Tứ Trụ & Thập Thần): Lấy đúng 100% từ bảng tra cứu 10x10 và bảng tàng can tr.30.
    2. Chuẩn hóa Mục IV (Đánh giá Khí Lực Thân Vượng/Nhược):
       - Đắc Lệnh: Nêu rõ tàng can cụ thể, cấm suy diễn theo ngũ hành tương sinh.
       - Đắc Địa: Chỉ Tỷ/Kiếp thông căn, CẤM ẤN, cấm mơ hồ.
       - Đắc Thế: Chỉ Tỷ/Kiếp/Ấn, loại bỏ Quý và phe tiết/khắc Thân.
       - Bỏ hoàn toàn thang điểm số tự chế (40/35/20).
    3. Chuẩn hóa Mục V (Định danh Cách Cục):
       - Kiến Lộc Cách: Nhật Chủ đắc Lộc tại Chi Tháng, CẤM cụm 'Tỷ Kiên thấu lên Thiên Can'.
    """
    if not noi_dung_ai or not isinstance(noi_dung_ai, str):
        return noi_dung_ai

    noi_dung_kq = noi_dung_ai

    # 1. Chuẩn hóa Mục II
    muc_2_chuan = tao_noi_dung_chuan_muc_2(tu_tru)
    pattern_muc_2 = re.compile(
        r'(^[ \t]*(?:[•\-\*#]+\s*|\d+[\.\)]\s*|\*+|\b)(?:Mục\s*(?:II|2)|II\.?)\b[^\n]*\n)(.*?)(?=(?:^[ \t]*(?:[•\-\*#]+\s*|\d+[\.\)]\s*|\*+|\b)(?:Mục\s*(?:III|3)|III\.?)\b)|\Z)',
        flags=re.DOTALL | re.MULTILINE | re.IGNORECASE
    )
    match_muc_2 = pattern_muc_2.search(noi_dung_kq)
    if match_muc_2:
        noi_dung_kq = noi_dung_kq[:match_muc_2.start()] + muc_2_chuan + "\n\n" + noi_dung_kq[match_muc_2.end():].lstrip()

    # 2. Chuẩn hóa Mục IV (Đánh giá Khí Lực Bản Thân)
    muc_4_chuan = tao_noi_dung_chuan_muc_4(tu_tru)
    pattern_muc_4 = re.compile(
        r'(^[ \t]*(?:[•\-\*#]+\s*|\d+[\.\)]\s*|\*+|\b)(?:Mục\s*(?:IV|4)|IV\.?)\b[^\n]*\n)(.*?)(?=(?:^[ \t]*(?:[•\-\*#]+\s*|\d+[\.\)]\s*|\*+|\b)(?:Mục\s*(?:V|5)|V\.?)\b)|\Z)',
        flags=re.DOTALL | re.MULTILINE | re.IGNORECASE
    )
    match_muc_4 = pattern_muc_4.search(noi_dung_kq)
    if match_muc_4:
        noi_dung_kq = noi_dung_kq[:match_muc_4.start()] + muc_4_chuan + "\n\n" + noi_dung_kq[match_muc_4.end():].lstrip()
    else:
        # Nếu chưa tìm thấy với pattern chặt chẽ, thử tìm bất kỳ dòng nào có "Đánh giá Khí Lực Bản Thân"
        pattern_muc_4_fallback = re.compile(
            r'(^[ \t]*[•\-\*#\d\.\s\*]*Đánh giá Khí Lực Bản Thân[^\n]*\n)(.*?)(?=(?:^[ \t]*[•\-\*#\d\.\s\*]*Định danh Cách Cục[^\n]*\n)|\Z)',
            flags=re.DOTALL | re.MULTILINE | re.IGNORECASE
        )
        match_muc_4_fallback = pattern_muc_4_fallback.search(noi_dung_kq)
        if match_muc_4_fallback:
            noi_dung_kq = noi_dung_kq[:match_muc_4_fallback.start()] + muc_4_chuan + "\n\n" + noi_dung_kq[match_muc_4_fallback.end():].lstrip()
        else:
            # Tìm vị trí trước Mục V để chèn
            pattern_muc_5_find = re.compile(
                r'(^[ \t]*(?:[•\-\*#]+\s*|\d+[\.\)]\s*|\*+|\b)(?:Mục\s*(?:V|5)|V\.?)\b[^\n]*)',
                flags=re.MULTILINE | re.IGNORECASE
            )
            match_muc_5_find = pattern_muc_5_find.search(noi_dung_kq)
            if match_muc_5_find:
                noi_dung_kq = noi_dung_kq[:match_muc_5_find.start()] + muc_4_chuan + "\n\n" + noi_dung_kq[match_muc_5_find.start():]

    # 3. Chuẩn hóa Mục V (Định danh Cách Cục)
    muc_5_chuan = tao_noi_dung_chuan_muc_5(tu_tru)
    pattern_muc_5 = re.compile(
        r'(^[ \t]*(?:[•\-\*#]+\s*|\d+[\.\)]\s*|\*+|\b)(?:Mục\s*(?:V|5)|V\.?)\b[^\n]*\n)(.*?)(?=(?:^[ \t]*(?:[•\-\*#]+\s*|\d+[\.\)]\s*|\*+|\b)(?:Mục\s*(?:VI|6)|VI\.?)\b)|\Z)',
        flags=re.DOTALL | re.MULTILINE | re.IGNORECASE
    )
    match_muc_5 = pattern_muc_5.search(noi_dung_kq)
    if match_muc_5:
        noi_dung_kq = noi_dung_kq[:match_muc_5.start()] + muc_5_chuan + "\n\n" + noi_dung_kq[match_muc_5.end():].lstrip()

    # 4. Quét sạch triệt để mọi dấu vết của thang điểm số tự chế (40/35/20, điểm Lệnh/Địa/Thế)
    noi_dung_kq = re.sub(r'\(?(?:thang\s+)?điểm\s*(?:số)?\s*[:\-]?\s*40\s*/\s*35\s*/\s*20\)?', '', noi_dung_kq, flags=re.IGNORECASE)
    noi_dung_kq = re.sub(r'\(?40\s*/\s*35\s*/\s*20\)?', '', noi_dung_kq)
    noi_dung_kq = re.sub(r'\(?Điểm\s*(?:Lệnh|Địa|Thế)[^\)\n]*\)?', '', noi_dung_kq, flags=re.IGNORECASE)
    noi_dung_kq = re.sub(r'\(?\d+\s*điểm\s*(?:cho|vào)?\s*(?:Đắc\s*)?(?:Lệnh|Địa|Thế)[^\)\n]*\)?', '', noi_dung_kq, flags=re.IGNORECASE)
    noi_dung_kq = re.sub(r'\(điểm\s+Lệnh\s+\d+\)', '', noi_dung_kq, flags=re.IGNORECASE)
    noi_dung_kq = re.sub(r'\(điểm\s+Địa\s+\d+\)', '', noi_dung_kq, flags=re.IGNORECASE)
    noi_dung_kq = re.sub(r'\(điểm\s+Thế\s+\d+\)', '', noi_dung_kq, flags=re.IGNORECASE)
    noi_dung_kq = re.sub(r'Tỷ Kiên thấu lên Thiên Can', 'Nhật Chủ đắc Lộc tại Chi Tháng', noi_dung_kq)

    return noi_dung_kq
