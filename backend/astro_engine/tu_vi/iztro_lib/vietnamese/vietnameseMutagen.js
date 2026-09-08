"use strict";
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getVietnameseMutagenByStar = exports.getVietnameseMutagensByStem = exports.VIETNAMESE_MUTAGENS_KEYS = exports.VIETNAMESE_MUTAGENS_VI = void 0;
/**
 * Bảng Tứ Hóa Tử Vi Việt Nam (Nam Phái truyền thống)
 * Định dạng mỗi can là mảng 4 sao: [Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ]
 */
exports.VIETNAMESE_MUTAGENS_VI = {
    Giáp: ['Liêm Trinh', 'Phá Quân', 'Vũ Khúc', 'Thái Dương'],
    Ất: ['Thiên Cơ', 'Thiên Lương', 'Tử Vi', 'Thái Âm'],
    Bính: ['Thiên Đồng', 'Thiên Cơ', 'Văn Xương', 'Liêm Trinh'],
    Đinh: ['Thái Âm', 'Thiên Đồng', 'Thiên Cơ', 'Cự Môn'],
    Mậu: ['Tham Lang', 'Thái Âm', 'Hữu Bật', 'Thiên Cơ'],
    Kỷ: ['Vũ Khúc', 'Tham Lang', 'Thiên Lương', 'Văn Khúc'],
    Canh: ['Thái Dương', 'Vũ Khúc', 'Thiên Đồng', 'Thái Âm'],
    Tân: ['Cự Môn', 'Thái Dương', 'Văn Khúc', 'Văn Xương'],
    Nhâm: ['Thiên Lương', 'Tử Vi', 'Thiên Phủ', 'Vũ Khúc'],
    Quý: ['Phá Quân', 'Cự Môn', 'Thái Âm', 'Tham Lang'],
};
/**
 * Phiên bản Tứ Hóa dạng Key chuẩn của iztro (dùng cho map nội bộ)
 */
exports.VIETNAMESE_MUTAGENS_KEYS = {
    jiaHeavenly: ['lianzhenMaj', 'pojunMaj', 'wuquMaj', 'taiyangMaj'],
    yiHeavenly: ['tianjiMaj', 'tianliangMaj', 'ziweiMaj', 'taiyinMaj'],
    bingHeavenly: ['tiantongMaj', 'tianjiMaj', 'wenchangMin', 'lianzhenMaj'],
    dingHeavenly: ['taiyinMaj', 'tiantongMaj', 'tianjiMaj', 'jumenMaj'],
    wuHeavenly: ['tanlangMaj', 'taiyinMaj', 'youbiMin', 'tianjiMaj'],
    jiHeavenly: ['wuquMaj', 'tanlangMaj', 'tianliangMaj', 'wenquMin'],
    gengHeavenly: ['taiyangMaj', 'wuquMaj', 'tiantongMaj', 'taiyinMaj'],
    xinHeavenly: ['jumenMaj', 'taiyangMaj', 'wenquMin', 'wenchangMin'],
    renHeavenly: ['tianliangMaj', 'ziweiMaj', 'tianfuMaj', 'wuquMaj'],
    guiHeavenly: ['pojunMaj', 'jumenMaj', 'taiyinMaj', 'tanlangMaj'],
};
/**
 * Lấy danh sách 4 sao Hóa [Lộc, Quyền, Khoa, Kỵ] theo Thiên Can
 */
function getVietnameseMutagensByStem(stem, options) {
    // Chuẩn hóa tên can
    var cleanStem = stem.trim().replace(/^.+ - /, ''); // phòng trường hợp truyền vào chuỗi "Bính Tuất"
    var firstStem = cleanStem.split(' ')[0];
    // Xử lý tùy chọn cho can Canh
    if ((firstStem === 'Canh' || firstStem === '庚' || firstStem === 'gengHeavenly') && (options === null || options === void 0 ? void 0 : options.canhMutagenType) === 'khoi_viet') {
        return ['Thái Dương', 'Vũ Khúc', 'Thiên Khôi', 'Thái Âm'];
    }
    // Tiếng Việt
    for (var _i = 0, _a = Object.entries(exports.VIETNAMESE_MUTAGENS_VI); _i < _a.length; _i++) {
        var _b = _a[_i], key = _b[0], value = _b[1];
        if (firstStem.startsWith(key)) {
            return __spreadArray([], value, true);
        }
    }
    // Tiếng Trung (fallback)
    var CHINESE_STEM_MAP = {
        '甲': 'Giáp', '乙': 'Ất', '丙': 'Bính', '丁': 'Đinh', '戊': 'Mậu',
        '己': 'Kỷ', '庚': 'Canh', '辛': 'Tân', '壬': 'Nhâm', '癸': 'Quý'
    };
    var viStem = CHINESE_STEM_MAP[firstStem] || 'Giáp';
    return __spreadArray([], exports.VIETNAMESE_MUTAGENS_VI[viStem], true);
}
exports.getVietnameseMutagensByStem = getVietnameseMutagensByStem;
/**
 * Tra cứu xem một sao có Tứ Hóa theo Thiên Can đang xét hay không
 * @returns 'Lộc' | 'Quyền' | 'Khoa' | 'Kỵ' | ''
 */
function getVietnameseMutagenByStar(starName, heavenlyStem, options) {
    var _a = getVietnameseMutagensByStem(heavenlyStem, options), loc = _a[0], quyen = _a[1], khoa = _a[2], ky = _a[3];
    if (starName === loc || starName.includes(loc))
        return 'Lộc';
    if (starName === quyen || starName.includes(quyen))
        return 'Quyền';
    if (starName === khoa || starName.includes(khoa))
        return 'Khoa';
    if (starName === ky || starName.includes(ky))
        return 'Kỵ';
    return '';
}
exports.getVietnameseMutagenByStar = getVietnameseMutagenByStar;
