# -*- coding: utf-8 -*-
"""
Định nghĩa đầy đủ 8 SQLAlchemy Models cho toàn bộ 4 hệ thống huyền học:
1. User (Tài khoản người dùng)
2. BirthProfile (Hồ sơ sinh Dương lịch & Âm lịch)
3. LaSoTuViResult (Kết quả an sao Tử Vi 12 cung)
4. TuTruResult (Kết quả phân tích Tứ Trụ / Bát Tự & Dụng Thần)
5. QueKinhDichResult (Kết quả gieo quẻ Kinh Dịch, biến quẻ, hào động)
6. TuongAnhResult (Kết quả phân tích nhân tướng học xem tay/mặt từ ảnh)
7. ChatHistory (Lịch sử hội thoại luận giải theo từng hệ thống)
8. UsageQuota (Quản lý hạn mức sử dụng AI hàng ngày)
"""

import os
import uuid
from datetime import datetime, date
from sqlalchemy import (
    event,
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Date,
    Text,
    Enum,
    JSON,
    ForeignKey,
    UniqueConstraint,
    Uuid
)
from sqlalchemy.orm import relationship
from db.database import Base


# ==============================================================================
# 1. USER MODEL
# ==============================================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    da_dong_y_sinh_trac_hoc = Column(Boolean, default=False, nullable=False)
    thoi_gian_dong_y_sinh_trac_hoc = Column(DateTime(timezone=True), nullable=True)

    # Quan hệ 1-N với các bảng nghiệp vụ (Cascade Delete khi xóa tài khoản User)
    birth_profiles = relationship("BirthProfile", back_populates="user", cascade="all, delete-orphan")
    que_kinh_dich_results = relationship("QueKinhDichResult", back_populates="user", cascade="all, delete-orphan")
    tuong_anh_results = relationship("TuongAnhResult", back_populates="user", cascade="all, delete-orphan")
    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    usage_quotas = relationship("UsageQuota", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} is_active={self.is_active}>"


