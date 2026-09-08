import { VietnameseAstroOptions } from './types';
/**
 * Bảng Tứ Hóa Tử Vi Việt Nam (Nam Phái truyền thống)
 * Định dạng mỗi can là mảng 4 sao: [Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ]
 */
export declare const VIETNAMESE_MUTAGENS_VI: Record<string, [string, string, string, string]>;
/**
 * Phiên bản Tứ Hóa dạng Key chuẩn của iztro (dùng cho map nội bộ)
 */
export declare const VIETNAMESE_MUTAGENS_KEYS: Record<string, [string, string, string, string]>;
/**
 * Lấy danh sách 4 sao Hóa [Lộc, Quyền, Khoa, Kỵ] theo Thiên Can
 */
export declare function getVietnameseMutagensByStem(stem: string, options?: VietnameseAstroOptions): [string, string, string, string];
/**
 * Tra cứu xem một sao có Tứ Hóa theo Thiên Can đang xét hay không
 * @returns 'Lộc' | 'Quyền' | 'Khoa' | 'Kỵ' | ''
 */
export declare function getVietnameseMutagenByStar(starName: string, heavenlyStem: string, options?: VietnameseAstroOptions): string;
