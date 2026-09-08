# -*- coding: utf-8 -*-
"""
Forum Router — Diễn đàn cộng đồng Huyền Học.
Endpoints:
  GET  /forum/posts              — Danh sách bài viết (phân trang, lọc chủ đề)
  POST /forum/posts              — Đăng bài mới
  GET  /forum/posts/{id}         — Chi tiết bài + bình luận
  DELETE /forum/posts/{id}       — Xóa bài (chỉ chủ bài)
  POST /forum/posts/{id}/comments — Bình luận
  DELETE /forum/comments/{id}    — Xóa bình luận (chỉ chủ comment)
"""

import re
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from auth.dependencies import get_current_user
from db.database import get_db
from db.models import User, ForumPost, ForumComment

router = APIRouter(prefix="/forum", tags=["Forum"])

# ------------------------------------------------------------------
# Từ cấm — Content Safety
# ------------------------------------------------------------------
BAD_WORDS = [
    "chết", "tử vong", "tự tử", "ung thư", "tuyệt mạng", "đoản mệnh",
    "giết", "hiếp", "khủng bố", "bom", "súng", "ma túy",
]

def _check_content_safety(text: str) -> None:
    low = text.lower()
    for w in BAD_WORDS:
        if w in low:
            raise HTTPException(
                status_code=400,
                detail=f"Nội dung chứa từ không phù hợp: '{w}'. Vui lòng điều chỉnh."
            )

def _author_name(user: User, an_danh: bool) -> str:
    if an_danh:
        return "Ẩn Danh"
    return (user.ten_hien_thi or user.email.split("@")[0]) if user else "Thành Viên"

