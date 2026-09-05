# -*- coding: utf-8 -*-
"""
Bộ 10 Integration Tests cho Infrastructure Layer (Prompt 7.2):
1. Gọi liên tục vượt quá rate_limit_per_minute từ CÙNG 1 IP -> trả về 429.
2. Gọi từ 2 IP khác nhau, mỗi IP dưới giới hạn -> cả 2 đều thành công (không bị tính chung).
3. Đợi qua khoảng thời gian sliding window -> IP bị chặn có thể gọi lại bình thường.
4. Rate limiting KHÔNG ảnh hưởng đến Usage Quota (Prompt 6.5) -> 2 cơ chế hoạt động độc lập.
5. Test khoi_tao_sentry -> xác nhận KHÔNG lỗi khi sentry_dsn rỗng (môi trường dev).
6. Mô phỏng 1 lỗi trong request -> Sentry nhận được lỗi kèm context (user_id, endpoint).
7. Chạy backup_database -> xác nhận file backup được tạo, có timestamp đúng, dung lượng > 0.
8. Test RESTORE THỰC TẾ: dùng file backup, khôi phục vào database test riêng -> kiểm tra khớp số lượng bản ghi mỗi bảng.
9. Chạy don_dep_backup_cu với backup cũ hơn 30 ngày -> xác nhận bị xóa; backup mới -> giữ lại.
10. Test scheduled job độc lập: backup_database lỗi -> xoa_anh_het_han vẫn chạy bình thường.
"""

import os
import sys
import time
import uuid
import shutil
import sqlite3
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from config import settings
from main import app
from middleware.rate_limiter import RateLimiter, default_rate_limiter
from middleware.sentry_setup import khoi_tao_sentry, gan_context_loi
from middleware.backup_service import (
    backup_database,
    restore_database,
    don_dep_backup_cu,
    chay_tat_ca_scheduled_jobs
)
from db.database import SessionLocal, Base, engine
from db.models import User, BirthProfile, TuongAnhResult

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def clean_rate_limiter():
    """Tự động làm sạch trạng thái Rate Limiter trước mỗi test case"""
    default_rate_limiter.reset()
    yield
    default_rate_limiter.reset()


# ==============================================================================
# TEST 1: VƯỢT QUÁ RATE LIMIT TỪ CÙNG 1 IP -> 429
# ==============================================================================
def test_01_rate_limit_same_ip_exceeded_429():
    test_ip = "198.51.100.1"
    limit = 5

    # Cấu hình limiter tạm thời hoặc kiểm tra qua middleware
    with patch.object(settings, "rate_limit_per_minute", limit):
        # 5 request đầu tiên thành công (status không phải 429)
        for i in range(limit):
            resp = client.get("/auth/me", headers={"X-Forwarded-For": test_ip})
            assert resp.status_code != 429, f"Request {i+1} không nên bị chặn 429"

        # Request thứ 6 vượt giới hạn -> Bắt buộc nhận 429
        blocked_resp = client.get("/auth/me", headers={"X-Forwarded-For": test_ip})
        assert blocked_resp.status_code == 429
        data = blocked_resp.json()
        assert data["thanh_cong"] is False
        assert "Quá nhiều yêu cầu" in data["loi"]
        assert "Retry-After" in blocked_resp.headers


# ==============================================================================
# TEST 2: HAI IP KHÁC NHAU DƯỚI GIỚI HẠN -> KHÔNG BỊ TÍNH CHUNG
# ==============================================================================
def test_02_rate_limit_distinct_ips():
    ip_a = "192.0.2.1"
    ip_b = "192.0.2.2"
    limit = 4

    with patch.object(settings, "rate_limit_per_minute", limit):
        # IP A gửi 3 request (dưới limit 4)
        for _ in range(3):
            resp_a = client.get("/auth/me", headers={"X-Forwarded-For": ip_a})
            assert resp_a.status_code != 429

        # IP B gửi 3 request (dưới limit 4)
        for _ in range(3):
            resp_b = client.get("/auth/me", headers={"X-Forwarded-For": ip_b})
            assert resp_b.status_code != 429

        # Tổng cộng đã 6 request nhưng không IP nào vượt 4 -> Cả 2 đều không bị 429
        check_a = client.get("/auth/me", headers={"X-Forwarded-For": ip_a})
        check_b = client.get("/auth/me", headers={"X-Forwarded-For": ip_b})
        assert check_a.status_code != 429
        assert check_b.status_code != 429


