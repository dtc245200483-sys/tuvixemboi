# -*- coding: utf-8 -*-
"""
Kiểm duyệt nội dung (Content Safety Checker):
Kết hợp giữa Moderation API tiêu chuẩn và bộ từ khóa ngữ cảnh huyền học Việt Nam.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from .moderation_client import kiem_tra_moderation_api
from .custom_keywords import TU_KHOA_CHAN_CUNG, TU_KHOA_CAN_MEM_HOA

logger = logging.getLogger("ContentSafetyChecker")


def kiem_duyet_noi_dung(
    text: str,
    custom_moderation_fn: Optional[Callable[[str], Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Kiểm duyệt văn bản đầu vào:
    1. Gọi Moderation API.
    2. Quét bộ từ khóa chặn cứng (Hard block).
    3. Quét bộ từ khóa cần làm mềm (Needs softening).
    4. Trả về kết quả đánh giá rõ ràng.
    """
    if not text or not text.strip():
        return {
            "qua_duyet": True,
            "can_mem_hoa": False,
            "danh_sach_cum_tu_can_sua": [],
            "ly_do": "Văn bản rỗng."
        }

    # 1. Kiểm tra qua Moderation API
    mod_fn = custom_moderation_fn or kiem_tra_moderation_api
    mod_res = mod_fn(text)
    
    if mod_res.get("vi_pham"):
        categories = mod_res.get("danh_muc_vi_pham", [])
        return {
            "qua_duyet": False,
            "can_mem_hoa": False,
            "ly_do": f"Vi phạm tiêu chuẩn an toàn (Moderation API: {', '.join(categories)})",
            "danh_muc": categories,
            "nguon_phat_hien": "moderation_api"
        }

    text_lower = text.lower()

    # 2. Quét từ khóa chặn cứng (TU_KHOA_CHAN_CUNG)
    matched_hard = [kw for kw in TU_KHOA_CHAN_CUNG if kw.lower() in text_lower]
    if matched_hard:
        return {
            "qua_duyet": False,
            "can_mem_hoa": False,
            "ly_do": f"Nội dung chứa thuật ngữ cực đoan/dọa nạn bị chặn: {', '.join(matched_hard)}",
            "danh_muc": ["hard_block_occult"],
            "tu_khoa_vi_pham": matched_hard,
            "nguon_phat_hien": "custom_keywords_hard"
        }

    # 3. Quét từ khóa cần làm mềm (TU_KHOA_CAN_MEM_HOA)
    matched_soft = [kw for kw in TU_KHOA_CAN_MEM_HOA if kw.lower() in text_lower]
    if matched_soft:
        return {
            "qua_duyet": True,
            "can_mem_hoa": True,
            "danh_sach_cum_tu_can_sua": matched_soft,
            "ly_do": f"Nội dung có xu hướng tuyệt đối hóa/tiêu cực, cần điều chỉnh mềm mại: {', '.join(matched_soft)}",
            "nguon_phat_hien": "custom_keywords_soft"
        }

    # 4. Hợp lệ hoàn toàn
    return {
        "qua_duyet": True,
        "can_mem_hoa": False,
        "danh_sach_cum_tu_can_sua": [],
        "ly_do": "Nội dung đạt chuẩn an toàn."
    }
