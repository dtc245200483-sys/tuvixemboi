# -*- coding: utf-8 -*-
"""
Router Chat Tương tác Đa hệ thống:
- Quản lý phiên trò chuyện (ChatSession): Danh sách tối đa 20 cuộc trò chuyện gần nhất.
- Hỗ trợ tạo mới, xóa từng cuộc trò chuyện độc lập, phân trang tin nhắn trong cuộc trò chuyện.
- Luận giải có ghi nhớ ngữ cảnh Hồ Sơ Mệnh Đang Chọn và tuyệt đối nghiêm cấm từ ngữ cực đoan.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User, ChatHistory, ChatSession, BirthProfile, TuongAnhResult
from auth.dependencies import get_current_user
from api.dependencies import kiem_tra_quota_truoc_khi_xu_ly
from api.schemas import (
    APIResponse,
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    ChatHistoryItem,
    ChatSessionItem,
    ChatSessionListResponse,
    ChatSessionCreateRequest
)
from interpretation_api.orchestrator.main_flow import luan_giai

router = APIRouter(prefix="/chat", tags=["Chat"])


def _prune_old_sessions(user_id: uuid.UUID, db: Session, keep_count: int = 20):
    """Đảm bảo mỗi người dùng chỉ lưu tối đa keep_count cuộc trò chuyện gần nhất."""
    try:
        sessions = (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .all()
        )
        if len(sessions) > keep_count:
            to_delete = sessions[keep_count:]
            for s in to_delete:
                db.delete(s)
            db.commit()
    except Exception:
        db.rollback()


@router.get("/sessions", response_model=APIResponse[ChatSessionListResponse])
def lay_danh_sach_phien_chat(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách tối đa 20 cuộc trò chuyện gần nhất của người dùng.
    """
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .limit(20)
        .all()
    )
    items = []
    for s in sessions:
        msg_count = db.query(ChatHistory).filter(ChatHistory.session_id == s.id).count()
        last_msg = (
            db.query(ChatHistory)
            .filter(ChatHistory.session_id == s.id)
            .order_by(ChatHistory.created_at.desc())
            .first()
        )
        preview = None
        if last_msg:
            preview = last_msg.tra_loi[:80] if last_msg.tra_loi else last_msg.cau_hoi[:80]

        items.append(
            ChatSessionItem(
                id=str(s.id),
                tieu_de=s.tieu_de,
                created_at=s.created_at,
                updated_at=s.updated_at,
                so_tin_nhan=msg_count,
                tin_nhan_cuoi=preview
            )
        )

    return APIResponse(
        thanh_cong=True,
        du_lieu=ChatSessionListResponse(
            danh_sach=items,
            tong_so=len(items)
        ),
        loi=None
    )


