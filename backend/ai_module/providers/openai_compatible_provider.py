# -*- coding: utf-8 -*-
"""
Cổng kết nối AI tương thích OpenAI (OpenAI-compatible Provider).
Hỗ trợ mọi nền tảng AI chuẩn OpenAI REST API:
- Chatz.ai / Z.ai (chat.z.ai / api.z.ai / GLM-4 / GLM-4-flash)
- OpenAI (GPT-4o, GPT-4o-mini)
- Groq / Together AI / DeepSeek / OpenRouter
- Mọi endpoint tùy chỉnh qua AI_BASE_URL và AI_MODEL
"""

import os
import time
import logging
from typing import Optional
import httpx

from config import settings
from ai_module.base_provider import BaseAIProvider
from ai_module.schemas import AIRequest, AIResponse

logger = logging.getLogger("OpenAICompatibleProvider")


class OpenAICompatibleProvider(BaseAIProvider):
    """Provider đa năng tương thích chuẩn OpenAI, hỗ trợ chatz.ai / z.ai / glm / openai."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        provider_name: str = "openai_compatible",
        timeout_seconds: float = 60.0
    ):
        self._provider_name = provider_name
        self._api_key = (
            api_key or
            os.getenv("AI_API_KEY") or
            getattr(settings, "ai_api_key", "") or
            os.getenv("OPENAI_API_KEY", "")
        )

        # 1. Tự động nhận diện Base URL
        custom_url = base_url or os.getenv("AI_BASE_URL") or getattr(settings, "ai_base_url", "")
        if not custom_url:
            p_lower = self._provider_name.lower()
            env_provider = getattr(settings, "ai_provider", "").lower()
            if any(k in p_lower or k in env_provider for k in ["chatz", "z.ai", "z_ai", "glm", "chat.z.ai"]):
                custom_url = "https://api.z.ai/api/paas/v4/chat/completions"
            else:
                custom_url = "https://api.openai.com/v1/chat/completions"
        elif not custom_url.endswith("/chat/completions"):
            custom_url = custom_url.rstrip("/") + "/chat/completions"

        self.base_url = custom_url

        # 2. Tự động nhận diện Model
        custom_model = model or os.getenv("AI_MODEL") or getattr(settings, "ai_model", "")
        if not custom_model:
            if "z.ai" in self.base_url or "bigmodel" in self.base_url or "chatz" in self._provider_name.lower():
                custom_model = "glm-4-flash"
            else:
                custom_model = "gpt-4o-mini"

        self.model = custom_model
        self.timeout = timeout_seconds
        logger.info(f"[{self.provider_name}] Khởi tạo với URL={self.base_url}, Model={self.model}")

    @property
    def provider_name(self) -> str:
        return self._provider_name

    def goi_ai(self, request: AIRequest) -> AIResponse:
        t_start = time.perf_counter()

        if not self._api_key or self._api_key.startswith("dev_") or self._api_key == "test_key":
            return AIResponse(
                text="",
                provider=self.provider_name,
                tokens_used=0,
                thoi_gian_xu_ly_ms=int((time.perf_counter() - t_start) * 1000),
                thanh_cong=False,
                loi_neu_co="Chưa cấu hình API Key AI hợp lệ (AI_API_KEY). Vui lòng thêm key trên Dashboard Render.",
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

        clean_key = self._api_key.strip()
        headers = {
            "Authorization": f"Bearer {clean_key}",
            "Content-Type": "application/json"
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(self.base_url, json=payload, headers=headers)

            elapsed_ms = int((time.perf_counter() - t_start) * 1000)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if not choices:
                    return AIResponse(
                        text="",
                        provider=self.provider_name,
                        tokens_used=0,
                        thoi_gian_xu_ly_ms=elapsed_ms,
                        thanh_cong=False,
                        loi_neu_co="Phản hồi từ AI không chứa nội dung (empty choices).",
                        bi_cat_ngang=False
                    )
                content = choices[0].get("message", {}).get("content", "")
                tokens = data.get("usage", {}).get("total_tokens", 0)
                finish_reason = choices[0].get("finish_reason", "")
                return AIResponse(
                    text=content,
                    provider=self.provider_name,
                    tokens_used=tokens,
                    thoi_gian_xu_ly_ms=elapsed_ms,
                    thanh_cong=True,
                    loi_neu_co=None,
                    bi_cat_ngang=(finish_reason == "length")
                )
            else:
                err_detail = resp.text
                logger.error(f"[{self.provider_name}] Lỗi HTTP {resp.status_code}: {err_detail}")
                return AIResponse(
                    text="",
                    provider=self.provider_name,
                    tokens_used=0,
                    thoi_gian_xu_ly_ms=int((time.perf_counter() - t_start) * 1000),
                    thanh_cong=False,
                    loi_neu_co=f"Lỗi phản hồi từ máy chủ AI ({resp.status_code}): {err_detail[:150]}",
                    bi_cat_ngang=False
                )
        except Exception as e:
            logger.error(f"[{self.provider_name}] Exception khi gọi API: {e}")
            return AIResponse(
                text="",
                provider=self.provider_name,
                tokens_used=0,
                thoi_gian_xu_ly_ms=int((time.perf_counter() - t_start) * 1000),
                thanh_cong=False,
                loi_neu_co=f"Không thể kết nối đến máy chủ AI: {str(e)[:150]}",
                bi_cat_ngang=False
            )
