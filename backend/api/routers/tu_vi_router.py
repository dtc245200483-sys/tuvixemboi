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
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User, BirthProfile, LaSoTuViResult
from api.dependencies import kiem_tra_quota_truoc_khi_xu_ly
from api.schemas import APIResponse, TuViResponse
from calendar_converter.lunar_calendar import solar_to_lunar, xac_dinh_gio_sinh_theo_canh_gio
from astro_engine.tu_vi import lap_la_so, xac_dinh_cuc, CAN_LIST, CUNG_DIA_CHI
from interpretation_api.orchestrator.main_flow import luan_giai

router = APIRouter(prefix="/tu-vi", tags=["Tu Vi"])


@router.get("/{birth_profile_id}", response_model=APIResponse[TuViResponse])
def xem_la_so_tu_vi(
    birth_profile_id: str,
    current_user: User = Depends(kiem_tra_quota_truoc_khi_xu_ly),
    db: Session = Depends(get_db)
):
    """
    Lấy hoặc an lá số Tử Vi và luận giải tổng quan trọn đời.
    - Đã xác thực người dùng và kiểm tra quota hàng ngày.
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
    
    # Kiểm tra tính toàn vẹn và đúng đắn của thứ tự 12 cung chức năng và Cục số
    is_cung_valid = False
    if la_so_record and la_so_record.du_lieu_json:
        cung_menh_p = la_so_record.du_lieu_json.get("cung_menh_vi_tri")
        cac_cung_list = la_so_record.du_lieu_json.get("cac_cung", [])
        cuc_saved = la_so_record.du_lieu_json.get("cuc", {}).get("ten")

        can_nam = CAN_LIST[(nam_am + 6) % 10]
        chi_nam = CUNG_DIA_CHI[(nam_am + 8) % 12]
        cuc_chuan = xac_dinh_cuc(f"{can_nam} {chi_nam}", cung_menh_p if cung_menh_p is not None else 0).get("ten")

        if cung_menh_p is not None and len(cac_cung_list) == 12 and cuc_saved == cuc_chuan:
            cung_map = {c.get("vi_tri_dia_chi"): c.get("ten_cung_chuc_nang") for c in cac_cung_list}
            huynh_de_pos = (cung_menh_p - 1) % 12
            if cung_map.get(huynh_de_pos) == "Huynh Đệ":
                is_cung_valid = True

    can_tinh_lai = (
        not la_so_record or 
        not la_so_record.du_lieu_json or 
        not is_cung_valid or
        "cung_than_vi_tri" not in la_so_record.du_lieu_json or
        "than_cu" not in la_so_record.du_lieu_json or
        "chinh_tinh" not in la_so_record.du_lieu_json.get("cac_cung", [{}])[0] or
        len(la_so_record.du_lieu_json.get("cac_cung", [{}])[0].get("danh_sach_sao", [])) < 3
    )

    if can_tinh_lai:
        la_so_data = lap_la_so(
            ngay_sinh_am=ngay_am,
            thang_sinh_am=thang_am,
            nam_sinh_am=nam_am,
            gio_sinh_chi=gio_chi,
            gioi_tinh=profile.gioi_tinh
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

    # 2. Điều phối luận giải AI (tổng quan)
    input_data = copy.deepcopy(la_so_data)
    input_data["id"] = str(profile.id)
    input_data["reference_id"] = str(profile.id)
    input_data["he_thong"] = "tu_vi"
    input_data["la_tong_quan"] = True

    luan_giai_res = luan_giai(
        user_id=str(current_user.id),
        cau_hoi="Luận giải tổng quan lá số Tử Vi trọn đời",
        du_lieu_dau_vao=input_data,
        co_dinh_kem_anh=False,
        la_tong_quan=True,
        db=db
    )

    return APIResponse(
        thanh_cong=True,
        du_lieu={
            "birth_profile_id": str(profile.id),
            "la_so": la_so_data,
            "luan_giai": luan_giai_res
        },
        loi=None
    )
