# -*- coding: utf-8 -*-
"""
Mô đun làm mềm ngôn từ (Content Softener):
Sử dụng AI để biến đổi các phán quyết mang tính tuyệt đối hoặc gây hoang mang
thành lời khuyên tích cực, nhẹ nhàng và xây dựng theo triết lý 'dức năng thắng số'.
"""

import os
import sys
import re
import logging
from typing import List, Optional, Any

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from ai_module.client import AIClient
from ai_module.schemas import AIRequest

logger = logging.getLogger("ContentSoftener")

# Bảng ánh xạ thay thế dự phòng thông minh (Rule-based Fallback)
FALLBACK_REPLACEMENTS = {
    "ch?c ch?n g?p ??i h?n": "c?n ??c bi?t l?u ? c?n tr?ng trong c?c giai ?o?n th? th?ch",
    "s? ph?n bi ??t": "cu?c s?ng tr?i qua m?t s? giai ?o?n c?n ki?n tr? t?i luy?n",
    "b? t?c ho?n to?n": "t?m th?i g?p tr? ng?i c?n b?nh t?nh t?m h??ng gi?i quy?t",
    "kh?ng c?n ???ng lui": "c?n suy x?t k? l??ng tr??c khi ??a ra quy?t ??nh quan tr?ng",
    "v?n xui ?eo b?m c? ??i": "c? nh?ng giai ?o?n v?n tr?nh ch?m l?i ?? t?ch l?y kinh nghi?m",
    "kh?ng c? l?i tho?t": "c?n th?m th?i gian v? s? ki?n nh?n ?? t?m gi?i ph?p ph? h?p",
    "t?ng gia b?i s?n": "c?n th?n tr?ng t?i ?a trong qu?n l? t?i ch?nh v? ??u t?",
    "tr?ng tay ho?n to?n": "c?n ch? tr?ng t?ch l?y v? ki?m so?t r?i ro t?i s?n",
    "ng??i ph?i ng?u ph?n b?i": "c?n ch? ? vun ??p v? l?ng nghe trong ??i s?ng h?n nh?n",
    "kh?ng th? n?o th?nh c?ng": "c?n n? l?c nhi?u h?n v? t?m h??ng ?i ph? h?p h?n",
    "v? ph??ng c?u v?n": "c?n gi? t?m th? ?i?m t?nh ?? t?ng b??c th?o g? kh? kh?n",
    "s? nghi?p s?p ?? ho?n to?n": "s? nghi?p c? giai ?o?n chuy?n d?ch c?n t?i c?u tr?c",
    "gia ??nh tan n?t": "gia ??o c? l?c b?t h?a c?n s? nh?n nh?n v? th?u hi?u",
    "v?n h?n kh?ng th? tr?nh": "th? th?ch mang t?nh chu k? c? th? chuy?n h?a b?ng s? tu d??ng",
    "cu?c ??i ?en ??i t?t c?ng": "giai ?o?n tr?c tr? l? c? h?i ?? t?i luy?n b?n l?nh"
}


def mem_hoa_noi_dung(
    text: str,
    danh_sach_cum_tu_can_sua: List[str],
    ai_client: Optional[Any] = None
) -> str:
    """
    Viết lại đoạn văn giữ nguyên ý nghĩa cốt lõi nhưng diễn đạt nhẹ nhàng,
    tránh ngôn từ tuyệt đối hóa hoặc gây hoảng sợ.
    """
    if not text or not text.strip():
        return text

    prompt = f"""Bạn là chuyên gia cố vấn tâm lý và huyền học mang phong cách nhã nhặn, định hướng tích cực.
Hãy viết lại đoạn văn luận giải sau đây:
- Giữ nguyên bản chất tri thức của lá số/quẻ.
- TUYỆT ĐỐI KHÔNG dùng các cụm từ tiêu cực/tuyệt đối sau: {', '.join(danh_sach_cum_tu_can_sua)}.
- Thay thế bằng cách diễn đạt xây dựng, đề cao giáo dục tu dưỡng, thận trọng, không gây hoang mang.
- CHỈ TRẢ VỀ ĐOẠN VĂN ĐÃ SỬA, không thêm lời dẫn.

Đoạn văn cần viết lại:
"{text}"
"""

    client = ai_client or AIClient()
    req = AIRequest(prompt=prompt, temperature=0.3, max_tokens=1000)

    try:
        resp = client.goi_ai_voi_retry(req)
        if resp.thanh_cong and resp.text and resp.text.strip():
            softened = resp.text.strip()
            # Bỏ qua dấu ngoặc kép nếu AI trả về bọc trong nháy
            if softened.startswith('"') and softened.endswith('"'):
                softened = softened[1:-1].strip()
            return softened
    except Exception as e:
        logger.warning(f"Gọi AI làm mềm thất bại ({str(e)}), áp dụng fallback thay thế từ ngữ.")

    # Fallback: Thay thế trực tiếp các cụm từ bằng phương án nhẹ nhàng hơn
    result = text
    for term in danh_sach_cum_tu_can_sua:
        replacement = FALLBACK_REPLACEMENTS.get(
            term.lower(),
            "c?n l?u ? c?n tr?ng v? gi? t?m th? b?nh t?nh ?? chuy?n h?a"
        )
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        result = pattern.sub(replacement, result)

    return result
