# -*- coding: utf-8 -*-
"""
Bộ 9 Test Cases kiểm thử toàn diện Interpretation Orchestrator:
1. Luồng đầy đủ câu hỏi Tử Vi + lá số hợp lệ -> JSON có cấu trúc, có nội dung luận giải.
2. Câu hỏi mơ hồ (can_hoi_lai = True) -> dừng đúng lúc, trả về gợi ý, KHÔNG gọi AI.
3. Hệ thống chưa có dữ liệu train -> thông báo rõ ràng, KHÔNG gọi AI.
4. Tra cứu Knowledge Base trả về rỗng -> prompt có lưu ý không có tri thức, response có ghi chú giới hạn.
5. AI trả JSON sai format lần 1, đúng lần 2 -> retry 1 lần thành công.
6. AI liên tục trả sai format sau 2 lần -> báo lỗi rõ ràng, không crash.
7. Test lay_lich_su_chat và luu_lich_su_chat với database SQLite in-memory.
8. Luồng cho cả 4 hệ thống (tu_vi, bat_tu, kinh_dich, nhan_tuong) -> mỗi bên dùng đúng template riêng.
9. Tính toàn vẹn nguồn: nguon_tri_thuc_da_dung khớp 100% với kết quả từ search().
"""

import uuid
import json
from unittest.mock import MagicMock, patch
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base
from db.models import User, ChatHistory
from interpretation_api.orchestrator.main_flow import luan_giai
from interpretation_api.orchestrator.chat_context import lay_lich_su_chat, luu_lich_su_chat
from ai_module.schemas import AIResponse

TEST_USER_ID = "11111111-1111-1111-1111-111111111111"
TEST_USER_UUID = uuid.UUID(TEST_USER_ID)


