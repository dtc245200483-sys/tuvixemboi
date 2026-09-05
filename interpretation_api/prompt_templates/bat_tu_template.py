# -*- coding: utf-8 -*-
"""
Template prompt luận giải Bát Tự Tứ Trụ.
"""

from typing import List, Dict, Any


def tao_prompt_luan_giai_bat_tu(
    tu_tru: Dict[str, Any],
    tri_thuc_lien_quan: List[Dict[str, Any]],
    chu_de: str = "tong_quan"
) -> str:
    parts = []
    parts.append("=== THÔNG TIN TỨ TRỤ BÁT TỰ ===")
    parts.append(f"- Chủ đề luận giải yêu cầu: {chu_de}")
    
    if "nam" in tu_tru:
        parts.append(f"- Trụ Năm: {tu_tru.get('nam')}")
    if "thang" in tu_tru:
        parts.append(f"- Trụ Tháng: {tu_tru.get('thang')}")
    if "ngay" in tu_tru:
        parts.append(f"- Trụ Ngày (Nhật Trụ): {tu_tru.get('ngay')}")
    if "gio" in tu_tru:
        parts.append(f"- Trụ Giờ: {tu_tru.get('gio')}")
    if "nhat_chu" in tu_tru:
        parts.append(f"- Nhật Chủ: {tu_tru.get('nhat_chu')}")
    if "dung_than" in tu_tru:
        parts.append(f"- Dụng Thần: {tu_tru.get('dung_than')}")
    if "hy_than" in tu_tru:
        parts.append(f"- Hỷ Thần: {tu_tru.get('hy_than')}")

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
1. BẠN CHỈ ĐƯỢC LUẬN GIẢI DỰA TRÊN TRI THỨC ĐƯỢC CUNG CẤP Ở TRÊN. Tuyệt đối không tự bịa thêm.
2. Luận giải theo nguyên lý cân bằng âm dương ngũ hành và tác dụng của Dụng Thần.
3. Bắt buộc trả về đúng JSON có cấu trúc:
{
  "chu_de": "%s",
  "noi_dung": "nội dung luận giải chi tiết",
  "muc_do_tin_cay": float (0.0 đến 1.0)
}
""" % chu_de)
    return "\n".join(parts)
