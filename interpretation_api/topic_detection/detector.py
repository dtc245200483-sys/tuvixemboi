# -*- coding: utf-8 -*-
"""
Module tổng hợp xác định hệ thống huyền học (Topic Detector):
1. ƯU TIÊN nhận diện ảnh: Nếu co_dinh_kem_anh = True -> Nhân Tướng Học ngay lập tức.
2. ƯU TIÊN Rule-based: Quét từ khóa nhanh và tiết kiệm chi phí gọi AI.
3. Fallback AI Classifier: Khi câu hỏi mơ hồ hoặc chứa từ khóa xung đột, gọi AI Module xét cả ngữ cảnh.
4. Xử lý trường hợp chưa có dữ liệu huấn luyện (dem_so_luong == 0).
5. Xử lý câu hỏi hoàn toàn không rõ: Yêu cầu hỏi lại kèm gợi ý câu hỏi thân thiện.
"""

import logging
from typing import Optional, List, Dict, Any

from interpretation_api.topic_detection.rule_based import phat_hien_theo_tu_khoa
from interpretation_api.topic_detection.ai_classifier import phan_loai_bang_ai
from knowledge_base.vector_store import dem_so_luong

logger = logging.getLogger("TopicDetector")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


def xac_dinh_he_thong(
    cau_hoi: str,
    user_id: str = "anonymous",
    co_dinh_kem_anh: bool = False,
    lich_su_chat: Optional[List[Dict[str, str]]] = None,
    ai_client: Optional[Any] = None,
    check_kb_data: bool = True,
    custom_kb_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Hàm điều phối chính xác định hệ thống huyền học của yêu cầu.
    """
    # 1. Nếu có đính kèm ảnh sinh trắc học -> Quy thuộc ngay về Nhân Tướng Học
    if co_dinh_kem_anh:
        logger.info(f"[TOPIC_DETECT] User={user_id} | Đính kèm ảnh -> Hệ thống: 'nhan_tuong' (Phương pháp: dinh_kem_anh)")
        res = {
            "he_thong": "nhan_tuong",
            "chua_co_du_lieu": False,
            "can_hoi_lai": False,
            "phuong_phap": "dinh_kem_anh",
            "do_tin_cay": 1.0,
            "ly_do": "Người dùng đính kèm ảnh bàn tay/khuôn mặt thuộc nghiệp vụ Nhân Tướng Học."
        }
        if check_kb_data:
            so_luong = dem_so_luong("nhan_tuong", custom_db_path=custom_kb_path)
            if so_luong == 0:
                res["chua_co_du_lieu"] = True
        return res

    # 2. Thử phân loại bằng Rule-based (từ khóa đặc trưng)
    detected_sys = phat_hien_theo_tu_khoa(cau_hoi)
    method = "rule_based"
    confidence = 0.95
    reason = ""

    if detected_sys:
        system = detected_sys
        reason = f"Khớp chính xác bộ từ khóa đặc trưng của '{system}'."
    else:
        # 3. Chuyển sang AI Classifier khi không khớp hoặc có xung đột từ khóa
        method = "ai_classification"
        ai_res = phan_loai_bang_ai(cau_hoi, lich_su_chat=lich_su_chat, ai_client=ai_client)
        system = ai_res.get("he_thong", "khong_ro")
        confidence = float(ai_res.get("do_tin_cay", 0.5))
        reason = ai_res.get("ly_do_ngan_gon", "Phân loại bởi AI.")

    logger.info(
        f"[TOPIC_DETECT] User={user_id} | Câu hỏi: '{cau_hoi[:60]}...' | "
        f"Phương pháp={method} | Kết quả={system} | Độ tin cậy={confidence:.2f}"
    )

    # 4. Trường hợp không rõ hệ thống
    if not system or system == "khong_ro":
        return {
            "he_thong": None,
            "can_hoi_lai": True,
            "goi_y_cau_hoi": "Dạ bạn muốn tra cứu vận mệnh theo Tử Vi Đẩu Số, gieo quẻ Kinh Dịch, xem Bát Tự Tứ Trụ hay xem tướng mạo/chỉ tay ạ?",
            "phuong_phap": method,
            "do_tin_cay": confidence,
            "chua_co_du_lieu": False,
            "ly_do": reason or "Câu hỏi mơ hồ, chưa đủ dữ kiện để xác định chuyên khoa huyền học."
        }

    # 5. Kiểm tra xem hệ thống đã có dữ liệu train trong Knowledge Base chưa
    chua_co_du_lieu = False
    if check_kb_data:
        try:
            count = dem_so_luong(system, custom_db_path=custom_kb_path)
            if count == 0:
                chua_co_du_lieu = True
        except Exception as e:
            logger.warning(f"Lỗi khi kiểm tra số lượng tri thức của '{system}': {str(e)}")

    return {
        "he_thong": system,
        "chua_co_du_lieu": chua_co_du_lieu,
        "can_hoi_lai": False,
        "phuong_phap": method,
        "do_tin_cay": confidence,
        "ly_do": reason
    }
