# -*- coding: utf-8 -*-
"""
Tầng nghiệp vụ (Service layer) xử lý đăng ký, xác thực và làm mới token.
"""

import uuid
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from db.models import User
from auth.schemas import UserRegister
from auth.security import hash_password, verify_password, create_access_token, decode_token


def register_user(db: Session, user_data: UserRegister) -> User:
    """Kiểm tra email trùng, hash password và tạo bản ghi User mới"""
    # 1. Kiểm tra email đã tồn tại trong hệ thống chưa
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email này đã được đăng ký trong hệ thống, vui lòng chọn email khác hoặc đăng nhập"
        )

    # 2. Hash password và tạo User
    hashed = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Tìm user theo email và xác thực mật khẩu, trả về User hoặc None"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def refresh_access_token(refresh_token: str, db: Session) -> str:
    """Giải mã refresh token, kiểm tra tính hợp lệ và cấp access token mới"""
    payload = decode_token(refresh_token)

    # Đảm bảo token gửi lên đúng là loại refresh
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token gửi lên không phải refresh token hợp lệ",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token thiếu định danh người dùng (sub)",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Định dạng UUID người dùng trong token không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Kiểm tra user còn tồn tại và active trong Database không
    user = db.query(User).filter(User.id == user_uuid).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại hoặc đã bị khóa",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Tạo Access token mới
    new_access_token = create_access_token({
        "sub": str(user.id),
        "email": user.email
    })
    return new_access_token
