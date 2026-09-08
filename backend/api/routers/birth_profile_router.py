# -*- coding: utf-8 -*-
"""
Router quản lý hồ sơ ngày giờ sinh (Birth Profile):
- POST /birth-profile: Tạo hồ sơ mới, tự động tính ngày âm qua calendar_converter
- GET /birth-profile: Danh sách hồ sơ của user hiện tại
- GET /birth-profile/{id}: Chi tiết hồ sơ của user hiện tại
- PUT /birth-profile/{id}: Cập nhật hồ sơ
- DELETE /birth-profile/{id}: Xóa hồ sơ
"""

import uuid
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User, BirthProfile
from auth.dependencies import get_current_user
from calendar_converter.lunar_calendar import solar_to_lunar
from middleware.quota_service import kiem_tra_va_tang_quota
from api.schemas import (
    APIResponse,
    BirthProfileCreateRequest,
    BirthProfileUpdateRequest,
    BirthProfileResponse
)

router = APIRouter(prefix="/birth-profile", tags=["Birth Profile"])


def _to_response_data(profile: BirthProfile) -> dict:
    lunar_info = None
    if profile.ngay_sinh_duong:
        try:
            lunar_info = solar_to_lunar(
                profile.ngay_sinh_duong.day,
                profile.ngay_sinh_duong.month,
                profile.ngay_sinh_duong.year,
                gio=profile.gio_sinh if profile.gio_sinh is not None else 12
            )
            if lunar_info:
                can_n = lunar_info.get('can_nam', '')
                chi_n = lunar_info.get('chi_nam', '')
                can_t = lunar_info.get('can_thang', '')
                chi_t = lunar_info.get('chi_thang', '')
                can_ng = lunar_info.get('can_ngay', '')
                chi_ng = lunar_info.get('chi_ngay', '')
                ten_g = lunar_info.get('ten_gio', '')
                lunar_info['can_chi_nam'] = f"{can_n} {chi_n}".strip()
                lunar_info['can_chi_thang'] = f"{can_t} {chi_t}".strip()
                lunar_info['can_chi_ngay'] = f"{can_ng} {chi_ng}".strip()
                lunar_info['can_chi_gio'] = f"Giờ {ten_g}".strip()
        except Exception:
            pass

    return {
        "id": str(profile.id),
        "user_id": str(profile.user_id),
        "ho_ten": profile.ho_ten,
        "ngay_sinh_duong": profile.ngay_sinh_duong,
        "gio_sinh": profile.gio_sinh,
        "phut_sinh": profile.phut_sinh,
        "gioi_tinh": profile.gioi_tinh,
        "ngay_sinh_am": profile.ngay_sinh_am,
        "thong_tin_am_lich": lunar_info,
        "is_default": getattr(profile, "is_default", False),
        "is_quick_chart": getattr(profile, "is_quick_chart", False),
        "created_at": profile.created_at
    }


