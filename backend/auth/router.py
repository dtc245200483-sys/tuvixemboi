# -*- coding: utf-8 -*-
"""
Router API cho phân hệ xác thực /auth
- POST /auth/register: Đăng ký tài khoản
- POST /auth/login: Đăng nhập nhận cặp access/refresh token
- POST /auth/refresh: Cấp mới access token từ refresh token
- GET /auth/me: Lấy thông tin user hiện tại (kiểm tra token)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from auth.schemas import (
    UserRegister,
    TokenResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    UserResponse,
    ChangePasswordRequest,
    DeleteAccountRequest
)
from auth.service import register_user, authenticate_user, refresh_access_token
from auth.security import create_access_token, create_refresh_token, verify_password, hash_password
from auth.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Đăng ký tài khoản mới, trả về thông tin User (status 201)"""
    new_user = register_user(db, user_data)
    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    """
    Đăng nhập hệ thống, hỗ trợ linh hoạt cả JSON (từ frontend Axios)
    lẫn form-data (từ OAuth2PasswordRequestForm / Swagger UI).
    """
    content_type = request.headers.get("content-type", "")
    email = None
    password = None

    if "application/json" in content_type:
        try:
            body = await request.json()
            email = body.get("email") or body.get("username")
            password = body.get("password")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dữ liệu JSON gửi lên không đúng định dạng"
            )
    else:
        # Form data (x-www-form-urlencoded hoặc multipart/form-data)
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng cung cấp đầy đủ email và mật khẩu"
        )

    # Xác thực người dùng
    user = authenticate_user(db, str(email).strip(), str(password))
    if not user:
        # Bảo mật: Thông báo lỗi chung chung, KHÔNG tiết lộ email có tồn tại hay không
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản này đã bị khóa hoặc chưa kích hoạt",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Sinh cặp Access Token & Refresh Token
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Nhận refresh token và cấp access token mới"""
    new_access_token = refresh_access_token(payload.refresh_token, db)
    return RefreshTokenResponse(
        access_token=new_access_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Lấy thông tin tài khoản đang đăng nhập hiện tại từ Bearer token"""
    return current_user


@router.put("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Đổi mật khẩu tài khoản người dùng:
    - Xác thực mật khẩu cũ.
    - Cập nhật mật khẩu mới (hash bcrypt).
    """
    if not verify_password(payload.mat_khau_cu, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không chính xác"
        )

    if payload.mat_khau_cu == payload.mat_khau_moi:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới không được trùng với mật khẩu hiện tại"
        )

    current_user.password_hash = hash_password(payload.mat_khau_moi)
    db.commit()

    return {
        "thanh_cong": True,
        "thong_bao": "Đổi mật khẩu thành công",
        "du_lieu": {"message": "Đổi mật khẩu thành công"}
    }


@router.delete("/me")
def delete_account(
    payload: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Xóa vĩnh viễn tài khoản người dùng:
    - Yêu cầu xác nhận email chính chủ.
    - Xóa CASCADE toàn bộ dữ liệu nghiệp vụ (hồ sơ, quẻ, chat, quota).
    - Xóa sạch tệp ảnh sinh trắc học vật lý trên disk qua SQLAlchemy before_delete hook.
    """
    if payload.email.strip().lower() != current_user.email.strip().lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Địa chỉ email xác nhận không trùng khớp với tài khoản hiện tại"
        )

    user_id_str = str(current_user.id)
    user_email = current_user.email

    db.delete(current_user)
    db.commit()

    return {
        "thanh_cong": True,
        "thong_bao": f"Tài khoản {user_email} và toàn bộ dữ liệu liên quan đã được xóa vĩnh viễn.",
        "du_lieu": {"user_id": user_id_str, "status": "deleted"}
    }
