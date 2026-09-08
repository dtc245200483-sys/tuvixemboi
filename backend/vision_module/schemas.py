# -*- coding: utf-8 -*-
"""
Pydantic Schemas cho Vision Module phân tích hình thái Bàn tay và Khuôn mặt.
Chỉ chứa các trường mô tả khách quan các đặc điểm quan sát được,
tuyệt đối không chứa các trường suy diễn luận giải vận mệnh hay danh tính cá nhân.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class TayAnhInput(BaseModel):
    loai_anh: str = Field(default="tay", description="Loại ảnh: tay")
    du_lieu_anh: str = Field(..., description="Dữ liệu ảnh dạng chuỗi base64 hoặc đường dẫn")


class MatAnhInput(BaseModel):
    loai_anh: str = Field(default="mat", description="Loại ảnh: mat")
    du_lieu_anh: str = Field(..., description="Dữ liệu ảnh dạng chuỗi base64 hoặc đường dẫn")


class DacDiemTay(BaseModel):
    hinh_dang_ban_tay: str = Field(..., description="Hình dáng tổng thể bàn tay (vuông, dài, thon, tròn dày)")
    do_ro_duong_tam_dao: str = Field(..., description="Đặc điểm quan sát đường Tâm Đạo (rõ nét, mờ, đứt đoạn, độ dài)")
    do_ro_duong_tri_dao: str = Field(..., description="Đặc điểm quan sát đường Trí Đạo (thẳng, cong, phân nhánh, độ sâu)")
    do_ro_duong_sinh_dao: str = Field(..., description="Đặc điểm quan sát đường Sinh Đạo (liên tục, vòng cung rộng/hẹp, nét)")
    hinh_dang_ngon_tay: List[str] = Field(default_factory=list, description="Danh sách quan sát hình dáng các ngón tay")
    mo_ta_them: str = Field(default="", description="Các chi tiết quan sát phụ (độ đầy các gò, nếp nhăn cổ tay...)")


class DacDiemMat(BaseModel):
    hinh_dang_tran: str = Field(..., description="Đặc điểm hình thái trán (cao, rộng, bằng phẳng, tròn, hẹp)")
    hinh_dang_mat: str = Field(..., description="Đặc điểm hình thái mắt (mắt 1 mí/2 mí, đuôi mắt, tỷ lệ tròng)")
    hinh_dang_mui: str = Field(..., description="Đặc điểm hình thái mũi (sống mũi thẳng/gãy, cánh mũi, chóp mũi)")
    hinh_dang_mieng: str = Field(..., description="Đặc điểm hình thái miệng và môi (khóe miệng, độ dày môi, viền môi)")
    hinh_dang_cam: str = Field(..., description="Đặc điểm hình thái cằm và quai hàm (tròn, vuông, nhọn, chẻ)")
    vi_tri_not_ruoi: List[str] = Field(default_factory=list, description="Danh sách vị trí nốt ruồi quan sát thấy nếu có")
    ti_vet_da_lieu_hoac_mun: List[str] = Field(default_factory=list, description="Danh sách mụn, vết thâm mụn hoặc tì vết tạm thời (không phải nốt ruồi)")
    mo_ta_them: str = Field(default="", description="Chi tiết hình thái tổng thể (tỷ lệ tam đình, lông mày...)")
