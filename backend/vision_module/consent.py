# -*- coding: utf-8 -*-
"""
Module Quản Lý Chấp Thuận Người Dùng (User Consent Management)
Xử lý chính sách đồng ý thu thập và xử lý hình ảnh sinh trắc học nhạy cảm (bàn tay, khuôn mặt).
"""

import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from db.models import User
from middleware.data_retention import ghi_audit_log


def kiem_tra_dong_y(user_id: str, db: Session) -> bool:
    """
    Kiểm tra người dùng đã đồng ý điều khoản sử dụng ảnh sinh trắc học hay chưa.
    Trả về True nếu đã đồng ý (da_dong_y_sinh_trac_hoc = True), ngược lại False.
    """
    try:
        uid = uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id
    except ValueError:
        return False

    user = db.query(User).filter(User.id == uid).first()
    if not user:
        return False

    return bool(user.da_dong_y_sinh_trac_hoc)


def ghi_nhan_dong_y(user_id: str, db: Session) -> None:
    """
    Ghi nhận sự đồng ý của người dùng, cập nhật `da_dong_y_sinh_trac_hoc = True`
    và lưu lại timestamp thời điểm đồng ý.
    """
    try:
        uid = uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Định dạng user_id không hợp lệ."
        )

    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại."
        )

    user.da_dong_y_sinh_trac_hoc = True
    user.thoi_gian_dong_y_sinh_trac_hoc = datetime.utcnow()
    db.commit()
    db.refresh(user)

    ghi_audit_log(
        hanh_dong="USER_CONSENT_GRANTED",
        ban_ghi_id="N/A",
        user_id=str(user.id),
        duong_dan="N/A",
        ly_do="Người dùng chủ động đồng ý điều khoản xử lý dữ liệu ảnh sinh trắc học."
    )


def require_biometric_consent(user_id: str, db: Session) -> None:
    """
    Hàm chặn: Nếu user chưa đồng ý, raise HTTPException 403 Forbidden yêu cầu đồng ý trước.
    """
    if not kiem_tra_dong_y(user_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Người dùng chưa đồng ý điều khoản (ch?a ??ng ? ?i?u kho?n) xử lý hình ảnh sinh trắc học. "
                "Vui lòng gọi endpoint POST /vision/consent để đồng ý trước khi tải ảnh."
            )
        )