# ------------------------------------------------------------------
# GET /forum/posts
# ------------------------------------------------------------------
@router.get("/posts")
def list_posts(
    chu_de: Optional[str] = Query(None, description="Lọc theo chủ đề: tu-vi | bat-tu | kinh-dich | nhan-tuong | chung"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ForumPost).options(joinedload(ForumPost.user))
    if chu_de:
        q = q.filter(ForumPost.chu_de == chu_de)
    total = q.count()
    posts = q.order_by(ForumPost.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for p in posts:
        # Đếm bình luận
        so_bl = db.query(ForumComment).filter(ForumComment.post_id == p.id).count()
        result.append({
            "id": str(p.id),
            "tieu_de": p.tieu_de,
            "noi_dung_rut_gon": p.noi_dung[:200] + ("..." if len(p.noi_dung) > 200 else ""),
            "chu_de": p.chu_de,
            "an_danh": p.an_danh,
            "ten_tac_gia": _author_name(p.user, p.an_danh),
            "luot_xem": p.luot_xem,
            "so_binh_luan": so_bl,
            "la_cua_toi": str(p.user_id) == str(current_user.id),
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        })

    return {
        "thanh_cong": True,
        "du_lieu": {
            "danh_sach": result,
            "tong_so": total,
            "trang_hien_tai": page,
            "kich_thuoc_trang": page_size,
        }
    }


# ------------------------------------------------------------------
# POST /forum/posts
# ------------------------------------------------------------------
@router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tieu_de = (body.get("tieu_de") or "").strip()
    noi_dung = (body.get("noi_dung") or "").strip()
    chu_de = (body.get("chu_de") or "chung").strip()
    an_danh = bool(body.get("an_danh", False))

    if not tieu_de or len(tieu_de) < 5:
        raise HTTPException(status_code=400, detail="Tiêu đề phải có ít nhất 5 ký tự.")
    if not noi_dung or len(noi_dung) < 10:
        raise HTTPException(status_code=400, detail="Nội dung phải có ít nhất 10 ký tự.")
    if chu_de not in ["tu-vi", "bat-tu", "kinh-dich", "nhan-tuong", "chung"]:
        chu_de = "chung"

    _check_content_safety(tieu_de)
    _check_content_safety(noi_dung)

    post = ForumPost(
        user_id=current_user.id,
        tieu_de=tieu_de,
        noi_dung=noi_dung,
        chu_de=chu_de,
        an_danh=an_danh,
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return {
        "thanh_cong": True,
        "du_lieu": {
            "id": str(post.id),
            "tieu_de": post.tieu_de,
            "chu_de": post.chu_de,
            "an_danh": post.an_danh,
            "created_at": post.created_at.isoformat(),
        }
    }


# ------------------------------------------------------------------
# GET /forum/posts/{post_id}
# ------------------------------------------------------------------
@router.get("/posts/{post_id}")
def get_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        pid = uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID bài viết không hợp lệ.")

    post = db.query(ForumPost).options(
        joinedload(ForumPost.user),
        joinedload(ForumPost.binh_luan).joinedload(ForumComment.user)
    ).filter(ForumPost.id == pid).first()

    if not post:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết.")

    # Tăng lượt xem
    post.luot_xem = (post.luot_xem or 0) + 1
    db.commit()

    comments = []
    for c in post.binh_luan:
        comments.append({
            "id": str(c.id),
            "noi_dung": c.noi_dung,
            "an_danh": c.an_danh,
            "ten_tac_gia": _author_name(c.user, c.an_danh),
            "la_cua_toi": str(c.user_id) == str(current_user.id),
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })

    return {
        "thanh_cong": True,
        "du_lieu": {
            "id": str(post.id),
            "tieu_de": post.tieu_de,
            "noi_dung": post.noi_dung,
            "chu_de": post.chu_de,
            "an_danh": post.an_danh,
            "ten_tac_gia": _author_name(post.user, post.an_danh),
            "luot_xem": post.luot_xem,
            "la_cua_toi": str(post.user_id) == str(current_user.id),
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "binh_luan": comments,
        }
    }


# ------------------------------------------------------------------
# DELETE /forum/posts/{post_id}
# ------------------------------------------------------------------
@router.delete("/posts/{post_id}")
def delete_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        pid = uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID không hợp lệ.")

    post = db.query(ForumPost).filter(ForumPost.id == pid).first()
    if not post:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết.")
    if str(post.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa bài này.")

    db.delete(post)
    db.commit()
    return {"thanh_cong": True, "thong_bao": "Đã xóa bài viết."}


# ------------------------------------------------------------------
# POST /forum/posts/{post_id}/comments
# ------------------------------------------------------------------
@router.post("/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: str,
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        pid = uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID không hợp lệ.")

    post = db.query(ForumPost).filter(ForumPost.id == pid).first()
    if not post:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết.")

    noi_dung = (body.get("noi_dung") or "").strip()
    an_danh = bool(body.get("an_danh", False))

    if not noi_dung or len(noi_dung) < 3:
        raise HTTPException(status_code=400, detail="Nội dung bình luận quá ngắn.")

    _check_content_safety(noi_dung)

    comment = ForumComment(
        post_id=pid,
        user_id=current_user.id,
        noi_dung=noi_dung,
        an_danh=an_danh,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {
        "thanh_cong": True,
        "du_lieu": {
            "id": str(comment.id),
            "noi_dung": comment.noi_dung,
            "an_danh": comment.an_danh,
            "ten_tac_gia": _author_name(current_user, an_danh),
            "la_cua_toi": True,
            "created_at": comment.created_at.isoformat(),
        }
    }


# ------------------------------------------------------------------
# DELETE /forum/comments/{comment_id}
# ------------------------------------------------------------------
@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cid = uuid.UUID(comment_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID không hợp lệ.")

    comment = db.query(ForumComment).filter(ForumComment.id == cid).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Không tìm thấy bình luận.")
    if str(comment.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa bình luận này.")

    db.delete(comment)
    db.commit()
    return {"thanh_cong": True, "thong_bao": "Đã xóa bình luận."}
