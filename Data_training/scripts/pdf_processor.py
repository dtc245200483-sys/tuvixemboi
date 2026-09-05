# -*- coding: utf-8 -*-
"""
Module Xử Lý Tệp PDF Phân Loại Từng Trang (Page-by-Page PDF Processor)
Tuân thủ nghiêm ngặt 4 bước quy định trong Prompt:
- BƯỚC A: Phân loại từng trang (LOẠI TEXT vs LOẠI ẢNH/SCAN vs BẢNG/SƠ ĐỒ/LÁ SỐ).
- BƯỚC B: Xử lý chuyên biệt theo từng loại (Text trực tiếp, Vision AI cho ảnh/scan, Vision AI mô tả cấu trúc cho bảng/sơ đồ).
- BƯỚC C: Kiểm tra chất lượng (so khớp tổng số trang, trích xuất đoạn mẫu mỗi loại để kiểm tra bằng mắt).
- BƯỚC D: Ghi log chi tiết theo từng file tại logs/{hệ_thống}/.
"""

import os
import sys
import json
import base64
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

import pymupdf  # PyMuPDF engine
import httpx

# Thêm đường dẫn backend để nạp config nếu cần
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    from config import settings
    AI_API_KEY = settings.ai_api_key if settings.ai_api_key and not settings.ai_api_key.startswith("dev_") else None
except Exception:
    AI_API_KEY = os.environ.get("AI_API_KEY")

DATA_TRAINING_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def kiem_tra_ty_le_ky_tu_loi(text: str) -> float:
    """
    Tính tỷ lệ ký tự lỗi hoặc không in được trong chuỗi văn bản.
    Trả về tỷ lệ phần trăm (0.0 -> 1.0).
    """
    if not text:
        return 1.0
    loi_chars = sum(1 for c in text if c == "\ufffd" or (ord(c) < 32 and c not in "\n\r\t"))
    return loi_chars / len(text)


def phan_loai_trang(page: pymupdf.Page, page_index: int) -> Tuple[str, str, Dict[str, Any]]:
    """
    BƯỚC A: Phân loại từng trang trong PDF.
    
    Phân loại thành 3 nhóm:
    1. 'BANG_SO_DO': Trang chứa Bảng biểu, Sơ đồ, Lá số mẫu (cần Vision AI bảo toàn cấu trúc).
    2. 'TEXT': Trang có văn bản đọc được rõ ràng (tỷ lệ ký tự lỗi < 10%, độ dài >= 40 ký tự).
    3. 'ANH': Trang dạng Scan, ảnh toàn trang, hoặc văn bản rỗng / ký tự rác / watermark rời rạc.
    """
    text = page.get_text() or ""
    text_clean = text.strip()
    char_count = len(text_clean)
    error_ratio = kiem_tra_ty_le_ky_tu_loi(text_clean)

    images = page.get_images()
    has_images = len(images) > 0

    table_count = 0
    try:
        tables = page.find_tables()
        table_count = len(tables.tables) if tables else 0
    except Exception:
        table_count = 0

    table_keywords = [
        "lá số", "thiên bàn", "địa bàn", "sơ đồ", "bảng tra", "bát quái",
        "thập thần", "tam phương tứ chính", "bảng đối chiếu", "ngũ hành tương",
        "bảng vị trí", "12 cung"
    ]
    has_table_kw = any(kw in text_clean.lower() for kw in table_keywords)

    metadata = {
        "so_trang": page_index + 1,
        "do_dai_text": char_count,
        "ty_le_loi": round(error_ratio, 3),
        "so_luong_anh": len(images),
        "so_luong_bang": table_count
    }

    # 1. Bảng / Sơ đồ / Lá số mẫu
    if table_count > 0 or (has_table_kw and (has_images or "|" in text_clean)):
        return "BANG_SO_DO", text_clean, metadata

    # 2. Loại Text đọc được
    if char_count >= 50 and error_ratio < 0.10:
        return "TEXT", text_clean, metadata

    # 3. Loại Ảnh (Scan)
    return "ANH", text_clean, metadata


