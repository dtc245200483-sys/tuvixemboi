# -*- coding: utf-8 -*-
"""
Module tiền xử lý và kiểm định chất lượng hình ảnh tải lên.
Đảm bảo kiểm tra độ phân giải, độ sáng, độ tương phản và loại bỏ file giả mạo
trước khi chuyển tiếp đến Vision AI, tiết kiệm chi phí và tránh lỗi nhận diện.
"""

import io
from typing import Dict, Any, Tuple
from PIL import Image, ImageStat, UnidentifiedImageError

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
MIN_DIMENSION = 200                   # Tối thiểu 200x200 pixel
MAX_DIMENSION = 1600                  # Kích thước tối đa sau khi chuẩn hóa


def kiem_tra_chat_luong_anh(anh_bytes: bytes) -> Dict[str, Any]:
    """
    Kiểm tra chất lượng ảnh toàn diện:
    1. Dung lượng file không vượt quá 5MB.
    2. Định dạng ảnh hợp lệ (loại trừ file .txt, .pdf đổi đuôi).
    3. Độ phân giải tối thiểu 200x200 pixel.
    4. Độ sáng không bị quá tối (<25) hoặc cháy sáng (>240).
    5. Độ tương phản / độ nét đủ để quan sát (độ lệch chuẩn độ xám > 8).
    
    Returns:
        dict: {
            "dat_yeu_cau": bool,
            "ly_do_neu_khong_dat": str hoặc None,
            "width": int,
            "height": int,
            "format": str
        }
    """
    if not anh_bytes or len(anh_bytes) == 0:
        return {
            "dat_yeu_cau": False,
            "ly_do_neu_khong_dat": "Dữ liệu tệp tải lên rỗng.",
            "width": 0, "height": 0, "format": ""
        }

    # 1. Giới hạn dung lượng tệp
    if len(anh_bytes) > MAX_FILE_SIZE_BYTES:
        return {
            "dat_yeu_cau": False,
            "ly_do_neu_khong_dat": f"Kích thước tệp ({len(anh_bytes)/(1024*1024):.1f}MB) vượt quá giới hạn tối đa 5MB.",
            "width": 0, "height": 0, "format": ""
        }

    # 2. Xác thực định dạng ảnh thực sự
    try:
        img_buffer = io.BytesIO(anh_bytes)
        img = Image.open(img_buffer)
        img.verify()  # Kiểm tra tính toàn vẹn file
        
        # Mở lại sau khi verify để đọc pixel
        img_buffer.seek(0)
        img = Image.open(img_buffer)
        img_format = img.format or "JPEG"
    except (UnidentifiedImageError, Exception):
        return {
            "dat_yeu_cau": False,
            "ly_do_neu_khong_dat": "Tệp tải lên không phải là định dạng hình ảnh hợp lệ (hoặc tệp đã bị hư hỏng).",
            "width": 0, "height": 0, "format": ""
        }

    w, h = img.size

    # 3. Kiểm tra độ phân giải tối thiểu
    if w < MIN_DIMENSION or h < MIN_DIMENSION:
        return {
            "dat_yeu_cau": False,
            "ly_do_neu_khong_dat": f"Độ phân giải ảnh quá thấp ({w}x{h} pixel). Yêu cầu tối thiểu {MIN_DIMENSION}x{MIN_DIMENSION} pixel.",
            "width": w, "height": h, "format": img_format
        }

    # 4. Kiểm tra độ sáng và độ mờ/tương phản
    gray_img = img.convert("L")
    stat = ImageStat.Stat(gray_img)
    mean_val = stat.mean[0]
    stddev_val = stat.stddev[0]

    if mean_val < 20:
        return {
            "dat_yeu_cau": False,
            "ly_do_neu_khong_dat": "Ảnh quá tối hoặc thiếu sáng trầm trọng, không thể quan sát chi tiết.",
            "width": w, "height": h, "format": img_format
        }

    if mean_val > 245:
        return {
            "dat_yeu_cau": False,
            "ly_do_neu_khong_dat": "Ảnh bị chói hoặc cháy sáng, mất hết chi tiết đường nét.",
            "width": w, "height": h, "format": img_format
        }

    if stddev_val < 8:
        return {
            "dat_yeu_cau": False,
            "ly_do_neu_khong_dat": "Ảnh quá mờ hoặc đơn sắc, không đủ độ tương phản để nhận diện.",
            "width": w, "height": h, "format": img_format
        }

    return {
        "dat_yeu_cau": True,
        "ly_do_neu_khong_dat": None,
        "width": w,
        "height": h,
        "format": img_format
    }


def resize_va_chuan_hoa(anh_bytes: bytes, max_dimension: int = MAX_DIMENSION) -> bytes:
    """
    Chuẩn hóa ảnh:
    - Chuyển sang không gian màu RGB.
    - Thu nhỏ tỷ lệ nếu chiều dài/chiều rộng lớn hơn max_dimension (tiết kiệm băng thông API).
    - Xuất ra định dạng JPEG chất lượng cao (quality=85).
    """
    img = Image.open(io.BytesIO(anh_bytes)).convert("RGB")
    w, h = img.size

    if w > max_dimension or h > max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

    output = io.BytesIO()
    img.save(output, format="JPEG", quality=85, optimize=True)
    return output.getvalue()
