import React, { useState, useEffect } from 'react';
import { IconSparkles, IconRefresh, IconAlertCircle, IconCrown } from '@tabler/icons-react';
import { quotaService } from '../services/api';
import QuotaExceededModal from './QuotaExceededModal';

/**
 * Dispatch custom event to notify all QuotaBadge instances to refresh
 */
export const notifyQuotaUpdated = () => {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('quota-updated'));
  }
};

export default function QuotaBadge({ refreshTrigger = 0, className = '' }) {
  const [quotaInfo, setQuotaInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const fetchQuota = async () => {
    try {
      setLoading(true);
      const res = await quotaService.getQuota();
      const data = res.data?.du_lieu || res.data;
      setQuotaInfo(data);
    } catch (err) {
      // Offline or error fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuota();
  }, [refreshTrigger]);

  useEffect(() => {
    const handleQuotaEvent = () => {
      fetchQuota();
    };
    if (typeof window !== 'undefined') {
      window.addEventListener('quota-updated', handleQuotaEvent);
    }
    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('quota-updated', handleQuotaEvent);
      }
    };
  }, []);

  if (!quotaInfo) return null;

  const isPremium = Boolean(quotaInfo.is_premium);
  const soConLai = quotaInfo.so_luot_con_lai ?? 50;
  const isLow = !isPremium && soConLai <= 5;
  const isOut = !isPremium && soConLai <= 0;

  return (
    <>
      <div
        onClick={() => {
          if (isOut || isLow || !isPremium) {
            setShowModal(true);
          }
        }}
        className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-body transition-all cursor-pointer ${
          isPremium
            ? 'bg-gradient-to-r from-[#FAF2E1] to-[#FFF9E6] border-[#D4AF37] text-[#6B140E] font-bold shadow-xs'
            : isOut
            ? 'bg-[#FAF0EE] border-[#E6C2BC] text-primary font-semibold hover:border-red-500'
            : isLow
            ? 'bg-[#FAF5EE] border-accent/60 text-primary font-medium hover:border-accent'
            : 'bg-[#FAF5EE] border-surface-border text-text-primary hover:border-accent/40'
        } ${className}`}
        title={
          isPremium
            ? 'Tài khoản Premium VIP: Không giới hạn an sao & AI'
            : `Hạn mức: ${quotaInfo.so_luot_da_dung || 0}/${quotaInfo.gioi_han_ngay || 50} lượt trong ngày. Bấm để xem chi tiết & Nâng cấp`
        }
      >
        {isPremium ? (
          <IconCrown size={15} className="text-[#D4AF37] flex-shrink-0" />
        ) : isOut ? (
          <IconAlertCircle size={15} className="text-primary flex-shrink-0 animate-pulse" />
        ) : (
          <IconSparkles size={15} className="text-accent flex-shrink-0" />
        )}

        <span className={isPremium ? 'text-[#6B140E]' : ''}>
          {isPremium
            ? '👑 Premium (Không giới hạn)'
            : isOut
            ? 'Hết lượt hôm nay (Nâng cấp VIP)'
            : `Còn ${soConLai} lượt hôm nay`}
        </span>

        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            fetchQuota();
          }}
          disabled={loading}
          className="ml-0.5 opacity-70 hover:opacity-100 transition-opacity focus:outline-none"
          aria-label="Làm mới hạn mức"
        >
          <IconRefresh size={13} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      <QuotaExceededModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        initialSeconds={quotaInfo.so_giay_con_lai_den_reset}
        onUpgraded={() => {
          fetchQuota();
        }}
      />
    </>
  );
}

