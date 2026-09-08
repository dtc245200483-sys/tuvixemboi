import React, { useEffect, useRef, useLayoutEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  IconSparkles,
  IconCompass,
  IconRefresh,
  IconAlertCircle,
  IconUser,
  IconHelpCircle,
  IconInfoCircle,
  IconArrowRight,
} from '@tabler/icons-react';

// Topic badges helper
const getSystemBadge = (heThong) => {
  switch (heThong) {
    case 'tu_vi':
      return { label: 'Tử Vi Đẩu Số', icon: IconSparkles, color: 'text-primary bg-[#FAF5EE] border-accent/40' };
    case 'bat_tu':
      return { label: 'Bát Tự Hà Lạc', icon: IconCompass, color: 'text-primary bg-[#FAF5EE] border-accent/40' };
    case 'kinh_dich':
      return { label: 'Kinh Dịch', icon: IconCompass, color: 'text-primary bg-[#FAF5EE] border-accent/40' };
    case 'nhan_tuong':
      return { label: 'Nhân Tướng Học', icon: IconSparkles, color: 'text-primary bg-[#FAF5EE] border-accent/40' };
    default:
      return { label: 'Trợ Lý Phong Thủy', icon: IconSparkles, color: 'text-text-secondary bg-surface border-surface-border' };
  }
};

const formatTime = (isoString) => {
  if (!isoString) return '';
  try {
    const d = new Date(isoString);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return '';
  }
};

