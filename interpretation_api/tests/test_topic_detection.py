# -*- coding: utf-8 -*-
"""
Bộ 10 Test Cases kiểm thử toàn diện Topic Detection Module:
1. Câu hỏi rõ ràng Tử Vi -> Rule-based nhận diện đúng, không gọi AI.
2. Câu hỏi rõ ràng Bát Tự -> Rule-based nhận diện đúng.
3. Câu hỏi rõ ràng Kinh Dịch -> Rule-based nhận diện đúng.
4. Câu hỏi mơ hồ -> Rule-based trả None, chuyển sang AI classifier.
5. co_dinh_kem_anh = True -> Nhân Tướng Học ngay không cần phân loại thêm.
6. Câu hỏi không rõ ngay cả với AI -> trả về can_hoi_lai = True kèm gợi ý câu hỏi.
7. Hệ thống chưa có dữ liệu train (dem_so_luong = 0) -> chua_co_du_lieu = True.
8. Câu hỏi có ngữ cảnh lich_su_chat -> AI suy luận dựa vào lịch sử chat.
9. Test hiệu năng: rule-based < 50ms so với gọi AI.
10. Câu hỏi chứa từ khóa xung đột nhiều hệ thống -> Rule-based coi là mơ hồ, chuyển AI phân xử.
"""

import time
import json
from unittest.mock import MagicMock, patch
import pytest

from interpretation_api.topic_detection.keywords import KEYWORDS
from interpretation_api.topic_detection.rule_based import phat_hien_theo_tu_khoa
from interpretation_api.topic_detection.ai_classifier import phan_loai_bang_ai
from interpretation_api.topic_detection.detector import xac_dinh_he_thong
from ai_module.schemas import AIResponse


class MockAIClient:
    """Mock AI Client linh hoạt cho test topic detection."""
    def __init__(self, return_system: str = "tu_vi", confidence: float = 0.9):
        self.return_system = return_system
        self.confidence = confidence
        self.called_with_prompt = None
        self.call_count = 0

    def goi_ai_voi_retry(self, request, **kwargs):
        self.call_count += 1
        self.called_with_prompt = request.prompt
        resp_json = json.dumps({
            "he_thong": self.return_system,
            "do_tin_cay": self.confidence,
            "ly_do_ngan_gon": f"Mocked classification as {self.return_system}"
        })
        return AIResponse(
            text=resp_json,
            provider="mock_gemini",
            tokens_used=45,
            thoi_gian_xu_ly_ms=80,
            thanh_cong=True
        )


def test_1_cau_hoi_ro_rang_tu_vi():
    """Test 1: Câu hỏi rõ ràng về Tử Vi -> phat_hien_theo_tu_khoa nhận diện đúng, không gọi AI."""
    query = "Lá số có cung Mệnh tại Dần gặp sao Tử Vi và Thất Sát"
    detected = phat_hien_theo_tu_khoa(query)
    assert detected == "tu_vi"

    mock_ai = MockAIClient()
    res = xac_dinh_he_thong(query, ai_client=mock_ai, check_kb_data=False)
    assert res["he_thong"] == "tu_vi"
    assert res["phuong_phap"] == "rule_based"
    assert res["can_hoi_lai"] is False
    assert mock_ai.call_count == 0  # Tuyệt đối không cần gọi AI


def test_2_cau_hoi_ro_rang_bat_tu():
    """Test 2: Câu hỏi rõ ràng về Bát Tự -> nhận diện đúng bat_tu."""
    query = "Tìm dụng thần và hỷ thần theo can chi tứ trụ"
    detected = phat_hien_theo_tu_khoa(query)
    assert detected == "bat_tu"

    res = xac_dinh_he_thong(query, check_kb_data=False)
    assert res["he_thong"] == "bat_tu"
    assert res["phuong_phap"] == "rule_based"


def test_3_cau_hoi_ro_rang_kinh_dich():
    """Test 3: Câu hỏi rõ ràng về Kinh Dịch -> nhận diện đúng kinh_dich."""
    query = "Gieo quẻ hỏi việc kinh doanh xuất hiện hào động tại hào 3"
    detected = phat_hien_theo_tu_khoa(query)
    assert detected == "kinh_dich"

    res = xac_dinh_he_thong(query, check_kb_data=False)
    assert res["he_thong"] == "kinh_dich"
    assert res["phuong_phap"] == "rule_based"


def test_4_cau_hoi_mo_ho_chuyen_sang_ai():
    """Test 4: Câu hỏi mơ hồ -> rule-based trả None, chuyển sang AI classification."""
    query = "Tôi có nên đầu tư bất động sản trong năm nay không?"
    detected = phat_hien_theo_tu_khoa(query)
    assert detected is None  # Không có từ khóa huyền học cụ thể

    mock_ai = MockAIClient(return_system="tu_vi", confidence=0.75)
    res = xac_dinh_he_thong(query, ai_client=mock_ai, check_kb_data=False)

    assert res["he_thong"] == "tu_vi"
    assert res["phuong_phap"] == "ai_classification"
    assert mock_ai.call_count == 1


