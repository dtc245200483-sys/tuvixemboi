# -*- coding: utf-8 -*-
"""
Router Bát Tự Tứ Trụ:
- GET /bat-tu/{birth_profile_id}:
  Kiểm tra đã có TuTruResult chưa; nếu chưa thì gọi astro_engine/bat_tu tính và lưu.
  Sau đó gọi interpretation_api orchestrator luan_giai với he_thong="bat_tu", qua Content Safety & Cache.
  
LỰA CHỌN THIẾT KẾ:
Sử dụng mô hình đồng bộ (synchronous request/response).
"""

import uuid
import copy
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User, BirthProfile, TuTruResult
from api.dependencies import kiem_tra_quota_truoc_khi_xu_ly
from api.schemas import APIResponse, BatTuResponse
from calendar_converter.lunar_calendar import xac_dinh_gio_sinh_theo_canh_gio
from astro_engine.bat_tu import lap_tu_tru
from interpretation_api.orchestrator.main_flow import luan_giai

from datetime import date, datetime

def parse_date_safe(d) -> date:
    """Chuyển đổi an toàn đối tượng date, datetime hoặc chuỗi ISO thành datetime.date"""
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    if isinstance(d, str):
        clean_str = d.split("T")[0].split(" ")[0]
        parts = [int(p) for p in clean_str.split("-")]
        if len(parts) == 3:
            return date(parts[0], parts[1], parts[2])
    raise ValueError(f"Không thể định dạng ngày hợp lệ từ: {d}")


router = APIRouter(prefix="/bat-tu", tags=["Bat Tu"])


@router.get("/{birth_profile_id}", response_model=APIResponse[BatTuResponse])
def xem_bat_tu_tu_tru(
    birth_profile_id: str,
    current_user: User = Depends(kiem_tra_quota_truoc_khi_xu_ly),
    db: Session = Depends(get_db)
):
    """
    Lập Tứ Trụ Bát Tự và luận giải ngũ hành, thân vượng nhược, Dụng Thần.
    - Đã xác thực người dùng và kiểm tra quota hàng ngày.
    - Caching kết quả luận giải tổng quan độc lập với Tử Vi.
    """
    try:
        p_uuid = uuid.UUID(birth_profile_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Định dạng ID hồ sơ sinh không hợp lệ")

    profile = db.query(BirthProfile).filter(BirthProfile.id == p_uuid, BirthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy hồ sơ sinh")

    gioi_tinh = getattr(profile, "gioi_tinh", "nam") or "nam"
    ngay_duong = parse_date_safe(profile.ngay_sinh_duong)

    # 1. Kiểm tra đã có TuTruResult chưa
    tu_tru_record = db.query(TuTruResult).filter(TuTruResult.birth_profile_id == profile.id).first()
    canh_gio = xac_dinh_gio_sinh_theo_canh_gio(profile.gio_sinh, profile.phut_sinh)
    gio_chi = canh_gio["chi_gio"]

    if not tu_tru_record:
        tu_tru_data = lap_tu_tru(
            ngay_duong=ngay_duong.day,
            thang_duong=ngay_duong.month,
            nam_duong=ngay_duong.year,
            gio_chi=gio_chi,
            gioi_tinh=gioi_tinh,
            gio_sinh=profile.gio_sinh,
            phut_sinh=profile.phut_sinh
        )

        tu_tru_record = TuTruResult(
            id=uuid.uuid4(),
            birth_profile_id=profile.id,
            du_lieu_json=tu_tru_data
        )
        db.add(tu_tru_record)
        db.commit()
        db.refresh(tu_tru_record)
    else:
        tu_tru_data = tu_tru_record.du_lieu_json
        vn = tu_tru_data.get("vuong_nhuoc_detail") if isinstance(tu_tru_data, dict) else {}
        can_recompute = (
            not isinstance(tu_tru_data, dict)
            or "vung_bien_4_tru" not in tu_tru_data
            or "chi_tiet_tru" not in tu_tru_data
            or "cach_cuc" not in tu_tru_data
            or not isinstance(vn, dict)
            or not vn.get("bang_chung_the")
            or "cans_tiet_khac" not in vn
        )
        if can_recompute:
            tu_tru_data = lap_tu_tru(
                ngay_duong=ngay_duong.day,
                thang_duong=ngay_duong.month,
                nam_duong=ngay_duong.year,
                gio_chi=gio_chi,
                gioi_tinh=gioi_tinh,
                gio_sinh=profile.gio_sinh,
                phut_sinh=profile.phut_sinh
            )
            tu_tru_record.du_lieu_json = tu_tru_data
            db.commit()
            try:
                from middleware.quota_service import xoa_cache_theo_he_thong
                xoa_cache_theo_he_thong("bat_tu", db=db)
            except Exception:
                pass


    # 2. Luận giải AI
    input_data = copy.deepcopy(tu_tru_data)
    input_data["id"] = str(profile.id)
    input_data["reference_id"] = str(profile.id)
    input_data["he_thong"] = "bat_tu"
    input_data["la_tong_quan"] = True

    luan_giai_res = luan_giai(
        user_id=str(current_user.id),
        cau_hoi="Luận giải tổng quan lá số Bát Tự Tứ Trụ",
        du_lieu_dau_vao=input_data,
        co_dinh_kem_anh=False,
        la_tong_quan=True,
        db=db
    )

    return APIResponse(
        thanh_cong=True,
        du_lieu={
            "birth_profile_id": str(profile.id),
            "tu_tru": tu_tru_data,
            "luan_giai": luan_giai_res
        },
        loi=None
    )
