# -*- coding: utf-8 -*-
"""
Script Khởi Tạo Tài Khoản Quản Trị Viên (Admin)
Tự động thiết lập trong cơ sở dữ liệu để đăng nhập ngay trên Web/App
"""

import sys
import os
import uuid
from datetime import datetime, date

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Đảm bảo đường dẫn import đúng
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import SessionLocal, engine, Base
from db.models import User, BirthProfile, UsageQuota
from auth.security import hash_password

def create_admin_account(email: str = "admin@khaitamhuyenhoc.com", password: str = "Admin@123456"):
    # Đảm bảo các bảng đã tồn tại
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Kiểm tra tài khoản đã tồn tại chưa
        user = db.query(User).filter(User.email == email).first()
        if user:
            # Cập nhật mật khẩu mới và kích hoạt
            user.password_hash = hash_password(password)
            user.is_active = True
            user.da_dong_y_sinh_trac_hoc = True
            user.thoi_gian_dong_y_sinh_trac_hoc = datetime.utcnow()
            db.commit()
            db.refresh(user)
            print(f"[✓] Đã cập nhật mật khẩu cho tài khoản Admin: {email}")
        else:
            user = User(
                id=uuid.uuid4(),
                email=email,
                password_hash=hash_password(password),
                is_active=True,
                da_dong_y_sinh_trac_hoc=True,
                thoi_gian_dong_y_sinh_trac_hoc=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"[✓] Đã tạo thành công tài khoản Admin mới: {email}")

        # 2. Tạo hồ sơ sinh mặc định cho Admin nếu chưa có
        profile = db.query(BirthProfile).filter(BirthProfile.user_id == user.id).first()
        if not profile:
            profile = BirthProfile(
                id=uuid.uuid4(),
                user_id=user.id,
                ho_ten="Quản Trị Viên (Admin)",
                ngay_sinh_duong=date(1990, 1, 1),
                gio_sinh=9,
                phut_sinh=30,
                gioi_tinh="nam",
                created_at=datetime.utcnow()
            )
            db.add(profile)
            db.commit()
            print("[✓] Đã tạo hồ sơ sinh mẫu cho Admin (Nam, 01/01/1990, 09:30).")

        # 3. Tạo hạn mức AI Quota cao cho Admin
        hom_nay = date.today()
        quota = db.query(UsageQuota).filter(
            UsageQuota.user_id == user.id,
            UsageQuota.ngay == hom_nay
        ).first()
        if not quota:
            quota = UsageQuota(
                id=uuid.uuid4(),
                user_id=user.id,
                ngay=hom_nay,
                so_luot_da_dung=0
            )
            db.add(quota)
            db.commit()
            print("[✓] Đã khởi tạo hạn mức AI Quota cho ngày hôm nay.")

        print("\n" + "=" * 60)
        print(" THÔNG TIN TÀI KHOẢN QUẢN TRỊ VIÊN (ADMIN)")
        print("=" * 60)
        print(f" • Email:     {email}")
        print(f" • Mật khẩu:  {password}")
        print("=" * 60 + "\n")
        return user
    except Exception as e:
        db.rollback()
        print(f"[!] Lỗi khi tạo tài khoản Admin: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    # Tạo tài khoản chính
    create_admin_account("admin@khaitamhuyenhoc.com", "Admin@123456")
    # Tạo thêm tài khoản phụ dự phòng ngắn gọn
    create_admin_account("admin@tuvixemboi.vn", "Admin@123456")
