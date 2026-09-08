/**
 * ==============================================================================
 * VIETNAM ASTROLOGY ADAPTER (TỬ VI ĐẨU SỐ VIỆT NAM ADAPTER) - ENGINE ĐỘNG 100%
 * ==============================================================================
 * Module độc lập nhận đầu vào là lá số `astrolabe` từ thư viện `iztro` (Trung Châu Phái)
 * và ghi đè (override) triệt để các sao theo chuẩn Tử Vi Nam Phái / Việt Nam truyền thống
 * (tương đương thuật toán trên tuvi.vn, tuviglobal, lyso.vn).
 *
 * 100% THUẬT TOÁN TÍNH TOÁN ĐỘNG:
 * 1. Hàm xác định Can Chi từ năm bất kỳ (Dương lịch / Âm lịch):
 *    - canIndex = (year - 4) % 10
 *    - chiIndex = (year - 4) % 12
 * 2. Tuần Không & Triệt Lộ: Chiếm trọn cặp 2 cung liền kề theo công thức toán học.
 *    - Triệt Lộ: start = 8 - (canIndex % 5) * 2 -> [start, start + 1]
 *    - Tuần Không: tuanChi = (chiIndex - canIndex + 12) % 12 -> [(tuanChi - 2) % 12, (tuanChi - 1) % 12]
 * 3. Tách biệt 2 tầng Tứ Hóa:
 *    - Tầng 1: Tứ Hóa Bản Mệnh (Gốc) theo Can năm sinh ([Lộc], [Quyền], [Khoa], [Kỵ]).
 *    - Tầng 2: Tứ Hóa Lưu Niên theo Can của targetYear ([LN.Lộc], [LN.Quyền], [LN.Khoa], [LN.Kỵ]).
 *    - Không ghi đè làm mất Tứ Hóa bản mệnh.
 * 4. Thiên Khôi & Thiên Việt: Động theo Can năm sinh (Giáp/Mậu/Canh Sửu-Mùi, Ất/Kỷ Tý-Thân, etc.).
 * 5. Mệnh Chủ: Động theo Địa Chi của Cung an Mệnh (Sửu/Dần/Tuất: Lộc Tồn, Mão/Dậu: Văn Khúc, etc.).
 * 6. Bộ 13 Sao Lưu Niên: Động 100% theo targetYear (Thái Tuế, Tang Môn, Bạch Hổ, Khốc, Hư, Lộc Tồn,
 *    Kình Dương, Đà La, Thiên Mã, Đào Hoa, Hồng Loan, Thiên Khôi, Thiên Việt).
 * ==============================================================================
 */
