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
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=False
)

# Kích hoạt tính năng Foreign Key Constraints cho SQLite (mặc định SQLite tắt FK)
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in settings.database_url:
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

    # Kiểm tra cột session_id trong chat_histories
    with engine.connect() as conn:
        try:
            from sqlalchemy import text
            if "sqlite" in settings.database_url:
                cols = [row[1] for row in conn.execute(text("PRAGMA table_info(chat_histories)")).fetchall()]
                if "session_id" not in cols:
                    conn.execute(text("ALTER TABLE chat_histories ADD COLUMN session_id CHAR(36)"))
                    conn.commit()
            else:
                conn.execute(text("ALTER TABLE chat_histories ADD COLUMN IF NOT EXISTS session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE"))
                conn.commit()
        except Exception:
            pass


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
