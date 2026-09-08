"use strict";
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
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.applyVietnamAstrologyRules = exports.astrolabeByLunarDate = exports.astrolabeBySolarDate = exports.vietnamAstrologyAdapter = exports.calculateYearlyStars = exports.isBadStar = exports.BAD_STAR_NAMES = exports.MAJOR_STAR_NAMES = exports.getStarHanh = exports.STAR_ELEMENT_MAP = exports.calculateHuoLing = exports.calculateSoulMasterStar = exports.SOUL_MASTER_MAP = exports.calculateKuiYue = exports.getVietnameseMutagenTable = exports.VIETNAMESE_MUTAGEN_TABLE = exports.calculateTuanTriet = exports.calculateTuanBranches = exports.calculateTrietBranches = exports.getPalaceByZiIndex = exports.isDuongNamOrAmNu = exports.stemToIndex = exports.branchToZiIndex = exports.getCanChiFromYear = exports.IZTRO_PALACE_ORDER_FROM_YIN = exports.CN_STEMS = exports.STEMS = exports.CN_BRANCHES_FROM_ZI = exports.BRANCHES_FROM_ZI = void 0;
var astro = __importStar(require("./astro"));
var FunctionalStar_1 = __importDefault(require("./star/FunctionalStar"));
// ------------------------------------------------------------------------------
// HẰNG SỐ & BẢNG TRA CỨU HÌNH HỌC THIÊN BÀN
// ------------------------------------------------------------------------------
/** 12 Địa Chi theo thứ tự chuẩn từ Tý (0) đến Hợi (11) */
exports.BRANCHES_FROM_ZI = [
    'Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'
];
exports.CN_BRANCHES_FROM_ZI = [
    '子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'
];
/** 10 Thiên Can theo thứ tự chuẩn từ Giáp (0) đến Quý (9) */
exports.STEMS = [
    'Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý'
];
exports.CN_STEMS = [
    '甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'
];
/** Thứ tự 12 Cung trong mảng `astrolabe.palaces` của iztro (Bắt đầu từ Dần = 0) */
exports.IZTRO_PALACE_ORDER_FROM_YIN = [
    'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi', 'Tý', 'Sửu'
];
// ------------------------------------------------------------------------------
// 1. CÔNG THỨC XÁC ĐỊNH CAN CHI TỪ NĂM BẤT KỲ (DƯƠNG LỊCH HOẶC ÂM LỊCH)
// ------------------------------------------------------------------------------
/**
 * Xác định Thiên Can và Địa Chi từ năm bất kỳ (Dương lịch hoặc Âm lịch).
 * Quy ước đánh số chỉ số (Index 0-based):
 * - Thiên Can (0 -> 9): 0: Giáp, 1: Ất, 2: Bính, 3: Đinh, 4: Mậu, 5: Kỷ, 6: Canh, 7: Tân, 8: Nhâm, 9: Quý.
 *   Công thức: canIndex = (year - 4) % 10 (nếu < 0 thì + 10).
 * - Địa Chi (0 -> 11): 0: Tý, 1: Sửu, 2: Dần, 3: Mão, 4: Thìn, 5: Tỵ, 6: Ngọ, 7: Mùi, 8: Thân, 9: Dậu, 10: Tuất, 11: Hợi.
 *   Công thức: chiIndex = (year - 4) % 12 (nếu < 0 thì + 12).
 */
function getCanChiFromYear(year) {
    var canIndex = ((year - 4) % 10 + 10) % 10;
    var chiIndex = ((year - 4) % 12 + 12) % 12;
    var can = exports.STEMS[canIndex];
    var chi = exports.BRANCHES_FROM_ZI[chiIndex];
    return {
        canIndex: canIndex,
        chiIndex: chiIndex,
        can: can,
        chi: chi,
        canChi: "".concat(can, " ").concat(chi),
    };
}
exports.getCanChiFromYear = getCanChiFromYear;
/** Chuyển tên Địa Chi sang số thứ tự 0..11 (Tý = 0, Sửu = 1, ..., Hợi = 11) */
function branchToZiIndex(branchName) {
    if (!branchName)
        return 0;
    var clean = branchName.trim();
    for (var i = 0; i < exports.BRANCHES_FROM_ZI.length; i++) {
        if (clean.includes(exports.BRANCHES_FROM_ZI[i]))
            return i;
    }
    for (var i = 0; i < exports.CN_BRANCHES_FROM_ZI.length; i++) {
        if (clean.includes(exports.CN_BRANCHES_FROM_ZI[i]))
            return i;
    }
    return 0;
}
exports.branchToZiIndex = branchToZiIndex;
/** Chuyển tên Thiên Can sang số thứ tự 0..9 (Giáp = 0, ..., Quý = 9) */
function stemToIndex(stemName) {
    if (!stemName)
        return 0;
    var clean = stemName.trim();
    for (var i = 0; i < exports.STEMS.length; i++) {
        if (clean.includes(exports.STEMS[i]))
            return i;
    }
    for (var i = 0; i < exports.CN_STEMS.length; i++) {
        if (clean.includes(exports.CN_STEMS[i]))
            return i;
    }
    return 0;
}
exports.stemToIndex = stemToIndex;
/** Kiểm tra năm sinh thuộc Dương Nam / Âm Nữ hay Âm Nam / Dương Nữ */
function isDuongNamOrAmNu(yearStem, gender) {
    var stemIdx = stemToIndex(yearStem);
    var isYangStem = stemIdx % 2 === 0; // Giáp, Bính, Mậu, Canh, Nhâm là Can Dương
    var isMale = (gender || '').toLowerCase() === 'male' || (gender || '') === 'Nam';
    // Dương Nam (Dương + Nam = true), Âm Nữ (Âm + Nữ = true)
    return (isYangStem && isMale) || (!isYangStem && !isMale);
}
exports.isDuongNamOrAmNu = isDuongNamOrAmNu;
/** Tìm ô cung trong `astrolabe.palaces` theo chỉ số Địa Chi (0 = Tý ... 11 = Hợi) */
function getPalaceByZiIndex(astrolabe, ziIndex) {
    if (!astrolabe || !astrolabe.palaces || !Array.isArray(astrolabe.palaces))
        return null;
    var cleanZi = ((ziIndex % 12) + 12) % 12;
    var vnBranch = exports.BRANCHES_FROM_ZI[cleanZi];
    var cnBranch = exports.CN_BRANCHES_FROM_ZI[cleanZi];
    // 1. Tìm theo thuộc tính earthlyBranch của cung (an toàn tuyệt đối)
    var found = astrolabe.palaces.find(function (p) {
        var b = (p.earthlyBranch || '').trim();
        return b === vnBranch || b === cnBranch;
    });
    if (found)
        return found;
    // 2. Fallback: Trong iztro cung 0 khởi từ Dần (2), nên cung Tý (0) = index 10
    var fallbackIdx = (cleanZi - 2 + 12) % 12;
    return astrolabe.palaces[fallbackIdx];
}
exports.getPalaceByZiIndex = getPalaceByZiIndex;
/** Tạo mới một Star object tương thích cả FunctionalStar lẫn plain JSON object */
function createStar(name, type, scope, palace, astrolabe) {
    if (scope === void 0) { scope = 'origin'; }
    try {
        var star = new FunctionalStar_1.default({
            name: name,
            type: type,
            scope: scope,
        });
        if (palace)
            star.setPalace(palace);
        if (astrolabe)
            star.setAstrolabe(astrolabe);
        return star;
    }
    catch (_a) {
        return { name: name, type: type, scope: scope };
    }
}
/** Xóa một danh sách tên sao khỏi mảng sao của cung */
function removeStarsByName(starList, targetNames) {
    if (!Array.isArray(starList))
        return;
    var _loop_1 = function (i) {
        var s = starList[i];
        var sName = typeof s === 'string' ? s : (s === null || s === void 0 ? void 0 : s.name) || '';
        if (targetNames.some(function (target) { return sName === target || sName.includes(target); })) {
            starList.splice(i, 1);
        }
    };
    for (var i = starList.length - 1; i >= 0; i--) {
        _loop_1(i);
    }
}
// ------------------------------------------------------------------------------
// 2. THUẬT TOÁN AN TUẦN KHÔNG VÀ TRIỆT LỘ ĐỘNG (2 CUNG LIỀN KỀ)
// ------------------------------------------------------------------------------
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
function calculateTrietBranches(canIndex) {
    var normCan = ((canIndex % 10) + 10) % 10;
    var startBranch = 8 - (normCan % 5) * 2;
    return [startBranch, startBranch + 1];
}
exports.calculateTrietBranches = calculateTrietBranches;
/**
 * Thuật toán an TUẦN KHÔNG ĐỘNG (Tính theo Tuần Giáp của năm sinh):
 * - Tính vị trí đầu tuần (Giáp): tuanChi = (chiIndex - canIndex + 12) % 12
 * - Hai cung Không Vong luôn là: [(tuanChi - 2 + 12) % 12, (tuanChi - 1 + 12) % 12]
 *
 * (Ví dụ: Mậu Dần -> can=4, chi=2 -> tuanChi = (2 - 4 + 12)%12 = 10 (Tuất) -> Tuần Không = [8, 9] (Thân, Dậu))
 * (Ví dụ: Bính Tuất -> can=2, chi=10 -> tuanChi = (10 - 2 + 12)%12 = 8 (Thân) -> Tuần Không = [6, 7] (Ngọ, Mùi))
 */
