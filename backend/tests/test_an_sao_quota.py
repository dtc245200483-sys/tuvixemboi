# -*- coding: utf-8 -*-
"""
Bộ Test tự động kiểm tra tính năng An Sao Lập Lá Số, Quota & Premium:
1. Đăng ký & Đăng nhập user.
2. Tạo hồ sơ đầu tiên -> kiểm tra is_default=True, default_birth_profile_id được lưu.
3. Gọi POST /birth-profile/an-sao -> kiểm tra trừ 1 quota, is_quick_chart=True, is_default=False.
4. Kiểm tra Hồ Sơ Mệnh mặc định của user vẫn là hồ sơ ban đầu, không bị thay đổi.
5. Cưỡng chế quota về 50 -> Gọi an-sao tiếp theo trả về HTTP 429 Too Many Requests kèm thông báo.
6. Gọi POST /quota/upgrade-premium -> Nâng cấp thành công lên VIP.
7. Gọi an-sao khi đã là Premium -> Thành công, không bị chặn bởi Quota.
"""

import os
import sys
import uuid
from datetime import date
import pytest
from fastapi.testclient import TestClient

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from main import app
from db.database import SessionLocal, engine, Base
from db.models import User, BirthProfile, UsageQuota

client = TestClient(app, raise_server_exceptions=False)

TEST_USER_EMAIL = "test_an_sao_quota_user@khaitamhuyenhoc.vn"
TEST_PASSWORD = "StrongSecurePassword123@"


@pytest.fixture(scope="module", autouse=True)
def clean_db():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == TEST_USER_EMAIL).first()
        if user:
            db.delete(user)
            db.commit()
    finally:
        db.close()
    yield
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == TEST_USER_EMAIL).first()
        if user:
            db.delete(user)
            db.commit()
    finally:
        db.close()


def test_an_sao_quota_and_premium_flow():
    # 1. Đăng ký & Đăng nhập
    reg_resp = client.post("/auth/register", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_PASSWORD,
        "confirm_password": TEST_PASSWORD
    })
    assert reg_resp.status_code in [201, 400]

    login_resp = client.post("/auth/login", data={
        "username": TEST_USER_EMAIL,
        "password": TEST_PASSWORD
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Tạo hồ sơ chính đầu tiên (Phạm Vũ Quang Hưng)
    p1_resp = client.post("/birth-profile", json={
        "ho_ten": "Phạm Vũ Quang Hưng",
        "ngay_sinh_duong": "1888-05-29",
        "gio_sinh": 4,
        "phut_sinh": 0,
        "gioi_tinh": "nam"
    }, headers=headers)
    assert p1_resp.status_code == 201
    p1_data = p1_resp.json()["du_lieu"]
    assert p1_data["is_default"] is True
    assert p1_data["is_quick_chart"] is False
    main_profile_id = p1_data["id"]

    # Kiểm tra quota ban đầu chưa bị trừ
    q0_resp = client.get("/quota", headers=headers)
    assert q0_resp.status_code == 200
    assert q0_resp.json()["du_lieu"]["so_luot_da_dung"] == 0

    # 3. Thực hiện An Sao Lập Lá Số (nhập người khác: Nguyễn Văn B)
    an_sao_resp = client.post("/birth-profile/an-sao", json={
        "ho_ten": "Nguyễn Văn B (Người xem thử)",
        "ngay_sinh_duong": "2000-01-01",
        "gio_sinh": 10,
        "phut_sinh": 0,
        "gioi_tinh": "nu"
    }, headers=headers)
    assert an_sao_resp.status_code == 201
    an_sao_data = an_sao_resp.json()["du_lieu"]

    # 4. Kiểm tra lá số an sao nhanh có is_quick_chart=True, is_default=False
    assert an_sao_data["is_quick_chart"] is True
    assert an_sao_data["is_default"] is False

    # Kiểm tra hồ sơ mệnh mặc định trong danh sách vẫn là hồ sơ đầu tiên
    list_resp = client.get("/birth-profile", headers=headers)
    assert list_resp.status_code == 200
    profiles = list_resp.json()["du_lieu"]
    # Profile mặc định (Phạm Vũ Quang Hưng) phải nằm ở vị trí đầu tiên
    assert profiles[0]["id"] == main_profile_id
    assert profiles[0]["is_default"] is True
    assert profiles[0]["ho_ten"] == "Phạm Vũ Quang Hưng"

    # Kiểm tra quota đã bị trừ 1 lượt (so_luot_da_dung = 1)
    q1_resp = client.get("/quota", headers=headers)
    assert q1_resp.status_code == 200
    assert q1_resp.json()["du_lieu"]["so_luot_da_dung"] == 1
    assert q1_resp.json()["du_lieu"]["so_luot_con_lai"] == 49

    # 5. Cưỡng chế quota về hết lượt (50 lượt)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == TEST_USER_EMAIL).first()
        hom_nay = date.today()
        q_record = db.query(UsageQuota).filter(UsageQuota.user_id == user.id, UsageQuota.ngay == hom_nay).first()
        q_record.so_luot_da_dung = 50
        db.commit()
    finally:
        db.close()

    # Thử an sao khi hết quota -> Phải trả về HTTP 429
    blocked_resp = client.post("/birth-profile/an-sao", json={
        "ho_ten": "Người xem khi hết quota",
        "ngay_sinh_duong": "1999-09-09",
        "gio_sinh": 9,
        "phut_sinh": 0,
        "gioi_tinh": "nam"
    }, headers=headers)
    assert blocked_resp.status_code == 429
    assert "hết lượt" in blocked_resp.json()["loi"].lower()

    # 6. Nâng cấp tài khoản lên Premium
    upg_resp = client.post("/quota/upgrade-premium", headers=headers)
    assert upg_resp.status_code == 200
    assert upg_resp.json()["du_lieu"]["is_premium"] is True

    # 7. Sau khi nâng cấp Premium -> An sao lại thành công ngay, không còn bị chặn
    premium_an_sao_resp = client.post("/birth-profile/an-sao", json={
        "ho_ten": "Người xem sau khi lên Premium",
        "ngay_sinh_duong": "1999-09-09",
        "gio_sinh": 9,
        "phut_sinh": 0,
        "gioi_tinh": "nam"
    }, headers=headers)
    assert premium_an_sao_resp.status_code == 201
    assert premium_an_sao_resp.json()["du_lieu"]["is_quick_chart"] is True

    # 8. Test chuyển đổi hồ sơ mặc định PUT /birth-profile/{id}/set-default
    new_profile_id = premium_an_sao_resp.json()["du_lieu"]["id"]
    set_def_resp = client.put(f"/birth-profile/{new_profile_id}/set-default", headers=headers)
    assert set_def_resp.status_code == 200
    assert set_def_resp.json()["du_lieu"]["is_default"] is True
