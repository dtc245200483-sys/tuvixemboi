# -*- coding: utf-8 -*-
"""
L?p AI Client ?i?u ph?i to?n b? c?c y?u c?u AI trong h? th?ng:
- H? tr? ch?n v? chuy?n ??i Provider (Gemini / DeepSeek).
- Retry pattern v?i Exponential Backoff t? ??ng khi g?p s? c? timeout/rate-limit.
- Tu?n th? nguy?n t?c b?o m?t d? li?u: CH? log metadata k? thu?t, KH?NG log prompt/response nh?y c?m.
"""

import time
import logging
from typing import Optional, Dict, Any, Callable

from config import settings
from ai_module.schemas import AIRequest, AIResponse
from ai_module.base_provider import BaseAIProvider
from ai_module.providers.gemini_provider import GeminiProvider
from ai_module.providers.deepseek_provider import DeepSeekProvider

logger = logging.getLogger("AIModuleClient")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


class AIClient:
    """Client trung t?m x? l? g?i AI th?ng nh?t."""

    def __init__(
        self,
        default_provider: Optional[str] = None,
        gemini_provider: Optional[BaseAIProvider] = None,
        deepseek_provider: Optional[BaseAIProvider] = None
    ):
        provider_name = (default_provider or getattr(settings, "ai_provider", "gemini") or "gemini").strip().lower()
        if provider_name not in ["gemini", "deepseek"]:
            provider_name = "gemini"

        self.current_provider_name = provider_name
        self.providers: Dict[str, BaseAIProvider] = {
            "gemini": gemini_provider or GeminiProvider(),
            "deepseek": deepseek_provider or DeepSeekProvider()
        }

    @property
    def current_provider(self) -> BaseAIProvider:
        """L?y provider hi?n ?ang ???c k?ch ho?t."""
        return self.providers.get(self.current_provider_name, self.providers["gemini"])

    def chuyen_doi_provider(self, provider_moi: str) -> None:
        """
        Chuy?n ??i provider ?ang s? d?ng (VD: 'gemini' <-> 'deepseek').
        H? tr? fallback khi m?t provider g?p s? c? k?o d?i.
        """
        p_name = provider_moi.strip().lower()
        if p_name not in self.providers:
            raise ValueError(f"Provider '{provider_moi}' kh?ng ???c h? tr?. Ch? h? tr?: {list(self.providers.keys())}")
        self.current_provider_name = p_name
        logger.info(f"[AI_CLIENT] ?? chuy?n ??i provider ho?t ??ng sang: '{self.current_provider_name}'")

    def _ghi_log_metadata(self, res: AIResponse, attempt: int) -> None:
        """
        Ghi log metadata cu?c g?i AI tu?n th? nguy?n t?c b?o m?t d? li?u:
        CH? ghi: provider, tokens_used, thoi_gian_xu_ly_ms, thanh_cong, loi (n?u c?).
        TUY?T ??I KH?NG ghi n?i dung c?u h?i (prompt) hay c?u tr? l?i (response text)
        v? c? th? ch?a th?ng tin sinh tr?c h?c/ng?y th?ng n?m sinh nh?y c?m.
        """
        status_str = "TH?NH C?NG" if res.thanh_cong else "TH?T B?I"
        log_msg = (
            f"[AI_CALL_AUDIT] Provider={res.provider} | L?n th?={attempt} | Tr?ng th?i={status_str} | "
            f"Tokens={res.tokens_used} | Th?i gian={res.thoi_gian_xu_ly_ms}ms | C?t ngang={res.bi_cat_ngang}"
        )
        if not res.thanh_cong and res.loi_neu_co:
            log_msg += f" | L?i: {res.loi_neu_co}"

        if res.thanh_cong:
            logger.info(log_msg)
        else:
            logger.warning(log_msg)

    def goi_ai_voi_retry(
        self,
        request: AIRequest,
        so_lan_thu_lai: int = 3,
        initial_backoff: float = 1.0,
        backoff_factor: float = 2.0,
        sleeper: Callable[[float], None] = time.sleep
    ) -> AIResponse:
        """
        G?i AI v?i c? ch? Exponential Backoff Retry.
        
        Quy tr?nh:
        1. Th? g?i provider hi?n t?i.
        2. N?u th?t b?i, t?nh th?i gian ch?: `initial_backoff * (backoff_factor ** attempt)`.
        3. T?m d?ng b?ng sleeper() v? th? l?i ??n t?i ?a `so_lan_thu_lai`.
        4. N?u qu? s? l?n th? v?n th?t b?i, tr? v? AIResponse v?i `thanh_cong = False`
           k?m th?ng ?i?p l?i, KH?NG n?m ngo?i l? l?m crash ?ng d?ng g?i.
        """
        last_response: Optional[AIResponse] = None

        for attempt in range(1, so_lan_thu_lai + 1):
            provider = self.current_provider
            try:
                response = provider.goi_ai(request)
            except Exception as e:
                response = AIResponse(
                    text="",
                    provider=provider.provider_name,
                    tokens_used=0,
                    thoi_gian_xu_ly_ms=0,
                    thanh_cong=False,
                    loi_neu_co=f"Ngo?i l? kh?ng x?c ??nh t? {provider.provider_name}: {str(e)}",
                    bi_cat_ngang=False
                )

            last_response = response
            self._ghi_log_metadata(response, attempt)

            if response.thanh_cong:
                return response

            # N?u ch?a th?nh c?ng v? c?n l??t retry -> ch? exponential backoff
            if attempt < so_lan_thu_lai:
                wait_time = initial_backoff * (backoff_factor ** (attempt - 1))
                logger.info(
                    f"[RETRY_BACKOFF] L?n g?i th? {attempt} th?t b?i. Ch? {wait_time:.2f}s tr??c khi th? l?i..."
                )
                sleeper(wait_time)

        # Tr? v? k?t qu? th?t b?i cu?i c?ng n?u ?? h?t l??t th?
        return last_response or AIResponse(
            text="",
            provider=self.current_provider_name,
            tokens_used=0,
            thoi_gian_xu_ly_ms=0,
            thanh_cong=False,
            loi_neu_co="Qu? s? l?n th? l?i nh?ng kh?ng nh?n ???c ph?n h?i th?nh c?ng.",
            bi_cat_ngang=False
        )
