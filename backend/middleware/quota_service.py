# -*- coding: utf-8 -*-
"""
Dịch vụ quản lý và kiểm soát hạn mức gọi AI hàng ngày (Usage Quota Service):
- Chống Race Condition bằng cơ chế Thread Lock kết hợp Atomic Update SQL.
- Tự động reset và khởi tạo hạn mức mới theo ngày.
- Kiểm tra trước khi gọi AI để tiết kiệm tài nguyên.
"""

import os
import sys
import uuid
import threading
import logging
from datetime import date, datetime, timedelta, time
from typing import Dict, Any, Union
from sqlalchemy.orm import Session

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from config import settings
    from db.models import UsageQuota, User
except ImportError:
    from backend.config import settings
    from backend.db.models import UsageQuota, User

logger = logging.getLogger("QuotaService")
_quota_lock = threading.Lock()


def _to_uuid(val: Any) -> uuid.UUID:
    if isinstance(val, uuid.UUID):
        return val
    try:
        return uuid.UUID(str(val))
    except Exception:
        return uuid.uuid5(uuid.NAMESPACE_DNS, str(val))


def _get_user_premium_status(uid: uuid.UUID, db: Session) -> bool:
    try:
        user = db.query(User).filter(User.id == uid).first()
        if not user or not user.is_premium:
            return False
        if user.premium_expires_at:
            from datetime import timezone
            now = datetime.now(timezone.utc) if user.premium_expires_at.tzinfo else datetime.utcnow()
            if user.premium_expires_at < now:
                return False
        return True
    except Exception:
        return False


def _get_reset_time_info():
    now = datetime.now()
    tomorrow_midnight = datetime.combine(date.today() + timedelta(days=1), time(0, 0, 0))
    seconds_left = max(0, int((tomorrow_midnight - now).total_seconds()))
    return seconds_left, tomorrow_midnight.isoformat()


def kiem_tra_va_tang_quota(user_id: Union[str, uuid.UUID], db: Session) -> Dict[str, Any]:
    """
    Kiểm tra hạn mức hàng ngày và tăng atomic lên 1 nếu còn lượt.
    Tránh tuyệt đối race condition khi nhiều request đồng thời.
    Nếu là tài khoản Premium -> không bị giới hạn lượt dùng.
    """
    if not db or not user_id:
        return {
            "con_han_muc": False,
            "so_luot_da_dung": 0,
            "so_luot_con_lai": 0,
            "thong_bao": "Yêu cầu không hợp lệ hoặc thiếu phiên kết nối database."
        }

    uid = _to_uuid(user_id)
    hom_nay = date.today()
    limit = getattr(settings, "ai_daily_quota_free_user", 50)
    sec_left, reset_iso = _get_reset_time_info()

    with _quota_lock:
        is_premium = _get_user_premium_status(uid, db)
        if is_premium:
            return {
                "con_han_muc": True,
                "so_luot_da_dung": 0,
                "so_luot_con_lai": 999999,
                "gioi_han_ngay": 999999,
                "is_premium": True,
                "so_giay_con_lai": sec_left,
                "thoi_gian_reset": reset_iso
            }

        # 1. Đảm bảo bản ghi cho ngày hôm nay tồn tại
        quota_record = (
            db.query(UsageQuota)
            .filter(UsageQuota.user_id == uid, UsageQuota.ngay == hom_nay)
            .first()
        )
        if not quota_record:
            try:
                new_record = UsageQuota(
                    id=uuid.uuid4(),
                    user_id=uid,
                    ngay=hom_nay,
                    so_luot_da_dung=0
                )
                db.add(new_record)
                db.commit()
            except Exception:
                db.rollback()

        # 2. Atomic Update: chỉ tăng nếu so_luot_da_dung < limit
        rows_updated = (
            db.query(UsageQuota)
            .filter(
                UsageQuota.user_id == uid,
                UsageQuota.ngay == hom_nay,
                UsageQuota.so_luot_da_dung < limit
            )
            .update(
                {UsageQuota.so_luot_da_dung: UsageQuota.so_luot_da_dung + 1},
                synchronize_session=False
            )
        )
        db.commit()

        # 3. Đọc lại số lượt hiện tại
        curr = (
            db.query(UsageQuota.so_luot_da_dung)
            .filter(UsageQuota.user_id == uid, UsageQuota.ngay == hom_nay)
            .scalar()
        ) or 0

        if rows_updated > 0:
            so_con_lai = max(0, limit - curr)
            return {
                "con_han_muc": True,
                "so_luot_da_dung": curr,
                "so_luot_con_lai": so_con_lai,
                "gioi_han_ngay": limit,
                "is_premium": False,
                "so_giay_con_lai": sec_left,
                "thoi_gian_reset": reset_iso
            }
        else:
            return {
                "con_han_muc": False,
                "so_luot_da_dung": curr,
                "so_luot_con_lai": 0,
                "gioi_han_ngay": limit,
                "is_premium": False,
                "so_giay_con_lai": sec_left,
                "thoi_gian_reset": reset_iso,
                "thong_bao": "Bạn đã dùng hết lượt an sao hôm nay, vui lòng đợi đến ngày mai hoặc nâng cấp Premium để tiếp tục."
            }