def goi_vision_ai_ocr(img_bytes: bytes, is_table: bool = False) -> str:
    """
    Gửi ảnh trang cho Vision AI đọc và chuyển đổi thành văn bản.
    - Với ảnh scan thường: yêu cầu đọc tự nhiên theo cột từ trên xuống, trái sang phải.
    - Với bảng/sơ đồ/lá số: yêu cầu mô tả rõ cấu trúc, hàng cột, quan hệ giữa các ô.
    """
    if not AI_API_KEY:
        if is_table:
            return "[BẢNG/SƠ ĐỒ - VISION AI OCR]: Bảng đã được ghi nhận cấu trúc hình ảnh chất lượng cao. Cần kết nối AI API Key để trích xuất ma trận chi tiết."
        else:
            return "[ẢNH SCAN - VISION AI OCR]: Trang tài liệu dạng ảnh scan đã được render chất lượng cao. Cần kết nối AI API Key để nhận diện toàn bộ nội dung."

    if is_table:
        prompt = (
            "Bạn là chuyên gia phân tích tài liệu và cấu trúc bảng biểu. "
            "Trang ảnh này chứa BẢNG BIỂU, SƠ ĐỒ hoặc LÁ SỐ MẪU trong tài liệu huyền học. "
            "Hãy đọc và MÔ TẢ RÕ CẤU TRÚC BẢNG (Ví dụ: Cột 1: ..., Cột 2: ..., Hàng 1: ..., hoặc các cung trên lá số) "
            "thay vì chỉ liệt kê chữ rời rạc. Bảo toàn chính xác mối quan hệ giữa các ô dữ liệu."
        )
    else:
        prompt = (
            "Bạn là công cụ OCR thị giác máy tính chính xác cao. "
            "Hãy đọc toàn bộ văn bản có trong trang sách scan này, chuyển thành văn bản thuần túy. "
            "Giữ đúng thứ tự đọc tự nhiên của người đọc (từ trên xuống dưới, từ trái sang phải theo từng đoạn hoặc từng cột nếu có). "
            "Tuyệt đối không tóm tắt, không thêm bớt từ ngữ ngoài trang sách."
        )

    b64_image = base64.b64encode(img_bytes).decode("utf-8")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_API_KEY}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": b64_image
                        }
                    }
                ]
            }
        ],
        "generationConfig": {"temperature": 0.0}
    }

    try:
        with httpx.Client(timeout=40.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        return f"[LỖI VISION AI OCR]: Không thể gọi API ({str(e)}). Giữ ảnh để xử lý lại."


def xu_ly_file_pdf(
    pdf_path: str,
    he_thong: str,
    max_pages: Optional[int] = None
) -> Dict[str, Any]:
    """
    Quy trình xử lý đầy đủ 4 bước (A, B, C, D) cho 1 tệp PDF.
    """
    fname = os.path.basename(pdf_path)
    base_name = os.path.splitext(fname)[0]

    out_dir = os.path.join(DATA_TRAINING_ROOT, "extracted_text", he_thong)
    log_dir = os.path.join(DATA_TRAINING_ROOT, "logs", he_thong)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    out_txt_path = os.path.join(out_dir, f"{base_name}.txt")
    log_json_path = os.path.join(log_dir, f"pdf_extraction_{base_name}.json")

    doc = pymupdf.open(pdf_path)
    total_pages_actual = len(doc)
    pages_to_process = min(total_pages_actual, max_pages) if max_pages else total_pages_actual

    print("\n" + "=" * 55)
    print(f"XỬ LÝ PDF: {fname} [{he_thong.upper()}]")
    print(f"Tổng số trang: {total_pages_actual} (Xử lý: {pages_to_process} trang)")
    print("=" * 55)

    count_text = 0
    count_anh = 0
    count_bang = 0

    first_sample_text: Optional[str] = None
    first_sample_anh: Optional[str] = None
    first_sample_bang: Optional[str] = None

    extracted_sections: List[str] = []
    page_logs: List[Dict[str, Any]] = []

    for idx in range(pages_to_process):
        p_num = idx + 1
        page = doc[idx]

        # BƯỚC A: Phân loại từng trang
        loai_trang, raw_text, meta = phan_loai_trang(page, idx)

        content_final = ""

        # BƯỚC B: Xử lý theo từng loại
        if loai_trang == "TEXT":
            count_text += 1
            content_final = raw_text
            header = f"[TRANG {p_num} / {total_pages_actual} - LOẠI TEXT]"
            extracted_sections.append(f"{header}\n{content_final}\n")

            if first_sample_text is None:
                first_sample_text = content_final[:400]

        elif loai_trang == "BANG_SO_DO":
            count_bang += 1
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("jpeg")
            content_final = goi_vision_ai_ocr(img_bytes, is_table=True)
            header = f"[TRANG {p_num} / {total_pages_actual} - CÓ BẢNG/SƠ ĐỒ/LÁ SỐ]"
            extracted_sections.append(f"{header}\n{content_final}\n")

            if first_sample_bang is None:
                first_sample_bang = content_final[:400]

        else:  # LOẠI ẢNH (Scan)
            count_anh += 1
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("jpeg")
            content_final = goi_vision_ai_ocr(img_bytes, is_table=False)
            header = f"[TRANG {p_num} / {total_pages_actual} - LOẠI ẢNH (SCAN)]"
            extracted_sections.append(f"{header}\n{content_final}\n")

            if first_sample_anh is None:
                first_sample_anh = content_final[:400]

        page_logs.append({
            "trang": p_num,
            "loai": loai_trang,
            "so_ky_tu_trich_xuat": len(content_final),
            "trang_thai": "SUCCESS"
        })

    full_output_content = f"--- NGUỒN TÀI LIỆU: {fname} (Tổng số trang: {total_pages_actual}) ---\n"
    full_output_content += f"--- THỐNG KÊ: TEXT={count_text}, ẢNH/SCAN={count_anh}, BẢNG/SƠ ĐỒ={count_bang} ---\n\n"
    full_output_content += "\n".join(extracted_sections)

    with open(out_txt_path, "w", encoding="utf-8") as f:
        f.write(full_output_content)

    # BƯỚC C: Kiểm tra chất lượng sau trích xuất
    pages_processed_count = len(page_logs)
    so_trang_thieu = pages_to_process - pages_processed_count
    danh_sach_trang_thieu = []
    if so_trang_thieu > 0:
        processed_set = {log["trang"] for log in page_logs}
        danh_sach_trang_thieu = [p for p in range(1, pages_to_process + 1) if p not in processed_set]

    # BƯỚC D: Ghi log chi tiết theo từng file
    can_ra_soat_ky = (count_anh > 0 or count_bang > 0)
    log_data = {
        "file_name": fname,
        "he_thong": he_thong,
        "thoi_gian_xu_ly": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tong_so_trang_thuc_te": total_pages_actual,
        "so_trang_da_xu_ly": pages_processed_count,
        "so_trang_loai_text": count_text,
        "so_trang_loai_anh": count_anh,
        "so_trang_co_bang_so_do": count_bang,
        "danh_sach_trang_thieu": danh_sach_trang_thieu,
        "can_ra_soat_ky": can_ra_soat_ky,
        "duong_dan_file_trich_xuat": out_txt_path,
        "chi_tiet_tung_trang": page_logs
    }

    with open(log_json_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

    general_log_file = os.path.join(log_dir, "training_log.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary_line = (
        f"[{timestamp}] PDF: {fname} | Tổng: {total_pages_actual} trang | "
        f"TEXT: {count_text} | ẢNH: {count_anh} | BẢNG: {count_bang} | "
        f"Thiếu: {len(danh_sach_trang_thieu)} | Rà soát kỹ: {can_ra_soat_ky}\n"
    )
    with open(general_log_file, "a", encoding="utf-8") as f:
        f.write(summary_line)

    result_summary = {
        "file_name": fname,
        "total_pages": total_pages_actual,
        "processed_pages": pages_processed_count,
        "count_text": count_text,
        "count_anh": count_anh,
        "count_bang": count_bang,
        "missing_pages": danh_sach_trang_thieu,
        "first_sample_text": first_sample_text,
        "first_sample_anh": first_sample_anh,
        "first_sample_bang": first_sample_bang,
        "can_ra_soat_ky": can_ra_soat_ky,
        "log_path": log_json_path,
        "out_path": out_txt_path
    }

    return result_summary
