# -*- coding: utf-8 -*-
"""
Template prompt luận giải Nhân Tướng Học (Chỉ tay & Khuôn mặt).
"""

from typing import List, Dict, Any


def tao_prompt_luan_giai_nhan_tuong(
    dac_diem: Dict[str, Any],
    tri_thuc_lien_quan: List[Dict[str, Any]],
    chu_de: str = "tong_quan"
) -> str:
    parts = []
    parts.append("=== ĐẶC ĐIỂM HÌNH THÁI QUAN SÁT (VISION AI) ===")
    parts.append(f"- Chủ đề luận giải yêu cầu: {chu_de}")
    
    for k, v in dac_diem.items():
        if v:
            parts.append(f"- {k}: {v}")

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
1. BẠN CHỈ ĐƯỢC LUẬN GIẢI DỰA TRÊN TRI THỨC ĐƯỢC CUNG CẤP Ở TRÊN.
2. Nhấn mạnh ý nghĩa nhân tướng khách quan, 'tướng tùy tâm sinh', khuyên tu dưỡng đạo đức.
3. Bắt buộc trả về đúng JSON có cấu trúc:
{
  "chu_de": "%s",
  "noi_dung": "nội dung luận giải chi tiết",
  "muc_do_tin_cay": float (0.0 đến 1.0)
}
""" % chu_de)
    return "\n".join(parts)