# ==============================================================================
# TEST 3: QUA KHOẢNG THỜI GIAN SLIDING WINDOW -> IP ĐƯỢC MỞ KHÓA
# ==============================================================================
def test_03_rate_limit_sliding_window_reset():
    limiter = RateLimiter()
    key = "user_ip_test_window"
    limit = 2
    window = 10  # 10 giây

    base_time = 1000.0

    # Tại t = 1000.0: Gửi 2 request hợp lệ
    with patch("time.time", return_value=base_time):
        assert limiter.kiem_tra_rate_limit(key, limit, window) is True
        assert limiter.kiem_tra_rate_limit(key, limit, window) is True
        # Request thứ 3 cùng thời điểm -> Bị chặn
        assert limiter.kiem_tra_rate_limit(key, limit, window) is False

    # Tại t = 1005.0 (vẫn trong window 10s): Vẫn bị chặn
    with patch("time.time", return_value=base_time + 5.0):
        assert limiter.kiem_tra_rate_limit(key, limit, window) is False

    # Tại t = 1011.0 (đã qua window 10s): Được mở khóa và chấp nhận lại bình thường
    with patch("time.time", return_value=base_time + 11.0):
        assert limiter.kiem_tra_rate_limit(key, limit, window) is True


# ==============================================================================
# TEST 4: RATE LIMIT VÀ USAGE QUOTA HOẠT ĐỘNG HOÀN TOÀN ĐỘC LẬP
# ==============================================================================
def test_04_rate_limit_quota_independence():
    """
    Xác nhận Rate Limit (theo IP, chống spam chung) và Usage Quota (theo User ID, giới hạn AI)
    hoạt động độc lập, không thay thế hay làm sai lệch lẫn nhau.
    """
    from middleware.quota_service import kiem_tra_va_tang_quota, lay_thong_tin_quota
    db = SessionLocal()
    try:
        # Tạo người dùng hợp lệ trong DB để thỏa mãn ràng buộc khóa ngoại
        user = User(
            id=uuid.uuid4(),
            email=f"quota_infra_{uuid.uuid4().hex[:6]}@example.com",
            password_hash="dummy_hash"
        )
        db.add(user)
        db.commit()
        user_uuid = user.id

        client_ip = "203.0.113.199"

        # 1. User tăng Quota sử dụng qua quota service
        quota_res1 = kiem_tra_va_tang_quota(user_uuid, db)
        assert quota_res1["con_han_muc"] is True
        assert quota_res1["so_luot_da_dung"] == 1
        limit = quota_res1["gioi_han_ngay"]
        assert quota_res1["so_luot_con_lai"] == limit - 1

        # 2. Nhưng IP của user này bị spam và chạm ngưỡng Rate Limit
        with patch.object(settings, "rate_limit_per_minute", 2):
            # Gửi 2 request bình thường từ IP này
            r1 = client.get("/auth/me", headers={"X-Forwarded-For": client_ip})
            r2 = client.get("/auth/me", headers={"X-Forwarded-For": client_ip})
            assert r1.status_code != 429
            assert r2.status_code != 429

            # Request thứ 3 từ IP này -> Bị chặn bởi Rate Limit (chưa hề gọi đến AI logic)
            r3 = client.get("/auth/me", headers={"X-Forwarded-For": client_ip})
            assert r3.status_code == 429
            assert "Quá nhiều yêu cầu" in r3.json()["loi"]

        # 3. Quota của user trong DB vẫn giữ nguyên (vẫn dùng 1, còn limit-1), không bị ảnh hưởng bởi Rate Limit
        info_after = lay_thong_tin_quota(user_uuid, db)
        assert info_after["so_luot_da_dung"] == 1
        assert info_after["so_luot_con_lai"] == limit - 1
    finally:
        db.close()


# ==============================================================================
# TEST 5: KHOI_TAO_SENTRY KHÔNG GÂY LỖI KHI DSN RỖNG (MÔI TRƯỜNG DEV)
# ==============================================================================
def test_05_sentry_init_empty_dsn():
    with patch.object(settings, "sentry_dsn", ""):
        ket_qua = khoi_tao_sentry()
        # Xác nhận trả về False an toàn, không ném ngoại lệ
        assert ket_qua is False


