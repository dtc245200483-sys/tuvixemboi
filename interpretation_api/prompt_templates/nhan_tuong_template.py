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
2. QUY TẮC PHÂN BIỆT NỐT RUỒI & MỤN/TÌ VẾT TẠM THỜI:
   - CHỈ luận giải nốt ruồi nếu 'vi_tri_not_ruoi' ghi nhận rõ ràng là nốt ruồi sắc tố cố định.
   - TUYỆT ĐỐI KHÔNG luận giải các đốm trong 'ti_vet_da_lieu_hoac_mun' (mụn trứng cá, vết thâm mụn sậm màu, sẹo tạm thời) thành nốt ruồi định mệnh hay điềm báo tướng số. Trong Nhân Tướng Học: "Khí trệ sinh mụn, mụn là biểu hiện nội tiết / phong nhiệt tạm thời, không phải bộ vị diện tướng cố định".
   - Nếu có mụn hoặc tì vết tạm thời, hãy giải thích khách quan, nhắc nhở mệnh chủ giữ tinh thần thư thái, vệ sinh da liễu tốt, tuyệt đối không hoang mang lo lắng.
3. Nhấn mạnh ý nghĩa nhân tướng khách quan, 'tướng tùy tâm sinh, tướng do tâm đổi', khuyên tu dưỡng đạo đức và sống an nhiên.
4. Bắt buộc trả về đúng JSON có cấu trúc:
{
  "chu_de": "%s",
  "noi_dung": "nội dung luận giải chi tiết",
  "muc_do_tin_cay": float (0.0 đến 1.0)
}
""" % chu_de)
    return "\n".join(parts)
