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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.astroVietnam = exports.vietnamesePlugin = exports.applyVietnameseRules = void 0;
var index_1 = require("../index");
var FunctionalStar_1 = __importDefault(require("../star/FunctionalStar"));
var vietnameseRules_1 = require("./vietnameseRules");
var vietnameseMutagen_1 = require("./vietnameseMutagen");
var vietnameseLuuTinh_1 = require("./vietnameseLuuTinh");
/**
 * Xóa một ngôi sao khỏi danh sách theo tên
 */
function removeStarFromList(stars, starNamesToRemove) {
    var _loop_1 = function (i) {
        var sName = stars[i].name;
        if (starNamesToRemove.some(function (target) { return sName === target || sName.includes(target); })) {
            stars.splice(i, 1);
        }
    };
    for (var i = stars.length - 1; i >= 0; i--) {
        _loop_1(i);
    }
}
/**
 * Tìm chỉ số cung chứa một ngôi sao theo tên
 */
function findStarPalaceIndex(astrolabe, starName) {
    for (var i = 0; i < astrolabe.palaces.length; i++) {
        var p = astrolabe.palaces[i];
        var all = __spreadArray(__spreadArray(__spreadArray([], p.majorStars, true), p.minorStars, true), p.adjectiveStars, true);
        if (all.some(function (s) { return s.name === starName || s.name.includes(starName); })) {
            return i;
        }
    }
    return -1;
}
/**
 * HÀM CỐT LÕI: Ghi đè (override/adapter) các quy tắc Tử Vi Việt Nam lên đối tượng Astrolabe của iztro
 */
