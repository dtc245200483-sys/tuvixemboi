# -*- coding: utf-8 -*-
"""
Template prompt luận giải Tử Vi Đẩu Số.
"""

from typing import List, Dict, Any


def tao_prompt_luan_giai_tu_vi(
    la_so: Dict[str, Any],
    tri_thuc_lien_quan: List[Dict[str, Any]],
    chu_de: str = "tong_quan"
) -> str:
    """
    Ghép prompt luận giải Tử Vi chuẩn hóa.
    Bắt buộc AI bám sát tri thức cung cấp, không tự bịa ngoài phạm vi.
    """
    parts = []
    parts.append("=== THÔNG TIN LÁ SỐ TỬ VI ===")
    parts.append(f"- Chủ đề luận giải yêu cầu: {chu_de}")
    
    # Trích xuất các cung và sao nổi bật
    if "cung_menh" in la_so:
        parts.append(f"- Cung Mệnh: {la_so.get('cung_menh')}")
    if "cung_than" in la_so:
        parts.append(f"- Cung Thân: {la_so.get('cung_than')}")
    if "cuc" in la_so:
        parts.append(f"- Cục: {la_so.get('cuc')}")
    if "chinh_tinh" in la_so:
        parts.append(f"- Chính tinh: {la_so.get('chinh_tinh')}")
    if "sao_chu_dao" in la_so:
        parts.append(f"- Sao chủ đạo: {la_so.get('sao_chu_dao')}")
    if "chi_tiet_cung" in la_so:
        parts.append(f"- Chi tiết cung: {la_so.get('chi_tiet_cung')}")
    
    parts.append("\n=== TRI THỨC HUẤN LUYỆN TỬ KNOWLEDGE BASE ===")
    if tri_thuc_lien_quan:
        for idx, item in enumerate(tri_thuc_lien_quan, 1):
            ten = item.get("ten", "Tri thức")
            noi_dung = item.get("noi_dung_moi", "")
            nguon = item.get("nguon_goc", "Kinh điển")
            parts.append(f"[{idx}] {ten} (Nguồn: {nguon}): {noi_dung}")
    else:
        parts.append("LƯU Ý: Hiện không có tri thức cụ thể trong hệ thống cho trường hợp này. Hãy trả lời thận trọng, khách quan và nêu rõ giới hạn kiến thức.")

    parts.append("""
=== HƯỚNG DẪN LUẬN GIẢI ===
1. BẠN CHỈ ĐƯỢC LUẬN GIẢI DỰA TRÊN TRI THỨC ĐƯỢC CUNG CẤP Ở TRÊN. Tuyệt đối không tự bịa thêm ngoài phạm vi.
2. Giữ giọng văn khách quan, nhã nhặn, mang tính định hướng tích cực.
3. Bắt buộc trả về đúng JSON có cấu trúc:
{
  "chu_de": "%s",
  "noi_dung": "nội dung luận giải chi tiết",
  "muc_do_tin_cay": float (từ 0.0 đến 1.0 dựa trên độ đầy đủ của tri thức tham chiếu)
}
""" % chu_de)

    return "\n".join(parts)
