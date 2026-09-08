/**
 * Tùy chọn cấu hình cho hệ thống Tử Vi Việt Nam
 */
export interface VietnameseAstroOptions {
    /**
     * Tùy chọn Tứ Hóa cho Can Canh:
     * - 'standard': Nhật (Lộc) - Vũ (Quyền) - Đồng (Khoa) - Âm (Kỵ) (Mặc định chuẩn Tử Vi Việt Nam)
     * - 'khoi_viet': Nhật (Lộc) - Vũ (Quyền) - Khôi (Khoa) - Việt (Kỵ) / hoặc Âm (Kỵ)
     */
    canhMutagenType?: 'standard' | 'khoi_viet';
    /**
     * Tùy chọn sao Chủ Mệnh cho cung Sửu:
     * - 'CuMon': Cự Môn (Mặc định)
     * - 'LocTon': Lộc Tồn
     */
    chouSoulStar?: 'CuMon' | 'LocTon';
    /**
     * Ngôn ngữ hiển thị (Mặc định: 'vi-VN')
     */
    language?: 'vi-VN' | 'zh-CN' | 'zh-TW' | 'en-US' | 'ja-JP' | 'ko-KR';
    /**
     * Có xóa các sao Tuần/Triệt đơn lẻ cũ của Trung Châu Phái trước khi an cặp 2 cung không
     * Mặc định: true
     */
    cleanOldXunKongJieKong?: boolean;
}
/**
 * Interface kết quả Lưu Tinh theo năm xem (Lưu Niên)
 */
export interface VietnameseYearlyLuuResult {
    targetYear: number;
    heavenlyStem: string;
    earthlyBranch: string;
    /**
     * Danh sách sao lưu cho từng cung từ 0 đến 11 (bắt đầu từ Dần)
     */
    palaceLuuStars: {
        [palaceIndex: number]: string[];
    };
    /**
     * Tứ Hóa Lưu Niên của năm xem: [Lộc, Quyền, Khoa, Kỵ]
     */
    yearlyMutagen: string[];
}
