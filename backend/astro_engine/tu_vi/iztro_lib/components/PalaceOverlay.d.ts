import { OverlayCell } from '../overlayEngine';
/**
 * Thuộc tính của component PalaceOverlay
 */
export interface PalaceOverlayProps {
    /** Dữ liệu vận hạn động tại ô cung tương ứng (optional để tương thích ngược) */
    overlayCell?: OverlayCell;
    /** Trạng thái bật/tắt hiển thị lớp phủ (mặc định: true) */
    visible?: boolean;
    /** Chế độ hiển thị gộp trên màn hình nhỏ (mobile) */
    compact?: boolean;
}
/**
 * Kết quả render của PalaceOverlay dạng chuỗi HTML và đối tượng cấu trúc
 */
export interface PalaceOverlayRenderResult {
    /** HTML 3 badge hiển thị riêng lẻ (cho màn hình desktop/tablet) */
    badgesHtml: string;
    /** HTML 3 badge gộp 1 dòng ngắn gọn (cho màn hình mobile) */
    compactBadgesHtml: string;
    /** HTML khu vực danh sách sao Lưu Niên */
    starsHtml: string;
    /** Nhãn gộp dạng văn bản thuần (vd: "ĐV.Điền · LN.Quan · Th.5") */
    compactText: string;
    /** Toàn bộ khối HTML overlay để chèn vào thân ô cung */
    fullOverlayHtml: string;
}
/**
 * Tạo nhãn gộp dạng văn bản thuần từ 3 tầng vận hạn (cho mobile hoặc tooltip)
 */
export declare function getCompactOverlayLabel(cell?: OverlayCell): string;
/**
 * Render chuỗi HTML cho 3 badge vận hạn:
 * 1. cell.daiHan.label: badge nền xám nhạt, chữ nhỏ
 * 2. cell.luuNien.label: badge nền cam nhạt, chữ nhỏ, đậm hơn
 * 3. cell.luuNguyet.label: badge nền xanh nhạt, chữ nhỏ nhất
 */
export declare function renderOverlayBadges(cell?: OverlayCell, compact?: boolean): string;
/**
 * Render chuỗi HTML cho danh sách sao Lưu Niên trong ô cung:
 * - Ngăn cách bằng đường viền đứt / khoảng cách rõ ràng với phần sao Bản Mệnh
 * - Giữ nguyên tên sao gốc từ iztro có tiền tố thật (vd: "Lưu Lộc", "Lưu Mã", "Lưu Khôi"...)
 * - Style chữ nghiêng, màu sắc khác hẳn sao Bản Mệnh để dễ phân biệt
 */
export declare function renderLuuNienStars(cell?: OverlayCell): string;
/**
 * Component PalaceOverlay: Tạo toàn bộ cấu trúc giao diện vận hạn động cho 1 ô cung
 *
 * @param props Thuộc tính truyền vào (chứa overlayCell tùy chọn và cờ visible)
 * @returns Đối tượng chứa các đoạn HTML tương ứng cho từng vị trí trong ô cung
 */
export declare function renderPalaceOverlay(props: PalaceOverlayProps): PalaceOverlayRenderResult;
