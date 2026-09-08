import React from 'react';
import { IconLoader2 } from '@tabler/icons-react';

export const SUGGESTION_TOPICS = [
  { id: 'cong_danh', title: 'Công danh sự nghiệp' },
  { id: 'anh_em', title: 'Anh em, bạn bè' },
  { id: 'con_cai', title: 'Con cái' },
  { id: 'tinh_duyen', title: 'Tình duyên' },
  { id: 'vo_chong', title: 'Vợ chồng' },
  { id: 'tai_van', title: 'Tài vận, kinh tế' },
  { id: 'suc_khoe', title: 'Sức khỏe, bệnh tật' },
  { id: 'xuat_ngoai', title: 'Xuất ngoại' },
  { id: 'bang_huu', title: 'Bằng hữu, đồng nghiệp' },
  { id: 'phuc_duc', title: 'Phúc khí tổ tiên' },
  { id: 'cha_me', title: 'Cha mẹ' },
  { id: 'dien_trach', title: 'Nhà cửa, đất đai' },
  { id: 'dai_van', title: 'Đại vận' },
  { id: 'tieu_van', title: 'Tiểu vận' },
];

export default function TuViTopicSuggestions({
  activeTopic,
  onSelectTopic,
  loadingTopic,
  isChatOpen = false,
}) {
  return (
    <div className="w-full rounded-card overflow-hidden border border-[#B3261E]/30 bg-surface shadow-subtle my-4 transition-all">
      {/* BANNER HOA VĂN Á ĐÔNG "GỢI Ý" */}
      <div className="relative py-2 px-4 sm:px-6 bg-gradient-to-r from-[#6B140E] via-[#8B1C13] to-[#6B140E] border-b border-[#D4AF37]/40 flex items-center justify-center select-none overflow-hidden">
        {/* Họa tiết hoa văn chìm */}
        <div className="absolute inset-0 opacity-15 pointer-events-none bg-[radial-gradient(#D4AF37_1px,transparent_1px)] [background-size:12px_12px]" />
        <div className="relative z-10 flex items-center gap-2">
          <span className="text-[#D4AF37] text-xs sm:text-sm">✦</span>
          <h3 className="font-heading text-lg sm:text-xl font-bold tracking-wider text-[#FAF5EE] drop-shadow-md">
            Gợi ý
          </h3>
          <span className="text-[#D4AF37] text-xs sm:text-sm">✦</span>
        </div>
      </div>

      {/* DANH SÁCH CÁC NÚT BẤM PILL CHỦ ĐỀ */}
      <div className="p-3 sm:p-4 bg-[#FBF8F3]">
        <div className="flex flex-wrap items-center gap-2 sm:gap-2.5">
          {SUGGESTION_TOPICS.map((t) => {
            const isActive = activeTopic === t.id && !isChatOpen;
            const isLoadingThis = loadingTopic === t.id;

            return (
              <button
                key={t.id}
                type="button"
                onClick={() => onSelectTopic(t.id)}
                disabled={isLoadingThis}
                className={`px-3.5 py-1.5 rounded-full text-xs sm:text-sm font-body font-medium transition-all duration-200 flex items-center gap-1.5 shadow-2xs ${
                  isActive
                    ? 'bg-[#8B0000] text-white font-semibold shadow-sm ring-2 ring-[#8B0000]/30 scale-[1.02]'
                    : 'bg-white text-gray-700 hover:bg-[#F3EDE2] hover:text-[#8B0000] border border-gray-200/90 active:scale-95'
                }`}
              >
                {isLoadingThis ? (
                  <IconLoader2 size={14} className="animate-spin text-current" />
                ) : null}
                <span>{t.title}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