/** 12 Địa Chi theo thứ tự chuẩn từ Tý (0) đến Hợi (11) */
export declare const BRANCHES_FROM_ZI: readonly ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"];
export declare const CN_BRANCHES_FROM_ZI: readonly ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];
/** 10 Thiên Can theo thứ tự chuẩn từ Giáp (0) đến Quý (9) */
export declare const STEMS: readonly ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"];
export declare const CN_STEMS: readonly ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"];
/** Thứ tự 12 Cung trong mảng `astrolabe.palaces` của iztro (Bắt đầu từ Dần = 0) */
export declare const IZTRO_PALACE_ORDER_FROM_YIN: readonly ["Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu"];
export interface VietnamAstrologyOptions {
    /** Năm xem hạn để tính bộ sao Lưu Niên và Tứ Hóa Lưu Niên (Mặc định: Năm hiện tại) */
    targetYear?: number;
    /** Biến thể sao Hóa Khoa của Can Nhâm: 'TaPhu' (mặc định) hoặc 'ThienPhu' */
    nhamMutagenKhoa?: 'TaPhu' | 'ThienPhu';
    /** Biến thể Khôi Việt Can Canh: 'SuuMui' (mặc định) hoặc 'NgoDan' */
    canhKuiYue?: 'SuuMui' | 'NgoDan';
    /** Tùy chọn sao Chủ Mệnh tại Cung Sửu: 'LocTon' (mặc định tuvi.vn) hoặc 'CuMon' */
    chouSoulStar?: 'LocTon' | 'CuMon';
    /** Xóa bỏ các sao Tuần/Triệt cũ do iztro an đơn cung (Mặc định: true) */
    cleanOldStars?: boolean;
}
export interface YearlyStarItem {
    name: string;
    type: 'yearly' | 'soft' | 'tough' | 'adjective';
    scope: 'yearly';
    palaceIndex?: number;
    earthlyBranch?: string;
    hanh?: 'Kim' | 'Moc' | 'Thuy' | 'Hoa' | 'Tho';
    chinhTinhHanh?: 'Kim' | 'Moc' | 'Thuy' | 'Hoa' | 'Tho';
}
/**
 * Xác định Thiên Can và Địa Chi từ năm bất kỳ (Dương lịch hoặc Âm lịch).
 * Quy ước đánh số chỉ số (Index 0-based):
 * - Thiên Can (0 -> 9): 0: Giáp, 1: Ất, 2: Bính, 3: Đinh, 4: Mậu, 5: Kỷ, 6: Canh, 7: Tân, 8: Nhâm, 9: Quý.
 *   Công thức: canIndex = (year - 4) % 10 (nếu < 0 thì + 10).
 * - Địa Chi (0 -> 11): 0: Tý, 1: Sửu, 2: Dần, 3: Mão, 4: Thìn, 5: Tỵ, 6: Ngọ, 7: Mùi, 8: Thân, 9: Dậu, 10: Tuất, 11: Hợi.
 *   Công thức: chiIndex = (year - 4) % 12 (nếu < 0 thì + 12).
 */
export declare function getCanChiFromYear(year: number): {
    canIndex: number;
    chiIndex: number;
    can: string;
    chi: string;
    canChi: string;
};
/** Chuyển tên Địa Chi sang số thứ tự 0..11 (Tý = 0, Sửu = 1, ..., Hợi = 11) */
export declare function branchToZiIndex(branchName: string): number;
/** Chuyển tên Thiên Can sang số thứ tự 0..9 (Giáp = 0, ..., Quý = 9) */
export declare function stemToIndex(stemName: string): number;
/** Kiểm tra năm sinh thuộc Dương Nam / Âm Nữ hay Âm Nam / Dương Nữ */
export declare function isDuongNamOrAmNu(yearStem: string, gender: string): boolean;
/** Tìm ô cung trong `astrolabe.palaces` theo chỉ số Địa Chi (0 = Tý ... 11 = Hợi) */
export declare function getPalaceByZiIndex(astrolabe: any, ziIndex: number): any;
/**
 * Thuật toán an TRIỆT LỘ ĐỘNG (Tính theo Can năm sinh `canIndex`):
 * - Can 0, 5 (Giáp, Kỷ): [Thân, Dậu] (Index 8, 9)
 * - Can 1, 6 (Ất, Canh): [Ngọ, Mùi] (Index 6, 7)
 * - Can 2, 7 (Bính, Tân): [Thìn, Tỵ] (Index 4, 5)
 * - Can 3, 8 (Đinh, Nhâm): [Dần, Mão] (Index 2, 3)
 * - Can 4, 9 (Mậu, Quý): [Tý, Sửu] (Index 0, 1)
 *
 * Công thức toán học: startBranch = 8 - (canIndex % 5) * 2; trietBranches = [startBranch, startBranch + 1]
 */
export declare function calculateTrietBranches(canIndex: number): [number, number];
/**
 * Thuật toán an TUẦN KHÔNG ĐỘNG (Tính theo Tuần Giáp của năm sinh):
 * - Tính vị trí đầu tuần (Giáp): tuanChi = (chiIndex - canIndex + 12) % 12
 * - Hai cung Không Vong luôn là: [(tuanChi - 2 + 12) % 12, (tuanChi - 1 + 12) % 12]
 *
 * (Ví dụ: Mậu Dần -> can=4, chi=2 -> tuanChi = (2 - 4 + 12)%12 = 10 (Tuất) -> Tuần Không = [8, 9] (Thân, Dậu))
 * (Ví dụ: Bính Tuất -> can=2, chi=10 -> tuanChi = (10 - 2 + 12)%12 = 8 (Thân) -> Tuần Không = [6, 7] (Ngọ, Mùi))
 */
