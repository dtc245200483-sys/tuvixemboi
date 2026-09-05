import React, { useState, useMemo } from 'react';
import {
  IconCompass,
  IconBriefcase,
  IconHeart,
  IconCoins,
  IconActivity,
  IconBulb,
  IconChevronDown,
  IconChevronUp,
  IconBook2,
  IconSparkles,
  IconInfoCircle
} from '@tabler/icons-react';

const TOPIC_ICONS = {
  'tong_quan': IconCompass,
  'tổng quan': IconCompass,
  'su_nghiep': IconBriefcase,
  'sự nghiệp': IconBriefcase,
  'công danh': IconBriefcase,
  'tinh_duyen': IconHeart,
  'tình duyên': IconHeart,
  'hôn nhân': IconHeart,
  'tai_loc': IconCoins,
  'tài lộc': IconCoins,
  'tiền tài': IconCoins,
  'suc_khoe': IconActivity,
  'sức khỏe': IconActivity,
  'loi_khuyen': IconBulb,
  'lời khuyên': IconBulb,
  'bien_phap': IconBulb,
};

function getTopicIcon(title) {
  const lower = (title || '').toLowerCase();
  for (const key of Object.keys(TOPIC_ICONS)) {
    if (lower.includes(key)) {
      return TOPIC_ICONS[key];
    }
  }
  return IconSparkles;
}

