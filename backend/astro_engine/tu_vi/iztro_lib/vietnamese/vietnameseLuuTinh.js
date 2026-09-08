"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.calculateVietnameseYearlyLuuStars = exports.getThienMaPalaceIndex = exports.getLocTonPalaceIndex = exports.getCanChiOfYear = void 0;
var vietnameseRules_1 = require("./vietnameseRules");
var vietnameseMutagen_1 = require("./vietnameseMutagen");
/**
 * Tính Can Chi của năm dương lịch
 */
function getCanChiOfYear(year) {
    var stemIndex = (year - 4) % 10;
    var branchZiIndex = (year - 4) % 12;
    var stem = vietnameseRules_1.STEMS[(stemIndex + 10) % 10];
    var branch = vietnameseRules_1.BRANCHES_FROM_ZI[(branchZiIndex + 12) % 12];
    return { stem: stem, branch: branch, stemIndex: (stemIndex + 10) % 10, branchZiIndex: (branchZiIndex + 12) % 12 };
}
exports.getCanChiOfYear = getCanChiOfYear;
/**
 * Lấy vị trí cung của Lộc Tồn theo Thiên Can (Cung 0: Dần -> 11: Sửu)
 */
function getLocTonPalaceIndex(stemName) {
    var sIdx = (0, vietnameseRules_1.stemToIndex)(stemName);
    switch (sIdx) {
        case 0: return 0; // Giáp tại Dần (palace 0)
        case 1: return 1; // Ất tại Mão (palace 1)
        case 2: // Bính
        case 4: return 3; // Mậu tại Tỵ (palace 3)
        case 3: // Đinh
        case 5: return 4; // Kỷ tại Ngọ (palace 4)
        case 6: return 6; // Canh tại Thân (palace 6)
        case 7: return 7; // Tân tại Dậu (palace 7)
        case 8: return 9; // Nhâm tại Hợi (palace 9)
        case 9: return 10; // Quý tại Tý (palace 10)
        default: return 0;
    }
}
exports.getLocTonPalaceIndex = getLocTonPalaceIndex;
/**
 * Lấy vị trí cung của Thiên Mã theo Địa Chi (Cung 0: Dần -> 11: Sửu)
 */
function getThienMaPalaceIndex(branchName) {
    var bZi = (0, vietnameseRules_1.branchToZiIndex)(branchName);
    // Dần (2), Ngọ (6), Tuất (10) -> Thân (palace 6)
    if ([2, 6, 10].includes(bZi))
        return 6;
    // Thân (8), Tý (0), Thìn (4) -> Dần (palace 0)
    if ([8, 0, 4].includes(bZi))
        return 0;
    // Tỵ (5), Dậu (9), Sửu (1) -> Hợi (palace 9)
    if ([5, 9, 1].includes(bZi))
        return 9;
    // Hợi (11), Mão (3), Mùi (7) -> Tỵ (palace 3)
    return 3;
}
exports.getThienMaPalaceIndex = getThienMaPalaceIndex;
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
function calculateVietnameseYearlyLuuStars(targetYear, options) {
    var _a = getCanChiOfYear(targetYear), stem = _a.stem, branch = _a.branch, branchZiIndex = _a.branchZiIndex;
    // Khởi tạo 12 cung lưu
    var palaceLuuStars = {};
    for (var i = 0; i < 12; i++) {
        palaceLuuStars[i] = [];
    }
    // 1. L.Thái Tuế
    var thaiTuePalace = (0, vietnameseRules_1.branchToPalaceIndex)(branch);
    palaceLuuStars[thaiTuePalace].push('L.Thái Tuế');
    // 2. L.Tang Môn (cách L.Thái Tuế 2 cung đi thuận)
    var tangMonPalace = (thaiTuePalace + 2) % 12;
    palaceLuuStars[tangMonPalace].push('L.Tang Môn');
    // 3. L.Bạch Hổ (xung chiếu với L.Tang Môn)
    var bachHoPalace = (tangMonPalace + 6) % 12;
    palaceLuuStars[bachHoPalace].push('L.Bạch Hổ');
    // 4 & 5. L.Thiên Khốc & L.Thiên Hư: Khởi từ Ngọ (palace 4 / Zi 6)
    // Khốc đi nghịch đến Chi năm xem, Hư đi thuận đến Chi năm xem
    // Ngọ có ZiIndex = 6. Độ lệch bước = branchZiIndex
    // Khởi Ngọ là năm Tý (bước = 0). Đến năm Chi thì đếm bước = branchZiIndex.
    var ngoPalace = (0, vietnameseRules_1.branchToPalaceIndex)('Ngọ'); // 4
    var thienKhocPalace = (ngoPalace - branchZiIndex + 24) % 12;
    var thienHuPalace = (ngoPalace + branchZiIndex) % 12;
    palaceLuuStars[thienKhocPalace].push('L.Thiên Khốc');
    palaceLuuStars[thienHuPalace].push('L.Thiên Hư');
    // 6. L.Lộc Tồn
    var locTonPalace = getLocTonPalaceIndex(stem);
    palaceLuuStars[locTonPalace].push('L.Lộc Tồn');
    // 7. L.Kình Dương (trước Lộc Tồn 1 cung)
    var kinhDuongPalace = (locTonPalace + 1) % 12;
    palaceLuuStars[kinhDuongPalace].push('L.Kình Dương');
    // 8. L.Đà La (sau Lộc Tồn 1 cung)
    var daLaPalace = (locTonPalace - 1 + 12) % 12;
    palaceLuuStars[daLaPalace].push('L.Đà La');
    // 9. L.Thiên Mã
    var thienMaPalace = getThienMaPalaceIndex(branch);
    palaceLuuStars[thienMaPalace].push('L.Thiên Mã');
    // 10. Tứ Hóa Lưu Niên của năm xem
    var yearlyMutagen = (0, vietnameseMutagen_1.getVietnameseMutagensByStem)(stem, options);
    return {
        targetYear: targetYear,
        heavenlyStem: stem,
        earthlyBranch: branch,
        palaceLuuStars: palaceLuuStars,
        yearlyMutagen: yearlyMutagen,
    };
}
exports.calculateVietnameseYearlyLuuStars = calculateVietnameseYearlyLuuStars;
