# -*- coding: utf-8 -*-
"""
Moderation API Client dùng chung để kiểm tra các danh mục vi phạm tiêu chuẩn
(hate, harassment, self-harm, sexual, violence...).
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.error
import json

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from config import settings
except ImportError:
    from backend.config import settings

logger = logging.getLogger("ModerationClient")


def kiem_tra_moderation_api(text: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Gọi OpenAI Moderation API (hoặc endpoint tương đương) để kiểm duyệt văn bản.
    Trả về: {vi_pham: bool, danh_muc_vi_pham: list[str], muc_do: dict}
    """
    key = api_key or getattr(settings, "content_safety_api_key", "")
    
    # Nếu chưa cấu hình API key, mặc định cho qua ở tầng Moderation API
    # (việc chặn sẽ dựa vào bộ quy tắc custom keywords chuyên biệt).
    if not key or not key.strip():
        return {
            "vi_pham": False,
            "danh_muc_vi_pham": [],
            "muc_do": {}
        }

    url = "https://api.openai.com/v1/moderations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key.strip()}"
    }
    payload = json.dumps({"input": text}).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("results", [])
            if not results:
                return {"vi_pham": False, "danh_muc_vi_pham": [], "muc_do": {}}
            
            res0 = results[0]
            flagged = res0.get("flagged", False)
            categories = res0.get("categories", {})
            category_scores = res0.get("category_scores", {})
            
            danh_muc = [k for k, v in categories.items() if v is True]
            return {
                "vi_pham": flagged,
                "danh_muc_vi_pham": danh_muc,
                "muc_do": category_scores
            }
    except Exception as e:
        logger.warning(f"Gọi Moderation API thất bại ({str(e)}), chuyển sang chế độ dự phòng rule-based.")
        return {
            "vi_pham": False,
            "danh_muc_vi_pham": [],
            "muc_do": {},
            "loi": str(e)
        }