export declare function calculateTuanBranches(canIndex: number, chiIndex: number): [number, number];
/**
 * Hàm an Tuần Không và Triệt Lộ tổng quát, chấp nhận cả số năm (>100), canIndex (0..9), hoặc chuỗi Can / Chi
 */
export declare function calculateTuanTriet(yearOrStem: number | string, yearBranch?: string | number): {
    trietBranches: [number, number];
    tuanBranches: [number, number];
};
/**
 * Bảng Tứ Hóa 10 Thiên Can chuẩn Nam Phái Việt Nam:
 * - Can 0 (Giáp): Liêm Trinh, Phá Quân, Vũ Khúc, Thái Dương
 * - Can 1 (Ất): Thiên Cơ, Thiên Lương, Tử Vi, Thái Âm
 * - Can 2 (Bính): Thiên Đồng, Thiên Cơ, Văn Xương, Liêm Trinh
 * - Can 3 (Đinh): Thái Âm, Thiên Đồng, Thiên Cơ, Cự Môn
 * - Can 4 (Mậu): Tham Lang, Thái Âm, Hữu Bật, Thiên Cơ
 * - Can 5 (Kỷ): Vũ Khúc, Tham Lang, Thiên Lương, Văn Khúc
 * - Can 6 (Canh): Thái Dương, Vũ Khúc, Thiên Đồng, Thái Âm
 * - Can 7 (Tân): Cự Môn, Thái Dương, Văn Khúc, Văn Xương
 * - Can 8 (Nhâm): Thiên Lương, Tử Vi, Tả Phù, Vũ Khúc (hoặc Thiên Phủ nếu cấu hình)
 * - Can 9 (Quý): Phá Quân, Cự Môn, Thái Âm, Tham Lang
 */
export declare const VIETNAMESE_MUTAGEN_TABLE: Record<number, [string, string, string, string]>;
export declare function getVietnameseMutagenTable(yearStemOrYear: string | number, options?: VietnamAstrologyOptions): {
    loc: string;
    quyen: string;
    khoa: string;
    ky: string;
};
/**
 * Bảng tra Thiên Khôi - Thiên Việt ĐỘNG:
 * - Can 0, 4, 6 (Giáp, Mậu, Canh): Khôi tại Sửu (1), Việt tại Mùi (7)
 * - Can 1, 5 (Ất, Kỷ): Khôi tại Tý (0), Việt tại Thân (8)
 * - Can 2, 3 (Bính, Đinh): Khôi tại Hợi (11), Việt tại Dậu (9)
 * - Can 7 (Tân): Khôi tại Dần (2), Việt tại Ngọ (6)
 * - Can 8, 9 (Nhâm, Quý): Khôi tại Mão (3), Việt tại Tỵ (5)
 */
export declare function calculateKuiYue(yearStemOrYear: string | number, options?: VietnamAstrologyOptions): {
    kuiBranch: number;
    yueBranch: number;
};
/**
 * Bảng tra Mệnh Chủ ĐỘNG theo Địa Chi của CUNG MỆNH:
 * - Tý: "Tham Lang"
 * - Sửu: "Lộc Tồn"
 * - Dần: "Lộc Tồn"
 * - Mão: "Văn Khúc"
 * - Thìn: "Liêm Trinh"
 * - Tỵ: "Vũ Khúc"
 * - Ngọ: "Phá Quân"
 * - Mùi: "Vũ Khúc"
 * - Thân: "Liêm Trinh"
 * - Dậu: "Văn Khúc"
 * - Tuất: "Lộc Tồn"
 * - Hợi: "Cự Môn"
 */
