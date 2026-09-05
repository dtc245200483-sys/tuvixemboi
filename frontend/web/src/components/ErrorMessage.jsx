import React from 'react';
import { IconAlertCircle, IconX } from '@tabler/icons-react';

/**
 * ErrorMessage - Khung thông báo lỗi chuẩn theo Design System:
 * - Tông màu đỏ trầm nhẹ nhàng, hài hòa nền kem (#FAF0EE, viền #E6C2BC, chữ #6B2B1F)
 * - Tuyệt đối không dùng đỏ tươi chói gắt
 */
export default function ErrorMessage({ message, onClose, className = '' }) {
  if (!message) return null;

  return (
    <div
      className={`bg-[#FAF0EE] border border-[#E6C2BC] rounded-btn p-3.5 flex items-start justify-between gap-3 text-sm text-primary shadow-subtle ${className}`}
      role="alert"
    >
      <div className="flex items-start gap-2.5">
        <IconAlertCircle size={20} className="text-primary flex-shrink-0 mt-0.5" stroke={1.75} />
        <div className="font-body leading-relaxed">{message}</div>
      </div>
      {onClose && (
        <button
          type="button"
          onClick={onClose}
          className="text-text-secondary hover:text-primary p-0.5 rounded transition-colors"
          aria-label="Đóng thông báo"
        >
          <IconX size={16} />
        </button>
      )}
    </div>
  );
}