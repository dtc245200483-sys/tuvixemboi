import { IFunctionalAstrolabe } from '../astro/FunctionalAstrolabe';
import { OverlayResult } from '../overlayEngine';
/**
 * Thuộc tính của bộ điều khiển thời điểm vận hạn
 */
export interface OverlayToolbarState {
    selectedYear: number;
    selectedMonth: number;
    isOverlayActive: boolean;
    birthYear: number;
}
/**
 * Ghép Năm + Tháng thành targetDateStr chuẩn dạng "YYYY-M-15"
 * (Lấy ngày 15 làm đại diện giữa tháng để xem Lưu Niên / Lưu Nguyệt)
 */
export declare function buildTargetDateStr(year: number, month: number, day?: number): string;
/**
 * Tạo danh sách năm từ năm sinh đến năm sinh + 100 tuổi
 */
export declare function generateYearOptions(birthYear: number, maxAge?: number): number[];
/**
 * Hàm Debounce chuẩn (~150ms) dùng để trì hoãn xử lý khi người dùng đổi nhanh liên tục
 */
export declare function createDebounce<F extends (...args: any[]) => any>(func: F, delayMs?: number): ((...args: Parameters<F>) => void) & {
    cancel: () => void;
};
/**
 * Tính toán lại lớp phủ vận hạn động từ lá số có sẵn mà KHÔNG tính lại Bản Mệnh
 *
 * @param astrolabe Lá số hiện tại (không gọi lại astro.bySolar)
 * @param year Năm cần xem
 * @param month Tháng cần xem (1 - 12)
 * @returns OverlayResult mới tương ứng với thời điểm đã chọn
 */
export declare function updateHoroscopeOverlay(astrolabe: IFunctionalAstrolabe, year: number, month: number): OverlayResult;
/**
 * Render cấu trúc HTML cho thanh công cụ thời điểm (Toolbar UI)
 */
export declare function renderOverlayToolbarHtml(state: {
    selectedYear: number;
    selectedMonth: number;
    birthYear: number;
    isOverlayActive: boolean;
    yearlyMutagensText?: string;
}): string;
