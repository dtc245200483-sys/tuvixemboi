# -*- coding: utf-8 -*-
"""
Trục điều phối luận giải trung tâm (Interpretation Main Flow) - Tích hợp Toàn diện:
0. Kiểm tra Cache luận giải cố định (nếu có lá số/quẻ reference_id và là luận giải tổng quan) -> trả về ngay, tiết kiệm AI.
1. Xác định hệ thống (Topic Detection).
2. Xử lý câu hỏi mơ hồ -> trả về gợi ý câu hỏi (không gọi AI).
3. Xử lý hệ thống chưa có dữ liệu huấn luyện -> thông báo rõ ràng (không gọi AI).
4. Tra cứu Knowledge Base trong đúng namespace.
5. Ghép prompt template theo chuyên môn (Tử Vi, Kinh Dịch, Bát Tự, Nhân Tướng).
6. Kiểm tra Usage Quota hàng ngày TRƯỚC KHI gọi AI -> chặn nếu hết lượt.
7. Gọi AIClient với retry exponential backoff.
8. Parse phản hồi thành JSON có cấu trúc (retry 1 lần nếu sai định dạng).
9. Kiểm duyệt an toàn nội dung (Content Safety Guardrails - Prompt 6.4).
10. Lưu ChatHistory (nếu có db).
11. Lưu Cache luận giải tổng quan (nếu đủ điều kiện).
"""

import os
import sys
import copy
import json
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

# T? ??ng c?u h?nh sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from interpretation_api.topic_detection.detector import xac_dinh_he_thong
from interpretation_api.orchestrator.chat_context import lay_lich_su_chat, luu_lich_su_chat
from interpretation_api.orchestrator.cache_service import tao_cache_key, lay_ket_qua_cache, luu_ket_qua_cache
from interpretation_api.prompt_templates import (
    tao_prompt_luan_giai_tu_vi,
    tao_prompt_luan_giai_bat_tu,
    tao_prompt_luan_giai_kinh_dich,
    tao_prompt_luan_giai_nhan_tuong
)
from knowledge_base.search_service import search
from ai_module.client import AIClient
from ai_module.schemas import AIRequest

try:
    from content_safety.pipeline import xu_ly_an_toan_noi_dung
    from middleware.quota_service import kiem_tra_va_tang_quota
except ImportError:
    from backend.content_safety.pipeline import xu_ly_an_toan_noi_dung
    from backend.middleware.quota_service import kiem_tra_va_tang_quota

logger = logging.getLogger("InterpretationOrchestrator")


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