def test_5_co_dinh_kem_anh_tra_ve_ngay_nhan_tuong():
    """Test 5: co_dinh_kem_anh = True -> trả về ngay nhan_tuong không qua bước phân loại khác."""
    mock_ai = MockAIClient()
    res = xac_dinh_he_thong(
        cau_hoi="Xem giúp tôi với",
        co_dinh_kem_anh=True,
        ai_client=mock_ai,
        check_kb_data=False
    )
    assert res["he_thong"] == "nhan_tuong"
    assert res["phuong_phap"] == "dinh_kem_anh"
    assert res["do_tin_cay"] == 1.0
    assert mock_ai.call_count == 0


def test_6_cau_hoi_khong_xac_dinh_duoc_can_hoi_lai():
    """Test 6: Câu hỏi thực sự không rõ (AI trả về khong_ro) -> trả về can_hoi_lai = True kèm gợi ý."""
    mock_ai = MockAIClient(return_system="khong_ro", confidence=0.0)
    res = xac_dinh_he_thong(
        cau_hoi="Hôm nay thời tiết thế nào?",
        ai_client=mock_ai,
        check_kb_data=False
    )
    assert res["he_thong"] is None
    assert res["can_hoi_lai"] is True
    assert "Dạ bạn muốn tra cứu vận mệnh theo Tử Vi" in res["goi_y_cau_hoi"]


def test_7_he_thong_chua_co_du_lieu_train():
    """Test 7: Hệ thống chưa có dữ liệu train (dem_so_luong = 0) -> chua_co_du_lieu = True."""
    query = "Xem lá số cung Mệnh Tử Vi"
    with patch("interpretation_api.topic_detection.detector.dem_so_luong", return_value=0):
        res = xac_dinh_he_thong(query, check_kb_data=True)
        assert res["he_thong"] == "tu_vi"
        assert res["chua_co_du_lieu"] is True


def test_8_ngu_canh_phu_thuoc_lich_su_chat():
    """Test 8: Câu hỏi phụ thuộc lịch sử chat -> AI dùng lich_su_chat để suy ra vẫn thuộc Tử Vi."""
    lich_su = [
        {"role": "user", "content": "Xem giúp tôi lá số Tử Vi cung Mệnh có sao Thất Sát"},
        {"role": "assistant", "content": "Lá số của bạn cho thấy tính cách quyết đoán, dũng mãnh."}
    ]
    query_ngan = "Còn về sự nghiệp thì sao?"
    
    mock_ai = MockAIClient(return_system="tu_vi", confidence=0.88)
    res = xac_dinh_he_thong(
        cau_hoi=query_ngan,
        lich_su_chat=lich_su,
        ai_client=mock_ai,
        check_kb_data=False
    )
    assert res["he_thong"] == "tu_vi"
    assert 'Thất Sát' in mock_ai.called_with_prompt


def test_9_hieu_nang_rule_based_duoi_50ms():
    """Test 9: Đo thời gian xử lý rule-based -> dưới 50ms."""
    query = "Cung Quan Lộc có sao Thiên Cơ hóa khoa"
    t_start = time.perf_counter()
    res = xac_dinh_he_thong(query, check_kb_data=False)
    elapsed_ms = (time.perf_counter() - t_start) * 1000

    assert res["he_thong"] == "tu_vi"
    assert res["phuong_phap"] == "rule_based"
    assert elapsed_ms < 50.0, f"Thời gian rule-based quá chậm: {elapsed_ms:.2f}ms"


def test_10_tu_khoa_xung_dot_chuyen_sang_ai_phan_xu():
    """Test 10: Câu hỏi chứa từ khóa của nhiều hệ thống -> rule-based coi là mơ hồ, chuyển AI."""
    # Vừa có 'cung mệnh' (Tử Vi) vừa có 'gieo quẻ' (Kinh Dịch)
    query_conflict = "Tôi xem cung Mệnh thấy xấu quá, giờ gieo quẻ hỏi học hành được không?"
    detected = phat_hien_theo_tu_khoa(query_conflict)
    # Phải trả về None vì xung đột từ khóa
    assert detected is None

    mock_ai = MockAIClient(return_system="kinh_dich", confidence=0.85)
    res = xac_dinh_he_thong(query_conflict, ai_client=mock_ai, check_kb_data=False)
    assert res["he_thong"] == "kinh_dich"
    assert res["phuong_phap"] == "ai_classification"
    assert mock_ai.call_count == 1
