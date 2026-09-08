import { IFunctionalAstrolabe } from '../astro/FunctionalAstrolabe';
import { VietnameseAstroOptions, VietnameseYearlyLuuResult } from './types';
/**
 * HÀM CỐT LÕI: Ghi đè (override/adapter) các quy tắc Tử Vi Việt Nam lên đối tượng Astrolabe của iztro
 */
export declare function applyVietnameseRules(astrolabe: IFunctionalAstrolabe, options?: VietnameseAstroOptions): IFunctionalAstrolabe;
/**
 * PLUGIN TỬ VI VIỆT NAM (dùng cho astrolabe.use(vietnamesePlugin) hoặc astro.loadPlugin)
 */
export declare function vietnamesePlugin(this: IFunctionalAstrolabe): void;
/**
 * WRAPPER THƯ VIỆN: astroVietnam
 * Cung cấp API trực tiếp thay thế hoặc bổ trợ cho astro.bySolar / astro.byLunar
 */
export declare const astroVietnam: {
    /**
     * Tính lá số theo Dương lịch chuẩn Tử Vi Việt Nam
     */
    bySolar: (solarDateStr: string, timeIndex: number, gender: string, fixLeap?: boolean, options?: VietnameseAstroOptions) => IFunctionalAstrolabe;
    /**
     * Tính lá số theo Âm lịch chuẩn Tử Vi Việt Nam
     */
    byLunar: (lunarDateStr: string, timeIndex: number, gender: string, isLeapMonth?: boolean, fixLeap?: boolean, options?: VietnameseAstroOptions) => IFunctionalAstrolabe;
    /**
     * Module Lưu Tinh: Tính toàn bộ sao lưu niên theo năm xem
     */
    getYearlyLuuTinh: (targetYear: number, options?: VietnameseAstroOptions) => VietnameseYearlyLuuResult;
    /**
     * Hàm override áp dụng lên đối tượng Astrolabe có sẵn
     */
    applyRules: typeof applyVietnameseRules;
};
