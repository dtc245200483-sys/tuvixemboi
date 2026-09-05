import React, { useState, useEffect } from 'react';
import { IconX, IconUser, IconCalendar, IconClock, IconCheck, IconAlertCircle } from '@tabler/icons-react';
import { birthProfileService } from '../../services/api';

export default function EditBirthProfileModal({ profile, isOpen, onClose, onSuccess }) {
  const [hoTen, setHoTen] = useState('');
  const [gioiTinh, setGioiTinh] = useState('nam');
  const [ngaySinh, setNgaySinh] = useState('');
  const [gioSinh, setGioSinh] = useState(12);
  const [phutSinh, setPhutSinh] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (profile) {
      setHoTen(profile.ho_ten || '');
      setGioiTinh(profile.gioi_tinh || 'nam');
      setNgaySinh(profile.ngay_sinh_duong || '');
      setGioSinh(profile.gio_sinh ?? 12);
      setPhutSinh(profile.phut_sinh ?? 0);
      setError(null);
    }
  }, [profile]);

  if (!isOpen || !profile) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!hoTen.trim()) {
      setError('Vui lòng nhập họ và tên');
      return;
    }

    try {
      setLoading(true);
      await birthProfileService.update(profile.id, {
        ho_ten: hoTen.trim(),
        gioi_tinh: gioiTinh,
        ngay_sinh_duong: ngaySinh || profile.ngay_sinh_duong,
        gio_sinh: Number(gioSinh),
        phut_sinh: Number(phutSinh),
      });
      if (onSuccess) {
        onSuccess();
      }
      onClose();
    } catch (err) {
      const msg =
        err.response?.data?.loi ||
        err.response?.data?.detail ||
        'Không thể cập nhật hồ sơ. Vui lòng thử lại.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#3B2417]/50 backdrop-blur-xs font-body animate-fade-in">
      <div className="card-base w-full max-w-lg p-6 sm:p-7 shadow-elevated border border-surface-border bg-surface relative">
        <button
          type="button"
          onClick={onClose}
          disabled={loading}
          className="absolute top-5 right-5 text-text-secondary hover:text-text-primary p-1 rounded-full transition-colors focus:outline-none"
        >
          <IconX size={20} />
        </button>

        <div className="mb-5 space-y-1">
          <h3 className="font-heading text-xl sm:text-2xl font-bold text-primary">
            Chỉnh Sửa Hồ Sơ Mệnh Chủ
          </h3>
          <p className="text-xs text-text-secondary">
            Cập nhật lại thông tin để hệ thống an sao và lập lá số chính xác
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-[#FAF0EE] border border-[#E6C2BC] text-primary text-xs flex items-center gap-2">
            <IconAlertCircle size={16} className="flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Họ tên */}
          <div className="space-y-1">
            <label className="block text-xs font-semibold text-text-primary">
              Họ và tên <span className="text-primary">*</span>
            </label>
            <input
              type="text"
              value={hoTen}
              onChange={(e) => setHoTen(e.target.value)}
              className="input-field text-sm"
              placeholder="VD: Nguyễn Văn An"
              required
            />
          </div>

          {/* Giới tính */}
          <div className="space-y-1">
            <label className="block text-xs font-semibold text-text-primary">
              Giới tính (ảnh hưởng đến chiều an sao Nam/Nữ)
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setGioiTinh('nam')}
                className={`py-2 px-3 rounded-btn border text-xs font-medium transition-all ${
                  gioiTinh === 'nam'
                    ? 'bg-[#FAF5EE] border-accent text-primary font-bold shadow-xs'
                    : 'bg-surface border-surface-border text-text-secondary hover:border-accent/40'
                }`}
              >
                Nam Mạng
              </button>
              <button
                type="button"
                onClick={() => setGioiTinh('nu')}
                className={`py-2 px-3 rounded-btn border text-xs font-medium transition-all ${
                  gioiTinh === 'nu'
                    ? 'bg-[#FAF5EE] border-accent text-primary font-bold shadow-xs'
                    : 'bg-surface border-surface-border text-text-secondary hover:border-accent/40'
                }`}
              >
                Nữ Mạng
              </button>
            </div>
          </div>

          {/* Ngày sinh Dương lịch */}
          <div className="space-y-1">
            <label className="block text-xs font-semibold text-text-primary">
              Ngày sinh Dương lịch <span className="text-primary">*</span>
            </label>
            <input
              type="date"
              value={ngaySinh}
              onChange={(e) => setNgaySinh(e.target.value)}
              className="input-field text-sm"
              required
            />
          </div>

          {/* Giờ và Phút sinh */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="block text-xs font-semibold text-text-primary">
                Giờ sinh (0 - 23h)
              </label>
              <input
                type="number"
                min={0}
                max={23}
                value={gioSinh}
                onChange={(e) => setGioSinh(e.target.value)}
                className="input-field text-sm"
              />
            </div>
            <div className="space-y-1">
              <label className="block text-xs font-semibold text-text-primary">
                Phút sinh (0 - 59p)
              </label>
              <input
                type="number"
                min={0}
                max={59}
                value={phutSinh}
                onChange={(e) => setPhutSinh(e.target.value)}
                className="input-field text-sm"
              />
            </div>
          </div>

          {/* Nút hành động */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-surface-border">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="btn-outline text-xs px-4 py-2"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary text-xs px-5 py-2 inline-flex items-center gap-1.5"
            >
              {loading ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-text-on-primary border-t-transparent rounded-full animate-spin" />
                  <span>Đang lưu...</span>
                </>
              ) : (
                <>
                  <IconCheck size={16} />
                  <span>Lưu Thay Đổi</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
