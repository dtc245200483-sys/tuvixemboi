# -*- coding: utf-8 -*-
"""
Unit Tests cho hệ thống cấu hình config.py
"""
import os
import pytest
from pydantic import ValidationError

def test_settings_development_load():
    """Kiểm tra Settings nạp đúng các giá trị mặc định từ môi trường development"""
    os.environ["ENV"] = "development"
    from config import Settings
    
    app_settings = Settings()
    assert app_settings.env == "development"
    assert app_settings.database_url == "sqlite:///./dev.db"
    assert app_settings.jwt_secret == "dev-secret-key-change-in-production"
    assert app_settings.ai_daily_quota_free_user == 50
    assert app_settings.rate_limit_per_minute == 120
    assert "http://localhost:5173" in app_settings.cors_origins_list
    assert "http://localhost:3000" in app_settings.cors_origins_list

def test_cors_origins_parsing():
    """Kiểm tra thuộc tính cors_origins_list tự động phân tách mảng chính xác"""
    from config import Settings
    custom_settings = Settings(
        database_url="sqlite:///./test.db",
        jwt_secret="super-secret-test",
        cors_origins="https://app.com, https://admin.app.com"
    )
    assert custom_settings.cors_origins_list == ["https://app.com", "https://admin.app.com"]

def test_production_missing_ai_key_raises_error():
    """Kiểm tra khi chạy production mà thiếu AI_API_KEY thì bắt buộc phải báo lỗi"""
    from config import Settings
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            env="production",
            database_url="postgresql://user:pass@localhost:5432/tuvi",
            jwt_secret="secure-prod-key-12345",
            ai_api_key="" # Bỏ trống AI_API_KEY trong production
        )
    assert "BẮT BUỘC: Phải cấu hình AI_API_KEY khi chạy trong môi trường production" in str(exc_info.value)

def test_production_security_warning_on_dev_secret(caplog):
    """Kiểm tra log cảnh báo nguy hiểm khi production dùng dev-secret"""
    from config import Settings
    import logging
    with caplog.at_level(logging.WARNING):
        Settings(
            env="production",
            database_url="postgresql://user:pass@localhost:5432/tuvi",
            jwt_secret="dev-secret-key-change-in-production",
            ai_api_key="valid-prod-key"
        )
    assert "CẢNH BÁO NGUY HIỂM BẢO MẬT" in caplog.text