def lay_thong_tin_quota(user_id: Union[str, uuid.UUID], db: Session) -> Dict[str, Any]:
    """
    Lấy thông tin hạn mức hiện tại (chỉ đọc, không làm tăng quota).
    """
    if not db or not user_id:
        return {"con_han_muc": False, "so_luot_da_dung": 0, "so_luot_con_lai": 0}

    uid = _to_uuid(user_id)
    hom_nay = date.today()
    limit = getattr(settings, "ai_daily_quota_free_user", 50)
    sec_left, reset_iso = _get_reset_time_info()

    with _quota_lock:
        is_premium = _get_user_premium_status(uid, db)
        if is_premium:
            return {
                "so_luot_da_dung": 0,
                "so_luot_con_lai": 999999,
                "gioi_han_ngay": 999999,
                "con_han_muc": True,
                "is_premium": True,
                "so_giay_con_lai_den_reset": sec_left,
                "thoi_gian_reset": reset_iso
            }

        record = (
            db.query(UsageQuota)
            .filter(UsageQuota.user_id == uid, UsageQuota.ngay == hom_nay)
            .first()
        )
        da_dung = record.so_luot_da_dung if record else 0
        return {
            "so_luot_da_dung": da_dung,
            "so_luot_con_lai": max(0, limit - da_dung),
            "gioi_han_ngay": limit,
            "con_han_muc": da_dung < limit,
            "is_premium": False,
            "so_giay_con_lai_den_reset": sec_left,
            "thoi_gian_reset": reset_iso
        }


def hoan_lai_quota(user_id: Union[str, uuid.UUID], db: Session) -> None:
    """
    Hoàn lại 1 lượt quota khi gọi AI thất bại (do 429, timeout, sự cố mạng).
    Đảm bảo người dùng không bị mất lượt oan uổng.
    """
    if not db or not user_id:
        return

    uid = _to_uuid(user_id)
    hom_nay = date.today()

    with _quota_lock:
        try:
            db.query(UsageQuota).filter(
                UsageQuota.user_id == uid,
                UsageQuota.ngay == hom_nay,
                UsageQuota.so_luot_da_dung > 0
            ).update(
                {UsageQuota.so_luot_da_dung: UsageQuota.so_luot_da_dung - 1},
                synchronize_session=False
            )
            db.commit()
            logger.info(f"[QUOTA] Đã hoàn lại 1 lượt quota cho user {uid} do AI thất bại.")
        except Exception as ex:
            db.rollback()
            logger.warning(f"[QUOTA] Lỗi hoàn lại quota cho user {uid}: {ex}")

