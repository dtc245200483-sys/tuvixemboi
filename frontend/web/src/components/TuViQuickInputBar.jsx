import React, { useState } from 'react';
import { IconSparkles, IconLoader2 } from '@tabler/icons-react';
import { birthProfileService } from '../services/api';
import { notifyQuotaUpdated } from './QuotaBadge';
import QuotaExceededModal from './QuotaExceededModal';

const CHI_HOURS = [
  { chi: 'Tý', range: '23:00 - 01:00', hour: 0, minute: 0 },
  { chi: 'Sửu', range: '01:00 - 03:00', hour: 2, minute: 0 },
  { chi: 'Dần', range: '03:00 - 05:00', hour: 4, minute: 0 },
  { chi: 'Mão', range: '05:00 - 07:00', hour: 6, minute: 0 },
  { chi: 'Thìn', range: '07:00 - 09:00', hour: 8, minute: 0 },
  { chi: 'Tỵ', range: '09:00 - 11:00', hour: 10, minute: 0 },
  { chi: 'Ngọ', range: '11:00 - 13:00', hour: 12, minute: 0 },
  { chi: 'Mùi', range: '13:00 - 15:00', hour: 14, minute: 0 },
  { chi: 'Thân', range: '15:00 - 17:00', hour: 16, minute: 0 },
  { chi: 'Dậu', range: '17:00 - 19:00', hour: 18, minute: 0 },
  { chi: 'Tuất', range: '19:00 - 21:00', hour: 20, minute: 0 },
  { chi: 'Hợi', range: '21:00 - 23:00', hour: 22, minute: 0 },
];

