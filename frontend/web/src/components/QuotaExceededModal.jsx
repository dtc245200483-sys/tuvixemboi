import React, { useState, useEffect } from 'react';
import {
  IconAlertTriangle,
  IconClock,
  IconCrown,
  IconSparkles,
  IconCheck,
  IconX,
  IconLoader2,
  IconFlame,
  IconInfinity
} from '@tabler/icons-react';
import { quotaService } from '../services/api';
import { notifyQuotaUpdated } from './QuotaBadge';

export default function QuotaExceededModal({
  isOpen,
  onClose,
  initialSeconds = null,
  onUpgraded = null,
}) {
  const [secondsLeft, setSecondsLeft] = useState(() => {
    if (initialSeconds && initialSeconds > 0) return initialSeconds;
    const now = new Date();
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);
    return Math.max(0, Math.floor((tomorrow - now) / 1000));
  });

  const [isUpgrading, setIsUpgrading] = useState(false);
  const [upgradeSuccess, setUpgradeSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Live countdown timer ticking down every second
  useEffect(() => {
    if (!isOpen) return;

    const timer = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          notifyQuotaUpdated();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isOpen]);

  if (!isOpen) return null;

  const hours = String(Math.floor(secondsLeft / 3600)).padStart(2, '0');
  const minutes = String(Math.floor((secondsLeft % 3600) / 60)).padStart(2, '0');
  const seconds = String(secondsLeft % 60).padStart(2, '0');

  const handleUpgrade = async () => {
    setIsUpgrading(true);
    setErrorMsg(null);
    try {
      await quotaService.upgradePremium();
      setUpgradeSuccess(true);
      notifyQuotaUpdated();
      if (onUpgraded) {
        onUpgraded();
      }
      setTimeout(() => {
        onClose();
        setUpgradeSuccess(false);
      }, 2000);
    } catch (err) {
      console.error('Lỗi nâng cấp Premium:', err);
      setErrorMsg(err.response?.data?.loi || 'Không thể nâng cấp lúc này. Vui lòng thử lại sau.');
    } finally {
      setIsUpgrading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-fadeIn">
      <div className="relative w-full max-w-lg bg-[#FAF6EE] border border-[#D4AF37]/50 rounded-2xl shadow-2xl overflow-hidden text-[#2C2420]">
        {/* Nút đóng */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-full text-[#7D6B58] hover:text-[#6B140E] hover:bg-black/5 transition-colors focus:outline-none z-10"
        >
          <IconX size={20} />
        </button>

        {/* Header viền mạ vàng */}
        <div className="bg-gradient-to-r from-[#6B140E] via-[#8B1C13] to-[#552218] text-white p-6 sm:p-7 relative">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-white/10 border border-[#D4AF37]/40 flex items-center justify-center text-[#D4AF37] flex-shrink-0 shadow-inner">
              <IconAlertTriangle size={28} />
            </div>
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#D4AF37]/20 border border-[#D4AF37]/40 text-[11px] font-bold text-[#F4D068] uppercase tracking-wider mb-1">
                <IconFlame size={12} />
                <span>Đã Hết Lượt Sử Dụng Hôm Nay</span>
              </div>
              <h3 className="font-heading text-xl sm:text-2xl font-bold tracking-wide">
                Hết Lượt An Sao Lập Lá Số
              </h3>
            </div>
          </div>
        </div>

        {/* Nội dung chính */}
        <div className="p-6 space-y-6">
          {upgradeSuccess ? (
            <div className="py-8 text-center space-y-3 animate-fadeIn">
              <div className="w-16 h-16 mx-auto rounded-full bg-[#D4AF37]/20 border-2 border-[#D4AF37] flex items-center justify-center text-[#D4AF37]">
                <IconCrown size={36} />
              </div>
              <h4 className="font-heading text-2xl font-bold text-[#6B140E]">
                Chúc Mừng Bạn Đã Lên Premium VIP!
              </h4>
              <p className="text-xs text-[#5D4E3C] max-w-sm mx-auto">
                Hạn mức của bạn đã được nâng lên <strong>Không Giới Hạn</strong>. Bạn có thể an sao lập lá số và luận giải AI ngay bây giờ.
              </p>
            </div>
          ) : (
            <>
              {/* KHỐI 1: ĐỒNG HỒ ĐẾM NGƯỢC HỒI LƯỢT */}
              <div className="bg-white rounded-xl p-4 border border-[#E2D9C8] shadow-xs text-center space-y-2">
                <div className="flex items-center justify-center gap-2 text-xs font-bold uppercase tracking-wider text-[#7D6B58]">
                  <IconClock size={15} className="text-[#8B1C13]" />
                  <span>Thời Gian Chờ Hồi Lượt Miễn Phí (00:00)</span>
                </div>
                <div className="flex items-center justify-center gap-2 font-mono text-2xl sm:text-3xl font-black text-[#6B140E]">
                  <span className="bg-[#FAF5EE] px-3 py-1.5 rounded-lg border border-[#D5C9B8]">
                    {hours}
                  </span>
                  <span className="text-[#A58E74]">:</span>
                  <span className="bg-[#FAF5EE] px-3 py-1.5 rounded-lg border border-[#D5C9B8]">
                    {minutes}
                  </span>
                  <span className="text-[#A58E74]">:</span>
                  <span className="bg-[#FAF5EE] px-3 py-1.5 rounded-lg border border-[#D5C9B8]">
                    {seconds}
                  </span>
                </div>
                <p className="text-[11px] text-[#7D6B58]">
                  Hệ thống tự động cấp lại <strong>50 lượt miễn phí</strong> vào đúng 00:00 mỗi ngày.
                </p>
              </div>

              {/* KHỐI 2: NÂNG CẤP PREMIUM VIP (KHÔNG CẦN CHỜ ĐỢI) */}
              <div className="relative bg-gradient-to-b from-[#FFFDF9] to-[#FAF2E1] border-2 border-[#D4AF37] rounded-xl p-5 shadow-md space-y-4">
                <div className="absolute -top-3 right-4 px-3 py-0.5 rounded-full bg-gradient-to-r from-[#D4AF37] to-[#B38F26] text-white text-[10px] font-bold uppercase tracking-wider shadow-xs flex items-center gap-1">
                  <IconSparkles size={11} />
                  <span>Được Khuyên Dùng</span>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-[#6B140E] text-[#D4AF37] flex items-center justify-center flex-shrink-0 shadow-sm">
                    <IconCrown size={22} />
                  </div>
                  <div>
                    <h4 className="font-heading text-lg font-bold text-[#6B140E]">
                      Gói Huyền Học Premium VIP
                    </h4>
                    <p className="text-xs text-[#5D4E3C]">
                      Mở khóa toàn bộ giới hạn - Sử dụng không chờ đợi
                    </p>
                  </div>
                </div>

                <ul className="space-y-2 text-xs text-[#3D322B]">
                  <li className="flex items-center gap-2">
                    <IconInfinity size={16} className="text-[#B38F26] flex-shrink-0" />
                    <span><strong>Không giới hạn</strong> số lần An Sao Lập Lá Số Tử Vi & Bát Tự</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <IconCheck size={16} className="text-emerald-700 flex-shrink-0" />
                    <span>Hỏi đáp Trợ lý Huyền học AI không giới hạn</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <IconCheck size={16} className="text-emerald-700 flex-shrink-0" />
                    <span>Ưu tiên băng thông & tốc độ phản hồi cao nhất</span>
                  </li>
                </ul>

                {errorMsg && (
                  <p className="text-xs text-red-600 font-medium">{errorMsg}</p>
                )}

                <button
                  type="button"
                  onClick={handleUpgrade}
                  disabled={isUpgrading}
                  className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-[#6B140E] via-[#8B1C13] to-[#552218] hover:from-[#552218] hover:to-[#431A12] text-white text-sm font-bold shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 active:scale-98 cursor-pointer disabled:opacity-75"
                >
                  {isUpgrading ? (
                    <>
                      <IconLoader2 size={18} className="animate-spin text-[#D4AF37]" />
                      <span>Đang kích hoạt gói VIP...</span>
                    </>
                  ) : (
                    <>
                      <IconCrown size={18} className="text-[#D4AF37]" />
                      <span>Nâng Cấp Premium Ngay</span>
                    </>
                  )}
                </button>
              </div>

              {/* Nút chờ đợi */}
              <div className="pt-1 text-center">
                <button
                  type="button"
                  onClick={onClose}
                  className="text-xs text-[#7D6B58] hover:text-[#6B140E] underline transition-colors"
                >
                  Tôi sẽ đợi đến 00:00 ngày mai để nhận lượt miễn phí
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
