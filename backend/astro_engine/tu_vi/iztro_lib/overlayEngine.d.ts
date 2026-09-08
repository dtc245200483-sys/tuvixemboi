import { Astrolabe } from './data/types';
import { IFunctionalAstrolabe } from './astro/FunctionalAstrolabe';
/**
 * Cấu trúc dữ liệu vận hạn động tại từng ô cung trong 12 cung địa bàn
 */
export interface OverlayCell {
    /** Tên cung gốc trên bản mệnh (ví dụ: 'Mệnh', 'Phụ Mẫu', 'Phúc Đức'...) */
    namePalaceGoc: string;
    /** Địa chi cung gốc trên bàn cờ (ví dụ: 'Dần', 'Mão', 'Thìn'...) */
    branchGoc: string;
    /** Tầng Đại Hạn (10 năm) */
    daiHan: {
        /** Nhãn hiển thị: "ĐV." + tên cung chức năng đại hạn an tại cung gốc này */
        label: string;
    };
    /** Tầng Tiểu Hạn (1 năm theo vòng tuổi) - Lưu ý: Tiểu Hạn không an sao lưu trong iztro */
    tieuHan: {
        /** Nhãn hiển thị: "TH." + tên cung chức năng tiểu hạn an tại cung gốc này */
        label: string;
    };
    /** Tầng Lưu Niên (1 năm theo địa chi năm xem) */
    luuNien: {
        /** Nhãn hiển thị: "LN." + tên cung chức năng lưu niên an tại cung gốc này */
        label: string;
        /** Danh sách tên các sao lưu niên an tại vị trí cung gốc này (giữ nguyên tên gốc từ iztro) */
        stars: string[];
    };
    /** Tầng Lưu Nguyệt (1 tháng âm lịch) */
    luuNguyet: {
        /** Nhãn hiển thị: "Th." + tên cung chức năng lưu nguyệt an tại cung gốc này */
        label: string;
        /** Danh sách tên các sao lưu nguyệt an tại vị trí cung gốc này */
        stars: string[];
    };
    /** Tầng Lưu Nhật (1 ngày âm lịch) */
    luuNhat: {
        /** Nhãn hiển thị: "Ng." + tên cung chức năng lưu nhật an tại cung gốc này */
        label: string;
        /** Danh sách tên các sao lưu nhật an tại vị trí cung gốc này */
        stars: string[];
    };
}
/**
 * Kết quả trả về tổng hợp của module Overlay Engine
 */
export interface OverlayResult {
    /** Ngày mục tiêu được truyền vào (chuỗi ngày cần tính vận hạn) */
    targetDate: string;
    /** Tứ Hóa của tầng Đại Hạn theo thứ tự [Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ] */
    decadalMutagen: string[];
    /** Tứ Hóa của tầng Lưu Niên theo thứ tự [Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ] */
    yearlyMutagen: string[];
    /** Thông tin tầng Lưu Niên (tùy chọn) */
    yearly?: {
        index: number;
        name: string;
    };
    /** Thông tin tầng Đại Hạn (tùy chọn) */
    decadal?: {
        index: number;
        name: string;
    };
    /** Thông tin tầng Lưu Nguyệt (tùy chọn) */
    monthly?: {
        index: number;
        name: string;
    };
    /** Danh sách 12 ô cung xếp đúng theo thứ tự song song 1-1 với astrolabe.palaces */
    cells: OverlayCell[];
}
/**
 * Kiểm tra tính hợp lệ của chuỗi ngày mục tiêu (targetDateStr)
 * Định dạng yêu cầu: "YYYY-M-D" hoặc "YYYY-MM-DD"
 * Xử lý chặt chẽ để ném ra thông báo lỗi rõ ràng, tránh để iztro ném lỗi không rõ ràng
 *
 * @param dateStr Chuỗi ngày cần kiểm tra
 * @throws Error nếu ngày không hợp lệ hoặc không tồn tại trên lịch
 */
export declare function validateTargetDate(dateStr: string): void;
/**
 * Tính toán và trích xuất dữ liệu vận hạn động cho lá số Tử Vi tại một mốc thời gian mục tiêu
 *
 * @param astrolabe Đối tượng lá số được tạo từ astro.bySolar(...) hoặc astro.byLunar(...)
 * @param targetDateStr Chuỗi ngày mục tiêu dạng "YYYY-M-D" (ví dụ: "2026-6-15")
 * @returns OverlayResult chứa Tứ Hóa các tầng và 12 ô cung với nhãn cung động và danh sách sao lưu
 */
export declare function getOverlayData(astrolabe: IFunctionalAstrolabe | Astrolabe, targetDateStr: string): OverlayResult;
