# -*- coding: utf-8 -*-
"""
Hệ thống Tinh Đẩu Tử Vi Đẩu Số Kinh Điển (108+ Tinh Tú).
Bao gồm:
- 14 Chính Tinh và Bảng Độ Sáng Miếu/Vượng/Đắc/Bình/Hãm tại 12 Cung.
- Vòng Thái Tuế (12 sao).
- Vòng Bác Sĩ (12 sao).
- Vòng Tràng Sinh (12 sao).
- Bộ Tứ Hóa (Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ).
- Lục Cát Tinh, Lục Sát Tinh.
- Tuần Không, Triệt Không.
- Toàn bộ Phụ Tinh Cát/Hung kinh điển.

Nguồn tham chiếu: Tử Vi Đẩu Số Toàn Thư (Hi Di Trần Đoàn), Tử Vi Áo Bí.
"""

# 1. 14 CHÍNH TINH
CHINH_TINH = [
    # Chùm sao Tử Vi
    {"ten": "Tử Vi", "loai": "chinh_tinh", "ngu_hanh": "Thổ", "chum": "TuVi", "chuc_nang": "Đế tinh, chủ quản 12 cung, quý hiển, phúc thọ"},
    {"ten": "Thiên Cơ", "loai": "chinh_tinh", "ngu_hanh": "Mộc", "chum": "TuVi", "chuc_nang": "Thiện tinh, mưu lược, trí tuệ, cơ biến linh hoạt"},
    {"ten": "Thái Dương", "loai": "chinh_tinh", "ngu_hanh": "Hỏa", "chum": "TuVi", "chuc_nang": "Quý tinh, chủ cung Quan Lộc, quang minh, quyền quý"},
    {"ten": "Vũ Khúc", "loai": "chinh_tinh", "ngu_hanh": "Kim", "chum": "TuVi", "chuc_nang": "Tài tinh, chủ cung Tài Bạch, cương nghị, thực tế"},
    {"ten": "Thiên Đồng", "loai": "chinh_tinh", "ngu_hanh": "Thủy", "chum": "TuVi", "chuc_nang": "Phúc tinh, an lạc, hòa nhã, phúc thọ cứu giải"},
    {"ten": "Liêm Trinh", "loai": "chinh_tinh", "ngu_hanh": "Hỏa", "chum": "TuVi", "chuc_nang": "Tù tinh, quyền uy, thứ đào hoa, công danh, liêm chính"},

    # Chùm sao Thiên Phủ
    {"ten": "Thiên Phủ", "loai": "chinh_tinh", "ngu_hanh": "Thổ", "chum": "ThienPhu", "chuc_nang": "Lệnh tinh, kho tàng ngân khố, bao dung, điềm đạm"},
    {"ten": "Thái Âm", "loai": "chinh_tinh", "ngu_hanh": "Thủy", "chum": "ThienPhu", "chuc_nang": "Phú tinh, chủ cung Điền Trạch, điềm đạm, nhu thuận, tiền tài"},
    {"ten": "Tham Lang", "loai": "chinh_tinh", "ngu_hanh": "Thủy", "chum": "ThienPhu", "chuc_nang": "Dục tinh, đệ nhất đào hoa, đa tài, năng động, dục vọng"},
    {"ten": "Cự Môn", "loai": "chinh_tinh", "ngu_hanh": "Thủy", "chum": "ThienPhu", "chuc_nang": "Ám tinh, khẩu tài, ngôn ngữ, biện luận, thị phi, quan sát"},
    {"ten": "Thiên Tướng", "loai": "chinh_tinh", "ngu_hanh": "Thủy", "chum": "ThienPhu", "chuc_nang": "Ấn tinh, tể tướng phò tá, trung chính, công tâm, danh giá"},
    {"ten": "Thiên Lương", "loai": "chinh_tinh", "ngu_hanh": "Mộc", "chum": "ThienPhu", "chuc_nang": "Ấm tinh, thọ tinh, che chở, cứu giải tai ách, đạo đức"},
    {"ten": "Thất Sát", "loai": "chinh_tinh", "ngu_hanh": "Kim", "chum": "ThienPhu", "chuc_nang": "Tướng tinh, quyền uy quân sự, dũng cảm, quyết đoán, xung trận"},
    {"ten": "Phá Quân", "loai": "chinh_tinh", "ngu_hanh": "Thủy", "chum": "ThienPhu", "chuc_nang": "Hao tinh, tiên phong phá địch, canh tân cải cách, dũng mãnh"}
]

