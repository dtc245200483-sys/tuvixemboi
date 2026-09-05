# -*- coding: utf-8 -*-
"""
C?ng k?t n?i Google Gemini (Gemini Provider)
H? tr? Gemini 1.5 Flash / Pro th?ng qua REST API chu?n c?a Google.
"""

import time
import base64
from typing import Optional
import httpx

from config import settings
from ai_module.base_provider import BaseAIProvider
from ai_module.schemas import AIRequest, AIResponse


class GeminiProvider(BaseAIProvider):
    """Hi?n th?c h?a g?i Google Gemini API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-1.5-flash",
        timeout_seconds: float = 30.0
    ):
        self._api_key = api_key or settings.ai_api_key
        self.model = model
        self.timeout = timeout_seconds

    @property
    def provider_name(self) -> str:
        return "gemini"

    def goi_ai(self, request: AIRequest) -> AIResponse:
        t_start = time.perf_counter()

        import os
        import json
        if os.environ.get("AI_MOCK") == "1" or self._api_key == "mock":
            if getattr(request, "image_bytes", None) is not None:
                vision_dict = {
                    "hinh_dang_tran": "Trán cao rộng sáng sủa",
                    "hinh_dang_mat": "Mắt sáng tinh anh, 2 mí rõ ràng",
                    "hinh_dang_mui": "Sống mũi thẳng, cánh mũi nở nang kín đáo",
                    "hinh_dang_mieng": "Khóe miệng hướng lên tươi tắn",
                    "hinh_dang_cam": "Cằm tròn đầy phúc hậu",
                    "hinh_dang_ban_tay": "Bàn tay vuông chữ điền đầy đặn",
                    "do_ro_duong_tam_dao": "Đường tâm đạo sâu dài",
                    "do_ro_duong_tri_dao": "Đường trí đạo thẳng nét",
                    "do_ro_duong_sinh_dao": "Đường sinh đạo vòng cung rõ",
                    "hinh_dang_ngon_tay": ["Ngón cái vững chãi", "Ngón trỏ dài"],
                    "vi_tri_not_ruoi": ["Nốt ruồi phú quý"],
                    "mo_ta_them": "Tỷ lệ ngũ quan cân xứng, tướng mạo đắc cách."
                }
                return AIResponse(
                    text=json.dumps(vision_dict, ensure_ascii=False),
                    provider=self.provider_name,
                    tokens_used=180,
                    thoi_gian_xu_ly_ms=int((time.perf_counter() - t_start) * 1000),
                    thanh_cong=True,
                    loi_neu_co=None,
                    bi_cat_ngang=False
                )
            text_dict = {
                "chu_de": "tong_quan",
                "noi_dung": "Thời vận hanh thông, công danh sự nghiệp phát triển thuận lợi. Cần chú ý giữ tâm thế vững vàng và tích cực tu dưỡng thiện nghiệp.",
                "muc_do_tin_cay": 0.92
            }
            return AIResponse(
                text=json.dumps(text_dict, ensure_ascii=False),
                provider=self.provider_name,
                tokens_used=120,
                thoi_gian_xu_ly_ms=int((time.perf_counter() - t_start) * 1000),
                thanh_cong=True,
                loi_neu_co=None,
                bi_cat_ngang=False
            )

        if not self._api_key or self._api_key.startswith("dev_") or self._api_key == "test_key":
            # X? l? khi ch?a c? API key h?p l? trong m?i tr??ng dev
            return AIResponse(
                text="",
                provider=self.provider_name,
                tokens_used=0,
                thoi_gian_xu_ly_ms=int((time.perf_counter() - t_start) * 1000),
                thanh_cong=False,
                loi_neu_co="Ch?a c?u h?nh API Key AI h?p l? cho Gemini (GEMINI_API_KEY).",
                bi_cat_ngang=False
            )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self._api_key}"

        parts = []
        if request.image_bytes:
            b64_img = base64.b64encode(request.image_bytes).decode("ascii")
            parts.append({
                "inline_data": {
                    "mime_type": request.mime_type,
                    "data": b64_img
                }
            })
        parts.append({"text": request.prompt})

        contents = [{"parts": parts}]
        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": request.max_tokens,
                "temperature": request.temperature
            }
        }

        if request.system_instruction:
            payload["system_instruction"] = {
                "parts": [{"text": request.system_instruction}]
            }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()

            # Tr?ch xu?t d? li?u ph?n h?i
            candidate = data.get("candidates", [{}])[0]
            finish_reason = candidate.get("finishReason", "STOP")
            bi_cat = (finish_reason == "MAX_TOKENS")

            text = ""
            content_parts = candidate.get("content", {}).get("parts", [])
            if content_parts:
                text = content_parts[0].get("text", "")

            tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
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
                loi_neu_co=f"Gemini API Timeout sau {self.timeout}s.",
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
                loi_neu_co=f"L?i g?i Gemini API: {str(e)}",
                bi_cat_ngang=False
            )
