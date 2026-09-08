"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getVietnameseSoulAndBody = exports.getVietnameseChangSheng12 = exports.VIETNAMESE_CHANGSHENG_STARS = exports.getVietnameseBoShi12 = exports.getVietnameseSuiQian12 = exports.VIETNAMESE_BOSHI_STARS = exports.VIETNAMESE_SUIQIAN_STARS = exports.getVietnameseHuoLing = exports.getVietnameseKuiYue = exports.getTuanTrietPalaceIndices = exports.isDuongNamOrAmNu = exports.stemToIndex = exports.branchToZiIndex = exports.branchToPalaceIndex = exports.PALACE_BRANCHES_FROM_YIN = exports.STEMS = exports.BRANCHES_FROM_ZI = void 0;
/**
 * Danh sách 12 Địa Chi theo thứ tự chuẩn từ Tý đến Hợi (để tính toán can chi)
 */
exports.BRANCHES_FROM_ZI = [
    'Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'
];
/**
 * Danh sách 10 Thiên Can theo thứ tự chuẩn
 */
exports.STEMS = [
    'Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý'
];
/**
 * Danh sách 12 Cung theo thứ tự cung trong iztro (Bắt đầu từ Cung Dần = 0)
 * 0: Dần, 1: Mão, 2: Thìn, 3: Tỵ, 4: Ngọ, 5: Mùi,
 * 6: Thân, 7: Dậu, 8: Tuất, 9: Hợi, 10: Tý, 11: Sửu
 */
exports.PALACE_BRANCHES_FROM_YIN = [
    'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi', 'Tý', 'Sửu'
];
/**
 * Chuyển đổi tên Địa Chi thành chỉ số cung iztro (0: Dần -> 11: Sửu)
 */
function branchToPalaceIndex(branchName) {
    var clean = branchName.trim();
    for (var i = 0; i < exports.PALACE_BRANCHES_FROM_YIN.length; i++) {
        if (clean.includes(exports.PALACE_BRANCHES_FROM_YIN[i])) {
            return i;
        }
    }
    // Hỗ trợ tiếng Trung
    var CN_MAP = {
        '寅': 0, '卯': 1, '辰': 2, '巳': 3, '午': 4, '未': 5,
        '申': 6, '酉': 7, '戌': 8, '亥': 9, '子': 10, '丑': 11
    };
    for (var _i = 0, _a = Object.entries(CN_MAP); _i < _a.length; _i++) {
        var _b = _a[_i], cn = _b[0], idx = _b[1];
        if (clean.includes(cn))
            return idx;
    }
    return 0;
}
exports.branchToPalaceIndex = branchToPalaceIndex;
/**
 * Chuyển đổi tên Địa Chi thành chỉ số chi chuẩn từ Tý = 0 đến Hợi = 11
 */
function branchToZiIndex(branchName) {
    var clean = branchName.trim();
    for (var i = 0; i < exports.BRANCHES_FROM_ZI.length; i++) {
        if (clean.includes(exports.BRANCHES_FROM_ZI[i])) {
            return i;
        }
    }
    var CN_ZI_MAP = {
        '子': 0, '丑': 1, '寅': 2, '卯': 3, '辰': 4, '巳': 5,
        '午': 6, '未': 7, '申': 8, '酉': 9, '戌': 10, '亥': 11
    };
    for (var _i = 0, _a = Object.entries(CN_ZI_MAP); _i < _a.length; _i++) {
        var _b = _a[_i], cn = _b[0], idx = _b[1];
        if (clean.includes(cn))
            return idx;
    }
    return 0;
}
exports.branchToZiIndex = branchToZiIndex;
/**
 * Chuyển đổi tên Thiên Can thành chỉ số từ Giáp = 0 đến Quý = 9
 */
function stemToIndex(stemName) {
    var clean = stemName.trim();
    for (var i = 0; i < exports.STEMS.length; i++) {
        if (clean.includes(exports.STEMS[i])) {
            return i;
        }
    }
    var CN_STEM_MAP = {
        '甲': 0, '乙': 1, '丙': 2, '丁': 3, '戊': 4,
        '己': 5, '庚': 6, '辛': 7, '壬': 8, '癸': 9
    };
    for (var _i = 0, _a = Object.entries(CN_STEM_MAP); _i < _a.length; _i++) {
        var _b = _a[_i], cn = _b[0], idx = _b[1];
        if (clean.includes(cn))
            return idx;
    }
    return 0;
}
exports.stemToIndex = stemToIndex;
/**
 * Xác định thuộc tính Âm Dương Nam Nữ
 * @returns true nếu là Dương Nam hoặc Âm Nữ (thuận), false nếu là Âm Nam hoặc Dương Nữ (nghịch)
 */
