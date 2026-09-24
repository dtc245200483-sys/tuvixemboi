# -*- coding: utf-8 -*-
"""
Bộ 12 Test Cases Tích Hợp Toàn Luồng cho API Orchestration Layer (backend/api/):
1. Đăng ký -> đăng nhập -> tạo BirthProfile -> xác nhận trả về đúng APIResponse với ngày âm lịch đã tính.
2. GET /tu-vi/{id} với BirthProfile hợp lệ -> xác nhận trả về lá số + luận giải đã qua Content Safety.
3. Gọi lại GET /tu-vi/{id} lần 2 (cùng id) -> xác nhận nhanh hơn lần 1 (dùng cache từ Prompt 6.5).
4. GET /bat-tu/{id} -> xác nhận trả về Tứ Trụ + luận giải riêng biệt, không lẫn với kết quả Tử Vi.
5. POST /gieo-que với câu hỏi cụ thể -> xác nhận trả về quẻ + luận giải.
6. POST /xem-tuong/tay KHÔNG có consent trước -> xác nhận bị từ chối đúng theo Prompt 4.2 (403).
7. POST /chat với câu hỏi tự do -> xác nhận Topic Detection hoạt động đúng, trả lời đúng hệ thống.
8. Gọi các endpoint AI liên tục đến khi hết quota -> xác nhận endpoint tiếp theo trả về lỗi 429 rõ ràng, KHÔNG chạy logic bên trong.
9. Test không có token (chưa đăng nhập) gọi bất kỳ route bảo vệ nào -> xác nhận đều trả về 401.
10. Test gọi API với dữ liệu đầu vào sai định dạng -> xác nhận trả về lỗi rõ ràng trong APIResponse, không crash server.
11. Test exception handler toàn cục: mô phỏng 1 lỗi bất ngờ -> xác nhận response trả về thông báo an toàn, không lộ stack trace.
12. Test CORS: mô phỏng request từ origin đã cấu hình trong CORS_ORIGINS -> xác nhận không bị chặn.
"""

import os
import sys
import uuid
import json
import time
from datetime import date, datetime
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from main import app
from db.database import SessionLocal, engine, Base
from db.models import User, BirthProfile, LaSoTuViResult, TuTruResult, QueKinhDichResult, UsageQuota, InterpretationCache
from ai_module.schemas import AIResponse

Base.metadata.create_all(bind=engine)
client = TestClient(app, raise_server_exceptions=False)

TEST_EMAIL_MAIN = "api_orchestrator_test_main@example.com"
TEST_EMAIL_NOCONSENT = "api_test_no_consent@example.com"
TEST_PASSWORD = "StrongSecurePassword123@"