# ==============================================================================
# TEST 6: SENTRY BẮT ĐƯỢC LỖI KÈM CONTEXT (USER_ID, ENDPOINT) KHÔNG CHỨA PII
# ==============================================================================
def test_06_sentry_capture_with_context():
    with patch("sentry_sdk.set_user") as mock_set_user, \
         patch("sentry_sdk.set_tag") as mock_set_tag:

        test_user_id = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
        test_endpoint = "/tu-vi/123"

        # Gắn context an toàn
        gan_context_loi(user_id=test_user_id, endpoint=test_endpoint)

        # Xác nhận chỉ gắn id cho user (không có ngày sinh, email, hình ảnh)
        mock_set_user.assert_called_once_with({"id": test_user_id})
        mock_set_tag.assert_called_once_with("endpoint", test_endpoint)


# ==============================================================================
# TEST 7: SAO LƯU BACKUP_DATABASE TẠO TỆP HỢP LỆ VỚI TIMESTAMP VÀ DUNG LƯỢNG > 0
# ==============================================================================
def test_07_backup_database_creates_file(tmp_path):
    custom_backup_dir = str(tmp_path / "test_backups")

    res = backup_database(output_dir=custom_backup_dir)

    assert res["thanh_cong"] is True
    assert res["loi"] is None
    assert os.path.exists(res["duong_dan"])
    assert res["dung_luong_bytes"] > 0
    assert res["ten_file"].startswith("backup_")
    # Kiểm tra định dạng timestamp trong tên tệp (YYYYMMDD_HHMMSS)
    parts = res["ten_file"].replace(".db", "").replace(".sql", "").split("_")
    assert len(parts) >= 3  # backup, sqlite/pg, YYYYMMDD, HHMMSS


# ==============================================================================
# TEST 8: RESTORE THỰC TẾ: KHÔI PHỤC DỮ LIỆU TỪ BACKUP VÀ ĐỐI CHIẾU TOÀN VẸN
# ==============================================================================
def test_08_restore_database_actual_verification(tmp_path):
    """
    Kiểm thử năng lực RESTORE THỰC TẾ:
    1. Tạo 1 cơ sở dữ liệu nguồn với các bảng User và BirthProfile có dữ liệu cụ thể.
    2. Chạy backup_database để xuất file snapshot.
    3. Chạy restore_database để khôi phục vào 1 database đích hoàn toàn mới.
    4. Đối chiếu số lượng bảng và dữ liệu từng bảng để chứng minh backup dùng được thật sự!
    """
    src_db_file = str(tmp_path / "source_db.db")
    backup_dir = str(tmp_path / "backups")
    target_db_file = str(tmp_path / "restored_db.db")

    # 1. Khởi tạo DB nguồn với 2 bảng và dữ liệu mẫu
    src_conn = sqlite3.connect(src_db_file)
    src_cursor = src_conn.cursor()
    src_cursor.execute("CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT, password_hash TEXT);")
    src_cursor.execute("CREATE TABLE profiles (id TEXT PRIMARY KEY, user_id TEXT, ho_ten TEXT, nam_sinh INTEGER);")
    src_cursor.execute("INSERT INTO users VALUES ('u1', 'test1@example.com', 'hash1');")
    src_cursor.execute("INSERT INTO users VALUES ('u2', 'test2@example.com', 'hash2');")
    src_cursor.execute("INSERT INTO profiles VALUES ('p1', 'u1', 'Nguyen Van A', 1990);")
    src_cursor.execute("INSERT INTO profiles VALUES ('p2', 'u1', 'Nguyen Van Con', 2018);")
    src_cursor.execute("INSERT INTO profiles VALUES ('p3', 'u2', 'Tran Thi B', 1995);")
    src_conn.commit()
    src_conn.close()

    # 2. Tạo bản sao lưu từ DB nguồn
    src_url = f"sqlite:///{src_db_file}"
    backup_res = backup_database(db_url=src_url, output_dir=backup_dir)
    assert backup_res["thanh_cong"] is True
    backup_file_path = backup_res["duong_dan"]
    assert os.path.exists(backup_file_path)

    # 3. Phục hồi thực tế vào database đích mới
    target_url = f"sqlite:///{target_db_file}"
    restore_res = restore_database(file_backup=backup_file_path, target_db_url=target_url)

    assert restore_res["thanh_cong"] is True
    assert restore_res["loi"] is None
    assert restore_res["so_bang"] == 2
    assert set(restore_res["danh_sach_bang"]) == {"users", "profiles"}

    # 4. Kiểm tra đối chiếu số lượng bản ghi chính xác
    target_conn = sqlite3.connect(target_db_file)
    target_cursor = target_conn.cursor()

    target_cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = target_cursor.fetchone()[0]
    assert user_count == 2, f"Kỳ vọng 2 users, thực tế nhận được {user_count}"

    target_cursor.execute("SELECT COUNT(*) FROM profiles;")
    profile_count = target_cursor.fetchone()[0]
    assert profile_count == 3, f"Kỳ vọng 3 profiles, thực tế nhận được {profile_count}"

    # Kiểm tra nội dung chi tiết
    target_cursor.execute("SELECT email, password_hash FROM users WHERE id='u1';")
    u1_data = target_cursor.fetchone()
    assert u1_data == ("test1@example.com", "hash1")

    target_conn.close()