export default function TuViQuickInputBar({
  currentProfile,
  onProfileCreated,
  buttonText = 'An Sao Lập Lá Số',
}) {
  const [hoTen, setHoTen] = useState(currentProfile?.ho_ten || 'Phạm Vũ Quang Hưng');
  const [gioiTinh, setGioiTinh] = useState(currentProfile?.gioi_tinh || 'nam');
  const [loaiLich, setLoaiLich] = useState('duong_lich');
  const [ngaySinh, setNgaySinh] = useState(currentProfile?.ngay_sinh_duong || '1995-10-15');
  const [chiIndex, setChiIndex] = useState(6); // Default: Ngọ (11:00 - 13:00)
  const [ngonNgu, setNgonNgu] = useState('vi-VN');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [showQuotaModal, setShowQuotaModal] = useState(false);

  // Tự động đồng bộ thông tin khi hồ sơ được tải hoặc thay đổi
  React.useEffect(() => {
    if (currentProfile) {
      if (currentProfile.ho_ten) setHoTen(currentProfile.ho_ten);
      if (currentProfile.gioi_tinh) setGioiTinh(currentProfile.gioi_tinh);
      if (currentProfile.ngay_sinh_duong) setNgaySinh(currentProfile.ngay_sinh_duong);
      if (currentProfile.gio_sinh !== undefined && currentProfile.gio_sinh !== null) {
        const h = Number(currentProfile.gio_sinh);
        const idx = (h === 23 || h === 0) ? 0 : Math.floor((h + 1) / 2) % 12;
        setChiIndex(idx);
      }
    }
  }, [currentProfile]);

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!hoTen.trim()) {
      setErrorMsg('Vui lòng nhập họ và tên');
      return;
    }
    if (!ngaySinh) {
      setErrorMsg('Vui lòng chọn ngày sinh');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);

    const selectedHour = CHI_HOURS[chiIndex] || CHI_HOURS[6];

    try {
      const payload = {
        ho_ten: hoTen.trim(),
        gioi_tinh: gioiTinh,
        ngay_sinh_duong: ngaySinh,
        gio_sinh: selectedHour.hour,
        phut_sinh: selectedHour.minute,
      };

      // Gọi endpoint /birth-profile/an-sao để trừ 1 lượt quota và an sao lá số
      const res = await birthProfileService.anSao(payload);
      const newProfile = res.data?.du_lieu || res.data;

      // Đồng bộ thông báo cập nhật QuotaBadge
      notifyQuotaUpdated();

      if (newProfile && newProfile.id) {
        if (onProfileCreated) {
          onProfileCreated(newProfile.id);
        }
      }
    } catch (err) {
      console.error('Lỗi an sao lập lá số:', err);
      const status = err.response?.status;
      const detail = err.response?.data?.detail || err.response?.data?.loi || '';
      const detailStr = typeof detail === 'string' ? detail : JSON.stringify(detail);

      if (status === 429 || detailStr.toLowerCase().includes('hết lượt')) {
        setShowQuotaModal(true);
        setErrorMsg('Bạn đã dùng hết lượt an sao hôm nay. Vui lòng nâng cấp Premium hoặc đợi đến 00:00 ngày mai.');
      } else {
        setErrorMsg(detailStr || 'Không thể tạo lá số. Vui lòng kiểm tra lại ngày giờ sinh.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full bg-[#FAF6EE] border border-[#E2D9C8] rounded-2xl p-4 sm:p-5 shadow-xs mb-6 text-[#2C2420]">
      <form onSubmit={handleSubmit} className="space-y-3">
        {/* HÀNG INPUT CÁC TRƯỜNG DỮ LIỆU */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {/* HỌ VÀ TÊN */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[#7D6B58] mb-1">
              Họ và tên
            </label>
            <input
              type="text"
              value={hoTen}
              onChange={(e) => setHoTen(e.target.value)}
              placeholder="Nhập họ tên..."
              className="w-full h-9 px-2.5 rounded-lg border border-[#D5C9B8] bg-[#F0F5FF] text-xs font-semibold text-gray-800 outline-none focus:border-[#8B1C13] focus:ring-1 focus:ring-[#8B1C13]/30 transition-all"
            />
          </div>

          {/* GIỚI TÍNH */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[#7D6B58] mb-1">
              Giới tính
            </label>
            <select
              value={gioiTinh}
              onChange={(e) => setGioiTinh(e.target.value)}
              className="w-full h-9 px-2 rounded-lg border border-[#D5C9B8] bg-white text-xs font-medium text-gray-800 outline-none focus:border-[#8B1C13] transition-all cursor-pointer"
            >
              <option value="nam">Nam (Dương Nam / Âm Nam)</option>
              <option value="nu">Nữ (Dương Nữ / Âm Nữ)</option>
            </select>
          </div>

          {/* LOẠI LỊCH */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[#7D6B58] mb-1">
              Loại lịch
            </label>
            <select
              value={loaiLich}
              onChange={(e) => setLoaiLich(e.target.value)}
              className="w-full h-9 px-2 rounded-lg border border-[#D5C9B8] bg-white text-xs font-medium text-gray-800 outline-none focus:border-[#8B1C13] transition-all cursor-pointer"
            >
              <option value="duong_lich">Dương Lịch (Solar)</option>
              <option value="am_lich">Âm Lịch (Lunar)</option>
            </select>
          </div>

          {/* NGÀY SINH */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[#7D6B58] mb-1">
              Ngày sinh
            </label>
            <input
              type="date"
              value={ngaySinh}
              onChange={(e) => setNgaySinh(e.target.value)}
              className="w-full h-9 px-2 rounded-lg border border-[#D5C9B8] bg-white text-xs font-medium text-gray-800 outline-none focus:border-[#8B1C13] transition-all cursor-pointer"
            />
          </div>

          {/* GIỜ SINH (12 ĐỊA CHI) */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[#7D6B58] mb-1 truncate">
              Giờ sinh (12 địa chi)
            </label>
            <select
              value={chiIndex}
              onChange={(e) => setChiIndex(parseInt(e.target.value, 10))}
              className="w-full h-9 px-2 rounded-lg border border-[#D5C9B8] bg-white text-xs font-medium text-gray-800 outline-none focus:border-[#8B1C13] transition-all cursor-pointer"
            >
              {CHI_HOURS.map((item, idx) => (
                <option key={item.chi} value={idx}>
                  {item.chi} ({item.range})
                </option>
              ))}
            </select>
          </div>

          {/* NGÔN NGỮ */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[#7D6B58] mb-1">
              Ngôn ngữ
            </label>
            <select
              value={ngonNgu}
              onChange={(e) => setNgonNgu(e.target.value)}
              className="w-full h-9 px-2 rounded-lg border border-[#D5C9B8] bg-white text-xs font-medium text-gray-800 outline-none focus:border-[#8B1C13] transition-all cursor-pointer"
            >
              <option value="vi-VN">Tiếng Việt (vi-VN)</option>
              <option value="zh-CN">Trung Văn (zh-CN)</option>
              <option value="en-US">English (en-US)</option>
            </select>
          </div>
        </div>

        {/* BÁO LỖI NẾU CÓ */}
        {errorMsg && (
          <p className="text-xs text-red-600 font-medium">{errorMsg}</p>
        )}

        {/* NÚT BẤM AN SAO LẬP LÁ SỐ */}
        <div className="pt-1 flex items-center gap-3">
          <button
            type="submit"
            disabled={isSubmitting}
            className="inline-flex items-center justify-center gap-2 px-6 py-2 rounded-lg bg-[#6B140E] hover:bg-[#552218] text-[#FAF5EE] text-xs sm:text-sm font-bold shadow-sm transition-all duration-200 active:scale-95 cursor-pointer disabled:opacity-70"
          >
            {isSubmitting && (
              <IconLoader2 size={16} className="animate-spin text-[#D4AF37]" />
            )}
            <span>{buttonText}</span>
          </button>
        </div>
      </form>

      {/* MODAL CẢNH BÁO HẾT LƯỢT VÀ NÂNG CẤP PREMIUM */}
      <QuotaExceededModal
        isOpen={showQuotaModal}
        onClose={() => setShowQuotaModal(false)}
        onUpgraded={() => {
          setErrorMsg(null);
        }}
      />
    </div>
  );
}
