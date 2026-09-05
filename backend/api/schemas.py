# -*- coding: utf-8 -*-
"""
Pydantic Schemas cho API Orchestration Layer (backend/api/):
- APIResponse: Chuẩn hóa envelope pattern {thanh_cong, du_lieu, loi} cho toàn bộ endpoint.
- Schemas cho BirthProfile, TuVi, BatTu, KinhDich, NhanTuong, Chat, Quota.
"""

from typing import Optional, Any, Generic, TypeVar, List, Dict
from datetime import date, datetime
import uuid
from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")


# ==============================================================================
# 1. RESPONSE ENVELOPE CHUẨN TOÀN HỆ THỐNG
# ==============================================================================
class APIResponse(BaseModel, Generic[T]):
    """
    Định dạng chuẩn của mọi response trả về cho Frontend:
    - thanh_cong: True nếu thành công, False nếu có lỗi.
    - du_lieu: Dữ liệu thực tế khi thành công, None khi lỗi.
    - loi: Thông báo lỗi thân thiện khi thất bại, None khi thành công.
    """
    thanh_cong: bool = Field(..., description="Trạng thái thành công hay thất bại")
    du_lieu: Optional[T] = Field(default=None, description="Dữ liệu phản hồi khi thành công")
    loi: Optional[str] = Field(default=None, description="Mô tả lỗi khi thất bại")


# ==============================================================================
# 2. BIRTH PROFILE SCHEMAS
# ==============================================================================
class BirthProfileCreateRequest(BaseModel):
    ho_ten: Optional[str] = Field(None, max_length=255, description="Họ và tên người xem")
    ngay_sinh_duong: date = Field(..., description="Ngày sinh Dương lịch (YYYY-MM-DD)")
    gio_sinh: int = Field(..., ge=0, le=23, description="Giờ sinh Dương lịch (0-23)")
    phut_sinh: int = Field(0, ge=0, le=59, description="Phút sinh Dương lịch (0-59)")
    gioi_tinh: str = Field(..., pattern="^(nam|nu)$", description="Giới tính: nam hoặc nu")

    @field_validator("ngay_sinh_duong")
    @classmethod
    def validate_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Ngày sinh không được ở tương lai")
        return v


class BirthProfileUpdateRequest(BaseModel):
    ho_ten: Optional[str] = Field(None, max_length=255, description="Họ và tên người xem")
    ngay_sinh_duong: Optional[date] = Field(None, description="Ngày sinh Dương lịch (YYYY-MM-DD)")
    gio_sinh: Optional[int] = Field(None, ge=0, le=23, description="Giờ sinh Dương lịch (0-23)")
    phut_sinh: Optional[int] = Field(None, ge=0, le=59, description="Phút sinh Dương lịch (0-59)")
    gioi_tinh: Optional[str] = Field(None, pattern="^(nam|nu)$", description="Giới tính: nam hoặc nu")


class BirthProfileResponse(BaseModel):
    id: str
    user_id: str
    ho_ten: Optional[str] = None
    ngay_sinh_duong: date
    gio_sinh: int
    phut_sinh: int
    gioi_tinh: str
    ngay_sinh_am: Optional[date] = None
    thong_tin_am_lich: Optional[Dict[str, Any]] = None
    created_at: datetime


# ==============================================================================
# 3. TỬ VI SCHEMAS
# ==============================================================================
class TuViResponse(BaseModel):
    birth_profile_id: str
    la_so: Dict[str, Any]
    luan_giai: Optional[Dict[str, Any]] = None


# ==============================================================================
# 4. BÁT TỰ SCHEMAS
# ==============================================================================
class BatTuResponse(BaseModel):
    birth_profile_id: str
    tu_tru: Dict[str, Any]
    luan_giai: Optional[Dict[str, Any]] = None


# ==============================================================================
# 5. KINH DỊCH SCHEMAS
# ==============================================================================
class GieoQueRequest(BaseModel):
    cau_hoi: str = Field(..., min_length=2, description="Câu hỏi hoặc tâm nguyện khi gieo quẻ")
    phuong_phap: str = Field("dong_xu", pattern="^(dong_xu|thoi_gian)$", description="Phương pháp: dong_xu hoặc thoi_gian")
    seed: Optional[int] = Field(None, description="Seed ngẫu nhiên (tùy chọn)")


class GieoQueResponse(BaseModel):
    id: str
    cau_hoi: str
    ma_que_chinh: str
    ma_que_bien: Optional[str] = None
    hao_dong: Optional[List[int]] = None
    chi_tiet_que: Dict[str, Any]
    luan_giai: Optional[Dict[str, Any]] = None


# ==============================================================================
# 6. NHÂN TƯỚNG SCHEMAS
# ==============================================================================
class NhanTuongResponse(BaseModel):
    id: str
    loai_anh: str
    dac_diem_quan_sat: Optional[Dict[str, Any]] = None
    luan_giai: Optional[Dict[str, Any]] = None


# ==============================================================================
# 7. CHAT SCHEMAS
# ==============================================================================
class ChatRequest(BaseModel):
    cau_hoi: str = Field(..., min_length=1, description="Nội dung câu hỏi gửi tới trợ lý phong thủy")
    reference_id: Optional[str] = Field(None, description="ID lá số/quẻ/ảnh liên quan nếu có")
    he_thong: Optional[str] = Field(None, pattern="^(tu_vi|kinh_dich|bat_tu|nhan_tuong)$", description="Hệ thống cụ thể nếu muốn chỉ định")


class ChatResponse(BaseModel):
    he_thong: Optional[str] = None
    cau_hoi: str
    tra_loi: str
    chi_tiet: Optional[Dict[str, Any]] = None


class ChatHistoryItem(BaseModel):
    id: str
    he_thong: str
    reference_id: Optional[str] = None
    cau_hoi: str
    tra_loi: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    tong_so: int
    trang: int
    kich_thuoc_trang: int
    danh_sach: List[ChatHistoryItem]


# ==============================================================================
# 8. QUOTA SCHEMAS
# ==============================================================================
class QuotaResponse(BaseModel):
    so_luot_da_dung: int
    so_luot_con_lai: int
    gioi_han_ngay: int
    con_han_muc: bool
