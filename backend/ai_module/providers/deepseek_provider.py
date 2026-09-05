# -*- coding: utf-8 -*-
"""
C?ng k?t n?i DeepSeek (DeepSeek Provider)
H? tr? deepseek-chat v? deepseek-reasoner qua OpenAI-compatible API endpoint.
"""

import time
from typing import Optional
import httpx

from config import settings
from ai_module.base_provider import BaseAIProvider
from ai_module.schemas import AIRequest, AIResponse


class DeepSeekProvider(BaseAIProvider):
    """Hi?n th?c h?a g?i DeepSeek API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com/chat/completions",
        timeout_seconds: float = 30.0
    ):
        self._api_key = api_key or getattr(settings, "deepseek_api_key", None) or settings.ai_api_key
        self.model = model
        self.base_url = base_url
        self.timeout = timeout_seconds

    @property
    def provider_name(self) -> str:
        return "deepseek"

    def goi_ai(self, request: AIRequest) -> AIResponse:
        t_start = time.perf_counter()

        if not self._api_key or self._api_key.startswith("dev_") or self._api_key == "test_key":
            return AIResponse(
                text="",
                provider=self.provider_name,
                tokens_used=0,
                thoi_gian_xu_ly_ms=int((time.perf_counter() - t_start) * 1000),
                thanh_cong=False,
                loi_neu_co="Ch?a c?u h?nh API Key AI h?p l? cho DeepSeek.",
                bi_cat_ngang=False
            )

        messages = []
        if request.system_instruction:
            messages.append({"role": "system", "content": request.system_instruction})
        messages.append({"role": "user", "content": request.prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(self.base_url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            choice = data.get("choices", [{}])[0]
            finish_reason = choice.get("finish_reason", "stop")
            bi_cat = (finish_reason == "length")

            text = choice.get("message", {}).get("content", "")
            tokens = data.get("usage", {}).get("total_tokens", 0)
            elapsed_ms = int((time.perf_counter() - t_start) * 1000)

            return AIResponse(
                text=text,
                provider=self.provider_name,
                tokens_used=tokens,
                thoi_gian_xu_ly_ms=elapsed_ms,
                thanh_cong=True,
                loi_neu_co=None,
                bi_cat_ngang=bi_cat
            )

        except httpx.TimeoutException:
            elapsed_ms = int((time.perf_counter() - t_start) * 1000)
            return AIResponse(
                text="",
                provider=self.provider_name,
                tokens_used=0,
                thoi_gian_xu_ly_ms=elapsed_ms,
                thanh_cong=False,
                loi_neu_co=f"DeepSeek API Timeout sau {self.timeout}s.",
                bi_cat_ngang=False
            )
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - t_start) * 1000)
            return AIResponse(
                text="",
                provider=self.provider_name,
                tokens_used=0,
                thoi_gian_xu_ly_ms=elapsed_ms,
                thanh_cong=False,
                loi_neu_co=f"L?i g?i DeepSeek API: {str(e)}",
                bi_cat_ngang=False
            )
