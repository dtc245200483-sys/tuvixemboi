import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  IconUser,
  IconCheck,
  IconPlus,
  IconX,
  IconCalendar,
  IconStar,
  IconLoader2
} from '@tabler/icons-react';
import { birthProfileService } from '../services/api';

export default function SelectProfileModal({
  isOpen,
  onClose,
  profiles = [],
  selectedProfileId,
  onProfileSelected,
}) {
  const navigate = useNavigate();
  const [settingId, setSettingId] = useState(null);

  if (!isOpen) return null;

  const handleSelectDefault = async (profile) => {
    setSettingId(profile.id);
    try {
      await birthProfileService.setDefault(profile.id);
      if (typeof window !== 'undefined') {
        localStorage.setItem('selected_ho_so_menh_id', profile.id);
      }
      if (onProfileSelected) {
        onProfileSelected(profile);
      }
      onClose();
    } catch (err) {
      console.error('Lỗi đặt hồ sơ mặc định:', err);
      // Vẫn lưu localStorage và cập nhật UI phía client nếu backend gặp sự cố
      if (typeof window !== 'undefined') {
        localStorage.setItem('selected_ho_so_menh_id', profile.id);
      }
      if (onProfileSelected) {
        onProfileSelected(profile);
      }
      onClose();
    } finally {
      setSettingId(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-fadeIn">
      <div className="relative w-full max-w-xl bg-[#FAF6EE] border border-[#E2D9C8] rounded-2xl shadow-2xl overflow-hidden text-[#2C2420] max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-[#6B140E] text-white p-5 sm:p-6 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center text-[#D4AF37]">
              <IconUser size={22} />
            </div>
            <div>
              <h3 className="font-heading text-lg sm:text-xl font-bold tracking-wide">
                Chọn Hồ Sơ Mệnh Lý
              </h3>
              <p className="text-xs text-[#EADFC8]">
                Chọn hồ sơ mệnh chủ chính hoặc chuyển đổi giữa các hồ sơ đã lưu
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full text-white/70 hover:text-white hover:bg-white/10 transition-colors focus:outline-none"
          >
            <IconX size={20} />
          </button>
        </div>

        {/* Danh sách hồ sơ */}
        <div className="p-5 sm:p-6 space-y-3 overflow-y-auto flex-1">
          {profiles.length === 0 ? (
            <div className="text-center py-8 text-sm text-[#7D6B58] space-y-3">
              <p>Bạn chưa có hồ sơ sinh nào.</p>
              <Link
                to="/birth-profile"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#6B140E] text-white text-xs font-bold"
              >
                <IconPlus size={16} />
                <span>Tạo hồ sơ đầu tiên</span>
              </Link>
            </div>
          ) : (
            profiles.map((p) => {
              const isCurrent = String(p.id) === String(selectedProfileId);
              const lunar = p.thong_tin_am_lich || {};
              const isSetting = settingId === p.id;

              return (
                <div
                  key={p.id}
                  className={`p-4 rounded-xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                    isCurrent
                      ? 'bg-[#FFFDF9] border-[#6B140E] ring-1 ring-[#6B140E]/30 shadow-xs'
                      : 'bg-white border-[#E2D9C8] hover:border-[#8B1C13]/60'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-heading text-base font-bold text-[#6B140E]">
                        {p.ho_ten || 'Mệnh Chủ'}
                      </span>
                      {isCurrent && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#6B140E] text-[#FAF5EE] text-[10px] font-bold uppercase tracking-wider">
                          <IconCheck size={12} />
                          <span>Hồ Sơ Đang Chọn</span>
                        </span>
                      )}
                      <span className="px-2 py-0.5 rounded bg-[#FAF5EE] border border-[#E2D9C8] text-[11px] font-medium text-[#7D6B58]">
                        {p.gioi_tinh === 'nam' ? 'Nam Mạng' : 'Nữ Mạng'}
                      </span>
                    </div>

                    <div className="text-xs text-[#7D6B58] flex flex-wrap items-center gap-x-3 gap-y-1">
                      <span>
                        Dương lịch: {p.ngay_sinh_duong} ({p.gio_sinh}h:{String(p.phut_sinh).padStart(2, '0')})
                      </span>
                      <span>•</span>
                      <span>
                        Âm lịch: {lunar.can_chi_nam || p.ngay_sinh_am || '--'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end sm:self-center">
                    {isCurrent ? (
                      <span className="text-xs font-semibold text-emerald-700 flex items-center gap-1 py-1.5 px-3">
                        <IconCheck size={15} />
                        <span>Đang hiển thị</span>
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => handleSelectDefault(p)}
                        disabled={isSetting}
                        className="py-1.5 px-3 rounded-lg border border-[#8B1C13] text-[#8B1C13] hover:bg-[#8B1C13] hover:text-white text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                      >
                        {isSetting ? (
                          <IconLoader2 size={14} className="animate-spin" />
                        ) : (
                          <IconStar size={14} />
                        )}
                        <span>Chọn làm Hồ Sơ Mệnh</span>
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-[#F2EDE2] border-t border-[#E2D9C8] flex items-center justify-between gap-3 flex-shrink-0">
          <Link
            to="/birth-profile"
            onClick={onClose}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#6B140E] hover:bg-[#552218] text-white text-xs font-bold shadow-xs transition-colors"
          >
            <IconPlus size={15} />
            <span>Thêm Hồ Sơ Mới</span>
          </Link>

          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-[#D5C9B8] text-xs font-semibold text-[#7D6B58] hover:bg-white transition-colors"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
}
