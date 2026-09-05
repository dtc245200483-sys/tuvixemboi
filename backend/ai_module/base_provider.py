# -*- coding: utf-8 -*-
"""
L?p c? s? tr?u t??ng (Abstract Base Provider) cho c?c c?ng k?t n?i AI.
M?i nh? cung c?p (Gemini, DeepSeek, Claude...) ??u ph?i hi?n th?c h?a interface n?y.
"""

from abc import ABC, abstractmethod
from ai_module.schemas import AIRequest, AIResponse


class BaseAIProvider(ABC):
    """Interface chu?n ??nh ngh?a ph??ng th?c g?i AI."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """T?n ??nh danh c?a nh? cung c?p AI (VD: 'gemini', 'deepseek')."""
        pass

    @abstractmethod
    def goi_ai(self, request: AIRequest) -> AIResponse:
        """
        Th?c thi cu?c g?i API ??n d?ch v? AI.
        Ph?i x? l? ngo?i l? n?i b? v? lu?n tr? v? ??i t??ng AIResponse th?ng nh?t.
        """
        pass