# BẢNG ĐỘ SÁNG MIẾU / VƯỢNG / ĐẮC / BÌNH / HÃM CỦA 14 CHÍNH TINH TẠI 12 CUNG ĐỊA CHI
# Index: 0: Tý, 1: Sửu, 2: Dần, 3: Mão, 4: Thìn, 5: Tỵ, 6: Ngọ, 7: Mùi, 8: Thân, 9: Dậu, 10: Tuất, 11: Hợi
CHINH_TINH_DAC_HAM = {
    "Tử Vi":      {0: "B", 1: "Đ", 2: "V", 3: "Đ", 4: "V", 5: "V", 6: "M", 7: "Đ", 8: "V", 9: "Đ", 10: "V", 11: "B"},
    "Thiên Cơ":   {0: "Đ", 1: "H", 2: "V", 3: "M", 4: "M", 5: "B", 6: "Đ", 7: "H", 8: "V", 9: "M", 10: "M", 11: "B"},
    "Thái Dương": {0: "H", 1: "H", 2: "V", 3: "M", 4: "V", 5: "M", 6: "M", 7: "Đ", 8: "B", 9: "H", 10: "H", 11: "H"},
    "Vũ Khúc":    {0: "V", 1: "M", 2: "V", 3: "H", 4: "M", 5: "B", 6: "V", 7: "M", 8: "V", 9: "H", 10: "M", 11: "B"},
    "Thiên Đồng": {0: "V", 1: "H", 2: "M", 3: "Đ", 4: "H", 5: "Đ", 6: "H", 7: "H", 8: "M", 9: "H", 10: "H", 11: "Đ"},
    "Liêm Trinh": {0: "B", 1: "H", 2: "V", 3: "H", 4: "M", 5: "H", 6: "V", 7: "H", 8: "V", 9: "H", 10: "M", 11: "H"},
    "Thiên Phủ":  {0: "M", 1: "M", 2: "M", 3: "B", 4: "M", 5: "V", 6: "M", 7: "M", 8: "M", 9: "B", 10: "M", 11: "V"},
    "Thái Âm":    {0: "M", 1: "M", 2: "H", 3: "H", 4: "H", 5: "H", 6: "H", 7: "B", 8: "B", 9: "V", 10: "M", 11: "M"},
    "Tham Lang":  {0: "H", 1: "M", 2: "Đ", 3: "H", 4: "M", 5: "H", 6: "H", 7: "M", 8: "Đ", 9: "H", 10: "M", 11: "H"},
    "Cự Môn":     {0: "V", 1: "H", 2: "V", 3: "M", 4: "H", 5: "H", 6: "V", 7: "H", 8: "B", 9: "M", 10: "H", 11: "V"},
    "Thiên Tướng":{0: "V", 1: "Đ", 2: "M", 3: "H", 4: "V", 5: "Đ", 6: "V", 7: "Đ", 8: "M", 9: "H", 10: "V", 11: "Đ"},
    "Thiên Lương":{0: "V", 1: "V", 2: "M", 3: "M", 4: "V", 5: "H", 6: "M", 7: "V", 8: "H", 9: "H", 10: "M", 11: "H"},
    "Thất Sát":   {0: "M", 1: "Đ", 2: "M", 3: "H", 4: "H", 5: "B", 6: "M", 7: "Đ", 8: "M", 9: "H", 10: "H", 11: "B"},
    "Phá Quân":   {0: "M", 1: "V", 2: "H", 3: "H", 4: "V", 5: "H", 6: "M", 7: "V", 8: "H", 9: "H", 10: "V", 11: "H"}
}

