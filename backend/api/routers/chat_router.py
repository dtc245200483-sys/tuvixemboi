# -*- coding: utf-8 -*-
"""
Router Chat Tương tác Đa hệ thống:
- POST /chat: Đặt câu hỏi tự do (Topic Detection tự động phân loại hệ thống nếu không chỉ định).
- GET /chat/history: Phân trang lịch sử hội thoại của người dùng.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User, ChatHistory, TuongAnhResult
from auth.dependencies import get_current_user
from api.dependencies import kiem_tra_quota_truoc_khi_xu_ly
from api.schemas import (
    APIResponse,
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    ChatHistoryItem
)
from interpretation_api.orchestrator.main_flow import luan_giai

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=APIResponse[ChatResponse])
def gui_cau_hoi_chat(
    req: ChatRequest,
    current_user: User = Depends(kiem_tra_quota_truoc_khi_xu_ly),
    db: Session = Depends(get_db)
):
    """
    Gửi câu hỏi tự do tới trợ lý phong thủy.
    - Tự động nhận diện chủ đề huyền học (Topic Detection).
    - Tra cứu tri thức chuẩn xác và sinh luận giải cá nhân hóa.
    - Tự động kiểm duyệt Content Safety và ghi nhận ChatHistory.
    """
    du_lieu = {}
    co_anh = False

    if req.reference_id:
        du_lieu["reference_id"] = req.reference_id
        du_lieu["id"] = req.reference_id
        # Tra cứu đặc điểm ảnh nếu reference_id là ảnh sinh trắc học
        try:
            ref_uuid = uuid.UUID(req.reference_id)
            img_rec = db.query(TuongAnhResult).filter(
                TuongAnhResult.id == ref_uuid,
                TuongAnhResult.user_id == current_user.id
            ).first()
            if img_rec:
                du_lieu.update(img_rec.dac_diem_quan_sat_json or {})
                du_lieu["loai_anh"] = img_rec.loai_anh
                co_anh = True
                if not req.he_thong:
                    du_lieu["he_thong"] = "nhan_tuong"
        except Exception:
            pass

    if req.he_thong:
        du_lieu["he_thong"] = req.he_thong

    res = luan_giai(
        user_id=str(current_user.id),
        cau_hoi=req.cau_hoi,
        du_lieu_dau_vao=du_lieu,
        co_dinh_kem_anh=co_anh,
        la_tong_quan=False,
        db=db
    )

    noi_dung_tra_loi = ""
    if isinstance(res.get("cau_tra_loi"), dict):
        noi_dung_tra_loi = (
            res["cau_tra_loi"].get("noi_dung") or
            res["cau_tra_loi"].get("loi_khuyen") or
            str(res["cau_tra_loi"])
        )
    elif res.get("cau_tra_loi"):
        noi_dung_tra_loi = str(res.get("cau_tra_loi"))
    elif res.get("thong_bao"):
        noi_dung_tra_loi = res.get("thong_bao", "")

    # Coi can_hoi_lai hoặc chua_co_du_lieu là tin nhắn hợp lệ trả về cho người dùng
    is_success = bool(
        res.get("thanh_cong") or
        res.get("can_hoi_lai") or
        res.get("chua_co_du_lieu")
    )

    return APIResponse(
        thanh_cong=is_success,
        du_lieu={
            "he_thong": res.get("he_thong"),
            "cau_hoi": req.cau_hoi,
            "tra_loi": noi_dung_tra_loi,
            "chi_tiet": res
        },
        loi=None if is_success else res.get("thong_bao")
    )


@router.get("/history", response_model=APIResponse[ChatHistoryResponse])
def xem_lich_su_chat(
    page: int = Query(default=1, ge=1, description="Số thứ tự trang"),
    page_size: int = Query(default=20, ge=1, le=100, description="Số lượng bản ghi mỗi trang"),
    he_thong: Optional[str] = Query(default=None, description="Lọc theo hệ thống (tu_vi, kinh_dich, bat_tu, nhan_tuong)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Xem lịch sử trò chuyện của người dùng với tính năng phân trang.
    """
    query = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id)
    if he_thong:
        query = query.filter(ChatHistory.he_thong == he_thong)

    total = query.count()
    offset = (page - 1) * page_size
    records = query.order_by(ChatHistory.created_at.desc()).offset(offset).limit(page_size).all()

    items = [
        ChatHistoryItem(
            id=str(r.id),
            he_thong=r.he_thong,
            reference_id=str(r.reference_id) if r.reference_id else None,
            cau_hoi=r.cau_hoi,
            tra_loi=r.tra_loi,
            created_at=r.created_at
        )
        for r in records
    ]

    return APIResponse(
        thanh_cong=True,
        du_lieu=ChatHistoryResponse(
            tong_so=total,
            trang=page,
            kich_thuoc_trang=page_size,
            danh_sach=items
        ),
        loi=None
    )
