# -*- coding: utf-8 -*-
"""
Module nhận diện chủ đề dựa trên từ khóa (Rule-based Topic Detection):
- Quét câu hỏi và đếm số lượng từ khóa khớp với mỗi hệ thống.
- Trả về tên hệ thống nếu rõ ràng, không mơ hồ.
- Trả về None nếu không khớp từ khóa hoặc chứa từ khóa xung đột của nhiều hệ thống để chuyển sang AI.
"""

import re
from typing import Optional, Dict
from interpretation_api.topic_detection.keywords import KEYWORDS


def phat_hien_theo_tu_khoa(cau_hoi: str) -> Optional[str]:
    """
    Phát hiện hệ thống huyền học dựa trên bộ từ khóa đặc trưng.
    
    Quy tắc quyết định:
    1. Chuyển về chữ thường, tìm các cụm từ khóa.
    2. Tính điểm cho từng hệ thống.
    3. Nếu chỉ DUY NHẤT 1 hệ thống có điểm > 0 -> Trả về hệ thống đó.
    4. Nếu có >= 2 hệ thống cùng có từ khóa (xung đột) -> Trả về None (để AI phân loại).
    5. Nếu không có hệ thống nào có từ khóa -> Trả về None.
    """
    if not cau_hoi or not cau_hoi.strip():
        return None

    text_lower = cau_hoi.lower()

    scores: Dict[str, int] = {k: 0 for k in KEYWORDS.keys()}

    for he_thong, kw_list in KEYWORDS.items():
        for kw in kw_list:
            # Sử dụng ranh giới từ hoặc tìm kiếm chuỗi con đối với cụm từ nhiều tiếng
            if " " in kw:
                if kw in text_lower:
                    scores[he_thong] += 2  # Cụm từ dài đặc trưng có trọng số cao hơn
            else:
                # Từ đơn dùng regex boundary để tránh khớp sai trong từ khác
                pattern = r"(?<!\w)" + re.escape(kw) + r"(?!\w)"
                if re.search(pattern, text_lower):
                    scores[he_thong] += 1

    # Lọc các hệ thống có điểm > 0
    active_systems = {sys: score for sys, score in scores.items() if score > 0}

    # Trường hợp 1: Không có từ khóa nào khớp
    if not active_systems:
        return None

    # Trường hợp 2: Khớp từ khóa của từ 2 hệ thống trở lên (mơ hồ / xung đột)
    if len(active_systems) > 1:
        return None

    # Trường hợp 3: Khớp duy nhất 1 hệ thống
    return list(active_systems.keys())[0]
