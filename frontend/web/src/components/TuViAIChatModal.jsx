import React, { useState, useRef, useEffect } from 'react';
import {
  IconMessages,
  IconSend,
  IconSparkles,
  IconX,
  IconUser,
  IconLoader2,
  IconShieldCheck,
  IconBulb,
} from '@tabler/icons-react';
import { tuViService } from '../services/api';
import { CleanCommentView } from '../utils/textFormatter';

const QUICK_QUESTIONS = [
  'Năm 2026 này công danh sự nghiệp của tôi có cơ hội thăng tiến không?',
  'Cung Phu Thê của tôi cần lưu ý gì để giữ gìn gia đạo êm ấm?',
  'Tài vận và kinh tế trong giai đoạn này nên tích lũy hay đầu tư?',
  'Cung Tật Ách nhắc nhở tôi cần chú trọng dưỡng sinh phương diện nào?',
  'Cách cục Mệnh Thân của tôi phù hợp phát triển trong lĩnh vực gì nhất?',
];

export default function TuViAIChatModal({
  birthProfileId,
  chartData,
  onClose,
  isOpen = true,
  initialQuestion = null,
}) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'ai',
      text: `Kính chào quý bạn! Tôi là Trợ lý Luận giải Tử Vi & Bát Tự AI. Tôi đã nắm rõ thông tin lá số của ${
        chartData?.userName || 'Mệnh chủ'
      } (${chartData?.napAmVal || 'Bản mệnh'}, ${
        chartData?.cucVal || 'Cục'
      }). Xin mời quý bạn đặt câu hỏi cụ thể về bất kỳ phương diện nào trong lá số.`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputVal, setInputVal] = useState('');
  const [isSending, setIsSending] = useState(false);
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);
  const hasSentInitialRef = useRef(false);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 150);
      if (initialQuestion && !hasSentInitialRef.current) {
        hasSentInitialRef.current = true;
        handleSend(initialQuestion);
      }
    }
  }, [isOpen, initialQuestion]);

  const handleSend = async (textToSend) => {
    const text = (textToSend || inputVal).trim();
    if (!text || isSending || !birthProfileId) return;

    const userMsg = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputVal('');
    setIsSending(true);

    try {
      const res = await tuViService.chatWithChart(birthProfileId, text);
      const isSuccess = res.data?.thanh_cong;
      const data = res.data?.du_lieu || res.data;

      if (isSuccess === false) {
        const errorMsg = {
          id: `ai-err-${Date.now()}`,
          sender: 'ai',
          text: 'Hệ thống AI đang bận kết nối hoặc quá tải lượt yêu cầu. Quý bạn chỉ cần nhấn nút bên dưới để gửi lại câu hỏi.',
          isError: true,
          lastQuestion: text,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, errorMsg]);
      } else {
        const aiReply =
          data?.tra_loi ||
          data?.chi_tiet?.cau_tra_loi?.noi_dung ||
          'Hệ thống đã ghi nhận câu hỏi và phân tích xong lá số của bạn.';

        const aiMsg = {
          id: `ai-${Date.now()}`,
          sender: 'ai',
          text: aiReply,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, aiMsg]);
      }
    } catch (err) {
      console.error('Lỗi khi gửi câu hỏi Tử Vi AI:', err);
      const errorMsg = {
        id: `ai-err-${Date.now()}`,
        sender: 'ai',
        text: 'Hệ thống AI đang bận kết nối hoặc quá tải lượt yêu cầu. Quý bạn chỉ cần nhấn nút bên dưới để gửi lại câu hỏi.',
        isError: true,
        lastQuestion: text,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="rounded-card border border-[#B3261E]/40 bg-surface shadow-card overflow-hidden my-4 transition-all animate-fadeIn">
      {/* HEADER KHỐI CHAT */}
      <div className="px-4 sm:px-6 py-3.5 bg-gradient-to-r from-[#6B140E] via-[#8B1C13] to-[#6B140E] text-[#FAF5EE] flex items-center justify-between border-b border-[#D4AF37]/30">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-[#FAF5EE]/15 flex items-center justify-center text-[#D4AF37] border border-[#D4AF37]/40 shadow-xs">
            <IconSparkles size={18} />
          </div>
          <div>
            <h3 className="font-heading text-base sm:text-lg font-bold text-[#FAF5EE] flex items-center gap-2">
              <span>Hỏi Đáp AI Theo Lá Số Tử Vi</span>
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#D4AF37]/20 text-[#D4AF37] font-body border border-[#D4AF37]/30">
                Trực tuyến
              </span>
            </h3>
            <p className="text-xs text-[#FAF5EE]/80 font-body hidden sm:block">
              Phân tích chuyên sâu cung, sao, vận hạn cho đương số {chartData?.userName || 'Mệnh chủ'}
            </p>
          </div>
        </div>

        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-full hover:bg-white/15 text-[#FAF5EE] transition-colors"
            title="Đóng khung chat"
          >
            <IconX size={18} />
          </button>
        )}
      </div>

      {/* GỢI Ý CÂU HỎI NHANH */}
      <div className="px-4 py-2.5 bg-[#FAF5EE] border-b border-surface-border flex items-center gap-2 overflow-x-auto text-xs font-body">
        <div className="flex items-center gap-1 text-accent font-semibold flex-shrink-0">
          <IconBulb size={15} />
          <span>Gợi ý hỏi:</span>
        </div>
        <div className="flex items-center gap-2">
          {QUICK_QUESTIONS.map((q, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSend(q)}
              disabled={isSending}
              className="px-2.5 py-1 rounded-full bg-white border border-accent/25 hover:border-accent hover:bg-accent/5 text-text-primary whitespace-nowrap transition-all"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* DANH SÁCH TIN NHẮN */}
      <div className="p-4 sm:p-6 space-y-4 max-h-[420px] min-h-[260px] overflow-y-auto bg-[#FDFBF7]/60">
        {messages.map((m) => {
          const isAi = m.sender === 'ai';
          return (
            <div
              key={m.id}
              className={`flex items-start gap-2.5 ${isAi ? 'justify-start' : 'justify-end'}`}
            >
              {isAi && (
                <div className="w-8 h-8 rounded-full bg-[#8B1C13] text-[#D4AF37] flex items-center justify-center flex-shrink-0 border border-[#D4AF37]/30 shadow-2xs mt-0.5">
                  <IconSparkles size={16} />
                </div>
              )}

              <div
                className={`max-w-[85%] sm:max-w-[78%] rounded-2xl p-3.5 sm:p-4 text-xs sm:text-sm font-body leading-relaxed shadow-subtle ${
                  isAi
                    ? 'bg-white text-text-primary border border-surface-border rounded-tl-xs'
                    : 'bg-[#8B1C13] text-white rounded-tr-xs'
                }`}
              >
                {isAi && !m.isError ? (
                  <CleanCommentView content={m.text} />
                ) : (
                  <div className={`whitespace-pre-line leading-relaxed ${m.isError ? 'text-[#8B1C13] font-medium' : ''}`}>
                    {m.text}
                  </div>
                )}
                {m.isError && m.lastQuestion && (
                  <button
                    type="button"
                    onClick={() => handleSend(m.lastQuestion)}
                    disabled={isSending}
                    className="mt-2.5 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#8B1C13] text-[#FFF8DC] text-xs font-semibold hover:bg-[#6b140e] transition-all cursor-pointer shadow-xs active:scale-95"
                  >
                    <span>🔄 Nhấn để gửi lại câu hỏi</span>
                  </button>
                )}
                <div
                  className={`text-[10px] mt-1 text-right ${
                    isAi ? 'text-text-secondary/70' : 'text-white/70'
                  }`}
                >
                  {m.time}
                </div>
              </div>

              {!isAi && (
                <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-700 flex items-center justify-center flex-shrink-0 shadow-2xs mt-0.5">
                  <IconUser size={16} />
                </div>
              )}
            </div>
          );
        })}

        {isSending && (
          <div className="flex items-center gap-2.5 justify-start animate-fadeIn">
            <div className="w-8 h-8 rounded-full bg-[#8B1C13] text-[#D4AF37] flex items-center justify-center flex-shrink-0 border border-[#D4AF37]/30 shadow-2xs">
              <IconSparkles size={16} />
            </div>
            <div className="bg-white border border-surface-border rounded-2xl rounded-tl-xs p-3.5 text-xs sm:text-sm text-text-secondary flex items-center gap-2 shadow-subtle">
              <IconLoader2 size={16} className="animate-spin text-accent" />
              <span>Trợ lý AI đang tra cứu tinh bàn và tổng hợp luận giải...</span>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* CAM KẾT BẢO MẬT & ĐẠO ĐỨC NỘI DUNG */}
      <div className="px-4 py-1.5 bg-[#FAF5EE] border-t border-surface-border/60 flex items-center justify-between text-[11px] text-text-secondary font-body">
        <div className="flex items-center gap-1.5 text-green-800">
          <IconShieldCheck size={14} className="text-green-600" />
          <span>Nội dung được kiểm duyệt an toàn, mang định hướng tích cực & dưỡng sinh.</span>
        </div>
        <span className="hidden sm:inline text-text-secondary/60">Tử Vi Đẩu Số Toàn Thư</span>
      </div>

      {/* KHUNG NHẬP CÂU HỎI */}
      <div className="p-3 sm:p-4 bg-white border-t border-surface-border">
        <div className="flex items-center gap-2">
          <textarea
            ref={inputRef}
            rows={1}
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Nhập câu hỏi về lá số (VD: năm nay đầu tư được không, gia đạo, công việc...)"
            disabled={isSending}
            className="flex-1 resize-none rounded-btn border border-surface-border px-3.5 py-2 text-xs sm:text-sm font-body text-text-primary focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent bg-surface transition-all placeholder:text-text-secondary/60 max-h-24 min-h-[38px]"
          />
          <button
            type="button"
            onClick={() => handleSend()}
            disabled={!inputVal.trim() || isSending}
            className="px-4 py-2 rounded-btn bg-[#8B1C13] hover:bg-[#A32217] disabled:opacity-40 disabled:cursor-not-allowed text-white font-body font-semibold text-xs sm:text-sm flex items-center gap-1.5 transition-all shadow-xs active:scale-95 flex-shrink-0"
          >
            {isSending ? (
              <IconLoader2 size={16} className="animate-spin" />
            ) : (
              <IconSend size={16} />
            )}
            <span className="hidden sm:inline">Gửi</span>
          </button>
        </div>
      </div>
    </div>
  );
}
