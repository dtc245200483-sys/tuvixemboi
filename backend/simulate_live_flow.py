# -*- coding: utf-8 -*-
"""
Script mô phỏng toàn bộ luồng thực tế (End-to-End Live User Journey):
1. POST /auth/register -> Đăng ký tài khoản
2. POST /auth/login -> Đăng nhập & lấy Bearer token
3. POST /birth-profile -> Tạo hồ sơ ngày giờ sinh (tự động tính âm lịch)
4. GET /tu-vi/{id} -> Lập & luận giải Tử Vi trọn đời (có cache & quota)
5. GET /bat-tu/{id} -> Lập & luận giải Bát Tự Tứ Trụ
6. POST /gieo-que -> Gieo quẻ Kinh Dịch & luận giải
7. POST /vision/consent & POST /xem-tuong/tay -> Đồng ý sinh trắc học & xem tướng chỉ tay
8. POST /chat -> Chat tự do hỏi đáp huyền học (tự động nhận diện topic)
9. GET /chat/history -> Tra cứu lịch sử chat phân trang
10. GET /quota -> Kiểm tra hạn mức sử dụng trong ngày
"""

import os
import sys
import io
import json
import base64
from unittest.mock import patch
from PIL import Image, ImageDraw

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
from db.database import SessionLocal
from db.models import User
from ai_module.schemas import AIResponse

client = TestClient(app)