# ==============================================================================
# 2. BIRTH PROFILE MODEL
# ==============================================================================
class BirthProfile(Base):
    __tablename__ = "birth_profiles"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ho_ten = Column(String(255), nullable=True)
    ngay_sinh_duong = Column(Date, nullable=False)
    gio_sinh = Column(Integer, nullable=False)  # 0-23
    phut_sinh = Column(Integer, default=0, nullable=False)  # 0-59
    gioi_tinh = Column(Enum("nam", "nu", name="gioi_tinh_enum"), nullable=False)
    ngay_sinh_am = Column(Date, nullable=True)  # Tính từ calendar_converter để cache
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Quan hệ
    user = relationship("User", back_populates="birth_profiles")
    la_so_tu_vi = relationship("LaSoTuViResult", back_populates="birth_profile", uselist=False, cascade="all, delete-orphan")
    tu_tru = relationship("TuTruResult", back_populates="birth_profile", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<BirthProfile id={self.id} user_id={self.user_id} ho_ten={self.ho_ten} ngay_sinh_duong={self.ngay_sinh_duong}>"


# ==============================================================================
# 3. LA SO TU VI RESULT MODEL
# ==============================================================================
class LaSoTuViResult(Base):
    __tablename__ = "la_so_tu_vi_results"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    birth_profile_id = Column(Uuid(as_uuid=True), ForeignKey("birth_profiles.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    du_lieu_json = Column(JSON, nullable=False)  # Toàn bộ dữ liệu 12 cung, chính tinh, phụ tinh, cục, mệnh
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Quan hệ 1-1 với BirthProfile
    birth_profile = relationship("BirthProfile", back_populates="la_so_tu_vi")

    def __repr__(self) -> str:
        return f"<LaSoTuViResult id={self.id} birth_profile_id={self.birth_profile_id}>"


# ==============================================================================
# 4. TU TRU RESULT MODEL
# ==============================================================================
class TuTruResult(Base):
    __tablename__ = "tu_tru_results"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    birth_profile_id = Column(Uuid(as_uuid=True), ForeignKey("birth_profiles.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    du_lieu_json = Column(JSON, nullable=False)  # Lưu trữ 8 chữ Bát Tự (Can-Chi 4 trụ), ngũ hành sinh khắc, Dụng Thần
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Quan hệ 1-1 với BirthProfile
    birth_profile = relationship("BirthProfile", back_populates="tu_tru")

    def __repr__(self) -> str:
        return f"<TuTruResult id={self.id} birth_profile_id={self.birth_profile_id}>"


# ==============================================================================
# 5. QUE KINH DICH RESULT MODEL
# ==============================================================================
class QueKinhDichResult(Base):
    __tablename__ = "que_kinh_dich_results"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    cau_hoi = Column(Text, nullable=True)
    ma_que_chinh = Column(String(50), nullable=False)  # Tên hoặc mã quẻ chính (VD: CÀN, KHÔN, TRUÂN...)
    ma_que_bien = Column(String(50), nullable=True)    # Mã quẻ biến (nếu có hào động)
    hao_dong = Column(JSON, nullable=True)             # Danh sách vị trí các hào động (VD: [1, 5])
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="que_kinh_dich_results")

    def __repr__(self) -> str:
        return f"<QueKinhDichResult id={self.id} user_id={self.user_id} ma_que_chinh={self.ma_que_chinh} ma_que_bien={self.ma_que_bien}>"


# ==============================================================================
# 6. TUONG ANH RESULT MODEL
# ==============================================================================
class TuongAnhResult(Base):
    """
    Lưu trữ kết quả phân tích nhân tướng học (chỉ tay hoặc khuôn mặt) từ hình ảnh.

    LƯU Ý VỀ BẢO MẬT & XÓA DỮ LIỆU SINH TRẮC HỌC:
    - ondelete="CASCADE" tại ForeignKey đảm bảo khi User bị xóa, bản ghi metadata trong DB tự động xóa.
    - ĐẶC BIỆT: Việc xóa tệp tin vật lý lưu tại `duong_dan_anh` (trên disk/S3) BẮT BUỘC phải được
      thực hiện ở tầng Service (Application logic), do cơ chế CASCADE thuần của Database không thể can thiệp hệ thống tệp.
    - Cột `ngay_het_han_luu_tru` được kiểm tra định kỳ bởi Background Worker để tự động xóa vĩnh viễn file ảnh nhạy cảm.
    """
    __tablename__ = "tuong_anh_results"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    loai_anh = Column(Enum("tay", "mat", name="loai_anh_enum"), nullable=False)
    duong_dan_anh = Column(String(500), nullable=False)  # Đường dẫn tệp ảnh đã mã hóa
    dac_diem_quan_sat_json = Column(JSON, nullable=True)  # Kết quả bóc tách từ vision_module
    da_duoc_xoa = Column(Boolean, default=False, nullable=False)
    ngay_het_han_luu_tru = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="tuong_anh_results")

    def __repr__(self) -> str:
        return f"<TuongAnhResult id={self.id} user_id={self.user_id} loai_anh={self.loai_anh} da_duoc_xoa={self.da_duoc_xoa}>"


# ==============================================================================
# 7. CHAT HISTORY MODEL
# ==============================================================================
class ChatHistory(Base):
    __tablename__ = "chat_histories"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    he_thong = Column(Enum("tu_vi", "kinh_dich", "bat_tu", "nhan_tuong", name="he_thong_enum"), nullable=False, index=True)
    reference_id = Column(Uuid(as_uuid=True), nullable=True, index=True)  # Trỏ tới ID của lá số/quẻ/tướng ảnh tương ứng
    cau_hoi = Column(Text, nullable=False)
    tra_loi = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="chat_histories")

    def __repr__(self) -> str:
        return f"<ChatHistory id={self.id} user_id={self.user_id} he_thong={self.he_thong} ref={self.reference_id}>"


# ==============================================================================
# 8. USAGE QUOTA MODEL
# ==============================================================================
class UsageQuota(Base):
    __tablename__ = "usage_quotas"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ngay = Column(Date, nullable=False, index=True)
    so_luot_da_dung = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Mỗi user mỗi ngày chỉ có duy nhất 1 bản ghi hạn mức
    __table_args__ = (
        UniqueConstraint("user_id", "ngay", name="uq_user_daily_quota"),
    )

    user = relationship("User", back_populates="usage_quotas")

    def __repr__(self) -> str:
        return f"<UsageQuota id={self.id} user_id={self.user_id} ngay={self.ngay} so_luot={self.so_luot_da_dung}>"

@event.listens_for(User, "before_delete")
def delete_all_user_images_on_user_delete(mapper, connection, target):
    for r in getattr(target, "tuong_anh_results", []):
        if r.duong_dan_anh and os.path.exists(r.duong_dan_anh):
            try:
                os.remove(r.duong_dan_anh)
            except Exception:
                pass

@event.listens_for(TuongAnhResult, "after_delete")
def delete_image_file_on_tuong_anh_delete(mapper, connection, target):
    if target.duong_dan_anh and os.path.exists(target.duong_dan_anh):
        try:
            os.remove(target.duong_dan_anh)
        except Exception:
            pass


class InterpretationCache(Base):
    __tablename__ = "interpretation_caches"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    he_thong = Column(String(20), nullable=False, index=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    ket_qua_json = Column(JSON, nullable=False)
    tao_luc = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    het_han_luc = Column(DateTime(timezone=True), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<InterpretationCache id={self.id} key={self.cache_key} he_thong={self.he_thong}>"