# ==============================================================================
# TEST 9: DỌN DẸP BACKUP CŨ (> 30 NGÀY XÓA, < 30 NGÀY GIỮ LẠI)
# ==============================================================================
def test_09_cleanup_old_backups(tmp_path):
    backup_dir = str(tmp_path / "test_cleanup_dir")
    os.makedirs(backup_dir, exist_ok=True)

    now = time.time()
    day_in_seconds = 86400

    # 1. Tạo 2 tệp backup cũ (35 ngày và 40 ngày trước)
    file_old1 = os.path.join(backup_dir, "backup_sqlite_20260101_000000.db")
    file_old2 = os.path.join(backup_dir, "backup_sqlite_20260110_000000.db")
    with open(file_old1, "w") as f:
        f.write("old backup 1")
    with open(file_old2, "w") as f:
        f.write("old backup 2")
    os.utime(file_old1, (now - 35 * day_in_seconds, now - 35 * day_in_seconds))
    os.utime(file_old2, (now - 40 * day_in_seconds, now - 40 * day_in_seconds))

    # 2. Tạo 1 tệp backup mới (3 ngày trước)
    file_new = os.path.join(backup_dir, "backup_sqlite_20260220_000000.db")
    with open(file_new, "w") as f:
        f.write("recent backup")
    os.utime(file_new, (now - 3 * day_in_seconds, now - 3 * day_in_seconds))

    # 3. Chạy dọn dẹp với ngưỡng 30 ngày
    cleanup_res = don_dep_backup_cu(so_ngay_giu=30, backup_dir=backup_dir)

    assert cleanup_res["so_file_da_xoa"] == 2
    assert cleanup_res["so_file_con_lai"] == 1
    assert not os.path.exists(file_old1)
    assert not os.path.exists(file_old2)
    assert os.path.exists(file_new)


# ==============================================================================
# TEST 10: SCHEDULED JOBS ĐỘC LẬP: BACKUP LỖI KHÔNG ẢNH HƯỞNG ĐẾN XÓA ẢNH
# ==============================================================================
def test_10_scheduled_jobs_isolated_error_handling():
    """
    Mô phỏng trường hợp backup_database gặp sự cố (ổ đĩa đầy, mất quyền...)
    Xác nhận xoa_anh_het_han và don_dep_backup_cu VẪN CHẠY BÌNH THƯỜNG.
    """
    mock_xoa_anh = MagicMock(return_value={"so_luong_da_xoa": 2, "danh_sach_id": ["id1", "id2"]})

    with patch("middleware.backup_service.backup_database", side_effect=RuntimeError("Ổ đĩa sao lưu bị ngắt kết nối!")):
        with patch("middleware.data_retention.xoa_anh_het_han", mock_xoa_anh):
            # Thực thi bộ điều phối scheduled jobs
            ket_qua = chay_tat_ca_scheduled_jobs()

            # Job 1 (backup) ghi nhận lỗi
            assert ket_qua["backup"]["thanh_cong"] is False
            assert "Ổ đĩa sao lưu bị ngắt kết nối!" in ket_qua["backup"]["loi"]

            # Job 2 (dọn dẹp backup) vẫn chạy thành công
            assert ket_qua["don_dep_backup"]["so_file_da_xoa"] >= 0

            # Job 3 (xóa ảnh hết hạn) VẪN ĐƯỢC GỌI VÀ HOÀN TẤT BÌNH THƯỜNG
            mock_xoa_anh.assert_called_once()
            assert ket_qua["xoa_anh_het_han"] == {"so_luong_da_xoa": 2, "danh_sach_id": ["id1", "id2"]}
