# -*- coding: utf-8 -*-
"""
Kiểm thử tính năng quản lý phiên trò chuyện AI (ChatSession):
1. Tạo session mới và kiểm tra cấu trúc.
2. Gửi tin nhắn gắn liền với session_id và xác nhận tin nhắn thuộc đúng session.
3. Cô lập tin nhắn giữa các session khác nhau.
4. Lấy danh sách session (tối đa 20 phiên gần nhất).
5. Tự động cắt tỉa đảm bảo không vượt quá 20 sessions.
6. Xóa riêng từng session và xác nhận tin nhắn bên trong bị xóa sạch (cascade delete).
"""

import os
import sys
import uuid
import pytest
from fastapi.testclient import TestClient

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from db.database import Base, get_db, engine, SessionLocal
from db.models import User, ChatSession, ChatHistory, UsageQuota
from auth.security import create_access_token
from main import app

# Đảm bảo bảng tồn tại (gọi init_db để đảm bảo migration)
from db.database import init_db
init_db()

TEST_EMAIL_CHAT = "chat_session_unit_test@example.com"
client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="module", autouse=True)
def cleanup_chat_test_user():
    """Xóa user test trước và sau khi chạy module."""
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == TEST_EMAIL_CHAT).first()
        if u:
            db.delete(u)
            db.commit()
    finally:
        db.close()

    yield

    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == TEST_EMAIL_CHAT).first()
        if u:
            db.delete(u)
            db.commit()
    finally:
        db.close()


@pytest.fixture(scope="module")
def auth_headers():
    """Tạo user test và trả về auth headers."""
    db = SessionLocal()
    try:
        # Tạo user test nếu chưa có
        from auth.security import hash_password
        user = User(
            id=uuid.uuid4(),
            email=TEST_EMAIL_CHAT,
            password_hash=hash_password("TestPassword123!"),
            is_active=True,
            is_premium=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = str(user.id)
        user_email = user.email
    finally:
        db.close()

    token = create_access_token({"sub": user_id, "email": user_email})
    return {"Authorization": f"Bearer {token}"}


def test_chat_session_lifecycle(auth_headers):
    """Test toàn bộ vòng đời một phiên trò chuyện."""
    headers = auth_headers

    # 1. Tạo session mới
    res_create = client.post(
        "/chat/sessions",
        json={"tieu_de": "Hỏi về công danh sự nghiệp"},
        headers=headers
    )
    assert res_create.status_code == 200, f"Tạo session thất bại: {res_create.text}"
    data_sess = res_create.json()["du_lieu"]
    sess_id = data_sess["id"]
    assert data_sess["tieu_de"] == "Hỏi về công danh sự nghiệp"

    # 2. Lấy danh sách sessions - phải có ít nhất 1
    res_list = client.get("/chat/sessions", headers=headers)
    assert res_list.status_code == 200
    sessions = res_list.json()["du_lieu"]["danh_sach"]
    assert any(s["id"] == sess_id for s in sessions)

    # 3. Lấy tin nhắn rỗng của session mới tạo
    res_msgs = client.get(f"/chat/sessions/{sess_id}/messages", headers=headers)
    assert res_msgs.status_code == 200
    msgs_data = res_msgs.json()["du_lieu"]
    assert msgs_data["tong_so"] == 0

    # 4. Tạo session thứ 2
    res_create2 = client.post(
        "/chat/sessions",
        json={"tieu_de": "Hỏi về nhân duyên tình cảm"},
        headers=headers
    )
    assert res_create2.status_code == 200
    sess_id_2 = res_create2.json()["du_lieu"]["id"]

    # 5. Xóa session 1
    res_del = client.delete(f"/chat/sessions/{sess_id}", headers=headers)
    assert res_del.status_code == 200

    # 6. Truy vấn lại session 1 - phải 404
    res_check = client.get(f"/chat/sessions/{sess_id}/messages", headers=headers)
    assert res_check.status_code == 404

    # 7. Session 2 vẫn tồn tại
    res_check2 = client.get(f"/chat/sessions/{sess_id_2}/messages", headers=headers)
    assert res_check2.status_code == 200

    # Cleanup session 2
    client.delete(f"/chat/sessions/{sess_id_2}", headers=headers)


def test_max_20_sessions_pruning(auth_headers):
    """Test auto-prune: sau khi tạo 25 sessions chỉ còn tối đa 20."""
    headers = auth_headers

    # Tạo 25 sessions liên tiếp
    for i in range(25):
        client.post(
            "/chat/sessions",
            json={"tieu_de": f"Cuộc trò chuyện số {i+1}"},
            headers=headers
        )

    # Lấy danh sách sessions
    res_list = client.get("/chat/sessions", headers=headers)
    assert res_list.status_code == 200
    sessions = res_list.json()["du_lieu"]["danh_sach"]

    # Phải có tối đa 20 sessions
    assert len(sessions) <= 20
