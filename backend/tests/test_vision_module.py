# -*- coding: utf-8 -*-
"""
Bộ 7 Test Cases kiểm thử toàn diện Vision Module:
- Kiểm định chất lượng ảnh (độ nét, ánh sáng, kích thước, định dạng tệp).
- Phân tích hình thái bàn tay (DacDiemTay) & khuôn mặt (DacDiemMat).
- Xử lý toàn luồng dịch vụ upload và lưu cơ sở dữ liệu với chính sách 30 ngày.
- Xử lý lỗi ngoại lệ và fallback an toàn khi Vision AI trả sai định dạng.
"""

import os
import io
import json
import uuid
from datetime import datetime, timedelta
import pytest
from PIL import Image, ImageDraw
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base
from db.models import User, TuongAnhResult
from vision_module.schemas import DacDiemTay, DacDiemMat
from vision_module.preprocessor import kiem_tra_chat_luong_anh, resize_va_chuan_hoa
from vision_module.analyzer import phan_tich_anh_tay, phan_tich_anh_mat
from vision_module.service import xu_ly_anh_upload


def create_valid_test_image(width=400, height=400) -> bytes:
    """Tạo ảnh thử nghiệm hợp lệ, rõ nét và có độ tương phản."""
    img = Image.new("RGB", (width, height), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    draw.line([(50, 50), (350, 350)], fill=(30, 30, 30), width=4)
    draw.line([(50, 350), (350, 50)], fill=(50, 50, 50), width=4)
    draw.ellipse([(150, 150), (250, 250)], outline=(20, 20, 20), width=3)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def create_dark_test_image(width=400, height=400) -> bytes:
    """Tạo ảnh quá tối, không đạt yêu cầu ánh sáng."""
    img = Image.new("RGB", (width, height), color=(10, 10, 10))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def db_session():
    """Tạo DB in-memory tạm thời cho unit test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    # Tạo 1 user mẫu
    user = User(
        id=uuid.uuid4(),
        email="vision_test@example.com",
        password_hash="test_hash_123",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    yield db, user
    db.close()


def test_case_1_phan_tich_anh_tay_valid():
    """
    Test 1: Upload 1 ảnh bàn tay rõ nét, hợp lệ.
    Xác nhận phan_tich_anh_tay trả về DacDiemTay đầy đủ các trường, không rỗng.
    """
    img_bytes = create_valid_test_image()

    def mock_palm_ai_caller(prompt: str, image_bytes: bytes) -> str:
        return json.dumps({
            "hinh_dang_ban_tay": "Bàn tay dạng chữ nhật, lòng bàn tay dày và đầy đặn",
            "do_ro_duong_tam_dao": "Đường Tâm Đạo rõ nét, sâu, chạy dài từ gò Thủy Tinh hướng về gò Mộc Tinh",
            "do_ro_duong_tri_dao": "Đường Trí Đạo thẳng, đậm nét, kết thúc ở vị trí gò Hỏa Tinh thứ hai",
            "do_ro_duong_sinh_dao": "Đường Sinh Đạo uốn cong rộng, bao quanh gò Kim Tinh, không có nét đứt",
            "hinh_dang_ngon_tay": [
                "Ngón cái thẳng, đốt gốc dày",
                "Ngón trỏ dài ngang ngửa ngón áp út",
                "Các ngón tay khép kín, kẽ tay không hở"
            ],
            "mo_ta_them": "Gò Thái Âm và gò Kim Tinh phát triển nổi rõ, sắc da lòng bàn tay hồng hào"
        })

    result = phan_tich_anh_tay(img_bytes, ai_caller=mock_palm_ai_caller)
    assert isinstance(result, DacDiemTay)
    assert result.hinh_dang_ban_tay != ""
    assert result.do_ro_duong_tam_dao != ""
    assert result.do_ro_duong_tri_dao != ""
    assert result.do_ro_duong_sinh_dao != ""
    assert len(result.hinh_dang_ngon_tay) >= 1
    assert result.mo_ta_them != ""


def test_case_2_phan_tich_anh_mat_valid():
    """
    Test 2: Upload 1 ảnh khuôn mặt rõ nét, hợp lệ.
    Xác nhận phan_tich_anh_mat trả về DacDiemMat đầy đủ các trường.
    """
    img_bytes = create_valid_test_image()

    def mock_face_ai_caller(prompt: str, image_bytes: bytes) -> str:
        return json.dumps({
            "hinh_dang_tran": "Trán cao, rộng, bề mặt bằng phẳng không có nếp nhăn ngang hằn sâu",
            "hinh_dang_mat": "Mắt hai mí rõ ràng, khóe mắt ngang, tròng đen to tròn và tỷ lệ cân đối",
            "hinh_dang_mui": "Sống mũi thẳng, cao vừa phải, chóp mũi tròn, hai cánh mũi thon gọn",
            "hinh_dang_mieng": "Khuôn miệng vừa vặn, khóe miệng hơi hướng lên trên, môi trên mỏng hơn môi dưới",
            "hinh_dang_cam": "Cằm tròn đầy đặn, đường nét quai hàm thon gọn hình trái xoan",
            "vi_tri_not_ruoi": ["Nốt ruồi nhỏ màu nâu nhạt ở cánh mũi phải"],
            "mo_ta_them": "Tỷ lệ tam đình (thượng đình, trung đình, hạ đình) tương đối đồng đều"
        })

    result = phan_tich_anh_mat(img_bytes, ai_caller=mock_face_ai_caller)
    assert isinstance(result, DacDiemMat)
    assert result.hinh_dang_tran != ""
    assert result.hinh_dang_mat != ""
    assert result.hinh_dang_mui != ""
    assert result.hinh_dang_mieng != ""
    assert result.hinh_dang_cam != ""
    assert len(result.vi_tri_not_ruoi) == 1
    assert result.mo_ta_them != ""


def test_case_3_kiem_tra_chat_luong_anh_low_quality():
    """
    Test 3: Upload ảnh mờ/chất lượng thấp (quá tối).
    Xác nhận kiem_tra_chat_luong_anh phát hiện đúng và trả về dat_yeu_cau: False kèm lý do.
    """
    dark_bytes = create_dark_test_image()
    qc = kiem_tra_chat_luong_anh(dark_bytes)
    assert qc["dat_yeu_cau"] is False
    assert "tối" in qc["ly_do_neu_khong_dat"].lower()


def test_case_4_reject_non_image_file():
    """
    Test 4: Upload file không phải ảnh (file .txt đổi đuôi thành .jpg).
    Xác nhận hệ thống từ chối xử lý, báo lỗi rõ ràng.
    """
    fake_file_bytes = b"Day la noi dung tep tin van ban txt gia mao lam hinh anh jpg."
    qc = kiem_tra_chat_luong_anh(fake_file_bytes)
    assert qc["dat_yeu_cau"] is False
    assert "không phải" in qc["ly_do_neu_khong_dat"].lower() or "định dạng" in qc["ly_do_neu_khong_dat"].lower()

    with pytest.raises(ValueError) as exc_info:
        phan_tich_anh_tay(fake_file_bytes)
    assert "chất lượng ảnh không đạt" in str(exc_info.value).lower()


def test_case_5_reject_oversized_file():
    """
    Test 5: Upload ảnh vượt quá kích thước giới hạn (5MB).
    Xác nhận bị từ chối trước khi gọi Vision AI.
    """
    oversized_bytes = b"\\x00" * (6 * 1024 * 1024)
    qc = kiem_tra_chat_luong_anh(oversized_bytes)
    assert qc["dat_yeu_cau"] is False
    assert "vượt quá giới hạn" in qc["ly_do_neu_khong_dat"].lower()


def test_case_6_xu_ly_anh_upload_full_flow(db_session):
    """
    Test 6: Test xu_ly_anh_upload toàn luồng:
    Xác nhận bản ghi TuongAnhResult được tạo đúng trong database,
    có ngay_het_han_luu_tru được tính đúng (+30 ngày).
    """
    db, user = db_session
    img_bytes = create_valid_test_image()

    def mock_ai_caller(prompt: str, image_bytes: bytes) -> str:
        return json.dumps({
            "hinh_dang_ban_tay": "Bàn tay dày dặn, hình vuông",
            "do_ro_duong_tam_dao": "Đường Tâm Đạo sâu và liên tục",
            "do_ro_duong_tri_dao": "Đường Trí Đạo uốn lượn nhẹ",
            "do_ro_duong_sinh_dao": "Đường Sinh Đạo đậm và rõ",
            "hinh_dang_ngon_tay": ["Ngón tay tròn đều"],
            "mo_ta_them": "Các gò bàn tay phát triển"
        })

    before_time = datetime.utcnow()
    record = xu_ly_anh_upload(
        user_id=str(user.id),
        loai_anh="tay",
        anh_bytes=img_bytes,
        db=db,
        ai_caller=mock_ai_caller
    )

    assert record.id is not None
    assert record.user_id == user.id
    assert record.loai_anh == "tay"
    assert os.path.exists(record.duong_dan_anh)
    assert record.dac_diem_quan_sat_json["hinh_dang_ban_tay"] == "Bàn tay dày dặn, hình vuông"

    expected_expiry = before_time + timedelta(days=30)
    diff = abs((record.ngay_het_han_luu_tru - expected_expiry).total_seconds())
    assert diff < 60, f"Hạn lưu trữ tính sai: {record.ngay_het_han_luu_tru}"


def test_case_7_fallback_on_invalid_vision_ai_response():
    """
    Test 7: Test mô phỏng Vision AI trả về format không đúng mong đợi.
    Xác nhận hệ thống xử lý fallback đúng (báo lỗi thân thiện, không crash).
    """
    img_bytes = create_valid_test_image()

    def mock_broken_ai_caller(prompt: str, image_bytes: bytes) -> str:
        return "Xin chào, tôi là AI nhưng tôi không trả về JSON đâu nhé!"

    with pytest.raises(ValueError) as exc_info:
        phan_tich_anh_tay(img_bytes, ai_caller=mock_broken_ai_caller)

    assert "không đúng định dạng mong đợi" in str(exc_info.value)
