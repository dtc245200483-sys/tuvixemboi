# -*- coding: utf-8 -*-
"""
Pydantic Schemas cho AI Module:
- AIRequest: D? li?u ??u v?o chu?n h?a cho c?c truy v?n AI (text & multimodal).
- AIResponse: K?t qu? ??u ra th?ng nh?t t? c?c nh? cung c?p AI (Gemini, DeepSeek...).
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AIRequest(BaseModel):
    prompt: str = Field(..., description="N?i dung c?u h?i ho?c ch? th? cho AI")
    max_tokens: int = Field(1000, ge=1, le=8192, description="S? l??ng token t?i ?a sinh ra")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="?? s?ng t?o c?a m? h?nh")
    system_instruction: Optional[str] = Field(None, description="Ch? th? h? th?ng ??nh h??ng phong c?ch AI")
    image_bytes: Optional[bytes] = Field(None, description="D? li?u nh? ph?n c?a ?nh n?u l? y?u c?u multimodal")
    mime_type: str = Field("image/jpeg", description="??nh d?ng MIME c?a ?nh")


class AIResponse(BaseModel):
    text: str = Field("", description="N?i dung v?n b?n do AI ph?n h?i")
    provider: str = Field(..., description="T?n nh? cung c?p AI (gemini / deepseek...)")
    tokens_used: int = Field(0, ge=0, description="T?ng s? token ?? s? d?ng (prompt + completion)")
    thoi_gian_xu_ly_ms: int = Field(0, ge=0, description="Th?i gian x? l? c?a API t?nh b?ng mili-gi?y")
    thanh_cong: bool = Field(True, description="Tr?ng th?i th?c thi cu?c g?i API")
    loi_neu_co: Optional[str] = Field(None, description="Th?ng ?i?p l?i chi ti?t n?u c? s? c?")
    bi_cat_ngang: bool = Field(False, description="??nh d?u n?u ph?n h?i b? c?t gi?a ch?ng do ch?m ng??ng max_tokens")