# ĐỘ SÁNG LỤC SÁT TINH TẠI 12 CUNG
SAT_TINH_DAC_HAM = {
    "Kình Dương": {4: "Đ", 10: "Đ", 1: "Đ", 7: "Đ"},  # Thìn Tuất Sửu Mùi Đắc, còn lại Hãm
    "Đà La":      {4: "Đ", 10: "Đ", 1: "Đ", 7: "Đ"},  # Thìn Tuất Sửu Mùi Đắc, còn lại Hãm
    "Hỏa Tinh":   {2: "Đ", 6: "Đ", 10: "Đ"},          # Dần Ngọ Tuất Đắc
    "Linh Tinh":  {2: "Đ", 6: "Đ", 10: "Đ"},          # Dần Ngọ Tuất Đắc
    "Địa Không":  {5: "Đ", 11: "Đ", 2: "Đ", 8: "Đ"},  # Tỵ Hợi Dần Thân Đắc
    "Địa Kiếp":   {5: "Đ", 11: "Đ", 2: "Đ", 8: "Đ"}   # Tỵ Hợi Dần Thân Đắc
}

# 2. VÒNG THÁI TUẾ (12 sao an thuận theo Chi năm)
VONG_THAI_TUE = [
    {"ten": "Thái Tuế", "loai": "cat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Nguyên thần, tư thế, chính danh, khí phách"},
    {"ten": "Thiếu Dương", "loai": "cat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Thông minh, cơ trí, từ bi, cứu giải"},
    {"ten": "Tang Môn", "loai": "bai_tinh", "ngu_hanh": "Mộc", "y_nghia": "Ưu tư, lo âu, tang tóc, trắc trở"},
    {"ten": "Thiếu Âm", "loai": "cat_tinh", "ngu_hanh": "Thủy", "y_nghia": "Hiền hậu, tĩnh tại, nhu thuận, may mắn"},
    {"ten": "Quan Phù", "loai": "bai_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Luật pháp, thị phi, kiện tụng, tranh biện"},
    {"ten": "Tử Phù", "loai": "bai_tinh", "ngu_hanh": "Kim", "y_nghia": "Hao tổn, trở ngại, buồn phiền, tai ách"},
    {"ten": "Tuế Phá", "loai": "bai_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Nghịch cảnh, bất khuất, phá cách, chống đối"},
    {"ten": "Long Đức", "loai": "cat_tinh", "ngu_hanh": "Thủy", "y_nghia": "Nhân hậu, phúc lộc, giải trừ hung họa"},
    {"ten": "Bạch Hổ", "loai": "bai_tinh", "ngu_hanh": "Kim", "y_nghia": "Uy quyền, quả cảm, cương nghị hoặc hình thương"},
    {"ten": "Phúc Đức", "loai": "cat_tinh", "ngu_hanh": "Thổ", "y_nghia": "Phúc thiện, may mắn, tổ tiên che chở"},
    {"ten": "Điếu Khách", "loai": "bai_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Khẩu tài, thuyết phục, ăn chơi, hao tài"},
    {"ten": "Trực Phù", "loai": "bai_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Chân thật, thiệt thòi, ngay thẳng, gánh vác"}
]

# 3. VÒNG BÁC SĨ (12 sao an từ Lộc Tồn, thuận nghịch theo Âm Dương Nam Nữ)
VONG_BAC_SI = [
    {"ten": "Bác Sĩ", "loai": "cat_tinh", "ngu_hanh": "Thủy", "y_nghia": "Trí tuệ, học vấn cao, nhân ái, hiểu biết"},
    {"ten": "Lực Sĩ", "loai": "cat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Sức khỏe, quyền lực, gánh vác, dũng mãnh"},
    {"ten": "Thanh Long", "loai": "cat_tinh", "ngu_hanh": "Thủy", "y_nghia": "Rồng xanh, may mắn, vui vẻ, khoa bảng"},
    {"ten": "Tiểu Hao", "loai": "bai_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Hao tài nhỏ, biến động, linh hoạt di chuyển"},
    {"ten": "Tướng Quân", "loai": "cat_tinh", "ngu_hanh": "Mộc", "y_nghia": "Oai phong, can đảm, tinh thần cầm quân"},
    {"ten": "Tấu Thư", "loai": "cat_tinh", "ngu_hanh": "Kim", "y_nghia": "Văn chương, tài khéo léo, đơn từ sắc bén"},
    {"ten": "Phi Liêm", "loai": "bai_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Nhanh chóng, phiêu lưu, thị phi bay đến"},
    {"ten": "Hỷ Thần", "loai": "cat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Tin vui, may mắn, gia tăng niềm vui"},
    {"ten": "Bệnh Phù", "loai": "bai_tinh", "ngu_hanh": "Thổ", "y_nghia": "Đau ốm, bệnh tật nhẹ, uể oải"},
    {"ten": "Đại Hao", "loai": "bai_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Hao tán lớn, tiêu pha mạnh, thay đổi triệt để"},
    {"ten": "Phục Binh", "loai": "sat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Mai phục, tiểu nhân ám hại, đa nghi"},
    {"ten": "Quan Phủ", "loai": "bai_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Rắc rối pháp luật, công môn, phân xử"}
]

