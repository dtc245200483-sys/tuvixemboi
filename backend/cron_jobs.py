# -*- coding: utf-8 -*-
"""
Script Thực Thi Định Kỳ Độc Lập (Standalone Cron Job Entrypoint)
Sử dụng cho các nền tảng PaaS (Render Cron, Railway Cron, Kubernetes CronJob, hoặc Linux crontab)
thay thế hoặc bổ trợ cho APScheduler trong container web.

Tác vụ thực hiện:
1. Sao lưu cơ sở dữ liệu (PostgreSQL qua pg_dump / SQLite backup API)
2. Dọn dẹp tệp sao lưu cũ hơn 30 ngày
3. Quét và xóa vĩnh viễn tệp ảnh sinh trắc học hết hạn lưu trữ bảo mật (Prompt 4.2)
"""

import os
import sys
import json
import logging
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Đảm bảo đường dẫn import cho backend và các module liên quan
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

ROOT_DIR = os.path.abspath(os.path.join(BACKEND_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import settings
from db.database import SessionLocal
from middleware.backup_service import chay_tat_ca_scheduled_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - [CRON_JOB] %(message)s"
)
logger = logging.getLogger("cron_jobs")


def main():
    logger.info(f"Khởi động phiên bảo trì định kỳ lúc: {datetime.utcnow().isoformat()} UTC")
    logger.info(f"Môi trường: [{settings.env}] | Database: [{settings.database_url.split('@')[-1] if '@' in settings.database_url else 'local'}]")

    try:
        ket_qua = chay_tat_ca_scheduled_jobs(db_session_factory=SessionLocal)
        logger.info("Hoàn tất tác vụ bảo trì định kỳ:")
        print(json.dumps(ket_qua, ensure_ascii=False, indent=2))
        
        # Kiểm tra xem có lỗi nghiêm trọng không
        has_error = False
        for job_name in ["backup", "don_dep_backup", "xoa_anh_het_han"]:
            job_res = ket_qua.get(job_name)
            if job_res and isinstance(job_res, dict) and job_res.get("thanh_cong") is False:
                logger.warning(f"Cảnh báo: Tác vụ {job_name} báo lỗi: {job_res.get('loi')}")

        logger.info("Phiên bảo trì kết thúc thành công.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Lỗi nghiêm trọng khi thực hiện bảo trì định kỳ: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
