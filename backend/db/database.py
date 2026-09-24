# -*- coding: utf-8 -*-
"""
Khởi tạo kết nối cơ sở dữ liệu SQLAlchemy và session management.
"""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from config import settings

connect_args = {}
db_url = settings.database_url
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    echo=False
)

# Kích hoạt tính năng Foreign Key Constraints cho SQLite (mặc định SQLite tắt FK)
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in db_url:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def init_db():
    """
    Khởi tạo các bảng và thực hiện auto-migration an toàn nếu có bảng/cột mới.
    """
    import db.models  # Nạp toàn bộ models
    Base.metadata.create_all(bind=engine)

    # Tự động đồng bộ các cột mới trong users, birth_profiles, chat_histories
    with engine.connect() as conn:
        try:
            from sqlalchemy import text
            is_sqlite = "sqlite" in settings.database_url.lower()

            if is_sqlite:
                # 1. users table
                u_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(users)")).fetchall()]
                if "da_dong_y_sinh_trac_hoc" not in u_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN da_dong_y_sinh_trac_hoc BOOLEAN DEFAULT 0"))
                if "thoi_gian_dong_y_sinh_trac_hoc" not in u_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN thoi_gian_dong_y_sinh_trac_hoc DATETIME"))
                if "is_premium" not in u_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_premium BOOLEAN DEFAULT 0"))
                if "premium_expires_at" not in u_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN premium_expires_at DATETIME"))
                if "default_birth_profile_id" not in u_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN default_birth_profile_id CHAR(36)"))

                # 2. birth_profiles table
                bp_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(birth_profiles)")).fetchall()]
                if "is_default" not in bp_cols:
                    conn.execute(text("ALTER TABLE birth_profiles ADD COLUMN is_default BOOLEAN DEFAULT 0"))
                if "is_quick_chart" not in bp_cols:
                    conn.execute(text("ALTER TABLE birth_profiles ADD COLUMN is_quick_chart BOOLEAN DEFAULT 0"))

                # 3. chat_histories table
                ch_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(chat_histories)")).fetchall()]
                if "session_id" not in ch_cols:
                    conn.execute(text("ALTER TABLE chat_histories ADD COLUMN session_id CHAR(36)"))

                conn.commit()
            else:
                # PostgreSQL
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS da_dong_y_sinh_trac_hoc BOOLEAN DEFAULT FALSE"))
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS thoi_gian_dong_y_sinh_trac_hoc TIMESTAMP WITH TIME ZONE"))
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_premium BOOLEAN DEFAULT FALSE"))
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS premium_expires_at TIMESTAMP WITH TIME ZONE"))
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS default_birth_profile_id UUID"))

                conn.execute(text("ALTER TABLE birth_profiles ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT FALSE"))
                conn.execute(text("ALTER TABLE birth_profiles ADD COLUMN IF NOT EXISTS is_quick_chart BOOLEAN DEFAULT FALSE"))

                conn.execute(text("ALTER TABLE chat_histories ADD COLUMN IF NOT EXISTS session_id UUID"))
                conn.commit()
        except Exception:
            conn.rollback()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection generator cung cấp SQLAlchemy session cho FastAPI endpoints.
    Đảm bảo session luôn được đóng an toàn kể cả khi có Exception.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
