# -*- coding: utf-8 -*-
"""
Module phân tích đặc điểm hình thái Bàn tay và Khuôn mặt thông qua Vision AI.
Sử dụng AIClient tập trung từ backend/ai_module/ để đảm bảo thống nhất quản lý kết nối,
retry backoff và ghi log bảo mật.
"""

import json
from typing import Callable, Optional, Dict, Any

from vision_module.schemas import DacDiemTay, DacDiemMat
from vision_module.preprocessor import kiem_tra_chat_luong_anh, resize_va_chuan_hoa
from vision_module.prompts import PROMPT_PHAN_TICH_TAY, PROMPT_PHAN_TICH_MAT
from ai_module.client import AIClient
from ai_module.schemas import AIRequest

_ai_client = AIClient()


def _clean_json_markdown(raw_text: str) -> str:
    """Làm sạch chuỗi JSON trả về từ AI (loại bỏ markdown block ```json ... ```)."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # Bỏ dòng đầu (```json hoặc ```) và dòng cuối (```)
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _call_unified_vision_ai(prompt: str, anh_bytes: bytes) -> str:
    """Gọi Vision AI thông qua AIClient tập trung với cơ chế retry tự động."""
    req = AIRequest(
        prompt=prompt,
        image_bytes=anh_bytes,
        temperature=0.1,
        max_tokens=1500
    )
    resp = _ai_client.goi_ai_voi_retry(req)
    if not resp.thanh_cong:
        raise ValueError(f"Lỗi khi kết nối với Vision AI: {resp.loi_neu_co}")
    return resp.text


def phan_tich_anh_tay(
    anh_bytes: bytes,
    ai_caller: Optional[Callable[[str, bytes], str]] = None
) -> DacDiemTay:
    """
    1. Phân tích ảnh bàn tay và trả về DacDiemTay mô tả khách quan.
    """
    # 1. Kiểm tra chất lượng
    qc = kiem_tra_chat_luong_anh(anh_bytes)
    if not qc["dat_yeu_cau"]:
        raise ValueError(f"Chất lượng ảnh không đạt yêu cầu: {qc['ly_do_neu_khong_dat']}")

    # 2. Chuẩn hóa ảnh
    chuan_hoa_bytes = resize_va_chuan_hoa(anh_bytes)

    # 3. Gọi Vision AI
    caller = ai_caller or _call_unified_vision_ai
    try:
        raw_response = caller(PROMPT_PHAN_TICH_TAY, chuan_hoa_bytes)
    except Exception as e:
        raise ValueError(f"Lỗi khi kết nối với Vision AI: {str(e)}")

    # 4. Parse JSON & Xử lý fallback
    clean_text = _clean_json_markdown(raw_response)
    try:
        parsed_dict = json.loads(clean_text)
        return DacDiemTay(**parsed_dict)
    except Exception:
        raise ValueError("Vision AI trả lời không đúng định dạng mong đợi. Vui lòng chụp lại ảnh bàn tay rõ nét hơn và thử lại.")


def phan_tich_anh_mat(
    anh_bytes: bytes,
    ai_caller: Optional[Callable[[str, bytes], str]] = None
) -> DacDiemMat:
    """
    2. Phân tích ảnh khuôn mặt và trả về DacDiemMat mô tả hình thái khách quan.
    """
    # 1. Kiểm tra chất lượng
    qc = kiem_tra_chat_luong_anh(anh_bytes)
    if not qc["dat_yeu_cau"]:
        raise ValueError(f"Chất lượng ảnh không đạt yêu cầu: {qc['ly_do_neu_khong_dat']}")

    # 2. Chuẩn hóa ảnh
    chuan_hoa_bytes = resize_va_chuan_hoa(anh_bytes)

    # 3. Gọi Vision AI
    caller = ai_caller or _call_unified_vision_ai
    try:
        raw_response = caller(PROMPT_PHAN_TICH_MAT, chuan_hoa_bytes)
    except Exception as e:
        raise ValueError(f"Lỗi khi kết nối với Vision AI: {str(e)}")

    # 4. Parse JSON & Xử lý fallback
    clean_text = _clean_json_markdown(raw_response)
    try:
        parsed_dict = json.loads(clean_text)
        return DacDiemMat(**parsed_dict)
    except Exception:
        raise ValueError("Vision AI trả lời không đúng định dạng mong đợi. Vui lòng chụp lại ảnh khuôn mặt rõ nét hơn và thử lại.")
