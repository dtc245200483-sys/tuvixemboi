"use strict";
// ==============================================================================
// OVERLAY TOOLBAR COMPONENT — BỘ ĐIỀU KHIỂN THỜI ĐIỂM XEM VẬN HẠN
// Quản lý trạng thái Năm, Tháng, tạo targetDateStr dạng "YYYY-M-15"
// Cung cấp Debounce ~150ms và logic cập nhật lớp phủ vận hạn
// ==============================================================================
Object.defineProperty(exports, "__esModule", { value: true });
exports.renderOverlayToolbarHtml = exports.updateHoroscopeOverlay = exports.createDebounce = exports.generateYearOptions = exports.buildTargetDateStr = void 0;
var overlayEngine_1 = require("../overlayEngine");
/**
 * Ghép Năm + Tháng thành targetDateStr chuẩn dạng "YYYY-M-15"
 * (Lấy ngày 15 làm đại diện giữa tháng để xem Lưu Niên / Lưu Nguyệt)
 */
function buildTargetDateStr(year, month, day) {
    if (day === void 0) { day = 15; }
    var y = Math.floor(year);
    var m = Math.floor(month);
    var d = Math.floor(day);
    return "".concat(y, "-").concat(m, "-").concat(d);
}
exports.buildTargetDateStr = buildTargetDateStr;
/**
 * Tạo danh sách năm từ năm sinh đến năm sinh + 100 tuổi
 */
function generateYearOptions(birthYear, maxAge) {
    if (maxAge === void 0) { maxAge = 100; }
    var years = [];
    var start = birthYear > 0 ? birthYear : new Date().getFullYear();
    var end = start + maxAge;
    for (var y = start; y <= end; y++) {
        years.push(y);
    }
    return years;
}
exports.generateYearOptions = generateYearOptions;
/**
 * Hàm Debounce chuẩn (~150ms) dùng để trì hoãn xử lý khi người dùng đổi nhanh liên tục
 */
function createDebounce(func, delayMs) {
    if (delayMs === void 0) { delayMs = 150; }
    var timerId = null;
    var debounced = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        if (timerId !== null) {
            clearTimeout(timerId);
        }
        timerId = setTimeout(function () {
            timerId = null;
            func.apply(void 0, args);
        }, delayMs);
    };
    debounced.cancel = function () {
        if (timerId !== null) {
            clearTimeout(timerId);
            timerId = null;
        }
    };
    return debounced;
}
exports.createDebounce = createDebounce;
/**
 * Tính toán lại lớp phủ vận hạn động từ lá số có sẵn mà KHÔNG tính lại Bản Mệnh
 *
 * @param astrolabe Lá số hiện tại (không gọi lại astro.bySolar)
 * @param year Năm cần xem
 * @param month Tháng cần xem (1 - 12)
 * @returns OverlayResult mới tương ứng với thời điểm đã chọn
 */
function updateHoroscopeOverlay(astrolabe, year, month) {
    var targetDateStr = buildTargetDateStr(year, month, 15);
    return (0, overlayEngine_1.getOverlayData)(astrolabe, targetDateStr);
}
exports.updateHoroscopeOverlay = updateHoroscopeOverlay;
/**
 * Render cấu trúc HTML cho thanh công cụ thời điểm (Toolbar UI)
 */
function renderOverlayToolbarHtml(state) {
    var selectedYear = state.selectedYear, selectedMonth = state.selectedMonth, birthYear = state.birthYear, isOverlayActive = state.isOverlayActive, _a = state.yearlyMutagensText, yearlyMutagensText = _a === void 0 ? '--' : _a;
    var yearOptions = generateYearOptions(birthYear);
    var yearOptionsHtml = yearOptions
        .map(function (y) { return "<option value=\"".concat(y, "\" ").concat(y === selectedYear ? 'selected' : '', ">N\u0103m ").concat(y, "</option>"); })
        .join('');
    var monthOptionsHtml = Array.from({ length: 12 }, function (_, i) { return i + 1; })
        .map(function (m) { return "<option value=\"".concat(m, "\" ").concat(m === selectedMonth ? 'selected' : '', ">Th\u00E1ng ").concat(m, "</option>"); })
        .join('');
    return "\n    <div class=\"overlay-toolbar\" id=\"overlayToolbar\">\n      <div class=\"overlay-toolbar-left\">\n        <!-- Ch\u1EBF \u0111\u1ED9 hi\u1EC3n th\u1ECB B\u1EA3n M\u1EC7nh / L\u01B0u Ni\u00EAn -->\n        <div class=\"overlay-control-item\">\n          <span class=\"overlay-control-label\">Ch\u1EBF \u0111\u1ED9:</span>\n          <div class=\"overlay-switch-group\">\n            <button type=\"button\" id=\"btnModeBanMenh\" class=\"overlay-switch-btn ".concat(!isOverlayActive ? 'active' : '', "\" onclick=\"setOverlayMode(false)\">B\u1EA3n M\u1EC7nh</button>\n            <button type=\"button\" id=\"btnModeLuuNien\" class=\"overlay-switch-btn ").concat(isOverlayActive ? 'active' : '', "\" onclick=\"setOverlayMode(true)\">L\u01B0u Ni\u00EAn <span id=\"lblLuuYear\">").concat(selectedYear, "</span></button>\n          </div>\n        </div>\n\n        <!-- B\u1ED9 ch\u1ECDn N\u0103m & Th\u00E1ng V\u1EADn H\u1EA1n -->\n        <div class=\"overlay-time-picker overlay-element\" id=\"overlayTimePicker\">\n          <div class=\"overlay-control-item\">\n            <label for=\"selOverlayYear\" class=\"overlay-control-label\">N\u0103m:</label>\n            <select id=\"selOverlayYear\" class=\"overlay-select\" onchange=\"onOverlayTimeChange()\">\n              ").concat(yearOptionsHtml, "\n            </select>\n          </div>\n\n          <div class=\"overlay-control-item\">\n            <label for=\"selOverlayMonth\" class=\"overlay-control-label\">Th\u00E1ng:</label>\n            <select id=\"selOverlayMonth\" class=\"overlay-select\" onchange=\"onOverlayTimeChange()\">\n              ").concat(monthOptionsHtml, "\n            </select>\n          </div>\n        </div>\n      </div>\n\n      <!-- T\u1EE9 H\u00F3a L\u01B0u Ni\u00EAn & Loading Status -->\n      <div class=\"overlay-toolbar-right\">\n        <div id=\"overlayLoadingBadge\" class=\"overlay-loading-badge\" style=\"display: none;\">\n          <span class=\"spinner-dot\"></span> \u0110ang chuy\u1EC3n v\u1EADn...\n        </div>\n        <div id=\"overlayMutagenSummary\" class=\"overlay-element\" style=\"font-size: 11px; font-weight: 600; color: #B45309; display: ").concat(isOverlayActive ? 'flex' : 'none', "; align-items: center; gap: 6px;\">\n          <span style=\"color: #6B2B1F; font-weight: 700;\">T\u1EE9 H\u00F3a L\u01B0u Ni\u00EAn:</span>\n          <span id=\"txtYearlyMutagens\" style=\"background: #FEF3C7; padding: 2px 8px; border-radius: 12px; border: 1px solid #F59E0B;\">").concat(yearlyMutagensText, "</span>\n        </div>\n      </div>\n    </div>\n  ");
}
exports.renderOverlayToolbarHtml = renderOverlayToolbarHtml;