function calculateTuanBranches(canIndex, chiIndex) {
    var normCan = ((canIndex % 10) + 10) % 10;
    var normChi = ((chiIndex % 12) + 12) % 12;
    var tuanChi = (normChi - normCan + 120) % 12;
    var b1 = (tuanChi - 2 + 12) % 12;
    var b2 = (tuanChi - 1 + 12) % 12;
    return [b1, b2];
}
exports.calculateTuanBranches = calculateTuanBranches;
/**
 * Hàm an Tuần Không và Triệt Lộ tổng quát, chấp nhận cả số năm (>100), canIndex (0..9), hoặc chuỗi Can / Chi
 */
function calculateTuanTriet(yearOrStem, yearBranch) {
    var canIdx = 0;
    var chiIdx = 0;
    if (typeof yearOrStem === 'number') {
        if (yearOrStem > 100) {
            // Số năm lịch (VD: 2006, 1984)
            var cc = getCanChiFromYear(yearOrStem);
            canIdx = cc.canIndex;
            chiIdx = cc.chiIndex;
        }
        else {
            // Chỉ số canIndex (0..9)
            canIdx = ((yearOrStem % 10) + 10) % 10;
            if (typeof yearBranch === 'number') {
                chiIdx = ((yearBranch % 12) + 12) % 12;
            }
            else if (typeof yearBranch === 'string') {
                chiIdx = branchToZiIndex(yearBranch);
            }
        }
    }
    else {
        canIdx = stemToIndex(yearOrStem);
        chiIdx = typeof yearBranch === 'number' ? yearBranch : branchToZiIndex(yearBranch || '');
    }
    var trietBranches = calculateTrietBranches(canIdx);
    var tuanBranches = calculateTuanBranches(canIdx, chiIdx);
    return { trietBranches: trietBranches, tuanBranches: tuanBranches };
}
exports.calculateTuanTriet = calculateTuanTriet;
// ------------------------------------------------------------------------------
// 3. TÁCH BIỆT 2 TẦNG TỨ HÓA (ĐỘNG THEO TỪNG NĂM)
// ------------------------------------------------------------------------------
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
exports.VIETNAMESE_MUTAGEN_TABLE = {
    0: ['Liêm Trinh', 'Phá Quân', 'Vũ Khúc', 'Thái Dương'],
    1: ['Thiên Cơ', 'Thiên Lương', 'Tử Vi', 'Thái Âm'],
    2: ['Thiên Đồng', 'Thiên Cơ', 'Văn Xương', 'Liêm Trinh'],
    3: ['Thái Âm', 'Thiên Đồng', 'Thiên Cơ', 'Cự Môn'],
    4: ['Tham Lang', 'Thái Âm', 'Hữu Bật', 'Thiên Cơ'],
    5: ['Vũ Khúc', 'Tham Lang', 'Thiên Lương', 'Văn Khúc'],
    6: ['Thái Dương', 'Vũ Khúc', 'Thiên Đồng', 'Thái Âm'],
    7: ['Cự Môn', 'Thái Dương', 'Văn Khúc', 'Văn Xương'],
    8: ['Thiên Lương', 'Tử Vi', 'Tả Phù', 'Vũ Khúc'],
    9: ['Phá Quân', 'Cự Môn', 'Thái Âm', 'Tham Lang'],
};
function getVietnameseMutagenTable(yearStemOrYear, options) {
    if (options === void 0) { options = {}; }
    var stemIdx = 0;
    if (typeof yearStemOrYear === 'number') {
        if (yearStemOrYear > 100) {
            stemIdx = getCanChiFromYear(yearStemOrYear).canIndex;
        }
        else {
            stemIdx = ((yearStemOrYear % 10) + 10) % 10;
        }
    }
    else {
        stemIdx = stemToIndex(yearStemOrYear);
    }
    var row = exports.VIETNAMESE_MUTAGEN_TABLE[stemIdx] || exports.VIETNAMESE_MUTAGEN_TABLE[0];
    var loc = row[0], quyen = row[1], khoa = row[2], ky = row[3];
    if (stemIdx === 8 && options.nhamMutagenKhoa === 'ThienPhu') {
        khoa = 'Thiên Phủ';
    }
    return { loc: loc, quyen: quyen, khoa: khoa, ky: ky };
}
exports.getVietnameseMutagenTable = getVietnameseMutagenTable;
// ------------------------------------------------------------------------------
// 4. THIÊN KHÔI - THIÊN VIỆT ĐỘNG (THEO CAN NĂM SINH)
// ------------------------------------------------------------------------------
/**
 * Bảng tra Thiên Khôi - Thiên Việt ĐỘNG:
 * - Can 0, 4, 6 (Giáp, Mậu, Canh): Khôi tại Sửu (1), Việt tại Mùi (7)
 * - Can 1, 5 (Ất, Kỷ): Khôi tại Tý (0), Việt tại Thân (8)
 * - Can 2, 3 (Bính, Đinh): Khôi tại Hợi (11), Việt tại Dậu (9)
 * - Can 7 (Tân): Khôi tại Dần (2), Việt tại Ngọ (6)
 * - Can 8, 9 (Nhâm, Quý): Khôi tại Mão (3), Việt tại Tỵ (5)
 */