function isDuongNamOrAmNu(stemName, gender) {
    var sIdx = stemToIndex(stemName);
    var isYangStem = sIdx % 2 === 0; // Giáp, Bính, Mậu, Canh, Nhâm là Dương
    var isMale = gender === 'Nam' || gender === 'male' || gender === 'nam' || gender === '男';
    // Dương Nam hoặc Âm Nữ là thuận
    return (isYangStem && isMale) || (!isYangStem && !isMale);
}
exports.isDuongNamOrAmNu = isDuongNamOrAmNu;
function getTuanTrietPalaceIndices(stemName, branchName) {
    var sIdx = stemToIndex(stemName);
    var bZiIdx = branchToZiIndex(branchName);
    // A. Triệt Lộ Không Vong (theo Can năm sinh):
    // Giáp (0), Kỷ (5): Thân - Dậu (Palace [6, 7])
    // Ất (1), Canh (6): Ngọ - Mùi (Palace [4, 5])
    // Bính (2), Tân (7): Thìn - Tỵ (Palace [2, 3])
    // Đinh (3), Nhâm (8): Dần - Mão (Palace [0, 1])
    // Mậu (4), Quý (9): Tý - Sửu (Palace [10, 11])
    var TRIET_MAP = {
        0: { indices: [6, 7], branches: ['Thân', 'Dậu'] },
        5: { indices: [6, 7], branches: ['Thân', 'Dậu'] },
        1: { indices: [4, 5], branches: ['Ngọ', 'Mùi'] },
        6: { indices: [4, 5], branches: ['Ngọ', 'Mùi'] },
        2: { indices: [2, 3], branches: ['Thìn', 'Tỵ'] },
        7: { indices: [2, 3], branches: ['Thìn', 'Tỵ'] },
        3: { indices: [0, 1], branches: ['Dần', 'Mão'] },
        8: { indices: [0, 1], branches: ['Dần', 'Mão'] },
        4: { indices: [10, 11], branches: ['Tý', 'Sửu'] },
        9: { indices: [10, 11], branches: ['Tý', 'Sửu'] },
    };
    var triet = TRIET_MAP[sIdx] || { indices: [2, 3], branches: ['Thìn', 'Tỵ'] };
    // B. Tuần Trung Không Vong (theo Tuần Giáp):
    // Tính con giáp đầu tuần: (Chi - Can + 12) % 12
    var giapZiBranch = (bZiIdx - sIdx + 12) % 12;
    var TUAN_MAP = {
        0: { indices: [8, 9], branches: ['Tuất', 'Hợi'] },
        10: { indices: [6, 7], branches: ['Thân', 'Dậu'] },
        8: { indices: [4, 5], branches: ['Ngọ', 'Mùi'] },
        6: { indices: [2, 3], branches: ['Thìn', 'Tỵ'] },
        4: { indices: [0, 1], branches: ['Dần', 'Mão'] },
        2: { indices: [10, 11], branches: ['Tý', 'Sửu'] }, // Tuần Giáp Dần (2)
    };
    var tuan = TUAN_MAP[giapZiBranch] || { indices: [4, 5], branches: ['Ngọ', 'Mùi'] };
    return {
        trietPalaceIndices: triet.indices,
        tuanPalaceIndices: tuan.indices,
        trietBranches: triet.branches,
        tuanBranches: tuan.branches,
    };
}
exports.getTuanTrietPalaceIndices = getTuanTrietPalaceIndices;
function getVietnameseKuiYue(stemName) {
    var sIdx = stemToIndex(stemName);
    switch (sIdx) {
        case 0: // Giáp
        case 4: // Mậu
            return { kuiPalaceIndex: 11, yuePalaceIndex: 5, kuiBranch: 'Sửu', yueBranch: 'Mùi' };
        case 1: // Ất
        case 5: // Kỷ
            return { kuiPalaceIndex: 10, yuePalaceIndex: 6, kuiBranch: 'Tý', yueBranch: 'Thân' };
        case 2: // Bính
        case 3: // Đinh
            return { kuiPalaceIndex: 9, yuePalaceIndex: 7, kuiBranch: 'Hợi', yueBranch: 'Dậu' };
        case 6: // Canh
        case 7: // Tân
            return { kuiPalaceIndex: 4, yuePalaceIndex: 0, kuiBranch: 'Ngọ', yueBranch: 'Dần' };
        case 8: // Nhâm
        case 9: // Quý
        default:
            return { kuiPalaceIndex: 1, yuePalaceIndex: 3, kuiBranch: 'Mão', yueBranch: 'Tỵ' };
    }
}
exports.getVietnameseKuiYue = getVietnameseKuiYue;
function getVietnameseHuoLing(yearBranch, timeIndex, isDuongNamOrAmNuValue) {
    var bZiIdx = branchToZiIndex(yearBranch);
    var fixedTime = timeIndex === 12 ? 0 : (timeIndex % 12);
    // Hỏa Tinh:
    // Dần (2), Ngọ (6), Tuất (10): Khởi Sửu (palace 11)
    // Thân (8), Tý (0), Thìn (4): Khởi Dần (palace 0)
    // Tỵ (5), Dậu (9), Sửu (1): Khởi Mão (palace 1)
    // Hợi (11), Mão (3), Mùi (7): Khởi Dậu (palace 7)
    var huoStart = 11;
    if ([8, 0, 4].includes(bZiIdx))
        huoStart = 0;
    else if ([5, 9, 1].includes(bZiIdx))
        huoStart = 1;
    else if ([11, 3, 7].includes(bZiIdx))
        huoStart = 7;
    // Hỏa Tinh luôn đếm thuận
    var huoPalaceIndex = (huoStart + fixedTime) % 12;
    // Linh Tinh:
    // Dần Ngọ Tuất khởi Mão (palace 1); 3 nhóm còn lại khởi Tuất (palace 8)
    var lingStart = [2, 6, 10].includes(bZiIdx) ? 1 : 8;
    // Dương Nam/Âm Nữ: đếm thuận; Âm Nam/Dương Nữ: đếm nghịch
    var lingPalaceIndex;
    if (isDuongNamOrAmNuValue) {
        lingPalaceIndex = (lingStart + fixedTime) % 12;
    }
    else {
        lingPalaceIndex = (lingStart - fixedTime + 12) % 12;
    }
    return {
        huoPalaceIndex: huoPalaceIndex,
        lingPalaceIndex: lingPalaceIndex,
    };
}
exports.getVietnameseHuoLing = getVietnameseHuoLing;
// ============================================================================
// 4. VÒNG THÁI TUẾ & VÒNG BÁC SĨ (VIỆT NAM)
// ============================================================================
exports.VIETNAMESE_SUIQIAN_STARS = [
    'Thái Tuế', 'Thiếu Dương', 'Tang Môn', 'Thiếu Âm',
    'Quan Phù', 'Tử Phù', 'Tuế Phá', 'Long Đức',
    'Bạch Hổ', 'Phúc Đức', 'Điếu Khách', 'Trực Phù'
];
exports.VIETNAMESE_BOSHI_STARS = [
    'Bác Sĩ', 'Lực Sỹ', 'Thanh Long', 'Tiểu Hao',
    'Tướng Quân', 'Tấu Thư', 'Phi Liêm', 'Hỷ Thần',
    'Bệnh Phù', 'Đại Hao', 'Phục Binh', 'Quan Phủ'
];
/**
 * Tính Vòng Thái Tuế Việt Nam cho 12 cung (khởi từ Chi năm sinh, luôn đi thuận)
 */
