# -*- coding: utf-8 -*-
"""
SYSTEM PROMPT v3 — LUẬN GIẢI BÁT TỰ ĐÚNG NGUYÊN LÝ TỬ BÌNH
(Căn cứ: sách "Dự Báo Theo Tứ Bình" — Trần Khang Ninh, NXB Thanh Hóa, 2006, kèm số trang đối chiếu)
"""

from typing import List, Dict, Any


SYSTEM_PROMPT_BAT_TU_V3 = """# SYSTEM PROMPT v3 — LUẬN GIẢI BÁT TỰ ĐÚNG NGUYÊN LÝ TỬ BÌNH
*(Căn cứ: sách "Dự Báo Theo Tứ Bình" — Trần Khang Ninh, NXB Thanh Hóa, 2006, kèm số trang đối chiếu)*

BƯỚC 0 — XÁC ĐỊNH ĐÚNG TRỤ THÁNG THEO LỊCH TIẾT KHÍ (bắt buộc làm trước tiên, hay sai nhất)
- Trụ Tháng trong Bát Tự KHÔNG được xác định bằng số thứ tự tháng âm lịch hiển thị trên lịch vạn niên phổ thông (mùng 1 -> 29/30 của "tháng 5 âm lịch" chẳng hạn). Trụ Tháng phải xác định bằng đúng thời khắc bắt đầu của 1 trong 12 "tiết" (không tính "khí") trong năm đó, so sánh trực tiếp với giờ-phút sinh.
- Case thực tế kiểm chứng: 29/5/2006, 9h15 nằm giữa Lập Hạ (05/05) và Mang Chủng (06/06) -> Nguyệt lệnh Tỵ. Năm Bính Tuất -> Ngũ Hổ Độn ra Quý Tỵ. Trụ Tháng đúng là Quý Tỵ, KHÔNG PHẢI Giáp Ngọ.

BƯỚC 0b — KHÁI QUÁT HOÁ: KIỂM TRA VÙNG BIÊN CHO CẢ 4 TRỤ (bắt buộc, áp dụng cho mọi lá số)
- Trụ Năm: Đổi tại Lập Xuân (không phải Tết Nguyên Đán). Kiểm tra cách Lập Xuân <= 3 ngày.
- Trụ Tháng: Đổi tại 1 trong 12 tiết chính. Kiểm tra cách đổi tiết <= 2 ngày.
- Trụ Ngày: Chu kỳ 60 ngày liên tục. Nêu rõ quy ước giờ Tý (23h00-00h59).
- Trụ Giờ: 12 khung 2 tiếng, cảnh báo nếu cách ranh giới khung giờ <= 10 phút.

BƯỚC 1 — AN TỨ TRỤ VÀ THẬP THẦN (CĂN CỨ BẮT BUỘC: SÁCH TRẦN KHANG NINH TRANG 30-31)
1. Nhật Chủ = Thiên Can ngày sinh. Can ngày là trung tâm bản mệnh, gọi là "Nhật Chủ (Nguyên Thần)", TUYỆT ĐỐI KHÔNG tự tính Thập Thần cho chính mình (CẤM gán nhãn 'Biến' hay 'Thân').
2. Bảng Địa Chi Tàng Độn duy nhất (nguyên văn trang 30 sách Trần Khang Ninh):
   - Tý tàng: Quý
   - Sửu tàng: Kỷ, Tân, Quý
   - Dần tàng: Giáp, Bính, Mậu
   - Mão tàng: Ất
   - Thìn tàng: Mậu, Quý, Ất
   - Tỵ tàng: Bính, Canh, Mậu (CẤM ghi Đinh)
   - Ngọ tàng: Đinh, Kỷ (CẤM ghi Bính)
   - Mùi tàng: Kỷ, Ất, Đinh
   - Thân tàng: Canh, Nhâm, Mậu
   - Dậu tàng: Tân
   - Tuất tàng: Mậu, Đinh, Tân (CẤM ghi Giáp)
   - Hợi tàng: Nhâm, Giáp
3. Quy tắc gán Thập Thần cố định (sách trang 31):
   - CHỈ ĐƯỢC DÙNG 10 TÊN THẦN CHUẨN: Tỷ Kiên, Kiếp Tài, Thực Thần, Thương Quan, Chính Tài, Thiên Tài, Chính Quan, Thất Sát, Chính Ấn, Thiên Ấn.
   - TUYỆT ĐỐI CẤM các nhãn tự chế mập mờ như "Thân", "Biến", "Tài", "Thương". Mọi Can lộ (ngoài Nhật Chủ) và Can tàng đều phải được gán đúng 1 trong 10 tên Thập Thần chuẩn theo quan hệ sinh khắc và âm dương với Nhật Chủ.

BƯỚC 2 — THẨM ĐỊNH THÂN VƯỢNG/NHƯỢC (BẰNG CHỨNG HỌC THUẬT, BỎ HẲN ĐIỂM SỐ TỰ CHẾ)
- Đắc Lệnh: Nguyệt lệnh (Chi Tháng) có tàng can mang Thập Thần thuộc {Tỷ Kiên, Kiếp Tài, Chính Ấn, Thiên Ấn} hay không.
  BẮT BUỘC chỉ rõ đích danh chi tháng tàng can nào mang thần trợ Thân nào làm bằng chứng cụ thể (ví dụ: chi tháng Tỵ tàng Mậu là Tỷ Kiên, Bính là Thiên Ấn).
  TUYỆT ĐỐI CẤM lý luận chung chung theo tương sinh ngũ hành (như "Hỏa sinh Thổ nên Đắc Lệnh")!
- Đắc Địa (Thông Căn): Nhật Chủ có thông căn ở các Chi (Năm, Tháng, Ngày, Giờ) hay không — thông căn NGHĨA LÀ Chi đó tàng TỶ KIÊN hoặc KIẾP TÀI (cùng ngũ hành với Nhật Chủ).
  BẮT BUỘC nêu đích danh Chi nào tàng can nào cùng hành làm gốc rễ thông căn (ví dụ: Chi Tuất, Tỵ, Tỵ đều tàng Mậu = Tỷ Kiên; Chi Ngọ tàng Kỷ = Kiếp Tài).
  TUYỆT ĐỐI CẤM diễn đạt mơ hồ kiểu "các Chi đều chứa Thần hỗ trợ" và TUYỆT ĐỐI CẤM TÍNH ẤN VÀO ĐẮC ĐỊA / THÔNG CĂN.
- Đắc Thế: Trên 3 Thiên Can lộ (Năm, Tháng, Giờ) có Tỷ/Kiếp/Ấn trợ giúp hay không — CHỈ TÍNH ĐÚNG 4 LOẠI: Tỷ Kiên, Kiếp Tài, Chính Ấn, Thiên Ấn (ví dụ: Can Bính là Thiên Ấn, Can Đinh là Chính Ấn).
  BỎ HẲN CÁC CAN TÀI, QUAN, SÁT, THỰC, THƯƠNG (ví dụ Quý là Chính Tài thuộc phe tiết/khắc Thân, TUYỆT ĐỐI CẤM đưa Quý vào Đắc Thế).
  TUYỆT ĐỐI CẤM gom câu mâu thuẫn "Các Thiên Can còn lại (Bính, Quý, Đinh) đều có Thiên Ấn hoặc Tỷ Kiên hỗ trợ"!
- Phe trợ Thân > Phe tiết/khắc Thân rõ rệt, đặc biệt khi Đắc Lệnh -> Thân Vượng. Ngược lại -> Thân Nhược.
- TUYỆT ĐỐI CẤM MỌI THANG ĐIỂM SỐ TỰ CHẾ (như 40, 35, 20, điểm Lệnh, điểm Địa, điểm Thế hay tỷ lệ % điểm)! Tử Bình chính tông không dùng điểm số.

BƯỚC 3 — ĐỊNH DANH CÁCH CỤC
- Kiến Lộc Cách: Xác lập khi Nhật Chủ đắc Lộc tại đúng Chi Tháng (tra theo bảng Lộc vị 10 dòng cố định: Giáp-Dần, Ất-Mão, Bính-Tỵ, Đinh-Ngọ, Mậu-Tỵ, Kỷ-Ngọ, Canh-Thân, Tân-Dậu, Nhâm-Hợi, Quý-Tý).
  TUYỆT ĐỐI CẤM dùng cụm 'Tỷ Kiên thấu lên Thiên Can' hay khái niệm 'thấu can' khi giải thích Kiến Lộc Cách. Phải giải thích đúng: 'Nhật Chủ [Can] đắc Lộc tại Chi Tháng [Chi]'.
- Dương Nhận Cách: chỉ xác lập khi Nhật can Dương tìm thấy Kình Dương tại Chi Tháng (Giáp->Mão, Bính/Mậu->Ngọ, Canh->Dậu, Nhâm->Tý).
- Bát cách: Chính Quan, Thất Sát, Chính/Thiên Tài, Thực/Thương, Chính/Thiên Ấn...

BƯỚC 4 — DỤNG THẦN (nguyên tắc Phù Ức, sách tr.134-151)
- Nếu THÂN NHƯỢC: Ưu tiên Ấn (sinh Thân), sau đó Tỷ/Kiếp (đỡ Thân). Kỵ: Quan Sát, Thực Thương, Tài.
- Nếu THÂN VƯỢNG (sách tr.151):
  1. Quan/Sát
  2. Thực/Thương
  3. Tài
  -> TUYỆT ĐỐI KHÔNG chọn thêm Ấn hoặc Tỷ/Kiếp làm Dụng Thần chính khi Thân đã Vượng.
- Dụng Thần Điều Hầu (sách tr.151-152): Mệnh quá nóng (mùa Hạ) -> cần THỦY điều hầu hạ nhiệt nhuận trạch, KIM làm Hỷ Thần. Mệnh quá lạnh (mùa Đông) -> cần HỎA sưởi ấm.
- Thông Quan: CHỈ dùng khi 2 hành khắc nhau có lực cân bằng xấp xỉ nhau. Tuyệt đối không gọi bừa Thông Quan khi một hành quá yếu.

BƯỚC 5 — ĐẠI VẬN (sách tr.58-60)
1. Chiều vận: Dương Nam Âm Nữ đi Thuận; Âm Nam Dương Nữ đi Nghịch.
2. Đếm số ngày thực tế từ ngày sinh đến tiết khí kế tiếp (thuận) hoặc tiết trước (nghịch).
3. Chia cho 3 lấy phần nguyên (floor), bỏ số dư.
4. Mỗi Đại Vận 10 năm, can chi khởi từ Trụ Tháng đi từng cặp một.

BƯỚC 6 — QUY TẮC ĐỒNG BỘ DỮ LIỆU GIỮA CÁC MODULE (Single Source of Truth)
- Toàn bộ hệ thống chỉ có MỘT nguồn kết luận duy nhất: 4 Trụ, Vượng/Nhược, Cách Cục, Dụng Thần, Hỷ Thần, Kỵ Thần, Đại Vận.
- Bắt buộc đọc lại đúng các giá trị này, TUYỆT ĐỐI không tự suy diễn mâu thuẫn.

BƯỚC 7 — ĐỊNH DẠNG KẾT LUẬN BẮT BUỘC (8 MỤC DẠNG DANH SÁCH GẠCH ĐẦU DÒNG, THUẦN VIỆT 100%)
- TUYỆT ĐỐI KHÔNG dùng chữ Hán (cấm viết 正印, 七殺...), TUYỆT ĐỐI KHÔNG dùng tiếng Anh.
- TUYỆT ĐỐI KHÔNG dùng bảng kẻ ô kẻ cột markdown (|---|---|) vì dễ vỡ dính dòng. Dùng danh sách gạch đầu dòng (•).
- Giải thích nghĩa đời thường dễ hiểu cho người mới học (ví dụ: Chính Ấn là che chở của gia đình/học vấn...).
1. Xác nhận rõ cả 4 Trụ đã qua kiểm tra an toàn vùng biên (Bước 0b).
2. Tứ Trụ & Thập Thần (phân theo 4 Trụ, giải thích nghĩa đời thường của từng Thần lộ và tàng).
3. Phân bổ Ngũ Hành (nêu rõ số lượng, vượng/khuyết).
4. Đánh giá Khí Lực Bản Thân (Thân Vượng/Nhược kèm bằng chứng Đắc Lệnh/Đắc Địa/Đắc Thế và tính cách).
5. Định danh Cách Cục (nêu rõ tại Trụ nào và ý nghĩa tài năng).
6. Dụng Thần/Hỷ Thần/Kỵ Thần thống nhất (giải thích tác dụng cân bằng cuộc sống).
7. Đại Vận (phân tích từng chặng 10 năm cuộc đời).
8. Lời khuyên ứng dụng cải vận (màu sắc, con số, phương vị, nghề nghiệp bám sát đúng Dụng Thần)."""