@pytest.fixture
def in_memory_db():
    """Khởi tạo SQLite in-memory database cho test chat context."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Tạo 1 user mẫu với UUID chuẩn
    user = User(
        id=TEST_USER_UUID,
        email="orch_test@example.com",
        password_hash="hashed_pw",
        is_active=True
    )
    session.add(user)
    session.commit()

    yield session
    session.close()


class MockAIClientOrchestrator:
    """Mock AI Client cho phép cấu hình các phản hồi khác nhau."""
    def __init__(self, responses=None):
        self.responses = responses or []
        self.call_count = 0
        self.prompts_received = []

    def goi_ai_voi_retry(self, request, **kwargs):
        self.call_count += 1
        self.prompts_received.append(request.prompt)
        if self.responses and self.call_count <= len(self.responses):
            text_resp = self.responses[self.call_count - 1]
        else:
            text_resp = json.dumps({
                "chu_de": "Luận giải mẫu",
                "noi_dung": "Nội dung luận giải thành công dựa trên tri thức tham chiếu.",
                "muc_do_tin_cay": 0.95
            })
        return AIResponse(
            text=text_resp,
            provider="mock_gemini",
            tokens_used=180,
            thoi_gian_xu_ly_ms=210,
            thanh_cong=True
        )


def test_1_luong_day_du_tu_vi(in_memory_db):
    """Test 1: Luồng đầy đủ với câu hỏi Tử Vi + lá số hợp lệ -> JSON kết quả có cấu trúc chuẩn."""
    la_so = {
        "id": "laso_001",
        "cung_menh": "Cung Mệnh tại Ngọ",
        "sao_chu_dao": "Tử Vi, Thiên Phủ",
        "cuc": "Đầu quân Hỏa Lục Cục"
    }
    cau_hoi = "Xem giúp tôi vận trình cung Mệnh có sao Tử Vi"

    mock_ai = MockAIClientOrchestrator()
    mock_tri_thuc = [{
        "id": "kb_tv_01",
        "ten": "Tử Vi Đế Tinh",
        "noi_dung_moi": "Tử Vi thuộc Âm Thổ, vương đế uy nghi, lãnh đạo phú quý.",
        "nguon_goc": "Tu Vi Toan Thu",
        "do_tin_cay": 0.98
    }]

    with patch("interpretation_api.orchestrator.main_flow.search", return_value=mock_tri_thuc):
        res = luan_giai(
            user_id=TEST_USER_ID,
            cau_hoi=cau_hoi,
            du_lieu_dau_vao=la_so,
            db=in_memory_db,
            ai_client=mock_ai
        )

    assert res["thanh_cong"] is True
    assert res["he_thong"] == "tu_vi"
    assert "noi_dung" in res["cau_tra_loi"]
    assert res["cau_tra_loi"]["muc_do_tin_cay"] == 0.95
    assert len(res["nguon_tri_thuc_da_dung"]) == 1
    assert res["nguon_tri_thuc_da_dung"][0]["ten"] == "Tử Vi Đế Tinh"


def test_2_cau_hoi_mo_ho_dung_dung_luc():
    """Test 2: Câu hỏi mơ hồ -> orchestrator dừng lại, trả về gợi ý, KHÔNG gọi AI luận giải."""
    mock_ai = MockAIClientOrchestrator()
    cau_hoi_mo_ho = "Hôm nay có điều gì vui không?"

    with patch("interpretation_api.orchestrator.main_flow.xac_dinh_he_thong") as mock_detect:
        mock_detect.return_value = {
            "he_thong": None,
            "can_hoi_lai": True,
            "goi_y_cau_hoi": "Bạn muốn xem theo Tử Vi hay Kinh Dịch?"
        }
        res = luan_giai(
            user_id=TEST_USER_ID,
            cau_hoi=cau_hoi_mo_ho,
            du_lieu_dau_vao={},
            ai_client=mock_ai
        )

    assert res["thanh_cong"] is False
    assert res["can_hoi_lai"] is True
    assert "Bạn muốn xem theo Tử Vi" in res["thong_bao"]
    assert mock_ai.call_count == 0  # Tiết kiệm gọi AI


def test_3_he_thong_chua_co_du_lieu_khong_goi_ai():
    """Test 3: Hệ thống chưa có dữ liệu huấn luyện -> thông báo rõ ràng, KHÔNG gọi AI."""
    mock_ai = MockAIClientOrchestrator()
    with patch("interpretation_api.orchestrator.main_flow.xac_dinh_he_thong") as mock_detect:
        mock_detect.return_value = {
            "he_thong": "nhan_tuong",
            "chua_co_du_lieu": True,
            "can_hoi_lai": False
        }
        res = luan_giai(
            user_id=TEST_USER_ID,
            cau_hoi="Xem tướng mặt",
            du_lieu_dau_vao={},
            ai_client=mock_ai
        )

    assert res["thanh_cong"] is False
    assert res["chua_co_du_lieu"] is True
    assert "hiện chưa có đủ dữ liệu" in res["thong_bao"]
    assert mock_ai.call_count == 0


def test_4_search_kb_rong_nhac_nho_than_trong():
    """Test 4: search() trả về rỗng -> prompt nhắc không có tri thức, kết quả có ghi chú giới hạn."""
    mock_ai = MockAIClientOrchestrator()
    with patch("interpretation_api.orchestrator.main_flow.search", return_value=[]):
        res = luan_giai(
            user_id=TEST_USER_ID,
            cau_hoi="Xem cung Mệnh Tử Vi",
            du_lieu_dau_vao={"sao_chu_dao": "Tử Vi"},
            ai_client=mock_ai
        )

    assert res["thanh_cong"] is True
    # Prompt gửi cho AI phải chứa lưu ý không có tri thức cụ thể
    assert "Hiện không có tri thức cụ thể" in mock_ai.prompts_received[0]
    # Phản hồi cuối phải có ghi chú giới hạn kiến thức
    assert "ghi_chu_gioi_han" in res["cau_tra_loi"]
    assert len(res["nguon_tri_thuc_da_dung"]) == 0


def test_5_ai_tra_sai_format_lan_1_retry_thanh_cong():
    """Test 5: AI trả sai format lần 1, orchestrator retry thành công ở lần 2."""
    mock_ai = MockAIClientOrchestrator(responses=[
        "Xin chào, tôi không trả về JSON đâu!",  # Lần 1 sai
        json.dumps({"chu_de": "Tử Vi", "noi_dung": "Thành công lần 2", "muc_do_tin_cay": 0.8})  # Lần 2 đúng
    ])

    with patch("interpretation_api.orchestrator.main_flow.search", return_value=[]):
        res = luan_giai(
            user_id=TEST_USER_ID,
            cau_hoi="Xem cung Mệnh Tử Vi",
            du_lieu_dau_vao={"sao_chu_dao": "Tử Vi"},
            ai_client=mock_ai
        )

    assert res["thanh_cong"] is True
    assert mock_ai.call_count == 2
    assert res["cau_tra_loi"]["noi_dung"] == "Thành công lần 2"


def test_6_ai_lien_tuc_tra_sai_format_bao_loi_khong_crash():
    """Test 6: AI liên tục trả sai format sau 2 lần -> báo lỗi rõ ràng, không crash."""
    mock_ai = MockAIClientOrchestrator(responses=[
        "Văn bản thuần lần 1",
        "Văn bản thuần lần 2 vẫn không phải JSON"
    ])

    with patch("interpretation_api.orchestrator.main_flow.search", return_value=[]):
        res = luan_giai(
            user_id=TEST_USER_ID,
            cau_hoi="Xem cung Mệnh Tử Vi",
            du_lieu_dau_vao={"sao_chu_dao": "Tử Vi"},
            ai_client=mock_ai
        )

    assert res["thanh_cong"] is False
    assert "sai định dạng kết quả sau 2 lần thử" in res["thong_bao"]
    assert mock_ai.call_count == 2


def test_7_lay_va_luu_lich_su_chat(in_memory_db):
    """Test 7: Test luu_lich_su_chat và lay_lich_su_chat theo trình tự thời gian."""
    uid = TEST_USER_UUID
    luu_lich_su_chat(uid, "tu_vi", "Câu hỏi 1", "Trả lời 1", db=in_memory_db)
    luu_lich_su_chat(uid, "tu_vi", "Câu hỏi 2", "Trả lời 2", db=in_memory_db)

    history = lay_lich_su_chat(uid, so_luong_gan_nhat=5, db=in_memory_db)
    assert len(history) == 4  # 2 cặp user - assistant
    assert history[0]["content"] == "Câu hỏi 1"
    assert history[1]["content"] == "Trả lời 1"
    assert history[2]["content"] == "Câu hỏi 2"
    assert history[3]["content"] == "Trả lời 2"


def test_8_luan_giai_4_he_thong_dung_dung_template():
    """Test 8: Kiểm thử cả 4 hệ thống -> mỗi hệ thống dùng đúng template chuyên biệt."""
    cases = [
        ("tu_vi", "Xem cung Mệnh sao Tử Vi", {"cung_menh": "Tí", "sao_chu_dao": "Tử Vi"}, "THÔNG TIN LÁ SỐ TỬ VI"),
        ("bat_tu", "Tìm dụng thần Bát Tự", {"nam": "Giáp Tý", "dung_than": "Hỏa"}, "THÔNG TIN TỨ TRỤ BÁT TỰ"),
        ("kinh_dich", "Gieo quẻ hào động Kinh Dịch", {"que_chinh": "Thuần Càn", "hao_dong": 2}, "THÔNG TIN QUẺ KINH DỊCH"),
        ("nhan_tuong", "Xem đường chỉ tay nhân tướng", {"duong_chi_tay": "Tâm đạo rõ nét"}, "ĐẶC ĐIỂM HÌNH THÁI QUAN SÁT")
    ]

    for sys_name, query, data, expected_header in cases:
        mock_ai = MockAIClientOrchestrator()
        with patch("interpretation_api.orchestrator.main_flow.search", return_value=[]):
            res = luan_giai(
                user_id=TEST_USER_ID,
                cau_hoi=query,
                du_lieu_dau_vao=data,
                ai_client=mock_ai
            )
            assert res["thanh_cong"] is True
            assert res["he_thong"] == sys_name
            # Template tương ứng đã được gửi đến AI
            assert expected_header in mock_ai.prompts_received[0]


def test_9_toan_ven_nguon_tri_thuc_da_dung():
    """Test 9: nguon_tri_thuc_da_dung khớp chính xác với các item mà search() đã tìm thấy."""
    mock_ai = MockAIClientOrchestrator()
    mock_kb_results = [
        {"id": "kb_01", "ten": "Quẻ Thuần Càn", "noi_dung_moi": "Cương kiện", "nguon_goc": "Kinh Dịch Ngô Tất Tố", "do_tin_cay": 0.98},
        {"id": "kb_02", "ten": "Hào Cửu Nhị", "noi_dung_moi": "Kiến long tại điền", "nguon_goc": "Kinh Dịch Ngô Tất Tố", "do_tin_cay": 0.98}
    ]

    with patch("interpretation_api.orchestrator.main_flow.search", return_value=mock_kb_results):
        res = luan_giai(
            user_id=TEST_USER_ID,
            cau_hoi="Gieo quẻ Thuần Càn hào 2 động",
            du_lieu_dau_vao={"que_chinh": "Thuần Càn"},
            ai_client=mock_ai
        )

    assert res["thanh_cong"] is True
    assert len(res["nguon_tri_thuc_da_dung"]) == 2
    assert res["nguon_tri_thuc_da_dung"][0]["id"] == "kb_01"
    assert res["nguon_tri_thuc_da_dung"][0]["ten"] == "Quẻ Thuần Càn"
    assert res["nguon_tri_thuc_da_dung"][1]["id"] == "kb_02"
    assert res["nguon_tri_thuc_da_dung"][1]["ten"] == "Hào Cửu Nhị"
