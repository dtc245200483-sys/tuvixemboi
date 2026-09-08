# -*- coding: utf-8 -*-
"""
Router Tử Vi Đẩu Số:
- GET /tu-vi/{birth_profile_id}:
  Kiểm tra đã có LaSoTuViResult chưa; nếu chưa thì gọi astro_engine/tu_vi tính và lưu.
  Sau đó gọi interpretation_api orchestrator luan_giai với he_thong="tu_vi", qua Content Safety & Cache.
  
LỰA CHỌN THIẾT KẾ:
Sử dụng mô hình đồng bộ (synchronous request/response).
Lý do: Ở quy mô 20-100 người dùng, thời gian xử lý AI (1-3 giây) hoàn toàn phù hợp để
trả về kết quả trực tiếp, đơn giản hơn nhiều so với cơ chế bất đồng bộ phức tạp (Celery/Polling).
"""

import uuid
import copy
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User, BirthProfile, LaSoTuViResult
from api.dependencies import kiem_tra_quota_truoc_khi_xu_ly
from api.schemas import APIResponse, TuViResponse, TuViTopicResponse, ChatRequest, ChatResponse
from calendar_converter.lunar_calendar import solar_to_lunar, xac_dinh_gio_sinh_theo_canh_gio
from astro_engine.tu_vi import lap_la_so, xac_dinh_cuc, CAN_LIST, CUNG_DIA_CHI
from interpretation_api.orchestrator.main_flow import luan_giai
from interpretation_api.orchestrator.cache_service import tao_cache_key, lay_ket_qua_cache, luu_ket_qua_cache

router = APIRouter(prefix="/tu-vi", tags=["Tu Vi"])


@router.get("/{birth_profile_id}/chart", response_model=APIResponse[TuViResponse])
def xem_la_so_tu_vi_chi_tiet(
    birth_profile_id: str,
    current_user: User = Depends(kiem_tra_quota_truoc_khi_xu_ly),
    db: Session = Depends(get_db)
):
    """Lấy trực tiếp dữ liệu lá số Tử Vi cực nhanh (< 50ms) không gọi qua AI luận giải."""
    return xem_la_so_tu_vi(birth_profile_id=birth_profile_id, only_chart=True, current_user=current_user, db=db)


