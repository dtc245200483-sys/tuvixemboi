import React from 'react';
import {
  IconCompass,
  IconSparkles,
  IconFlame,
  IconDroplet,
  IconLeaf,
  IconMountain,
  IconCoin,
  IconUser,
  IconHeartHandshake,
  IconClock,
  IconCalendarEvent,
  IconShieldCheck,
  IconBulb,
  IconChevronRight,
  IconMessages,
  IconLayersLinked,
  IconArrowRight,
} from '@tabler/icons-react';
import { PILLAR_DEFINITIONS, getPillarAnalysis } from '../utils/batTuAnalyzer';

const HANH_ICONS = {
  'Kim': IconCoin,
  'Mộc': IconLeaf,
  'Thủy': IconDroplet,
  'Hỏa': IconFlame,
  'Thổ': IconMountain,
};

const HANH_COLORS = {
  'Kim': { bg: 'bg-[#FAF5EE]', text: 'text-[#8A6F52]', border: 'border-[#D5C9B8]', badge: 'bg-[#FAF5EE] text-[#6E4F32] border-[#D5C9B8]' },
  'Mộc': { bg: 'bg-[#F2F7F2]', text: 'text-[#2D5A27]', border: 'border-[#C2DFC0]', badge: 'bg-[#E5F0E4] text-[#244A20] border-[#B8D7B5]' },
  'Thủy': { bg: 'bg-[#F0F5FA]', text: 'text-[#1D4E70]', border: 'border-[#BCD1E3]', badge: 'bg-[#E1ECF5] text-[#163E5A] border-[#B2CBE0]' },
  'Hỏa': { bg: 'bg-[#FAF0EE]', text: 'text-[#8B1C13]', border: 'border-[#E6C2BC]', badge: 'bg-[#F7E2DF] text-[#7A150D] border-[#E8BAB2]' },
  'Thổ': { bg: 'bg-[#FAF6EE]', text: 'text-[#855B14]', border: 'border-[#E0D0AE]', badge: 'bg-[#F5ECCE] text-[#704B0E] border-[#DAC38E]' },
};

