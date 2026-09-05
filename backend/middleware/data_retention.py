# -*- coding: utf-8 -*-
"""
Middleware Qu?n L? L?u Tr? D? Li?u Sinh Tr?c H?c & T? ??ng X?a ??nh K?
Tu?n th? nghi?m ng?t nguy?n t?c b?o m?t th?ng tin c? nh?n:
- T? ??ng x?a file ?nh v?t l? v? x?a r?ng k?t qu? b?c t?ch JSON khi h?t h?n.
- Cung c?p hook v? h?m ??nh k? qu?t c?c b?n ghi ?? qu? h?n l?u tr?.
- Ghi log chi ti?t v?o audit log ?? ph?c v? ki?m to?n an to?n d? li?u.
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy.orm import Session

from db.models import TuongAnhResult

AUDIT_LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "logs"))
AUDIT_LOG_FILE = os.path.join(AUDIT_LOG_DIR, "data_retention_audit.log")


def ghi_audit_log(hanh_dong: str, ban_ghi_id: str, user_id: str, duong_dan: str, ly_do: str) -> None:
    """
    Ghi nh?n nh?t k? audit an to?n b?o m?t cho m?i thao t?c x?a d? li?u sinh tr?c h?c.
    """
    os.makedirs(AUDIT_LOG_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    log_line = (
        f"[{timestamp}] ACTION={hanh_dong} | RESULT_ID={ban_ghi_id} | "
        f"USER_ID={user_id} | PATH={duong_dan} | REASON={ly_do}\n"
    )
    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)


def xoa_anh_het_han(db: Session) -> Dict[str, Any]:
    """
    Qu?t to?n b? TuongAnhResult c? `ngay_het_han_luu_tru` ?? qua (<= hi?n t?i)
    v? `da_duoc_xoa = False`:
    1. X?a file v?t l? t?i `duong_dan_anh`.
    2. C?p nh?t `da_duoc_xoa = True`.
    3. X?a lu?n `dac_diem_quan_sat_json` (kh?ng gi? l?i d? li?u ph?n t?ch sau khi ?nh ?? x?a).
    4. Ghi log audit.
    5. Commit DB v? tr? v? {so_luong_da_xoa, danh_sach_id}.
    """
    now = datetime.utcnow()
    # T?m c?c b?n ghi ?? h?t h?n nh?ng ch?a ???c ??nh d?u x?a
    danh_sach_het_han = db.query(TuongAnhResult).filter(
        TuongAnhResult.ngay_het_han_luu_tru <= now,
        TuongAnhResult.da_duoc_xoa == False
    ).all()

    danh_sach_id = []

    for record in danh_sach_het_han:
        file_path = record.duong_dan_anh
        # 1. X?a file v?t l? tr?n ??a
        file_existed = False
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                file_existed = True
            except Exception as e:
                print(f"[C?NH B?O] Kh?ng th? x?a file v?t l? {file_path}: {e}")

        # 2. C?p nh?t tr?ng th?i trong Database
        record.da_duoc_xoa = True
        record.dac_diem_quan_sat_json = None  # X?a r?ng to?n b? d? li?u ph?n t?ch

        # 3. Ghi audit log
        ghi_audit_log(
            hanh_dong="AUTO_RETENTION_DELETE",
            ban_ghi_id=str(record.id),
            user_id=str(record.user_id),
            duong_dan=file_path,
            ly_do=f"H?t h?n l?u tr? (H?n: {record.ngay_het_han_luu_tru.isoformat() if record.ngay_het_han_luu_tru else 'N/A'})"
        )

        danh_sach_id.append(str(record.id))

    if danh_sach_id:
        db.commit()

    return {
        "so_luong_da_xoa": len(danh_sach_id),
        "danh_sach_id": danh_sach_id
    }