function calculateKuiYue(yearStemOrYear, options) {
    if (options === void 0) { options = {}; }
    var stemIdx = 0;
    if (typeof yearStemOrYear === 'number') {
        if (yearStemOrYear > 100) {
            stemIdx = getCanChiFromYear(yearStemOrYear).canIndex;
        }
        else {
            stemIdx = ((yearStemOrYear % 10) + 10) % 10;
        }
    }
    else {
        stemIdx = stemToIndex(yearStemOrYear);
    }
    // Can 0, 4, 6: Khôi Sửu (1), Việt Mùi (7)
    if (stemIdx === 0 || stemIdx === 4 || (stemIdx === 6 && options.canhKuiYue !== 'NgoDan')) {
        return { kuiBranch: 1, yueBranch: 7 };
    }
    if (stemIdx === 6 && options.canhKuiYue === 'NgoDan') {
        return { kuiBranch: 6, yueBranch: 2 };
    }
    // Can 1, 5: Khôi Tý (0), Việt Thân (8)
    if (stemIdx === 1 || stemIdx === 5) {
        return { kuiBranch: 0, yueBranch: 8 };
    }
    // Can 2, 3: Khôi Hợi (11), Việt Dậu (9)
    if (stemIdx === 2 || stemIdx === 3) {
        return { kuiBranch: 11, yueBranch: 9 };
    }
    // Can 7: Khôi Dần (2), Việt Ngọ (6)
    if (stemIdx === 7) {
        return { kuiBranch: 2, yueBranch: 6 };
    }
    // Can 8, 9: Khôi Mão (3), Việt Tỵ (5)
    if (stemIdx === 8 || stemIdx === 9) {
        return { kuiBranch: 3, yueBranch: 5 };
    }
    return { kuiBranch: 1, yueBranch: 7 };
}
exports.calculateKuiYue = calculateKuiYue;
// ------------------------------------------------------------------------------
// 5. MỆNH CHỦ ĐỘNG (THEO ĐỊA CHI CUNG AN MỆNH)
// ------------------------------------------------------------------------------
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
exports.SOUL_MASTER_MAP = {
    0: 'Tham Lang',
    1: 'Lộc Tồn',
    2: 'Lộc Tồn',
    3: 'Văn Khúc',
    4: 'Liêm Trinh',
    5: 'Vũ Khúc',
    6: 'Phá Quân',
    7: 'Vũ Khúc',
    8: 'Liêm Trinh',
    9: 'Văn Khúc',
    10: 'Lộc Tồn',
    11: 'Cự Môn', // Hợi
};
function calculateSoulMasterStar(menhBranchOrIdx, options) {
    if (options === void 0) { options = {}; }
    var bIdx = 0;
    if (typeof menhBranchOrIdx === 'number') {
        bIdx = ((menhBranchOrIdx % 12) + 12) % 12;
    }
    else {
        bIdx = branchToZiIndex(menhBranchOrIdx);
    }
    if (bIdx === 1 && options.chouSoulStar === 'CuMon') {
        return 'Cự Môn';
    }
    return exports.SOUL_MASTER_MAP[bIdx] || 'Lộc Tồn';
}
exports.calculateSoulMasterStar = calculateSoulMasterStar;
// ------------------------------------------------------------------------------
// HỎA TINH & LINH TINH (THEO GIỜ SINH & ÂM DƯƠNG NAM NỮ)
// ------------------------------------------------------------------------------
function calculateHuoLing(yearBranch, hourBranch, isDuongNamOrAmNuValue) {
    var yBranchIdx = branchToZiIndex(yearBranch);
    var hBranchIdx = branchToZiIndex(hourBranch);
    // A. HỎA TINH:
    // - Dần Ngọ Tuất (2, 6, 10): Khởi từ Sửu (1)
    // - Thân Tý Thìn (8, 0, 4): Khởi từ Dần (2)
    // - Tỵ Dậu Sửu (5, 9, 1): Khởi từ Mão (3)
    // - Hợi Mão Mùi (11, 3, 7): Khởi từ Dậu (9)
    // Đếm là giờ Tý, đi THUẬN đến giờ sinh
    var huoStart = 1;
    if ([2, 6, 10].includes(yBranchIdx))
        huoStart = 1;
    else if ([8, 0, 4].includes(yBranchIdx))
        huoStart = 2;
    else if ([5, 9, 1].includes(yBranchIdx))
        huoStart = 3;
    else if ([11, 3, 7].includes(yBranchIdx))
        huoStart = 9;
    var huoBranch = (huoStart + hBranchIdx) % 12;
    // B. LINH TINH:
    // - Dần Ngọ Tuất: Khởi từ Mão (3)
    // - Thân Tý Thìn, Tỵ Dậu Sửu, Hợi Mão Mùi: Khởi từ Tuất (10)
    // Dương Nam / Âm Nữ đi NGHỊCH; Âm Nam / Dương Nữ đi THUẬN
    var lingStart = 10;
    if ([2, 6, 10].includes(yBranchIdx))
        lingStart = 3;
    else
        lingStart = 10;
    var lingBranch = 0;
    if (isDuongNamOrAmNuValue) {
        lingBranch = (lingStart - hBranchIdx + 120) % 12; // Dương Nam / Âm Nữ: Đi Nghịch
    }
    else {
        lingBranch = (lingStart + hBranchIdx) % 12; // Âm Nam / Dương Nữ: Đi Thuận
    }
    return { huoBranch: huoBranch, lingBranch: lingBranch };
}
exports.calculateHuoLing = calculateHuoLing;
// ------------------------------------------------------------------------------
// BẢNG MAPPING NGŨ HÀNH TINH TÚ & PHÂN LOẠI CÁT / HUNG TINH CHUẨN NAM PHÁI
// ------------------------------------------------------------------------------
exports.STAR_ELEMENT_MAP = {
    // 14 Chính Tinh
    'Tử Vi': 'Tho',
    'Thiên Cơ': 'Moc',
    'Thái Dương': 'Hoa',
    'Vũ Khúc': 'Kim',
    'Thiên Đồng': 'Thuy',
    'Liêm Trinh': 'Hoa',
    'Thiên Phủ': 'Tho',
    'Thái Âm': 'Thuy',
    'Tham Lang': 'Thuy',
    'Cự Môn': 'Thuy',
    'Thiên Tướng': 'Thuy',
    'Thiên Lương': 'Moc',
    'Thất Sát': 'Kim',
    'Phá Quân': 'Thuy',
    // Chữ Hán 14 Chính Tinh
    '紫微': 'Tho', '天机': 'Moc', '太阳': 'Hoa', '武曲': 'Kim',
    '天同': 'Thuy', '廉贞': 'Hoa', '天府': 'Tho', '太阴': 'Thuy',
    '贪狼': 'Thuy', '巨门': 'Thuy', '天相': 'Thuy', '天梁': 'Moc',
    '七杀': 'Kim', '破军': 'Thuy',
    // Cát Tinh (Lục Cát Tinh & Cát Phụ Tinh)
    'Văn Xương': 'Kim',
    'Văn Khúc': 'Thuy',
    'Tả Phù': 'Tho',
    'Tả Phụ': 'Tho',
    'Hữu Bật': 'Tho',
    'Thiên Khôi': 'Hoa',
    'Thiên Việt': 'Hoa',
    'Lộc Tồn': 'Tho',
    'Long Đức': 'Thuy',
    'Thiên Giải': 'Hoa',
    'Địa Giải': 'Tho',
    'Giải Thần': 'Moc',
    'Phúc Đức': 'Tho',
    'Thiên Đức': 'Hoa',
    'Nguyệt Đức': 'Hoa',
    'Thiếu Âm': 'Thuy',
    'Thiếu Dương': 'Hoa',
    'Thiên Quan': 'Hoa',
    'Thiên Phúc': 'Tho',
    'Ân Quang': 'Moc',
    'Thiên Quý': 'Tho',
    'Tam Thai': 'Thuy',
    'Bát Tọa': 'Moc',
    'Thai Phụ': 'Kim',
    'Phong Cáo': 'Tho',
    'Long Trì': 'Thuy',
    'Phượng Các': 'Tho',
    'Đào Hoa': 'Moc',
    'Hồng Loan': 'Thuy',
    'Thiên Hỷ': 'Thuy',
    'Hoa Cái': 'Kim',
    'Tấu Thư': 'Kim',
    'Bác Sĩ': 'Thuy',
    'Lực Sĩ': 'Hoa',
    'Thanh Long': 'Thuy',
    'Tướng Quân': 'Moc',
    'Hỷ Thần': 'Hoa',
    'Quốc Ấn': 'Tho',
    'Đường Phù': 'Moc',
    'Thiên Mã': 'Hoa',
    'Thiên Tài': 'Tho',
    'Thiên Thọ': 'Tho',
    'Thiên Y': 'Thuy',
    'Tràng Sinh': 'Thuy',
    'Mộc Dục': 'Thuy',
    'Quan Đới': 'Kim',
    'Lâm Quan': 'Kim',
    'Đế Vượng': 'Kim',
    'Thai': 'Tho',
    'Dưỡng': 'Moc',
    // Hung & Sát Tinh
    'Kình Dương': 'Kim',
    'Đà La': 'Kim',
    'Hỏa Tinh': 'Hoa',
    'Linh Tinh': 'Hoa',
    'Địa Không': 'Hoa',
    'Địa Kiếp': 'Hoa',
    'Tang Môn': 'Moc',
    'Bạch Hổ': 'Kim',
    'Điếu Khách': 'Hoa',
    'Thiên Khốc': 'Thuy',
    'Thiên Hư': 'Thuy',
    'Đại Hao': 'Hoa',
    'Tiểu Hao': 'Hoa',
    'Bệnh Phù': 'Tho',
    'Tử Phù': 'Hoa',
    'Trực Phù': 'Hoa',
    'Tuế Phá': 'Hoa',
    'Quan Phù': 'Hoa',
    'Quan Phủ': 'Hoa',
    'Thiên Hình': 'Hoa',
    'Thiên Riêu': 'Thuy',
    'Cô Thần': 'Hoa',
    'Quả Tú': 'Hoa',
    'Kiếp Sát': 'Hoa',
    'Phá Toái': 'Hoa',
    'Phục Binh': 'Hoa',
    'Phi Liêm': 'Hoa',
    'Thiên La': 'Kim',
    'Địa Võng': 'Kim',
    'Thiên Thương': 'Tho',
    'Thiên Sứ': 'Thuy',
    'Lưu Hà': 'Thuy',
    'Suy': 'Thuy',
    'Bệnh': 'Hoa',
    'Tử': 'Thuy',
    'Mộ': 'Tho',
    'Tuyệt': 'Tho',
    // Sao Lưu Niên
    'L.Thái Tuế': 'Hoa',
    'L.Tang Môn': 'Moc',
    'L.Bạch Hổ': 'Kim',
    'L.Thiên Khốc': 'Thuy',
    'L.Thiên Hư': 'Thuy',
    'L.Lộc Tồn': 'Tho',
    'L.Kình Dương': 'Kim',
    'L.Đà La': 'Kim',
    'L.Thiên Mã': 'Hoa',
    'L.Đào Hoa': 'Moc',
    'L.Hồng Loan': 'Thuy',
    'L.Thiên Khôi': 'Hoa',
    'L.Thiên Việt': 'Hoa',
};
/** Lấy Ngũ Hành của một sao */
function getStarHanh(starName) {
    if (!starName)
        return 'Tho';
    var clean = starName.trim();
    if (exports.STAR_ELEMENT_MAP[clean])
        return exports.STAR_ELEMENT_MAP[clean];
    if (clean.startsWith('L.')) {
        var base = clean.slice(2);
        if (exports.STAR_ELEMENT_MAP[base])
            return exports.STAR_ELEMENT_MAP[base];
    }
    return 'Tho';
}
exports.getStarHanh = getStarHanh;
exports.MAJOR_STAR_NAMES = [
    'Tử Vi', 'Liêm Trinh', 'Thiên Đồng', 'Vũ Khúc', 'Thái Dương', 'Thiên Cơ',
    'Thiên Phủ', 'Thái Âm', 'Tham Lang', 'Cự Môn', 'Thiên Tướng', 'Thiên Lương',
    'Thất Sát', 'Phá Quân',
    '紫微', '廉贞', '天同', '武曲', '太阳', '天机',
    '天府', '太阴', '贪狼', '巨门', '天相', '天梁',
    '七杀', '破军'
];
exports.BAD_STAR_NAMES = [
    // Lục Sát Tinh
    'Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh', 'Địa Không', 'Địa Kiếp',
    '擎羊', '陀罗', '火星', '铃星', '地空', '地劫',
    // Bại Tinh & Hung Tinh Khác
    'Tang Môn', 'Bạch Hổ', 'Điếu Khách', 'Thiên Khốc', 'Thiên Hư',
    'Đại Hao', 'Tiểu Hao', 'Bệnh Phù', 'Tử Phù', 'Trực Phù', 'Tuế Phá',
    'Quan Phù', 'Quan Phủ', 'Thiên Hình', 'Thiên Riêu', 'Cô Thần', 'Quả Tú',
    'Kiếp Sát', 'Phá Toái', 'Phục Binh', 'Phi Liêm', 'Thiên La', 'Địa Võng',
    'Thiên Thương', 'Thiên Sứ', 'Lưu Hà', 'Hóa Kỵ',
    '丧门', '白虎', '吊客', '天哭', '天虚', '大耗', '小耗', '病符', '死符',
    '岁破', '官府', '官符', '天刑', '天姚', '孤辰', '寡宿', '劫煞', '破碎',
    '伏兵', '飞廉', '天罗', '地网', '天伤', '天使', '化忌'
];
function isBadStar(starName) {
    if (!starName)
        return false;
    var clean = starName.trim();
    return exports.BAD_STAR_NAMES.some(function (b) { return clean === b || clean.includes(b); });
}
exports.isBadStar = isBadStar;
// ------------------------------------------------------------------------------
// 6. BỘ 13 SAO LƯU NIÊN (LƯU TINH HẠN NĂM THEO `targetYear`)
// ------------------------------------------------------------------------------
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
function calculateYearlyStars(targetYear) {
    var _a;
    var cc = getCanChiFromYear(targetYear);
    var targetStemIdx = cc.canIndex;
    var targetBranchIdx = cc.chiIndex;
    var targetStem = cc.can;
    var targetBranch = cc.chi;
    var starsMap = {};
    for (var i = 0; i < 12; i++)
        starsMap[i] = [];
    var addStar = function (branchZiIdx, starName, type) {
        if (type === void 0) { type = 'yearly'; }
        var cleanIdx = ((branchZiIdx % 12) + 12) % 12;
        var h = getStarHanh(starName);
        starsMap[cleanIdx].push({
            name: starName,
            type: type,
            scope: 'yearly',
            palaceIndex: cleanIdx,
            earthlyBranch: exports.BRANCHES_FROM_ZI[cleanIdx],
            hanh: h,
            chinhTinhHanh: h,
        });
    };
    // 1. L.Thái Tuế: Tại cung trùng Chi năm xem
    addStar(targetBranchIdx, 'L.Thái Tuế');
    // 2. L.Tang Môn: Cách L.Thái Tuế 2 cung thuận (+2)
    var tangMonBranch = (targetBranchIdx + 2) % 12;
    addStar(tangMonBranch, 'L.Tang Môn');
    // 3. L.Bạch Hổ: Xung chiếu trực diện với L.Tang Môn (+6)
    var bachHoBranch = (tangMonBranch + 6) % 12;
    addStar(bachHoBranch, 'L.Bạch Hổ');
    // 4. L.Thiên Khốc: Khởi từ Ngọ (6) đi NGHỊCH đến Chi năm xem
    var khocBranch = (6 - targetBranchIdx + 12) % 12;
    addStar(khocBranch, 'L.Thiên Khốc');
    // 5. L.Thiên Hư: Khởi từ Tý đếm thuận đến Chi năm xem
    var huBranch = targetBranchIdx;
    addStar(huBranch, 'L.Thiên Hư');
    // 6. L.Lộc Tồn: Tính theo Can năm xem
    var LOC_TON_MAP = {
        0: 2,
        1: 3,
        2: 5,
        3: 6,
        4: 5,
        5: 6,
        6: 8,
        7: 9,
        8: 11,
        9: 0, // Quý -> Tý (0)
    };
    var locTonBranch = (_a = LOC_TON_MAP[targetStemIdx]) !== null && _a !== void 0 ? _a : 2;
    addStar(locTonBranch, 'L.Lộc Tồn');
    // 7. L.Kình Dương: Cung tiến 1 so với L.Lộc Tồn (+1)
    addStar((locTonBranch + 1) % 12, 'L.Kình Dương');
    // 8. L.Đà La: Cung lùi 1 so với L.Lộc Tồn (-1)
    addStar((locTonBranch - 1 + 12) % 12, 'L.Đà La');
    // 9. L.Thiên Mã: Theo Tam hợp Chi năm xem
    var maBranch = 8;
    if ([2, 6, 10].includes(targetBranchIdx))
        maBranch = 8; // Dần Ngọ Tuất -> Thân (8)
    else if ([8, 0, 4].includes(targetBranchIdx))
        maBranch = 2; // Thân Tý Thìn -> Dần (2)
    else if ([5, 9, 1].includes(targetBranchIdx))
        maBranch = 11; // Tỵ Dậu Sửu -> Hợi (11)
    else if ([11, 3, 7].includes(targetBranchIdx))
        maBranch = 5; // Hợi Mão Mùi -> Tỵ (5)
    addStar(maBranch, 'L.Thiên Mã');
    // 10. L.Đào Hoa: Theo Tam hợp Chi năm xem
    var daoBranch = 3;
    if ([2, 6, 10].includes(targetBranchIdx))
        daoBranch = 3; // Dần Ngọ Tuất -> Mão (3)
    else if ([8, 0, 4].includes(targetBranchIdx))
        daoBranch = 9; // Thân Tý Thìn -> Dậu (9)
    else if ([5, 9, 1].includes(targetBranchIdx))
        daoBranch = 6; // Tỵ Dậu Sửu -> Ngọ (6)
    else if ([11, 3, 7].includes(targetBranchIdx))
        daoBranch = 0; // Hợi Mão Mùi -> Tý (0)
    addStar(daoBranch, 'L.Đào Hoa');
    // 11. L.Hồng Loan: Khởi Mão (3) tại Tý (0), đi NGHỊCH đến Chi năm xem
    var hongLoanBranch = (3 - targetBranchIdx + 12) % 12;
    addStar(hongLoanBranch, 'L.Hồng Loan');
    // 12. L.Thiên Khôi: Theo Can năm xem
    var _b = calculateKuiYue(targetStemIdx), khoiBranch = _b.kuiBranch, vietBranch = _b.yueBranch;
    addStar(khoiBranch, 'L.Thiên Khôi');
    // 13. L.Thiên Việt: Theo Can năm xem
    addStar(vietBranch, 'L.Thiên Việt');
    return { yearStem: targetStem, yearBranch: targetBranch, starsMap: starsMap };
}
exports.calculateYearlyStars = calculateYearlyStars;
// ------------------------------------------------------------------------------
// HÀM ADAPTER CHÍNH: vietnamAstrologyAdapter (ENGINE TỰ ĐỘNG ĐỘNG 100%)
// ------------------------------------------------------------------------------
/**
 * Hàm adapter chính: Nhận astrolabe từ iztro, ghi đè toàn diện 6 quy tắc Tử Vi Việt Nam
 * bằng các thuật toán toán học động 100% cho BẤT KỲ NĂM SINH NÀO và BẤT KỲ NĂM XEM HẠN NÀO.
 *
 * @param astrolabe Đối tượng FunctionalAstrolabe hoặc JSON Astrolabe từ iztro
 * @param options Tùy chọn cấu hình hoặc số năm xem hạn (number)
 * @returns Đối tượng lá số đã được chuẩn hóa hoàn toàn theo Nam Phái Việt Nam
 */