# 4. VÒNG TRÀNG SINH (12 trạng thái sinh diệt của Ngũ Hành theo Cục số)
VONG_TRANG_SINH = [
    {"ten": "Tràng Sinh", "loai": "cat_tinh", "ngu_hanh": "Thủy", "y_nghia": "Khởi đầu mới, sinh sôi, trường thọ, hưng thịnh"},
    {"ten": "Mộc Dục", "loai": "bai_tinh", "ngu_hanh": "Thủy", "y_nghia": "Tắm gội, đào hoa, đam mê sắc dục, bất định"},
    {"ten": "Quan Đới", "loai": "cat_tinh", "ngu_hanh": "Kim", "y_nghia": "Trưởng thành, chức vị, học vấn, trách nhiệm"},
    {"ten": "Lâm Quan", "loai": "cat_tinh", "ngu_hanh": "Kim", "y_nghia": "Vinh hiển, bổng lộc, đắc tài đắc quan"},
    {"ten": "Đế Vượng", "loai": "cat_tinh", "ngu_hanh": "Kim", "y_nghia": "Đỉnh cao phong độ, thịnh vượng, quyền thế tột bực"},
    {"ten": "Suy", "loai": "bai_tinh", "ngu_hanh": "Thủy", "y_nghia": "Suy giảm, thoái trào, thiếu nghị lực"},
    {"ten": "Bệnh", "loai": "bai_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Bệnh tật, mệt mỏi, thiếu sức sống"},
    {"ten": "Tử", "loai": "bai_tinh", "ngu_hanh": "Thủy", "y_nghia": "Tĩnh lặng, kín đáo, thâm trầm, chấm dứt giai đoạn"},
    {"ten": "Mộ", "loai": "bai_tinh", "ngu_hanh": "Thổ", "y_nghia": "Thu tàng, gìn giữ, chậm chạp, khép kín"},
    {"ten": "Tuyệt", "loai": "bai_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Dứt điểm, cạn kiệt, cô độc, chuẩn bị chuyển hóa"},
    {"ten": "Thai", "loai": "cat_tinh", "ngu_hanh": "Thổ", "y_nghia": "Mầm mống, ấp ủ, thụ thai, hình thành dự định"},
    {"ten": "Dưỡng", "loai": "cat_tinh", "ngu_hanh": "Mộc", "y_nghia": "Nuôi dưỡng, tích lũy nội lực, chăm sóc tương lai"}
]

# 5. BỘ TỨ HÓA (4 Dạng Biến Hóa Khí Huyền Học)
TU_HOA_INFO = {
    "Hóa Lộc": {"loai": "tu_hoa", "ngu_hanh": "Mộc", "y_nghia": "Tài lộc, cơ hội dồi dào, phúc ấm, duyên may"},
    "Hóa Quyền": {"loai": "tu_hoa", "ngu_hanh": "Hỏa", "y_nghia": "Quyền hành, chủ động, bản lĩnh, chỉ huy"},
    "Hóa Khoa": {"loai": "tu_hoa", "ngu_hanh": "Thủy", "y_nghia": "Khoa bảng, danh tiếng quý giá, cứu giải bệnh tật tai ương"},
    "Hóa Kỵ": {"loai": "tu_hoa", "ngu_hanh": "Thủy", "y_nghia": "Trắc trở, thị phi, thử thách, dính mắc, tu thân dưỡng tính"}
}