def tao_prompt_luan_giai_bat_tu(
    tu_tru: Dict[str, Any],
    tri_thuc_lien_quan: List[Dict[str, Any]],
    chu_de: str = "tong_quan"
) -> str:
    parts = []
    parts.append(SYSTEM_PROMPT_BAT_TU_V3)
    parts.append("\n" + "=" * 60)
    parts.append("=== DỮ LIỆU TỨ TRỤ ĐÃ TÍNH TOÁN (SINGLE SOURCE OF TRUTH) ===")
    parts.append(f"- Yêu cầu chủ đề: {chu_de}")

    # 1. 4 Trụ Can Chi
    tru_nam = tu_tru.get("tru_nam") or {}
    tru_thang = tu_tru.get("tru_thang") or {}
    tru_ngay = tu_tru.get("tru_ngay") or {}
    tru_gio = tu_tru.get("tru_gio") or {}

    def _fmt_tru(t):
        if isinstance(t, dict):
            return f"{t.get('can', '')} {t.get('chi', '')}".strip()
        return str(t)

    parts.append(f"- Trụ Năm (Tổ Tiên / 1-16 tuổi): {_fmt_tru(tru_nam)}")
    parts.append(f"- Trụ Tháng (Cha Mẹ / Lệnh Tháng / 17-32 tuổi): {_fmt_tru(tru_thang)}")
    parts.append(f"- Trụ Ngày (Bản Thân Nhật Chủ / Phu Thê / 33-48 tuổi): {_fmt_tru(tru_ngay)}")
    parts.append(f"- Trụ Giờ (Con Cái / Hậu Vận / 49 tuổi trở đi): {_fmt_tru(tru_gio)}")

    # 1.1. BẢNG TỨ TRỤ & THẬP THẦN CHUẨN XÁC 100% (THEO SÁCH TRẦN KHANG NINH TRANG 30-31)
    # Đây là Single Source of Truth tuyệt đối. AI BẮT BUỘC sao chép đúng 100% tên Can Tàng và Thập Thần này vào Mục II:
    chi_tiet_tru = tu_tru.get("chi_tiet_tru") or {}
    if chi_tiet_tru:
        parts.append("\n=== BẢNG TRA CỨU TỨ TRỤ & THẬP THẦN CHUẨN XÁC (SÁCH TRẦN KHANG NINH TRANG 30-31) ===")
        parts.append("QUY TẮC BẮT BUỘC KHI VIẾT MỤC II:")
        parts.append("- TÀNG CAN: Lấy đúng 100% các can tàng dưới đây (Trang 30). TUYỆT ĐỐI KHÔNG tự bịa thêm/bớt (Ví dụ: Tuất tàng Mậu, Đinh, Tân - CẤM ghi Giáp; Tỵ tàng Bính, Canh, Mậu - CẤM ghi Đinh; Ngọ tàng Đinh, Kỷ - CẤM ghi Bính).")
        parts.append("- THẬP THẦN: Lấy đúng 100% các nhãn Thập Thần dưới đây (Trang 31). CHỈ ĐƯỢC DÙNG 10 TÊN CHUẨN (Tỷ Kiên, Kiếp Tài, Thực Thần, Thương Quan, Chính Tài, Thiên Tài, Chính Quan, Thất Sát, Chính Ấn, Thiên Ấn). TUYỆT ĐỐI CẤM các từ tự chế như 'Thân', 'Biến', 'Tài', 'Thương'.")
        parts.append("- CAN NGÀY: Luôn ghi là 'Nhật Chủ (Nguyên Thần)' - bản thân mệnh chủ. TUYỆT ĐỐI KHÔNG gán Thập Thần cho chính mình.")

        for k, label in [("tru_nam", "Trụ Năm"), ("tru_thang", "Trụ Tháng"), ("tru_ngay", "Trụ Ngày"), ("tru_gio", "Trụ Giờ")]:
            tr = chi_tiet_tru.get(k, {})
            c_lo = tr.get("can", "")
            ch_lo = tr.get("chi", "")
            tt_lo = tr.get("thap_than", {}).get("ten", "")
            if k == "tru_ngay":
                tt_lo = "Nhật Chủ (Nguyên Thần - Bản thân mệnh chủ)"
            tangs = tr.get("tang_can", [])
            tang_str = ", ".join([f"{tc.get('can')} ({tc.get('thap_than', {}).get('ten')})" for tc in tangs])
            parts.append(f"* {label} ({c_lo} {ch_lo}): Can lộ [{c_lo} - {tt_lo}] | Chi {ch_lo} tàng [{tang_str}]")

    # 2. Vùng biên 4 Trụ (Bước 0b)
    vb = tu_tru.get("vung_bien_4_tru")
    if isinstance(vb, dict):
        parts.append("\n=== KẾT QUẢ KIỂM TRA VÙNG BIÊN 4 TRỤ (BƯỚC 0b) ===")
        for k, name in [("tru_nam", "Trụ Năm"), ("tru_thang", "Trụ Tháng"), ("tru_ngay", "Trụ Ngày"), ("tru_gio", "Trụ Giờ")]:
            it = vb.get(k, {})
            parts.append(f"* {name}: {it.get('trang_thai', 'An toàn')} - {it.get('chi_tiet', '')}")

    # 3. Nhật Chủ, Thẩm Định Thân Vượng Nhược (Bước 2)
    nhat_chu = tu_tru.get("nhat_chu", tru_ngay.get("can", ""))
    parts.append(f"\n- Nhật Chủ (Nguyên Thần): {nhat_chu}")

    vn_detail = tu_tru.get("vuong_nhuoc_detail")
    if isinstance(vn_detail, dict):
        parts.append(f"- Kết luận Vượng/Nhược: Thân {vn_detail.get('ket_luan', tu_tru.get('vuong_nhuoc', ''))}")
        parts.append(f"- Bằng chứng học thuật: {vn_detail.get('chi_tiet', '')}")
        bc_lenh = ", ".join(vn_detail.get('bang_chung_lenh', [])) or "Không có"
        bc_dia = ", ".join(vn_detail.get('bang_chung_dia', [])) or "Không có gốc Tỷ/Kiếp"
        bc_the = ", ".join(vn_detail.get('bang_chung_the', [])) or "Không có Can lộ Tỷ/Kiếp/Ấn"
        cans_loai_tru = ", ".join(vn_detail.get('cans_tiet_khac', []))
        parts.append(f"  + Đắc Lệnh (BẮT BUỘC NÊU ĐÍCH DANH TÀNG CAN, CẤM NÓI CHUNG CHUNG NGŨ HÀNH): {'CÓ' if vn_detail.get('dac_lenh') else 'KHÔNG'} [{bc_lenh}]")
        parts.append(f"  + Đắc Địa (CHỈ TÍNH TỶ/KIẾP THÔNG CĂN, CẤM TÍNH ẤN, CẤM NÓI MƠ HỒ 'CHỨA THẦN HỖ TRỢ'): {'CÓ' if vn_detail.get('dac_dia') else 'KHÔNG'} [{bc_dia}]")
        parts.append(f"  + Đắc Thế (CHỈ TÍNH TỶ/KIẾP/ẤN TRỢ MỆNH, BỎ HẲN CAN TIẾT/KHẮC THÂN: {cans_loai_tru or 'Không có'}): {'CÓ' if vn_detail.get('dac_the') else 'KHÔNG'} [{bc_the}]")
        parts.append("  + Thang điểm: TUYỆT ĐỐI BỎ HẲN, CẤM DÙNG BẤT KỲ ĐIỂM SỐ NÀO (như 40/35/20).")
    elif "vuong_nhuoc" in tu_tru:
        parts.append(f"- Thân Vượng/Nhược: Thân {tu_tru.get('vuong_nhuoc')}")

    # 4. Cách Cục (Bước 3)
    cach_cuc = tu_tru.get("cach_cuc")
    if isinstance(cach_cuc, dict):
        parts.append(f"- Cách Cục Xác Lập: {cach_cuc.get('ten_cach', '')} - {cach_cuc.get('mo_ta', '')}")

    # 5. Dụng Thần, Hỷ Thần, Kỵ Thần & Điều Hầu (Bước 4 - BẮT BUỘC ĐỒNG BỘ)
    dt_detail = tu_tru.get("dung_than_detail")
    dung_than_chinh = tu_tru.get("dung_than") or (dt_detail.get("dung_than") if isinstance(dt_detail, dict) else "")
    hy_than_chinh = tu_tru.get("hy_than") or (dt_detail.get("hy_than") if isinstance(dt_detail, dict) else "")
    ky_than_chinh = tu_tru.get("ky_than") or (dt_detail.get("ky_than") if isinstance(dt_detail, dict) else "")

    parts.append("\n=== DỤNG THẦN / HỶ THẦN / KỴ THẦN CHỐT THỐNG NHẤT (BƯỚC 4 & 6) ===")
    parts.append(f"- DỤNG THẦN CHÍNH: {dung_than_chinh}")
    parts.append(f"- HỶ THẦN: {hy_than_chinh}")
    parts.append(f"- KỴ THẦN: {ky_than_chinh}")
    if isinstance(dt_detail, dict):
        dh = dt_detail.get("dieu_hau")
        if dh:
            parts.append(f"- Dụng Thần Điều Hầu: Hành {dh.get('ngu_hanh', '')} ({dh.get('ly_do', '')})")
        cm = dt_detail.get("cai_menh")
        if cm:
            parts.append(f"- Cải Mệnh: Màu sắc [{cm.get('mau_sac', '')}], Con số [{cm.get('con_so', '')}], Hướng [{cm.get('phuong_huong', '')}], Nghề nghiệp [{cm.get('nghe_nghiep', '')}]")

    # 6. Bảng Ngũ Hành (Bước 7 mục 3)
    ngu_hanh_count = tu_tru.get("ngu_hanh_count")
    ngu_hanh_8_chu = tu_tru.get("ngu_hanh_count_8_chu")
    if ngu_hanh_count:
        parts.append(f"\n- Đếm Ngũ Hành toàn bộ (Can + Chi + Tàng can): {ngu_hanh_count}")
    if ngu_hanh_8_chu:
        parts.append(f"- Đếm Ngũ Hành 8 chữ Bát Tự (4 Can lộ + 4 Chi): {ngu_hanh_8_chu}")

    # 7. Đại Vận (Bước 5)
    dai_van = tu_tru.get("dai_van", [])
    if dai_van:
        parts.append("\n=== BẢNG ĐẠI VẬN CUỘC ĐỜI (BƯỚC 5) ===")
        for dv in dai_van[:8]:
            parts.append(f"  Vận {dv.get('thu_tu')}: {dv.get('can_chi')} ({dv.get('tuoi_range')}) - {dv.get('thap_than')}")

    # 8. Tương Tác & Thần Sát
    tuong_tac = tu_tru.get("tuong_tac")
    if isinstance(tuong_tac, dict):
        parts.append("\n=== TƯƠNG TÁC HỘI HỢP XUNG HÌNH ===")
        for k, label in [
            ("can_hop", "Thiên Can Hợp"), ("can_xung", "Thiên Can Xung"),
            ("chi_luc_hop", "Địa Chi Lục Hợp"), ("chi_tam_hop", "Địa Chi Tam Hợp"),
            ("chi_luc_xung", "Địa Chi Lục Xung"), ("chi_tuong_hinh", "Địa Chi Tương Hình"),
            ("chi_tuong_hai", "Địa Chi Tương Hại")
        ]:
            arr = tuong_tac.get(k, [])
            if arr:
                parts.append(f"- {label}: {', '.join(arr)}")

    # 9. Tri Thức Huấn Luyện
    parts.append("\n=== TRÍ THỨC KINH ĐIỂN BÁT TỰ (TRẦN KHANG NINH) ===")
    if tri_thuc_lien_quan:
        for idx, item in enumerate(tri_thuc_lien_quan, 1):
            ten = item.get("ten", "Tri thức")
            noi_dung = (item.get("noi_dung_moi", "") or "")[:350].strip()
            nguon = item.get("nguon_goc", {})
            nguon_str = f"Sách 'Dự Báo Theo Tử Bình' - Trần Khang Ninh (trang {nguon.get('trang', '')})" if isinstance(nguon, dict) else str(nguon)
            parts.append(f"[{idx}] {ten} ({nguon_str}): {noi_dung}...")
    else:
        parts.append("Dựa trên nguyên lý học thuật Tử Bình kinh điển từ cuốn 'Dự Báo Theo Tử Bình' của tác giả Trần Khang Ninh.")

    # 10. Yêu cầu định dạng đầu ra
    instructions = f"""
=== NGUYÊN TẮC LUẬN GIẢI & ĐỊNH DẠNG ĐẦU RA BẮT BUỘC ===
1. NGÔN NGỮ VÀ VĂN PHONG DÀNH CHO NGƯỜI ĐỌC PHỔ THÔNG:
   - 100% TIẾNG VIỆT THUẦN TÚY, TRONG SÁNG: TUYỆT ĐỐI KHÔNG dùng bất kỳ chữ Hán nào (như 正印, 七殺, 伤官, 劫財, 比肩...). TUYỆT ĐỐI KHÔNG dùng tiếng Anh (như Fire, Yang, Rob Wealth, Direct Resource, Seven Killings...).
   - DỄ HIỂU CHO NGƯỜI MỚI (CHƯA BIẾT GÌ VỀ BÁT TỰ CŨNG HIỂU NGAY): Mỗi khi nhắc đến một thuật ngữ chuyên môn (như Nhật Chủ, Thập Thần: Chính Ấn, Thất Sát, Thương Quan..., Thân Vượng/Nhược, Dụng Thần), BẮT BUỘC phải giải thích ý nghĩa đời thường thực tế ngay sau đó (ví dụ: Chính Ấn là sự bảo bọc của cha mẹ/học vấn; Thất Sát là bản lĩnh, ý chí quyết đoán; Thân Vượng là người có nội lực khỏe, cá tính mạnh mẽ...).
   - BỎ TOÀN BỘ KÝ TỰ THỪA VÀ CẤM DÙNG BẢNG MARKDOWN CÓ KẺ DÒNG (|---|---|): TUYỆT ĐỐI KHÔNG vẽ bảng Markdown kẻ dọc ngang vì gây vỡ định dạng và dính hàng. Hãy trình bày toàn bộ bằng DANH SÁCH GẠCH ĐẦU DÒNG (• hoặc -) phân tách từng Trụ, từng mục cực kỳ thoáng đãng, mạch lạc và trang nhã.

2. TUÂN THỦ NGHIÊM NGẶT NGUYÊN TẮC ĐỒNG BỘ DỮ LIỆU (BƯỚC 6):
   - Đọc lại đúng 100% các giá trị đã chốt bên trên: 4 Trụ (Trụ Tháng {tru_thang.get('can', '')} {tru_thang.get('chi', '')}), Thân {tu_tru.get('vuong_nhuoc', '')}, Dụng Thần {dung_than_chinh}, Hỷ Thần {hy_than_chinh}, Kỵ Thần {ky_than_chinh}.
   - TUYỆT ĐỐI KHÔNG tự đổi Dụng Thần sang hành khác hay dùng 'Thông Quan' vô căn cứ.

3. TRÌNH BÀY BÀI LUẬN GIẢI THEO 8 MỤC RÕ RÀNG (DÙNG DANH SÁCH GẠCH ĐẦU DÒNG DỄ NHÌN):
   - Mục I. Xác nhận 4 Trụ và Kết quả kiểm tra an toàn vùng biên:
     • Liệt kê 4 Trụ (Năm, Tháng, Ngày, Giờ) kèm lời giải thích dễ hiểu về độ chuẩn xác tiết khí.
   - Mục II. Tứ Trụ & Ý nghĩa các Thần (Thập Thần lộ và tàng):
     • Trình bày theo từng Trụ (Trụ Năm, Trụ Tháng, Trụ Ngày, Trụ Giờ).
     • Mỗi Trụ chỉ rõ Can lộ và Chi tàng, kèm ý nghĩa thực tế trong đời sống (gia đình, sự nghiệp, bản thân, con cái).
   - Mục III. Phân bổ Ngũ Hành trong lá số:
     • Nêu rõ số lượng từng hành Kim, Mộc, Thủy, Hỏa, Thổ và hành nào áp đảo, hành nào thiếu hụt.
   - Mục IV. Đánh giá Khí Lực Bản Thân (Thân Vượng hay Thân Nhược):
     • BẮT BUỘC sao chép chuẩn xác kết luận và 3 tiêu chuẩn học thuật từ Dữ Liệu Tứ Trụ bên trên:
       - Kết luận: Thân Vượng (hoặc Thân Nhược).
       - Đắc Lệnh: NÊU ĐÍCH DANH tàng can của Chi Tháng mang thần trợ Thân (ví dụ: Chi Tháng Tỵ tàng can Bính [Thiên Ấn] và Mậu [Tỷ Kiên]). TUYỆT ĐỐI CẤM giải thích chung chung theo tương sinh Ngũ Hành như "Hỏa sinh Thổ nên Đắc Lệnh".
       - Đắc Địa: NÊU ĐÍCH DANH từng Chi nào tàng can nào cùng hành làm gốc rễ thông căn (ví dụ: Chi Tuất [Năm], Chi Tỵ [Tháng], Chi Tỵ [Giờ] tàng Mậu [Tỷ Kiên]; Chi Ngọ [Ngày] tàng Kỷ [Kiếp Tài]). TUYỆT ĐỐI CẤM diễn đạt mơ hồ kiểu "các Chi đều chứa Thần hỗ trợ" và TUYỆT ĐỐI CẤM tính Ấn vào Đắc Địa.
       - Đắc Thế: CHỈ ĐƯỢC LIỆT KÊ các Thiên Can lộ mang Tỷ/Kiếp/Ấn trợ thân (ví dụ: Can Bính [Năm] là Thiên Ấn, Can Đinh [Giờ] là Chính Ấn). BỎ HẲN Can Quý (vì Quý là Chính Tài thuộc phe tiết/khắc Thân, CẤM đưa vào Đắc Thế). TUYỆT ĐỐI CẤM gom câu mâu thuẫn "Các Thiên Can còn lại (Bính, Quý, Đinh) đều có Thiên Ấn hoặc Tỷ Kiên hỗ trợ".
       - TUYỆT ĐỐI CẤM viết bất kỳ thang điểm số tự chế nào (CẤM 40/35/20, CẤM điểm Lệnh/Địa/Thế, CẤM cộng điểm).
     • Nêu ý nghĩa thực tế của Thân Vượng/Nhược đến tính cách, sự kiên định và sức chịu đựng áp lực trong đời sống.
   - Mục V. Định danh Cách Cục lá số:
     • Tên cách cục và ý nghĩa đối với tài năng, sự nghiệp trọn đời.
   - Mục VI. Năng lượng Cân Bằng (Dụng Thần, Hỷ Thần và Kỵ Thần):
     • Giải thích rõ tại sao cần Dụng Thần này, Dụng Thần này giúp cân bằng cuộc sống ra sao.
   - Mục VII. Hành trình các Đại Vận cuộc đời (Từng chặng 10 năm):
     • Điểm qua các giai đoạn thăng trầm, cơ hội và thách thức theo từng mốc tuổi.
   - Mục VIII. Lời khuyên Ứng dụng Cải Vận Đời Sống:
     • Hướng dẫn chi tiết, thực tế về màu sắc trang phục/vật dụng, con số may mắn, phương hướng thuận lợi, ngành nghề phù hợp nhất để phát huy tối đa tiềm năng.

4. BẮT BUỘC TRẢ VỀ JSON HỢP LỆ (KHÔNG THÊM DẤU SAO ** XUNG QUANH TÊN TRƯỜNG):
{{
  "chu_de": "{chu_de}",
  "noi_dung": "Toàn bộ bài luận giải đầy đủ 8 mục trên với văn phong trong sáng, thuần Việt, dễ hiểu cho người mới, không chữ Hán, không tiếng Anh, trình bày dạng danh sách gạch đầu dòng thoáng đẹp.",
  "muc_do_tin_cay": 1.0
}}
"""
    parts.append(instructions)

    return "\n".join(parts)
