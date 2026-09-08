"use strict";
// ==============================================================================
// PALACE OVERLAY COMPONENT — HIỂN THỊ LỚP VẬN HẠN ĐỘNG TRÊN Ô CUNG TỬ VI
// Hỗ trợ hiển thị 3 badge vận hạn (Đại Hạn, Lưu Niên, Lưu Nguyệt) và khu vực sao Lưu Niên
// Tương thích ngược 100%: overlayCell là prop tùy chọn (optional)
// ==============================================================================
Object.defineProperty(exports, "__esModule", { value: true });
exports.renderPalaceOverlay = exports.renderLuuNienStars = exports.renderOverlayBadges = exports.getCompactOverlayLabel = void 0;
/**
 * Tạo nhãn gộp dạng văn bản thuần từ 3 tầng vận hạn (cho mobile hoặc tooltip)
 */
function getCompactOverlayLabel(cell) {
    var _a, _b, _c;
    if (!cell)
        return '';
    var parts = [];
    if ((_a = cell.daiHan) === null || _a === void 0 ? void 0 : _a.label)
        parts.push(cell.daiHan.label);
    if ((_b = cell.luuNien) === null || _b === void 0 ? void 0 : _b.label)
        parts.push(cell.luuNien.label);
    if ((_c = cell.luuNguyet) === null || _c === void 0 ? void 0 : _c.label)
        parts.push(cell.luuNguyet.label);
    return parts.join(' · ');
}
exports.getCompactOverlayLabel = getCompactOverlayLabel;
/**
 * Render chuỗi HTML cho 3 badge vận hạn:
 * 1. cell.daiHan.label: badge nền xám nhạt, chữ nhỏ
 * 2. cell.luuNien.label: badge nền cam nhạt, chữ nhỏ, đậm hơn
 * 3. cell.luuNguyet.label: badge nền xanh nhạt, chữ nhỏ nhất
 */
function renderOverlayBadges(cell, compact) {
    var _a, _b, _c;
    if (compact === void 0) { compact = false; }
    if (!cell)
        return '';
    if (compact) {
        var compactText = getCompactOverlayLabel(cell);
        if (!compactText)
            return '';
        return "<span class=\"overlay-badge-compact\" title=\"V\u1EADn h\u1EA1n: ".concat(compactText, "\">").concat(compactText, "</span>");
    }
    var badges = [];
    // 1. Đại Hạn: badge xám nhạt
    if ((_a = cell.daiHan) === null || _a === void 0 ? void 0 : _a.label) {
        badges.push("<span class=\"overlay-badge badge-dai-han\" title=\"\u0110\u1EA1i H\u1EA1n\">".concat(cell.daiHan.label, "</span>"));
    }
    // 2. Lưu Niên: badge cam nhạt, đậm hơn
    if ((_b = cell.luuNien) === null || _b === void 0 ? void 0 : _b.label) {
        badges.push("<span class=\"overlay-badge badge-luu-nien\" title=\"L\u01B0u Ni\u00EAn\">".concat(cell.luuNien.label, "</span>"));
    }
    // 3. Lưu Nguyệt: badge xanh nhạt, chữ nhỏ nhất
    if ((_c = cell.luuNguyet) === null || _c === void 0 ? void 0 : _c.label) {
        badges.push("<span class=\"overlay-badge badge-luu-nguyet\" title=\"L\u01B0u Nguy\u1EC7t\">".concat(cell.luuNguyet.label, "</span>"));
    }
    return badges.join('');
}
exports.renderOverlayBadges = renderOverlayBadges;
/**
 * Render chuỗi HTML cho danh sách sao Lưu Niên trong ô cung:
 * - Ngăn cách bằng đường viền đứt / khoảng cách rõ ràng với phần sao Bản Mệnh
 * - Giữ nguyên tên sao gốc từ iztro có tiền tố thật (vd: "Lưu Lộc", "Lưu Mã", "Lưu Khôi"...)
 * - Style chữ nghiêng, màu sắc khác hẳn sao Bản Mệnh để dễ phân biệt
 */
function renderLuuNienStars(cell) {
    if (!cell || !cell.luuNien || !Array.isArray(cell.luuNien.stars) || cell.luuNien.stars.length === 0) {
        return '';
    }
    var starItems = cell.luuNien.stars
        .map(function (starName) { return "<span class=\"overlay-luu-star-tag\" title=\"Sao L\u01B0u Ni\u00EAn\">".concat(starName, "</span>"); })
        .join('');
    return "\n    <!-- [START OVERLAY: Khu V\u1EF1c Sao L\u01B0u Ni\u00EAn] -->\n    <div class=\"overlay-luu-stars-container\">\n      <div class=\"overlay-luu-stars-header\">\n        <span class=\"overlay-luu-stars-title\">\u2605 L\u01B0u Ni\u00EAn</span>\n      </div>\n      <div class=\"overlay-luu-stars-list\">\n        ".concat(starItems, "\n      </div>\n    </div>\n    <!-- [END OVERLAY: Khu V\u1EF1c Sao L\u01B0u Ni\u00EAn] -->\n  ");
}
exports.renderLuuNienStars = renderLuuNienStars;
/**
 * Component PalaceOverlay: Tạo toàn bộ cấu trúc giao diện vận hạn động cho 1 ô cung
 *
 * @param props Thuộc tính truyền vào (chứa overlayCell tùy chọn và cờ visible)
 * @returns Đối tượng chứa các đoạn HTML tương ứng cho từng vị trí trong ô cung
 */
function renderPalaceOverlay(props) {
    var overlayCell = props.overlayCell, _a = props.visible, visible = _a === void 0 ? true : _a, _b = props.compact, compact = _b === void 0 ? false : _b;
    // Nếu không có dữ liệu hoặc cờ visible = false, trả về rỗng (tương thích ngược hoàn hảo)
    if (!overlayCell || !visible) {
        return {
            badgesHtml: '',
            compactBadgesHtml: '',
            starsHtml: '',
            compactText: '',
            fullOverlayHtml: '',
        };
    }
    var badgesHtml = renderOverlayBadges(overlayCell, false);
    var compactBadgesHtml = renderOverlayBadges(overlayCell, true);
    var compactText = getCompactOverlayLabel(overlayCell);
    var starsHtml = renderLuuNienStars(overlayCell);
    var fullOverlayHtml = "\n    <!-- [START OVERLAY: PalaceOverlay Component] -->\n    <div class=\"palace-overlay-wrapper\">\n      <div class=\"overlay-badges-row desktop-only\">\n        ".concat(badgesHtml, "\n      </div>\n      <div class=\"overlay-badges-row mobile-only\">\n        ").concat(compactBadgesHtml, "\n      </div>\n      ").concat(starsHtml, "\n    </div>\n    <!-- [END OVERLAY: PalaceOverlay Component] -->\n  ");
    return {
        badgesHtml: badgesHtml,
        compactBadgesHtml: compactBadgesHtml,
        starsHtml: starsHtml,
        compactText: compactText,
        fullOverlayHtml: fullOverlayHtml,
    };
}
exports.renderPalaceOverlay = renderPalaceOverlay;