function applyVietnameseRules(astrolabe, options) {
    var _a;
    if (options === void 0) { options = {}; }
    if (!astrolabe || !astrolabe.palaces || astrolabe.palaces.length < 12) {
        return astrolabe;
    }
    // 1. TRÍCH XUẤT THÔNG TIN CĂN BẢN TỪ LÁ SỐ
    // Bóc tách Can Chi năm và Giờ từ chineseDate: "Bính Tuất - Giáp Ngọ - Mậu Ngọ - Đinh Tỵ"
    var cDateParts = (astrolabe.chineseDate || '').split(' - ');
    var yearPillar = cDateParts[0] || 'Giáp Tý';
    var hourPillar = cDateParts[3] || cDateParts[cDateParts.length - 1] || 'Tý';
    var yearParts = yearPillar.trim().split(' ');
    var yearStem = yearParts[0] || 'Giáp';
    var yearBranch = yearParts[1] || 'Tý';
    var hourParts = hourPillar.trim().split(' ');
    var hourBranch = hourParts[hourParts.length - 1] || 'Tý';
    var timeIndex = (0, vietnameseRules_1.branchToZiIndex)(hourBranch); // 0: Tý .. 11: Hợi
    var isDuongNamOrAmNuValue = (0, vietnameseRules_1.isDuongNamOrAmNu)(yearStem, astrolabe.gender);
    // ==========================================================================
    // QUY TẮC 1: TUẦN KHÔNG & TRIỆT LỘ (CHIẾM CẶP 2 CUNG LIÊN TIẾP)
    // ==========================================================================
    if (options.cleanOldXunKongJieKong !== false) {
        // Xóa sao Tuần/Triệt cũ nếu có
        var OLD_STARS_1 = ['Tuần Không', 'Triệt Lộ', 'Không Vong', '截空', '旬空', '截路', '空亡'];
        astrolabe.palaces.forEach(function (p) {
            removeStarFromList(p.minorStars, OLD_STARS_1);
            removeStarFromList(p.adjectiveStars, OLD_STARS_1);
        });
    }
    var _b = (0, vietnameseRules_1.getTuanTrietPalaceIndices)(yearStem, yearBranch), trietPalaceIndices = _b.trietPalaceIndices, tuanPalaceIndices = _b.tuanPalaceIndices;
    // Gắn Triệt vào cả 2 cung
    trietPalaceIndices.forEach(function (pIdx) {
        var palace = astrolabe.palaces[pIdx];
        if (palace && !palace.adjectiveStars.some(function (s) { return s.name === 'Triệt Lộ' || s.name === 'Triệt'; })) {
            var star = new FunctionalStar_1.default({
                name: 'Triệt Lộ',
                type: 'adjective',
                scope: 'origin',
            });
            star.setPalace(palace);
            star.setAstrolabe(astrolabe);
            palace.adjectiveStars.push(star);
        }
    });
    // Gắn Tuần vào cả 2 cung
    tuanPalaceIndices.forEach(function (pIdx) {
        var palace = astrolabe.palaces[pIdx];
        if (palace && !palace.adjectiveStars.some(function (s) { return s.name === 'Tuần Không' || s.name === 'Tuần'; })) {
            var star = new FunctionalStar_1.default({
                name: 'Tuần Không',
                type: 'adjective',
                scope: 'origin',
            });
            star.setPalace(palace);
            star.setAstrolabe(astrolabe);
            palace.adjectiveStars.push(star);
        }
    });
    // ==========================================================================
    // QUY TẮC 2: CHUẨN HÓA THIÊN KHÔI - THIÊN VIỆT & TỨ HÓA THEO THIÊN CAN
    // ==========================================================================
    // A. Khôi - Việt
    var _c = (0, vietnameseRules_1.getVietnameseKuiYue)(yearStem), kuiPalaceIndex = _c.kuiPalaceIndex, yuePalaceIndex = _c.yuePalaceIndex;
    // Xóa Khôi Việt cũ
    astrolabe.palaces.forEach(function (p) {
        removeStarFromList(p.minorStars, ['Thiên Khôi', 'Thiên Việt', '天魁', '天钺']);
        removeStarFromList(p.adjectiveStars, ['Thiên Khôi', 'Thiên Việt', '天魁', '天钺']);
    });
    // Gắn Khôi Việt mới vào đúng cung
    var kuiPalace = astrolabe.palaces[kuiPalaceIndex];
    if (kuiPalace) {
        var star = new FunctionalStar_1.default({ name: 'Thiên Khôi', type: 'soft', scope: 'origin' });
        star.setPalace(kuiPalace);
        star.setAstrolabe(astrolabe);
        kuiPalace.minorStars.push(star);
    }
    var yuePalace = astrolabe.palaces[yuePalaceIndex];
    if (yuePalace) {
        var star = new FunctionalStar_1.default({ name: 'Thiên Việt', type: 'soft', scope: 'origin' });
        star.setPalace(yuePalace);
        star.setAstrolabe(astrolabe);
        yuePalace.minorStars.push(star);
    }
    // B. Tứ Hóa Nam Phái
    astrolabe.palaces.forEach(function (p) {
        // Cập nhật thuộc tính mutagen cho cả majorStars và minorStars
        p.majorStars.forEach(function (s) {
            var mut = (0, vietnameseMutagen_1.getVietnameseMutagenByStar)(s.name, yearStem, options);
            s.mutagen = mut ? "H\u00F3a ".concat(mut) : undefined;
        });
        p.minorStars.forEach(function (s) {
            var mut = (0, vietnameseMutagen_1.getVietnameseMutagenByStar)(s.name, yearStem, options);
            s.mutagen = mut ? "H\u00F3a ".concat(mut) : undefined;
        });
    });
    // ==========================================================================
    // QUY TẮC 3: HỎA TINH & LINH TINH (THEO GIỜ SINH & ÂM DƯƠNG NAM NỮ)
    // ==========================================================================
    var _d = (0, vietnameseRules_1.getVietnameseHuoLing)(yearBranch, timeIndex, isDuongNamOrAmNuValue), huoPalaceIndex = _d.huoPalaceIndex, lingPalaceIndex = _d.lingPalaceIndex;
    // Xóa Hỏa Tinh & Linh Tinh cũ
    astrolabe.palaces.forEach(function (p) {
        removeStarFromList(p.minorStars, ['Hỏa Tinh', 'Linh Tinh', '火星', '铃星']);
        removeStarFromList(p.adjectiveStars, ['Hỏa Tinh', 'Linh Tinh', '火星', '铃星']);
    });
    // Gắn Hỏa Tinh & Linh Tinh mới
    var huoPalace = astrolabe.palaces[huoPalaceIndex];
    if (huoPalace) {
        var star = new FunctionalStar_1.default({ name: 'Hỏa Tinh', type: 'tough', scope: 'origin' });
        star.setPalace(huoPalace);
        star.setAstrolabe(astrolabe);
        huoPalace.minorStars.push(star);
    }
    var lingPalace = astrolabe.palaces[lingPalaceIndex];
    if (lingPalace) {
        var star = new FunctionalStar_1.default({ name: 'Linh Tinh', type: 'tough', scope: 'origin' });
        star.setPalace(lingPalace);
        star.setAstrolabe(astrolabe);
        lingPalace.minorStars.push(star);
    }
    // ==========================================================================
    // QUY TẮC 4: VÒNG THÁI TUẾ & VÒNG BÁC SĨ (CHUẨN VIỆT NAM)
    // ==========================================================================
    // A. Vòng Thái Tuế
    var vietnameseSuiQian = (0, vietnameseRules_1.getVietnameseSuiQian12)(yearBranch);
    for (var i = 0; i < 12; i++) {
        astrolabe.palaces[i].suiqian12 = vietnameseSuiQian[i];
    }
    // B. Vòng Bác Sĩ (khởi từ Lộc Tồn)
    var locTonIdx = findStarPalaceIndex(astrolabe, 'Lộc Tồn');
    if (locTonIdx === -1) {
        // Nếu chưa tìm thấy thì tính vị trí Lộc Tồn theo Thiên Can
        var sIdx = (0, vietnameseRules_1.stemToIndex)(yearStem);
        var STEM_TO_LU = {
            0: 0, 1: 1, 2: 3, 3: 4, 4: 3, 5: 4, 6: 6, 7: 7, 8: 9, 9: 10
        };
        locTonIdx = (_a = STEM_TO_LU[sIdx]) !== null && _a !== void 0 ? _a : 0;
    }
    var vietnameseBoShi = (0, vietnameseRules_1.getVietnameseBoShi12)(locTonIdx, isDuongNamOrAmNuValue);
    for (var i = 0; i < 12; i++) {
        astrolabe.palaces[i].boshi12 = vietnameseBoShi[i];
    }
    // ==========================================================================
    // QUY TẮC 5: VÒNG TRÀNG SINH (12 SAO THEO CỤC VÀ ÂM DƯƠNG NAM NỮ)
    // ==========================================================================
    var vietnameseChangSheng = (0, vietnameseRules_1.getVietnameseChangSheng12)(astrolabe.fiveElementsClass, isDuongNamOrAmNuValue);
    for (var i = 0; i < 12; i++) {
        astrolabe.palaces[i].changsheng12 = vietnameseChangSheng[i];
    }
    // ==========================================================================
    // QUY TẮC 6: CHỦ MỆNH VÀ CHỦ THÂN THEO TỬ VI VIỆT
    // ==========================================================================
    // Tìm cung Mệnh
    var menhPalace = astrolabe.palaces.find(function (p) { return p.isOriginalPalace || p.name === 'Mệnh' || p.name === 'Mệnh Cung'; }) || astrolabe.palaces[0];
    var _e = (0, vietnameseRules_1.getVietnameseSoulAndBody)(menhPalace.earthlyBranch, yearBranch, options), soul = _e.soul, body = _e.body;
    astrolabe.soul = soul;
    astrolabe.body = body;
    return astrolabe;
}
exports.applyVietnameseRules = applyVietnameseRules;
/**
 * PLUGIN TỬ VI VIỆT NAM (dùng cho astrolabe.use(vietnamesePlugin) hoặc astro.loadPlugin)
 */
