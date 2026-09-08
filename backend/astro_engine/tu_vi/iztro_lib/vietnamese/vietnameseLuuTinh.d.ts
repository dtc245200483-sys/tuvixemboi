import { VietnameseYearlyLuuResult, VietnameseAstroOptions } from './types';
/**
 * Tính Can Chi của năm dương lịch
 */
export declare function getCanChiOfYear(year: number): {
    stem: string;
    branch: string;
    stemIndex: number;
    branchZiIndex: number;
};
/**
 * Lấy vị trí cung của Lộc Tồn theo Thiên Can (Cung 0: Dần -> 11: Sửu)
 */
export declare function getLocTonPalaceIndex(stemName: string): number;
/**
 * Lấy vị trí cung của Thiên Mã theo Địa Chi (Cung 0: Dần -> 11: Sửu)
 */
export declare function getThienMaPalaceIndex(branchName: string): number;
/**
 * MODULE LƯU TINH: Tính toàn bộ các sao Lưu Niên theo năm xem hạn
 *
 * 1. L.Thái Tuế: Cung trùng Địa Chi năm xem.
 * 2. L.Tang Môn: Cách L.Thái Tuế 2 cung đi thuận.
 * 3. L.Bạch Hổ: Xung chiếu với L.Tang Môn (+6 cung).
 * 4. L.Thiên Khốc: Khởi từ Ngọ đi nghịch đến Chi năm xem.
 * 5. L.Thiên Hư: Khởi từ Ngọ đi thuận đến Chi năm xem.
 * 6. L.Lộc Tồn: Theo Can năm xem.
 * 7. L.Kình Dương: Đứng trước L.Lộc Tồn 1 cung (+1).
 * 8. L.Đà La: Đứng sau L.Lộc Tồn 1 cung (-1).
 * 9. L.Thiên Mã: Theo Chi năm xem.
 * 10. Tứ Hóa Lưu Niên: 4 sao [Lộc, Quyền, Khoa, Kỵ] theo Can năm xem.
 */
export declare function calculateVietnameseYearlyLuuStars(targetYear: number, options?: VietnameseAstroOptions): VietnameseYearlyLuuResult;
