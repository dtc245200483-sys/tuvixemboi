"use strict";
// ==============================================================================
// OVERLAY ENGINE — MODULE TÍNH VẬN HẠN ĐỘNG CHO TỬ VI ĐẨU SỐ (IZTRO)
// Hỗ trợ tính toán và ánh xạ các tầng vận hạn: Đại Hạn, Tiểu Hạn, Lưu Niên, Lưu Nguyệt, Lưu Nhật
// Tuân thủ 100% chuẩn API của thư viện iztro (SylarLong/iztro)
// ==============================================================================
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
exports.getOverlayData = exports.validateTargetDate = void 0;
/**
 * Kiểm tra tính hợp lệ của chuỗi ngày mục tiêu (targetDateStr)
 * Định dạng yêu cầu: "YYYY-M-D" hoặc "YYYY-MM-DD"
 * Xử lý chặt chẽ để ném ra thông báo lỗi rõ ràng, tránh để iztro ném lỗi không rõ ràng
 *
 * @param dateStr Chuỗi ngày cần kiểm tra
 * @throws Error nếu ngày không hợp lệ hoặc không tồn tại trên lịch
 */
function validateTargetDate(dateStr) {
    if (typeof dateStr !== 'string' || !dateStr.trim()) {
        throw new Error('Invalid targetDateStr: date string must be a non-empty string.');
    }
    var trimmed = dateStr.trim();
    // Regex kiểm tra định dạng YYYY-M-D hoặc YYYY/M/D
    var match = trimmed.match(/^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$/);
    if (!match) {
        throw new Error("Invalid targetDateStr: \"".concat(dateStr, "\". Expected format \"YYYY-M-D\" or \"YYYY-MM-DD\" (e.g. \"2026-6-15\")."));
    }
    var year = parseInt(match[1], 10);
    var month = parseInt(match[2], 10);
    var day = parseInt(match[3], 10);
    if (year < 1900 || year > 2100) {
        throw new Error("Invalid targetDateStr: year ".concat(year, " is outside supported range (1900-2100)."));
    }
    if (month < 1 || month > 12) {
        throw new Error("Invalid targetDateStr: month ".concat(month, " is invalid (must be between 1 and 12)."));
    }
    // Kiểm tra số ngày hợp lệ trong tháng (bao gồm cả năm nhuận dương lịch)
    var daysInMonth = new Date(year, month, 0).getDate();
    if (day < 1 || day > daysInMonth) {
        throw new Error("Invalid targetDateStr: day ".concat(day, " is invalid for year ").concat(year, ", month ").concat(month, " (month has ").concat(daysInMonth, " days)."));
    }
}
exports.validateTargetDate = validateTargetDate;
/**
 * Tính toán và trích xuất dữ liệu vận hạn động cho lá số Tử Vi tại một mốc thời gian mục tiêu
 *
 * @param astrolabe Đối tượng lá số được tạo từ astro.bySolar(...) hoặc astro.byLunar(...)
 * @param targetDateStr Chuỗi ngày mục tiêu dạng "YYYY-M-D" (ví dụ: "2026-6-15")
 * @returns OverlayResult chứa Tứ Hóa các tầng và 12 ô cung với nhãn cung động và danh sách sao lưu
 */
