import { VietnameseAstroOptions } from './types';
/**
 * Danh sách 12 Địa Chi theo thứ tự chuẩn từ Tý đến Hợi (để tính toán can chi)
 */
export declare const BRANCHES_FROM_ZI: string[];
/**
 * Danh sách 10 Thiên Can theo thứ tự chuẩn
 */
export declare const STEMS: string[];
/**
 * Danh sách 12 Cung theo thứ tự cung trong iztro (Bắt đầu từ Cung Dần = 0)
 * 0: Dần, 1: Mão, 2: Thìn, 3: Tỵ, 4: Ngọ, 5: Mùi,
 * 6: Thân, 7: Dậu, 8: Tuất, 9: Hợi, 10: Tý, 11: Sửu
 */
export declare const PALACE_BRANCHES_FROM_YIN: string[];
/**
 * Chuyển đổi tên Địa Chi thành chỉ số cung iztro (0: Dần -> 11: Sửu)
 */
export declare function branchToPalaceIndex(branchName: string): number;
/**
 * Chuyển đổi tên Địa Chi thành chỉ số chi chuẩn từ Tý = 0 đến Hợi = 11
 */
export declare function branchToZiIndex(branchName: string): number;
/**
 * Chuyển đổi tên Thiên Can thành chỉ số từ Giáp = 0 đến Quý = 9
 */
export declare function stemToIndex(stemName: string): number;
/**
 * Xác định thuộc tính Âm Dương Nam Nữ
 * @returns true nếu là Dương Nam hoặc Âm Nữ (thuận), false nếu là Âm Nam hoặc Dương Nữ (nghịch)
 */
export declare function isDuongNamOrAmNu(stemName: string, gender: string): boolean;
export interface TuanTrietResult {
    /** 2 chỉ số cung chứa Triệt (0: Dần .. 11: Sửu) */
    trietPalaceIndices: [number, number];
    /** 2 chỉ số cung chứa Tuần (0: Dần .. 11: Sửu) */
    tuanPalaceIndices: [number, number];
    trietBranches: [string, string];
    tuanBranches: [string, string];
}
export declare function getTuanTrietPalaceIndices(stemName: string, branchName: string): TuanTrietResult;
export interface KuiYueResult {
    kuiPalaceIndex: number;
    yuePalaceIndex: number;
    kuiBranch: string;
    yueBranch: string;
}
export declare function getVietnameseKuiYue(stemName: string): KuiYueResult;
export interface HuoLingResult {
    huoPalaceIndex: number;
    lingPalaceIndex: number;
}
export declare function getVietnameseHuoLing(yearBranch: string, timeIndex: number, isDuongNamOrAmNuValue: boolean): HuoLingResult;
export declare const VIETNAMESE_SUIQIAN_STARS: string[];
export declare const VIETNAMESE_BOSHI_STARS: string[];
/**
 * Tính Vòng Thái Tuế Việt Nam cho 12 cung (khởi từ Chi năm sinh, luôn đi thuận)
 */
export declare function getVietnameseSuiQian12(yearBranch: string): string[];
/**
 * Tính Vòng Bác Sĩ Việt Nam (khởi từ Lộc Tồn, phân chiều theo Âm Dương Nam Nữ)
 */
export declare function getVietnameseBoShi12(luPalaceIndex: number, isDuongNamOrAmNuValue: boolean): string[];
export declare const VIETNAMESE_CHANGSHENG_STARS: string[];
export declare function getVietnameseChangSheng12(cucNameOrNumber: string | number, isDuongNamOrAmNuValue: boolean): string[];
export interface SoulAndBodyResult {
    soul: string;
    body: string;
}
export declare function getVietnameseSoulAndBody(menhPalaceBranch: string, yearBranch: string, options?: VietnameseAstroOptions): SoulAndBodyResult;
