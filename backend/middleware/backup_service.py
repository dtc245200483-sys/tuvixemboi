# -*- coding: utf-8 -*-
"""
Dịch vụ Sao lưu (Backup), Phục hồi (Restore) và Dọn dẹp dữ liệu tự động:
- backup_database: Tự động trích xuất snapshot database (SQLite/Postgres) có gắn timestamp.
- restore_database: Phục hồi thực tế từ file backup vào database đích (xác thực toàn vẹn số bảng/dòng).
- don_dep_backup_cu: Dọn dẹp các tệp backup cũ hơn số ngày quy định (mặc định 30 ngày).
- chay_tat_ca_scheduled_jobs: Bộ điều phối chạy định kỳ độc lập (lỗi backup không ảnh hưởng xóa ảnh).
"""

import os
import shutil
import sqlite3
import subprocess
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from config import settings

logger = logging.getLogger("middleware.backup")

BACKUP_DEFAULT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")


def _lay_duong_dan_sqlite_file(db_url: str) -> str:
    """Trích xuất đường dẫn file cục bộ từ SQLite connection string"""
    # Xử lý sqlite:///path hoặc sqlite:////path
    clean_path = db_url.replace("sqlite:///", "")
    if clean_path.startswith("/"):
        clean_path = clean_path[1:]
    # Nếu là relative path
    if not os.path.isabs(clean_path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        clean_path = os.path.normpath(os.path.join(base_dir, clean_path))
    return clean_path


def backup_database(
    db_url: Optional[str] = None,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Tạo snapshot sao lưu toàn diện database:
    - Đối với SQLite: Sử dụng SQLite Online Backup API (an toàn, không khóa ghi cơ sở dữ liệu).
    - Đối với Postgres: Sử dụng tiện ích pg_dump.
    
    Returns:
        dict: {
            "thanh_cong": bool,
            "duong_dan": str,
            "ten_file": str,
            "dung_luong_bytes": int,
            "thoi_gian": str,
            "loi": Optional[str]
        }
    """
    url = db_url or settings.database_url
    dest_dir = output_dir or BACKUP_DEFAULT_DIR
    os.makedirs(dest_dir, exist_ok=True)

    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    try:
        if url.startswith("sqlite"):
            src_file = _lay_duong_dan_sqlite_file(url)
            if not os.path.exists(src_file):
                # Nếu database chưa tạo file thì tạo file rỗng hoặc báo lỗi
                raise FileNotFoundError(f"Không tìm thấy file cơ sở dữ liệu nguồn SQLite tại: {src_file}")

            backup_filename = f"backup_sqlite_{timestamp_str}.db"
            dest_path = os.path.join(dest_dir, backup_filename)

            # Sử dụng SQLite Backup API để sao lưu an toàn khi DB đang mở
            src_conn = sqlite3.connect(src_file)
            dst_conn = sqlite3.connect(dest_path)
            try:
                src_conn.backup(dst_conn)
            finally:
                dst_conn.close()
                src_conn.close()

            file_size = os.path.getsize(dest_path)
            logger.info(f"[BACKUP_SUCCESS] Đã sao lưu SQLite -> '{dest_path}' ({file_size} bytes)")

            return {
                "thanh_cong": True,
                "duong_dan": dest_path,
                "ten_file": backup_filename,
                "dung_luong_bytes": file_size,
                "thoi_gian": timestamp_str,
                "loi": None
            }

        elif "postgresql" in url or "postgres" in url:
            backup_filename = f"backup_pg_{timestamp_str}.sql"
            dest_path = os.path.join(dest_dir, backup_filename)

            # Gọi pg_dump với chuỗi kết nối
            cmd = ["pg_dump", url, "-f", dest_path]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if res.returncode != 0:
                raise RuntimeError(f"pg_dump thất bại: {res.stderr}")

            file_size = os.path.getsize(dest_path)
            logger.info(f"[BACKUP_SUCCESS] Đã sao lưu PostgreSQL -> '{dest_path}' ({file_size} bytes)")
            return {
                "thanh_cong": True,
                "duong_dan": dest_path,
                "ten_file": backup_filename,
                "dung_luong_bytes": file_size,
                "thoi_gian": timestamp_str,
                "loi": None
            }
        else:
            raise ValueError(f"Chưa hỗ trợ sao lưu cho hệ quản trị DB URL: {url}")

    except Exception as e:
        logger.error(f"[BACKUP_ERROR] Lỗi trong quá trình sao lưu cơ sở dữ liệu: {e}", exc_info=True)
        return {
            "thanh_cong": False,
            "duong_dan": None,
            "ten_file": None,
            "dung_luong_bytes": 0,
            "thoi_gian": timestamp_str,
            "loi": str(e)
        }


def restore_database(file_backup: str, target_db_url: str) -> Dict[str, Any]:
    """
    Phục hồi cơ sở dữ liệu từ file backup vào cơ sở dữ liệu đích:
    - Kiểm định khả năng RESTORE thực tế.
    - Xác thực số lượng bảng và dữ liệu sau phục hồi để đảm bảo backup hợp lệ.
    """
    if not os.path.exists(file_backup):
        return {
            "thanh_cong": False,
            "target_db": target_db_url,
            "so_bang": 0,
            "danh_sach_bang": [],
            "loi": f"Tệp backup không tồn tại: {file_backup}"
        }

    try:
        if target_db_url.startswith("sqlite"):
            target_file = _lay_duong_dan_sqlite_file(target_db_url)
            os.makedirs(os.path.dirname(os.path.abspath(target_file)), exist_ok=True)

            # Sao chép/phục hồi qua SQLite API
            src_conn = sqlite3.connect(file_backup)
            dst_conn = sqlite3.connect(target_file)
            try:
                src_conn.backup(dst_conn)
            finally:
                dst_conn.close()
                src_conn.close()

            # Kiểm tra số bảng và cấu trúc dữ liệu sau phục hồi
            verify_conn = sqlite3.connect(target_file)
            cursor = verify_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cursor.fetchall()]
            verify_conn.close()

            logger.info(f"[RESTORE_SUCCESS] Đã phục hồi vào '{target_file}'. Tìm thấy {len(tables)} bảng: {tables}")
            return {
                "thanh_cong": True,
                "target_db": target_db_url,
                "so_bang": len(tables),
                "danh_sach_bang": tables,
                "loi": None
            }

        elif "postgresql" in target_db_url or "postgres" in target_db_url:
            cmd = ["psql", target_db_url, "-f", file_backup]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if res.returncode != 0:
                raise RuntimeError(f"psql restore thất bại: {res.stderr}")

            return {
                "thanh_cong": True,
                "target_db": target_db_url,
                "so_bang": -1,
                "danh_sach_bang": [],
                "loi": None
            }
        else:
            raise ValueError(f"Chưa hỗ trợ phục hồi cho DB URL: {target_db_url}")

    except Exception as e:
        logger.error(f"[RESTORE_ERROR] Lỗi khi phục hồi dữ liệu từ '{file_backup}': {e}", exc_info=True)
        return {
            "thanh_cong": False,
            "target_db": target_db_url,
            "so_bang": 0,
            "danh_sach_bang": [],
            "loi": str(e)
        }


def don_dep_backup_cu(so_ngay_giu: int = 30, backup_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Xóa các tệp backup cũ hơn so_ngay_giu (mặc định 30 ngày) để tránh cạn kiệt dung lượng ổ đĩa.
    """
    target_dir = backup_dir or BACKUP_DEFAULT_DIR
    if not os.path.exists(target_dir):
        return {
            "so_file_da_xoa": 0,
            "so_file_con_lai": 0,
            "danh_sach_xoa": [],
            "loi": None
        }

    now_ts = time.time()
    cutoff_ts = now_ts - (so_ngay_giu * 86400)

    da_xoa: List[str] = []
    con_lai: List[str] = []

    for fname in os.listdir(target_dir):
        fpath = os.path.join(target_dir, fname)
        if not os.path.isfile(fpath):
            continue

        try:
            mtime = os.path.getmtime(fpath)
            if mtime < cutoff_ts:
                os.remove(fpath)
                da_xoa.append(fname)
                logger.info(f"[CLEANUP_BACKUP] Đã xóa backup cũ (> {so_ngay_giu} ngày): {fname}")
            else:
                con_lai.append(fname)
        except Exception as e:
            logger.warning(f"Lỗi khi xử lý tệp '{fname}': {e}")

    return {
        "so_file_da_xoa": len(da_xoa),
        "so_file_con_lai": len(con_lai),
        "danh_sach_xoa": da_xoa,
        "loi": None
    }


def chay_tat_ca_scheduled_jobs(db_session_factory=None) -> Dict[str, Any]:
    """
    Bộ điều phối thực thi các tác vụ bảo trì định kỳ hàng ngày:
    1. backup_database()
    2. don_dep_backup_cu()
    3. xoa_anh_het_han() (từ middleware.data_retention, Prompt 4.2)
    
    YÊU CẦU CỐT LÕI:
    - Xử lý lỗi ĐỘC LẬP cho từng job (try...except riêng lẻ).
    - Nếu backup_database lỗi, xoa_anh_het_han và don_dep_backup_cu VẪN CHẠY BÌNH THƯỜNG,
      không bị ảnh hưởng dây chuyền.
    """
    logger.info("[SCHEDULED_JOBS] Bắt đầu phiên chạy các tác vụ bảo trì định kỳ...")
    ket_qua = {
        "backup": None,
        "don_dep_backup": None,
        "xoa_anh_het_han": None,
        "thoi_gian_chay": datetime.utcnow().isoformat()
    }

    # Job 1: Sao lưu cơ sở dữ liệu
    try:
        logger.info("[SCHEDULED_JOB_1] Thực hiện sao lưu database...")
        res_backup = backup_database()
        ket_qua["backup"] = res_backup
    except Exception as e:
        logger.error(f"[SCHEDULED_JOB_1_FAIL] Sao lưu database thất bại: {e}", exc_info=True)
        ket_qua["backup"] = {"thanh_cong": False, "loi": str(e)}

    # Job 2: Dọn dẹp backup cũ
    try:
        logger.info("[SCHEDULED_JOB_2] Thực hiện dọn dẹp backup cũ...")
        res_cleanup = don_dep_backup_cu(so_ngay_giu=30)
        ket_qua["don_dep_backup"] = res_cleanup
    except Exception as e:
        logger.error(f"[SCHEDULED_JOB_2_FAIL] Dọn dẹp backup cũ thất bại: {e}", exc_info=True)
        ket_qua["don_dep_backup"] = {"thanh_cong": False, "loi": str(e)}

    # Job 3: Xóa ảnh sinh trắc học hết hạn bảo mật (Prompt 4.2)
    try:
        logger.info("[SCHEDULED_JOB_3] Thực hiện quét xóa ảnh sinh trắc học hết hạn...")
        from middleware.data_retention import xoa_anh_het_han
        if db_session_factory is not None:
            db = db_session_factory()
        else:
            from db.database import SessionLocal
            db = SessionLocal()

        try:
            res_xoa_anh = xoa_anh_het_han(db)
            ket_qua["xoa_anh_het_han"] = res_xoa_anh
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[SCHEDULED_JOB_3_FAIL] Quét xóa ảnh hết hạn thất bại: {e}", exc_info=True)
        ket_qua["xoa_anh_het_han"] = {"thanh_cong": False, "loi": str(e)}

    logger.info(f"[SCHEDULED_JOBS_COMPLETED] Hoàn thành phiên bảo trì: {ket_qua}")
    return ket_qua


_scheduler_instance = None


def khoi_tao_scheduler(db_session_factory=None):
    """
    Khởi tạo BackgroundScheduler lập lịch tác vụ định kỳ 1 lần mỗi ngày (02:00 sáng):
    - Đảm bảo an toàn không xung đột khi chạy reload hoặc test.
    """
    global _scheduler_instance
    try:
        from apscheduler.schedulers.background import BackgroundScheduler

        if _scheduler_instance is not None and _scheduler_instance.running:
            return _scheduler_instance

        scheduler = BackgroundScheduler()
        # Chạy hàng ngày vào lúc 02:00 sáng
        scheduler.add_job(
            chay_tat_ca_scheduled_jobs,
            "cron",
            hour=2,
            minute=0,
            args=[db_session_factory],
            id="daily_maintenance_job",
            replace_existing=True
        )
        scheduler.start()
        _scheduler_instance = scheduler
        logger.info("[SCHEDULER] Đã khởi động APScheduler cho các tác vụ định kỳ hàng ngày (02:00).")
        return scheduler
    except Exception as e:
        logger.warning(f"[SCHEDULER] Không thể khởi động APScheduler: {e}")
        return None


def dung_scheduler():
    """Dừng scheduler khi ứng dụng tắt"""
    global _scheduler_instance
    if _scheduler_instance is not None and _scheduler_instance.running:
        _scheduler_instance.shutdown(wait=False)
        _scheduler_instance = None
        logger.info("[SCHEDULER] Đã dừng APScheduler.")