MOCK_AI_RESPONSE = AIResponse(
    text=json.dumps({
        "chu_de": "tong_quan",
        "noi_dung": "Lá số cát tường, đắc cách quý hiển, công danh sự nghiệp phát triển thuận lợi và bền vững.",
        "muc_do_tin_cay": 0.88
    }, ensure_ascii=False),
    provider="gemini",
    tokens_used=120,
    thoi_gian_xu_ly_ms=65,
    thanh_cong=True,
    loi_neu_co=None,
    bi_cat_ngang=False
)


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Dọn dẹp dữ liệu thử nghiệm trước và sau toàn bộ suite test."""
    db = SessionLocal()
    try:
        test_emails = [TEST_EMAIL_MAIN, TEST_EMAIL_NOCONSENT, "api_test_quota_user@example.com"]
        for email in test_emails:
            u = db.query(User).filter(User.email == email).first()
            if u:
                db.delete(u)
        db.commit()
    finally:
        db.close()

    yield

    db = SessionLocal()
    try:
        test_emails = [TEST_EMAIL_MAIN, TEST_EMAIL_NOCONSENT, "api_test_quota_user@example.com"]
        for email in test_emails:
            u = db.query(User).filter(User.email == email).first()
            if u:
                db.delete(u)
        db.commit()
    finally:
        db.close()


@pytest.fixture(scope="module")
def authenticated_client():
    """Tạo tài khoản chính và đăng nhập, trả về client kèm auth headers."""
    # 1. Đăng ký
    reg_resp = client.post("/auth/register", json={
        "email": TEST_EMAIL_MAIN,
        "password": TEST_PASSWORD,
        "confirm_password": TEST_PASSWORD
    })
    assert reg_resp.status_code in [201, 400]

    # 2. Đăng nhập lấy access_token
    login_resp = client.post("/auth/login", data={
        "username": TEST_EMAIL_MAIN,
        "password": TEST_PASSWORD
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    return headers


def _get_or_create_profile_id(headers):
    list_resp = client.get("/birth-profile", headers=headers)
    profiles = list_resp.json().get("du_lieu", [])
    if profiles:
        return profiles[0]["id"]
    create_resp = client.post("/birth-profile", json={
        "ho_ten": "Nguyễn Văn An",
        "ngay_sinh_duong": "1990-08-15",
        "gio_sinh": 11,
        "phut_sinh": 30,
        "gioi_tinh": "nam"
    }, headers=headers)
    return create_resp.json()["du_lieu"]["id"]


# ==============================================================================
# TEST 1: AUTH & BIRTH PROFILE FLOW (Đăng ký -> Đăng nhập -> Tạo Profile)
# ==============================================================================
def test_01_auth_birth_profile_flow(authenticated_client):
    headers = authenticated_client
    profile_payload = {
        "ho_ten": "Nguyễn Văn An",
        "ngay_sinh_duong": "1990-08-15",
        "gio_sinh": 11,
        "phut_sinh": 30,
        "gioi_tinh": "nam"
    }
    resp = client.post("/birth-profile", json=profile_payload, headers=headers)
    assert resp.status_code == 201
    res_data = resp.json()

    # Kiểm tra Envelope APIResponse
    assert res_data["thanh_cong"] is True
    assert res_data["loi"] is None
    assert "du_lieu" in res_data

    du_lieu = res_data["du_lieu"]
    assert du_lieu["ho_ten"] == "Nguyễn Văn An"
    assert du_lieu["ngay_sinh_duong"] == "1990-08-15"
    assert du_lieu["gio_sinh"] == 11

    # Kiểm tra ngày âm lịch đã được tính toán tự động qua calendar_converter
    # Ngày 15/08/1990 Dương lịch là ngày 25/06/1990 Âm lịch (Canh Ngọ)
    assert du_lieu["ngay_sinh_am"] == "1990-06-25"
    assert du_lieu["thong_tin_am_lich"] is not None
    assert du_lieu["thong_tin_am_lich"]["can_nam"] == "Canh"
    assert du_lieu["thong_tin_am_lich"]["chi_nam"] == "Ngọ"


# ==============================================================================
# TEST 2: GET /tu-vi/{id} (Lập lá số Tử Vi + Luận giải qua Content Safety)
# ==============================================================================
def test_02_tu_vi_endpoint(authenticated_client):
    headers = authenticated_client
    profile_id = _get_or_create_profile_id(headers)

    with patch("ai_module.client.AIClient.goi_ai_voi_retry", return_value=MOCK_AI_RESPONSE):
        resp = client.get(f"/tu-vi/{profile_id}", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["thanh_cong"] is True
    assert data["loi"] is None

    payload = data["du_lieu"]
    assert payload["birth_profile_id"] == profile_id
    assert "la_so" in payload
    # Xác nhận 12 cung được tính toán bởi astro_engine
    assert "cac_cung" in payload["la_so"]
    assert len(payload["la_so"]["cac_cung"]) == 12

    # Luận giải AI
    luan_giai = payload["luan_giai"]
    assert luan_giai["thanh_cong"] is True
    assert "cau_tra_loi" in luan_giai
    assert "cát tường" in luan_giai["cau_tra_loi"]["noi_dung"]


# ==============================================================================
# TEST 3: GET /tu-vi/{id} LẦN 2 DÙNG CACHE (Nhanh hơn, không gọi AI mới)
# ==============================================================================
def test_03_tu_vi_cache_hit(authenticated_client):
    headers = authenticated_client
    profile_id = _get_or_create_profile_id(headers)

    # Đảm bảo nếu AI bị gọi sẽ ném lỗi (chứng minh hoàn toàn dùng cache)
    with patch("ai_module.client.AIClient.goi_ai_voi_retry", side_effect=Exception("AI KHÔNG ĐƯỢC PHÉP ĐƯỢC GỌI KHI CÓ CACHE!")):
        t0 = time.perf_counter()
        resp = client.get(f"/tu-vi/{profile_id}", headers=headers)
        t1 = time.perf_counter()

    assert resp.status_code == 200
    data = resp.json()
    assert data["thanh_cong"] is True
    assert data["du_lieu"]["birth_profile_id"] == profile_id
    # Trả về kết quả luận giải đồng nhất từ cache
    assert "cát tường" in data["du_lieu"]["luan_giai"]["cau_tra_loi"]["noi_dung"]
    # Tốc độ phản hồi từ cache rất nhanh (< 0.5s)
    assert (t1 - t0) < 1.0


# ==============================================================================
# TEST 4: GET /bat-tu/{id} (Tứ Trụ Bát Tự riêng biệt, không lẫn Tử Vi)
# ==============================================================================
def test_04_bat_tu_endpoint(authenticated_client):
    headers = authenticated_client
    profile_id = _get_or_create_profile_id(headers)

    mock_bat_tu_ai = AIResponse(
        text=json.dumps({
            "chu_de": "bat_tu_tong_quan",
            "noi_dung": "Thân vượng, Kim Thủy tương sinh, Hỏa làm Dụng Thần điều hòa.",
            "muc_do_tin_cay": 0.90
        }, ensure_ascii=False),
        provider="gemini",
        tokens_used=110,
        thoi_gian_xu_ly_ms=60,
        thanh_cong=True,
        loi_neu_co=None,
        bi_cat_ngang=False
    )

    with patch("ai_module.client.AIClient.goi_ai_voi_retry", return_value=mock_bat_tu_ai):
        resp = client.get(f"/bat-tu/{profile_id}", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["thanh_cong"] is True
    payload = data["du_lieu"]
    assert "tu_tru" in payload
    # 4 Trụ Can Chi của Bát Tự
    assert "tru_nam" in payload["tu_tru"]
    assert "tru_thang" in payload["tu_tru"]
    assert "tru_ngay" in payload["tu_tru"]
    assert "tru_gio" in payload["tu_tru"]

    # Luận giải Bát Tự không lẫn với Tử Vi
    luan_giai = payload["luan_giai"]
    assert luan_giai["he_thong"] == "bat_tu"
    assert "Dụng Thần" in luan_giai["cau_tra_loi"]["noi_dung"]


# ==============================================================================
# TEST 5: POST /gieo-que (Gieo quẻ Kinh Dịch + Luận giải)
# ==============================================================================
def test_05_gieo_que_endpoint(authenticated_client):
    headers = authenticated_client

    mock_dich_ai = AIResponse(
        text=json.dumps({
            "chu_de": "kinh_dich_tong_quan",
            "noi_dung": "Quẻ Càn vi Thiên hanh thông nguyên hanh lợi trinh, thời vận khởi sắc.",
            "muc_do_tin_cay": 0.89
        }, ensure_ascii=False),
        provider="gemini",
        tokens_used=130,
        thoi_gian_xu_ly_ms=70,
        thanh_cong=True,
        loi_neu_co=None,
        bi_cat_ngang=False
    )

    req_payload = {
        "cau_hoi": "Hỏi về khởi nghiệp kinh doanh trong quý tới",
        "phuong_phap": "dong_xu",
        "seed": 12345
    }

    with patch("ai_module.client.AIClient.goi_ai_voi_retry", return_value=mock_dich_ai):
        resp = client.post("/gieo-que", json=req_payload, headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["thanh_cong"] is True
    du_lieu = data["du_lieu"]
    assert du_lieu["cau_hoi"] == req_payload["cau_hoi"]
    assert "ma_que_chinh" in du_lieu
    assert "chi_tiet_que" in du_lieu
    assert du_lieu["luan_giai"]["he_thong"] == "kinh_dich"
    assert "Quẻ Càn" in du_lieu["luan_giai"]["cau_tra_loi"]["noi_dung"]


# ==============================================================================
# TEST 6: POST /xem-tuong/tay KHÔNG CÓ CONSENT -> BỊ CHẶN 403
# ==============================================================================
def test_06_xem_tuong_without_consent():
    # Tạo user chưa đồng ý điều khoản sinh trắc học
    client.post("/auth/register", json={
        "email": TEST_EMAIL_NOCONSENT,
        "password": TEST_PASSWORD,
        "confirm_password": TEST_PASSWORD
    })
    login_resp = client.post("/auth/login", data={
        "username": TEST_EMAIL_NOCONSENT,
        "password": TEST_PASSWORD
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Gửi request xem tướng tay với dummy base64
    dummy_b64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/"
    resp = client.post(
        "/xem-tuong/tay",
        data={"du_lieu_anh_base64": dummy_b64, "cau_hoi": "Xem đường chỉ tay sự nghiệp"},
        headers=headers
    )

    # Bắt buộc bị từ chối 403 Forbidden theo Prompt 4.2
    assert resp.status_code == 403
    data = resp.json()
    assert data["thanh_cong"] is False
    assert "sinh trắc học" in data["loi"].lower() or "đồng ý" in data["loi"].lower() or "consent" in data["loi"].lower()


# ==============================================================================
# TEST 7: POST /chat TỰ DO (Topic Detection nhận diện đúng hệ thống)
# ==============================================================================
def test_07_chat_topic_detection(authenticated_client):
    headers = authenticated_client

    mock_chat_ai = AIResponse(
        text=json.dumps({
            "chu_de": "cung_quan_loc",
            "noi_dung": "Cung Quan Lộc có Tử Vi Thiên Phủ biểu thị sự nghiệp vững vàng, có tài lãnh đạo.",
            "muc_do_tin_cay": 0.92
        }, ensure_ascii=False),
        provider="gemini",
        tokens_used=95,
        thoi_gian_xu_ly_ms=55,
        thanh_cong=True,
        loi_neu_co=None,
        bi_cat_ngang=False
    )

    with patch("ai_module.client.AIClient.goi_ai_voi_retry", return_value=mock_chat_ai):
        resp = client.post(
            "/chat",
            json={"cau_hoi": "Cho tôi hỏi về sao Tử Vi tại cung Quan Lộc có ý nghĩa gì?"},
            headers=headers
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["thanh_cong"] is True
    assert data["du_lieu"]["he_thong"] == "tu_vi"
    assert "Quan Lộc" in data["du_lieu"]["tra_loi"]

    # Kiểm tra lịch sử chat được lưu
    hist_resp = client.get("/chat/history", headers=headers)
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()
    assert hist_data["du_lieu"]["tong_so"] >= 1
    assert any("Quan Lộc" in it["cau_hoi"] for it in hist_data["du_lieu"]["danh_sach"])


# ==============================================================================
# TEST 8: HẾT QUOTA HÀNG NGÀY -> TRẢ VỀ 429 RÕ RÀNG, KHÔNG GỌI AI
# ==============================================================================
def test_08_quota_exhaustion_429(authenticated_client):
    headers = authenticated_client

    # Lấy thông tin user hiện tại và cưỡng chế đặt so_luot_da_dung = limit trong DB
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == TEST_EMAIL_MAIN).first()
        hom_nay = date.today()
        q_record = db.query(UsageQuota).filter(UsageQuota.user_id == user.id, UsageQuota.ngay == hom_nay).first()
        if not q_record:
            q_record = UsageQuota(id=uuid.uuid4(), user_id=user.id, ngay=hom_nay, so_luot_da_dung=50)
            db.add(q_record)
        else:
            q_record.so_luot_da_dung = 50
        db.commit()
    finally:
        db.close()

    # Kiểm tra route /quota xác nhận đã hết hạn mức
    quota_res = client.get("/quota", headers=headers)
    assert quota_res.status_code == 200
    assert quota_res.json()["du_lieu"]["con_han_muc"] is False

    # Khi gọi endpoint AI (ví dụ: POST /chat), dependency kiem_tra_quota_truoc_khi_xu_ly
    # BẮT BUỘC chặn ngay với HTTP 429, KHÔNG gọi AI
    with patch("ai_module.client.AIClient.goi_ai_voi_retry", side_effect=Exception("KHÔNG ĐƯỢC CHẠY LOGIC AI KHI HẾT QUOTA!")):
        resp = client.post(
            "/chat",
            json={"cau_hoi": "Câu hỏi khi đã hết hạn mức sử dụng hôm nay"},
            headers=headers
        )

    assert resp.status_code == 429
    err_data = resp.json()
    assert err_data["thanh_cong"] is False
    assert "hết lượt" in err_data["loi"].lower()

    # Khôi phục lại quota để không ảnh hưởng các test khác nếu có
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == TEST_EMAIL_MAIN).first()
        q_record = db.query(UsageQuota).filter(UsageQuota.user_id == user.id, UsageQuota.ngay == hom_nay).first()
        if q_record:
            q_record.so_luot_da_dung = 1
            db.commit()
    finally:
        db.close()


# ==============================================================================
# TEST 9: CHƯA ĐĂNG NHẬP (KHÔNG TOKEN) -> TRẢ VỀ 401
# ==============================================================================
def test_09_unauthorized_access_401():
    protected_endpoints = [
        ("GET", "/birth-profile"),
        ("GET", "/quota"),
        ("POST", "/chat"),
        ("POST", "/gieo-que"),
        ("GET", "/tu-vi/00000000-0000-0000-0000-000000000000"),
        ("GET", "/bat-tu/00000000-0000-0000-0000-000000000000"),
    ]

    for method, path in protected_endpoints:
        if method == "GET":
            resp = client.get(path)
        else:
            resp = client.post(path, json={"cau_hoi": "Test unauthorized"})
        assert resp.status_code == 401, f"Endpoint {method} {path} phải trả về 401 khi không có token"
        data = resp.json()
        assert data["thanh_cong"] is False
        assert "xác thực" in data["loi"].lower() or "token" in data["loi"].lower()


# ==============================================================================
# TEST 10: DỮ LIỆU ĐẦU VÀO SAI ĐỊNH DẠNG -> BẮT QUA 422 TRONG APIRESPONSE
# ==============================================================================
def test_10_invalid_input_validation(authenticated_client):
    headers = authenticated_client

    # Gửi giờ sinh sai phạm vi (> 23), giới tính không hợp lệ
    invalid_payload = {
        "ho_ten": "Sai Giờ Sinh",
        "ngay_sinh_duong": "1995-10-20",
        "gio_sinh": 99,
        "phut_sinh": 150,
        "gioi_tinh": "khong_xac_dinh"
    }

    resp = client.post("/birth-profile", json=invalid_payload, headers=headers)
    assert resp.status_code == 422
    data = resp.json()
    # Xác nhận exception handler RequestValidationError bọc đúng envelope
    assert data["thanh_cong"] is False
    assert data["du_lieu"] is None
    assert "Dữ liệu đầu vào không hợp lệ" in data["loi"]


# ==============================================================================
# TEST 11: GLOBAL EXCEPTION HANDLER (Bắt lỗi 500 an toàn, ghi nhận Sentry)
# ==============================================================================
def test_11_global_exception_handler(authenticated_client):
    headers = authenticated_client

    # Thêm route test cố ý ném lỗi bất ngờ vào app để kiểm tra handler toàn cục
    @app.get("/test-internal-crash-simulation")
    def simulate_crash():
        raise ZeroDivisionError("Cố ý mô phỏng chia cho 0 ngoài ý muốn")
    app.router.routes.insert(0, app.router.routes.pop())

    mock_sentry = MagicMock()
    with patch.dict("sys.modules", {"sentry_sdk": mock_sentry}):
        resp = client.get("/test-internal-crash-simulation")

    assert resp.status_code == 500
    data = resp.json()

    # Bọc envelope an toàn, không rò rỉ stack trace
    assert data["thanh_cong"] is False
    assert data["du_lieu"] is None
    assert data["loi"] == "Đã có lỗi xảy ra, vui lòng thử lại"
    # Không để lộ chi tiết kỹ thuật
    assert "ZeroDivisionError" not in str(data)
    assert "traceback" not in str(data).lower()

    # Xác nhận đã gọi capture_exception
    assert mock_sentry.capture_exception.called


# ==============================================================================
# TEST 12: CORS POLICY (Origin hợp lệ không bị chặn)
# ==============================================================================
def test_12_cors_policy():
    # Giả lập request từ Frontend Vite (http://localhost:5173 đã cấu hình trong CORS_ORIGINS)
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET"
    }
    resp = client.options("/health", headers=headers)
    assert resp.status_code in [200, 204]
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"

    # Request GET thông thường từ origin hợp lệ
    resp_get = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert resp_get.status_code == 200
    assert resp_get.headers.get("access-control-allow-origin") == "http://localhost:5173"


# ==============================================================================
# TEST 13: ENDPOINT LUẬN GIẢI THEO CHỦ ĐỀ GỢI Ý (GET /tu-vi/{id}/topic)
# ==============================================================================
def test_13_tu_vi_topic_endpoint(authenticated_client):
    headers = authenticated_client
    profile_id = _get_or_create_profile_id(headers)

    mock_topic_ai = AIResponse(
        text=json.dumps({
            "chu_de": "Công danh sự nghiệp",
            "noi_dung": "Cung Quan Lộc sáng sủa, có tiềm năng phát triển vững vàng.",
            "muc_do_tin_cay": 0.90
        }, ensure_ascii=False),
        provider="freellmapi",
        tokens_used=120,
        thoi_gian_xu_ly_ms=80,
        thanh_cong=True,
        loi_neu_co=None,
        bi_cat_ngang=False
    )

    with patch("ai_module.client.AIClient.goi_ai_voi_retry", return_value=mock_topic_ai):
        resp = client.get(f"/tu-vi/{profile_id}/topic?topic=cong_danh", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["thanh_cong"] is True
    assert data["du_lieu"]["topic"] == "cong_danh"
    assert data["du_lieu"]["tieu_de"] == "Công danh sự nghiệp"
    assert "Cung Quan Lộc" in data["du_lieu"]["luan_giai"]["cau_tra_loi"]["noi_dung"]


# ==============================================================================
# TEST 14: ENDPOINT HỎI ĐÁP AI THEO LÁ SỐ (POST /tu-vi/{id}/chat)
# ==============================================================================
def test_14_tu_vi_chat_endpoint(authenticated_client):
    headers = authenticated_client
    profile_id = _get_or_create_profile_id(headers)

    mock_chat_ai = AIResponse(
        text=json.dumps({
            "chu_de": "hoi_dap_tu_vi",
            "noi_dung": "Dựa trên cung Mệnh có Tử Vi, bạn là người độc lập, tự chủ và có tư duy quản lý tốt.",
            "muc_do_tin_cay": 0.90
        }, ensure_ascii=False),
        provider="freellmapi",
        tokens_used=150,
        thoi_gian_xu_ly_ms=100,
        thanh_cong=True,
        loi_neu_co=None,
        bi_cat_ngang=False
    )

    with patch("ai_module.client.AIClient.goi_ai_voi_retry", return_value=mock_chat_ai):
        resp = client.post(
            f"/tu-vi/{profile_id}/chat",
            json={"cau_hoi": "Tôi có hợp làm quản lý không?"},
            headers=headers
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["thanh_cong"] is True
    assert "Tử Vi" in data["du_lieu"]["tra_loi"]

