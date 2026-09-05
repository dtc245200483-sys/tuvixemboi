# -*- coding: utf-8 -*-
"""
B? 8 Test Cases ki?m th? to?n di?n Data Privacy & Retention Policy:
1. Upload ?nh khi CH?A ??ng ? ?i?u kho?n -> 403 Forbidden.
2. G?i POST /vision/consent -> c?p nh?t da_dong_y_sinh_trac_hoc = True.
3. Upload ?nh SAU KHI ?? ??ng ? -> 200 OK.
4. Qu?t xoa_anh_het_han -> b?n ghi qu? h?n b? x?a file v?t l?, da_duoc_xoa=True, dac_diem_quan_sat_json=None.
5. Qu?t xoa_anh_het_han -> b?n ghi CH?A h?t h?n KH?NG b? x?a.
6. DELETE /vision/anh/{id} ch?nh ch? -> x?a th?nh c?ng c? file v?t l? l?n DB.
7. DELETE /vision/anh/{id} c?a user kh?c -> 403 Forbidden, kh?ng ???c ph?p x?a.
8. X?a t?i kho?n User -> x?a to?n b? TuongAnhResult c? trong DB l?n t?p v?t l? tr?n disk (hook SQLAlchemy).
"""

import io
import os
import uuid
import json
import base64
from datetime import datetime, timedelta
from unittest.mock import patch
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import Base, get_db
from db.models import User, TuongAnhResult
from auth.security import create_access_token
from middleware.data_retention import xoa_anh_het_han
from vision_module.schemas import DacDiemTay, DacDiemMat
from main import app


def create_sample_image_bytes() -> bytes:
    img = Image.new("RGB", (300, 300), color=(220, 220, 220))
    draw = ImageDraw.Draw(img)
    draw.line([(30, 30), (270, 270)], fill=(20, 20, 20), width=4)
    draw.line([(30, 270), (270, 30)], fill=(40, 40, 40), width=4)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture(scope="function")
def test_setup():
    # S? d?ng StaticPool v? check_same_thread: False ?? SQLite in-memory d?ng chung an to?n tr?n c?c thread c?a FastAPI
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # T?o phi?n DB ??c l?p cho test runner
    db = TestingSession()

    user_a = User(
        id=uuid.uuid4(),
        email="user_a@privacy.test",
        password_hash="hash_a",
        is_active=True,
        da_dong_y_sinh_trac_hoc=False
    )
    user_b = User(
        id=uuid.uuid4(),
        email="user_b@privacy.test",
        password_hash="hash_b",
        is_active=True,
        da_dong_y_sinh_trac_hoc=True
    )
    db.add_all([user_a, user_b])
    db.commit()
    db.refresh(user_a)
    db.refresh(user_b)

    token_a = create_access_token({"sub": str(user_a.id), "type": "access"})
    token_b = create_access_token({"sub": str(user_b.id), "type": "access"})

    client = TestClient(app)

    yield {
        "db": db,
        "user_a": user_a,
        "user_b": user_b,
        "token_a": token_a,
        "token_b": token_b,
        "client": client
    }

    app.dependency_overrides.clear()
    db.close()


def test_1_upload_without_consent_returns_403(test_setup):
    """
    Test 1: Upload ?nh khi CH?A ??ng ? ?i?u kho?n -> x?c nh?n b? t? ch?i l?i 403.
    """
    client = test_setup["client"]
    token_a = test_setup["token_a"]
    img_b64 = base64.b64encode(create_sample_image_bytes()).decode("ascii")

    headers = {"Authorization": f"Bearer {token_a}"}
    response = client.post(
        "/vision/upload-tay",
        data={"du_lieu_anh_base64": img_b64},
        headers=headers
    )
    assert response.status_code == 403
    assert "ch?a ??ng ? ?i?u kho?n" in response.json()["detail"]


def test_2_post_consent_updates_user_record(test_setup):
    """
    Test 2: G?i POST /vision/consent -> x?c nh?n da_dong_y_sinh_trac_hoc ???c c?p nh?t ??ng.
    """
    client = test_setup["client"]
    db = test_setup["db"]
    user_a = test_setup["user_a"]
    token_a = test_setup["token_a"]

    assert user_a.da_dong_y_sinh_trac_hoc is False

    headers = {"Authorization": f"Bearer {token_a}"}
    response = client.post("/vision/consent", headers=headers)
    assert response.status_code == 200
    assert response.json()["da_dong_y_sinh_trac_hoc"] is True

    db.refresh(user_a)
    assert user_a.da_dong_y_sinh_trac_hoc is True
    assert user_a.thoi_gian_dong_y_sinh_trac_hoc is not None


