# -*- coding: utf-8 -*-
"""
API Dependencies cho toàn bộ route hệ thống:
- kiem_tra_quota_truoc_khi_xu_ly: Dependency chặn trước khi vào logic AI nếu hết quota.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from auth.dependencies import get_current_user
from middleware.quota_service import lay_thong_tin_quota


def kiem_tra_quota_truoc_khi_xu_ly(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency dùng chung cho mọi route cần gọi AI (tu_vi, bat_tu, kinh_dich, nhan_tuong, chat).
    Kiểm tra hạn mức quota của user TRƯỚC KHI thực hiện bất kỳ tính toán hay gọi AI nào.
    Raise HTTPException 429 nếu đã hết quota hôm nay.
    """
    info = lay_thong_tin_quota(user_id=str(current_user.id), db=db)
    if not info.get("con_han_muc", True):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Bạn đã dùng hết lượt hỏi hôm nay, vui lòng quay lại vào ngày mai"
        )
    return current_user
