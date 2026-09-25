# -*- coding: utf-8 -*-
"""
Tu Vi & Xem Boi AI Platform - Backend Main Application
Tích hợp toàn bộ Router nghiệp vụ, tầng bảo vệ hạ tầng và xử lý ngoại lệ toàn cục:
- Middleware Rate Limiting chống spam/brute-force theo IP
- Giám sát lỗi tập trung qua Sentry SDK
- Lập lịch sao lưu tự động & quét dọn dữ liệu hết hạn qua APScheduler (Lifespan handler)
- Toàn bộ Routers: Auth, Vision, Birth Profile, Tu Vi, Bat Tu, Kinh Dich, Nhan Tuong, Chat, Quota
- Global Exception Handlers (HTTPException, RequestValidationError, Exception) chuẩn hóa qua APIResponse
"""

import os
import sys
import logging
from contextlib import asynccontextmanager

# Đảm bảo PYTHONPATH nhận diện các gói cấp cao (interpretation_api, knowledge_base, astro_engine)
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_CURRENT_DIR)
for _p in [_CURRENT_DIR, _ROOT_DIR, os.path.join(_ROOT_DIR, "interpretation_api"), os.path.join(_ROOT_DIR, "knowledge_base")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from middleware.sentry_setup import khoi_tao_sentry, gan_context_loi
from middleware.rate_limiter import rate_limit_middleware
from middleware.backup_service import khoi_tao_scheduler, dung_scheduler

from auth.router import router as auth_router
from vision_module.router import router as vision_router
from api.routers import (
    birth_profile_router,
    tu_vi_router,
    bat_tu_router,
    kinh_dich_router,
    nhan_tuong_router,
    chat_router,
    quota_router
)
from api.routers.forum_router import router as forum_router

logger = logging.getLogger("backend.main")

# 1. Khởi tạo Sentry SDK khi khởi động ứng dụng
khoi_tao_sentry()


def _warmup_background():
    """Tải trước mô hình embedding, vector store và API provider ở luồng nền để tối ưu tốc độ cho request đầu tiên."""
    if os.getenv("ENABLE_WARMUP", "false").lower() != "true":
        logger.info("[WARMUP] Tối ưu hóa RAM cho môi trường container: Bỏ qua warmup mô hình nặng.")
        return
    try:
        from knowledge_base.embedding_service import get_embedding_model
        logger.info("[WARMUP] Đang tải trước mô hình embedding trong nền...")
        get_embedding_model()
        logger.info("[WARMUP] Hoàn tất nạp trước mô hình embedding thành công!")

        from knowledge_base.search_service import search
        search("Tử Vi", "tu_vi", top_k=1)
        logger.info("[WARMUP] Hoàn tất nạp trước vector store search!")

        from ai_module.providers.freellm_provider import FreeLLMProvider
        FreeLLMProvider()
        logger.info("[WARMUP] Hoàn tất nạp trước FreeLLM keys!")
    except Exception as e:
        logger.warning(f"[WARMUP] Bỏ qua tải trước: {e}")



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Quản lý vòng đời ứng dụng FastAPI: khởi tạo DB, khởi động APScheduler và nạp trước mô hình nền"""
    from db.database import init_db
    init_db()
    if os.getenv("DISABLE_SCHEDULER", "false").lower() != "true":
        khoi_tao_scheduler()
    import threading
    threading.Thread(target=_warmup_background, daemon=True).start()
    yield
    dung_scheduler()


app = FastAPI(
    title="Tu Vi & Xem Boi AI API",
    description="Backend API nền tảng cho ứng dụng Tử Vi Đẩu Số, Kinh Dịch, Bát Tự và Nhân Tướng Học",
    version="1.0.0",
    debug=False,
    lifespan=lifespan
)

# 2. Thiết lập CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3. Đăng ký Middleware Rate Limiting & Context Sentry cho mọi HTTP Request
@app.middleware("http")
async def custom_infrastructure_middleware(request: Request, call_next):
    # Gắn context endpoint cho Sentry trước khi request được xử lý
    gan_context_loi(endpoint=request.url.path)
    # Kiểm tra Rate Limit theo IP
    return await rate_limit_middleware(request, call_next)


# ==============================================================================
# EXCEPTION HANDLERS TOÀN CỤC (RESPONSE ENVELOPE CHO TOÀN BỘ LỖI)
# ==============================================================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Xử lý tất cả HTTPException (400, 401, 403, 404, 429...) và bọc trong envelope APIResponse:
    { "thanh_cong": false, "du_lieu": null, "loi": detail, "detail": detail }
    """
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "thanh_cong": False,
            "du_lieu": None,
            "loi": str(exc.detail),
            "detail": str(exc.detail)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Xử lý lỗi validate schema đầu vào từ Pydantic (422) và chuẩn hóa trong envelope APIResponse:
    { "thanh_cong": false, "du_lieu": null, "loi": "Dữ liệu đầu vào không hợp lệ..." }
    """
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(l) for l in err.get("loc", []) if l != "body"])
        msg = err.get("msg", "Dữ liệu không hợp lệ")
        errors.append(f"{loc}: {msg}" if loc else msg)
    loi_str = "Dữ liệu đầu vào không hợp lệ: " + "; ".join(errors)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "thanh_cong": False,
            "du_lieu": None,
            "loi": loi_str,
            "detail": loi_str
        }
    )


@app.exception_handler(Exception)
async def global_unhandled_exception_handler(request: Request, exc: Exception):
    """
    Bắt mọi lỗi chưa được xử lý (unhandled exception - 500):
    - Ghi nhận stack trace đầy đủ vào Sentry kèm endpoint context và local logger.
    - Trả về thông báo an toàn, thân thiện, KHÔNG làm rò rỉ stack trace ra ngoài.
    """
    logger.error(f"Lỗi hệ thống không xử lý được: {str(exc)}", exc_info=True)
    gan_context_loi(endpoint=request.url.path)
    try:
        import sentry_sdk
        sentry_sdk.capture_exception(exc)
    except Exception:
        pass

    detail_msg = f"{type(exc).__name__}: {str(exc)}"
    is_debug = request.headers.get("x-debug") == "1"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "thanh_cong": False,
            "du_lieu": None,
            "loi": detail_msg if is_debug else "Đã có lỗi xảy ra, vui lòng thử lại",
            "detail": detail_msg if is_debug else "Đã có lỗi xảy ra, vui lòng thử lại"
        }
    )


# ==============================================================================
# GẮN ROUTERS VÀO ỨNG DỤNG
# ==============================================================================
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(vision_router)
app.include_router(birth_profile_router)
app.include_router(tu_vi_router)
app.include_router(bat_tu_router)
app.include_router(kinh_dich_router)
app.include_router(nhan_tuong_router)
app.include_router(chat_router)
app.include_router(quota_router)
app.include_router(forum_router)


@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint kiểm tra trạng thái hoạt động cơ bản của hệ thống"""
    import shutil
    return {
        "status": "ok",
        "version": "v1.0.15",
        "node": shutil.which("node"),
        "nodejs": shutil.which("nodejs")
    }


# ==============================================================================
# PHỤC VỤ GIAO DIỆN WEB NGƯỜI DÙNG (SPA FRONTEND)
# ==============================================================================
_STATIC_DIR = os.path.join(_CURRENT_DIR, "static")
if not os.path.exists(_STATIC_DIR):
    _STATIC_DIR = os.path.join(_ROOT_DIR, "frontend", "web", "dist")

if os.path.exists(_STATIC_DIR):
    _assets_dir = os.path.join(_STATIC_DIR, "assets")
    if os.path.exists(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")

    _images_dir = os.path.join(_STATIC_DIR, "images")
    if os.path.exists(_images_dir):
        app.mount("/images", StaticFiles(directory=_images_dir), name="images")

    _icons_dir = os.path.join(_STATIC_DIR, "icons")
    if os.path.exists(_icons_dir):
        app.mount("/icons", StaticFiles(directory=_icons_dir), name="icons")

    @app.get("/", tags=["Frontend"])
    async def serve_index():
        """Phục vụ trang chủ Web Tử Vi cho người dùng"""
        index_file = os.path.join(_STATIC_DIR, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        return RedirectResponse(url="/docs")

    @app.get("/{full_path:path}", tags=["Frontend"])
    async def serve_spa_frontend(full_path: str):
        """Phục vụ các route chuyển trang React Router và file tĩnh của Web"""
        # Nếu là các tiền tố API đã biết nhưng không khớp router cụ thể -> trả về 404 API
        if full_path.startswith(("api/", "auth/")):
            raise HTTPException(status_code=404, detail="API endpoint không tồn tại")

        # Phục vụ file tĩnh cụ thể nếu có (VD: favicon.svg, manifest.json, sw.js, v.v.)
        candidate = os.path.join(_STATIC_DIR, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)

        # Mọi route chuyển trang của React SPA (VD: /tu-vi, /dashboard, /settings, /login)
        index_file = os.path.join(_STATIC_DIR, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Giao diện chưa được build")
else:
    @app.get("/", tags=["Root"])
    def root_fallback():
        return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=(settings.env == "development"))