function vietnamesePlugin() {
    applyVietnameseRules(this);
}
exports.vietnamesePlugin = vietnamesePlugin;
/**
 * WRAPPER THƯ VIỆN: astroVietnam
 * Cung cấp API trực tiếp thay thế hoặc bổ trợ cho astro.bySolar / astro.byLunar
 */
exports.astroVietnam = {
    /**
     * Tính lá số theo Dương lịch chuẩn Tử Vi Việt Nam
     */
    bySolar: function (solarDateStr, timeIndex, gender, fixLeap, options) {
        if (fixLeap === void 0) { fixLeap = true; }
        if (options === void 0) { options = {}; }
        // 1. Dùng iztro an sao nền
        var baseAstrolabe = index_1.astro.bySolar(solarDateStr, timeIndex, gender, fixLeap, options.language || 'vi-VN');
        // 2. Ghi đè các quy tắc Tử Vi Việt Nam
        return applyVietnameseRules(baseAstrolabe, options);
    },
    /**
     * Tính lá số theo Âm lịch chuẩn Tử Vi Việt Nam
     */
    byLunar: function (lunarDateStr, timeIndex, gender, isLeapMonth, fixLeap, options) {
        if (isLeapMonth === void 0) { isLeapMonth = false; }
        if (fixLeap === void 0) { fixLeap = true; }
        if (options === void 0) { options = {}; }
        var baseAstrolabe = index_1.astro.byLunar(lunarDateStr, timeIndex, gender, isLeapMonth, fixLeap, options.language || 'vi-VN');
        return applyVietnameseRules(baseAstrolabe, options);
    },
    /**
     * Module Lưu Tinh: Tính toàn bộ sao lưu niên theo năm xem
     */
    getYearlyLuuTinh: function (targetYear, options) {
        if (options === void 0) { options = {}; }
        return (0, vietnameseLuuTinh_1.calculateVietnameseYearlyLuuStars)(targetYear, options);
    },
    /**
     * Hàm override áp dụng lên đối tượng Astrolabe có sẵn
     */
    applyRules: applyVietnameseRules,
};