def test_3_upload_after_consent_succeeds(test_setup):
    """
    Test 3: Upload ?nh SAU KHI ?? ??ng ? -> x?c nh?n th?nh c?ng.
    """
    client = test_setup["client"]
    user_b = test_setup["user_b"]
    token_b = test_setup["token_b"]
    img_b64 = base64.b64encode(create_sample_image_bytes()).decode("ascii")

    mock_tay = DacDiemTay(
        hinh_dang_ban_tay="B?n tay vu?ng v?n",
        do_ro_duong_tam_dao="S?u r?",
        do_ro_duong_tri_dao="Th?ng v? d?i",
        do_ro_duong_sinh_dao="U?n cong r?ng",
        hinh_dang_ngon_tay=["Ng?n th?ng"],
        mo_ta_them="G? Kim Tinh ??y ??n"
    )

    with patch("vision_module.service.phan_tich_anh_tay", return_value=mock_tay):
        headers = {"Authorization": f"Bearer {token_b}"}
        response = client.post(
            "/vision/upload-tay",
            data={"du_lieu_anh_base64": img_b64},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["loai_anh"] == "tay"
        assert "id" in data


def test_4_xoa_anh_het_han_removes_physical_file_and_clears_json(test_setup):
    """
    Test 4: T?o 1 b?n ghi TuongAnhResult c? ngay_het_han_luu_tru l? ng?y trong qu? kh?
    -> ch?y xoa_anh_het_han -> x?c nh?n file b? x?a, da_duoc_xoa = True, dac_diem_quan_sat_json b? x?a r?ng.
    """
    db = test_setup["db"]
    user_b = test_setup["user_b"]

    temp_dir = os.path.abspath(r"backend/storage/uploads/images/test_expired")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, "expired_img.jpg")
    with open(temp_file, "wb") as f:
        f.write(create_sample_image_bytes())

    assert os.path.exists(temp_file)

    expired_date = datetime.utcnow() - timedelta(days=1)
    record = TuongAnhResult(
        id=uuid.uuid4(),
        user_id=user_b.id,
        loai_anh="tay",
        duong_dan_anh=temp_file,
        dac_diem_quan_sat_json={"mo_ta": "??c ?i?m nh?y c?m"},
        da_duoc_xoa=False,
        ngay_het_han_luu_tru=expired_date
    )
    db.add(record)
    db.commit()

    result = xoa_anh_het_han(db)
    assert result["so_luong_da_xoa"] >= 1
    assert str(record.id) in result["danh_sach_id"]

    db.refresh(record)
    assert not os.path.exists(temp_file)
    assert record.da_duoc_xoa is True
    assert record.dac_diem_quan_sat_json is None


def test_5_xoa_anh_het_han_preserves_unexpired_records(test_setup):
    """
    Test 5: T?o 1 b?n ghi CH?A h?t h?n -> ch?y xoa_anh_het_han -> x?c nh?n b?n ghi n?y KH?NG b? x?a.
    """
    db = test_setup["db"]
    user_b = test_setup["user_b"]

    temp_dir = os.path.abspath(r"backend/storage/uploads/images/test_active")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, "active_img.jpg")
    with open(temp_file, "wb") as f:
        f.write(create_sample_image_bytes())

    future_date = datetime.utcnow() + timedelta(days=20)
    record = TuongAnhResult(
        id=uuid.uuid4(),
        user_id=user_b.id,
        loai_anh="mat",
        duong_dan_anh=temp_file,
        dac_diem_quan_sat_json={"mo_ta": "M?t ch? ?i?n"},
        da_duoc_xoa=False,
        ngay_het_han_luu_tru=future_date
    )
    db.add(record)
    db.commit()

    result = xoa_anh_het_han(db)
    assert str(record.id) not in result["danh_sach_id"]

    db.refresh(record)
    assert os.path.exists(temp_file)
    assert record.da_duoc_xoa is False
    assert record.dac_diem_quan_sat_json is not None

    if os.path.exists(temp_file):
        os.remove(temp_file)