function vietnamAstrologyAdapter(astrolabe, options) {
    var _a, _b, _c, _d;
    if (!astrolabe || !astrolabe.palaces || !Array.isArray(astrolabe.palaces)) {
        return astrolabe;
    }
    var astroObj = astrolabe;
    var opts = typeof options === 'number' ? { targetYear: options } : options || {};
    var targetYear = opts.targetYear || new Date().getFullYear();
    // 1. TRÍCH XUẤT CAN CHI NĂM SINH VÀ GIỜ SINH ĐỘNG
    var birthYearNum = 0;
    if (astroObj.solarDate) {
        var y = parseInt(astroObj.solarDate.split('-')[0], 10);
        if (!isNaN(y) && y > 0)
            birthYearNum = y;
    }
    var yearStem = 'Giáp';
    var yearBranch = 'Tý';
    var hourBranch = 'Tý';
    if ((_b = (_a = astroObj.rawDates) === null || _a === void 0 ? void 0 : _a.chineseDate) === null || _b === void 0 ? void 0 : _b.yearly) {
        yearStem = astroObj.rawDates.chineseDate.yearly[0] || 'Giáp';
        yearBranch = astroObj.rawDates.chineseDate.yearly[1] || 'Tý';
    }
    else if (astroObj.chineseDate) {
        var parts = astroObj.chineseDate.split(' - ');
        var yPillar = parts[0] || 'Giáp Tý';
        var yTokens = yPillar.trim().split(' ');
        yearStem = yTokens[0] || 'Giáp';
        yearBranch = yTokens[1] || 'Tý';
    }
    else if (birthYearNum > 0) {
        var cc = getCanChiFromYear(birthYearNum);
        yearStem = cc.can;
        yearBranch = cc.chi;
    }
    if ((_d = (_c = astroObj.rawDates) === null || _c === void 0 ? void 0 : _c.chineseDate) === null || _d === void 0 ? void 0 : _d.hourly) {
        hourBranch = astroObj.rawDates.chineseDate.hourly[1] || 'Tý';
    }
    else if (astroObj.time) {
        hourBranch = astroObj.time.replace(/giờ|Giờ/g, '').trim() || 'Tý';
    }
    var birthStemIdx = stemToIndex(yearStem);
    var birthBranchIdx = branchToZiIndex(yearBranch);
    var isDuongNamOrAmNuVal = isDuongNamOrAmNu(yearStem, astroObj.gender);
    // ============================================================================
    // 1. GHI ĐÈ TUẦN KHÔNG VÀ TRIỆT LỘ ĐỘNG (2 CUNG LIỀN KỀ)
    // ============================================================================
    var XUN_JIE_NAMES = ['Tuần Không', 'Triệt Lộ', 'Tuần', 'Triệt', 'Không Vong', '截空', '旬空', '截路', '空亡'];
    astroObj.palaces.forEach(function (p) {
        removeStarsByName(p.minorStars, XUN_JIE_NAMES);
        removeStarsByName(p.adjectiveStars, XUN_JIE_NAMES);
        p.hasTuan = false;
        p.hasTriet = false;
        p.co_tuan = false;
        p.co_triet = false;
    });
    var _e = calculateTuanTriet(birthStemIdx, yearBranch), trietBranches = _e.trietBranches, tuanBranches = _e.tuanBranches;
    trietBranches.forEach(function (bIdx) {
        var palace = getPalaceByZiIndex(astroObj, bIdx);
        if (palace) {
            palace.hasTriet = true;
            palace.co_triet = true;
            removeStarsByName(palace.adjectiveStars, XUN_JIE_NAMES);
            removeStarsByName(palace.minorStars, XUN_JIE_NAMES);
        }
    });
    tuanBranches.forEach(function (bIdx) {
        var palace = getPalaceByZiIndex(astroObj, bIdx);
        if (palace) {
            palace.hasTuan = true;
            palace.co_tuan = true;
            removeStarsByName(palace.adjectiveStars, XUN_JIE_NAMES);
            removeStarsByName(palace.minorStars, XUN_JIE_NAMES);
        }
    });
    // ============================================================================
    // 2. GHI ĐÈ HỎA TINH VÀ LINH TINH (THEO GIỜ SINH & ÂM DƯƠNG NAM NỮ)
    // ============================================================================
    var _f = calculateHuoLing(yearBranch, hourBranch, isDuongNamOrAmNuVal), huoBranch = _f.huoBranch, lingBranch = _f.lingBranch;
    if (opts.cleanOldStars !== false) {
        var OLD_HUO_LING_1 = ['Hỏa Tinh', 'Linh Tinh', '火星', '铃星'];
        astroObj.palaces.forEach(function (p) {
            removeStarsByName(p.minorStars, OLD_HUO_LING_1);
            removeStarsByName(p.adjectiveStars, OLD_HUO_LING_1);
        });
    }
    var huoPalace = getPalaceByZiIndex(astroObj, huoBranch);
    if (huoPalace) {
        if (!huoPalace.minorStars)
            huoPalace.minorStars = [];
        huoPalace.minorStars.push(createStar('Hỏa Tinh', 'tough', 'origin', huoPalace, astroObj));
    }
    var lingPalace = getPalaceByZiIndex(astroObj, lingBranch);
    if (lingPalace) {
        if (!lingPalace.minorStars)
            lingPalace.minorStars = [];
        lingPalace.minorStars.push(createStar('Linh Tinh', 'tough', 'origin', lingPalace, astroObj));
    }
    // ============================================================================
    // 3. TÁCH BIỆT 2 TẦNG TỨ HÓA (ĐỘNG THEO TỪNG NĂM)
    // ============================================================================
    // --- TẦNG 1: TỨ HÓA BẢN MỆNH (GỐC) - TÍNH THEO CAN NĂM SINH ---
    var birthMutagenTable = getVietnameseMutagenTable(birthStemIdx, opts);
    var bLoc = birthMutagenTable.loc, bQuyen = birthMutagenTable.quyen, bKhoa = birthMutagenTable.khoa, bKy = birthMutagenTable.ky;
    astroObj.palaces.forEach(function (p) {
        var allStars = __spreadArray(__spreadArray(__spreadArray([], (p.majorStars || []), true), (p.minorStars || []), true), (p.adjectiveStars || []), true);
        allStars.forEach(function (s) {
            if (!s || !s.name)
                return;
            var sName = s.name.trim();
            if (sName === bLoc) {
                s.mutagen = 'Hóa Lộc';
                s.hoa = 'Lộc';
                s.originMutagen = 'Lộc';
                s.originMutagenLabel = '[Lộc]';
            }
            else if (sName === bQuyen) {
                s.mutagen = 'Hóa Quyền';
                s.hoa = 'Quyền';
                s.originMutagen = 'Quyền';
                s.originMutagenLabel = '[Quyền]';
            }
            else if (sName === bKhoa) {
                s.mutagen = 'Hóa Khoa';
                s.hoa = 'Khoa';
                s.originMutagen = 'Khoa';
                s.originMutagenLabel = '[Khoa]';
            }
            else if (sName === bKy) {
                s.mutagen = 'Hóa Kỵ';
                s.hoa = 'Kỵ';
                s.originMutagen = 'Kỵ';
                s.originMutagenLabel = '[Kỵ]';
            }
            else {
                if (s.mutagen)
                    s.mutagen = undefined;
                if (s.hoa)
                    s.hoa = undefined;
                if (s.originMutagen)
                    s.originMutagen = undefined;
                if (s.originMutagenLabel)
                    s.originMutagenLabel = undefined;
            }
        });
    });
    // --- TẦNG 2: TỨ HÓA LƯU NIÊN - TÍNH THEO CAN CỦA TARGETYEAR ---
    var targetYearCanChiInfo = getCanChiFromYear(targetYear);
    var targetCanIndex = targetYearCanChiInfo.canIndex;
    var targetMutagenTable = getVietnameseMutagenTable(targetCanIndex, opts);
    var lnLoc = targetMutagenTable.loc, lnQuyen = targetMutagenTable.quyen, lnKhoa = targetMutagenTable.khoa, lnKy = targetMutagenTable.ky;
    var yearlyMutagenArray = [lnLoc, lnQuyen, lnKhoa, lnKy];
    astroObj.yearlyMutagen = yearlyMutagenArray;
    astroObj.yearlyMutagens = { loc: lnLoc, quyen: lnQuyen, khoa: lnKhoa, ky: lnKy };
    if (astroObj.overlay) {
        astroObj.overlay.yearlyMutagen = yearlyMutagenArray;
        astroObj.overlay.yearlyMutagens = { loc: lnLoc, quyen: lnQuyen, khoa: lnKhoa, ky: lnKy };
    }
    // Gắn nhãn riêng biệt có tiền tố [LN.Lộc], [LN.Quyền], [LN.Khoa], [LN.Kỵ], KHÔNG GHI ĐÈ Tứ Hóa bản mệnh
    astroObj.palaces.forEach(function (p) {
        var allStars = __spreadArray(__spreadArray(__spreadArray([], (p.majorStars || []), true), (p.minorStars || []), true), (p.adjectiveStars || []), true);
        allStars.forEach(function (s) {
            if (!s || !s.name)
                return;
            var sName = s.name.trim();
            if (sName === lnLoc) {
                s.yearlyMutagen = 'LN.Lộc';
                s.lnMutagen = 'LN.Lộc';
                s.luuMutagen = 'LN.Lộc';
                s.luuHoa = 'LN.Lộc';
                s.yearlyMutagenLabel = '[LN.Lộc]';
            }
            else if (sName === lnQuyen) {
                s.yearlyMutagen = 'LN.Quyền';
                s.lnMutagen = 'LN.Quyền';
                s.luuMutagen = 'LN.Quyền';
                s.luuHoa = 'LN.Quyền';
                s.yearlyMutagenLabel = '[LN.Quyền]';
            }
            else if (sName === lnKhoa) {
                s.yearlyMutagen = 'LN.Khoa';
                s.lnMutagen = 'LN.Khoa';
                s.luuMutagen = 'LN.Khoa';
                s.luuHoa = 'LN.Khoa';
                s.yearlyMutagenLabel = '[LN.Khoa]';
            }
            else if (sName === lnKy) {
                s.yearlyMutagen = 'LN.Kỵ';
                s.lnMutagen = 'LN.Kỵ';
                s.luuMutagen = 'LN.Kỵ';
                s.luuHoa = 'LN.Kỵ';
                s.yearlyMutagenLabel = '[LN.Kỵ]';
            }
            else {
                s.yearlyMutagen = undefined;
                s.lnMutagen = undefined;
                s.luuMutagen = undefined;
                s.luuHoa = undefined;
                s.yearlyMutagenLabel = undefined;
            }
        });
    });
    // ============================================================================
    // 4. GHI ĐÈ THIÊN KHÔI & THIÊN VIỆT ĐỘNG (THEO CAN NĂM SINH)
    // ============================================================================
    var _g = calculateKuiYue(birthStemIdx, opts), kuiBranch = _g.kuiBranch, yueBranch = _g.yueBranch;
    if (opts.cleanOldStars !== false) {
        var OLD_KUI_YUE_1 = ['Thiên Khôi', 'Thiên Việt', '天魁', '天钺'];
        astroObj.palaces.forEach(function (p) {
            removeStarsByName(p.minorStars, OLD_KUI_YUE_1);
            removeStarsByName(p.adjectiveStars, OLD_KUI_YUE_1);
        });
    }
    var kuiPalace = getPalaceByZiIndex(astroObj, kuiBranch);
    if (kuiPalace) {
        if (!kuiPalace.minorStars)
            kuiPalace.minorStars = [];
        kuiPalace.minorStars.push(createStar('Thiên Khôi', 'soft', 'origin', kuiPalace, astroObj));
    }
    var yuePalace = getPalaceByZiIndex(astroObj, yueBranch);
    if (yuePalace) {
        if (!yuePalace.minorStars)
            yuePalace.minorStars = [];
        yuePalace.minorStars.push(createStar('Thiên Việt', 'soft', 'origin', yuePalace, astroObj));
    }
    // ============================================================================
    // 5. GHI ĐÈ MỆNH CHỦ ĐỘNG (THEO ĐỊA CHI CUNG AN MỆNH)
    // ============================================================================
    var menhPalace = astroObj.palaces.find(function (p) { return p.name === 'Mệnh' || p.name === '命宫' || p.name === '命'; }) ||
        astroObj.palaces.find(function (p) { return (p.name || '').trim().startsWith('Mệnh'); }) ||
        (astroObj.earthlyBranchOfSoulPalace
            ? astroObj.palaces.find(function (p) { return (p.earthlyBranch || '').trim() === astroObj.earthlyBranchOfSoulPalace.trim(); })
            : null) ||
        astroObj.palaces[0];
    var menhBranchStr = (astroObj.earthlyBranchOfSoulPalace || (menhPalace === null || menhPalace === void 0 ? void 0 : menhPalace.earthlyBranch) || 'Tý').trim();
    var menhBranchIdx = branchToZiIndex(menhBranchStr);
    var soulStar = calculateSoulMasterStar(menhBranchIdx, opts);
    astroObj.soul = soulStar;
    astroObj.masterStar = soulStar;
    astroObj.menh_chu = soulStar;
    astroObj.menhChu = soulStar;
    // ============================================================================
    // 6. BỔ SUNG BỘ 13 SAO LƯU NIÊN (LƯU TINH HẠN NĂM VÀO `yearlyStars`)
    // ============================================================================
    var _h = calculateYearlyStars(targetYear), luStem = _h.yearStem, luBranch = _h.yearBranch, starsMap = _h.starsMap;
    astroObj.targetYear = targetYear;
    astroObj.targetYearCanChi = "".concat(luStem, " ").concat(luBranch);
    var allYearlyStarsList = [];
    // ============================================================================
    // 7. CẤU TRÚC LẠI THUỘC TÍNH SAO TRONG TỪNG Ô CUNG
    // ============================================================================
    astroObj.palaces.forEach(function (palace) {
        // 1. majorStars: Chuẩn hóa đắc hãm và gán ngũ hành
        if (!Array.isArray(palace.majorStars))
            palace.majorStars = [];
        palace.majorStars.forEach(function (s) {
            var h = getStarHanh(s.name);
            s.chinhTinhHanh = h;
            s.hanh = h;
            s.type = 'major';
        });
        // 2. Thu thập và phân loại cát tinh (goodStars) & hung/sát tinh (badStars)
        var rawSubStars = __spreadArray(__spreadArray([], (palace.minorStars || []), true), (palace.adjectiveStars || []), true);
        // Thêm các sao từ các vòng nếu chưa có
        if (palace.boshi12 && !rawSubStars.some(function (s) { return s.name === palace.boshi12; })) {
            rawSubStars.push(createStar(palace.boshi12, 'soft', 'origin', palace, astroObj));
        }
        if (palace.suiqian12 && !rawSubStars.some(function (s) { return s.name === palace.suiqian12; })) {
            rawSubStars.push(createStar(palace.suiqian12, 'adjective', 'origin', palace, astroObj));
        }
        if (palace.jiangqian12) {
            var jName_1 = palace.jiangqian12 === 'Hàm Trì' ? 'Đào Hoa' : palace.jiangqian12;
            if (!rawSubStars.some(function (s) { return s.name === jName_1; })) {
                rawSubStars.push(createStar(jName_1, 'adjective', 'origin', palace, astroObj));
            }
        }
        // Loại bỏ sao Tuần/Triệt và trùng lặp theo tên
        var seenNames = new Set();
        var uniqueSubStars = [];
        rawSubStars.forEach(function (s) {
            var name = (s.name || '').trim();
            if (!name || XUN_JIE_NAMES.includes(name) || seenNames.has(name))
                return;
            seenNames.add(name);
            uniqueSubStars.push(s);
        });
        var goodStars = [];
        var badStars = [];
        uniqueSubStars.forEach(function (s) {
            var h = getStarHanh(s.name);
            s.chinhTinhHanh = h;
            s.hanh = h;
            if (isBadStar(s.name)) {
                s.type = 'tough';
                badStars.push(s);
            }
            else {
                s.type = 'soft';
                goodStars.push(s);
            }
        });
        palace.goodStars = goodStars;
        palace.badStars = badStars;
        // Duy trì tương thích với iztro
        palace.minorStars = uniqueSubStars.filter(function (s) { return s.type === 'soft' || s.type === 'tough'; });
        palace.adjectiveStars = uniqueSubStars.filter(function (s) { return s.type !== 'soft' && s.type !== 'tough'; });
        // 3. yearlyStars: Mảng sao lưu có tiền tố 'L.'
        var bIdx = branchToZiIndex(palace.earthlyBranch || 'Tý');
        var palaceYearly = starsMap[bIdx] || [];
        palace.yearlyStars = palaceYearly.map(function (s) { return ({
            name: s.name,
            type: 'yearly',
            scope: 'yearly',
            hanh: s.hanh,
            chinhTinhHanh: s.chinhTinhHanh,
        }); });
        allYearlyStarsList.push.apply(allYearlyStarsList, palaceYearly);
    });
    astroObj.yearlyStars = allYearlyStarsList;
    return astroObj;
}
exports.vietnamAstrologyAdapter = vietnamAstrologyAdapter;
// ------------------------------------------------------------------------------
// CÁC WRAPPER TIỆN DỤNG THAY THẾ TRỰC TIẾP API IZTRO
// ------------------------------------------------------------------------------
/**
 * Hàm wrapper tiện ích an sao theo Dương Lịch chuẩn Tử Vi Việt Nam
 */
