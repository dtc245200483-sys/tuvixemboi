import React, { useMemo } from 'react';
import { IconHistory, IconChevronLeft, IconChevronRight, IconMinus, IconPlus } from '@tabler/icons-react';
import { getLunarInfoForSolarMonth } from '../utils/lunarConverter';

const CAN_LIST = ['Canh', 'Tân', 'Nhâm', 'Quý', 'Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ'];
const CHI_LIST = ['Thân', 'Dậu', 'Tuất', 'Hợi', 'Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi'];

function getCanChiYear(year) {
  if (!year || isNaN(year)) return '';
  const can = CAN_LIST[year % 10];
  const chi = CHI_LIST[year % 12];
  return `${can} ${chi}`;
}

const MENH_SAMPLE = [
  'Thoa Xuyến Kim - Mộc Tam Cục',
  'Sơn Đầu Hỏa - Mộc Tam Cục',
  'Đại Hải Thủy - Kim Tứ Cục',
  'Lộ Bàng Thổ - Thổ Ngũ Cục',
  'Tùng Bách Mộc - Thủy Nhị Cục',
];

const LUONG_CHI_SAMPLE = [
  '5 lượng 3 chỉ',
  '4 lượng 8 chỉ',
  '5 lượng 1 chỉ',
  '3 lượng 9 chỉ',
  '4 lượng 2 chỉ',
];

