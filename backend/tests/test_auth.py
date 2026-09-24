# -*- coding: utf-8 -*-
"""
Unit and Integration Tests cho hệ thống Xác thực (Auth).
Bao quát toàn bộ 9 bước kiểm thử theo tiêu chuẩn của Prompt 2.2.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from db.database import SessionLocal, engine, Base
Base.metadata.create_all(bind=engine)
from db.models import User

client = TestClient(app)

TEST_EMAIL = "auth_test_user_777@example.com"
TEST_PASSWORD = "StrongPassword123@"

@pytest.fixture(autouse=True)
def cleanup_test_user():
    # Cleanup trước khi test
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == TEST_EMAIL).first()
        if user:
            db.delete(user)
            db.commit()
    finally:
        db.close()
    
    yield
    
    # Cleanup sau khi test
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == TEST_EMAIL).first()
        if user:
            db.delete(user)
            db.commit()
    finally:
        db.close()

def test_full_auth_flow():
    # 1. Health check
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json().get("status") == "ok"

    # 2. Đăng ký thành công (201)
    reg_payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "confirm_password": TEST_PASSWORD
    }
    res_reg = client.post("/auth/register", json=reg_payload)
    assert res_reg.status_code == 201
    reg_data = res_reg.json()
    assert reg_data["email"] == TEST_EMAIL
    assert "id" in reg_data
    assert "password_hash" not in reg_data

    # 3. Đăng ký trùng email -> Lỗi 409
    res_reg_dup = client.post("/auth/register", json=reg_payload)
    assert res_reg_dup.status_code == 409

    # 4. Đăng nhập thành công -> trả về access_token và refresh_token
    login_payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    res_login = client.post("/auth/login", json=login_payload)
    assert res_login.status_code == 200
    login_data = res_login.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data
    assert login_data["token_type"] == "bearer"
    access_token = login_data["access_token"]
    refresh_token = login_data["refresh_token"]

    # 5. Gọi /auth/me KHÔNG kèm token -> Lỗi 401
    res_me_no_token = client.get("/auth/me")
    assert res_me_no_token.status_code == 401

    # 6. Gọi /auth/me CÓ kèm token -> Thành công trả về đúng User
    headers = {"Authorization": f"Bearer {access_token}"}
    res_me_with_token = client.get("/auth/me", headers=headers)
    assert res_me_with_token.status_code == 200
    me_data = res_me_with_token.json()
    assert me_data["email"] == TEST_EMAIL
    assert me_data["id"] == reg_data["id"]
    assert "password_hash" not in me_data

    # 7. Đăng nhập với password SAI -> Lỗi 401, không lộ thông tin
    bad_login_payload = {
        "email": TEST_EMAIL,
        "password": "WrongPassword999@"
    }
    res_bad_login = client.post("/auth/login", json=bad_login_payload)
    assert res_bad_login.status_code == 401
    assert "Email hoặc mật khẩu không chính xác" in res_bad_login.json()["detail"]

    # 8. Gọi /auth/refresh -> nhận access_token mới và test lại với /auth/me
    res_refresh = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert res_refresh.status_code == 200
    new_access_token = res_refresh.json()["access_token"]
    assert new_access_token != ""

    new_headers = {"Authorization": f"Bearer {new_access_token}"}
    res_me_new_token = client.get("/auth/me", headers=new_headers)
    assert res_me_new_token.status_code == 200
    assert res_me_new_token.json()["email"] == TEST_EMAIL
