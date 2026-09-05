# -*- coding: utf-8 -*-
"""
FastAPI Router cho Vision Module & Qu?n L? D? Li?u Sinh Tr?c H?c Nh?y C?m
Bao g?m:
- Ch?p thu?n ?i?u kho?n sinh tr?c h?c (POST /vision/consent).
- Upload v? ph?n t?ch ?nh B?n tay / Khu?n m?t (ki?m tra consent tr??c, ch?n 403 n?u ch?a ??ng ?).
- Ng??i d?ng t? x?a ?nh b?t k? l?c n?o (DELETE /vision/anh/{id}, x?a c? file v?t l? l?n DB).
- Li?t k? metadata ?nh c? nh?n (GET /vision/anh-cua-toi, kh?ng tr? v? ?nh g?c).
"""

import os
import uuid
import base64
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User, TuongAnhResult
from auth.dependencies import get_current_user
from vision_module.schemas import TayAnhInput, MatAnhInput
from vision_module.consent import kiem_tra_dong_y, ghi_nhan_dong_y, require_biometric_consent
from vision_module.service import xu_ly_anh_upload
from middleware.data_retention import ghi_audit_log

router = APIRouter(prefix="/vision", tags=["Vision Module"])


@router.get("/consent", status_code=status.HTTP_200_OK)
def kiem_tra_trang_thai_consent(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kiểm tra trạng thái người dùng đã đồng ý điều khoản sinh trắc học hay chưa.
    """
    da_dong_y = kiem_tra_dong_y(str(current_user.id), db)
    return {
        "status": "success",
        "da_dong_y_sinh_trac_hoc": da_dong_y
    }


@router.post("/consent", status_code=status.HTTP_200_OK)
def cap_nhat_dong_y_sinh_trac_hoc(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ng??i d?ng x?c nh?n ??ng ? ?i?u kho?n thu th?p v? ph?n t?ch d? li?u ?nh sinh tr?c h?c.
    B?t bu?c ph?i g?i endpoint n?y tr??c khi th?c hi?n t?i ?nh l?n.
    """
    ghi_nhan_dong_y(str(current_user.id), db)
    return {
        "status": "success",
        "message": "?? ghi nh?n s? ??ng ? thu th?p v? x? l? h?nh ?nh sinh tr?c h?c theo ch?nh s?ch b?o m?t.",
        "da_dong_y_sinh_trac_hoc": True
    }


@router.post("/upload-tay", status_code=status.HTTP_200_OK)
async def upload_anh_tay(
    file: Optional[UploadFile] = File(None),
    du_lieu_anh_base64: Optional[str] = Form(None),
    so_ngay_luu_tru: int = Query(default=30, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    T?i l?n v? ph?n t?ch h?nh ?nh b?n tay.
    Y?u c?u: Ng??i d?ng ph?i ??ng ? ?i?u kho?n sinh tr?c h?c tr??c (l?i 403 n?u ch?a ??ng ?).
    """
    # 1. Ki?m tra Consent
    require_biometric_consent(str(current_user.id), db)

    # 2. L?y d? li?u bytes c?a ?nh
    if file:
        anh_bytes = await file.read()
    elif du_lieu_anh_base64:
        try:
            # Lo?i b? data URL header n?u c? (data:image/jpeg;base64,...)
            if "," in du_lieu_anh_base64:
                du_lieu_anh_base64 = du_lieu_anh_base64.split(",")[1]
            anh_bytes = base64.b64decode(du_lieu_anh_base64)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="D? li?u chu?i base64 c?a ?nh kh?ng h?p l?."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui l?ng cung c?p t?p t?i l?n (file) ho?c d? li?u base64 (du_lieu_anh_base64)."
        )

    # 3. G?i x? l?
    try:
        record = xu_ly_anh_upload(
            user_id=str(current_user.id),
            loai_anh="tay",
            anh_bytes=anh_bytes,
            db=db,
            so_ngay_luu_tru=so_ngay_luu_tru
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return {
        "status": "success",
        "id": str(record.id),
        "loai_anh": record.loai_anh,
        "dac_diem_quan_sat": record.dac_diem_quan_sat_json,
        "ngay_het_han_luu_tru": record.ngay_het_han_luu_tru.isoformat() if record.ngay_het_han_luu_tru else None
    }


@router.post("/upload-mat", status_code=status.HTTP_200_OK)
async def upload_anh_mat(
    file: Optional[UploadFile] = File(None),
    du_lieu_anh_base64: Optional[str] = Form(None),
    so_ngay_luu_tru: int = Query(default=30, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    T?i l?n v? ph?n t?ch h?nh ?nh khu?n m?t.
    Y?u c?u: Ng??i d?ng ph?i ??ng ? ?i?u kho?n sinh tr?c h?c tr??c (l?i 403 n?u ch?a ??ng ?).
    """
    # 1. Ki?m tra Consent
    require_biometric_consent(str(current_user.id), db)

    # 2. L?y d? li?u bytes c?a ?nh
    if file:
        anh_bytes = await file.read()
    elif du_lieu_anh_base64:
        try:
            if "," in du_lieu_anh_base64:
                du_lieu_anh_base64 = du_lieu_anh_base64.split(",")[1]
            anh_bytes = base64.b64decode(du_lieu_anh_base64)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="D? li?u chu?i base64 c?a ?nh kh?ng h?p l?."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui l?ng cung c?p t?p t?i l?n (file) ho?c d? li?u base64 (du_lieu_anh_base64)."
        )

    # 3. G?i x? l?
    try:
        record = xu_ly_anh_upload(
            user_id=str(current_user.id),
            loai_anh="mat",
            anh_bytes=anh_bytes,
            db=db,
            so_ngay_luu_tru=so_ngay_luu_tru
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return {
        "status": "success",
        "id": str(record.id),
        "loai_anh": record.loai_anh,
        "dac_diem_quan_sat": record.dac_diem_quan_sat_json,
        "ngay_het_han_luu_tru": record.ngay_het_han_luu_tru.isoformat() if record.ngay_het_han_luu_tru else None
    }


@router.delete("/anh/{id}", status_code=status.HTTP_200_OK)
def tu_xoa_anh(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ng??i d?ng ch? ??ng x?a ?nh v? k?t qu? ph?n t?ch b?t k? l?c n?o tr??c khi h?t h?n.
    Quy t?c b?o m?t:
    - Ch? ???c x?a ?nh c?a CH?NH M?NH (l?i 403 n?u c? x?a ?nh ng??i kh?c).
    - X?a v?nh vi?n c? file v?t l? tr?n ??a v? b?n ghi trong Database.
    """
    try:
        record_uuid = uuid.UUID(str(id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID h?nh ?nh kh?ng h?p l? (y?u c?u ??nh d?ng UUID)."
        )

    record = db.query(TuongAnhResult).filter(TuongAnhResult.id == record_uuid).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kh?ng t?m th?y b?n ghi h?nh ?nh y?u c?u."
        )

    # Ki?m tra quy?n s? h?u (Security check)
    if record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="B?n kh?ng c? quy?n x?a h?nh ?nh thu?c v? t?i kho?n c?a ng??i d?ng kh?c."
        )

    # 1. X?a file v?t l? tr?n ? ??a
    file_path = record.duong_dan_anh
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"[C?NH B?O] Kh?ng th? x?a t?p v?t l? {file_path}: {e}")

    # 2. X?a b?n ghi trong Database
    db.delete(record)
    db.commit()

    # 3. Ghi audit log
    ghi_audit_log(
        hanh_dong="USER_SELF_DELETE",
        ban_ghi_id=str(record_uuid),
        user_id=str(current_user.id),
        duong_dan=file_path,
        ly_do="Ng??i d?ng ch? ??ng t? x?a h?nh ?nh v? k?t qu? ph?n t?ch c? nh?n."
    )

    return {
        "status": "success",
        "message": "?? x?a v?nh vi?n h?nh ?nh v?t l? v? to?n b? d? li?u ph?n t?ch li?n quan."
    }


@router.get("/anh-cua-toi", status_code=status.HTTP_200_OK)
def danh_sach_anh_cua_toi(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Li?t k? danh s?ch ?nh ng??i d?ng ?? t?i l?n.
    TU?N TH? B?O M?T: Tuy?t ??i kh?ng tr? v? file ?nh g?c hay binary, ch? tr? metadata qu?n l?.
    """
    records = db.query(TuongAnhResult).filter(
        TuongAnhResult.user_id == current_user.id
    ).order_by(TuongAnhResult.created_at.desc()).all()

    danh_sach = []
    for r in records:
        danh_sach.append({
            "id": str(r.id),
            "loai_anh": r.loai_anh,
            "da_duoc_xoa": r.da_duoc_xoa,
            "ngay_upload": r.created_at.isoformat() if r.created_at else None,
            "ngay_het_han": r.ngay_het_han_luu_tru.isoformat() if r.ngay_het_han_luu_tru else None
        })

    return danh_sach
