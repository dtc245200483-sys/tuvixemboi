/**
 * ==============================================================================
 * VIETNAM ASTROLOGY ADAPTER UTILITY
 * Path: src/utils/vietnamAstrologyAdapter.ts
 * ==============================================================================
 * Cung cấp hàm `applyVietnamAstrologyRules` chuẩn hóa toàn diện lá số Tử Vi
 * theo quy chuẩn Nam Phái Việt Nam truyền thống (tuvi.vn, tuviglobal, lyso.vn).
 */
import { vietnamAstrologyAdapter, getCanChiFromYear, calculateTrietBranches, calculateTuanBranches, calculateTuanTriet, calculateHuoLing, calculateKuiYue, calculateSoulMasterStar, calculateYearlyStars, getVietnameseMutagenTable, astrolabeBySolarDate, astrolabeByLunarDate, VietnamAstrologyOptions, YearlyStarItem, BRANCHES_FROM_ZI, STEMS, STAR_ELEMENT_MAP, getStarHanh, SOUL_MASTER_MAP, MAJOR_STAR_NAMES, BAD_STAR_NAMES, isBadStar } from '../vietnamAstrologyAdapter';
export { vietnamAstrologyAdapter, getCanChiFromYear, calculateTrietBranches, calculateTuanBranches, calculateTuanTriet, calculateHuoLing, calculateKuiYue, calculateSoulMasterStar, calculateYearlyStars, getVietnameseMutagenTable, astrolabeBySolarDate, astrolabeByLunarDate, VietnamAstrologyOptions, YearlyStarItem, BRANCHES_FROM_ZI, STEMS, STAR_ELEMENT_MAP, getStarHanh, SOUL_MASTER_MAP, MAJOR_STAR_NAMES, BAD_STAR_NAMES, isBadStar, };
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
export declare function applyVietnamAstrologyRules(astrolabe: any, targetYear?: number): any;
export default applyVietnamAstrologyRules;
