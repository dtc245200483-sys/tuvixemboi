# -*- coding: utf-8 -*-
"""
Hệ thống quản lý cấu hình tập trung (Centralized Configuration Management)
Đọc và validate toàn bộ biến môi trường từ .env theo môi trường dev/staging/production.
"""

import os
import logging
from typing import List
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("config")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

# Xác định môi trường chạy: development, staging, hoặc production
ENV_MODE = os.getenv("ENV", "development").strip().lower()

# Định vị đường dẫn file .env tương ứng
current_dir = os.path.dirname(os.path.abspath(__file__))
env_file_path = os.path.join(current_dir, f".env.{ENV_MODE}")
if not os.path.exists(env_file_path):
    # Thử tìm file .env tiêu chuẩn nếu chưa có .env.{ENV_MODE}
    fallback_path = os.path.join(current_dir, ".env")
    if os.path.exists(fallback_path):
        env_file_path = fallback_path

logger.info(f"Đang tải cấu hình cho môi trường: [{ENV_MODE}] từ file: {os.path.basename(env_file_path)}")


class Settings(BaseSettings):
    """Lớp cấu hình ứng dụng kế thừa BaseSettings từ pydantic-settings"""

    # 1. Cơ sở dữ liệu & Xác thực
    database_url: str = Field("sqlite:///./app.db", description="Connection string cơ sở dữ liệu")
    jwt_secret: str = Field("tuvi-production-jwt-secret-key-2026-secure-fixed", description="Khóa bí mật dùng ký JWT")
    jwt_algorithm: str = Field("HS256", description="Thuật toán mã hóa JWT")
    access_token_expire_minutes: int = Field(1440, description="Thời gian hết hạn của Access Token (phút) - 24 giờ")
    refresh_token_expire_days: int = Field(30, description="Thời gian hết hạn của Refresh Token (ngày)")

    # 2. AI Module & Vector Store
    ai_api_key: str = Field("c95e54cd3aa14f63890573b48be05a7a.RsUeUEeZ9grFGRM7", description="API Key cho dịch vụ AI bên ngoài (chatz.ai, z.ai, Gemini, OpenAI)")
    ai_provider: str = Field("freellmapi", description="Nhà cung cấp dịch vụ AI (freellmapi, chatz, z.ai, gemini, deepseek, openai)")
    ai_base_url: str = Field("https://api.z.ai/api/paas/v4/chat/completions", description="Base URL cho OpenAI/Chatz/Z.ai API (VD: https://api.z.ai/api/paas/v4/chat/completions)")
    ai_model: str = Field("glm-4.5-air", description="Tên model AI tùy chỉnh (VD: glm-4.5-air, glm-4-flash, gpt-4o-mini)")
    vector_db_path: str = Field("./knowledge_base/vector_store", description="Đường dẫn lưu trữ ChromaDB vector store")
    content_safety_api_key: str = Field("", description="API Key kiểm duyệt an toàn nội dung")
    freellm_db_path: str = Field(r"D:\AI github\freellmapi\server\data\freeapi.db", description="Đường dẫn đến file SQLite chứa API keys của FreeLLMAPI")
    freellm_encryption_key: str = Field("2ac1f647a1367841a052fa585f31800b66189d3af5a48e0befd7301a9265da48", description="Khóa giải mã AES-GCM cho database FreeLLMAPI")
    freellm_model: str = Field("openai/gpt-oss-120b", description="Model AI sử dụng cho FreeLLMProvider")

    # 3. Giám sát & Môi trường
    sentry_dsn: str = Field("", description="Sentry DSN ghi nhận crash log")
    env: str = Field("development", description="Môi trường chạy: development | staging | production")
    cors_origins: str = Field("http://localhost:5173,http://localhost:3000", description="Danh sách CORS origins")
    rate_limit_per_minute: int = Field(60, description="Giới hạn số request/phút trên mỗi IP")
    ai_daily_quota_free_user: int = Field(10, description="Hạn mức gọi AI miễn phí mỗi ngày cho mỗi user")
    port: int = Field(8000, description="Cổng dịch vụ backend")

    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("vector_db_path", mode="after")
    @classmethod
    def resolve_vector_db_path(cls, v: str) -> str:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        candidate1 = os.path.join(root_dir, "knowledge_base", "vector_store")
        if os.path.exists(candidate1):
            return candidate1
        if v and os.path.exists(v):
            return os.path.abspath(v)
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        """Tự động tách chuỗi CORS_ORIGINS phân cách bằng dấu phẩy thành list Python"""
        if not self.cors_origins:
            return ["*"]
        clean_str = self.cors_origins.strip().strip("[]'\"")
        origins = [origin.strip() for origin in clean_str.split(",") if origin.strip()]
        return origins if origins else ["*"]

    @model_validator(mode="after")
    def validate_security_and_production(self) -> "Settings":
        """Rà soát và xác thực nghiêm ngặt cấu hình trước khi khởi động ứng dụng"""
        env_lower = self.env.strip().lower()

        # Kiểm tra biến bắt buộc tối thiểu
        if not self.database_url or not self.database_url.strip():
            raise ValueError("Cấu hình DATABASE_URL không được để trống!")
        if not self.jwt_secret or not self.jwt_secret.strip():
            raise ValueError("Cấu hình JWT_SECRET không được để trống!")

        # Kiểm tra các điều kiện an toàn đối với môi trường PRODUCTION
        if env_lower == "production":
            # 1. Bắt buộc phải có AI_API_KEY khi chạy production
            if not self.ai_api_key or not self.ai_api_key.strip():
                raise ValueError("BẮT BUỘC: Phải cấu hình AI_API_KEY khi chạy trong môi trường production!")

            # 2. Cảnh báo bảo mật nếu JWT_SECRET vẫn dùng secret của dev
            dev_keywords = ["dev-secret", "change-in-production", "default_secret", "secret", "123456"]
            if any(kw in self.jwt_secret.lower() for kw in dev_keywords):
                logger.warning(
                    "⚠️ [CẢNH BÁO NGUY HIỂM BẢO MẬT]: Ứng dụng đang chạy trong môi trường PRODUCTION "
                    "nhưng JWT_SECRET đang sử dụng giá trị mặc định/dev! Hãy cập nhật JWT_SECRET an toàn ngay!"
                )

            # 3. Khuyến nghị không dùng SQLite trong production
            if self.database_url.startswith("sqlite"):
                logger.warning(
                    "⚠️ [CẢNH BÁO]: Ứng dụng đang chạy trong môi trường PRODUCTION nhưng DATABASE_URL là SQLite! "
                    "Khuyến nghị sử dụng PostgreSQL cho môi trường sản xuất."
                )

        return self


# Khởi tạo singleton instance dùng chung toàn bộ dự án
settings = Settings()