# Quy tắc Tứ Hóa theo 10 Thiên Can (Giáp, Ất, Bính, Đinh, Mậu, Kỷ, Canh, Tân, Nhâm, Quý)
# Thứ tự: [Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ]
BANG_TU_HOA = {
    "Giáp": [("Liêm Trinh", "Hóa Lộc"), ("Phá Quân", "Hóa Quyền"), ("Vũ Khúc", "Hóa Khoa"), ("Thái Dương", "Hóa Kỵ")],
    "Ất":   [("Thiên Cơ", "Hóa Lộc"), ("Thiên Lương", "Hóa Quyền"), ("Tử Vi", "Hóa Khoa"), ("Thái Âm", "Hóa Kỵ")],
    "Bính": [("Thiên Đồng", "Hóa Lộc"), ("Thiên Cơ", "Hóa Quyền"), ("Văn Xương", "Hóa Khoa"), ("Liêm Trinh", "Hóa Kỵ")],
    "Đinh": [("Thái Âm", "Hóa Lộc"), ("Thiên Đồng", "Hóa Quyền"), ("Thiên Cơ", "Hóa Khoa"), ("Cự Môn", "Hóa Kỵ")],
    "Mậu":  [("Tham Lang", "Hóa Lộc"), ("Thái Âm", "Hóa Quyền"), ("Hữu Bật", "Hóa Khoa"), ("Thiên Cơ", "Hóa Kỵ")],
    "Kỷ":   [("Vũ Khúc", "Hóa Lộc"), ("Tham Lang", "Hóa Quyền"), ("Thiên Lương", "Hóa Khoa"), ("Văn Khúc", "Hóa Kỵ")],
    "Canh": [("Thái Dương", "Hóa Lộc"), ("Vũ Khúc", "Hóa Quyền"), ("Thái Âm", "Hóa Khoa"), ("Thiên Đồng", "Hóa Kỵ")],
    "Tân":  [("Cự Môn", "Hóa Lộc"), ("Thái Dương", "Hóa Quyền"), ("Văn Khúc", "Hóa Khoa"), ("Văn Xương", "Hóa Kỵ")],
    "Nhâm": [("Thiên Lương", "Hóa Lộc"), ("Tử Vi", "Hóa Quyền"), ("Tả Phù", "Hóa Khoa"), ("Vũ Khúc", "Hóa Kỵ")],
    "Quý":  [("Phá Quân", "Hóa Lộc"), ("Cự Môn", "Hóa Quyền"), ("Thái Âm", "Hóa Khoa"), ("Tham Lang", "Hóa Kỵ")]
}

