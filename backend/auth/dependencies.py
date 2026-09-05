# -*- coding: utf-8 -*-
"""
Dependencies cho FastAPI endpoints yêu cầu xác thực người dùng.
"""

import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from auth.security import decode_token

# Khởi tạo OAuth2PasswordBearer với endpoint đăng nhập /auth/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency lấy thông tin User hiện tại từ JWT access token.
    Ném lỗi HTTPException 401 nếu token bị thiếu, hết hạn, không hợp lệ hoặc user bị khóa.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yêu cầu xác thực: Chưa cung cấp Bearer token trong header Authorization",
            headers={"WWW-Authenticate": "Bearer"}
        )

    payload = decode_token(token)

    # Kiểm tra loại token phải là access token
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token cung cấp không phải access token hợp lệ",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không chứa định danh người dùng (sub)",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Định dạng UUID người dùng không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản người dùng không tồn tại trong hệ thống",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản này đã bị vô hiệu hóa hoặc bị khóa",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user
