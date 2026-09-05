# -*- coding: utf-8 -*-
"""
Quy trình kiểm duyệt an toàn nội dung toàn diện (Content Safety Pipeline):
Bắt buộc thực thi sau mọi kết quả luận giải từ Interpretation Orchestrator.
"""

import copy
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable

from .checker import kiem_duyet_noi_dung
from .softener import mem_hoa_noi_dung

logger = logging.getLogger("ContentSafetyPipeline")

THONG_BAO_AN_TOAN_MAC_DINH = (
    "N?i dung n?y c?n ???c xem x?t l?i ?? ??m b?o t?nh t?ch c?c v? ph? h?p. "
    "Vui l?ng th? di?n ??t c?u h?i theo c?ch kh?c ho?c tham kh?o chuy?n gia t? v?n tr?c ti?p."
)


def xu_ly_an_toan_noi_dung(
    ket_qua_luan_giai: Dict[str, Any],
    ai_client: Optional[Any] = None,
    custom_moderation_fn: Optional[Callable[[str], Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Kiểm duyệt toàn bộ các phần nội dung trong kết quả luận giải:
    - Nếu bị chặn cứng -> thay bằng thông báo an toàn.
    - Nếu cần mềm hóa -> gọi mem_hoa_noi_dung -> tái kiểm tra.
    - Nếu sau mềm hóa vẫn vi phạm -> chuyển thẳng sang thông báo an toàn, không lặp vô hạn.
    - Ghi log audit riêng, tuyệt đối không ghi nội dung nhạy cảm.
    """
    if not ket_qua_luan_giai:
        return ket_qua_luan_giai

    res = copy.deepcopy(ket_qua_luan_giai)
    cau_tra_loi = res.get("cau_tra_loi")
    
    da_mem_hoa = False
    da_bi_chan = False

    if isinstance(cau_tra_loi, dict):
        for field, val in list(cau_tra_loi.items()):
            if not isinstance(val, str) or not val.strip():
                continue

            # Bước 1: Kiểm duyệt nội dung trường này
            check_res = kiem_duyet_noi_dung(val, custom_moderation_fn=custom_moderation_fn)

            # Bước 2: Xử lý nếu bị chặn cứng
            if not check_res.get("qua_duyet"):
                da_bi_chan = True
                # Ghi log audit an toàn (KHÔNG ghi nội dung nhạy cảm)
                logger.warning(
                    f"[CONTENT_SAFETY_AUDIT] Thời gian={datetime.now().isoformat()} | "
                    f"Trường={field} | Trạng thái=DA_BI_CHAN | "
                    f"Loại vi phạm={check_res.get('danh_muc', [])} | "
                    f"Lý do={check_res.get('ly_do')}"
                )
                cau_tra_loi[field] = THONG_BAO_AN_TOAN_MAC_DINH
                continue

            # Bước 3: Xử lý nếu cần mềm hóa
            if check_res.get("can_mem_hoa"):
                terms_to_fix = check_res.get("danh_sach_cum_tu_can_sua", [])
                logger.info(
                    f"[CONTENT_SAFETY_AUDIT] Thời gian={datetime.now().isoformat()} | "
                    f"Trường={field} | Trạng thái=CAN_MEM_HOA | "
                    f"Số lượng cụm từ={len(terms_to_fix)}"
                )
                
                # Mềm hóa lần 1
                softened = mem_hoa_noi_dung(val, terms_to_fix, ai_client=ai_client)
                
                # Tái kiểm tra nội dung sau khi mềm hóa
                recheck_res = kiem_duyet_noi_dung(softened, custom_moderation_fn=custom_moderation_fn)
                
                if (not recheck_res.get("qua_duyet")) or recheck_res.get("can_mem_hoa"):
                    # Nếu sau mềm hóa vẫn còn vi phạm -> chuyển thẳng thông báo an toàn mặc định
                    da_bi_chan = True
                    logger.warning(
                        f"[CONTENT_SAFETY_AUDIT] Thời gian={datetime.now().isoformat()} | "
                        f"Trường={field} | Trạng thái=MEM_HOA_THAT_BAI_CHUYEN_CHAN | "
                        f"Lý do={recheck_res.get('ly_do')}"
                    )
                    cau_tra_loi[field] = THONG_BAO_AN_TOAN_MAC_DINH
                else:
                    da_mem_hoa = True
                    cau_tra_loi[field] = softened

    # Gắn metadata kiểm duyệt vào kết quả
    res["kiem_duyet_an_toan"] = {
        "da_qua_duyet": not da_bi_chan,
        "da_mem_hoa": da_mem_hoa,
        "da_bi_chan": da_bi_chan
    }

    return res