export default function ChatHistoryList({
  messages = [],
  isSending = false,
  isLoadingHistory = false,
  hasMore = false,
  onLoadMore,
  onRetry,
  onSelectSampleQuestion,
}) {
  const navigate = useNavigate();
  const listContainerRef = useRef(null);
  const prevScrollHeightRef = useRef(0);
  const isPrependingRef = useRef(false);

  // Preserve scroll position when older messages are prepended
  useLayoutEffect(() => {
    if (isPrependingRef.current && listContainerRef.current) {
      const container = listContainerRef.current;
      const heightDiff = container.scrollHeight - prevScrollHeightRef.current;
      container.scrollTop += heightDiff;
      isPrependingRef.current = false;
    }
  }, [messages]);

  // Scroll to bottom on initial load or new message
  useEffect(() => {
    if (!isPrependingRef.current && listContainerRef.current) {
      const container = listContainerRef.current;
      // If user is reasonably near bottom, scroll down
      const isNearBottom =
        container.scrollHeight - container.scrollTop - container.clientHeight < 200;
      if (isNearBottom || messages.length <= 2) {
        container.scrollTop = container.scrollHeight;
      }
    }
  }, [messages, isSending]);

  // Handle infinite scroll upward
  const handleScroll = () => {
    if (!listContainerRef.current || isLoadingHistory || !hasMore) return;
    const container = listContainerRef.current;

    if (container.scrollTop < 60) {
      isPrependingRef.current = true;
      prevScrollHeightRef.current = container.scrollHeight;
      onLoadMore();
    }
  };

  const sampleQuestions = [
    'Năm nay công danh sự nghiệp của tôi có cơ hội thăng tiến không?',
    'Gieo giúp tôi một quẻ Kinh Dịch hỏi về việc hợp tác làm ăn.',
    'Phân tích cung Phu Thê và tình duyên của tôi.',
    'Đặc điểm khuôn mặt hoặc bàn tay của tôi nói lên điều gì về hậu vận?',
  ];

  return (
    <div
      ref={listContainerRef}
      onScroll={handleScroll}
      className="flex-1 overflow-y-auto px-3 sm:px-6 py-4 space-y-4 font-body"
    >
      {/* Loading older messages indicator */}
      {isLoadingHistory && (
        <div className="flex justify-center py-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface border border-surface-border text-xs text-text-secondary shadow-sm">
            <div className="w-3.5 h-3.5 border-2 border-accent border-t-transparent rounded-full animate-spin" />
            <span>Đang tải tin nhắn cũ hơn...</span>
          </div>
        </div>
      )}

      {/* Has more hint button */}
      {!isLoadingHistory && hasMore && messages.length > 0 && (
        <div className="flex justify-center py-1">
          <button
            type="button"
            onClick={() => {
              isPrependingRef.current = true;
              prevScrollHeightRef.current = listContainerRef.current?.scrollHeight || 0;
              onLoadMore();
            }}
            className="text-xs text-text-secondary hover:text-accent font-medium underline transition-colors"
          >
            Cuộn lên hoặc bấm để xem thêm tin nhắn cũ
          </button>
        </div>
      )}

      {/* Empty State */}
      {messages.length === 0 && !isLoadingHistory && (
        <div className="h-full min-h-[360px] flex flex-col items-center justify-center text-center max-w-xl mx-auto py-8 px-4">
          <div className="w-16 h-16 rounded-2xl bg-[#FAF5EE] border border-accent/40 flex items-center justify-center text-accent mb-4 shadow-sm">
            <IconCompass size={32} />
          </div>
          <h2 className="text-2xl sm:text-3xl font-body font-bold text-primary mb-2">
            Đàm Đạo Huyền Học
          </h2>
          <p className="text-sm text-text-secondary max-w-md mb-6 leading-relaxed">
            Hỏi đáp trực tiếp với AI tích hợp toàn diện 4 trụ cột: Tử Vi, Bát Tự, Kinh Dịch và Nhân Tướng Học.
          </p>

          <div className="w-full space-y-2 text-left">
            <div className="text-xs font-semibold uppercase tracking-wider text-text-secondary px-1">
              Câu hỏi gợi ý:
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {sampleQuestions.map((q, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => onSelectSampleQuestion(q)}
                  className="p-3 rounded-xl bg-surface hover:bg-[#FAF5EE] border border-surface-border hover:border-accent/60 text-xs text-text-primary text-left transition-all shadow-sm flex items-start justify-between gap-2 group"
                >
                  <span className="line-clamp-2">{q}</span>
                  <IconArrowRight size={14} className="text-text-secondary group-hover:text-accent flex-shrink-0 mt-0.5 transition-colors" />
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Message List */}
      {messages.map((msg) => {
        const isUser = msg.sender === 'user';
        const isSendingMsg = msg.status === 'sending';
        const isErrorMsg = msg.status === 'error';
        const badge = !isUser ? getSystemBadge(msg.he_thong) : null;
        const BadgeIcon = badge?.icon;

        if (isUser) {
          return (
            <div key={msg.id} className="flex justify-end">
              <div className="max-w-[85%] sm:max-w-[75%] space-y-1.5 text-right">
                <div
                  className={`inline-block text-left p-3.5 rounded-2xl rounded-tr-sm bg-[#FAF5EE] border border-accent/40 text-text-primary text-sm shadow-sm transition-opacity ${
                    isSendingMsg ? 'opacity-70' : 'opacity-100'
                  } ${isErrorMsg ? 'border-primary/60 bg-[#FAF0EE]' : ''}`}
                >
                  {/* Image attachment thumbnail if present */}
                  {msg.image_url && (
                    <div className="mb-2 rounded-lg overflow-hidden border border-surface-border max-w-[200px]">
                      <img
                        src={msg.image_url}
                        alt="Ảnh đính kèm"
                        className="w-full h-auto object-cover max-h-48"
                      />
                    </div>
                  )}
                  <p className="whitespace-pre-wrap leading-relaxed">{msg.noi_dung}</p>
                </div>

                <div className="flex items-center justify-end gap-1.5 text-[11px] text-text-secondary px-1">
                  <span>{formatTime(msg.created_at)}</span>
                  {isSendingMsg && (
                    <span className="italic text-accent">Đang gửi...</span>
                  )}
                  {isErrorMsg && (
                    <div className="inline-flex items-center gap-1 text-primary font-medium">
                      <IconAlertCircle size={13} />
                      <span>Lỗi gửi</span>
                      <button
                        type="button"
                        onClick={onRetry}
                        className="ml-1 underline hover:text-accent font-semibold inline-flex items-center gap-0.5"
                      >
                        <IconRefresh size={11} /> Gửi lại
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        }

        // AI Message
        return (
          <div key={msg.id} className="flex justify-start items-start gap-2.5 sm:gap-3">
            {/* AI Avatar */}
            <div className="w-8 h-8 rounded-full bg-[#FAF5EE] border border-surface-border text-accent flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
              <IconSparkles size={16} />
            </div>

            <div className="max-w-[90%] sm:max-w-[82%] space-y-1">
              {/* Header Badge */}
              <div className="flex items-center gap-2 flex-wrap">
                {badge && (
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md border text-[11px] font-medium font-body ${badge.color}`}
                  >
                    {BadgeIcon && <BadgeIcon size={12} />}
                    {badge.label}
                  </span>
                )}
                {msg.can_hoi_lai && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#FAF5EE] border border-accent/60 text-primary text-[11px] font-medium">
                    <IconHelpCircle size={12} />
                    Cần thêm thông tin
                  </span>
                )}
                {msg.chua_co_du_lieu && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#FAF5EE] border border-surface-border text-text-secondary text-[11px] font-medium">
                    <IconInfoCircle size={12} />
                    Chưa có dữ liệu sinh
                  </span>
                )}
                <span className="text-[11px] text-text-secondary ml-auto">
                  {formatTime(msg.created_at)}
                </span>
              </div>

              {/* Message Bubble */}
              <div
                className={`p-4 rounded-2xl rounded-tl-sm bg-surface border text-text-primary text-sm shadow-sm leading-relaxed whitespace-pre-wrap ${
                  msg.is_quota_notice
                    ? 'bg-[#FAF0EE] border-[#E6C2BC] text-primary'
                    : msg.can_hoi_lai
                    ? 'border-accent/60 bg-[#FAF5EE]/30'
                    : 'border-surface-border'
                }`}
              >
                {msg.noi_dung}

                {/* Call-to-action if missing birth data */}
                {msg.chua_co_du_lieu && (
                  <div className="mt-3 pt-3 border-t border-surface-border flex items-center justify-between">
                    <span className="text-xs text-text-secondary">
                      Thiết lập hồ sơ ngày giờ sinh để AI lấy dữ liệu lập lá số:
                    </span>
                    <button
                      type="button"
                      onClick={() => navigate('/birth-profile')}
                      className="ml-2 px-3 py-1.5 rounded-lg bg-primary hover:bg-[#552218] text-text-on-primary text-xs font-medium transition-all shadow-sm flex items-center gap-1 flex-shrink-0"
                    >
                      Nhập thông tin sinh
                      <IconArrowRight size={13} />
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}

      {/* Typing Indicator */}
      {isSending && (
        <div className="flex justify-start items-start gap-2.5 sm:gap-3">
          <div className="w-8 h-8 rounded-full bg-[#FAF5EE] border border-surface-border text-accent flex items-center justify-center flex-shrink-0 shadow-sm">
            <IconSparkles size={16} />
          </div>
          <div className="p-3.5 rounded-2xl rounded-tl-sm bg-surface border border-surface-border shadow-sm flex items-center gap-2">
            <div className="flex items-center gap-1 px-1">
              <span className="w-2 h-2 rounded-full bg-accent animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 rounded-full bg-accent animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 rounded-full bg-accent animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <span className="text-xs text-text-secondary font-body">
              Đang tra cứu tri thức & tổng hợp luận giải...
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