@router.post("/sessions", response_model=APIResponse[ChatSessionItem])
def tao_phien_chat_moi(
    req: Optional[ChatSessionCreateRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo một cuộc trò chuyện mới độc lập.
    Đảm bảo chỉ lưu tối đa 20 cuộc trò chuyện gần nhất (cắt tỉa phiên cũ).
    """
    _prune_old_sessions(current_user.id, db, keep_count=19)
    title = (req.tieu_de if req and req.tieu_de else "Cuộc trò chuyện mới").strip()
    new_sess = ChatSession(
        id=uuid.uuid4(),
        user_id=current_user.id,
        tieu_de=title or "Cuộc trò chuyện mới",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_sess)
    db.commit()
    db.refresh(new_sess)

    return APIResponse(
        thanh_cong=True,
        du_lieu=ChatSessionItem(
            id=str(new_sess.id),
            tieu_de=new_sess.tieu_de,
            created_at=new_sess.created_at,
            updated_at=new_sess.updated_at,
            so_tin_nhan=0,
            tin_nhan_cuoi=None
        ),
        loi=None
    )


@router.delete("/sessions/{session_id}", response_model=APIResponse[dict])
def xoa_phien_chat(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Xóa riêng một cuộc trò chuyện và toàn bộ tin nhắn bên trong.
    """
    try:
        s_uuid = uuid.UUID(session_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID cuộc trò chuyện không hợp lệ")

    sess = db.query(ChatSession).filter(
        ChatSession.id == s_uuid,
        ChatSession.user_id == current_user.id
    ).first()

    if not sess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy cuộc trò chuyện này")

    db.delete(sess)
    db.commit()

    return APIResponse(
        thanh_cong=True,
        du_lieu={"thanh_cong": True, "thong_bao": "Đã xóa cuộc trò chuyện thành công"},
        loi=None
    )


@router.get("/sessions/{session_id}/messages", response_model=APIResponse[ChatHistoryResponse])
def lay_tin_nhan_phien_chat(
    session_id: str,
    page: int = Query(default=1, ge=1, description="Số thứ tự trang"),
    page_size: int = Query(default=15, ge=1, le=100, description="Số lượng tin nhắn mỗi trang"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phân trang tin nhắn trong một cuộc trò chuyện cụ thể.
    Hỗ trợ nút 'Cuộn lên hoặc bấm để xem thêm tin nhắn cũ'.
    """
    try:
        s_uuid = uuid.UUID(session_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID cuộc trò chuyện không hợp lệ")

    sess = db.query(ChatSession).filter(
        ChatSession.id == s_uuid,
        ChatSession.user_id == current_user.id
    ).first()

    if not sess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy cuộc trò chuyện này")

    query = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id,
        ChatHistory.session_id == s_uuid
    )
    total = query.count()
    offset = (page - 1) * page_size
    records = query.order_by(ChatHistory.created_at.desc()).offset(offset).limit(page_size).all()

    # Sắp xếp lại theo thời gian tăng dần để hiển thị tự nhiên trong khung chat
    items = [
        ChatHistoryItem(
            id=str(r.id),
            session_id=str(r.session_id) if r.session_id else None,
            he_thong=r.he_thong,
            reference_id=str(r.reference_id) if r.reference_id else None,
            cau_hoi=r.cau_hoi,
            tra_loi=r.tra_loi,
            created_at=r.created_at
        )
        for r in reversed(records)
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


@router.post("", response_model=APIResponse[ChatResponse])
def gui_cau_hoi_chat(
    req: ChatRequest,
    current_user: User = Depends(kiem_tra_quota_truoc_khi_xu_ly),
    db: Session = Depends(get_db)
):
    """
    Gửi câu hỏi tự do tới trợ lý phong thủy.
    - Quản lý phiên trò chuyện riêng biệt.
    - Nạp ngữ cảnh hồ sơ mệnh chủ đang đàm đạo.
    - Tuân thủ quy chuẩn an toàn nội dung (Content Safety Softener).
    """
    du_lieu = {}
    co_anh = False

    # 1. Xác định hoặc tạo phiên trò chuyện (ChatSession)
    active_session = None
    if req.session_id:
        try:
            s_uuid = uuid.UUID(req.session_id)
            active_session = db.query(ChatSession).filter(
                ChatSession.id == s_uuid,
                ChatSession.user_id == current_user.id
            ).first()
        except Exception:
            pass

    if not active_session:
        _prune_old_sessions(current_user.id, db, keep_count=19)
        raw_title = req.cau_hoi.strip() if req.cau_hoi else "Cuộc trò chuyện mới"
        title = raw_title[:45] + ("..." if len(raw_title) > 45 else "")
        active_session = ChatSession(
            id=uuid.uuid4(),
            user_id=current_user.id,
            tieu_de=title or "Cuộc trò chuyện mới",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(active_session)
        db.commit()
        db.refresh(active_session)
    else:
        active_session.updated_at = datetime.utcnow()
        if active_session.tieu_de == "Cuộc trò chuyện mới" and req.cau_hoi:
            raw_title = req.cau_hoi.strip()
            active_session.tieu_de = raw_title[:45] + ("..." if len(raw_title) > 45 else "")
        db.commit()

    du_lieu["session_id"] = str(active_session.id)

    # 2. Bổ sung ngữ cảnh hồ sơ mệnh chủ (người hỏi)
    profile = None
    if req.birth_profile_id:
        try:
            p_uuid = uuid.UUID(req.birth_profile_id)
            profile = db.query(BirthProfile).filter(
                BirthProfile.id == p_uuid,
                BirthProfile.user_id == current_user.id
            ).first()
        except Exception:
            pass

    if not profile and current_user.default_birth_profile_id:
        profile = db.query(BirthProfile).filter(
            BirthProfile.id == current_user.default_birth_profile_id,
            BirthProfile.user_id == current_user.id
        ).first()

    if not profile:
        profile = (
            db.query(BirthProfile)
            .filter(BirthProfile.user_id == current_user.id)
            .order_by(BirthProfile.is_default.desc(), BirthProfile.created_at.asc())
            .first()
        )

    if profile:
        du_lieu["ho_so_menh_chu"] = {
            "id": str(profile.id),
            "ho_ten": profile.ho_ten,
            "gioi_tinh": profile.gioi_tinh,
            "ngay_sinh_duong": profile.ngay_sinh_duong.isoformat() if hasattr(profile.ngay_sinh_duong, "isoformat") else str(profile.ngay_sinh_duong),
            "gio_sinh": profile.gio_sinh,
            "phut_sinh": profile.phut_sinh,
            "ngay_sinh_am": profile.ngay_sinh_am.isoformat() if hasattr(profile.ngay_sinh_am, "isoformat") else (str(profile.ngay_sinh_am) if profile.ngay_sinh_am else None)
        }
        # Tự động lập hoặc lấy lá số Tử Vi của hồ sơ này để đưa vào ngữ cảnh luận giải chuyên sâu
        try:
            from db.models import LaSoTuViResult
            from astro_engine.tu_vi import lap_la_so
            la_so_record = db.query(LaSoTuViResult).filter(LaSoTuViResult.birth_profile_id == profile.id).first()
            if la_so_record and la_so_record.du_lieu_json:
                la_so_data = la_so_record.du_lieu_json
            else:
                la_so_data = lap_la_so(
                    ho_ten=profile.ho_ten,
                    ngay_sinh_duong=profile.ngay_sinh_duong,
                    gio_sinh=profile.gio_sinh or 12,
                    phut_sinh=profile.phut_sinh or 0,
                    gioi_tinh=profile.gioi_tinh or "nam"
                )
            if la_so_data and isinstance(la_so_data, dict):
                for k, v in la_so_data.items():
                    if k not in du_lieu:
                        du_lieu[k] = v
        except Exception as e:
            logger.warning(f"Lỗi khi nạp lá số Tử Vi vào chat: {e}")

    # 3. Trích xuất đặc điểm ảnh đính kèm nếu có
    if req.reference_id:
        du_lieu["reference_id"] = req.reference_id
        du_lieu["id"] = req.reference_id
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

    # 4. Thực thi quy trình luận giải Orchestrator
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

    # Khi AI hỏi lại (can_hoi_lai), thêm thông tin hồ sơ đang có để người dùng không nhầm phải nhập lại
    if res.get("can_hoi_lai") and profile:
        ho_ten = profile.ho_ten or "bạn"
        ngay_sinh = profile.ngay_sinh_duong.strftime("%d/%m/%Y") if hasattr(profile.ngay_sinh_duong, "strftime") else str(profile.ngay_sinh_duong)
        noi_dung_tra_loi = (
            f"Dạ {ho_ten} (sinh {ngay_sinh}), "
            + (noi_dung_tra_loi or "bạn muốn tra cứu vận mệnh theo Tử Vi Đẩu Số, gieo quẻ Kinh Dịch, xem Bát Tự Tứ Trụ hay xem tướng mạo/chỉ tay ạ?")
        )

    is_success = bool(
        res.get("thanh_cong") or
        res.get("can_hoi_lai") or
        res.get("chua_co_du_lieu")
    )

    return APIResponse(
        thanh_cong=is_success,
        du_lieu={
            "session_id": str(active_session.id) if active_session else None,
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
    session_id: Optional[str] = Query(default=None, description="Lọc theo phiên trò chuyện"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Xem lịch sử trò chuyện của người dùng với tính năng phân trang.
    """
    query = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id)
    if he_thong:
        query = query.filter(ChatHistory.he_thong == he_thong)
    if session_id:
        try:
            s_uuid = uuid.UUID(session_id)
            query = query.filter(ChatHistory.session_id == s_uuid)
        except Exception:
            pass

    total = query.count()
    offset = (page - 1) * page_size
    records = query.order_by(ChatHistory.created_at.desc()).offset(offset).limit(page_size).all()

    items = [
        ChatHistoryItem(
            id=str(r.id),
            session_id=str(r.session_id) if r.session_id else None,
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