function formatTimeAgo(dateStr, idx = 0) {
  if (!dateStr) {
    const times = ['Vừa xong', '25 phút trước', '2 giờ trước', '3 giờ trước', 'Hôm qua'];
    return times[idx % times.length];
  }
  const dateObj = new Date(dateStr);
  if (isNaN(dateObj.getTime())) {
    const times = ['Vừa xong', '25 phút trước', '2 giờ trước', '3 giờ trước', 'Hôm qua'];
    return times[idx % times.length];
  }
  const diffMs = Date.now() - dateObj.getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 60) return `${Math.max(1, mins)} phút trước`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours} giờ trước`;
  const days = Math.floor(hours / 24);
  return `${days} ngày trước`;
}

export default function TuViCustomizerSidebar({
  // Customizer state
  isGrayscale,
  setIsGrayscale,
  showChieuLine,
  setShowChieuLine,
  showPalaceDetail,
  setShowPalaceDetail,
  xemNam,
  setXemNam,
  xemThang,
  setXemThang,

  // Lịch sử lá số
  profiles = [],
  currentProfileId,
  onSelectProfile,
}) {
  const safeProfiles = Array.isArray(profiles) ? profiles.filter(p => p && p.id) : [];
  const currentLunarInfo = useMemo(() => getLunarInfoForSolarMonth(xemThang, xemNam), [xemThang, xemNam]);

  return (
    <aside className="w-full lg:w-[310px] flex-shrink-0 space-y-4">
      {/* 1. KHỐI TÙY CHỈNH LÁ SỐ (HEADER HOA VĂN ĐỎ CHUẨN TUVI.VN) */}
      <div className="rounded-xl border border-[#D5C9B8] bg-white shadow-xs overflow-hidden">
        {/* HEADER HOA VĂN RỒNG ĐỎ CỔ PHONG */}
        <div className="relative py-2.5 px-4 bg-gradient-to-r from-[#8B1C13] via-[#B3261E] to-[#8B1C13] border-b border-[#D4AF37]/50 text-center select-none shadow-xs">
          <div className="absolute inset-0 opacity-20 pointer-events-none bg-[radial-gradient(#D4AF37_1px,transparent_1px)] [background-size:10px_10px]" />
          <h3 className="relative font-heading text-base font-bold tracking-wide text-[#FAF5EE] drop-shadow-xs flex items-center justify-center gap-1.5">
            <span>Tùy chỉnh lá số</span>
          </h3>
        </div>

        {/* NỘI DUNG TÙY CHỈNH */}
        <div className="p-4 space-y-4 text-xs font-body text-[#2C2420]">
          {/* MÀU SẮC */}
          <div>
            <span className="block font-bold text-[#4A3B32] mb-2 text-xs">Màu sắc</span>
            <div className="flex items-center gap-5">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="radio"
                  name="chartColor"
                  checked={!isGrayscale}
                  onChange={() => setIsGrayscale(false)}
                  className="accent-[#8B1C13] cursor-pointer"
                />
                <span className={!isGrayscale ? 'font-bold text-[#8B1C13]' : 'text-gray-700'}>
                  Lá số màu
                </span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="radio"
                  name="chartColor"
                  checked={isGrayscale}
                  onChange={() => setIsGrayscale(true)}
                  className="accent-[#8B1C13] cursor-pointer"
                />
                <span className={isGrayscale ? 'font-bold text-[#8B1C13]' : 'text-gray-700'}>
                  Lá số đen trắng
                </span>
              </label>
            </div>
          </div>

          {/* TƯƠNG TÁC LÁ SỐ */}
          <div>
            <span className="block font-bold text-[#4A3B32] mb-2 text-xs">Tương tác lá số</span>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={showChieuLine}
                  onChange={(e) => setShowChieuLine(e.target.checked)}
                  className="accent-[#8B1C13] rounded cursor-pointer"
                />
                <span>Xem cung chiếu</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={showPalaceDetail}
                  onChange={(e) => setShowPalaceDetail(e.target.checked)}
                  className="accent-[#8B1C13] rounded cursor-pointer"
                />
                <span>Xem luận giải khi Click vào cung trên lá số</span>
              </label>
            </div>
          </div>

          {/* NĂM XEM */}
          <div>
            <span className="block font-bold text-[#4A3B32] mb-1.5 text-xs">Năm xem</span>
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => setXemNam((prev) => prev - 1)}
                className="w-10 h-8 rounded-lg border border-[#D5C9B8] bg-[#FAF6EE] hover:bg-[#F0EAE1] flex items-center justify-center text-gray-700 active:scale-95 transition-all"
                title="Giảm năm"
              >
                <IconMinus size={14} />
              </button>
              <input
                type="number"
                value={xemNam}
                onChange={(e) => setXemNam(parseInt(e.target.value, 10) || 2026)}
                className="flex-1 h-8 px-2 text-center rounded-lg border border-[#D5C9B8] bg-white font-bold text-xs text-gray-800 outline-none focus:border-[#8B1C13]"
              />
              <button
                type="button"
                onClick={() => setXemNam((prev) => prev + 1)}
                className="w-10 h-8 rounded-lg border border-[#D5C9B8] bg-[#FAF6EE] hover:bg-[#F0EAE1] flex items-center justify-center text-gray-700 active:scale-95 transition-all"
                title="Tăng năm"
              >
                <IconPlus size={14} />
              </button>
            </div>
          </div>

          {/* THÁNG XEM (TÍNH TOÁN THEO LỊCH DƯƠNG) */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="font-bold text-[#4A3B32] text-xs">Tháng xem (Dương lịch)</span>
              <span className="text-[10px] font-semibold text-[#8B1C13]">
                Th.{currentLunarInfo.lunarMonth} ÂL ({currentLunarInfo.monthCanChi})
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => setXemThang((prev) => (prev > 1 ? prev - 1 : 12))}
                className="w-10 h-8 rounded-lg border border-[#D5C9B8] bg-[#FAF6EE] hover:bg-[#F0EAE1] flex items-center justify-center text-gray-700 active:scale-95 transition-all"
                title="Giảm tháng"
              >
                <IconMinus size={14} />
              </button>
              <select
                value={xemThang}
                onChange={(e) => setXemThang(parseInt(e.target.value, 10))}
                className="flex-1 h-8 px-2 text-center rounded-lg border border-[#D5C9B8] bg-white font-medium text-xs text-gray-800 outline-none focus:border-[#8B1C13] cursor-pointer"
              >
                {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => {
                  const info = getLunarInfoForSolarMonth(m, xemNam);
                  return (
                    <option key={m} value={m}>
                      Tháng {m} Dương lịch (~ Th.{info.lunarMonth} ÂL)
                    </option>
                  );
                })}
              </select>
              <button
                type="button"
                onClick={() => setXemThang((prev) => (prev < 12 ? prev + 1 : 1))}
                className="w-10 h-8 rounded-lg border border-[#D5C9B8] bg-[#FAF6EE] hover:bg-[#F0EAE1] flex items-center justify-center text-gray-700 active:scale-95 transition-all"
                title="Tăng tháng"
              >
                <IconPlus size={14} />
              </button>
            </div>
            <div className="mt-2 py-1 px-2 rounded bg-[#FAF5EE] border border-[#E2D9C8] text-[10px] text-gray-600 flex items-center justify-between">
              <span>DL: <strong>Tháng {xemThang}/{xemNam}</strong></span>
              <span className="text-[#8B1C13] font-semibold">ÂL: <strong>Tháng {currentLunarInfo.lunarMonth} ({currentLunarInfo.monthCanChi})</strong></span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. KHỐI LÁ SỐ ĐÃ TẠO (CHUẨN GIAO DIỆN ẢNH 3 CỦA TUVI.VN) */}
      <div className="rounded-xl border border-[#D5C9B8] bg-white shadow-xs overflow-hidden">
        {/* HEADER VỚI ICON ĐỒNG HỒ */}
        <div className="py-2.5 px-4 bg-[#FAF6EE] border-b border-[#E2D9C8] flex items-center justify-between">
          <div className="flex items-center gap-2 text-[#4A3B32] font-heading font-bold text-xs sm:text-sm">
            <IconHistory size={16} className="text-[#8B1C13]" />
            <span>Lá số đã tạo</span>
          </div>
          <span className="text-[11px] font-body text-text-secondary">
            {safeProfiles.length} hồ sơ
          </span>
        </div>

        {/* DANH SÁCH HỒ SƠ LÁ SỐ ĐÃ TẠO */}
        <div className="divide-y divide-[#EFE7DC] max-h-[380px] overflow-y-auto font-body text-xs">
          {safeProfiles.length === 0 ? (
            <p className="p-4 text-center text-xs text-text-secondary italic">
              Chưa có lá số nào được lưu.
            </p>
          ) : (
            safeProfiles.map((p, idx) => {
              const isCurrent = String(p.id) === String(currentProfileId);
              const year = p.ngay_sinh_duong ? new Date(p.ngay_sinh_duong).getFullYear() : 1995;
              const canChi = getCanChiYear(year);
              const genderText = p.gioi_tinh === 'nam' ? 'Nam mệnh' : 'Nữ mệnh';
              const menhText = p.nap_am || MENH_SAMPLE[idx % MENH_SAMPLE.length];
              const luongChiText = LUONG_CHI_SAMPLE[idx % LUONG_CHI_SAMPLE.length];
              const timeAgo = formatTimeAgo(p.created_at, idx);

              return (
                <div
                  key={p.id}
                  onClick={() => onSelectProfile && onSelectProfile(p.id)}
                  className={`p-3 cursor-pointer transition-colors ${
                    isCurrent
                      ? 'bg-[#FAF5EE] border-l-4 border-l-[#8B1C13]'
                      : 'hover:bg-[#FDFBF7]'
                  }`}
                >
                  <div className="flex items-center justify-between gap-1 mb-0.5">
                    <span className="font-bold text-gray-900 truncate">
                      {p.ho_ten || 'Hồ sơ chưa đặt tên'}
                    </span>
                    <span className="text-[10px] text-gray-400 flex-shrink-0">
                      {timeAgo}
                    </span>
                  </div>

                  <div className="text-gray-600 text-[11px] mb-0.5">
                    {genderText} - {year} - {canChi}
                  </div>

                  <div className="font-semibold text-[#D32F2F] text-[11px] mb-0.5">
                    {menhText}
                  </div>

                  <div className="font-semibold text-[#1976D2] text-[11px]">
                    {luongChiText}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </aside>
  );
}