function getVietnameseSuiQian12(yearBranch) {
    var startPalace = branchToPalaceIndex(yearBranch);
    var result = new Array(12);
    for (var i = 0; i < 12; i++) {
        var palaceIdx = (startPalace + i) % 12;
        result[palaceIdx] = exports.VIETNAMESE_SUIQIAN_STARS[i];
    }
    return result;
}
exports.getVietnameseSuiQian12 = getVietnameseSuiQian12;
/**
 * Tính Vòng Bác Sĩ Việt Nam (khởi từ Lộc Tồn, phân chiều theo Âm Dương Nam Nữ)
 */
function getVietnameseBoShi12(luPalaceIndex, isDuongNamOrAmNuValue) {
    var result = new Array(12);
    for (var i = 0; i < 12; i++) {
        var palaceIdx = isDuongNamOrAmNuValue
            ? (luPalaceIndex + i) % 12
            : (luPalaceIndex - i + 12) % 12;
        result[palaceIdx] = exports.VIETNAMESE_BOSHI_STARS[i];
    }
    return result;
}
exports.getVietnameseBoShi12 = getVietnameseBoShi12;
// ============================================================================
// 5. VÒNG TRÀNG SINH (12 SAO THEO NGŨ HÀNH CỤC VÀ ÂM DƯƠNG NAM NỮ)
// ============================================================================
exports.VIETNAMESE_CHANGSHENG_STARS = [
    'Trường Sinh', 'Mộc Dục', 'Quan Đới', 'Lâm Quan',
    'Đế Vượng', 'Suy', 'Bệnh', 'Tử',
    'Mộ', 'Tuyệt', 'Thai', 'Dưỡng'
];
function getVietnameseChangSheng12(cucNameOrNumber, isDuongNamOrAmNuValue) {
    var cucNum = typeof cucNameOrNumber === 'number' ? cucNameOrNumber : 2;
    if (typeof cucNameOrNumber === 'string') {
        if (cucNameOrNumber.includes('Nhị') || cucNameOrNumber.includes('2') || cucNameOrNumber.includes('Thủy'))
            cucNum = 2;
        else if (cucNameOrNumber.includes('Tam') || cucNameOrNumber.includes('3') || cucNameOrNumber.includes('Mộc'))
            cucNum = 3;
        else if (cucNameOrNumber.includes('Tứ') || cucNameOrNumber.includes('4') || cucNameOrNumber.includes('Kim'))
            cucNum = 4;
        else if (cucNameOrNumber.includes('Ngũ') || cucNameOrNumber.includes('5') || cucNameOrNumber.includes('Thổ'))
            cucNum = 5;
        else if (cucNameOrNumber.includes('Lục') || cucNameOrNumber.includes('6') || cucNameOrNumber.includes('Hỏa'))
            cucNum = 6;
    }
    // Khởi Sinh theo Cục:
    // Thủy Nhị Cục (2): Thân (palace 6)
    // Mộc Tam Cục (3): Hợi (palace 9)
    // Kim Tứ Cục (4): Tỵ (palace 3)
    // Thổ Ngũ Cục (5): Thân (palace 6)
    // Hỏa Lục Cục (6): Dần (palace 0)
    var startPalace = 6;
    switch (cucNum) {
        case 2:
            startPalace = 6;
            break;
        case 3:
            startPalace = 9;
            break;
        case 4:
            startPalace = 3;
            break;
        case 5:
            startPalace = 6;
            break;
        case 6:
            startPalace = 0;
            break;
    }
    var result = new Array(12);
    for (var i = 0; i < 12; i++) {
        var palaceIdx = isDuongNamOrAmNuValue
            ? (startPalace + i) % 12
            : (startPalace - i + 12) % 12;
        result[palaceIdx] = exports.VIETNAMESE_CHANGSHENG_STARS[i];
    }
    return result;
}
exports.getVietnameseChangSheng12 = getVietnameseChangSheng12;
function getVietnameseSoulAndBody(menhPalaceBranch, yearBranch, options) {
    var menhBranchClean = menhPalaceBranch.trim();
    var yearBranchClean = yearBranch.trim();
    // Chủ Mệnh tính theo Cung Mệnh đóng
    var SOUL_MAP = {
        'Tý': 'Tham Lang',
        'Sửu': (options === null || options === void 0 ? void 0 : options.chouSoulStar) === 'LocTon' ? 'Lộc Tồn' : 'Cự Môn',
        'Dần': 'Lộc Tồn',
        'Mão': 'Văn Khúc',
        'Thìn': 'Liêm Trinh',
        'Tỵ': 'Vũ Khúc',
        'Ngọ': 'Phá Quân',
        'Mùi': 'Vũ Khúc',
        'Thân': 'Liêm Trinh',
        'Dậu': 'Văn Khúc',
        'Tuất': 'Lộc Tồn',
        'Hợi': 'Cự Môn'
    };
    var soul = 'Tham Lang';
    for (var _i = 0, _a = Object.entries(SOUL_MAP); _i < _a.length; _i++) {
        var _b = _a[_i], b = _b[0], name_1 = _b[1];
        if (menhBranchClean.includes(b)) {
            soul = name_1;
            break;
        }
    }
    // Chủ Thân tính theo Chi năm sinh
    var BODY_MAP = {
        'Tý': 'Hỏa Tinh',
        'Ngọ': 'Hỏa Tinh',
        'Sửu': 'Thiên Tướng',
        'Mùi': 'Thiên Tướng',
        'Dần': 'Thiên Lương',
        'Thân': 'Thiên Lương',
        'Mão': 'Thiên Đồng',
        'Dậu': 'Thiên Đồng',
        'Thìn': 'Văn Xương',
        'Tuất': 'Văn Xương',
        'Tỵ': 'Thiên Cơ',
        'Hợi': 'Thiên Cơ'
    };
    var body = 'Hỏa Tinh';
    for (var _c = 0, _d = Object.entries(BODY_MAP); _c < _d.length; _c++) {
        var _e = _d[_c], b = _e[0], name_2 = _e[1];
        if (yearBranchClean.includes(b)) {
            body = name_2;
            break;
        }
    }
    return { soul: soul, body: body };
}
exports.getVietnameseSoulAndBody = getVietnameseSoulAndBody;