export default function BatTuPillarDetail({
  selectedPillarId,
  onSelectPillar,
  tuTruData,
  onOpenChatWithQuestion = null,
}) {
  const analysis = getPillarAnalysis(selectedPillarId, tuTruData);
  if (!analysis) return null;

  const {
    def,
    can,
    chi,
    canDetail,
    chiDetail,
    thapThanCan,
    theDungCanChi,
    tangCanWithThapThan,
    paragraphs,
  } = analysis;

  const CanIcon = HANH_ICONS[canDetail.hanh] || IconSparkles;
  const ChiIcon = HANH_ICONS[chiDetail.hanh] || IconSparkles;
  const canColor = HANH_COLORS[canDetail.hanh] || HANH_COLORS['Thổ'];
  const chiColor = HANH_COLORS[chiDetail.hanh] || HANH_COLORS['Thổ'];

  const pillarList = [
    { id: 'tru_nam', label: 'Trụ Năm', sub: 'Tổ Tiên / 1-16t' },
    { id: 'tru_thang', label: 'Trụ Tháng', sub: 'Cha Mẹ / 17-32t' },
    { id: 'tru_ngay', label: 'Trụ Ngày', sub: 'Bản Thân / 33-48t', isNhatChu: true },
    { id: 'tru_gio', label: 'Trụ Giờ', sub: 'Con Cái / 49t+' },
  ];

  const handleAskAI = (paraTitle) => {
    if (!onOpenChatWithQuestion) return;
    const q = `Xin phân tích chuyên sâu cho tôi về ${def.name} (${can} ${chi}) trong lá số Bát Tự, đặc biệt là phương diện: ${paraTitle}`;
    onOpenChatWithQuestion(q);
  };

  return (
    <section className="card-base p-5 sm:p-7 space-y-6 border-2 border-[#D4AF37]/50 shadow-md bg-gradient-to-b from-[#FFFDF9] to-[#FAF6EE] relative overflow-hidden transition-all duration-300">
      {/* Nền hoa văn trang nhã */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-accent/5 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />

      {/* Header thanh điều hướng 4 trụ */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-surface-border pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20 text-xs font-mono font-semibold flex items-center gap-1.5">
              <IconCompass size={14} className="text-primary animate-spin-slow" />
              Chi Tiết Từng Trụ
            </span>
            <span className="text-xs font-body text-text-secondary">
              Nhấn chọn để xem bình luận riêng
            </span>
          </div>
          <h3 className="font-heading text-xl sm:text-2xl font-bold text-primary mt-1 flex items-center gap-2">
            <span>{def.name}:</span>
            <span className="text-[#8B1C13] font-extrabold">{can} {chi}</span>
            <span className="text-xs sm:text-sm font-body px-2.5 py-0.5 rounded-full bg-accent/20 text-[#855B14] border border-accent/40 font-medium">
              {def.alias}
            </span>
          </h3>
        </div>

        {/* Thanh chuyển nhanh 4 Trụ (Tab Pill) */}
        <div className="flex items-center gap-1.5 p-1 bg-[#FAF5EE] rounded-btn border border-surface-border overflow-x-auto">
          {pillarList.map((p) => {
            const isActive = selectedPillarId === p.id;
            return (
              <button
                key={p.id}
                type="button"
                onClick={() => onSelectPillar(p.id)}
                className={`px-3 py-1.5 rounded-btn text-xs font-body font-medium transition-all whitespace-nowrap flex items-center gap-1.5 ${
                  isActive
                    ? 'bg-primary text-text-on-primary shadow-xs font-semibold'
                    : 'text-text-secondary hover:text-text-primary hover:bg-surface'
                }`}
              >
                <span>{p.label}</span>
                {p.isNhatChu && (
                  <span className={`text-[9px] px-1 py-0.2 rounded font-mono ${isActive ? 'bg-accent text-[#552218] font-bold' : 'bg-accent/20 text-accent'}`}>
                    Nhật Chủ
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>


      {/* Thông tin Cung Vị & Giai đoạn cuộc đời */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Cung Vị */}
        <div className="p-3.5 rounded-card bg-surface border border-surface-border space-y-1 shadow-2xs">
          <span className="text-[11px] font-mono uppercase text-text-secondary flex items-center gap-1.5">
            <IconHeartHandshake size={14} className="text-accent" />
            Cung Vị Đại Diện
          </span>
          <div className="font-heading font-bold text-base text-text-primary">
            {def.cungVi}
          </div>
          <p className="text-[11px] font-body text-text-secondary line-clamp-1">
            {def.vaiTroChinh}
          </p>
        </div>

        {/* Giai đoạn tuổi */}
        <div className="p-3.5 rounded-card bg-surface border border-surface-border space-y-1 shadow-2xs">
          <span className="text-[11px] font-mono uppercase text-text-secondary flex items-center gap-1.5">
            <IconClock size={14} className="text-accent" />
            Giai Đoạn Vận Trình
          </span>
          <div className="font-heading font-bold text-base text-text-primary">
            {def.giaiDoan.split(':')[0]}
          </div>
          <p className="text-[11px] font-body text-text-secondary">
            {def.giaiDoan.split(':')[1]?.trim() || def.giaiDoan}
          </p>
        </div>

        {/* Khí thế Can Chi */}
        <div className="p-3.5 rounded-card bg-surface border border-surface-border space-y-1 shadow-2xs">
          <span className="text-[11px] font-mono uppercase text-text-secondary flex items-center gap-1.5">
            <IconLayersLinked size={14} className="text-accent" />
            Thế Đứng Can - Chi
          </span>
          <div className="font-heading font-bold text-base text-text-primary">
            {theDungCanChi.theDung.split('(')[0]}
          </div>
          <p className="text-[11px] font-body text-text-secondary line-clamp-1">
            {theDungCanChi.sacThai || theDungCanChi.yNghia}
          </p>
        </div>

        {/* Thập Thần Thiên Can */}
        <div className="p-3.5 rounded-card bg-surface border border-accent/40 space-y-1 shadow-2xs">
          <span className="text-[11px] font-mono uppercase text-accent font-semibold flex items-center gap-1.5">
            <IconSparkles size={14} className="text-accent" />
            Thập Thần Thiên Can
          </span>
          <div className="font-heading font-bold text-base text-primary">
            {thapThanCan.name}
          </div>
          <p className="text-[11px] font-body text-text-secondary line-clamp-1">
            {thapThanCan.short} chiếu mệnh tại Can {can}
          </p>
        </div>
      </div>

      {/* Chi tiết Thiên Can & Địa Chi & Tàng Can */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Thẻ Thiên Can */}
        <div className={`p-4 rounded-card border ${canColor.border} ${canColor.bg} space-y-3`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-7 h-7 rounded-full bg-surface border border-surface-border flex items-center justify-center">
                <CanIcon size={16} className={canColor.text} />
              </span>
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-text-secondary block">
                  Thiên Can Lộ Khí
                </span>
                <span className="font-heading font-bold text-xl text-text-primary">
                  {can} <span className="text-xs font-normal text-text-secondary">({canDetail.amDuong} {canDetail.hanh})</span>
                </span>
              </div>
            </div>
            <span className={`text-xs font-body px-2.5 py-0.5 rounded-full border font-semibold ${canColor.badge}`}>
              {thapThanCan.name}
            </span>
          </div>
          <p className="text-xs font-body text-text-secondary leading-relaxed bg-surface/80 p-2.5 rounded-btn border border-surface-border/50">
            <strong>Tượng trưng:</strong> {canDetail.tuong}. {canDetail.tinhChat}
          </p>
        </div>

        {/* Thẻ Địa Chi & Tàng Can */}
        <div className={`p-4 rounded-card border ${chiColor.border} ${chiColor.bg} space-y-3`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-7 h-7 rounded-full bg-surface border border-surface-border flex items-center justify-center">
                <ChiIcon size={16} className={chiColor.text} />
              </span>
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-text-secondary block">
                  Địa Chi Thừa Khí
                </span>
                <span className="font-heading font-bold text-xl text-text-primary">
                  {chi} <span className="text-xs font-normal text-text-secondary">({chiDetail.conGiap} - {chiDetail.amDuong} {chiDetail.hanh})</span>
                </span>
              </div>
            </div>
            <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-surface border border-surface-border text-text-secondary">
              Tàng {tangCanWithThapThan.length} Can
            </span>
          </div>

          {/* Danh sách Tàng Can */}
          <div className="flex flex-wrap gap-1.5 pt-0.5">
            {tangCanWithThapThan.map((tc, idx) => (
              <span
                key={idx}
                className="text-[11px] font-body px-2 py-1 rounded-btn bg-surface border border-surface-border shadow-2xs flex items-center gap-1.5"
                title={`${tc.can} (${tc.hanh}): ${tc.thapThan.name} (${tc.vaiTro})`}
              >
                <span className="font-heading font-bold text-primary">{tc.can}</span>
                <span className="text-text-secondary font-mono text-[10px]">({tc.vaiTro})</span>
                <span className="text-[#855B14] font-semibold text-[10px]">→ {tc.thapThan.short}</span>
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* KHỐI BÌNH LUẬN PHÂN TÍCH CHUYÊN SÂU */}
      <div className="space-y-4 pt-2">
        <div className="flex items-center justify-between border-b border-surface-border pb-2.5">
          <h4 className="font-heading text-lg font-bold text-primary flex items-center gap-2">
            <IconBulb size={20} className="text-accent" />
            <span>Bình Luận Luận Giải Riêng Cho {def.name} ({can} {chi})</span>
          </h4>
          <span className="text-xs font-body text-text-secondary italic hidden sm:block">
            * Nguyên lý Tử Bình Chân Thuyên & Trích Thiên Tủy
          </span>
        </div>

        <div className="space-y-3.5">
          {paragraphs.map((p, idx) => (
            <div
              key={idx}
              className="p-4 rounded-card bg-surface border border-surface-border/80 shadow-2xs hover:border-accent/50 transition-all space-y-2 group"
            >
              <div className="flex items-center justify-between">
                <h5 className="font-heading text-base font-bold text-primary flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-accent/20 text-accent text-xs font-mono font-bold flex items-center justify-center">
                    {idx + 1}
                  </span>
                  <span>{p.title}</span>
                </h5>
                {onOpenChatWithQuestion && (
                  <button
                    type="button"
                    onClick={() => handleAskAI(p.title)}
                    className="text-[11px] font-body text-accent hover:text-primary flex items-center gap-1 px-2 py-1 rounded-btn hover:bg-[#FAF5EE] transition-colors"
                    title="Hỏi AI sâu hơn về phần này"
                  >
                    <IconMessages size={14} />
                    <span>Hỏi AI thêm</span>
                  </button>
                )}
              </div>
              <p className="font-body text-sm text-text-secondary leading-relaxed pl-7">
                {p.text}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Footer gợi ý chuyển tiếp */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-3.5 rounded-card bg-[#FAF5EE] border border-accent/40 text-xs font-body">
        <div className="flex items-center gap-2 text-text-secondary">
          <IconShieldCheck size={18} className="text-accent flex-shrink-0" />
          <span>
            Bạn đang xem phân tích chuyên sâu của <strong>{def.name}</strong>. Hãy click vào các trụ khác để đối chiếu sự tương hỗ giữa các thời khắc.
          </span>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {pillarList.map((p) => {
            if (p.id === selectedPillarId) return null;
            return (
              <button
                key={p.id}
                type="button"
                onClick={() => onSelectPillar(p.id)}
                className="px-2 py-1 rounded-btn bg-surface border border-surface-border hover:border-accent text-text-primary text-[11px] font-medium transition-colors flex items-center gap-1"
              >
                <span>Xem {p.label}</span>
                <IconArrowRight size={12} className="text-accent" />
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}