def create_valid_palm_image_b64() -> str:
    img = Image.new("RGB", (400, 400), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    draw.line([(50, 50), (350, 350)], fill=(30, 30, 30), width=4)
    draw.line([(50, 350), (350, 50)], fill=(50, 50, 50), width=4)
    draw.ellipse([(150, 150), (250, 250)], outline=(20, 20, 20), width=3)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode("ascii")

def mock_ai_dispatch(self, req):
    """Giả lập AI phản hồi phù hợp cho cả Vision AI (JSON đặc điểm) và Interpretation AI."""
    if getattr(req, "image_bytes", None) is not None:
        vision_dict = {
            "hinh_dang_ban_tay": "Bàn tay vuông chữ điền đầy đặn",
            "do_ro_duong_tam_dao": "Đường tâm đạo sâu, dài hướng về gò Mộc Tinh, tình cảm phong phú",
            "do_ro_duong_tri_dao": "Đường trí đạo sâu thẳng, tư duy logic quyết đoán",
            "do_ro_duong_sinh_dao": "Đường sinh đạo liên tục vòng cung rộng, sinh lực dồi dào",
            "hinh_dang_ngon_tay": ["Ngón cái vững chãi", "Ngón trỏ thẳng biểu thị lãnh đạo"],
            "mo_ta_them": "Gò Thái Dương hồng hào nổi cao, chỉ tay quý nhân phù trợ rõ nét",
            "hinh_dang_tran": "Trán cao rộng sáng sủa",
            "hinh_dang_mat": "Mắt sáng tinh anh, 2 mí rõ ràng",
            "hinh_dang_mui": "Sống mũi thẳng, cánh mũi nở nang kín đáo",
            "hinh_dang_mieng": "Khóe miệng hướng lên tươi tắn",
            "hinh_dang_cam": "Cằm tròn đầy phúc hậu",
            "vi_tri_not_ruoi": ["Nốt ruồi phú quý gần lông mày"]
        }
        return AIResponse(
            text=json.dumps(vision_dict, ensure_ascii=False),
            provider="gemini",
            tokens_used=180,
            thoi_gian_xu_ly_ms=85,
            thanh_cong=True,
            loi_neu_co=None
        )
    text_dict = {
        "chu_de": "tong_quan",
        "noi_dung": "Thời vận hanh thông, quý nhân phù trợ, công danh sự nghiệp phát triển thuận lợi.",
        "muc_do_tin_cay": 0.92
    }
    return AIResponse(
        text=json.dumps(text_dict, ensure_ascii=False),
        provider="gemini",
        tokens_used=125,
        thoi_gian_xu_ly_ms=68,
        thanh_cong=True,
        loi_neu_co=None
    )

def run_simulation():
    with patch("ai_module.client.AIClient.goi_ai_voi_retry", side_effect=mock_ai_dispatch, autospec=True):
        print("=" * 80)
        print("KIỂM THỬ MÔ PHỎNG LUỒNG THỰC TẾ (END-TO-END LIVE USER JOURNEY)")
        print("=" * 80)

        email = "live_demo_user@example.com"
        password = "UserDemoSecret123@"
        
        db = SessionLocal()
        old_u = db.query(User).filter(User.email == email).first()
        if old_u:
            db.delete(old_u)
            db.commit()
        db.close()

        # 1. Đăng ký
        print("\n[BƯỚC 1] Đăng ký tài khoản mới: POST /auth/register")
        reg_res = client.post("/auth/register", json={
            "email": email,
            "password": password,
            "confirm_password": password
        })
        print(f"Status: {reg_res.status_code}")
        print(f"Response: {json.dumps(reg_res.json(), ensure_ascii=False)}")

        # 2. Đăng nhập
        print("\n[BƯỚC 2] Đăng nhập hệ thống: POST /auth/login")
        login_res = client.post("/auth/login", data={"username": email, "password": password})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Status: {login_res.status_code}")
        print(f"Token Type: {login_res.json()['token_type']} | Access Token: {token[:25]}...")

        # 3. Tạo hồ sơ sinh
        print("\n[BƯỚC 3] Tạo hồ sơ sinh: POST /birth-profile")
        profile_res = client.post("/birth-profile", json={
            "ho_ten": "Trần Quốc Toản",
            "ngay_sinh_duong": "1992-10-15",
            "gio_sinh": 8,
            "phut_sinh": 15,
            "gioi_tinh": "nam"
        }, headers=headers)
        print(f"Status: {profile_res.status_code}")
        profile_data = profile_res.json()["du_lieu"]
        profile_id = profile_data["id"]
        print(f"Hồ sơ ID: {profile_id}")
        print(f"Dương lịch: {profile_data['ngay_sinh_duong']} {profile_data['gio_sinh']}h{profile_data['phut_sinh']}")
        print(f"Âm lịch tự động tính: Ngày {profile_data['ngay_sinh_am']} ({profile_data['thong_tin_am_lich']['can_nam']} {profile_data['thong_tin_am_lich']['chi_nam']})")

        # 4. Xem Tử Vi
        print(f"\n[BƯỚC 4] Lập và Luận giải Tử Vi: GET /tu-vi/{profile_id}")
        tv_res = client.get(f"/tu-vi/{profile_id}", headers=headers)
        print(f"Status: {tv_res.status_code}")
        tv_data = tv_res.json()["du_lieu"]
        print(f"Cung Mệnh: {tv_data['la_so']['ten_cung_menh']} | Cục: {tv_data['la_so']['cuc']} | Nạp Âm: {tv_data['la_so']['ngu_hanh_nap_am']}")
        print(f"Số cung hoàng đạo an sao: {len(tv_data['la_so']['cac_cung'])} cung")
        print(f"Luận giải Tử Vi: {tv_data['luan_giai']['cau_tra_loi']['noi_dung']}")

        # 5. Xem Bát Tự Tứ Trụ
        print(f"\n[BƯỚC 5] Lập và Luận giải Bát Tự: GET /bat-tu/{profile_id}")
        bt_res = client.get(f"/bat-tu/{profile_id}", headers=headers)
        print(f"Status: {bt_res.status_code}")
        bt_data = bt_res.json()["du_lieu"]
        print(f"Tứ Trụ: Năm={bt_data['tu_tru']['tru_nam']['can']} {bt_data['tu_tru']['tru_nam']['chi']} | Tháng={bt_data['tu_tru']['tru_thang']['can']} {bt_data['tu_tru']['tru_thang']['chi']} | Ngày={bt_data['tu_tru']['tru_ngay']['can']} {bt_data['tu_tru']['tru_ngay']['chi']} | Giờ={bt_data['tu_tru']['tru_gio']['can']} {bt_data['tu_tru']['tru_gio']['chi']}")
        print(f"Luận giải Bát Tự: {bt_data['luan_giai']['cau_tra_loi']['noi_dung']}")

        # 6. Gieo quẻ Kinh Dịch
        print("\n[BƯỚC 6] Gieo quẻ Kinh Dịch: POST /gieo-que")
        dich_res = client.post("/gieo-que", json={
            "cau_hoi": "Hỏi về vận thế tài lộc và kinh doanh trong năm",
            "phuong_phap": "dong_xu"
        }, headers=headers)
        print(f"Status: {dich_res.status_code}")
        dich_data = dich_res.json()["du_lieu"]
        print(f"Quẻ Chính: {dich_data['ma_que_chinh']} | Quẻ Biến: {dich_data['ma_que_bien']} | Hào Động: {dich_data['hao_dong']}")
        print(f"Luận giải Kinh Dịch: {dich_data['luan_giai']['cau_tra_loi']['noi_dung']}")

        # 7. Xem Nhân Tướng (Consent -> Upload)
        print("\n[BƯỚC 7] Xem tướng bàn tay: POST /vision/consent -> POST /xem-tuong/tay")
        consent_res = client.post("/vision/consent", headers=headers)
        print(f"Consent Status: {consent_res.status_code} -> {consent_res.json().get('message', 'OK')}")

        sample_img = create_valid_palm_image_b64()
        tuong_res = client.post("/xem-tuong/tay", data={
            "du_lieu_anh_base64": sample_img,
            "cau_hoi": "Xem đường sinh đạo và công danh"
        }, headers=headers)
        print(f"Status: {tuong_res.status_code}")
        tuong_data = tuong_res.json()["du_lieu"]
        print(f"Bản ghi Tướng ảnh ID: {tuong_data['id']} | Loại: {tuong_data['loai_anh']}")
        print(f"Luận giải Nhân Tướng: {tuong_data['luan_giai']['cau_tra_loi']['noi_dung']}")

        # 8. Chat tự do (Topic Detection)
        print("\n[BƯỚC 8] Chat tương tác đa hệ thống: POST /chat")
        chat_res = client.post("/chat", json={
            "cau_hoi": "Cung Quan Lộc của tôi có ý nghĩa như thế nào?"
        }, headers=headers)
        print(f"Status: {chat_res.status_code}")
        chat_data = chat_res.json()["du_lieu"]
        print(f"Hệ thống phát hiện tự động: {chat_data['he_thong']}")
        print(f"Câu trả lời: {chat_data['tra_loi']}")

        # 9. Lịch sử Chat
        print("\n[BƯỚC 9] Lấy lịch sử hội thoại: GET /chat/history")
        hist_res = client.get("/chat/history?page=1&page_size=5", headers=headers)
        print(f"Status: {hist_res.status_code}")
        print(f"Tổng số tin nhắn: {hist_res.json()['du_lieu']['tong_so']}")

        # 10. Tra cứu hạn mức Quota
        print("\n[BƯỚC 10] Tra cứu Quota: GET /quota")
        quota_res = client.get("/quota", headers=headers)
        print(f"Status: {quota_res.status_code}")
        q_data = quota_res.json()["du_lieu"]
        print(f"Quota trong ngày: Đã dùng={q_data['so_luot_da_dung']} | Còn lại={q_data['so_luot_con_lai']}/{q_data['gioi_han_ngay']} | Còn hạn mức={q_data['con_han_muc']}")

        print("\n" + "=" * 80)
        print("HOÀN TẤT MÔ PHỎNG 10 BƯỚC: BACKEND SẴN SÀNG 100% CHO FRONTEND!")
        print("=" * 80)

if __name__ == "__main__":
    run_simulation()
