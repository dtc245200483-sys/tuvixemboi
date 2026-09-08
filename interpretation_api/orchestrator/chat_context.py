# -*- coding: utf-8 -*-
"""
Quản lý ngữ cảnh hội thoại (Chat Context) thông qua ChatHistory:
- lay_lich_su_chat: Trích xuất các tin nhắn gần nhất của người dùng.
- luu_lich_su_chat: Lưu lại câu hỏi và phản hồi sau khi luận giải thành công.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import desc

try:
    from db.models import ChatHistory
except ImportError:
    from backend.db.models import ChatHistory

logger = logging.getLogger("ChatContext")


def _to_uuid(val: Any) -> Any:
    """Chuyển đổi chuỗi hex hoặc uuid sang đối tượng uuid.UUID hợp lệ cho SQLAlchemy."""
    if val is None:
        return None
    if isinstance(val, uuid.UUID):
        return val
    try:
        return uuid.UUID(str(val))
    except Exception:
        # Nếu không phải UUID hợp lệ, tạo deterministic UUID từ chuỗi
        return uuid.uuid5(uuid.NAMESPACE_DNS, str(val))


def lay_lich_su_chat(
    user_id: Union[str, uuid.UUID],
    so_luong_gan_nhat: int = 5,
    session_id: Optional[Union[str, uuid.UUID]] = None,
    db: Optional[Session] = None
) -> List[Dict[str, Any]]:
    """
    Lấy N tin nhắn gần nhất của người dùng từ ChatHistory.
    Nếu có session_id, cô lập chỉ lấy lịch sử thuộc phiên trò chuyện đó.
    Sắp xếp theo trình tự thời gian tự nhiên (để truyền vào prompt).
    """
    if not db or not user_id:
        return []

    try:
        uid = _to_uuid(user_id)
        query = db.query(ChatHistory).filter(ChatHistory.user_id == uid)
        if session_id:
            sid = _to_uuid(session_id)
            query = query.filter(ChatHistory.session_id == sid)

        records = (
            query.order_by(desc(ChatHistory.created_at))
            .limit(so_luong_gan_nhat)
            .all()
        )
        # Đảo ngược lại để có thứ tự từ cũ đến mới
        records_sorted = sorted(records, key=lambda x: x.created_at)

        history = []
        for r in records_sorted:
            history.append({
                "role": "user",
                "content": r.cau_hoi,
                "he_thong": r.he_thong,
                "reference_id": str(r.reference_id) if r.reference_id else None,
                "session_id": str(r.session_id) if r.session_id else None,
                "created_at": r.created_at
            })
            history.append({
                "role": "assistant",
                "content": r.tra_loi,
                "he_thong": r.he_thong,
                "reference_id": str(r.reference_id) if r.reference_id else None,
                "session_id": str(r.session_id) if r.session_id else None,
                "created_at": r.created_at
            })
        return history
    except Exception as e:
        logger.warning(f"Lỗi khi lấy lịch sử chat của user {user_id}: {str(e)}")
        return []


def luu_lich_su_chat(
    user_id: Union[str, uuid.UUID],
    he_thong: str,
    cau_hoi: str,
    tra_loi: str,
    reference_id: Optional[Union[str, uuid.UUID]] = None,
    session_id: Optional[Union[str, uuid.UUID]] = None,
    db: Optional[Session] = None
) -> Optional[ChatHistory]:
    """
    Lưu lại cuộc trao đổi vào bảng ChatHistory sau khi luận giải thành công.
    Hỗ trợ liên kết session_id cho từng cuộc trò chuyện độc lập.
    """
    if not db or not user_id:
        return None

    try:
        uid = _to_uuid(user_id)
        ref_id = _to_uuid(reference_id) if reference_id else None
        s_id = _to_uuid(session_id) if session_id else None

        entry = ChatHistory(
            id=uuid.uuid4(),
            user_id=uid,
            session_id=s_id,
            he_thong=he_thong,
            cau_hoi=cau_hoi,
            tra_loi=tra_loi,
            reference_id=ref_id
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi lưu lịch sử chat: {str(e)}")
        return None
