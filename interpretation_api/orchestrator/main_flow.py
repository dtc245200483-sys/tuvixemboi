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
    from astro_engine.bat_tu.validator import kiem_tra_va_chuan_hoa_luan_giai_bat_tu
except ImportError:
    kiem_tra_va_chuan_hoa_luan_giai_bat_tu = None

try:
    from content_safety.pipeline import xu_ly_an_toan_noi_dung
    from middleware.quota_service import kiem_tra_va_tang_quota, hoan_lai_quota
except ImportError:
    from backend.content_safety.pipeline import xu_ly_an_toan_noi_dung
    from backend.middleware.quota_service import kiem_tra_va_tang_quota, hoan_lai_quota

logger = logging.getLogger("InterpretationOrchestrator")


def _extract_clean_content(raw: str, default_subject: str = "") -> Dict[str, Any]:
    """
    Bóc tách nội dung luận giải từ chuỗi trả về của AI:
    - Bóc tách JSON chuẩn nếu có.
    - Nếu JSON dở dang / lỗi cú pháp, tự động dùng Regex bóc tách trường 'noi_dung' và 'chu_de'.
    - Loại bỏ hoàn toàn các ký tự JSON wrapper, các ký tự escape \\n, \\" để trả về văn bản sạch 100%.
    """
    import re
    s = raw.strip()
    # 1. Loại bỏ thẻ suy nghĩ <think>...</think> nếu có
    if "<think>" in s and "</think>" in s:
        s = re.sub(r"<think>.*?</think>", "", s, flags=re.DOTALL).strip()
    # 2. Loại bỏ code block markdown ```json ... ```
    s = re.sub(r"^```[a-zA-Z]*\s*", "", s).strip()
    s = re.sub(r"\s*```$", "", s).strip()

    # Thử parse JSON trực tiếp
    try:
        data = json.loads(s)
        if isinstance(data, dict):
            content = data.get("noi_dung") or data.get("content") or data.get("cau_tra_loi")
            if isinstance(content, str) and content.strip():
                # Nếu nội dung lại bị lồng JSON bên trong
                if content.strip().startswith("{") and ('"noi_dung"' in content or '"chu_de"' in content):
                    return _extract_clean_content(content, default_subject)
                return {
                    "chu_de": data.get("chu_de") or default_subject,
                    "noi_dung": content.strip(),
                    "muc_do_tin_cay": float(data.get("muc_do_tin_cay", 0.85))
                }
    except Exception:
        pass

    # Nếu parse JSON trực tiếp thất bại (do JSON dở dang hoặc unescaped newlines):
    noi_dung_match = re.search(r'[*"]*noi_dung[*"]*\s*:\s*[*"]*(.*)', s, flags=re.DOTALL)
    if noi_dung_match:
        extracted = noi_dung_match.group(1).lstrip(' \t\n\r"*')
        extracted = re.sub(r'",\s*"muc_do_tin_cay".*$', '', extracted, flags=re.DOTALL)
        extracted = re.sub(r'"\s*}\s*$', '', extracted, flags=re.DOTALL)
        extracted = extracted.rstrip(' \t\n\r"}\'').strip()

        try:
            extracted = json.loads(f'"{extracted}"')
        except Exception:
            extracted = extracted.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')

        chu_de_match = re.search(r'[*"]*chu_de[*"]*\s*:\s*[*"]*([^"*]+)[*"]*', s)
        subject = chu_de_match.group(1).strip() if chu_de_match else default_subject

        return {
            "chu_de": subject,
            "noi_dung": extracted.strip(),
            "muc_do_tin_cay": 0.85
        }

    # Nếu không phải JSON, loại bỏ dấu bọc JSON còn sót
    clean_text = s
    clean_text = re.sub(r'^\s*\{\s*[*"]*chu_de[*"]*\s*:\s*[^,\n]*,?\s*[*"]*noi_dung[*"]*\s*:\s*[*"]*?', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'"?\s*(?:,\s*"muc_do_tin_cay"[^}]*)?\}\s*$', '', clean_text)
    clean_text = clean_text.replace('\\n', '\n').replace('\\"', '"')

    return {
        "chu_de": default_subject,
        "noi_dung": clean_text.strip(),
        "muc_do_tin_cay": 0.85
    }



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
                if (explicit_system == "bat_tu" or res_copy.get("he_thong") == "bat_tu") and kiem_tra_va_chuan_hoa_luan_giai_bat_tu:
                    cl = res_copy.get("cau_tra_loi")
                    if isinstance(cl, dict) and cl.get("noi_dung"):
                        cl["noi_dung"] = kiem_tra_va_chuan_hoa_luan_giai_bat_tu(
                            cl["noi_dung"],
                            du_lieu_dau_vao
                        )
                res_copy["tu_cache"] = True
                return res_copy

        # 1. Lấy ngữ cảnh lịch sử chat và xác định hệ thống
        session_id = du_lieu_dau_vao.get("session_id")
        if explicit_system and explicit_system in ["tu_vi", "bat_tu", "kinh_dich", "nhan_tuong"]:
            he_thong = explicit_system
            topic_info = {"he_thong": he_thong, "do_tin_cay": 1.0, "phuong_phap": "explicit"}
        else:
            lich_su = lay_lich_su_chat(user_id=user_id, so_luong_gan_nhat=5, session_id=session_id, db=db) if db else []
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

        # 3. Nếu KB trống -> KHÔNG chặn, chỉ ghi log để AI tự dùng kiến thức sẵn có trả lời
        if topic_info.get("chua_co_du_lieu"):
            logger.warning(
                f"[ORCHESTRATOR] Knowledge Base của hệ thống '{he_thong}' đang trống trên server. "
                "AI sẽ tự trả lời dựa trên kiến thức huyền học nội tại."
            )

        # Nếu chưa kiểm tra cache ở bước 0 (do chưa có explicit_system) nhưng nay đã xác định được hệ thống
        if db and ref_id and is_general and not cache_key:
            cache_key = tao_cache_key(he_thong=he_thong, reference_id=str(ref_id), cau_hoi=None)
            cached_res = lay_ket_qua_cache(cache_key, db=db)
            if cached_res:
                logger.info(f"Lấy thành công kết quả từ cache cho hệ thống: {he_thong}")
                res_copy = copy.deepcopy(cached_res)
                if (he_thong == "bat_tu" or res_copy.get("he_thong") == "bat_tu") and kiem_tra_va_chuan_hoa_luan_giai_bat_tu:
                    cl = res_copy.get("cau_tra_loi")
                    if isinstance(cl, dict) and cl.get("noi_dung"):
                        cl["noi_dung"] = kiem_tra_va_chuan_hoa_luan_giai_bat_tu(
                            cl["noi_dung"],
                            du_lieu_dau_vao
                        )
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

        # 5. Ghép prompt luận giải theo đúng hệ thống (kèm thông tin hồ sơ mệnh chủ nếu có)
        effective_question = cau_hoi
        if 'lich_su' not in locals():
            lich_su = lay_lich_su_chat(user_id=user_id, so_luong_gan_nhat=5, session_id=session_id, db=db) if db else []

        if len(cau_hoi.strip().split()) <= 4 and lich_su:
            prev_questions = [m.get("cau_hoi") for m in lich_su if m.get("cau_hoi") and len(m.get("cau_hoi", "")) > 10]
            if prev_questions:
                effective_question = f"{prev_questions[-1]} (Yêu cầu luận giải chuyên sâu theo {he_thong})"

        ho_so_mc = du_lieu_dau_vao.get("ho_so_menh_chu")
        if ho_so_mc and isinstance(ho_so_mc, dict):
            mc_ten = ho_so_mc.get("ho_ten", "")
            mc_gioi_tinh = "Nam" if ho_so_mc.get("gioi_tinh") == "nam" else "Nữ"
            mc_ngay_sinh = ho_so_mc.get("ngay_sinh_duong", "")
            mc_gio_sinh = ho_so_mc.get("gio_sinh", "")
            effective_question = (
                f"{effective_question}\n"
                f"[THÔNG TIN NGƯỜI HỎI (MỆNH CHỦ)]: Họ tên: {mc_ten}, Giới tính: {mc_gioi_tinh}, Ngày sinh: {mc_ngay_sinh}, Giờ: {mc_gio_sinh}h. "
                f"Hãy xưng hô và đưa ra lời giải đáp tương thích theo thông tin này."
            )

        if he_thong == "tu_vi":
            prompt = tao_prompt_luan_giai_tu_vi(du_lieu_dau_vao, tri_thuc_lien_quan, chu_de=effective_question)
        elif he_thong == "bat_tu":
            prompt = tao_prompt_luan_giai_bat_tu(du_lieu_dau_vao, tri_thuc_lien_quan, chu_de=effective_question)
        elif he_thong == "kinh_dich":
            prompt = tao_prompt_luan_giai_kinh_dich(du_lieu_dau_vao, tri_thuc_lien_quan, chu_de=effective_question)
        elif he_thong == "nhan_tuong":
            prompt = tao_prompt_luan_giai_nhan_tuong(du_lieu_dau_vao, tri_thuc_lien_quan, chu_de=effective_question)
        else:
            raise ValueError(f"Hệ thống không hợp lệ: {he_thong}")

        # Bổ sung quy chuẩn an toàn nội dung nghiêm ngặt chống từ ngữ cực đoan
        prompt += (
            "\n\n[QUY CHUẨN AN TOÀN NỘI DUNG VÀ ĐẠO ĐỨC]:\n"
            "- TUYỆT ĐỐI KHÔNG sử dụng các từ ngữ cực đoan, phán xét đoản mạng, tử vong, chết chóc, tuyệt mệnh, ung thư, tự sát, tự tử.\n"
            "- Luôn hướng dẫn tích cực, an tâm, gợi mở hướng cải thiện phúc đức, tu tâm dưỡng tính theo triết lý 'Tướng tùy tâm sinh, đức năng thắng số'."
        )

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

        # 7. Gọi AI Client thống nhất (tăng max_tokens lên 2500 để luận giải đầy đủ 8 mục không bị ngắt)
        client = ai_client or AIClient()
        req = AIRequest(prompt=prompt, temperature=0.2, max_tokens=2500)
        ai_resp = client.goi_ai_voi_retry(req)

        if not ai_resp.thanh_cong:
            if db and user_id:
                hoan_lai_quota(user_id=user_id, db=db)
            return {
                "he_thong": he_thong,
                "thanh_cong": False,
                "thong_bao": "Hệ thống AI đang bận kết nối. Quý bạn vui lòng nhấn lại để tiếp tục.",
                "cau_tra_loi": None,
                "nguon_tri_thuc_da_dung": []
            }

        # 8. Bóc tách nội dung luận giải chuẩn sạch 100%, không để lọt vỏ bọc JSON hay ký tự lạ
        parsed_data = _extract_clean_content(ai_resp.text, default_subject=cau_hoi)

        if not parsed_data.get("noi_dung"):
            logger.warning(f"[ORCHESTRATOR] Bóc tách nội dung rỗng! ai_resp.text len={len(ai_resp.text)}, preview={repr(ai_resp.text[:300])}")
            if db and user_id:
                hoan_lai_quota(user_id=user_id, db=db)
            return {
                "he_thong": he_thong,
                "thanh_cong": False,
                "thong_bao": "Hệ thống AI đang bận kết nối. Quý bạn vui lòng nhấn lại để tiếp tục.",
                "cau_tra_loi": None,
                "nguon_tri_thuc_da_dung": []
            }



        # Chuẩn hóa bắt buộc cho Bát Tự theo sách Trần Khang Ninh (trang 30-31)
        if he_thong == "bat_tu" and kiem_tra_va_chuan_hoa_luan_giai_bat_tu and parsed_data.get("noi_dung"):
            parsed_data["noi_dung"] = kiem_tra_va_chuan_hoa_luan_giai_bat_tu(
                parsed_data["noi_dung"],
                du_lieu_dau_vao
            )

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
                session_id=session_id,
                db=db
            )

        # 11. Lưu kết quả vào cache nếu là luận giải tổng quan
        if db and ref_id and is_general and safe_result.get("thanh_cong"):
            c_key = cache_key or tao_cache_key(he_thong=he_thong, reference_id=str(ref_id), cau_hoi=None)
            luu_ket_qua_cache(cache_key=c_key, he_thong=he_thong, ket_qua=safe_result, db=db, ttl_ngay=7)

        return safe_result

    except Exception as e:
        logger.error(f"Lỗi ngoại lệ trong Interpretation Orchestrator: {str(e)}")
        if db and user_id:
            try:
                hoan_lai_quota(user_id=user_id, db=db)
            except Exception:
                pass
        return {
            "he_thong": None,
            "thanh_cong": False,
            "thong_bao": "Hệ thống AI đang bận kết nối. Quý bạn vui lòng nhấn lại để tiếp tục.",
            "cau_tra_loi": None,
            "nguon_tri_thuc_da_dung": []
        }

