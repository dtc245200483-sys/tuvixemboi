# -*- coding: utf-8 -*-
"""
Script Tự Động Khởi Tạo & Triển Khai Cơ Sở Dữ Liệu Sản Xuất (Production DB Deploy & Seed)
1. Thực thi Alembic Migrations (`alembic upgrade head`) nhắm vào DATABASE_URL sản xuất.
2. Kiểm tra xác nhận toàn bộ 8 bảng được tạo thành công.
3. Chạy pipeline nạp dữ liệu tri thức Knowledge Base (`nap_toan_bo()`) vào ChromaDB Vector Store.
"""

import os
import sys
import logging

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from sqlalchemy import inspect

# Đảm bảo đường dẫn import
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

ROOT_DIR = os.path.abspath(os.path.join(BACKEND_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import settings
from db.database import engine
from alembic.config import Config
from alembic import command
from knowledge_base.ingest_pipeline import nap_toan_bo

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("deploy_db")

EXPECTED_TABLES = [
    "users",
    "birth_profiles",
    "la_so_tu_vi_results",
    "tu_tru_results",
    "que_kinh_dich_results",
    "tuong_anh_results",
    "chat_histories",
    "usage_quotas"
]


def run_database_migrations():
    """Chạy Alembic upgrade head lên database đích"""
    logger.info(f"Bắt đầu chạy Alembic migration lên database: [{settings.database_url.split('@')[-1] if '@' in settings.database_url else 'local'}]")
    alembic_ini_path = os.path.join(BACKEND_DIR, "alembic.ini")
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("script_location", os.path.join(BACKEND_DIR, "db", "migrations"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)

    try:
        command.upgrade(alembic_cfg, "head")
        logger.info("Hoàn tất lệnh 'alembic upgrade head' thành công!")
    except Exception as e:
        if "already exists" in str(e).lower():
            logger.info("Các bảng đã tồn tại từ trước, đồng bộ phiên bản: 'alembic stamp head'...")
            command.stamp(alembic_cfg, "head")
            logger.info("Đã đồng bộ 'alembic stamp head' thành công!")
        else:
            raise e


def verify_tables():
    """Kiểm tra xác nhận các bảng đã tồn tại trong database"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    logger.info(f"Các bảng hiện có trong database: {existing_tables}")

    missing = [tbl for tbl in EXPECTED_TABLES if tbl not in existing_tables]
    if missing:
        logger.error(f"Thiếu các bảng sau trong cơ sở dữ liệu: {missing}")
        raise RuntimeError(f"Database migration chưa tạo đủ bảng: {missing}")
    
    logger.info(f"XÁC NHẬN: Toàn bộ {len(EXPECTED_TABLES)}/{len(EXPECTED_TABLES)} bảng cốt lõi đã được tạo chuẩn xác!")


def seed_knowledge_base():
    """Nạp dữ liệu tri thức vào ChromaDB vector store"""
    logger.info(f"Bắt đầu nạp tri thức Knowledge Base vào Vector Store: [{settings.vector_db_path}]")
    custom_root = os.path.join(ROOT_DIR, "Data_training", "rewritten")
    report = nap_toan_bo(custom_root=custom_root, custom_db_path=settings.vector_db_path)
    
    logger.info(f"Kết quả nạp tri thức: Tổng {report.get('tong_so_item_toan_he_thong', 0)} items trên 4 hệ thống.")
    for sys_name, res in report.get("cac_he_thong", {}).items():
        logger.info(f" - Hệ thống [{sys_name}]: {res.get('tong_so_item_da_nap', 0)} items đã nạp ({res.get('ghi_chu') or 'Thành công'})")


def main():
    print("=" * 80)
    print("TRIỂN KHAI & NẠP DỮ LIỆU CƠ SỞ DỮ LIỆU SẢN XUẤT (DATABASE DEPLOYMENT PIPELINE)")
    print("=" * 80)
    try:
        run_database_migrations()
        verify_tables()
        seed_knowledge_base()
        print("=" * 80)
        print("TRIỂN KHAI DATABASE & VECTOR STORE HOÀN TẤT THÀNH CÔNG 100%!")
        print("=" * 80)
    except Exception as e:
        logger.error(f"Thất bại trong quá trình triển khai database: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
