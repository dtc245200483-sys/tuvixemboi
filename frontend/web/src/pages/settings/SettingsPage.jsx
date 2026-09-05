import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  IconArrowLeft,
  IconUser,
  IconLock,
  IconCalendar,
  IconTrash,
  IconEdit,
  IconPhoto,
  IconShieldCheck,
  IconAlertTriangle,
  IconPlus,
  IconExternalLink,
  IconCheck,
  IconClock,
  IconX,
} from '@tabler/icons-react';
import { useAuthStore } from '../../store/authStore';
import { authService, birthProfileService, visionService } from '../../services/api';
import ChangePasswordForm from './ChangePasswordForm';
import EditBirthProfileModal from './EditBirthProfileModal';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function SettingsPage() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  // States
  const [currentUser, setCurrentUser] = useState(user);
  const [birthProfiles, setBirthProfiles] = useState([]);
  const [photos, setPhotos] = useState([]);
  const [loadingProfiles, setLoadingProfiles] = useState(true);
  const [loadingPhotos, setLoadingPhotos] = useState(true);

  // Modals & toggles
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [editingProfile, setEditingProfile] = useState(null);
  const [showDeleteAccountModal, setShowDeleteAccountModal] = useState(false);
  const [confirmEmailInput, setConfirmEmailInput] = useState('');
  const [isDeletingAccount, setIsDeletingAccount] = useState(false);
  const [deleteAccountError, setDeleteAccountError] = useState(null);

  // Load User details
  useEffect(() => {
    const fetchMe = async () => {
      try {
        const res = await authService.getMe();
        if (res.data) {
          setCurrentUser(res.data);
        }
      } catch (err) {
        // Fallback to store user
      }
    };
    fetchMe();
  }, []);

  // Load Birth Profiles
  const fetchProfiles = async () => {
    try {
      setLoadingProfiles(true);
      const res = await birthProfileService.getAll();
      const list = res.data?.du_lieu || res.data || [];
      setBirthProfiles(list);
    } catch (err) {
      console.error('Lỗi lấy danh sách hồ sơ sinh:', err);
    } finally {
      setLoadingProfiles(false);
    }
  };

  // Load Biometric Photos
  const fetchPhotos = async () => {
    try {
      setLoadingPhotos(true);
      const res = await visionService.getMyPhotos();
      const list = res.data || [];
      const activePhotos = Array.isArray(list) ? list.filter((p) => !p.da_duoc_xoa) : [];
      setPhotos(activePhotos);
    } catch (err) {
      console.error('Lỗi lấy danh sách ảnh sinh trắc học:', err);
    } finally {
      setLoadingPhotos(false);
    }
  };

  useEffect(() => {
    fetchProfiles();
    fetchPhotos();
  }, []);

  // Delete a Birth Profile
  const handleDeleteProfile = async (profileId, name) => {
    const confirmed = window.confirm(
      `Bạn có chắc chắn muốn xóa hồ sơ sinh của "${name || 'Mệnh chủ'}"? Hành động này sẽ xóa các lá số liên quan đến hồ sơ này.`
    );
    if (!confirmed) return;

    try {
      await birthProfileService.delete(profileId);
      fetchProfiles();
    } catch (err) {
      alert(err.response?.data?.loi || 'Không thể xóa hồ sơ sinh. Vui lòng thử lại.');
    }
  };

  // Delete a Biometric Photo
  const handleDeletePhoto = async (photoId, photoType) => {
    const typeLabel = photoType === 'mat' ? 'khuôn mặt' : 'bàn tay';
    const confirmed = window.confirm(
      `Bạn có chắc chắn muốn xóa vĩnh viễn tệp ảnh ${typeLabel} này khỏi máy chủ ngay lập tức?`
    );
    if (!confirmed) return;

    try {
      await visionService.deleteAnh(photoId);
      fetchPhotos();
    } catch (err) {
      alert(err.response?.data?.detail || 'Không thể xóa ảnh. Vui lòng thử lại.');
    }
  };

  // Delete Account (2-Step Confirmation)
  const handleDeleteAccount = async () => {
    setDeleteAccountError(null);
    const expectedEmail = currentUser?.email || user?.email;
    if (confirmEmailInput.trim().toLowerCase() !== expectedEmail?.toLowerCase()) {
      setDeleteAccountError('Địa chỉ email xác nhận không trùng khớp với tài khoản.');
      return;
    }

    try {
      setIsDeletingAccount(true);
      await authService.deleteAccount({ email: confirmEmailInput.trim() });
      logout();
      navigate('/register', {
        replace: true,
        state: { message: 'Tài khoản và toàn bộ dữ liệu của bạn đã được xóa vĩnh viễn.' },
      });
    } catch (err) {
      const msg =
        err.response?.data?.loi ||
        err.response?.data?.detail ||
        'Không thể xóa tài khoản. Vui lòng kiểm tra lại.';
      setDeleteAccountError(msg);
      setIsDeletingAccount(false);
    }
  };

  const formatDate = (isoString) => {
    if (!isoString) return '--';
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="min-h-screen bg-background text-text-primary font-body pb-12">
      {/* Navigation Header */}
      <header className="bg-surface border-b border-surface-border px-4 sm:px-8 py-4 sticky top-0 z-20 shadow-xs">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="p-2 -ml-2 rounded-xl text-text-secondary hover:text-primary hover:bg-[#FAF5EE] transition-colors focus:outline-none"
              title="Quay lại Trang Chủ"
            >
              <IconArrowLeft size={20} />
            </button>
            <div>
              <h1 className="font-heading text-xl sm:text-2xl font-bold text-primary">
                Cài Đặt & Quyền Riêng Tư
              </h1>
              <p className="text-xs text-text-secondary">
                Quản lý tài khoản, hồ sơ sinh và dữ liệu cá nhân
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Settings Container */}
      <main className="max-w-4xl mx-auto px-4 sm:px-8 py-8 space-y-8">
        {/* ========================================================= */}
        {/* MỤC 1: TÀI KHOẢN & BẢO MẬT */}
        {/* ========================================================= */}
        <section className="card-base p-6 sm:p-7 border border-surface-border bg-surface shadow-subtle space-y-5">
          <div className="flex items-center justify-between border-b border-surface-border pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-card bg-[#FAF5EE] border border-accent/40 flex items-center justify-center text-accent">
                <IconUser size={22} />
              </div>
              <div>
                <h2 className="font-heading text-lg sm:text-xl font-bold text-primary">
                  Thông Tin Tài Khoản
                </h2>
                <p className="text-xs text-text-secondary">
                  Thông tin đăng nhập và trạng thái bảo mật của bạn
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setShowPasswordModal(true)}
              className="btn-outline text-xs px-3.5 py-2 inline-flex items-center gap-1.5"
            >
              <IconLock size={15} />
              <span>Đổi Mật Khẩu</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div className="p-3.5 rounded-xl bg-[#FAF5EE]/60 border border-surface-border space-y-1">
              <span className="text-xs text-text-secondary font-medium">Địa chỉ Email</span>
              <p className="font-semibold text-text-primary break-all">
                {currentUser?.email || user?.email || '--'}
              </p>
            </div>
            <div className="p-3.5 rounded-xl bg-[#FAF5EE]/60 border border-surface-border space-y-1">
              <span className="text-xs text-text-secondary font-medium">Trạng thái tài khoản</span>
              <p className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary">
                <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
                Đang kích hoạt bình thường
              </p>
            </div>
          </div>
        </section>

        {/* ========================================================= */}
        {/* MỤC 2: QUẢN LÝ HỒ SƠ SINH */}
        {/* ========================================================= */}
        <section className="card-base p-6 sm:p-7 border border-surface-border bg-surface shadow-subtle space-y-5">
          <div className="flex items-center justify-between border-b border-surface-border pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-card bg-[#FAF5EE] border border-accent/40 flex items-center justify-center text-accent">
                <IconCalendar size={22} />
              </div>
              <div>
                <h2 className="font-heading text-lg sm:text-xl font-bold text-primary">
                  Hồ Sơ Mệnh Chủ
                </h2>
                <p className="text-xs text-text-secondary">
                  Danh sách ngày giờ sinh đã tạo (hỗ trợ nhiều hồ sơ cho bản thân và người thân)
                </p>
              </div>
            </div>

            <Link
              to="/birth-profile"
              className="btn-primary text-xs px-3.5 py-2 inline-flex items-center gap-1.5"
            >
              <IconPlus size={15} />
              <span>Thêm Hồ Sơ</span>
            </Link>
          </div>

          {loadingProfiles ? (
            <div className="py-6 text-center">
              <LoadingSpinner size="sm" text="Đang tải danh sách hồ sơ sinh..." />
            </div>
          ) : birthProfiles.length === 0 ? (
            <div className="py-8 text-center space-y-3 bg-[#FAF5EE]/40 rounded-xl border border-dashed border-surface-border">
              <p className="text-sm text-text-secondary">
                Bạn chưa có hồ sơ sinh nào. Hãy tạo hồ sơ để bắt đầu lập lá số Tử Vi & Bát Tự.
              </p>
              <Link to="/birth-profile" className="btn-primary text-xs px-4 py-2 inline-block">
                Thiết Lập Hồ Sơ Sinh Ngay
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {birthProfiles.map((p) => {
                const lunar = p.thong_tin_am_lich || {};
                return (
                  <div
                    key={p.id}
                    className="p-4 rounded-xl border border-surface-border bg-surface hover:border-accent/60 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-heading text-base font-bold text-primary">
                          {p.ho_ten || 'Mệnh Chủ'}
                        </span>
                        <span className="px-2 py-0.5 rounded-md bg-[#FAF5EE] border border-surface-border text-[11px] font-medium text-text-secondary">
                          {p.gioi_tinh === 'nam' ? 'Nam Mạng' : 'Nữ Mạng'}
                        </span>
                      </div>
                      <div className="text-xs text-text-secondary flex flex-wrap items-center gap-x-3 gap-y-1">
                        <span>
                          Dương lịch: {p.ngay_sinh_duong} ({p.gio_sinh}h:{String(p.phut_sinh).padStart(2, '0')})
                        </span>
                        <span>•</span>
                        <span>
                          Âm lịch: {lunar.can_chi_nam || p.ngay_sinh_am || '--'}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 self-end sm:self-center">
                      <Link
                        to={`/tu-vi?profile_id=${p.id}`}
                        className="btn-outline text-xs px-3 py-1.5 inline-flex items-center gap-1"
                        title="Xem lá số Tử Vi"
                      >
                        <span>Lá số</span>
                        <IconExternalLink size={13} />
                      </Link>
                      <button
                        type="button"
                        onClick={() => setEditingProfile(p)}
                        className="p-1.5 rounded-lg text-text-secondary hover:text-accent hover:bg-[#FAF5EE] border border-surface-border transition-colors focus:outline-none"
                        title="Chỉnh sửa hồ sơ"
                      >
                        <IconEdit size={16} />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteProfile(p.id, p.ho_ten)}
                        className="p-1.5 rounded-lg text-text-secondary hover:text-primary hover:bg-[#FAF0EE] border border-surface-border transition-colors focus:outline-none"
                        title="Xóa hồ sơ"
                      >
                        <IconTrash size={16} />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        {/* ========================================================= */}
        {/* MỤC 3: DỮ LIỆU SINH TRẮC HỌC & QUYỀN RIÊNG TƯ */}
        {/* ========================================================= */}
        <section className="card-base p-6 sm:p-7 border border-surface-border bg-surface shadow-subtle space-y-5">
          <div className="border-b border-surface-border pb-4 space-y-1">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-card bg-[#FAF5EE] border border-accent/40 flex items-center justify-center text-accent">
                <IconShieldCheck size={22} />
              </div>
              <div>
                <h2 className="font-heading text-lg sm:text-xl font-bold text-primary">
                  Dữ Liệu Sinh Trắc Học & Quyền Riêng Tư
                </h2>
                <p className="text-xs text-text-secondary">
                  Kiểm soát các hình ảnh khuôn mặt và bàn tay đã tải lên để xem nhân tướng
                </p>
              </div>
            </div>
            <div className="mt-2 text-xs text-text-secondary bg-[#FAF5EE]/70 p-3 rounded-xl border border-surface-border leading-relaxed">
              <strong className="text-primary">Chính sách bảo mật:</strong> Các tệp hình ảnh sinh trắc học được mã hóa và tự động xóa hoàn toàn khỏi máy chủ sau <strong>30 ngày</strong>. Bạn có quyền xóa tệp vật lý và bản ghi ngay lập tức bằng nút "Xóa ngay" bên dưới.
            </div>
          </div>

          {loadingPhotos ? (
            <div className="py-6 text-center">
              <LoadingSpinner size="sm" text="Đang tải dữ liệu ảnh sinh trắc học..." />
            </div>
          ) : photos.length === 0 ? (
            <div className="py-6 text-center text-sm text-text-secondary bg-[#FAF5EE]/30 rounded-xl border border-dashed border-surface-border">
              Bạn hiện không có dữ liệu hình ảnh sinh trắc học nào được lưu trữ trên hệ thống.
            </div>
          ) : (
            <div className="space-y-3">
              {photos.map((ph) => {
                const isMat = ph.loai_anh === 'mat';
                return (
                  <div
                    key={ph.id}
                    className="p-3.5 rounded-xl border border-surface-border bg-surface flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs"
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-9 h-9 rounded-lg bg-[#FAF5EE] border border-surface-border flex items-center justify-center text-accent flex-shrink-0 mt-0.5">
                        <IconPhoto size={18} />
                      </div>
                      <div className="space-y-0.5 text-xs">
                        <div className="font-bold text-text-primary">
                          {isMat ? 'Ảnh Diện Mạo Khuôn Mặt' : 'Ảnh Tướng Bàn Tay'}
                        </div>
                        <div className="text-text-secondary flex flex-wrap items-center gap-x-2 gap-y-0.5">
                          <span>Đăng tải: {formatDate(ph.ngay_upload)}</span>
                          <span>•</span>
                          <span className="text-primary font-medium">
                            Tự động xóa sau: {formatDate(ph.ngay_het_han)}
                          </span>
                        </div>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => handleDeletePhoto(ph.id, ph.loai_anh)}
                      className="text-xs px-3 py-1.5 rounded-btn bg-[#FAF0EE] hover:bg-[#E6C2BC]/40 border border-[#E6C2BC] text-primary transition-colors self-end sm:self-center flex items-center gap-1 font-medium focus:outline-none"
                    >
                      <IconTrash size={14} />
                      <span>Xóa ngay lập tức</span>
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        {/* ========================================================= */}
        {/* MỤC 4: XÓA TÀI KHOẢN (DANGER ZONE) */}
        {/* ========================================================= */}
        <section className="card-base p-6 sm:p-7 border border-[#E6C2BC] bg-[#FAF0EE]/60 shadow-subtle space-y-4">
          <div className="flex items-start gap-3.5">
            <div className="w-10 h-10 rounded-card bg-[#FAF0EE] border border-[#E6C2BC] flex items-center justify-center text-primary flex-shrink-0">
              <IconAlertTriangle size={22} />
            </div>
            <div className="space-y-1">
              <h2 className="font-heading text-lg sm:text-xl font-bold text-primary">
                Khu Vực Nguy Hiểm: Xóa Vĩnh Viễn Tài Khoản
              </h2>
              <p className="text-xs text-text-secondary leading-relaxed">
                Hành động này sẽ xóa vĩnh viễn tài khoản của bạn, bao gồm mọi hồ sơ ngày sinh, các bản tính toán Tử Vi & Bát Tự, lịch sử gieo quẻ, lịch sử trò chuyện cùng các tệp ảnh sinh trắc học vật lý trên máy chủ.
              </p>
            </div>
          </div>

          <div className="pt-2 flex justify-end">
            <button
              type="button"
              onClick={() => {
                setConfirmEmailInput('');
                setDeleteAccountError(null);
                setShowDeleteAccountModal(true);
              }}
              className="text-xs px-4 py-2.5 rounded-btn bg-[#6B2B1F] hover:bg-[#552218] text-[#FBF3E6] font-medium transition-all shadow-subtle focus:outline-none flex items-center gap-1.5"
            >
              <IconTrash size={15} />
              <span>Xóa Tài Khoản Của Tôi</span>
            </button>
          </div>
        </section>
      </main>

      {/* ========================================================= */}
      {/* MODAL 1: ĐỔI MẬT KHẨU */}
      {/* ========================================================= */}
      {showPasswordModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#3B2417]/50 backdrop-blur-xs font-body animate-fade-in">
          <div className="card-base w-full max-w-md p-6 sm:p-7 shadow-elevated border border-surface-border bg-surface relative">
            <button
              type="button"
              onClick={() => setShowPasswordModal(false)}
              className="absolute top-5 right-5 text-text-secondary hover:text-text-primary p-1 rounded-full transition-colors focus:outline-none"
            >
              <IconX size={20} />
            </button>

            <div className="mb-5 space-y-1">
              <h3 className="font-heading text-xl font-bold text-primary">
                Đổi Mật Khẩu Đăng Nhập
              </h3>
              <p className="text-xs text-text-secondary">
                Vui lòng nhập mật khẩu hiện tại và thiết lập mật khẩu mới
              </p>
            </div>

            <ChangePasswordForm
              onSuccess={() => setShowPasswordModal(false)}
              onCancel={() => setShowPasswordModal(false)}
            />
          </div>
        </div>
      )}

      {/* ========================================================= */}
      {/* MODAL 2: SỬA HỒ SƠ SINH */}
      {/* ========================================================= */}
      <EditBirthProfileModal
        profile={editingProfile}
        isOpen={Boolean(editingProfile)}
        onClose={() => setEditingProfile(null)}
        onSuccess={fetchProfiles}
      />

      {/* ========================================================= */}
      {/* MODAL 3: XÁC NHẬN XÓA TÀI KHOẢN (2 BƯỚC) */}
      {/* ========================================================= */}
      {showDeleteAccountModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#3B2417]/60 backdrop-blur-xs font-body animate-fade-in">
          <div className="card-base w-full max-w-md p-6 sm:p-7 shadow-elevated border border-[#E6C2BC] bg-surface relative space-y-4">
            <div className="w-12 h-12 rounded-full bg-[#FAF0EE] border border-[#E6C2BC] flex items-center justify-center text-primary mx-auto">
              <IconAlertTriangle size={26} />
            </div>

            <div className="text-center space-y-1">
              <h3 className="font-heading text-xl font-bold text-primary">
                Xác Nhận Xóa Vĩnh Viễn Tài Khoản
              </h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                Hành động này <strong className="text-primary">KHÔNG THỂ HOÀN TÁC</strong>. Toàn bộ thông tin hồ sơ và dữ liệu sinh trắc học sẽ bị xóa sạch khỏi máy chủ.
              </p>
            </div>

            {deleteAccountError && (
              <div className="p-3 rounded-lg bg-[#FAF0EE] border border-[#E6C2BC] text-primary text-xs">
                {deleteAccountError}
              </div>
            )}

            <div className="space-y-2 pt-1">
              <label className="block text-xs font-semibold text-text-primary">
                Để xác nhận, vui lòng gõ lại chính xác địa chỉ email của bạn:
                <span className="block font-mono text-primary font-bold mt-0.5 select-all">
                  {currentUser?.email || user?.email}
                </span>
              </label>
              <input
                type="text"
                value={confirmEmailInput}
                onChange={(e) => setConfirmEmailInput(e.target.value)}
                placeholder={currentUser?.email || user?.email}
                className="input-field text-sm font-mono"
                autoFocus
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-surface-border">
              <button
                type="button"
                onClick={() => setShowDeleteAccountModal(false)}
                disabled={isDeletingAccount}
                className="btn-outline text-xs px-4 py-2"
              >
                Giữ Lại Tài Khoản
              </button>
              <button
                type="button"
                onClick={handleDeleteAccount}
                disabled={
                  isDeletingAccount ||
                  confirmEmailInput.trim().toLowerCase() !== (currentUser?.email || user?.email)?.toLowerCase()
                }
                className="text-xs px-4 py-2 rounded-btn bg-[#6B2B1F] hover:bg-[#552218] text-[#FBF3E6] font-semibold transition-all disabled:opacity-40 disabled:hover:bg-[#6B2B1F] flex items-center gap-1.5 focus:outline-none"
              >
                {isDeletingAccount ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-[#FBF3E6] border-t-transparent rounded-full animate-spin" />
                    <span>Đang xóa...</span>
                  </>
                ) : (
                  <>
                    <IconTrash size={15} />
                    <span>Xác Nhận Xóa Vĩnh Viễn</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