function getOverlayData(astrolabe, targetDateStr) {
    var _a, _b, _c, _d, _e, _f, _g, _h, _j, _k, _l, _m, _o, _p, _q, _r, _s, _t, _u, _v, _w, _x, _y;
    // 1. Kiểm tra tính hợp lệ của đối tượng lá số đầu vào
    if (!astrolabe || typeof astrolabe !== 'object') {
        throw new Error('Invalid astrolabe: must be a valid Astrolabe instance.');
    }
    if (!Array.isArray(astrolabe.palaces) || astrolabe.palaces.length !== 12) {
        throw new Error("Invalid astrolabe: expected astrolabe.palaces to contain exactly 12 palaces, got ".concat(astrolabe.palaces ? astrolabe.palaces.length : 'undefined', "."));
    }
    var functionalAstrolabe = astrolabe;
    if (typeof functionalAstrolabe.horoscope !== 'function') {
        throw new Error('Invalid astrolabe: missing horoscope() method. Ensure the astrolabe instance was created by astro.bySolar() or astro.byLunar().');
    }
    // 2. Kiểm tra tính hợp lệ của ngày mục tiêu
    validateTargetDate(targetDateStr);
    // 3. Gọi hàm horoscope() từ iztro, có bọc try-catch để bắt các lỗi tiềm ẩn từ thư viện lõi
    var horoscope;
    try {
        horoscope = functionalAstrolabe.horoscope(targetDateStr.trim());
    }
    catch (err) {
        throw new Error("Failed to calculate horoscope for target date \"".concat(targetDateStr, "\": ").concat(err instanceof Error ? err.message : String(err)));
    }
    if (!horoscope || typeof horoscope !== 'object') {
        throw new Error("Failed to calculate horoscope: empty result returned for date \"".concat(targetDateStr, "\"."));
    }
    // 4. Ánh xạ 12 ô cung
    // QUY TẮC ÁNH XẠ CỦA IZTRO:
    // - astrolabe.palaces[i]: Cung gốc thứ i (cố định trên địa bàn, index từ 0 đến 11).
    // - horoscope[tầng].palaceNames[i]: Tên cung chức năng mà tầng vận hạn đó "an" vào cung gốc thứ i.
    //   Ví dụ: Nếu decadal.palaceNames[0] là 'Thiên Di', tức là tại cung gốc thứ 0 (palaces[0]),
    //   Đại Hạn an cung Thiên Di tại đây -> label: "ĐV.Thiên Di".
    // - horoscope[tầng].stars[i]: Mảng các sao lưu của tầng đó tại cung gốc thứ i.
    //   ĐẶC BIỆT LƯU Ý: stars[i] là mảng song song 1-1 với astrolabe.palaces[i] (cùng index i),
    //   KHÔNG map theo tên cung palaceNames!
    // - Nếu stars[i] rỗng hoặc không có sao nào thì trả về mảng rỗng `[]`, không throw lỗi.
    // - Giữ nguyên tên sao nguyên bản (ví dụ "Lưu Lộc", "Lưu Mã", "Văn Xương(M)", "Đà La(d)").
    var cells = [];
    for (var i = 0; i < 12; i++) {
        var palace = astrolabe.palaces[i];
        // Cung gốc
        var namePalaceGoc = palace.name;
        var branchGoc = palace.earthlyBranch;
        // Tầng Đại Hạn (Decadal)
        var decadalPalaceName = (_c = (_b = (_a = horoscope.decadal) === null || _a === void 0 ? void 0 : _a.palaceNames) === null || _b === void 0 ? void 0 : _b[i]) !== null && _c !== void 0 ? _c : '';
        var daiHan = {
            label: "\u0110V.".concat(decadalPalaceName),
        };
        // Tầng Tiểu Hạn (Age) - age (Tiểu Hạn) không có trường stars
        var agePalaceName = (_f = (_e = (_d = horoscope.age) === null || _d === void 0 ? void 0 : _d.palaceNames) === null || _e === void 0 ? void 0 : _e[i]) !== null && _f !== void 0 ? _f : '';
        var tieuHan = {
            label: "TH.".concat(agePalaceName),
        };
        // Tầng Lưu Niên (Yearly)
        var yearlyPalaceName = (_j = (_h = (_g = horoscope.yearly) === null || _g === void 0 ? void 0 : _g.palaceNames) === null || _h === void 0 ? void 0 : _h[i]) !== null && _j !== void 0 ? _j : '';
        var yearlyStarsRaw = (_l = (_k = horoscope.yearly) === null || _k === void 0 ? void 0 : _k.stars) === null || _l === void 0 ? void 0 : _l[i];
        var luuNien = {
            label: "LN.".concat(yearlyPalaceName),
            stars: Array.isArray(yearlyStarsRaw) ? yearlyStarsRaw.map(function (s) { return s.name; }) : [],
        };
        // Tầng Lưu Nguyệt (Monthly)
        var monthlyPalaceName = (_p = (_o = (_m = horoscope.monthly) === null || _m === void 0 ? void 0 : _m.palaceNames) === null || _o === void 0 ? void 0 : _o[i]) !== null && _p !== void 0 ? _p : '';
        var monthlyStarsRaw = (_r = (_q = horoscope.monthly) === null || _q === void 0 ? void 0 : _q.stars) === null || _r === void 0 ? void 0 : _r[i];
        var luuNguyet = {
            label: "Th.".concat(monthlyPalaceName),
            stars: Array.isArray(monthlyStarsRaw) ? monthlyStarsRaw.map(function (s) { return s.name; }) : [],
        };
        // Tầng Lưu Nhật (Daily)
        var dailyPalaceName = (_u = (_t = (_s = horoscope.daily) === null || _s === void 0 ? void 0 : _s.palaceNames) === null || _t === void 0 ? void 0 : _t[i]) !== null && _u !== void 0 ? _u : '';
        var dailyStarsRaw = (_w = (_v = horoscope.daily) === null || _v === void 0 ? void 0 : _v.stars) === null || _w === void 0 ? void 0 : _w[i];
        var luuNhat = {
            label: "Ng.".concat(dailyPalaceName),
            stars: Array.isArray(dailyStarsRaw) ? dailyStarsRaw.map(function (s) { return s.name; }) : [],
        };
        cells.push({
            namePalaceGoc: namePalaceGoc,
            branchGoc: branchGoc,
            daiHan: daiHan,
            tieuHan: tieuHan,
            luuNien: luuNien,
            luuNguyet: luuNguyet,
            luuNhat: luuNhat,
        });
    }
    // 5. Tổng hợp kết quả trả về
    return {
        targetDate: targetDateStr.trim(),
        decadalMutagen: ((_x = horoscope.decadal) === null || _x === void 0 ? void 0 : _x.mutagen) ? __spreadArray([], horoscope.decadal.mutagen, true) : [],
        yearlyMutagen: ((_y = horoscope.yearly) === null || _y === void 0 ? void 0 : _y.mutagen) ? __spreadArray([], horoscope.yearly.mutagen, true) : [],
        yearly: horoscope.yearly ? { index: horoscope.yearly.index, name: horoscope.yearly.name } : undefined,
        decadal: horoscope.decadal ? { index: horoscope.decadal.index, name: horoscope.decadal.name } : undefined,
        monthly: horoscope.monthly ? { index: horoscope.monthly.index, name: horoscope.monthly.name } : undefined,
        cells: cells,
    };
}
exports.getOverlayData = getOverlayData;