def test_6_delete_own_image_removes_file_and_record(test_setup):
    """
    Test 6: G?i DELETE /vision/anh/{id} v?i ?nh c?a CH?NH user ?? -> x?c nh?n x?a th?nh c?ng, c? file l?n b?n ghi.
    """
    client = test_setup["client"]
    db = test_setup["db"]
    user_b = test_setup["user_b"]
    token_b = test_setup["token_b"]

    temp_dir = os.path.abspath(r"backend/storage/uploads/images/test_self_delete")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, "to_delete.jpg")
    with open(temp_file, "wb") as f:
        f.write(create_sample_image_bytes())

    record = TuongAnhResult(
        id=uuid.uuid4(),
        user_id=user_b.id,
        loai_anh="tay",
        duong_dan_anh=temp_file,
        dac_diem_quan_sat_json={"mo_ta": "X?a ngay"},
        da_duoc_xoa=False,
        ngay_het_han_luu_tru=datetime.utcnow() + timedelta(days=10)
    )
    db.add(record)
    db.commit()

    headers = {"Authorization": f"Bearer {token_b}"}
    response = client.delete(f"/vision/anh/{record.id}", headers=headers)
    assert response.status_code == 200

    assert not os.path.exists(temp_file)
    check_db = db.query(TuongAnhResult).filter(TuongAnhResult.id == record.id).first()
    assert check_db is None


def test_7_delete_other_user_image_forbidden(test_setup):
    """
    Test 7: G?i DELETE /vision/anh/{id} v?i ?nh c?a USER KH?C -> x?c nh?n b? t? ch?i (403), kh?ng cho x?a.
    """
    client = test_setup["client"]
    db = test_setup["db"]
    user_b = test_setup["user_b"]
    token_a = test_setup["token_a"]

    temp_dir = os.path.abspath(r"backend/storage/uploads/images/test_other")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, "other_user.jpg")
    with open(temp_file, "wb") as f:
        f.write(create_sample_image_bytes())

    record_b = TuongAnhResult(
        id=uuid.uuid4(),
        user_id=user_b.id,
        loai_anh="mat",
        duong_dan_anh=temp_file,
        dac_diem_quan_sat_json={"mo_ta": "?nh c?a user B"},
        da_duoc_xoa=False,
        ngay_het_han_luu_tru=datetime.utcnow() + timedelta(days=10)
    )
    db.add(record_b)
    db.commit()

    headers = {"Authorization": f"Bearer {token_a}"}
    response = client.delete(f"/vision/anh/{record_b.id}", headers=headers)
    assert response.status_code == 403
    assert "ng??i d?ng kh?c" in response.json()["detail"]

    assert os.path.exists(temp_file)
    check_db = db.query(TuongAnhResult).filter(TuongAnhResult.id == record_b.id).first()
    assert check_db is not None

    if os.path.exists(temp_file):
        os.remove(temp_file)


def test_8_delete_user_account_cascades_and_removes_physical_files(test_setup):
    """
    Test 8: Test x?a t?i kho?n User -> x?c nh?n to?n b? TuongAnhResult li?n quan
    b? x?a c? b?n ghi DB l?n file v?t l? (hook SQLAlchemy).
    """
    db = test_setup["db"]

    test_user = User(
        id=uuid.uuid4(),
        email="to_be_deleted@privacy.test",
        password_hash="hash_del",
        is_active=True,
        da_dong_y_sinh_trac_hoc=True
    )
    db.add(test_user)
    db.commit()

    temp_dir = os.path.abspath(r"backend/storage/uploads/images/test_cascade")
    os.makedirs(temp_dir, exist_ok=True)
    file_1 = os.path.join(temp_dir, "user_img_1.jpg")
    file_2 = os.path.join(temp_dir, "user_img_2.jpg")

    for fpath in [file_1, file_2]:
        with open(fpath, "wb") as f:
            f.write(create_sample_image_bytes())
        assert os.path.exists(fpath)

    rec_1 = TuongAnhResult(
        id=uuid.uuid4(),
        user_id=test_user.id,
        loai_anh="tay",
        duong_dan_anh=file_1,
        dac_diem_quan_sat_json={},
        da_duoc_xoa=False
    )
    rec_2 = TuongAnhResult(
        id=uuid.uuid4(),
        user_id=test_user.id,
        loai_anh="mat",
        duong_dan_anh=file_2,
        dac_diem_quan_sat_json={},
        da_duoc_xoa=False
    )
    db.add_all([rec_1, rec_2])
    db.commit()

    # X?a t?i kho?n User
    db.delete(test_user)
    db.commit()

    # 1. Database CASCADE
    remaining_records = db.query(TuongAnhResult).filter(
        TuongAnhResult.user_id == test_user.id
    ).all()
    assert len(remaining_records) == 0

    # 2. File v?t l? ph?i b? x?a ho?n to?n
    assert not os.path.exists(file_1), "File v?t l? 1 ch?a b? x?a khi x?a User!"
    assert not os.path.exists(file_2), "File v?t l? 2 ch?a b? x?a khi x?a User!"
