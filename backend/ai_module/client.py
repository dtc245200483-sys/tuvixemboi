# -*- coding: utf-8 -*-
"""
Lớp AI Client điều phối toàn bộ các yêu cầu AI trong hệ thống:
- Hỗ trợ chọn và chuyển đổi Provider (FreeLLMAPI / Groq / Gemini / DeepSeek).
- Retry pattern với Exponential Backoff tự động khi gặp sự cố timeout/rate-limit.
- Tuân thủ nguyên tắc bảo mật dữ liệu: CHỈ log metadata kỹ thuật, KHÔNG log prompt/response nhạy cảm.
"""

import time
import logging
from typing import Optional, Dict, Any, Callable

from config import settings
from ai_module.schemas import AIRequest, AIResponse
from ai_module.base_provider import BaseAIProvider
from ai_module.providers.gemini_provider import GeminiProvider
from ai_module.providers.deepseek_provider import DeepSeekProvider
from ai_module.providers.freellm_provider import FreeLLMProvider

logger = logging.getLogger("AIModuleClient")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


class AIClient:
    """Client trung tâm xử lý gọi AI thống nhất."""

    def __init__(
        self,
        default_provider: Optional[str] = None,
        gemini_provider: Optional[BaseAIProvider] = None,
        deepseek_provider: Optional[BaseAIProvider] = None,
        freellm_provider: Optional[BaseAIProvider] = None
    ):
        if default_provider:
            provider_name = default_provider.strip().lower()
        elif freellm_provider is not None:
            provider_name = "freellmapi"
        elif gemini_provider is not None and getattr(settings, "ai_provider", None) == "gemini":
            provider_name = "gemini"
        elif deepseek_provider is not None and getattr(settings, "ai_provider", None) == "deepseek":
            provider_name = "deepseek"
        elif gemini_provider is not None and deepseek_provider is None and freellm_provider is None:
            # Caller specifically injected only gemini_provider (e.g. mock in unit tests)
            provider_name = "gemini"
        else:
            provider_name = (getattr(settings, "ai_provider", "freellmapi") or "freellmapi").strip().lower()

        self.providers: Dict[str, BaseAIProvider] = {
            "freellmapi": freellm_provider or FreeLLMProvider(),
            "groq": freellm_provider or FreeLLMProvider(),
            "gemini": gemini_provider or GeminiProvider(),
            "deepseek": deepseek_provider or DeepSeekProvider()
        }

        if provider_name not in self.providers:
            provider_name = "freellmapi"

        self.current_provider_name = provider_name

    @property
    def current_provider(self) -> BaseAIProvider:
        """Lấy provider hiện đang được kích hoạt."""
        return self.providers.get(self.current_provider_name, self.providers.get("freellmapi", self.providers.get("gemini")))

    def chuyen_doi_provider(self, provider_moi: str) -> None:
        """
        Chuyển đổi provider đang sử dụng (VD: 'freellmapi' <-> 'gemini' <-> 'deepseek').
        Hỗ trợ fallback khi một provider gặp sự cố kéo dài.
        """
        p_name = provider_moi.strip().lower()
        if p_name not in self.providers:
            raise ValueError(f"Provider '{provider_moi}' không được hỗ trợ. Chỉ hỗ trợ: {list(self.providers.keys())}")
        self.current_provider_name = p_name
        logger.info(f"[AI_CLIENT] Đã chuyển đổi provider hoạt động sang: '{self.current_provider_name}'")

    def _ghi_log_metadata(self, res: AIResponse, attempt: int) -> None:
        """
        Ghi log metadata cuộc gọi AI tuân thủ nguyên tắc bảo mật dữ liệu:
        CHỈ ghi: provider, tokens_used, thoi_gian_xu_ly_ms, thanh_cong, loi (nếu có).
        TUYỆT ĐỐI KHÔNG ghi nội dung câu hỏi (prompt) hay câu trả lời (response text)
        vì có thể chứa thông tin sinh trắc học/ngày tháng năm sinh nhạy cảm.
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
        so_lan_thu_lai: int = 2,
        initial_backoff: float = 0.4,
        backoff_factor: float = 1.5,
        sleeper: Callable[[float], None] = time.sleep
    ) -> AIResponse:
        """
        Gọi AI với cơ chế Exponential Backoff Retry.
        
        Quy trình:
        1. Thử gọi provider hiện tại.
        2. Nếu thất bại, tính thời gian chờ: `initial_backoff * (backoff_factor ** attempt)`.
        3. Tạm dừng bằng sleeper() và thử lại đến tối đa `so_lan_thu_lai`.
        4. Nếu quá số lần thử vẫn thất bại, trả về AIResponse với `thanh_cong = False`
           kèm thông điệp lỗi, KHÔNG ném ngoại lệ làm crash ứng dụng gọi.
        """
        last_response: Optional[AIResponse] = None
        # Đối với FreeLLMProvider, provider đã tự động luân chuyển nhiều keys và fallback model bên trong.
        # Không lặp lại vòng retry với sleep ở tầng client để đảm bảo phản hồi luôn <= 5 giây.
        effective_retries = 1 if self.current_provider_name in ["freellmapi", "groq"] else so_lan_thu_lai

        for attempt in range(1, effective_retries + 1):
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
                    loi_neu_co=f"Ngoại lệ không xác định từ {provider.provider_name}: {str(e)}",
                    bi_cat_ngang=False
                )

            last_response = response
            self._ghi_log_metadata(response, attempt)

            if response.thanh_cong:
                return response

            if not response.thanh_cong and response.loi_neu_co and ("API Key" in response.loi_neu_co or "Chưa cấu hình" in response.loi_neu_co):
                break

            # Nếu chưa thành công và còn lượt retry -> chờ exponential backoff
            if attempt < so_lan_thu_lai:
                wait_time = initial_backoff * (backoff_factor ** (attempt - 1))
                logger.info(
                    f"[RETRY_BACKOFF] Lần gọi thứ {attempt} thất bại. Chờ {wait_time:.2f}s trước khi thử lại..."
                )
                sleeper(wait_time)

        # Trả về kết quả thất bại cuối cùng nếu đã hết lượt thử
        return last_response or AIResponse(
            text="",
            provider=self.current_provider_name,
            tokens_used=0,
            thoi_gian_xu_ly_ms=0,
            thanh_cong=False,
            loi_neu_co="Quá số lần thử lại nhưng không nhận được phản hồi thành công.",
            bi_cat_ngang=False
        )
