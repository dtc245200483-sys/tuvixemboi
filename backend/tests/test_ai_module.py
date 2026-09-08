# -*- coding: utf-8 -*-
"""
B? 8 Test Cases ki?m th? to?n di?n AI Module & AIClient:
1. G?i goi_ai_voi_retry v?i prompt h?p l? -> AIResponse thanh_cong = True, c? text.
2. M? ph?ng l?i l?n 1, th?nh c?ng l?n 2 -> retry ho?t ??ng, thanh_cong = True.
3. M? ph?ng l?i c? 3 l?n -> thanh_cong = False, c? m? t? l?i, KH?NG crash.
4. Test exponential backoff -> th?i gian ch? gi?a c?c l?n retry t?ng d?n (1s, 2s, 4s).
5. Test chuyen_doi_provider -> ??i sang DeepSeek, l?n g?i sau d?ng DeepSeek.
6. Test response b? c?t do max_tokens -> bi_cat_ngang = True.
7. Test log b?o m?t -> ch? ghi metadata, KH?NG log prompt/response nh?y c?m.
8. Test c?u h?nh -> AIClient kh?i t?o ??ng provider m?c ??nh t? settings.ai_provider.
"""

import logging
from unittest.mock import MagicMock, patch
import pytest

from config import settings
from ai_module.schemas import AIRequest, AIResponse
from ai_module.base_provider import BaseAIProvider
from ai_module.client import AIClient


class MockProvider(BaseAIProvider):
    """Mock Provider linh ho?t ?? ki?m th? c?c k?ch b?n."""
    def __init__(self, name: str = "mock_provider"):
        self._name = name
        self.call_count = 0
        self.behavior = "success"  # 'success', 'fail_then_succeed', 'always_fail', 'truncated'

    @property
    def provider_name(self) -> str:
        return self._name

    def goi_ai(self, request: AIRequest) -> AIResponse:
        self.call_count += 1
        if self.behavior == "success":
            return AIResponse(
                text=f"Ph?n h?i m?u cho: {request.prompt}",
                provider=self.provider_name,
                tokens_used=120,
                thoi_gian_xu_ly_ms=150,
                thanh_cong=True,
                bi_cat_ngang=False
            )
        elif self.behavior == "fail_then_succeed":
            if self.call_count == 1:
                return AIResponse(
                    text="",
                    provider=self.provider_name,
                    tokens_used=0,
                    thoi_gian_xu_ly_ms=5000,
                    thanh_cong=False,
                    loi_neu_co="Timeout khi k?t n?i AI API l?n 1"
                )
            else:
                return AIResponse(
                    text="Ph?n h?i th?nh c?ng ? l?n retry th? 2",
                    provider=self.provider_name,
                    tokens_used=140,
                    thoi_gian_xu_ly_ms=200,
                    thanh_cong=True
                )
        elif self.behavior == "always_fail":
            return AIResponse(
                text="",
                provider=self.provider_name,
                tokens_used=0,
                thoi_gian_xu_ly_ms=1000,
                thanh_cong=False,
                loi_neu_co=f"L?i h? th?ng li?n t?c ? l?n g?i {self.call_count}"
            )
        elif self.behavior == "truncated":
            return AIResponse(
                text="Ph?n h?i b? c?t gi?a ch?ng...",
                provider=self.provider_name,
                tokens_used=request.max_tokens,
                thoi_gian_xu_ly_ms=300,
                thanh_cong=True,
                bi_cat_ngang=True
            )
        return AIResponse(text="", provider=self.provider_name, tokens_used=0, thoi_gian_xu_ly_ms=0, thanh_cong=False)


def test_1_goi_ai_hop_le_thanh_cong():
    """Test 1: G?i goi_ai_voi_retry v?i prompt ??n gi?n, h?p l? -> thanh_cong = True, c? text."""
    mock_gemini = MockProvider(name="gemini")
    mock_gemini.behavior = "success"
    client = AIClient(gemini_provider=mock_gemini)

    req = AIRequest(prompt="Ph?n t?ch ? ngh?a sao T? Vi t?i cung M?nh")
    resp = client.goi_ai_voi_retry(req)

    assert resp.thanh_cong is True
    assert len(resp.text) > 0
    assert resp.provider == "gemini"
    assert resp.tokens_used == 120
    assert resp.bi_cat_ngang is False
    assert mock_gemini.call_count == 1


def test_2_retry_khi_loi_lan_dau_thanh_cong_lan_hai():
    """Test 2: M? ph?ng l?i timeout ? l?n 1, th?nh c?ng ? l?n 2 -> retry ho?t ??ng ??ng."""
    mock_gemini = MockProvider(name="gemini")
    mock_gemini.behavior = "fail_then_succeed"
    client = AIClient(gemini_provider=mock_gemini)

    slept_times = []
    def fake_sleep(seconds: float):
        slept_times.append(seconds)

    req = AIRequest(prompt="Xin ch?o AI")
    resp = client.goi_ai_voi_retry(req, so_lan_thu_lai=3, sleeper=fake_sleep)

    assert resp.thanh_cong is True
    assert "th?nh c?ng ? l?n retry th? 2" in resp.text
    assert mock_gemini.call_count == 2
    assert len(slept_times) == 1  # Ch? sleep 1 l?n sau l?n th? th? 1 th?t b?i


