# -*- coding: utf-8 -*-
"""
D?ch v? x? l? ?nh t?i l?n cho Vision Module:
- X?c th?c v? ti?n x? l?.
- L?u tr? t?p ?nh (m? h?a t?n t?p).
- G?i Vision AI ph?n t?ch ??c ?i?m.
- Ghi nh?n k?t qu? v?o c? s? d? li?u TuongAnhResult k?m h?n l?u tr? (t?i ?a 30 ng?y).
"""

import os
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Callable
from sqlalchemy.orm import Session

from db.models import TuongAnhResult
from vision_module.preprocessor import kiem_tra_chat_luong_anh, resize_va_chuan_hoa
from vision_module.analyzer import phan_tich_anh_tay, phan_tich_anh_mat

STORAGE_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "uploads", "images")


def xu_ly_anh_upload(
    user_id: str,
    loai_anh: str,
    anh_bytes: bytes,
    db: Session,
    ai_caller: Optional[Callable[[str, bytes], str]] = None,
    so_ngay_luu_tru: int = 30
) -> TuongAnhResult:
    """
    X? l? to?n di?n quy tr?nh t?i l?n ?nh t??ng di?n / ch? tay:
    1. Ki?m tra dung l??ng v? ch?t l??ng ?nh tr??c khi g?i Vision AI.
    2. L?u tr? t?p ?nh m? h?a an to?n tr?n h? th?ng t?p.
    3. Ph?n t?ch ??c ?i?m kh?ch quan qua Vision AI.
    4. L?u b?n ghi TuongAnhResult v?o DB v?i h?n t? ??ng x?a (m?c ??nh 30 ng?y, kh?ng qu? 30 ng?y).
    """
    if loai_anh not in ["tay", "mat"]:
        raise ValueError(f"Lo?i ?nh '{loai_anh}' kh?ng h?p l?. Ch? ch?p nh?n 'tay' ho?c 'mat'.")

    # Gi?i h?n th?i gian l?u tr? t?i ?a 30 ng?y
    if so_ngay_luu_tru < 1 or so_ngay_luu_tru > 30:
        raise ValueError("Th?i h?n l?u tr? h?nh ?nh sinh tr?c h?c ch? ???c ph?p trong kho?ng t? 1 ??n 30 ng?y.")

    # 1. Ti?n x? l? & Ki?m tra ch?t l??ng ?nh
    qc = kiem_tra_chat_luong_anh(anh_bytes)
    if not qc["dat_yeu_cau"]:
        raise ValueError(f"?nh kh?ng ??t y?u c?u: {qc['ly_do_neu_khong_dat']}")

    chuan_hoa_bytes = resize_va_chuan_hoa(anh_bytes)

    # 2. L?u ?nh v?o th? m?c storage
    user_storage_dir = os.path.join(STORAGE_BASE_DIR, str(user_id))
    os.makedirs(user_storage_dir, exist_ok=True)

    # T?n file m? h?a ng?u nhi?n UUID4 duy nh?t
    file_id = uuid.uuid4().hex
    saved_filename = f"{file_id}.jpg"
    saved_filepath = os.path.join(user_storage_dir, saved_filename)

    with open(saved_filepath, "wb") as f:
        f.write(chuan_hoa_bytes)

    # 3. Ph?n t?ch qua Vision AI
    if loai_anh == "tay":
        dac_diem_model = phan_tich_anh_tay(chuan_hoa_bytes, ai_caller=ai_caller)
    else:
        dac_diem_model = phan_tich_anh_mat(chuan_hoa_bytes, ai_caller=ai_caller)

    dac_diem_json = dac_diem_model.model_dump()

    # 4. Ghi nh?n c? s? d? li?u v?i ch?nh s?ch h?t h?n
    ngay_het_han = datetime.utcnow() + timedelta(days=so_ngay_luu_tru)
    user_uuid = uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id

    record = TuongAnhResult(
        id=uuid.uuid4(),
        user_id=user_uuid,
        loai_anh=loai_anh,
        duong_dan_anh=saved_filepath,
        dac_diem_quan_sat_json=dac_diem_json,
        da_duoc_xoa=False,
        ngay_het_han_luu_tru=ngay_het_han
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record