def luan_giai(
    user_id: str,
    cau_hoi: str,
    du_lieu_dau_vao: Dict[str, Any],
    co_dinh_kem_anh: bool = False,
    la_tong_quan: bool = False,
    db: Optional[Session] = None,
    ai_client: Optional[Any] = None,
    custom_kb_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Trục điều phối toàn bộ quy trình luận giải huyền học.
    """
    try:
        # Xác định reference_id và cờ luận giải tổng quan
        ref_id = du_lieu_dau_vao.get("id") or du_lieu_dau_vao.get("reference_id")
        is_general = (
            la_tong_quan or
            du_lieu_dau_vao.get("la_tong_quan") is True or
            du_lieu_dau_vao.get("loai_luan_giai") == "tong_quan"
        )
        explicit_system = du_lieu_dau_vao.get("he_thong")

        # BƯỚC 0: Kiểm tra cache nếu có reference_id và là luận giải tổng quan
        cache_key = None
        if db and ref_id and is_general and explicit_system:
            cache_key = tao_cache_key(he_thong=explicit_system, reference_id=str(ref_id), cau_hoi=None)
            cached_res = lay_ket_qua_cache(cache_key, db=db)
            if cached_res:
                logger.info(f"Lấy thành công kết quả từ cache cho reference_id: {ref_id}")
                res_copy = copy.deepcopy(cached_res)
                res_copy["tu_cache"] = True
                return res_copy

        # 1. Lấy ngữ cảnh lịch sử chat và xác định hệ thống
        if explicit_system and explicit_system in ["tu_vi", "bat_tu", "kinh_dich", "nhan_tuong"]:
            he_thong = explicit_system
            topic_info = {"he_thong": he_thong, "do_tin_cay": 1.0, "phuong_phap": "explicit"}
        else:
            lich_su = lay_lich_su_chat(user_id=user_id, so_luong_gan_nhat=5, db=db) if db else []
            topic_info = xac_dinh_he_thong(
                cau_hoi=cau_hoi,
                user_id=user_id,
                co_dinh_kem_anh=co_dinh_kem_anh,
                lich_su_chat=lich_su,
                ai_client=ai_client,
                check_kb_data=True,
                custom_kb_path=custom_kb_path
            )
            he_thong = topic_info.get("he_thong")

        # 2. Xử lý nếu cần hỏi lại người dùng
        if topic_info.get("can_hoi_lai"):
            return {
                "he_thong": None,
                "thanh_cong": False,
                "can_hoi_lai": True,
                "thong_bao": topic_info.get("goi_y_cau_hoi"),
                "cau_tra_loi": None,
                "nguon_tri_thuc_da_dung": []
            }

        # 3. Xử lý nếu hệ thống chưa có dữ liệu huấn luyện
        if topic_info.get("chua_co_du_lieu"):
            return {
                "he_thong": he_thong,
                "thanh_cong": False,
                "chua_co_du_lieu": True,
                "can_hoi_lai": False,
                "thong_bao": f"Hệ thống '{he_thong}' hiện chưa có đủ dữ liệu tri thức để luận giải chính xác.",
                "cau_tra_loi": None,
                "nguon_tri_thuc_da_dung": []
            }

        # Nếu chưa kiểm tra cache ở bước 0 (do chưa có explicit_system) nhưng nay đã xác định được hệ thống
        if db and ref_id and is_general and not cache_key:
            cache_key = tao_cache_key(he_thong=he_thong, reference_id=str(ref_id), cau_hoi=None)
            cached_res = lay_ket_qua_cache(cache_key, db=db)
            if cached_res:
                logger.info(f"Lấy thành công kết quả từ cache cho hệ thống: {he_thong}")
                res_copy = copy.deepcopy(cached_res)
                res_copy["tu_cache"] = True
                return res_copy

        # 4. Tra cứu Knowledge Base trong đúng namespace
        search_terms = [cau_hoi]
        if he_thong == "tu_vi":
            if "sao_chu_dao" in du_lieu_dau_vao:
                search_terms.append(str(du_lieu_dau_vao["sao_chu_dao"]))
            if "cung_menh" in du_lieu_dau_vao:
                search_terms.append(str(du_lieu_dau_vao["cung_menh"]))
        elif he_thong == "kinh_dich":
            if "que_chinh" in du_lieu_dau_vao:
                search_terms.append(str(du_lieu_dau_vao["que_chinh"]))
        elif he_thong == "bat_tu":
            if "dung_than" in du_lieu_dau_vao:
                search_terms.append(str(du_lieu_dau_vao["dung_than"]))
            if "nhat_chu" in du_lieu_dau_vao:
                search_terms.append(str(du_lieu_dau_vao["nhat_chu"]))

        search_query = " ".join(search_terms)

        tri_thuc_lien_quan: List[Dict[str, Any]] = []
        try:
            tri_thuc_lien_quan = search(
                query=search_query,
                namespace=he_thong,
                top_k=3,
                nguong_lien_quan=0.3,
                custom_db_path=custom_kb_path
            )
        except Exception as e:
            logger.warning(f"Lỗi tra cứu Knowledge Base ({he_thong}): {str(e)}")
            tri_thuc_lien_quan = []

        # 5. Ghép prompt luận giải theo đúng hệ thống
        if he_thong == "tu_vi":
            prompt = tao_prompt_luan_giai_tu_vi(du_lieu_dau_vao, tri_thuc_lien_quan, chu_de=cau_hoi)
        elif he_thong == "bat_tu":
            prompt = tao_prompt_luan_giai_bat_tu(du_lieu_dau_vao, tri_thuc_lien_quan, chu_de=cau_hoi)
        elif he_thong == "kinh_dich":
            prompt = tao_prompt_luan_giai_kinh_dich(du_lieu_dau_vao, tri_thuc_lien_quan, chu_de=cau_hoi)
        elif he_thong == "nhan_tuong":
            prompt = tao_prompt_luan_giai_nhan_tuong(du_lieu_dau_vao, tri_thuc_lien_quan, chu_de=cau_hoi)
        else:
            raise ValueError(f"Hệ thống không hợp lệ: {he_thong}")

        # 6. Kiểm tra và trừ Usage Quota TRƯỚC KHI gọi AI
        if db and user_id:
            quota_res = kiem_tra_va_tang_quota(user_id=user_id, db=db)
            if not quota_res.get("con_han_muc"):
                return {
                    "he_thong": he_thong,
                    "thanh_cong": False,
                    "het_quota": True,
                    "thong_bao": quota_res.get(
                        "thong_bao",
                        "Bạn đã dùng hết lượt hỏi hôm nay, vui lòng quay lại vào ngày mai."
                    ),
                    "cau_tra_loi": None,
                    "nguon_tri_thuc_da_dung": []
                }

        # 7. Gọi AI Client thống nhất
        client = ai_client or AIClient()
        req = AIRequest(prompt=prompt, temperature=0.2, max_tokens=1500)
        ai_resp = client.goi_ai_voi_retry(req)

        if not ai_resp.thanh_cong:
            return {
                "he_thong": he_thong,
                "thanh_cong": False,
                "thong_bao": f"Sự cố kết nối dịch vụ AI: {ai_resp.loi_neu_co}",
                "cau_tra_loi": None,
                "nguon_tri_thuc_da_dung": []
            }

        # 8. Parse response và xử lý fallback nếu sai định dạng JSON
        parsed_data = None
        try:
            parsed_data = json.loads(_clean_json_str(ai_resp.text))
        except Exception:
            prompt_retry = prompt + """\n\nLƯU Ý BẮT BUỘC: Bạn đã trả về sai format. Hãy CHỈ trả về đúng JSON hợp lệ {"chu_de": "...", "noi_dung": "...", "muc_do_tin_cay": 0.8}, không kèm bất kỳ text nào khác ngoài JSON."""
            req_2 = AIRequest(prompt=prompt_retry, temperature=0.1, max_tokens=1500)
            ai_resp_2 = client.goi_ai_voi_retry(req_2)
            try:
                parsed_data = json.loads(_clean_json_str(ai_resp_2.text))
            except Exception:
                return {
                    "he_thong": he_thong,
                    "thanh_cong": False,
                    "thong_bao": "Không thể xử lý phản hồi từ AI do sai định dạng kết quả sau 2 lần thử.",
                    "cau_tra_loi": None,
                    "nguon_tri_thuc_da_dung": []
                }

        if not tri_thuc_lien_quan:
            parsed_data["ghi_chu_gioi_han"] = "Phản hồi thận trọng do chưa tìm thấy tri thức cụ thể trong Knowledge Base."

        nguon_da_dung = [
            {
                "id": it.get("id"),
                "ten": it.get("ten"),
                "nguon_goc": it.get("nguon_goc"),
                "do_tin_cay": it.get("do_tin_cay")
            }
            for it in tri_thuc_lien_quan
        ]

        raw_result = {
            "he_thong": he_thong,
            "thanh_cong": True,
            "cau_tra_loi": parsed_data,
            "nguon_tri_thuc_da_dung": nguon_da_dung
        }

        # 9. Bắt buộc kiểm duyệt an toàn nội dung (Content Safety - Prompt 6.4)
        safe_result = xu_ly_an_toan_noi_dung(raw_result, ai_client=client)

        # 10. Lưu lịch sử hội thoại nếu có session database
        if db:
            luu_lich_su_chat(
                user_id=user_id,
                he_thong=he_thong,
                cau_hoi=cau_hoi,
                tra_loi=safe_result.get("cau_tra_loi", {}).get("noi_dung", ""),
                reference_id=ref_id,
                db=db
            )

        # 11. Lưu kết quả vào cache nếu là luận giải tổng quan
        if db and ref_id and is_general and safe_result.get("thanh_cong"):
            c_key = cache_key or tao_cache_key(he_thong=he_thong, reference_id=str(ref_id), cau_hoi=None)
            luu_ket_qua_cache(cache_key=c_key, he_thong=he_thong, ket_qua=safe_result, db=db, ttl_ngay=7)

        return safe_result

    except Exception as e:
        logger.error(f"Lỗi ngoại lệ trong Interpretation Orchestrator: {str(e)}")
        return {
            "he_thong": None,
            "thanh_cong": False,
            "thong_bao": "Hệ thống gặp sự cố trong quá trình luận giải. Vui lòng thử lại sau.",
            "cau_tra_loi": None,
            "nguon_tri_thuc_da_dung": []
        }
