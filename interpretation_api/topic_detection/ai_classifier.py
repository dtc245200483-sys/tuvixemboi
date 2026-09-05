import os
import sys

# T? ??ng ??nh tuy?n sys.path t?i backend
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
# -*- coding: utf-8 -*-
"""
Module phân loại chủ đề bằng trí tuệ nhân tạo (AI Classification):
- Được gọi khi Rule-based không chắc chắn hoặc câu hỏi phức tạp/mơ hồ.
- Tận dụng AIClient thống nhất từ backend/ai_module/.
- Kết hợp ngữ cảnh lịch sử trò chuyện (lich_su_chat) để phân loại chính xác câu hỏi tiếp nối.
"""

import json
from typing import Optional, List, Dict, Any

try:
    from ai_module.client import AIClient
    from ai_module.schemas import AIRequest
except ImportError:
    from backend.ai_module.client import AIClient
    from backend.ai_module.schemas import AIRequest

PROMPT_PHAN_LOAI_TOPIC = '''Bạn là chuyên gia phân loại chủ đề huyền học Đông Phương.
Nhiệm vụ: Xác định câu hỏi của người dùng thuộc hệ thống nào trong 4 hệ thống sau:
1. tu_vi: Tử Vi Đẩu Số (lá số, cung, sao, vận hạn...)
2. kinh_dich: Kinh Dịch / Chu Dịch (quẻ bói, hào từ, gieo quẻ, thoán từ...)
3. bat_tu: Bát Tự / Tứ Trụ (can chi, ngũ hành, dụng thần, thập thần, nhật chủ...)
4. nhan_tuong: Nhân Tướng Học (chỉ tay, bàn tay, khuôn mặt, nốt ruồi, tướng mạo...)
5. khong_ro: Câu hỏi hoàn toàn không rõ hệ thống nào hoặc không liên quan đến huyền học.

Bắt buộc trả về JSON với cấu trúc:
{
  "he_thong": "tu_vi" | "kinh_dich" | "bat_tu" | "nhan_tuong" | "khong_ro",
  "do_tin_cay": float (0.0 - 1.0),
  "ly_do_ngan_gon": "giải thích ngắn gọn lý do phân loại"
}
'''


def _clean_json_str(raw: str) -> str:
    s = raw.strip()
    if s.startswith("```"):
        lines = s.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        s = "\n".join(lines).strip()
    return s


def phan_loai_bang_ai(
    cau_hoi: str,
    lich_su_chat: Optional[List[Dict[str, str]]] = None,
    ai_client: Optional[AIClient] = None
) -> Dict[str, Any]:
    """
    Gọi AI Module để phân loại câu hỏi người dùng vào đúng 1 trong 4 hệ thống (hoặc 'khong_ro').
    """
    client = ai_client or AIClient()

    # Xây dựng prompt kèm lịch sử hội thoại nếu có
    prompt_lines = []
    if lich_su_chat:
        prompt_lines.append("Lịch sử các lượt trao đổi trước đó:")
        for msg in lich_su_chat[-4:]:  # Lấy tối đa 4 tin nhắn gần nhất
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_lines.append(f"- {role}: {content}")
        prompt_lines.append("")

    prompt_lines.append(f'Câu hỏi cần phân loại: "{cau_hoi}"')
    full_prompt = "\n".join(prompt_lines)

    req = AIRequest(
        prompt=full_prompt,
        system_instruction=PROMPT_PHAN_LOAI_TOPIC,
        temperature=0.1,
        max_tokens=200
    )

    resp = client.goi_ai_voi_retry(req)

    if not resp.thanh_cong or not resp.text:
        return {
            "he_thong": "khong_ro",
            "do_tin_cay": 0.0,
            "ly_do_ngan_gon": f"Lỗi gọi AI Classifier: {resp.loi_neu_co or 'Phản hồi rỗng'}"
        }

    try:
        data = json.loads(_clean_json_str(resp.text))
        he_thong = data.get("he_thong", "khong_ro")
        if he_thong not in ["tu_vi", "kinh_dich", "bat_tu", "nhan_tuong", "khong_ro"]:
            he_thong = "khong_ro"

        return {
            "he_thong": he_thong,
            "do_tin_cay": float(data.get("do_tin_cay", 0.5)),
            "ly_do_ngan_gon": data.get("ly_do_ngan_gon", "")
        }
    except Exception as e:
        return {
            "he_thong": "khong_ro",
            "do_tin_cay": 0.0,
            "ly_do_ngan_gon": f"Không thể parse JSON từ AI: {str(e)}"
        }