function astrolabeBySolarDate(solarDateStr, timeIndex, gender, fixLeap, language, options) {
    if (fixLeap === void 0) { fixLeap = true; }
    if (language === void 0) { language = 'vi-VN'; }
    var baseAstrolabe = astro.bySolar(solarDateStr, timeIndex, gender, fixLeap, language);
    return vietnamAstrologyAdapter(baseAstrolabe, options);
}
exports.astrolabeBySolarDate = astrolabeBySolarDate;
/**
 * Hàm wrapper tiện ích an sao theo Âm Lịch chuẩn Tử Vi Việt Nam
 */
function astrolabeByLunarDate(lunarDateStr, timeIndex, gender, isLeapMonth, fixLeap, language, options) {
    if (isLeapMonth === void 0) { isLeapMonth = false; }
    if (fixLeap === void 0) { fixLeap = true; }
    if (language === void 0) { language = 'vi-VN'; }
    var baseAstrolabe = astro.byLunar(lunarDateStr, timeIndex, gender, isLeapMonth, fixLeap, language);
    return vietnamAstrologyAdapter(baseAstrolabe, options);
}
exports.astrolabeByLunarDate = astrolabeByLunarDate;
exports.applyVietnamAstrologyRules = vietnamAstrologyAdapter;
exports.default = vietnamAstrologyAdapter;
