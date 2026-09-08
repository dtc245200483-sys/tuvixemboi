# -*- coding: utf-8 -*-
"""
Router Hạn Mức Sử Dụng (Usage Quota):
- GET /quota: Trả về thông tin hạn mức lượt gọi AI trong ngày của người dùng.
"""

import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User
from auth.dependencies import get_current_user
from middleware.quota_service import lay_thong_tin_quota
from api.schemas import APIResponse, QuotaResponse

router = APIRouter(prefix="/quota", tags=["Quota"])


@router.get("", response_model=APIResponse[QuotaResponse])
def tra_cuu_quota_nguoi_dung(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tra cứu thông tin hạn mức sử dụng AI trong ngày của người dùng hiện tại:
    - so_luot_da_dung: Số lượt đã gọi trong ngày
    - so_luot_con_lai: Số lượt còn lại có thể gọi
    - gioi_han_ngay: Hạn mức tối đa trong ngày
    - con_han_muc: True nếu còn lượt gọi, False nếu đã hết
    - is_premium: True nếu là tài khoản VIP Premium
    - so_giay_con_lai_den_reset: Số giây đếm ngược đến 00:00 ngày mai
    - thoi_gian_reset: Thời điểm hồi lại hạn mức
    """
    info = lay_thong_tin_quota(user_id=str(current_user.id), db=db)
    return APIResponse(
        thanh_cong=True,
        du_lieu=QuotaResponse(
            so_luot_da_dung=info.get("so_luot_da_dung", 0),
            so_luot_con_lai=info.get("so_luot_con_lai", 0),
            gioi_han_ngay=info.get("gioi_han_ngay", 50),
            con_han_muc=info.get("con_han_muc", True),
            is_premium=info.get("is_premium", False),
            so_giay_con_lai_den_reset=info.get("so_giay_con_lai_den_reset"),
            thoi_gian_reset=info.get("thoi_gian_reset")
        ),
        loi=None
    )


@router.post("/upgrade-premium", response_model=APIResponse[dict])
def nang_cap_tai_khoan_premium(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Nâng cấp tài khoản người dùng lên gói Premium VIP:
    - Không giới hạn số lần An Sao Lập Lá Số
    - Không giới hạn hỏi đáp Trợ lý AI
    - Thời hạn 1 năm
    """
    current_user.is_premium = True
    current_user.premium_expires_at = datetime.utcnow() + timedelta(days=365)
    db.commit()
    db.refresh(current_user)

    return APIResponse(
        thanh_cong=True,
        du_lieu={
            "thong_bao": "Chúc mừng! Bạn đã kích hoạt thành công gói Premium VIP. Giờ đây bạn có thể An Sao Lập Lá Số và sử dụng trợ lý AI không giới hạn.",
            "is_premium": True,
            "premium_expires_at": current_user.premium_expires_at.isoformat() if current_user.premium_expires_at else None
        },
        loi=None
    )

