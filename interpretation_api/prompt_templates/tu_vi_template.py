# -*- coding: utf-8 -*-
"""
Template prompt luận giải Tử Vi Đẩu Số chuyên sâu & an toàn nội dung.
"""

from typing import List, Dict, Any

# Bản đồ ánh xạ chủ đề gợi ý sang cung chức năng Tử Vi
CHU_DE_TO_PALACE_MAP = {
    "cong_danh": ["Quan Lộc", "Mệnh"],
    "công danh sự nghiệp": ["Quan Lộc", "Mệnh"],
    "anh_em": ["Huynh Đệ"],
    "anh em, bạn bè": ["Huynh Đệ"],
    "con_cai": ["Tử Tức"],
    "con cái": ["Tử Tức"],
    "tinh_duyen": ["Phu Thê"],
    "tình duyên": ["Phu Thê"],
    "vo_chong": ["Phu Thê"],
    "vợ chồng": ["Phu Thê"],
    "tai_van": ["Tài Bạch"],
    "tài vận, kinh tế": ["Tài Bạch"],
    "suc_khoe": ["Tật Ách"],
    "sức khỏe, bệnh tật": ["Tật Ách"],
    "xuat_ngoai": ["Thiên Di"],
    "xuất ngoại": ["Thiên Di"],
    "bang_huu": ["Nô Bộc"],
    "bằng hữu, đồng nghiệp": ["Nô Bộc"],
    "phuc_duc": ["Phúc Đức"],
    "phúc khí tổ tiên": ["Phúc Đức"],
    "cha_me": ["Phụ Mẫu"],
    "cha mẹ": ["Phụ Mẫu"],
    "nhà cửa, đất đai": ["Điền Trạch"],
    "dien_trach": ["Điền Trạch"],
    "dai_van": ["Mệnh", "Quan Lộc", "Tài Bạch"],
    "tiểu vận": ["Mệnh", "Thân"],
    "tieu_van": ["Mệnh", "Thân"],
}