# 6. PHỤ TINH KINH ĐIỂN KHÁC (Cát Tinh, Hung Tinh, Sát Tinh, Bại Tinh)
PHU_TINH_CHI_TIET = {
    # Lục Cát Tinh
    "Tả Phù": {"loai": "cat_tinh", "ngu_hanh": "Thổ", "y_nghia": "Quý nhân phò tá, trợ lực trung thành"},
    "Hữu Bật": {"loai": "cat_tinh", "ngu_hanh": "Thổ", "y_nghia": "Bạn bè phù trợ, kết nối rộng rãi"},
    "Văn Xương": {"loai": "cat_tinh", "ngu_hanh": "Kim", "y_nghia": "Học thức, bằng cấp, khiếu văn chương"},
    "Văn Khúc": {"loai": "cat_tinh", "ngu_hanh": "Thủy", "y_nghia": "Nghệ thuật, tài hùng biện, sự tinh tế"},
    "Thiên Khôi": {"loai": "cat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Đệ nhất quý nhân, lãnh đạo nâng đỡ, đứng đầu"},
    "Thiên Việt": {"loai": "cat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Đệ nhị quý nhân, cơ duyên bất ngờ, trợ giúp ngầm"},

    # Tài Lộc & Lục Sát Tinh
    "Lộc Tồn": {"loai": "cat_tinh", "ngu_hanh": "Thổ", "y_nghia": "Trời ban phúc lộc, tích lũy giàu sang, ổn định"},
    "Kình Dương": {"loai": "sat_tinh", "ngu_hanh": "Kim", "y_nghia": "Dũng mãnh, tiến công, hình thương, mổ xẻ"},
    "Đà La": {"loai": "sat_tinh", "ngu_hanh": "Kim", "y_nghia": "Trì trệ, cản trở, thâm trầm, dằng dai"},
    "Hỏa Tinh": {"loai": "sat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Bốc đồng, phát tác nhanh, mãnh liệt"},
    "Linh Tinh": {"loai": "sat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Âm ỉ, thâm trầm, gan góc, bất ngờ"},
    "Địa Không": {"loai": "sat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Bất thường, kỳ tài dị tướng hoặc hao hụt đột ngột"},
    "Địa Kiếp": {"loai": "sat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Biến cố lớn, trắc trở rèn luyện ý chí, bạo phát"},

    # Quý Tinh, Phúc Tinh, Đào Hoa Tinh
    "Thiên Mã": {"loai": "cat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Ngựa xe, nghị lực di chuyển, công danh phương xa"},
    "Đào Hoa": {"loai": "cat_tinh", "ngu_hanh": "Mộc", "y_nghia": "Duyên dáng, thu hút ái tình, hoa mỹ"},
    "Hồng Loan": {"loai": "cat_tinh", "ngu_hanh": "Thủy", "y_nghia": "Hôn nhân, duyên lành, tình cảm thủy chung"},
    "Thiên Hỷ": {"loai": "cat_tinh", "ngu_hanh": "Thủy", "y_nghia": "Tin vui mừng, hỷ sự, sinh nở thuận lợi"},
    "Long Trì": {"loai": "cat_tinh", "ngu_hanh": "Thủy", "y_nghia": "Thanh tú, dòng dõi danh giá, nhan sắc"},
    "Phượng Các": {"loai": "cat_tinh", "ngu_hanh": "Mộc", "y_nghia": "Đài các, phong lưu, nhà cửa nguy nga"},
    "Hoa Cái": {"loai": "cat_tinh", "ngu_hanh": "Kim", "y_nghia": "Lọng che, quý phái, tài hoa nghệ thuật, tâm linh"},
    "Bạch Hổ": {"loai": "bai_tinh", "ngu_hanh": "Kim", "y_nghia": "Hùng dũng, quyền uy hoặc lo âu tang khó"},
    "Giải Thần": {"loai": "cat_tinh", "ngu_hanh": "Mộc", "y_nghia": "Hóa giải tai ách, gặp nạn hóa lành"},
    "Thiên Giải": {"loai": "cat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Cứu giải nạn ách, tâm tính từ thiện"},
    "Địa Giải": {"loai": "cat_tinh", "ngu_hanh": "Thổ", "y_nghia": "Hóa giải hung hiểm đất đai, giảm nhẹ tai ương"},

    # Văn Tinh & Phong Tước Tinh
    "Quốc Ấn": {"loai": "cat_tinh", "ngu_hanh": "Thổ", "y_nghia": "Con dấu chức quyền, địa vị pháp lý, uy danh"},
    "Đường Phù": {"loai": "cat_tinh", "ngu_hanh": "Mộc", "y_nghia": "Oai vệ, trang nghiêm, nhà cửa trang trọng"},
    "Thai Phụ": {"loai": "cat_tinh", "ngu_hanh": "Kim", "y_nghia": "Bằng sắc khen thưởng, danh vị danh dự"},
    "Phong Cáo": {"loai": "cat_tinh", "ngu_hanh": "Thổ", "y_nghia": "Phong thưởng, ghi nhận công trạng"},
    "Tam Thai": {"loai": "cat_tinh", "ngu_hanh": "Thủy", "y_nghia": "Nâng đỡ, phong nhã, an nhàn, xe kiệu"},
    "Bát Tọa": {"loai": "cat_tinh", "ngu_hanh": "Thổ", "y_nghia": "Ổn định, vị thế vững vàng, hòa ái"},
    "Ân Quang": {"loai": "cat_tinh", "ngu_hanh": "Mộc", "y_nghia": "Ơn đức trời phật ban, lòng trung hiếu nghĩa"},
    "Thiên Quý": {"loai": "cat_tinh", "ngu_hanh": "Thổ", "y_nghia": "Quý nhân bề trên chở che, gặp may mắn lớn"},
    "Thiên Quan": {"loai": "cat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Thiện tâm, phúc đức nhân từ, tu hành"},
    "Thiên Phúc": {"loai": "cat_tinh", "ngu_hanh": "Thổ", "y_nghia": "Phúc báo lâu dài, cứu khổ cứu nạn"},
    "Thiên Đức": {"loai": "cat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Đức độ lớn, hóa giải hung sát rất mạnh"},
    "Nguyệt Đức": {"loai": "cat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Hiền lành, phúc hậu, gia tăng tình duyên tốt đẹp"},

    # Các Bại Tinh & Hình Sát Tinh
    "Thiên Khốc": {"loai": "bai_tinh", "ngu_hanh": "Thủy", "y_nghia": "Tiếng khóc, u buồn, nhưng đắc địa có tiếng tăm vang dội"},
    "Thiên Hư": {"loai": "bai_tinh", "ngu_hanh": "Thủy", "y_nghia": "Hư hao, lo lắng, suy nhược"},
    "Thiên Hình": {"loai": "sat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Hình phạt, kỷ luật nghiêm ngặt, pháp luật, mổ xẻ, danh tiếng"},
    "Thiên Riêu": {"loai": "bai_tinh", "ngu_hanh": "Thủy", "y_nghia": "Đào hoa phong trần, phóng khoáng, mê tín dị đoan"},
    "Thiên Y": {"loai": "cat_tinh", "ngu_hanh": "Thủy", "y_nghia": "Thuốc thang chữa bệnh, chuyên gia y tế dưỡng sinh"},
    "Đẩu Quân": {"loai": "cat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Cân đo đong đếm, quản lý kho tàng, khởi nguyệt hạn"},
    "Cô Thần": {"loai": "bai_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Cô độc, độc lập, ít hòa đồng, tự lập"},
    "Quả Tú": {"loai": "bai_tinh", "ngu_hanh": "Thổ", "y_nghia": "Gìn giữ chặt chẽ, cô quạnh, kín đáo"},
    "Phá Toái": {"loai": "bai_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Vỡ vụn, cản trở bất ngờ, làm phiền lòng"},
    "Kiếp Sát": {"loai": "sat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Sát phạt bất ngờ, mạo hiểm, hình thương"},
    "Thiên Không": {"loai": "sat_tinh", "ngu_hanh": "Hỏa", "y_nghia": "Hư ảo, sắc sắc không không, mưu mô rồi về trắng tay, hướng thiện"},
    "Lưu Hà": {"loai": "bai_tinh", "ngu_hanh": "Thủy", "y_nghia": "Dòng sông chảy xiết, khẩu tài thao thao, cẩn trọng sông nước"},
    "Thiên La": {"loai": "sat_tinh", "ngu_hanh": "Kim", "y_nghia": "Lưới trời bủa vây tại Thìn, thử thách công danh"},
    "Địa Võng": {"loai": "sat_tinh", "ngu_hanh": "Kim", "y_nghia": "Lưới đất bủa vây tại Tuất, giam hãm ràng buộc"},
    "Thiên Thương": {"loai": "bai_tinh", "ngu_hanh": "Thổ", "y_nghia": "Thương tật, buồn phiền thường ngụ tại Nô Bộc"},
    "Thiên Sứ": {"loai": "bai_tinh", "ngu_hanh": "Thủy", "y_nghia": "Sứ giả trừ tà hay báo hung thường ngụ tại Tật Ách"}
}

# 7. MỆNH CHỦ & THÂN CHỦ
MENH_CHU_MAP = {
    "Tý": "Tham Lang",
    "Sửu": "Cự Môn",
    "Dần": "Lộc Tồn",
    "Mão": "Văn Khúc",
    "Thìn": "Liêm Trinh",
    "Tỵ": "Vũ Khúc",
    "Ngọ": "Phá Quân",
    "Mùi": "Vũ Khúc",
    "Thân": "Liêm Trinh",
    "Dậu": "Văn Khúc",
    "Tuất": "Lộc Tồn",
    "Hợi": "Cự Môn"
}

THAN_CHU_MAP = {
    "Tý": "Linh Tinh",
    "Sửu": "Thiên Tướng",
    "Dần": "Thiên Lương",
    "Mão": "Thiên Đồng",
    "Thìn": "Văn Xương",
    "Tỵ": "Thiên Cơ",
    "Ngọ": "Hỏa Tinh",
    "Mùi": "Thiên Tướng",
    "Thân": "Thiên Lương",
    "Dậu": "Thiên Đồng",
    "Tuất": "Văn Xương",
    "Hợi": "Thiên Cơ"
}