@router.post("", response_model=APIResponse[BirthProfileResponse], status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=APIResponse[BirthProfileResponse], status_code=status.HTTP_201_CREATED, include_in_schema=False)
def tao_ho_so_sinh(
    req: BirthProfileCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo hồ sơ sinh mới cho người dùng.
    Tự động tính ngày âm lịch và can chi năm/tháng/ngày/giờ thông qua calendar_converter.
    Hồ sơ đầu tiên của người dùng sẽ được tự động chọn làm hồ sơ mặc định.
    """
    try:
        lunar_data = solar_to_lunar(req.ngay_sinh_duong.day, req.ngay_sinh_duong.month, req.ngay_sinh_duong.year)
        ngay_am = date(lunar_data["nam_am"], lunar_data["thang_am"], lunar_data["ngay_am"])
    except Exception:
        ngay_am = None

    has_existing = db.query(BirthProfile.id).filter(BirthProfile.user_id == current_user.id).first() is not None
    is_default = not has_existing

    profile = BirthProfile(
        id=uuid.uuid4(),
        user_id=current_user.id,
        ho_ten=req.ho_ten.strip(),
        ngay_sinh_duong=req.ngay_sinh_duong,
        gio_sinh=req.gio_sinh,
        phut_sinh=req.phut_sinh,
        gioi_tinh=req.gioi_tinh,
        ngay_sinh_am=ngay_am,
        is_default=is_default,
        is_quick_chart=False
    )

    db.add(profile)
    if is_default:
        current_user.default_birth_profile_id = profile.id
    db.commit()
    db.refresh(profile)

    return APIResponse(
        thanh_cong=True,
        du_lieu=_to_response_data(profile),
        loi=None
    )


@router.post("/an-sao", response_model=APIResponse[BirthProfileResponse], status_code=status.HTTP_201_CREATED)
def an_sao_lap_la_so(
    req: BirthProfileCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Thực hiện An Sao Lập Lá Số từ thanh nhập nhanh:
    - Khấu trừ 1 lượt sử dụng hôm nay (đối với tài khoản Free), chặn nếu hết lượt.
    - Lưu hồ sơ với is_quick_chart=True, is_default=False (KHÔNG làm đổi Hồ Sơ Mệnh Đang Chọn).
    """
    quota_res = kiem_tra_va_tang_quota(user_id=current_user.id, db=db)
    if not quota_res.get("con_han_muc", True):
        msg = quota_res.get("thong_bao") or "Bạn đã dùng hết 50 lượt an sao hôm nay. Vui lòng đợi đến ngày mai hoặc nâng cấp Premium để tiếp tục."
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=msg
        )

    try:
        lunar_data = solar_to_lunar(req.ngay_sinh_duong.day, req.ngay_sinh_duong.month, req.ngay_sinh_duong.year)
        ngay_am = date(lunar_data["nam_am"], lunar_data["thang_am"], lunar_data["ngay_am"])
    except Exception:
        ngay_am = None

    profile = BirthProfile(
        id=uuid.uuid4(),
        user_id=current_user.id,
        ho_ten=req.ho_ten.strip(),
        ngay_sinh_duong=req.ngay_sinh_duong,
        gio_sinh=req.gio_sinh,
        phut_sinh=req.phut_sinh,
        gioi_tinh=req.gioi_tinh,
        ngay_sinh_am=ngay_am,
        is_default=False,
        is_quick_chart=True
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return APIResponse(
        thanh_cong=True,
        du_lieu=_to_response_data(profile),
        loi=None
    )


@router.put("/{profile_id}/set-default", response_model=APIResponse[BirthProfileResponse])
def dat_ho_so_menh_mac_dinh(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Đặt hồ sơ chỉ định làm Hồ Sơ Mệnh Đang Chọn (Mặc định)"""
    try:
        p_uuid = uuid.UUID(profile_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Định dạng ID không hợp lệ")

    target_profile = db.query(BirthProfile).filter(
        BirthProfile.id == p_uuid,
        BirthProfile.user_id == current_user.id
    ).first()
    if not target_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy hồ sơ sinh")

    # Bỏ cờ is_default của các hồ sơ khác của user này
    db.query(BirthProfile).filter(
        BirthProfile.user_id == current_user.id
    ).update({BirthProfile.is_default: False}, synchronize_session=False)

    target_profile.is_default = True
    current_user.default_birth_profile_id = target_profile.id

    db.commit()
    db.refresh(target_profile)

    return APIResponse(
        thanh_cong=True,
        du_lieu=_to_response_data(target_profile),
        loi=None
    )


@router.get("", response_model=APIResponse[List[BirthProfileResponse]])
@router.get("/", response_model=APIResponse[List[BirthProfileResponse]], include_in_schema=False)
def danh_sach_ho_so_sinh(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Liệt kê danh sách hồ sơ sinh của người dùng hiện tại, ưu tiên hồ sơ mặc định lên đầu"""
    profiles = (
        db.query(BirthProfile)
        .filter(BirthProfile.user_id == current_user.id)
        .order_by(BirthProfile.is_default.desc(), BirthProfile.created_at.desc())
        .all()
    )
    data = [_to_response_data(p) for p in profiles]
    return APIResponse(thanh_cong=True, du_lieu=data, loi=None)


@router.get("/{profile_id}", response_model=APIResponse[BirthProfileResponse])
def chi_tiet_ho_so_sinh(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xem chi tiết hồ sơ sinh theo ID"""
    try:
        p_uuid = uuid.UUID(profile_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Định dạng ID không hợp lệ")

    profile = db.query(BirthProfile).filter(BirthProfile.id == p_uuid, BirthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy hồ sơ sinh")

    return APIResponse(thanh_cong=True, du_lieu=_to_response_data(profile), loi=None)


@router.put("/{profile_id}", response_model=APIResponse[BirthProfileResponse])
def cap_nhat_ho_so_sinh(
    profile_id: str,
    req: BirthProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin hồ sơ sinh"""
    try:
        p_uuid = uuid.UUID(profile_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Định dạng ID không hợp lệ")

    profile = db.query(BirthProfile).filter(BirthProfile.id == p_uuid, BirthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy hồ sơ sinh")

    if req.ho_ten is not None:
        profile.ho_ten = req.ho_ten
    if req.gio_sinh is not None:
        profile.gio_sinh = req.gio_sinh
    if req.phut_sinh is not None:
        profile.phut_sinh = req.phut_sinh
    if req.gioi_tinh is not None:
        profile.gioi_tinh = req.gioi_tinh

    if req.ngay_sinh_duong is not None:
        profile.ngay_sinh_duong = req.ngay_sinh_duong
        try:
            lunar_data = solar_to_lunar(req.ngay_sinh_duong.day, req.ngay_sinh_duong.month, req.ngay_sinh_duong.year)
            profile.ngay_sinh_am = date(lunar_data["nam_am"], lunar_data["thang_am"], lunar_data["ngay_am"])
        except Exception:
            pass

    db.commit()
    db.refresh(profile)
    return APIResponse(thanh_cong=True, du_lieu=_to_response_data(profile), loi=None)


@router.delete("/{profile_id}", response_model=APIResponse[dict])
def xoa_ho_so_sinh(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xóa hồ sơ sinh (tự động xóa lá số và tứ trụ liên kết qua CASCADE)"""
    try:
        p_uuid = uuid.UUID(profile_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Định dạng ID không hợp lệ")

    profile = db.query(BirthProfile).filter(BirthProfile.id == p_uuid, BirthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy hồ sơ sinh")

    db.delete(profile)
    db.commit()
    return APIResponse(thanh_cong=True, du_lieu={"thong_bao": "Đã xóa hồ sơ sinh thành công", "id": profile_id}, loi=None)