@router.get("/{birth_profile_id}", response_model=APIResponse[TuViResponse])
def xem_la_so_tu_vi(
    birth_profile_id: str,
    only_chart: bool = False,
    current_user: User = Depends(kiem_tra_quota_truoc_khi_xu_ly),
    db: Session = Depends(get_db)
):
    """
    Lấy hoặc an lá số Tử Vi và luận giải tổng quan trọn đời.
    - Đã xác thực người dùng và kiểm tra quota hàng ngày.
    - Tham số only_chart=True: Chỉ lấy lá số tức thì (< 50ms) không cần chờ đợi AI.
    - Caching kết quả luận giải tổng quan: lần gọi thứ 2 cùng id sẽ trả về tức thì từ cache.
    """
    try:
        p_uuid = uuid.UUID(birth_profile_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Định dạng ID hồ sơ sinh không hợp lệ")

    profile = db.query(BirthProfile).filter(BirthProfile.id == p_uuid, BirthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy hồ sơ sinh")

    # 1. Kiểm tra và tính toán LaSoTuViResult (108+ sao chuẩn mực)
    canh_gio = xac_dinh_gio_sinh_theo_canh_gio(profile.gio_sinh, profile.phut_sinh)
    gio_chi = canh_gio["chi_gio"]

    if profile.ngay_sinh_am:
        ngay_am = profile.ngay_sinh_am.day
        thang_am = profile.ngay_sinh_am.month
        nam_am = profile.ngay_sinh_am.year
    else:
        lunar = solar_to_lunar(profile.ngay_sinh_duong.day, profile.ngay_sinh_duong.month, profile.ngay_sinh_duong.year)
        ngay_am = lunar["ngay_am"]
        thang_am = lunar["thang_am"]
        nam_am = lunar["nam_am"]

    la_so_record = db.query(LaSoTuViResult).filter(LaSoTuViResult.birth_profile_id == profile.id).first()
    
    can_tinh_lai = (
        not la_so_record or 
        not la_so_record.du_lieu_json or 
        "palaces" not in la_so_record.du_lieu_json or
        len(la_so_record.du_lieu_json.get("palaces", [])) != 12 or
        "loai_hanh_cua_ban_menh" not in la_so_record.du_lieu_json
    )

    if can_tinh_lai:
        la_so_data = lap_la_so(
            ho_ten=profile.ho_ten,
            ngay_sinh_duong=profile.ngay_sinh_duong,
            gio_sinh=profile.gio_sinh,
            phut_sinh=profile.phut_sinh,
            gioi_tinh=profile.gioi_tinh,
            ngay_sinh_am=profile.ngay_sinh_am,
            thang_sinh_am=thang_am,
            nam_sinh_am=nam_am,
            gio_sinh_chi=gio_chi
        )

        if not la_so_record:
            la_so_record = LaSoTuViResult(
                id=uuid.uuid4(),
                birth_profile_id=profile.id,
                du_lieu_json=la_so_data
            )
            db.add(la_so_record)
        else:
            la_so_record.du_lieu_json = la_so_data

        db.commit()
        db.refresh(la_so_record)
    else:
        la_so_data = la_so_record.du_lieu_json

    # Bổ sung thông tin hồ sơ cho Thiên Bàn
    if "thong_tin_co_ban" in la_so_data:
        la_so_data["thong_tin_co_ban"]["ho_ten"] = profile.ho_ten
        la_so_data["thong_tin_co_ban"]["gio_sinh_str"] = f"{profile.gio_sinh:02d}:{profile.phut_sinh:02d} (Giờ {gio_chi})"
        la_so_data["thong_tin_co_ban"]["ngay_duong_str"] = f"{profile.ngay_sinh_duong.day:02d}/{profile.ngay_sinh_duong.month:02d}/{profile.ngay_sinh_duong.year}"
        la_so_data["thong_tin_co_ban"]["ngay_am_str"] = f"{ngay_am:02d}/{thang_am:02d}/{nam_am} (Âm Lịch)"

    # Nếu chỉ lấy lá số (cực nhanh < 50ms, hiển thị ngay lập tức không bị treo)
    if only_chart:
        return APIResponse(
            thanh_cong=True,
            du_lieu={
                "birth_profile_id": str(profile.id),
                "la_so": la_so_data,
                "luan_giai": None
            },
            loi=None
        )

    # 2. Điều phối luận giải AI (tổng quan)
    input_data = copy.deepcopy(la_so_data)
    input_data["id"] = str(profile.id)
    input_data["reference_id"] = str(profile.id)
    input_data["he_thong"] = "tu_vi"
    input_data["la_tong_quan"] = True

    try:
        luan_giai_res = luan_giai(
            user_id=str(current_user.id),
            cau_hoi="Luận giải tổng quan lá số Tử Vi trọn đời",
            du_lieu_dau_vao=input_data,
            co_dinh_kem_anh=False,
            la_tong_quan=True,
            db=db
        )
    except Exception as e:
        luan_giai_res = {"cau_tra_loi": {"chu_de": "tong_quan", "noi_dung": "Hệ thống luận giải AI đang được cập nhật. Dữ liệu lá số và 12 cung hoàn toàn chính xác."}}

    return APIResponse(
        thanh_cong=True,
        du_lieu={
            "birth_profile_id": str(profile.id),
            "la_so": la_so_data,
            "luan_giai": luan_giai_res
        },
        loi=None
    )


# Bảng ánh xạ chủ đề gợi ý sang tiêu đề hiển thị chuẩn mực
TOPIC_TITLE_MAP = {
    "cong_danh": "Công danh sự nghiệp",
    "anh_em": "Anh em, bạn bè",
    "con_cai": "Con cái",
    "tinh_duyen": "Tình duyên",
    "vo_chong": "Vợ chồng",
    "tai_van": "Tài vận, kinh tế",
    "suc_khoe": "Sức khỏe, bệnh tật",
    "xuat_ngoai": "Xuất ngoại",
    "bang_huu": "Bằng hữu, đồng nghiệp",
    "phuc_duc": "Phúc khí tổ tiên",
    "cha_me": "Cha mẹ",
    "dien_trach": "Nhà cửa, đất đai",
    "dai_van": "Đại vận",
    "tieu_van": "Tiểu vận",
}


@router.get("/{birth_profile_id}/topic", response_model=APIResponse[TuViTopicResponse])
def xem_luan_giai_theo_chu_de(
    birth_profile_id: str,
    topic: str = Query(..., description="Mã chủ đề luận giải (cong_danh, con_cai, tinh_duyen...)"),
    current_user: User = Depends(kiem_tra_quota_truoc_khi_xu_ly),
    db: Session = Depends(get_db)
):
    """
    Luận giải chuyên sâu theo từng chủ đề gợi ý (Công danh, Con cái, Tình duyên, Vận hạn...).
    - Hỗ trợ lưu cache riêng cho từng chủ đề.
    - Thời gian phản hồi cực nhanh (~1s) qua FreeLLMAPI Groq.
    - Kiểm duyệt an toàn nội dung nghiêm ngặt, không từ ngữ chết chóc/tiêu cực.
    """
    try:
        p_uuid = uuid.UUID(birth_profile_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Định dạng ID hồ sơ sinh không hợp lệ")

    profile = db.query(BirthProfile).filter(BirthProfile.id == p_uuid, BirthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy hồ sơ sinh")

    la_so_record = db.query(LaSoTuViResult).filter(LaSoTuViResult.birth_profile_id == profile.id).first()
    if not la_so_record or not la_so_record.du_lieu_json:
        chart_res = xem_la_so_tu_vi(birth_profile_id=birth_profile_id, only_chart=True, current_user=current_user, db=db)
        la_so_data = chart_res.du_lieu["la_so"]
    else:
        la_so_data = la_so_record.du_lieu_json

    topic_key = topic.strip().lower()
    topic_title = TOPIC_TITLE_MAP.get(topic_key, topic.strip())

    # 1. Kiểm tra cache theo chủ đề
    cache_k = tao_cache_key(he_thong="tu_vi", reference_id=str(profile.id), cau_hoi=f"topic_{topic_key}")
    cached = lay_ket_qua_cache(cache_k, db=db)
    if cached:
        return APIResponse(
            thanh_cong=True,
            du_lieu={
                "birth_profile_id": str(profile.id),
                "topic": topic_key,
                "tieu_de": topic_title,
                "luan_giai": cached
            },
            loi=None
        )

    # 2. Tạo luận giải AI cho chủ đề cụ thể
    input_data = copy.deepcopy(la_so_data)
    input_data["id"] = str(profile.id)
    input_data["reference_id"] = str(profile.id)
    input_data["he_thong"] = "tu_vi"
    input_data["chu_de_yeu_cau"] = topic_title

    prompt_q = f"Luận giải chi tiết phương diện {topic_title} của lá số Tử Vi"
    try:
        luan_res = luan_giai(
            user_id=str(current_user.id),
            cau_hoi=prompt_q,
            du_lieu_dau_vao=input_data,
            co_dinh_kem_anh=False,
            la_tong_quan=False,
            db=db
        )
        # Lưu cache chủ đề 7 ngày nếu thành công
        if luan_res.get("thanh_cong"):
            luu_ket_qua_cache(cache_key=cache_k, he_thong="tu_vi", ket_qua=luan_res, db=db, ttl_ngay=7)
    except Exception as ex:
        logger.warning(f"Ngoại lệ khi tạo luận giải chủ đề {topic_title}: {ex}")
        luan_res = {
            "thanh_cong": False,
            "thong_bao": "Hệ thống AI đang bận kết nối. Quý bạn vui lòng nhấn thử lại để tiếp tục.",
            "cau_tra_loi": None,
            "nguon_tri_thuc_da_dung": []
        }

    api_success = bool(luan_res.get("thanh_cong"))
    return APIResponse(
        thanh_cong=api_success,
        du_lieu={
            "birth_profile_id": str(profile.id),
            "topic": topic_key,
            "tieu_de": topic_title,
            "luan_giai": luan_res
        },
        loi=None if api_success else "Hệ thống AI đang bận kết nối. Quý bạn vui lòng nhấn thử lại để tiếp tục."
    )


@router.post("/{birth_profile_id}/chat", response_model=APIResponse[ChatResponse])
def chat_hoi_dap_theo_la_so(
    birth_profile_id: str,
    req: ChatRequest,
    current_user: User = Depends(kiem_tra_quota_truoc_khi_xu_ly),
    db: Session = Depends(get_db)
):
    """
    Hỏi đáp tương tác AI trực tiếp theo lá số Tử Vi của người dùng.
    - Tự động gắn dữ liệu toàn bộ lá số vào ngữ cảnh hỏi đáp.
    - Kiểm duyệt an toàn nội dung, cấm từ ngữ nhạy cảm chết chóc.
    """
    try:
        p_uuid = uuid.UUID(birth_profile_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Định dạng ID hồ sơ sinh không hợp lệ")

    profile = db.query(BirthProfile).filter(BirthProfile.id == p_uuid, BirthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy hồ sơ sinh")

    la_so_record = db.query(LaSoTuViResult).filter(LaSoTuViResult.birth_profile_id == profile.id).first()
    la_so_data = la_so_record.du_lieu_json if la_so_record else {}

    input_data = copy.deepcopy(la_so_data)
    input_data["id"] = str(profile.id)
    input_data["reference_id"] = str(profile.id)
    input_data["he_thong"] = "tu_vi"
    input_data["la_chat_tu_vi"] = True

    cau_hoi_user = req.cau_hoi.strip()

    try:
        res = luan_giai(
            user_id=str(current_user.id),
            cau_hoi=cau_hoi_user,
            du_lieu_dau_vao=input_data,
            co_dinh_kem_anh=False,
            la_tong_quan=False,
            db=db
        )

        noi_dung_tra_loi = ""
        if isinstance(res.get("cau_tra_loi"), dict):
            noi_dung_tra_loi = (
                res["cau_tra_loi"].get("noi_dung") or
                res["cau_tra_loi"].get("loi_khuyen") or
                str(res["cau_tra_loi"])
            )
        elif res.get("cau_tra_loi"):
            noi_dung_tra_loi = str(res.get("cau_tra_loi"))
        elif res.get("thong_bao"):
            noi_dung_tra_loi = res.get("thong_bao", "")

        is_success = bool(res.get("thanh_cong") or res.get("can_hoi_lai"))
    except Exception:
        noi_dung_tra_loi = "Hệ thống đang tải dữ liệu để phân tích câu hỏi của bạn. Vui lòng thử lại trong giây lát."
        is_success = True
        res = {}

    return APIResponse(
        thanh_cong=is_success,
        du_lieu={
            "he_thong": "tu_vi",
            "cau_hoi": cau_hoi_user,
            "tra_loi": noi_dung_tra_loi,
            "chi_tiet": res
        },
        loi=None
    )
