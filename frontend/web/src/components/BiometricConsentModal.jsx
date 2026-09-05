import React, { useState } from 'react';
import { IconShieldCheck, IconLock, IconTrash, IconCheck, IconX } from '@tabler/icons-react';
import { visionService } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

export default function BiometricConsentModal({ isOpen, onClose, onConsentSuccess }) {
  const [agreed, setAgreed] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async () => {
    if (!agreed) {
      setError('Quý vị vui lòng đánh dấu đồng ý với các điều khoản bảo mật trước khi tiếp tục.');
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      await visionService.postConsent();
      onConsentSuccess();
    } catch (err) {
      setError('Không thể ghi nhận sự đồng ý lúc này. Vui lòng kiểm tra lại kết nối.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#3B2417]/50 backdrop-blur-xs animate-fadeIn">
      <div className="card-base max-w-lg w-full p-6 sm:p-8 space-y-5 bg-surface relative shadow-dropdown">
        {/* Nút đóng */}
        <button
          onClick={onClose}
          disabled={submitting}
          className="absolute top-4 right-4 text-text-secondary hover:text-text-primary p-1 rounded-btn focus:outline-none"
        >
          <IconX size={20} />
        </button>

        {/* Tiêu đề Modal */}
        <div className="flex items-center gap-3 border-b border-surface-border pb-4">
          <div className="w-11 h-11 rounded-card bg-[#FAF5EE] border border-accent/40 flex items-center justify-center text-accent flex-shrink-0">
            <IconShieldCheck size={24} stroke={1.75} />
          </div>
          <div>
            <h3 className="font-heading text-xl font-bold text-primary">
              Xác Nhận Quyền Riêng Tư Sinh Trắc Học
            </h3>
            <p className="font-body text-xs text-text-secondary mt-0.5">
              Cam kết bảo mật dữ liệu hình ảnh theo chuẩn bảo vệ thông tin cá nhân
            </p>
          </div>
        </div>

        {error && <ErrorMessage message={error} onClose={() => setError(null)} />}

        {/* Nội dung giải thích pháp lý & kỹ thuật */}
        <div className="space-y-3 font-body text-xs sm:text-sm text-text-primary leading-relaxed bg-[#FAF5EE]/60 p-4 rounded-card border border-surface-border">
          <div className="flex items-start gap-2.5">
            <IconLock size={18} className="text-accent flex-shrink-0 mt-0.5" />
            <p>
              <strong>Mục đích duy nhất:</strong> Hình ảnh bàn tay hoặc khuôn mặt chỉ được dùng để trích xuất đặc điểm nhân tướng học qua thuật toán thị giác máy tính.
            </p>
          </div>
          <div className="flex items-start gap-2.5">
            <IconTrash size={18} className="text-accent flex-shrink-0 mt-0.5" />
            <p>
              <strong>Quyền tự quyết:</strong> Quý vị có thể xóa vĩnh viễn hình ảnh bất kỳ lúc nào bằng nút <em>"Xóa ảnh này"</em> ngay trên giao diện. Hệ thống cũng tự động hủy dữ liệu tối đa sau 30 ngày.
            </p>
          </div>
        </div>

        {/* Checkbox Đồng ý */}
        <label className="flex items-start gap-3 cursor-pointer select-none pt-1">
          <input
            type="checkbox"
            checked={agreed}
            onChange={(e) => setAgreed(e.target.checked)}
            className="mt-1 w-4 h-4 text-primary rounded-btn border-surface-border focus:ring-accent focus:ring-1"
          />
          <span className="font-body text-xs sm:text-sm text-text-primary leading-snug">
            Tôi đã đọc, hiểu rõ và <strong>tự nguyện đồng ý</strong> cho phép hệ thống phân tích hình ảnh phục vụ thuật toán luận giải nhân tướng học.
          </span>
        </label>

        {/* Nút hành động */}
        <div className="flex flex-col-reverse sm:flex-row items-center justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            disabled={submitting}
            className="btn-outline w-full sm:w-auto px-5 py-2.5 text-sm"
          >
            Hủy Bỏ
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!agreed || submitting}
            className="btn-primary w-full sm:w-auto px-6 py-2.5 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? (
              <LoadingSpinner size="sm" color="white" text="Đang ghi nhận..." />
            ) : (
              <>
                <IconCheck size={18} />
                <span>Xác Nhận & Bắt Đầu</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
