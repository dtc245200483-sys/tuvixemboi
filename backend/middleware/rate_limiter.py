# -*- coding: utf-8 -*-
"""
Module Rate Limiting bảo vệ hạ tầng chống spam/brute-force/DDoS:
- Class RateLimiter: Sử dụng thuật toán In-Memory Sliding Window Log (thread-safe với threading.Lock).
- Hàm kiem_tra_rate_limit(key, gioi_han, khoang_thoi_gian_giay): Kiểm tra và ghi nhận request.
- Middleware rate_limit_middleware: Áp dụng cho mọi request theo IP khách hàng, trả về 429 nếu vượt giới hạn.
"""

import time
import threading
import logging
from typing import Dict, List, Optional
from fastapi import Request
from fastapi.responses import JSONResponse

from config import settings

logger = logging.getLogger("middleware.rate_limiter")


class RateLimiter:
    """
    Bộ đệm Rate Limiter In-Memory áp dụng thuật toán Sliding Window Log.
    Thiết kế chuẩn hóa interface để dễ dàng mở rộng sang Redis backend khi hệ thống mở rộng.
    """

    def __init__(self):
        self._lock = threading.Lock()
        # Lưu trữ: { "ip_hoac_user_id": [timestamp_1, timestamp_2, ...] }
        self._records: Dict[str, List[float]] = {}

    def kiem_tra_rate_limit(
        self,
        key: str,
        gioi_han: int,
        khoang_thoi_gian_giay: int = 60
    ) -> bool:
        """
        Kiểm tra xem key (IP hoặc user_id) có vượt quá số lượt gọi cho phép trong khung thời gian hay không.
        
        Args:
            key: Định danh người gọi (IP hoặc User ID).
            gioi_han: Số lượng request tối đa trong cửa sổ thời gian.
            khoang_thoi_gian_giay: Kích thước cửa sổ trượt (mặc định 60 giây).
            
        Returns:
            bool: True nếu request được chấp nhận, False nếu vượt ngưỡng (cần trả về 429).
        """
        now = time.time()
        window_start = now - khoang_thoi_gian_giay

        with self._lock:
            timestamps = self._records.get(key, [])
            
            # Loại bỏ tất cả timestamp nằm ngoài sliding window hiện tại
            valid_timestamps = [t for t in timestamps if t > window_start]

            if len(valid_timestamps) >= gioi_han:
                self._records[key] = valid_timestamps
                logger.warning(
                    f"[RATE_LIMIT_BLOCK] Key '{key}' vượt ngưỡng: {len(valid_timestamps)}/{gioi_han} req trong {khoang_thoi_gian_giay}s"
                )
                return False

            # Ghi nhận request hợp lệ mới
            valid_timestamps.append(now)
            self._records[key] = valid_timestamps
            return True

    def reset(self, key: Optional[str] = None) -> None:
        """Xóa lịch sử request (cho 1 key hoặc toàn bộ, hữu ích khi test)"""
        with self._lock:
            if key is not None:
                self._records.pop(key, None)
            else:
                self._records.clear()

    def lay_so_luot_hien_tai(self, key: str, khoang_thoi_gian_giay: int = 60) -> int:
        """Lấy số lượng request hiện có trong cửa sổ trượt"""
        now = time.time()
        window_start = now - khoang_thoi_gian_giay
        with self._lock:
            timestamps = self._records.get(key, [])
            return len([t for t in timestamps if t > window_start])


# Singleton Rate Limiter mặc định dùng chung cho ứng dụng
default_rate_limiter = RateLimiter()


def kiem_tra_rate_limit(
    key: str,
    gioi_han: int,
    khoang_thoi_gian_giay: int = 60
) -> bool:
    """Hàm tiện ích tra cứu qua default_rate_limiter singleton"""
    return default_rate_limiter.kiem_tra_rate_limit(
        key=key,
        gioi_han=gioi_han,
        khoang_thoi_gian_giay=khoang_thoi_gian_giay
    )


def lay_client_ip(request: Request) -> str:
    """
    Trích xuất IP khách hàng thực tế (ưu tiên X-Forwarded-For nếu qua proxy/load balancer)
    """
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        # Lấy IP đầu tiên trong danh sách client -> proxy1 -> proxy2
        client_ip = x_forwarded_for.split(",")[0].strip()
        if client_ip:
            return client_ip

    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()

    if request.client and request.client.host:
        return request.client.host

    return "127.0.0.1"


async def rate_limit_middleware(request: Request, call_next):
    """
    FastAPI Middleware kiểm tra Rate Limit theo IP cho mọi request:
    - Bỏ qua kiểm tra cho các endpoint tĩnh hoặc docs nếu cần
    - Sử dụng settings.rate_limit_per_minute làm giới hạn
    - Trả về HTTP 429 đúng chuẩn Response Envelope Pattern nếu vi phạm
    """
    path = request.url.path
    # Bỏ qua kiểm tra đối với health check và docs
    if path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)

    client_ip = lay_client_ip(request)
    limit = getattr(settings, "rate_limit_per_minute", 60)

    duoc_phep = default_rate_limiter.kiem_tra_rate_limit(
        key=client_ip,
        gioi_han=limit,
        khoang_thoi_gian_giay=60
    )

    if not duoc_phep:
        msg = "Quá nhiều yêu cầu. Vui lòng thử lại sau."
        return JSONResponse(
            status_code=429,
            content={
                "thanh_cong": False,
                "du_lieu": None,
                "loi": msg,
                "detail": msg
            },
            headers={"Retry-After": "60"}
        )

    response = await call_next(request)
    return response
