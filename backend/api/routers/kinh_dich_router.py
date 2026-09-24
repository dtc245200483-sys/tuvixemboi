# -*- coding: utf-8 -*-
"""
Router Kinh Dịch:
- POST /gieo-que: Gieo quẻ (đồng xu hoặc thời gian), lưu QueKinhDichResult, luận giải quẻ.
"""

import uuid
import copy
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User, QueKinhDichResult
from api.dependencies import kiem_tra_quota_truoc_khi_xu_ly
from api.schemas import APIResponse, GieoQueRequest, GieoQueResponse
from calendar_converter.lunar_calendar import xac_dinh_gio_sinh_theo_canh_gio
from astro_engine.kinh_dich import gieo_va_lap_que
from interpretation_api.orchestrator.main_flow import luan_giai

router = APIRouter(prefix="/gieo-que", tags=["Kinh Dich"])


@router.post("", response_model=APIResponse[GieoQueResponse])
def gieo_que_kinh_dich(
    req: GieoQueRequest,
    current_user: User = Depends(kiem_tra_quota_truoc_khi_xu_ly),
    db: Session = Depends(get_db)
):
    """
    Gieo quẻ Dịch theo phương pháp đồng xu hoặc thời gian chiêm bái.
    Tự động lập Quẻ Chính, Quẻ Biến, xác định Hào Động và luận giải cát hung.
    """
    now = datetime.now()
    kwargs = {}
    if req.phuong_phap == "thoi_gian":
        canh_gio = xac_dinh_gio_sinh_theo_canh_gio(now.hour, now.minute)
        kwargs = {
            "ngay_duong": now.day,
            "thang_duong": now.month,
            "nam_duong": now.year,
            "gio_chi": canh_gio["chi_gio"]
        }
    elif req.seed is not None:
        kwargs["seed"] = req.seed

    que_data = gieo_va_lap_que(phuong_phap=req.phuong_phap, **kwargs)

    ten_que_chinh = que_data.get("que_chinh", {}).get("ten_que", "CÀN")
    ten_que_bien = que_data.get("que_bien", {}).get("ten_que") if que_data.get("que_bien") else None
    hao_dong = que_data.get("hao_dong", [])

    rec = QueKinhDichResult(
        id=uuid.uuid4(),
        user_id=current_user.id,
        cau_hoi=req.cau_hoi,
        ma_que_chinh=ten_que_chinh,
        ma_que_bien=ten_que_bien,
        hao_dong=hao_dong
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    input_data = copy.deepcopy(que_data)
    input_data["id"] = str(rec.id)
    input_data["reference_id"] = str(rec.id)
    input_data["he_thong"] = "kinh_dich"
    input_data["la_tong_quan"] = True

    try:
        luan_giai_res = luan_giai(
            user_id=str(current_user.id),
            cau_hoi=req.cau_hoi,
            du_lieu_dau_vao=input_data,
            co_dinh_kem_anh=False,
            la_tong_quan=True,
            db=db
        )
    except Exception as e:
        luan_giai_res = {
            "thanh_cong": False,
            "cau_tra_loi": {
                "chu_de": "gieo_que",
                "noi_dung": f"Quẻ {ten_que_chinh} đã được thiết lập thành công. Bản đồ hào dịch, quẻ biến và tượng quẻ sẵn sàng tra cứu."
            }
        }

    return APIResponse(
        thanh_cong=True,
        du_lieu={
            "id": str(rec.id),
            "cau_hoi": req.cau_hoi,
            "ma_que_chinh": ten_que_chinh,
            "ma_que_bien": ten_que_bien,
            "hao_dong": hao_dong,
            "chi_tiet_que": que_data,
            "luan_giai": luan_giai_res
        },
        loi=None
    )