def test_3_loi_lien_tuc_tra_ve_thanh_cong_false_khong_crash():
    """Test 3: M? ph?ng l?i c? 3 l?n th? -> tr? v? thanh_cong = False, kh?ng crash."""
    mock_gemini = MockProvider(name="gemini")
    mock_gemini.behavior = "always_fail"
    client = AIClient(gemini_provider=mock_gemini)

    slept_times = []
    def fake_sleep(seconds: float):
        slept_times.append(seconds)

    req = AIRequest(prompt="Y?u c?u b? l?i")
    resp = client.goi_ai_voi_retry(req, so_lan_thu_lai=3, sleeper=fake_sleep)

    assert resp.thanh_cong is False
    assert resp.loi_neu_co is not None
    assert "L?i h? th?ng li?n t?c" in resp.loi_neu_co
    assert mock_gemini.call_count == 3
    assert len(slept_times) == 2  # Sleep sau l?n 1 v? sau l?n 2


def test_4_exponential_backoff_tang_dan():
    """Test 4: X?c nh?n th?i gian ch? gi?a c?c l?n retry t?ng d?n ??ng thi?t k? (1s, 2s, 4s)."""
    mock_gemini = MockProvider(name="gemini")
    mock_gemini.behavior = "always_fail"
    client = AIClient(gemini_provider=mock_gemini)

    wait_durations = []
    def record_sleep(seconds: float):
        wait_durations.append(seconds)

    req = AIRequest(prompt="Test backoff")
    client.goi_ai_voi_retry(
        req,
        so_lan_thu_lai=4,
        initial_backoff=1.0,
        backoff_factor=2.0,
        sleeper=record_sleep
    )

    # Ch? sau l?n 1 (1.0s), sau l?n 2 (2.0s), sau l?n 3 (4.0s)
    assert len(wait_durations) == 3
    assert wait_durations[0] == pytest.approx(1.0)
    assert wait_durations[1] == pytest.approx(2.0)
    assert wait_durations[2] == pytest.approx(4.0)
    assert wait_durations[1] > wait_durations[0]
    assert wait_durations[2] > wait_durations[1]


def test_5_chuyen_doi_provider():
    """Test 5: ??i t? Gemini sang DeepSeek -> l?n g?i ti?p theo d?ng ??ng DeepSeek."""
    mock_gemini = MockProvider(name="gemini")
    mock_deepseek = MockProvider(name="deepseek")
    client = AIClient(
        default_provider="gemini",
        gemini_provider=mock_gemini,
        deepseek_provider=mock_deepseek
    )

    assert client.current_provider_name == "gemini"

    # Chuy?n ??i provider
    client.chuyen_doi_provider("deepseek")
    assert client.current_provider_name == "deepseek"

    req = AIRequest(prompt="C?u h?i cho DeepSeek")
    resp = client.goi_ai_voi_retry(req)

    assert resp.provider == "deepseek"
    assert mock_deepseek.call_count == 1
    assert mock_gemini.call_count == 0


def test_6_response_bi_cat_do_max_tokens():
    """Test 6: M? ph?ng response c? flag c?t gi?a ch?ng -> AIResponse.bi_cat_ngang = True."""
    mock_gemini = MockProvider(name="gemini")
    mock_gemini.behavior = "truncated"
    client = AIClient(gemini_provider=mock_gemini)

    req = AIRequest(prompt="B?i lu?n d?i", max_tokens=500)
    resp = client.goi_ai_voi_retry(req)

    assert resp.thanh_cong is True
    assert resp.bi_cat_ngang is True


def test_7_log_ghi_metadata_khong_lo_thong_tin_nhay_cam(caplog):
    """Test 7: Log ghi nh?n metadata (provider, token, th?i gian) nh?ng KH?NG ghi prompt/response nh?y c?m."""
    mock_gemini = MockProvider(name="gemini")
    mock_gemini.behavior = "success"
    client = AIClient(gemini_provider=mock_gemini)

    sensitive_prompt = "Ng??i sinh ng?y 15/08/1990 l?c 14h30 t?i H? N?i c? l? s? th? n?o"
    req = AIRequest(prompt=sensitive_prompt)

    with caplog.at_level(logging.INFO):
        client.goi_ai_voi_retry(req)

    captured_text = caplog.text
    # 1. Metadata k? thu?t ph?i xu?t hi?n
    assert "Provider=gemini" in captured_text
    assert "Tokens=120" in captured_text
    assert "Th?i gian=150ms" in captured_text
    assert "Tr?ng th?i=TH?NH C?NG" in captured_text

    # 2. To?n b? n?i dung c?u h?i ch?a th?ng tin c? nh?n nh?y c?m TUY?T ??I KH?NG xu?t hi?n trong log
    assert sensitive_prompt not in captured_text
    assert "15/08/1990" not in captured_text


def test_8_khoi_tao_provider_mac_dinh_theo_config():
    """Test 8: AIClient kh?i t?o ??ng provider m?c ??nh d?a theo settings.ai_provider."""
    with patch.object(settings, "ai_provider", "deepseek"):
        client = AIClient()
        assert client.current_provider_name == "deepseek"

    with patch.object(settings, "ai_provider", "gemini"):
        client = AIClient()
        assert client.current_provider_name == "gemini"

    with patch.object(settings, "ai_provider", "freellmapi"):
        client = AIClient()
        assert client.current_provider_name == "freellmapi"


def test_9_freellm_provider_key_decryption_and_rotation():
    """Test 9: Ki?m tra FreeLLMProvider n?p key t? database v? lu?n chuy?n key th?nh c?ng."""
    from ai_module.providers.freellm_provider import FreeLLMProvider
    provider = FreeLLMProvider()
    # Phải nạp được ít nhất 1 key từ freeapi.db
    assert len(provider._keys_pool) >= 1
    # Kiểm tra key mask
    masked = provider._mask_key(provider._keys_pool[0])
    assert masked.startswith("gsk_") or masked.startswith("***")
    assert "..." in masked

    # Kiểm tra round-robin luân chuyển key
    key1 = provider._get_next_key()
    assert key1 is not None

