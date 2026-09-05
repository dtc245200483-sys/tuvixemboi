# -*- coding: utf-8 -*-
"""
Router Hạn Mức Sử Dụng (Usage Quota):
- GET /quota: Trả về thông tin hạn mức lượt gọi AI trong ngày của người dùng.
"""

from fastapi import APIRouter, Depends
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
    """
    info = lay_thong_tin_quota(user_id=str(current_user.id), db=db)
    return APIResponse(
        thanh_cong=True,
        du_lieu=QuotaResponse(
            so_luot_da_dung=info.get("so_luot_da_dung", 0),
            so_luot_con_lai=info.get("so_luot_con_lai", 0),
            gioi_han_ngay=info.get("gioi_han_ngay", 50),
            con_han_muc=info.get("con_han_muc", True)
        ),
        loi=None
    )