export default function InterpretationTabs({ luanGiai, systemName = 'Huyền Học' }) {
  // 1. Kiểm tra trường hợp hệ thống chưa có dữ liệu huấn luyện (Prompt 6.2/6.3)
  if (luanGiai?.chua_co_du_lieu) {
    return (
      <div className="bg-[#FAF5EE] border border-accent/40 rounded-card p-6 text-center space-y-3 shadow-subtle animate-fadeIn">
        <div className="w-12 h-12 mx-auto rounded-full bg-surface border border-accent/30 flex items-center justify-center text-accent">
          <IconSparkles size={24} />
        </div>
        <h3 className="font-heading text-xl font-bold text-primary">
          Tri Thức Đang Được Bổ Khuyết
        </h3>
        <p className="font-body text-sm text-text-secondary max-w-lg mx-auto leading-relaxed">
          Hệ thống <strong className="text-text-primary">{systemName}</strong> đang được các chuyên gia hoàn thiện kho tri thức kinh điển. Quý vị vui lòng quay lại sau để nhận bài luận giải chi tiết nhất.
        </p>
      </div>
    );
  }

  // 2. Trích xuất danh sách các mục luận giải { id, title, content }
  const sections = useMemo(() => {
    if (!luanGiai) return [];

    const cauTraLoi = luanGiai.cau_tra_loi || luanGiai;

    // Trường hợp 1: Trả về dạng mảng [{ chu_de, noi_dung }, ...]
    if (Array.isArray(cauTraLoi)) {
      return cauTraLoi.map((item, idx) => ({
        id: `tab-${idx}`,
        title: item.chu_de || item.tieu_de || `Chủ đề ${idx + 1}`,
        content: item.noi_dung || item.content || JSON.stringify(item),
      }));
    }

    // Trường hợp 2: Trả về object chứa các trường chủ đề
    if (typeof cauTraLoi === 'object' && cauTraLoi !== null) {
      // Nếu có chu_de và noi_dung trực tiếp
      if (cauTraLoi.chu_de && cauTraLoi.noi_dung) {
        const list = [
          {
            id: 'main',
            title: cauTraLoi.chu_de,
            content: cauTraLoi.noi_dung,
          },
        ];
        // Bổ sung các trường phụ nếu có
        if (cauTraLoi.loi_khuyen) {
          list.push({
            id: 'advice',
            title: 'Lời Khuyên Ứng Biến',
            content: cauTraLoi.loi_khuyen,
          });
        }
        return list;
      }

      // Nếu là object có các key chủ đề (tong_quan, su_nghiep, tinh_duyen...)
      const keys = Object.keys(cauTraLoi).filter(
        (k) => !['ghi_chu_gioi_han', 'muc_do_tin_cay', 'he_thong', 'thanh_cong'].includes(k)
      );

      if (keys.length > 0) {
        return keys.map((k) => {
          const val = cauTraLoi[k];
          let title = k
            .replace(/_/g, ' ')
            .replace(/^./, (str) => str.toUpperCase());
          if (k === 'tong_quan') title = 'Tổng Quan Mệnh Vận';
          if (k === 'su_nghiep') title = 'Sự Nghiệp & Công Danh';
          if (k === 'tinh_duyen') title = 'Tình Duyên & Gia Đạo';
          if (k === 'tai_loc') title = 'Tài Lộc & Điền Sản';
          if (k === 'suc_khoe') title = 'Sức Khỏe & Tật Ách';
          if (k === 'loi_khuyen') title = 'Phương Hướng Hóa Giải';

          const content = typeof val === 'string' ? val : JSON.stringify(val, null, 2);
          return { id: k, title, content };
        });
      }
    }

    // Trường hợp 3: Text chuỗi thuần
    if (typeof cauTraLoi === 'string') {
      return [
        {
          id: 'text-main',
          title: 'Luận Giải Chi Tiết',
          content: cauTraLoi,
        },
      ];
    }

    return [];
  }, [luanGiai]);

  const [activeTab, setActiveTab] = useState(0);
  const [openAccordions, setOpenAccordions] = useState({ 0: true });

  const toggleAccordion = (index) => {
    setOpenAccordions((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  if (!sections || sections.length === 0) {
    return (
      <div className="card-base p-6 text-center text-text-secondary font-body text-sm">
        Chưa có nội dung luận giải từ hệ thống.
      </div>
    );
  }

  const sources = luanGiai?.nguon_tri_thuc_da_dung || [];

  return (
    <div className="card-base p-6 sm:p-8 space-y-6">
      {/* Tiêu đề Khối Luận Giải */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-surface-border pb-4">
        <div>
          <span className="text-xs font-mono font-bold text-accent uppercase tracking-wider block">
            Tri Thức {systemName}
          </span>
          <h2 className="font-heading text-2xl font-bold text-primary mt-0.5">
            Bản Luận Giải Chi Tiết
          </h2>
        </div>
        {luanGiai?.tu_cache && (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#FAF5EE] border border-surface-border text-xs font-body text-text-secondary self-start sm:self-auto">
            <IconInfoCircle size={14} className="text-accent" />
            <span>Kết quả từ bộ nhớ đệm (Tối ưu phản hồi)</span>
          </span>
        )}
      </div>

      {/* 1. DESKTOP VIEW: TAB BAR */}
      <div className="hidden md:block">
        <div className="flex border-b border-surface-border gap-2 overflow-x-auto pb-px">
          {sections.map((sec, idx) => {
            const Icon = getTopicIcon(sec.title);
            const isActive = activeTab === idx;
            return (
              <button
                key={sec.id}
                type="button"
                onClick={() => setActiveTab(idx)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-body font-medium transition-all whitespace-nowrap border-b-2 rounded-t-btn ${
                  isActive
                    ? 'border-primary text-primary bg-[#FAF5EE]/60 font-semibold shadow-xs'
                    : 'border-transparent text-text-secondary hover:text-text-primary hover:border-surface-border'
                }`}
              >
                <Icon size={18} className={isActive ? 'text-accent' : 'text-text-secondary/70'} />
                <span>{sec.title}</span>
              </button>
            );
          })}
        </div>

        {/* Nội dung Tab đang chọn */}
        <div className="mt-6 p-6 rounded-card bg-[#FAF5EE]/40 border border-surface-border leading-relaxed font-body text-text-primary text-base space-y-4">
          <div className="flex items-center gap-2 text-primary font-heading text-xl font-bold">
            {React.createElement(getTopicIcon(sections[activeTab].title), {
              size: 22,
              className: 'text-accent',
            })}
            <span>{sections[activeTab].title}</span>
          </div>
          <div className="whitespace-pre-line text-sm sm:text-base leading-relaxed text-text-primary">
            {sections[activeTab].content}
          </div>
        </div>
      </div>

      {/* 2. MOBILE VIEW: ACCORDION */}
      <div className="md:hidden space-y-3">
        {sections.map((sec, idx) => {
          const Icon = getTopicIcon(sec.title);
          const isOpen = !!openAccordions[idx];
          return (
            <div
              key={sec.id}
              className="border border-surface-border rounded-card bg-surface overflow-hidden transition-all shadow-subtle"
            >
              <button
                type="button"
                onClick={() => toggleAccordion(idx)}
                className="w-full flex items-center justify-between p-4 text-left font-body text-sm font-semibold text-text-primary bg-surface hover:bg-[#FAF5EE]/50 transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <Icon size={18} className="text-accent flex-shrink-0" />
                  <span>{sec.title}</span>
                </div>
                {isOpen ? (
                  <IconChevronUp size={18} className="text-text-secondary" />
                ) : (
                  <IconChevronDown size={18} className="text-text-secondary" />
                )}
              </button>
              {isOpen && (
                <div className="p-4 pt-2 border-t border-surface-border bg-[#FAF5EE]/30 text-sm font-body text-text-primary leading-relaxed whitespace-pre-line">
                  {sec.content}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* 3. NGUỒN TRI THỨC KHOA HỌC / KINH ĐIỂN ĐÃ SỬ DỤNG */}
      {sources && sources.length > 0 && (
        <div className="pt-4 border-t border-surface-border/70 flex flex-wrap items-center gap-2 text-xs font-body text-text-secondary">
          <IconBook2 size={15} className="text-accent flex-shrink-0" />
          <span className="font-medium text-text-primary">Kinh thư đối chiếu:</span>
          {sources.map((src, i) => (
            <span
              key={i}
              className="px-2.5 py-0.5 rounded-full bg-[#FAF5EE] border border-surface-border text-[#552218]"
            >
              {src.ten || src.id || 'Cổ tịch chuẩn hóa'}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
