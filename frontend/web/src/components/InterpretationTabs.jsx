import React, { useState, useMemo, useCallback } from 'react';
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
  IconInfoCircle,
  IconLoader2,
  IconCheck,
  IconMessages,
} from '@tabler/icons-react';
import TuViTopicSuggestions, { SUGGESTION_TOPICS } from './TuViTopicSuggestions';
import TuViAIChatModal from './TuViAIChatModal';
import { tuViService } from '../services/api';
import { CleanCommentView, extractCleanCommentText } from '../utils/textFormatter';
import { filterBatTuByPillar } from '../utils/batTuAnalyzer';

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

export default function InterpretationTabs({
  luanGiai,
  systemName = 'Huyền Học',
  isLoading = false,
  birthProfileId = null,
  chartData = null,
  onRetryGeneral = null,
  selectedPillarId = 'tru_ngay',
  onSelectPillar = null,
  tuTruData = null,
}) {
  // Trạng thái chủ đề chuyên sâu & Chat
  const [activeTopic, setActiveTopic] = useState(null);
  const [topicResults, setTopicResults] = useState({});
  const [loadingTopic, setLoadingTopic] = useState(null);
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Tabs mặc định (tổng quan)
  const [activeTab, setActiveTab] = useState(0);
  const [openAccordions, setOpenAccordions] = useState({ 0: true });

  const toggleAccordion = (index) => {
    setOpenAccordions((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  // Hàm xử lý chọn chủ đề gợi ý (Công danh, Con cái, Tình duyên...)
  const handleSelectTopic = useCallback(
    async (topicId, forceRetry = false) => {
      // Đóng khung chat khi bấm chủ đề
      setIsChatOpen(false);
      setActiveTopic(topicId);

      // Nếu đã có trong cache bộ nhớ client, thành công và không phải forceRetry -> hiển thị tức thì (0ms)
      const cached = topicResults[topicId];
      if (cached && cached.thanh_cong && cached.cau_tra_loi && !forceRetry) {
        return;
      }
      if (!birthProfileId) return;

      setLoadingTopic(topicId);
      try {
        const res = await tuViService.getTopicInterpretation(birthProfileId, topicId);
        const data = res.data?.du_lieu || res.data;
        const luanGiaiObj = data?.luan_giai;
        if (luanGiaiObj && luanGiaiObj.thanh_cong && luanGiaiObj.cau_tra_loi) {
          setTopicResults((prev) => ({
            ...prev,
            [topicId]: luanGiaiObj,
          }));
        } else {
          setTopicResults((prev) => ({
            ...prev,
            [topicId]: {
              thanh_cong: false,
              thong_bao: 'Hệ thống AI đang bận hoặc quá tải kết nối. Quý bạn vui lòng nhấn nút bên dưới để thử lại.',
              cau_tra_loi: null,
            },
          }));
        }
      } catch (err) {
        console.error(`Lỗi khi lấy luận giải chủ đề ${topicId}:`, err);
        setTopicResults((prev) => ({
          ...prev,
          [topicId]: {
            thanh_cong: false,
            thong_bao: 'Hệ thống AI đang bận kết nối. Quý bạn chỉ cần nhấn thử lại là được.',
            cau_tra_loi: null,
          },
        }));
      } finally {
        setLoadingTopic(null);
      }
    },
    [birthProfileId, topicResults]
  );

  // Trích xuất danh sách các mục luận giải tổng quan
  const isBatTu = useMemo(() => {
    return systemName.includes('Bát Tự') || Boolean(tuTruData);
  }, [systemName, tuTruData]);

  const generalSections = useMemo(() => {
    if (!luanGiai || luanGiai.thanh_cong === false) return [];

    const cauTraLoi = luanGiai.cau_tra_loi;
    if (!cauTraLoi) return [];

    // NẾU LÀ HỆ THỐNG BÁT TỰ TỨ TRỤ: Lọc theo Trụ được người dùng nhấp chọn
    if (isBatTu) {
      let rawText = '';
      if (typeof cauTraLoi === 'string') {
        rawText = cauTraLoi;
      } else if (typeof cauTraLoi === 'object' && cauTraLoi !== null) {
        rawText = cauTraLoi.noi_dung || cauTraLoi.content || cauTraLoi.tong_quan || '';
        if (!rawText) {
          const firstKey = Object.keys(cauTraLoi).find(k => !['ghi_chu_gioi_han', 'muc_do_tin_cay', 'he_thong', 'thanh_cong'].includes(k));
          if (firstKey) rawText = cauTraLoi[firstKey];
        }
      }

      const currentPillar = selectedPillarId || 'tru_ngay';
      const filteredContent = filterBatTuByPillar(rawText, currentPillar, tuTruData);

      const pillarTitleMap = {
        tru_ngay: 'Luận giải Trụ Ngày (Bản Mệnh Nhật Chủ & Hôn Nhân)',
        tru_thang: 'Luận giải Trụ Tháng (Đề Cương Lệnh Tháng & Đại Vận)',
        tru_nam: 'Luận giải Trụ Năm (Tổ Tiên Cội Nguồn & Ngũ Hành)',
        tru_gio: 'Luận giải Trụ Giờ (Con Cái Tử Tức & Hậu Vận)',
        all: 'Luận giải Toàn Cảnh Tứ Trụ Bát Tự (Đầy Đủ 4 Trụ)'
      };

      const title = pillarTitleMap[currentPillar] || 'Luận giải Bát Tự Tứ Trụ';

      return [
        {
          id: `bat-tu-${currentPillar}`,
          title,
          content: extractCleanCommentText(filteredContent),
        },
      ];
    }

    // NẾU LÀ TỬ VI HOẶC HỆ THỐNG KHÁC:
    if (Array.isArray(cauTraLoi)) {
      return cauTraLoi.map((item, idx) => ({
        id: `tab-${idx}`,
        title: item.chu_de || item.tieu_de || `Chủ đề ${idx + 1}`,
        content: extractCleanCommentText(item.noi_dung || item.content || item),
      })).filter(it => Boolean(it.content));
    }

    if (typeof cauTraLoi === 'object' && cauTraLoi !== null) {
      if (cauTraLoi.chu_de && (cauTraLoi.noi_dung || cauTraLoi.content)) {
        const list = [
          {
            id: 'main',
            title: cauTraLoi.chu_de,
            content: extractCleanCommentText(cauTraLoi.noi_dung || cauTraLoi.content),
          },
        ];
        if (cauTraLoi.loi_khuyen) {
          list.push({
            id: 'advice',
            title: 'Lời Khuyên Ứng Biến',
            content: extractCleanCommentText(cauTraLoi.loi_khuyen),
          });
        }
        return list;
      }

      const keys = Object.keys(cauTraLoi).filter(
        (k) => !['ghi_chu_gioi_han', 'muc_do_tin_cay', 'he_thong', 'thanh_cong', 'thong_bao', 'nguon_tri_thuc_da_dung'].includes(k)
      );

      if (keys.length > 0) {
        return keys.map((k) => {
          const val = cauTraLoi[k];
          let title = k.replace(/_/g, ' ').replace(/^./, (str) => str.toUpperCase());
          if (k === 'tong_quan') title = 'Luận giải tổng quan lá số Tử Vi trọn đời';
          if (k === 'su_nghiep') title = 'Sự Nghiệp & Công Danh';
          if (k === 'tinh_duyen') title = 'Tình Duyên & Gia Đạo';
          if (k === 'tai_loc') title = 'Tài Lộc & Điền Sản';
          if (k === 'suc_khoe') title = 'Sức Khỏe & Tật Ách';
          if (k === 'loi_khuyen') title = 'Phương Hướng Hóa Giải';

          const content = extractCleanCommentText(val);
          return { id: k, title, content };
        }).filter(it => Boolean(it.content));
      }
    }

    if (typeof cauTraLoi === 'string') {
      return [
        {
          id: 'text-main',
          title: 'Luận Giải Chi Tiết',
          content: extractCleanCommentText(cauTraLoi),
        },
      ];
    }

    return [];
  }, [luanGiai, isBatTu, selectedPillarId, tuTruData]);

  // Nội dung chủ đề đang chọn (nếu có chọn chủ đề gợi ý)
  const currentTopicData = activeTopic ? topicResults[activeTopic] : null;
  const currentTopicTitle = useMemo(() => {
    if (!activeTopic) return '';
    const found = SUGGESTION_TOPICS.find((t) => t.id === activeTopic);
    return found ? found.title : activeTopic;
  }, [activeTopic]);

  // Nội dung hiển thị của chủ đề (bóc tách sạch 100%, không bao giờ để sót JSON hay ký tự kỹ thuật)
  const topicContent = useMemo(() => {
    if (!currentTopicData || currentTopicData.thanh_cong === false) return '';
    const res = currentTopicData.cau_tra_loi;
    if (!res) return '';
    return extractCleanCommentText(res);
  }, [currentTopicData]);


  const sources = (currentTopicData || luanGiai)?.nguon_tri_thuc_da_dung || [];

  // Trường hợp đang nạp ban đầu
  if (isLoading && !luanGiai) {
    return (
      <div className="card-base p-6 text-center space-y-3 shadow-subtle animate-pulse bg-[#FAF5EE]/70 border border-accent/20">
        <div className="inline-block animate-spin rounded-full h-7 w-7 border-2 border-accent border-t-transparent mb-1"></div>
        <h4 className="font-heading font-bold text-primary text-base">Đang Kết Nối Tri Thức Luận Giải AI...</h4>
        <p className="text-xs text-text-secondary font-body max-w-md mx-auto">
          Bảng lá số tử vi đã sẵn sàng để quý vị tra cứu. Hệ thống đang tổng hợp bài luận giải chi tiết theo các cung chức năng.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full bg-white border border-[#D5C9B8] rounded-xl shadow-xs overflow-hidden my-6">
      {/* HEADER KHỐI LUẬN GIẢI & NÚT HỎI ĐÁP AI NẰM CÙNG HÀNG NGANG */}
      <div className="py-3 px-4 sm:px-5 bg-[#FAF6EE] border-b border-[#E2D9C8] flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <IconBook2 size={20} className="text-[#8B1C13] flex-shrink-0" />
            <h2 className="font-heading text-base sm:text-lg font-bold text-[#4A3B32]">
              Bản Luận Giải Chi Tiết
            </h2>
          </div>

          <span className="text-[#D5C9B8] hidden sm:inline">|</span>

          {/* NÚT HỎI ĐÁP AI THEO LÁ SỐ NẰM CÙNG HÀNG NGANG */}
          <button
            type="button"
            onClick={() => {
              setIsChatOpen((prev) => !prev);
              setActiveTopic(null);
            }}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shadow-xs cursor-pointer active:scale-95 ${
              isChatOpen
                ? 'bg-[#8B1C13] text-white border border-[#8B1C13] ring-2 ring-[#8B1C13]/30'
                : 'bg-white hover:bg-[#FAF5EE] text-[#8B1C13] border border-[#D5C9B8] hover:border-[#8B1C13]'
            }`}
            title="Mở trợ lý Hỏi Đáp AI theo lá số Tử Vi"
          >
            <IconMessages size={15} className={isChatOpen ? 'text-[#D4AF37]' : 'text-[#8B1C13]'} />
            <span>Hỏi đáp AI theo lá số</span>
            <IconSparkles size={13} className={isChatOpen ? 'text-[#D4AF37]' : 'text-[#D4AF37]'} />
          </button>
        </div>

        <span className="text-[11px] font-mono font-bold text-[#8B1C13] uppercase tracking-wider bg-[#FAF0E6] px-2.5 py-1 rounded-md border border-[#E2D9C8]">
          Tri Thức {systemName}
        </span>
      </div>

      <div className="p-4 sm:p-5 space-y-4">
        {/* THANH BANNER "GỢI Ý" 14 CHỦ ĐỀ CHUẨN GIAO DIỆN TUVI.VN */}
        {systemName.includes('Tử Vi') && (
          <TuViTopicSuggestions
            activeTopic={activeTopic}
            onSelectTopic={(tId) => handleSelectTopic(tId, activeTopic === tId)}
            loadingTopic={loadingTopic}
            isChatOpen={isChatOpen}
          />
        )}

        {/* THANH CHUYỂN NHANH TRỤ CHO BÁT TỰ TỨ TRỤ - NHẤP NGÀY LUẬN NGÀY, NHẤP THÁNG LUẬN THÁNG */}
        {isBatTu && onSelectPillar && !activeTopic && !isChatOpen && (
          <div className="p-3.5 rounded-xl bg-gradient-to-r from-[#FAF5EE] to-[#F5ECE0] border border-[#D5C9B8] space-y-2.5 shadow-2xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#8B1C13] animate-pulse" />
                <span className="text-xs font-heading font-bold text-[#8B1C13] uppercase tracking-wider">
                  Xem Luận Giải Chi Tiết Theo Từng Trụ:
                </span>
              </div>
              <span className="text-[11px] font-body text-text-secondary italic">
                (Nhấn Ngày luận theo Ngày, Tháng theo Tháng, Năm theo Năm, Giờ theo Giờ)
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
              {[
                { id: 'tru_ngay', label: 'Trụ Ngày', sub: 'Bản Thân / Nhật Chủ', badge: 'Nhật Chủ' },
                { id: 'tru_thang', label: 'Trụ Tháng', sub: 'Cha Mẹ / Đề Cương', badge: 'Lệnh Tháng' },
                { id: 'tru_nam', label: 'Trụ Năm', sub: 'Tổ Tiên / Gốc Rễ', badge: 'Cội Nguồn' },
                { id: 'tru_gio', label: 'Trụ Giờ', sub: 'Con Cái / Hậu Vận', badge: 'Quy Túc' },
                { id: 'all', label: 'Toàn Cảnh', sub: 'Cả 4 Trụ (Đầy Đủ)', badge: 'Tổng Thể' },
              ].map((p) => {
                const isActive = (selectedPillarId || 'tru_ngay') === p.id;
                return (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => onSelectPillar(p.id)}
                    className={`p-2 rounded-lg text-left transition-all duration-200 cursor-pointer border flex flex-col justify-between ${
                      isActive
                        ? 'bg-[#8B1C13] text-white border-[#8B1C13] shadow-md ring-2 ring-[#8B1C13]/30 scale-[1.02]'
                        : 'bg-white text-[#4A3B32] border-[#D5C9B8] hover:border-[#8B1C13] hover:bg-[#FAF5EE] hover:shadow-2xs'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1">
                      <span className="font-heading font-bold text-xs sm:text-sm">
                        {p.label}
                      </span>
                      <span className={`text-[9px] font-mono px-1.5 py-0.2 rounded font-semibold ${
                        isActive ? 'bg-[#D4AF37] text-white' : 'bg-[#FAF5EE] text-[#855B14] border border-[#D5C9B8]/50'
                      }`}>
                        {p.badge}
                      </span>
                    </div>
                    <span className={`text-[10px] font-body line-clamp-1 mt-0.5 ${
                      isActive ? 'text-[#FAF5EE]' : 'text-text-secondary'
                    }`}>
                      {p.sub}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

      {/* KHỐI CHAT HỎI ĐÁP AI NẾU ĐANG MỞ */}
      {isChatOpen && (
        <TuViAIChatModal
          birthProfileId={birthProfileId}
          chartData={chartData}
          onClose={() => setIsChatOpen(false)}
          isOpen={isChatOpen}
        />
      )}

      {/* TRƯỜNG HỢP 1: ĐANG CHỌN XEM MỘT CHỦ ĐỀ GỢI Ý */}
      {activeTopic && !isChatOpen && (
        <div className="space-y-4 animate-fadeIn">
          <div className="flex items-center justify-between gap-2 border-b border-surface-border/80 pb-2">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#8B0000]"></span>
              <h3 className="font-heading text-lg sm:text-xl font-bold text-primary">
                Luận Giải Chuyên Sâu: {currentTopicTitle}
              </h3>
            </div>
            <button
              type="button"
              onClick={() => setActiveTopic(null)}
              className="text-xs text-accent hover:underline font-body font-medium cursor-pointer"
            >
              ← Về Luận giải tổng quan
            </button>
          </div>

          {loadingTopic === activeTopic ? (
            <div className="p-8 text-center bg-[#FAF5EE]/60 rounded-card border border-surface-border space-y-3">
              <IconLoader2 size={24} className="animate-spin text-accent mx-auto" />
              <p className="font-body text-sm text-text-primary font-semibold">
                Đang phân tích phương diện {currentTopicTitle} qua tinh bàn Tử Vi...
              </p>
              <p className="text-xs text-text-secondary">
                Tốc độ xử lý được tối ưu bởi FreeLLMAPI Groq (phản hồi trong ~1 giây).
              </p>
            </div>
          ) : (!currentTopicData || currentTopicData.thanh_cong === false || !topicContent) ? (
            <div className="p-6 sm:p-8 rounded-card bg-[#FAF5EE] border border-[#8B0000]/20 text-center space-y-3 shadow-2xs">
              <div className="w-12 h-12 rounded-full bg-[#8B0000]/10 flex items-center justify-center mx-auto text-[#8B0000]">
                <IconSparkles size={24} />
              </div>
              <h4 className="font-heading font-bold text-primary text-base sm:text-lg">
                Hệ Thống AI Đang Bận Kết Nối
              </h4>
              <p className="text-xs sm:text-sm text-text-secondary font-body max-w-md mx-auto">
                {currentTopicData?.thong_bao || 'Kết nối dịch vụ AI tạm thời bị gián đoạn do lưu lượng truy cập cao. Quý bạn chỉ cần nhấn nút bên dưới là được.'}
              </p>
              <button
                type="button"
                onClick={() => handleSelectTopic(activeTopic, true)}
                className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full bg-[#8B0000] text-[#FFF8DC] hover:bg-[#6b0000] font-body font-semibold text-xs sm:text-sm transition-all shadow-md active:scale-95 cursor-pointer"
              >
                <span>🔄 Nhấn lại để tiếp tục ({currentTopicTitle})</span>
              </button>
            </div>
          ) : (
            <div className="p-6 rounded-card bg-[#FAF5EE]/40 border border-surface-border leading-relaxed font-body text-text-primary text-base space-y-3 shadow-2xs">
              <div className="flex items-center gap-2 text-primary font-heading text-lg font-bold border-b border-surface-border/40 pb-2.5">
                {React.createElement(getTopicIcon(currentTopicTitle), {
                  size: 20,
                  className: 'text-accent',
                })}
                <span>{currentTopicTitle}</span>
              </div>
              <CleanCommentView content={topicContent} />
            </div>
          )}
        </div>
      )}

      {/* TRƯỜNG HỢP 2: BÁO LỖI LUẬN GIẢI TỔNG QUAN (NẾU AI BẬN) */}
      {!activeTopic && !isChatOpen && !isLoading && luanGiai && (luanGiai.thanh_cong === false || generalSections.length === 0) && (
        <div className="p-6 sm:p-8 rounded-card bg-[#FAF5EE] border border-[#8B0000]/20 text-center space-y-3 shadow-2xs">
          <div className="w-12 h-12 rounded-full bg-[#8B0000]/10 flex items-center justify-center mx-auto text-[#8B0000]">
            <IconSparkles size={24} />
          </div>
          <h4 className="font-heading font-bold text-primary text-base sm:text-lg">
            Hệ Thống AI Đang Bận Kết Nối
          </h4>
          <p className="text-xs sm:text-sm text-text-secondary font-body max-w-md mx-auto">
            {luanGiai?.thong_bao || 'Bản luận giải tổng quan chưa kịp tải xong do AI đang bận. Quý bạn chỉ cần nhấn nút bên dưới là được.'}
          </p>
          {onRetryGeneral && (
            <button
              type="button"
              onClick={onRetryGeneral}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full bg-[#8B0000] text-[#FFF8DC] hover:bg-[#6b0000] font-body font-semibold text-xs sm:text-sm transition-all shadow-md active:scale-95 cursor-pointer"
            >
              <span>🔄 Nhấn lại để tạo luận giải tổng quan</span>
            </button>
          )}
        </div>
      )}

      {/* TRƯỜNG HỢP 3: HIỂN THỊ TỔNG QUAN BAN ĐẦU (KHI CHƯA CHỌN CHỦ ĐỀ RIÊNG HOẶC CHAT) */}
      {!activeTopic && !isChatOpen && generalSections && generalSections.length > 0 && (

        <>
          {/* DESKTOP VIEW: TAB BAR */}
          <div className="hidden md:block">
            <div className="flex border-b border-surface-border gap-2 overflow-x-auto pb-px">
              {generalSections.map((sec, idx) => {
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
            <div className="mt-6 p-6 rounded-card bg-[#FAF5EE]/40 border border-surface-border leading-relaxed font-body text-text-primary text-base space-y-4 shadow-2xs">
              <div className="flex items-center gap-2 text-primary font-heading text-xl font-bold border-b border-surface-border/40 pb-2.5">
                {React.createElement(getTopicIcon(generalSections[activeTab]?.title || ''), {
                  size: 22,
                  className: 'text-accent',
                })}
                <span>{generalSections[activeTab]?.title}</span>
              </div>
              <CleanCommentView content={generalSections[activeTab]?.content} />
            </div>
          </div>

          {/* MOBILE VIEW: ACCORDION */}
          <div className="md:hidden space-y-3">
            {generalSections.map((sec, idx) => {
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
                    <div className="p-4 pt-3 border-t border-surface-border bg-[#FAF5EE]/30">
                      <CleanCommentView content={sec.content} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}

      {/* NGUỒN TRI THỨC KHOA HỌC / KINH ĐIỂN ĐÃ SỬ DỤNG */}
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
    </div>
  );
}
