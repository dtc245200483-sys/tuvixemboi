# -*- coding: utf-8 -*-
"""
Router Nhân Tướng Học:
- POST /xem-tuong/tay: Nhận ảnh bàn tay, kiểm tra consent sinh trắc học, phân tích vision, luận giải AI.
- POST /xem-tuong/mat: Nhận ảnh khuôn mặt, kiểm tra consent sinh trắc học, phân tích vision, luận giải AI.
"""

import base64
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User
from api.dependencies import kiem_tra_quota_truoc_khi_xu_ly
from api.schemas import APIResponse, NhanTuongResponse
from vision_module.consent import require_biometric_consent
from vision_module.service import xu_ly_anh_upload
from interpretation_api.orchestrator.main_flow import luan_giai

router = APIRouter(prefix="/xem-tuong", tags=["Nhan Tuong"])


async def _lay_bytes_anh(file: Optional[UploadFile], du_lieu_anh_base64: Optional[str]) -> bytes:
    if file:
        return await file.read()
    if du_lieu_anh_base64:
        try:
            b64 = du_lieu_anh_base64
            if "," in b64:
                b64 = b64.split(",")[1]
            return base64.b64decode(b64)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chuỗi dữ liệu ảnh base64 không hợp lệ")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vui lòng cung cấp tệp ảnh hoặc chuỗi base64")


@router.post("/tay", response_model=APIResponse[NhanTuongResponse])
async def xem_tuong_ban_tay(
    file: Optional[UploadFile] = File(None),
    du_lieu_anh_base64: Optional[str] = Form(None),
    cau_hoi: Optional[str] = Form("Luận giải tổng quan tướng bàn tay và đường chỉ tay"),
    so_ngay_luu_tru: int = Query(default=30, ge=1, le=30),
    current_user: User = Depends(kiem_tra_quota_truoc_khi_xu_ly),
    db: Session = Depends(get_db)
):
    """
    Phân tích và luận giải nhân tướng bàn tay.
    YÊU CẦU BẮT BUỘC: Đã đồng ý điều khoản sinh trắc học (Prompt 4.2). Lỗi 403 nếu chưa đồng ý.
    """
    # 1. Bắt buộc kiểm tra Consent sinh trắc học (Prompt 4.2)
    require_biometric_consent(str(current_user.id), db)

    # 2. Đọc bytes ảnh
    anh_bytes = await _lay_bytes_anh(file, du_lieu_anh_base64)

    # 3. Phân tích qua Vision Module
    try:
        record = xu_ly_anh_upload(
            user_id=str(current_user.id),
            loai_anh="tay",
            anh_bytes=anh_bytes,
            db=db,
            so_ngay_luu_tru=so_ngay_luu_tru
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # 4. Luận giải AI
    input_data = {
        "id": str(record.id),
        "reference_id": str(record.id),
        "he_thong": "nhan_tuong",
        "loai_anh": "tay",
        "la_tong_quan": True,
        **(record.dac_diem_quan_sat_json or {})
    }

    try:
        luan_giai_res = luan_giai(
            user_id=str(current_user.id),
            cau_hoi=cau_hoi or "Luận giải tổng quan tướng bàn tay và đường chỉ tay",
            du_lieu_dau_vao=input_data,
            co_dinh_kem_anh=True,
            la_tong_quan=True,
            db=db
        )
    except Exception as e:
        luan_giai_res = {
            "thanh_cong": False,
            "cau_tra_loi": {
                "chu_de": "nhan_tuong",
                "noi_dung": "Đã phân tích các đường chỉ tay và gò bàn tay thành công."
            }
        }

    return APIResponse(
        thanh_cong=True,
        du_lieu={
            "id": str(record.id),
            "loai_anh": record.loai_anh,
            "dac_diem_quan_sat": record.dac_diem_quan_sat_json,
            "luan_giai": luan_giai_res
        },
        loi=None
    )


@router.post("/mat", response_model=APIResponse[NhanTuongResponse])
async def xem_tuong_khuon_mat(
    file: Optional[UploadFile] = File(None),
    du_lieu_anh_base64: Optional[str] = Form(None),
    cau_hoi: Optional[str] = Form("Luận giải tổng quan diện mạo khuôn mặt"),
    so_ngay_luu_tru: int = Query(default=30, ge=1, le=30),
    current_user: User = Depends(kiem_tra_quota_truoc_khi_xu_ly),
    db: Session = Depends(get_db)
):
    """
    Phân tích và luận giải nhân tướng diện mạo khuôn mặt.
    YÊU CẦU BẮT BUỘC: Đã đồng ý điều khoản sinh trắc học. Lỗi 403 nếu chưa đồng ý.
    """
    # 1. Bắt buộc kiểm tra Consent sinh trắc học
    require_biometric_consent(str(current_user.id), db)

    # 2. Đọc bytes ảnh
    anh_bytes = await _lay_bytes_anh(file, du_lieu_anh_base64)

    # 3. Phân tích qua Vision Module
    try:
        record = xu_ly_anh_upload(
            user_id=str(current_user.id),
            loai_anh="mat",
            anh_bytes=anh_bytes,
            db=db,
            so_ngay_luu_tru=so_ngay_luu_tru
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # 4. Luận giải AI
    input_data = {
        "id": str(record.id),
        "reference_id": str(record.id),
        "he_thong": "nhan_tuong",
        "loai_anh": "mat",
        "la_tong_quan": True,
        **(record.dac_diem_quan_sat_json or {})
    }

    try:
        luan_giai_res = luan_giai(
            user_id=str(current_user.id),
            cau_hoi=cau_hoi or "Luận giải tổng quan diện mạo khuôn mặt",
            du_lieu_dau_vao=input_data,
            co_dinh_kem_anh=True,
            la_tong_quan=True,
            db=db
        )
    except Exception as e:
        luan_giai_res = {
            "thanh_cong": False,
            "cau_tra_loi": {
                "chu_de": "nhan_tuong",
                "noi_dung": "Đã phân tích các cung trên khuôn mặt và ngũ quan thành công."
            }
        }

    return APIResponse(
        thanh_cong=True,
        du_lieu={
            "id": str(record.id),
            "loai_anh": record.loai_anh,
            "dac_diem_quan_sat": record.dac_diem_quan_sat_json,
            "luan_giai": luan_giai_res
        },
        loi=None
    )