def tao_prompt_luan_giai_tu_vi(
    la_so: Dict[str, Any],
    tri_thuc_lien_quan: List[Dict[str, Any]],
    chu_de: str = "tong_quan"
) -> str:
    """
    Ghép prompt luận giải Tử Vi chuẩn hóa và tuân thủ nghiêm ngặt đạo đức huyền học:
    - Trích xuất thông tin các cung, chính tinh, cát hung tinh liên quan mật thiết đến chủ đề.
    - Cấm tuyệt đối ngôn từ chết chóc/đoản mệnh/tai họa cực đoan.
    - Định hướng giải pháp hóa giải, tu dưỡng, phòng ngừa tích cực.
    """
    parts = []
    parts.append("=== THÔNG TIN LÁ SỐ TỬ VI ĐẨU SỐ ===")
    parts.append(f"- Yêu cầu luận giải chuyên sâu: {chu_de}")

    # 1. Trích xuất thông tin bản mệnh cơ bản
    info = la_so.get("thong_tin_co_ban", {})
    if info:
        ho_ten = info.get("ho_ten", "Mệnh chủ")
        gioi_tinh = info.get("gioi_tinh", "")
        ngay_am = info.get("ngay_am_str", "")
        gio_sinh = info.get("gio_sinh_str", "")
        parts.append(f"- Đương số: {ho_ten} ({gioi_tinh}) | Sinh: {gio_sinh} ngày {ngay_am}")

    if "loai_hanh_cua_ban_menh" in la_so:
        parts.append(f"- Nạp âm bản mệnh: {la_so.get('loai_hanh_cua_ban_menh')}")
    if "cuc_cua_tuoi" in la_so:
        parts.append(f"- Ngũ hành Cục: {la_so.get('cuc_cua_tuoi')}")
    if "menh_chu" in la_so:
        parts.append(f"- Mệnh chủ: {la_so.get('menh_chu')} | Thân chủ: {la_so.get('than_chu', '')}")

    # 2. Trích xuất chi tiết các cung liên quan từ la_so["palaces"]
    palaces = la_so.get("palaces") or la_so.get("data", {}).get("palaces") or []
    c_lower = chu_de.lower()

    target_palace_names = []
    for k, v in CHU_DE_TO_PALACE_MAP.items():
        if k in c_lower:
            target_palace_names = v
            break

    if not target_palace_names:
        target_palace_names = ["Mệnh", "Thân", "Quan Lộc", "Tài Bạch"]

    relevant_palaces = []
    for p in palaces:
        p_name = p.get("name", "")
        if any(t in p_name for t in target_palace_names):
            majors = [f"{s.get('name')}({s.get('brightness', '')})" for s in p.get("majorStars", [])]
            minors = [s.get("name") for s in p.get("minorStars", [])[:8]]
            adjs = [s.get("name") for s in p.get("adjectiveStars", [])[:5]]
            relevant_palaces.append(
                f"+ Cung {p_name} ({p.get('earthlyBranch', '')}): Chính tinh: {', '.join(majors) or 'Vô chính diệu'} | Phụ tinh: {', '.join(minors + adjs)}"
            )

    if relevant_palaces:
        parts.append("- Cung chức năng trọng tâm:")
        parts.extend(relevant_palaces)
    elif "cung_menh" in la_so:
        parts.append(f"- Cung Mệnh: {la_so.get('cung_menh')}")

    # 3. Tri thức kinh điển tham chiếu
    parts.append("\n=== TRI THỨC KINH ĐIỂN THAM CHIẾU ===")
    if tri_thuc_lien_quan:
        for idx, item in enumerate(tri_thuc_lien_quan, 1):
            ten = item.get("ten", "Tri thức")
            noi_dung = item.get("noi_dung_moi", "")
            nguon = item.get("nguon_goc", "Kinh điển")
            parts.append(f"[{idx}] {ten} ({nguon}): {noi_dung}")
    else:
        parts.append("LƯU Ý: Hiện không có tri thức cụ thể trong hệ thống cho trường hợp này. Hãy trả lời thận trọng, khách quan và nêu rõ giới hạn kiến thức dựa trên nguyên lý cổ tịch Tử Vi Đẩu Số Toàn Thư.")

    # 4. Hướng dẫn & Quy tắc An toàn Nghiêm ngặt
    parts.append("""
=== QUY TẮC ĐẠO ĐỨC & NGUYÊN TẮC LUẬN GIẢI (BẮT BUỘC) ===
1. NGUYÊN TẮC AN TOÀN NỘI DUNG:
   - TUYỆT ĐỐI KHÔNG sử dụng các từ ngữ nhạy cảm chết chóc, tai ương cực đoan, phán quyết đoản thọ hoặc tuyệt vọng (như: 'chết', 'chết chóc', 'chết non', 'chết yểu', 'mất mạng', 'tử nạn', 'tận số', 'tuyệt mệnh', 'tuyệt tự', 'đoản mệnh', 'họa sát thân').
   - Khi luận giải các cung khó hoặc hung sát tinh (như Tật Ách, Kình Đà, Không Kiếp, Hóa Kỵ), LUÔN LUÔN dùng ngôn từ nhân văn, khuyên can dưỡng sinh, phòng ngừa rủi ro y tế định kỳ, chú ý cẩn trọng khi đi lại/giao thông, và hướng dẫn tu tâm dưỡng tính để hóa giải xung hiểm thành an lành.
2. VĂN PHONG & ĐỊNH HƯỚNG:
   - Giữ giọng văn nho nhã, uyên thấu, sâu sắc, thực tế và giàu tính động viên xây dựng ("Đức năng thắng số").
   - Trình bày rõ ràng theo từng đoạn: Đặc điểm tinh bàn -> Cơ hội & Thử thách -> Lời khuyên ứng biến.
3. ĐỊNH DẠNG ĐẦU RA BẮT BUỘC (JSON):
{
  "chu_de": "%s",
  "noi_dung": "nội dung luận giải chi tiết",
  "muc_do_tin_cay": float (từ 0.8 đến 1.0)
}
""" % chu_de)

    return "\n".join(parts)
