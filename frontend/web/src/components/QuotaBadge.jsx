import React, { useState, useEffect } from 'react';
import { IconSparkles, IconRefresh, IconAlertCircle } from '@tabler/icons-react';
import { quotaService } from '../services/api';

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

  const soConLai = quotaInfo.so_luot_con_lai ?? 50;
  const isLow = soConLai <= 5;
  const isOut = soConLai <= 0;

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-body transition-all ${
        isOut
          ? 'bg-[#FAF0EE] border-[#E6C2BC] text-primary font-semibold'
          : isLow
          ? 'bg-[#FAF5EE] border-accent/60 text-primary font-medium'
          : 'bg-[#FAF5EE] border-surface-border text-text-primary'
      } ${className}`}
      title={`Hạn mức: ${quotaInfo.so_luot_da_dung || 0}/${quotaInfo.gioi_han_ngay || 50} lượt trong ngày`}
    >
      {isOut ? (
        <IconAlertCircle size={15} className="text-primary flex-shrink-0" />
      ) : (
        <IconSparkles size={15} className="text-accent flex-shrink-0" />
      )}
      <span>
        {isOut
          ? 'Đã hết lượt hỏi hôm nay'
          : `Còn ${soConLai} lượt hỏi hôm nay`}
      </span>
      <button
        type="button"
        onClick={fetchQuota}
        disabled={loading}
        className="text-text-secondary hover:text-accent ml-0.5 transition-colors focus:outline-none"
        aria-label="Làm mới hạn mức"
      >
        <IconRefresh size={13} className={loading ? 'animate-spin' : ''} />
      </button>
    </div>
  );
}
