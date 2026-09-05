# -*- coding: utf-8 -*-
"""
Pydantic Schemas phục vụ yêu cầu và phản hồi cho hệ thống xác thực Auth.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class UserRegister(BaseModel):
    """Schema đăng ký tài khoản mới"""
    email: EmailStr = Field(..., description="Email đăng nhập của người dùng")
    password: str = Field(..., min_length=8, description="Mật khẩu tối thiểu 8 ký tự")
    confirm_password: str = Field(..., description="Xác nhận lại mật khẩu")

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Mật khẩu phải có độ dài tối thiểu từ 8 ký tự trở lên")
        return v

    @field_validator("confirm_password")
    @classmethod
    def validate_passwords_match(cls, v: str, info) -> str:
        password = info.data.get("password")
        if password and v != password:
            raise ValueError("Mật khẩu xác nhận không trùng khớp với mật khẩu đã nhập")
        return v


class UserLogin(BaseModel):
    """Schema đăng nhập tài khoản dạng JSON"""
    email: EmailStr = Field(..., description="Email đăng nhập")
    password: str = Field(..., description="Mật khẩu")


class TokenResponse(BaseModel):
    """Schema trả về access token và refresh token sau khi đăng nhập thành công"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Schema yêu cầu cấp mới access token từ refresh token"""
    refresh_token: str = Field(..., description="Refresh token hợp lệ đã được cấp trước đó")


class RefreshTokenResponse(BaseModel):
    """Schema phản hồi access token mới"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema thông tin người dùng (TUYỆT ĐỐI KHÔNG trả password_hash ra ngoài)"""
    id: uuid.UUID
    email: str
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequest(BaseModel):
    """Schema yêu cầu đổi mật khẩu người dùng"""
    mat_khau_cu: str = Field(..., description="Mật khẩu hiện tại")
    mat_khau_moi: str = Field(..., min_length=8, description="Mật khẩu mới tối thiểu 8 ký tự")
    xac_nhan_mat_khau: str = Field(..., description="Xác nhận lại mật khẩu mới")

    @field_validator("mat_khau_moi")
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Mật khẩu mới phải có độ dài tối thiểu từ 8 ký tự trở lên")
        return v

    @field_validator("xac_nhan_mat_khau")
    @classmethod
    def validate_passwords_match(cls, v: str, info) -> str:
        mat_khau_moi = info.data.get("mat_khau_moi")
        if mat_khau_moi and v != mat_khau_moi:
            raise ValueError("Mật khẩu xác nhận không trùng khớp với mật khẩu mới")
        return v


class DeleteAccountRequest(BaseModel):
    """Schema yêu cầu xóa tài khoản với xác nhận email"""
    email: EmailStr = Field(..., description="Gõ lại chính xác email tài khoản để xác nhận xóa vĩnh viễn")