export declare const SOUL_MASTER_MAP: Record<number, string>;
export declare function calculateSoulMasterStar(menhBranchOrIdx: string | number, options?: VietnamAstrologyOptions): string;
export declare function calculateHuoLing(yearBranch: string, hourBranch: string, isDuongNamOrAmNuValue: boolean): {
    huoBranch: number;
    lingBranch: number;
};
export declare const STAR_ELEMENT_MAP: Record<string, 'Kim' | 'Moc' | 'Thuy' | 'Hoa' | 'Tho'>;
/** Lấy Ngũ Hành của một sao */
export declare function getStarHanh(starName: string): 'Kim' | 'Moc' | 'Thuy' | 'Hoa' | 'Tho';
export declare const MAJOR_STAR_NAMES: string[];
export declare const BAD_STAR_NAMES: string[];
export declare function isBadStar(starName: string): boolean;
/**
 * Thuật toán an 13 Sao Lưu Niên ĐỘNG 100% theo năm xem hạn (`targetYear`):
 * - L.Thái Tuế: Cung trùng Địa Chi năm xem hạn
 * - L.Tang Môn: Cách L.Thái Tuế 2 cung thuận (+2)
 * - L.Bạch Hổ: Xung chiếu L.Tang Môn (+6)
 * - L.Thiên Khốc: Khởi từ Ngọ (6) đi NGHỊCH đến Chi năm xem hạn
 * - L.Thiên Hư: Khởi từ Tý (0) đi THUẬN đến Chi năm xem hạn
 * - L.Lộc Tồn: Theo Thiên Can của năm xem hạn
 * - L.Kình Dương: Cung tiến 1 so với L.Lộc Tồn (+1)
 * - L.Đà La: Cung lùi 1 so với L.Lộc Tồn (-1)
 * - L.Thiên Mã: Theo Tam hợp Chi năm xem hạn
 * - L.Đào Hoa: Theo Tam hợp Chi năm xem hạn
 * - L.Hồng Loan: Khởi Mão (3) tại Tý (0), đi NGHỊCH đến Chi năm xem hạn
 * - L.Thiên Khôi: Theo Thiên Can năm xem hạn
 * - L.Thiên Việt: Theo Thiên Can năm xem hạn
 */
export declare function calculateYearlyStars(targetYear: number): {
    yearStem: string;
    yearBranch: string;
    starsMap: Record<number, YearlyStarItem[]>;
};
/**
 * Hàm adapter chính: Nhận astrolabe từ iztro, ghi đè toàn diện 6 quy tắc Tử Vi Việt Nam
 * bằng các thuật toán toán học động 100% cho BẤT KỲ NĂM SINH NÀO và BẤT KỲ NĂM XEM HẠN NÀO.
 *
 * @param astrolabe Đối tượng FunctionalAstrolabe hoặc JSON Astrolabe từ iztro
 * @param options Tùy chọn cấu hình hoặc số năm xem hạn (number)
 * @returns Đối tượng lá số đã được chuẩn hóa hoàn toàn theo Nam Phái Việt Nam
 */
export declare function vietnamAstrologyAdapter<T = any>(astrolabe: T, options?: VietnamAstrologyOptions | number): T;
/**
 * Hàm wrapper tiện ích an sao theo Dương Lịch chuẩn Tử Vi Việt Nam
 */
export declare function astrolabeBySolarDate(solarDateStr: string, timeIndex: number, gender: 'male' | 'female' | string, fixLeap?: boolean, language?: string, options?: VietnamAstrologyOptions | number): any;
/**
 * Hàm wrapper tiện ích an sao theo Âm Lịch chuẩn Tử Vi Việt Nam
 */
export declare function astrolabeByLunarDate(lunarDateStr: string, timeIndex: number, gender: 'male' | 'female' | string, isLeapMonth?: boolean, fixLeap?: boolean, language?: string, options?: VietnamAstrologyOptions | number): any;
export declare const applyVietnamAstrologyRules: typeof vietnamAstrologyAdapter;
export default vietnamAstrologyAdapter;
