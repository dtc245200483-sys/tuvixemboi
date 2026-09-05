# -*- coding: utf-8 -*-
"""
Dịch vụ Cache Luận Giải (Interpretation Cache Service):
- Lưu trữ kết quả luận giải cố định (tổng quan lá số/quẻ) theo TTL.
- Tránh gọi lại AI tốn kém chi phí khi người dùng tra cứu lại cùng 1 lá số.
- Hỗ trợ xóa cache theo hệ thống (Cache Invalidation) khi cập nhật Knowledge Base.
"""

import os
import sys
import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from db.models import InterpretationCache
except ImportError:
    from backend.db.models import InterpretationCache

logger = logging.getLogger("InterpretationCacheService")


def tao_cache_key(he_thong: str, reference_id: str, cau_hoi: Optional[str] = None) -> str:
    """
    Tạo khóa cache duy nhất dựa trên hệ thống + reference_id + câu hỏi (nếu có).
    Sử dụng SHA-256 để đảm bảo không bị trùng lặp và chiều dài chuẩn dưới 255 ký tự.
    """
    c_clean = cau_hoi.strip().lower() if cau_hoi else "__tong_quan__"
    raw = f"{he_thong.strip().lower()}:{reference_id.strip()}:{c_clean}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{he_thong}_{reference_id[:8]}_{digest[:24]}"


def lay_ket_qua_cache(cache_key: str, db: Session) -> Optional[Dict[str, Any]]:
    """
    Tìm kết quả luận giải trong cache nếu còn hạn (het_han_luc > now).
    Trả về dict kết quả hoặc None nếu không có/hết hạn.
    """
    if not db or not cache_key:
        return None

    try:
        entry = (
            db.query(InterpretationCache)
            .filter(InterpretationCache.cache_key == cache_key)
            .first()
        )
        if not entry:
            return None

        # Kiểm tra TTL
        now = datetime.utcnow()
        if entry.het_han_luc <= now:
            logger.info(f"Cache key {cache_key} đã hết hạn.")
            return None

        return entry.ket_qua_json
    except Exception as e:
        logger.warning(f"Lỗi khi truy vấn cache ({cache_key}): {str(e)}")
        return None


def luu_ket_qua_cache(
    cache_key: str,
    he_thong: str,
    ket_qua: Dict[str, Any],
    db: Session,
    ttl_ngay: int = 7
) -> bool:
    """
    Lưu kết quả mới vào cache với thời hạn TTL (mặc định 7 ngày).
    """
    if not db or not cache_key or not ket_qua:
        return False

    try:
        now = datetime.utcnow()
        expire_at = now + timedelta(days=ttl_ngay)

        entry = (
            db.query(InterpretationCache)
            .filter(InterpretationCache.cache_key == cache_key)
            .first()
        )

        if entry:
            entry.ket_qua_json = ket_qua
            entry.het_han_luc = expire_at
            entry.tao_luc = now
        else:
            entry = InterpretationCache(
                id=uuid.uuid4(),
                he_thong=he_thong,
                cache_key=cache_key,
                ket_qua_json=ket_qua,
                tao_luc=now,
                het_han_luc=expire_at
            )
            db.add(entry)

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.warning(f"Lỗi khi lưu cache ({cache_key}): {str(e)}")
        return False


def xoa_cache_theo_he_thong(he_thong: str, db: Session) -> int:
    """
    Xóa toàn bộ cache của 1 hệ thống (Invalidate khi cập nhật Knowledge Base).
    """
    if not db or not he_thong:
        return 0

    try:
        deleted = (
            db.query(InterpretationCache)
            .filter(InterpretationCache.he_thong == he_thong)
            .delete(synchronize_session=False)
        )
        db.commit()
        logger.info(f"Đã xóa {deleted} bản ghi cache của hệ thống '{he_thong}'.")
        return deleted
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi xóa cache hệ thống '{he_thong}': {str(e)}")
        return 0
