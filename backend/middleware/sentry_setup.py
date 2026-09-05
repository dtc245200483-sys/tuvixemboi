# -*- coding: utf-8 -*-
"""
Module cấu hình giám sát lỗi hệ thống tập trung với Sentry:
- Khởi tạo an toàn chỉ khi có SENTRY_DSN (không lỗi trên dev).
- Gắn context nghiệp vụ (user_id, endpoint) hỗ trợ điều tra lỗi mà KHÔNG lộ dữ liệu cá nhân PII.
"""

import logging
from typing import Optional
from config import settings

logger = logging.getLogger("middleware.sentry")

# Trạng thái khởi tạo Sentry
_sentry_da_khoi_tao: bool = False


def khoi_tao_sentry() -> bool:
    """
    Cấu hình Sentry SDK đọc từ settings.sentry_dsn:
    - CHỈ kích hoạt khi có DSN hợp lệ (tránh gửi log rác từ môi trường phát triển cục bộ).
    - Thiết lập môi trường hoạt động theo settings.env (development / staging / production).
    - Tắt gửi PII (Personally Identifiable Information) mặc định để bảo mật người dùng.
    
    Returns:
        bool: True nếu Sentry đã được khởi tạo thành công, False nếu bỏ qua.
    """
    global _sentry_da_khoi_tao

    dsn = getattr(settings, "sentry_dsn", "").strip()
    if not dsn:
        logger.info("[SENTRY] Không có SENTRY_DSN được cấu hình. Bỏ qua khởi tạo Sentry (môi trường dev).")
        _sentry_da_khoi_tao = False
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration

        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )

        sentry_sdk.init(
            dsn=dsn,
            environment=settings.env,
            traces_sample_rate=1.0 if settings.env != "production" else 0.2,
            send_default_pii=False,
            integrations=[sentry_logging],
            attach_stacktrace=True
        )
        _sentry_da_khoi_tao = True
        logger.info(f"[SENTRY] Đã khởi tạo Sentry thành công trên môi trường '{settings.env}'.")
        return True
    except Exception as e:
        logger.warning(f"[SENTRY] Khởi tạo Sentry thất bại: {e}")
        _sentry_da_khoi_tao = False
        return False


def gan_context_loi(user_id: Optional[str] = None, endpoint: Optional[str] = None) -> None:
    """
    Gắn ngữ cảnh chẩn đoán lỗi vào Sentry Scope (Sentry SDK 2.x API):
    - user_id: Mã định danh tài khoản gặp sự cố (UUID).
    - endpoint: Đường dẫn API đang được gọi.
    
    NGUYÊN TẮC AN TOÀN BẢO MẬT:
    - KHÔNG lưu trữ họ tên, ngày tháng năm sinh, nội dung ảnh hoặc câu hỏi tâm linh vào Sentry.
    """
    try:
        import sentry_sdk

        if user_id:
            # Chỉ gắn id, không gắn email/ip/username vào user context
            sentry_sdk.set_user({"id": str(user_id)})
        if endpoint:
            sentry_sdk.set_tag("endpoint", str(endpoint))
    except Exception as e:
        logger.debug(f"Không thể gắn Sentry context: {e}")


def da_khoi_tao_sentry() -> bool:
    """Kiểm tra xem Sentry đã được khởi tạo và sẵn sàng hoạt động hay chưa"""
    global _sentry_da_khoi_tao
    return _sentry_da_khoi_tao
