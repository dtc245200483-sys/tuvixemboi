"use strict";
/**
 * ==============================================================================
 * VIETNAM ASTROLOGY ADAPTER UTILITY
 * Path: src/utils/vietnamAstrologyAdapter.ts
 * ==============================================================================
 * Cung cấp hàm `applyVietnamAstrologyRules` chuẩn hóa toàn diện lá số Tử Vi
 * theo quy chuẩn Nam Phái Việt Nam truyền thống (tuvi.vn, tuviglobal, lyso.vn).
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.applyVietnamAstrologyRules = exports.isBadStar = exports.BAD_STAR_NAMES = exports.MAJOR_STAR_NAMES = exports.SOUL_MASTER_MAP = exports.getStarHanh = exports.STAR_ELEMENT_MAP = exports.STEMS = exports.BRANCHES_FROM_ZI = exports.astrolabeByLunarDate = exports.astrolabeBySolarDate = exports.getVietnameseMutagenTable = exports.calculateYearlyStars = exports.calculateSoulMasterStar = exports.calculateKuiYue = exports.calculateHuoLing = exports.calculateTuanTriet = exports.calculateTuanBranches = exports.calculateTrietBranches = exports.getCanChiFromYear = exports.vietnamAstrologyAdapter = void 0;
var vietnamAstrologyAdapter_1 = require("../vietnamAstrologyAdapter");
Object.defineProperty(exports, "vietnamAstrologyAdapter", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.vietnamAstrologyAdapter; } });
Object.defineProperty(exports, "getCanChiFromYear", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.getCanChiFromYear; } });
Object.defineProperty(exports, "calculateTrietBranches", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.calculateTrietBranches; } });
Object.defineProperty(exports, "calculateTuanBranches", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.calculateTuanBranches; } });
Object.defineProperty(exports, "calculateTuanTriet", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.calculateTuanTriet; } });
Object.defineProperty(exports, "calculateHuoLing", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.calculateHuoLing; } });
Object.defineProperty(exports, "calculateKuiYue", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.calculateKuiYue; } });
Object.defineProperty(exports, "calculateSoulMasterStar", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.calculateSoulMasterStar; } });
Object.defineProperty(exports, "calculateYearlyStars", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.calculateYearlyStars; } });
Object.defineProperty(exports, "getVietnameseMutagenTable", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.getVietnameseMutagenTable; } });
Object.defineProperty(exports, "astrolabeBySolarDate", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.astrolabeBySolarDate; } });
Object.defineProperty(exports, "astrolabeByLunarDate", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.astrolabeByLunarDate; } });
Object.defineProperty(exports, "BRANCHES_FROM_ZI", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.BRANCHES_FROM_ZI; } });
Object.defineProperty(exports, "STEMS", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.STEMS; } });
Object.defineProperty(exports, "STAR_ELEMENT_MAP", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.STAR_ELEMENT_MAP; } });
Object.defineProperty(exports, "getStarHanh", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.getStarHanh; } });
Object.defineProperty(exports, "SOUL_MASTER_MAP", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.SOUL_MASTER_MAP; } });
Object.defineProperty(exports, "MAJOR_STAR_NAMES", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.MAJOR_STAR_NAMES; } });
Object.defineProperty(exports, "BAD_STAR_NAMES", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.BAD_STAR_NAMES; } });
Object.defineProperty(exports, "isBadStar", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.isBadStar; } });
/**
 * Áp dụng toàn bộ 6 quy tắc Tử Vi chuẩn Nam Phái Việt Nam vào lá số `astrolabe` từ `iztro`:
 * 1. Tuần Không & Triệt Lộ: Chiếm trọn 2 cung liên tiếp.
 * 2. Hỏa Tinh & Linh Tinh: Tính lại theo giờ sinh và phân biệt Âm Dương Nam Nữ.
 * 3. Bảng Tứ Hóa 10 Thiên Can: Chuẩn Nam Phái (Canh: Nhật-Vũ-Đồng-Âm; Nhâm: Lương-Vi-Phù-Vũ).
 * 4. Thiên Khôi & Thiên Việt: Can Giáp, Mậu, Canh khởi Sửu - Mùi, v.v.
 * 5. Sao Chủ Mệnh: Tính theo Chi của Cung Mệnh đóng (Tý: Tham Lang, Sửu: Cự Môn, ...).
 * 6. Bộ Sao Lưu Niên: 9 sao Lưu Niên (L.Thái Tuế, L.Tang Môn, L.Bạch Hổ, L.Khốc, L.Hư, L.Lộc Tồn, L.Kình Dương, L.Đà La, L.Thiên Mã) + Tứ Hóa Lưu Niên.
 *
 * @param astrolabe Đối tượng FunctionalAstrolabe hoặc JSON trả về từ iztro (astro.bySolar / astro.byLunar)
 * @param targetYear Năm xem hạn để tính 9 sao Lưu Niên (mặc định: 2026)
 * @returns Chính đối tượng `astrolabe` đã được ghi đè toàn diện
 */
function applyVietnamAstrologyRules(astrolabe, targetYear) {
    if (targetYear === void 0) { targetYear = 2026; }
    return (0, vietnamAstrologyAdapter_1.vietnamAstrologyAdapter)(astrolabe, targetYear);
}
exports.applyVietnamAstrologyRules = applyVietnamAstrologyRules;
exports.default = applyVietnamAstrologyRules;
