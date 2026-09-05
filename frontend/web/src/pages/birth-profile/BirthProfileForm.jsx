import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, Link } from 'react-router-dom';
import {
  IconCompass,
  IconCalendar,
  IconClock,
  IconUser,
  IconHelpCircle,
  IconCheck,
  IconArrowRight,
  IconArrowLeft,
  IconSparkles,
  IconInfoCircle,
  IconRefresh,
  IconChartBar,
  IconLayoutDashboard
} from '@tabler/icons-react';
import { birthProfileService } from '../../services/api';
import { useAuthStore } from '../../store/authStore';
import ErrorMessage from '../../components/ErrorMessage';
import LoadingSpinner from '../../components/LoadingSpinner';

const todayString = new Date().toISOString().split('T')[0];

const birthProfileSchema = z.object({
  ho_ten: z
    .string()
    .min(2, 'Họ và tên tối thiểu 2 ký tự')
    .max(100, 'Họ và tên không quá 100 ký tự'),
  ngay_sinh_duong: z
    .string()
    .min(1, 'Vui lòng chọn ngày sinh dương lịch')
    .refine((val) => val <= todayString, {
      message: 'Ngày sinh không được ở tương lai',
    }),
  gio_sinh: z.coerce
    .number({ invalid_type_error: 'Vui lòng chọn giờ sinh' })
    .min(0, 'Giờ sinh từ 0 đến 23')
    .max(23, 'Giờ sinh từ 0 đến 23'),
  phut_sinh: z.coerce
    .number({ invalid_type_error: 'Vui lòng chọn phút sinh' })
    .min(0, 'Phút sinh từ 0 đến 59')
    .max(59, 'Phút sinh từ 0 đến 59'),
  gioi_tinh: z.enum(['nam', 'nu'], {
    errorMap: () => ({ message: 'Vui lòng chọn giới tính (Nam Mạng hoặc Nữ Mạng)' }),
  }),
});

export default function BirthProfileForm() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const [serverError, setServerError] = useState(null);
  const [createdProfile, setCreatedProfile] = useState(null);
  const [showHourTooltip, setShowHourTooltip] = useState(false);

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(birthProfileSchema),
    defaultValues: {
      ho_ten: '',
      ngay_sinh_duong: '1995-10-24',
      gio_sinh: 14,
      phut_sinh: 30,
      gioi_tinh: 'nam',
    },
    mode: 'onBlur',
  });

  const onSubmit = async (data) => {
    setServerError(null);
    try {
      const res = await birthProfileService.create({
        ho_ten: data.ho_ten.trim(),
        ngay_sinh_duong: data.ngay_sinh_duong,
        gio_sinh: Number(data.gio_sinh),
        phut_sinh: Number(data.phut_sinh),
        gioi_tinh: data.gioi_tinh,
      });

      // Lấy dữ liệu hồ sơ đã tính toán âm lịch từ backend API response envelope
      const profileData = res.data?.du_lieu || res.data;
      setCreatedProfile(profileData);
    } catch (err) {
      if (err.response) {
        const detail = err.response.data?.detail || err.response.data?.loi;
        setServerError(typeof detail === 'string' ? detail : 'Không thể tạo hồ sơ sinh. Vui lòng kiểm tra lại dữ liệu.');
      } else {
        setServerError('Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại kết nối mạng của bạn.');
      }
    }
  };

  const handleResetNew = () => {
    setCreatedProfile(null);
    reset();
  };

  // Helper trích xuất thông tin âm lịch an toàn
  const lunar = createdProfile?.thong_tin_am_lich || {};
  const ngayAmStr = lunar.ngay_am || lunar.ngay || createdProfile?.ngay_sinh_am || '--';
  const thangAmStr = lunar.thang_am || lunar.thang || '--';
  const namAmStr = lunar.nam_am || lunar.nam || '--';
  const isLeap = lunar.la_thang_nhuan || lunar.nhuan;

  const canChiNam = lunar.can_chi_nam || (lunar.can_nam && lunar.chi_nam ? `${lunar.can_nam} ${lunar.chi_nam}` : '--');
  const canChiThang = lunar.can_chi_thang || (lunar.can_thang && lunar.chi_thang ? `${lunar.can_thang} ${lunar.chi_thang}` : '--');
  const canChiNgay = lunar.can_chi_ngay || (lunar.can_ngay && lunar.chi_ngay ? `${lunar.can_ngay} ${lunar.chi_ngay}` : '--');
  const canChiGio = lunar.can_chi_gio || (lunar.ten_gio ? `Giờ ${lunar.ten_gio}` : '--');

  return (
    <div className="min-h-screen bg-background text-text-primary">
      {/* Header thanh điều hướng */}
      <header className="bg-primary text-text-on-primary border-b border-[#552218] px-6 py-4 shadow-subtle sticky top-0 z-20">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              to="/dashboard"
              className="p-2 rounded-btn bg-[#552218] border border-surface-border/30 hover:border-accent text-text-on-primary transition-colors flex items-center gap-1.5"
              title="Về Bàn Làm Việc Tổng Quan (Dashboard)"
            >
              <IconArrowLeft size={16} />
              <span className="text-xs font-body hidden sm:inline">Tổng quan</span>
            </Link>
            <div className="w-9 h-9 rounded-btn bg-[#552218] border border-accent/40 flex items-center justify-center text-accent">
              <IconCompass size={22} stroke={1.75} />
            </div>
            <div>
              <h1 className="font-heading text-xl font-bold tracking-wide text-text-on-primary">
                Hồ Sơ Mệnh Lý
              </h1>
              <p className="text-xs text-[#D8C7B5] font-body">
                Nhập thông tin ngày giờ sinh lập lá số Tử Vi & Bát Tự
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/dashboard"
              className="text-xs font-body px-3 py-1.5 rounded-btn bg-[#552218] border border-surface-border/30 hover:border-accent text-text-on-primary transition-colors flex items-center gap-1.5"
            >
              <IconLayoutDashboard size={14} />
              <span className="hidden sm:inline">Dashboard</span>
            </Link>
            {user?.email && (
              <span className="hidden sm:inline text-xs text-[#EADFC8] font-body">
                {user.email}
              </span>
            )}
            <button
              onClick={logout}
              className="text-xs font-body px-3 py-1.5 rounded-btn bg-[#552218] border border-surface-border/30 hover:border-accent text-text-on-primary transition-colors"
            >
              Đăng xuất
            </button>
          </div>
        </div>
      </header>

      {/* Nội dung Form */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
        {serverError && (
          <ErrorMessage
            message={serverError}
            onClose={() => setServerError(null)}
            className="mb-6"
          />
        )}

        {/* KẾT QUẢ XÁC NHẬN ÂM LỊCH TỰ ĐỘNG (HIỂN THỊ SAU KHI TẠO XONG) */}
        {createdProfile ? (
          <div className="card-base p-6 sm:p-8 space-y-6 animate-fadeIn">
            <div className="flex items-start justify-between border-b border-surface-border pb-4">
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FAF5EE] border border-surface-border text-xs font-medium text-accent mb-2">
                  <IconCheck size={16} />
                  <span>Đã tính toán Âm Lịch & Can Chi thành công</span>
                </div>
                <h2 className="font-heading text-2xl font-bold text-primary">
                  Xác Nhận Thông Tin Hồ Sơ Sinh
                </h2>
                <p className="font-body text-sm text-text-secondary mt-0.5">
                  Vui lòng kiểm tra lại ngày Âm Lịch và Can Chi trước khi luận giải
                </p>
              </div>
              <button
                onClick={handleResetNew}
                className="btn-outline text-xs px-3 py-1.5"
                title="Tạo hồ sơ khác"
              >
                <IconRefresh size={16} />
                <span>Nhập lại</span>
              </button>
            </div>

            {/* Bảng đối chiếu Dương lịch và Âm lịch */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Thẻ Dương Lịch */}
              <div className="bg-[#FAF5EE] border border-surface-border rounded-btn p-4 space-y-2">
                <span className="text-xs font-mono font-bold text-accent uppercase tracking-wider block">
                  Dương Lịch Khởi Sinh
                </span>
                <p className="font-heading text-xl font-bold text-primary">
                  {createdProfile.ho_ten || 'Vô Danh'}
                </p>
                <div className="text-sm font-body text-text-primary space-y-1">
                  <p>
                    <span className="text-text-secondary">Ngày sinh:</span>{' '}
                    <strong>{createdProfile.ngay_sinh_duong}</strong>
                  </p>
                  <p>
                    <span className="text-text-secondary">Thời khắc:</span>{' '}
                    <strong>
                      {String(createdProfile.gio_sinh).padStart(2, '0')}h:
                      {String(createdProfile.phut_sinh).padStart(2, '0')}
                    </strong>
                  </p>
                  <p>
                    <span className="text-text-secondary">Giới tính:</span>{' '}
                    <strong className="capitalize">{createdProfile.gioi_tinh === 'nam' ? 'Nam Mạng' : 'Nữ Mạng'}</strong>
                  </p>
                </div>
              </div>

              {/* Thẻ Âm Lịch & Can Chi */}
              <div className="bg-surface border-2 border-accent/40 rounded-btn p-4 space-y-2 shadow-subtle">
                <span className="text-xs font-mono font-bold text-accent uppercase tracking-wider block">
                  Âm Lịch & Tứ Trụ Tự Động
                </span>
                <p className="font-heading text-xl font-bold text-primary">
                  Ngày {ngayAmStr} tháng {thangAmStr}{isLeap ? ' (Nhuận)' : ''} năm {namAmStr}
                </p>
                <div className="text-sm font-body text-text-primary space-y-1">
                  <p>
                    <span className="text-text-secondary">Năm Can Chi:</span>{' '}
                    <strong className="text-primary font-semibold">{canChiNam}</strong>
                  </p>
                  <p>
                    <span className="text-text-secondary">Tháng Can Chi:</span>{' '}
                    <strong className="text-primary font-semibold">{canChiThang}</strong>
                  </p>
                  <p>
                    <span className="text-text-secondary">Ngày Can Chi:</span>{' '}
                    <strong className="text-primary font-semibold">{canChiNgay}</strong>
                  </p>
                  <p>
                    <span className="text-text-secondary">Giờ Can Chi:</span>{' '}
                    <strong className="text-primary font-semibold">{canChiGio}</strong>
                  </p>
                </div>
              </div>
            </div>

            {/* Các hành động tiếp theo: Lập lá số & Phân tích */}
            <div className="pt-6 border-t border-surface-border space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <span className="text-xs font-body text-text-secondary">
                  Mã hồ sơ: <code className="font-mono bg-[#FAF5EE] px-2 py-0.5 rounded text-text-primary">{createdProfile.id}</code>
                </span>
                <span className="text-xs font-semibold text-accent uppercase tracking-wider">
                  ✦ Chọn bộ môn bắt đầu luận giải:
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Nút 1: Tử Vi Đẩu Số (Primary) */}
                <button
                  type="button"
                  id="btn-view-tuvi"
                  onClick={() => navigate(`/tu-vi?profile_id=${createdProfile.id}`)}
                  className="btn-primary p-4 flex items-center justify-between text-left shadow-subtle group hover:scale-[1.01] transition-transform"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-btn bg-[#552218] border border-accent/40 flex items-center justify-center text-accent flex-shrink-0">
                      <IconCompass size={22} />
                    </div>
                    <div>
                      <div className="font-heading font-bold text-base text-text-on-primary group-hover:text-accent transition-colors flex items-center gap-1.5">
                        <span>Xem Lá Số Tử Vi</span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-accent/30 text-text-on-primary">Chính Tông</span>
                      </div>
                      <div className="text-xs text-[#EADFC8] font-body mt-0.5">
                        12 Cung mệnh & 108 vì sao chính tinh, phụ tinh
                      </div>
                    </div>
                  </div>
                  <IconArrowRight size={20} className="text-accent group-hover:translate-x-1 transition-transform flex-shrink-0" />
                </button>

                {/* Nút 2: Bát Tự Tứ Trụ */}
                <button
                  type="button"
                  id="btn-view-battu"
                  onClick={() => navigate(`/bat-tu?profile_id=${createdProfile.id}`)}
                  className="btn-outline p-4 flex items-center justify-between text-left bg-surface hover:bg-[#FAF5EE] border-accent/40 group hover:scale-[1.01] transition-transform"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-btn bg-[#FAF5EE] border border-surface-border flex items-center justify-center text-primary flex-shrink-0">
                      <IconChartBar size={22} />
                    </div>
                    <div>
                      <div className="font-heading font-bold text-base text-primary group-hover:text-accent transition-colors flex items-center gap-1.5">
                        <span>Xem Bát Tự Tứ Trụ</span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface border border-surface-border text-text-secondary">Tử Bình</span>
                      </div>
                      <div className="text-xs text-text-secondary font-body mt-0.5">
                        Thiên Can, Địa Chi & Cân bằng Ngũ Hành
                      </div>
                    </div>
                  </div>
                  <IconArrowRight size={20} className="text-text-secondary group-hover:translate-x-1 transition-transform flex-shrink-0" />
                </button>
              </div>

              <div className="pt-3 flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-surface-border/50">
                <button
                  type="button"
                  onClick={handleResetNew}
                  className="btn-outline text-xs px-4 py-2 w-full sm:w-auto flex items-center justify-center gap-2"
                >
                  <IconRefresh size={15} />
                  <span>Nhập thông tin người khác</span>
                </button>

                <button
                  type="button"
                  id="btn-goto-dashboard"
                  onClick={() => navigate('/dashboard')}
                  className="btn-outline text-xs px-4 py-2 w-full sm:w-auto flex items-center justify-center gap-2 bg-[#FAF5EE] border-accent/30 text-primary font-semibold hover:border-accent"
                >
                  <IconLayoutDashboard size={15} />
                  <span>Vào Bàn Làm Việc Tổng Quan (Dashboard)</span>
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* FORM NHẬP THÔNG TIN SINH */
          <div className="card-base p-6 sm:p-8">
            <div className="mb-6">
              <h2 className="font-heading text-2xl font-bold text-primary">
                Thiết Lập Thông Tin Sinh
              </h2>
              <p className="font-body text-sm text-text-secondary mt-1">
                Thông tin ngày giờ sinh chính xác là nền tảng để an 108 vì sao Tử Vi và xác định Tứ Trụ Bát Tự.
              </p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
              {/* 1. Họ và tên */}
              <div>
                <label className="block font-body text-xs font-semibold text-text-primary uppercase tracking-wider mb-1.5">
                  Họ và Tên Mệnh Chủ <span className="text-primary">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-text-secondary">
                    <IconUser size={18} />
                  </div>
                  <input
                    type="text"
                    placeholder="Ví dụ: Nguyễn Văn An"
                    {...register('ho_ten')}
                    className={`w-full pl-10 pr-3.5 py-2.5 bg-surface rounded-btn border text-sm text-text-primary placeholder:text-text-secondary/60 focus:outline-none transition-all ${
                      errors.ho_ten
                        ? 'border-[#E6C2BC] bg-[#FAF0EE]/30 focus:border-primary'
                        : 'border-surface-border focus:border-accent focus:ring-1 focus:ring-accent/30'
                    }`}
                  />
                </div>
                {errors.ho_ten && (
                  <p className="text-xs text-primary font-body mt-1.5 pl-1 leading-normal">
                    {errors.ho_ten.message}
                  </p>
                )}
              </div>

              {/* 2. Giới tính (Nam Mạng / Nữ Mạng) */}
              <div>
                <label className="block font-body text-xs font-semibold text-text-primary uppercase tracking-wider mb-1.5">
                  Giới Tính Mệnh Chủ <span className="text-primary">*</span>
                </label>
                <Controller
                  name="gioi_tinh"
                  control={control}
                  render={({ field }) => (
                    <div className="grid grid-cols-2 gap-3">
                      {[
                        { id: 'nam', label: 'Nam Mạng' },
                        { id: 'nu', label: 'Nữ Mạng' },
                      ].map((item) => (
                        <button
                          key={item.id}
                          type="button"
                          onClick={() => field.onChange(item.id)}
                          className={`py-2.5 px-3 rounded-btn border text-sm font-medium transition-all text-center ${
                            field.value === item.id
                              ? 'bg-primary text-text-on-primary border-primary shadow-subtle'
                              : 'bg-surface text-text-primary border-surface-border hover:border-accent/60'
                          }`}
                        >
                          {item.label}
                        </button>
                      ))}
                    </div>
                  )}
                />
                {errors.gioi_tinh && (
                  <p className="text-xs text-primary font-body mt-1.5 pl-1 leading-normal">
                    {errors.gioi_tinh.message}
                  </p>
                )}
              </div>

              {/* 3. Ngày sinh dương lịch */}
              <div>
                <label className="block font-body text-xs font-semibold text-text-primary uppercase tracking-wider mb-1.5">
                  Ngày Sinh Dương Lịch <span className="text-primary">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-text-secondary">
                    <IconCalendar size={18} />
                  </div>
                  <input
                    type="date"
                    max={todayString}
                    {...register('ngay_sinh_duong')}
                    className={`w-full pl-10 pr-3.5 py-2.5 bg-surface rounded-btn border text-sm text-text-primary focus:outline-none transition-all ${
                      errors.ngay_sinh_duong
                        ? 'border-[#E6C2BC] bg-[#FAF0EE]/30 focus:border-primary'
                        : 'border-surface-border focus:border-accent focus:ring-1 focus:ring-accent/30'
                    }`}
                  />
                </div>
                {errors.ngay_sinh_duong && (
                  <p className="text-xs text-primary font-body mt-1.5 pl-1 leading-normal">
                    {errors.ngay_sinh_duong.message}
                  </p>
                )}
              </div>

              {/* 4. Giờ sinh & Phút sinh (Kèm Onboarding Tooltip) */}
              <div>
                <div className="flex items-center gap-1.5 mb-1.5 relative">
                  <label className="font-body text-xs font-semibold text-text-primary uppercase tracking-wider">
                    Giờ & Phút Sinh <span className="text-primary">*</span>
                  </label>
                  <button
                    type="button"
                    onClick={() => setShowHourTooltip(!showHourTooltip)}
                    onMouseEnter={() => setShowHourTooltip(true)}
                    onMouseLeave={() => setShowHourTooltip(false)}
                    className="text-accent hover:text-primary transition-colors focus:outline-none"
                    aria-label="Giải thích về giờ sinh"
                  >
                    <IconHelpCircle size={16} />
                  </button>

                  {/* Popover Tooltip */}
                  {showHourTooltip && (
                    <div className="absolute left-0 bottom-full mb-2 w-72 p-3 bg-surface border border-surface-border rounded-btn shadow-dropdown text-xs text-text-primary z-30 font-body leading-relaxed">
                      <div className="flex items-start gap-2">
                        <IconInfoCircle size={18} className="text-accent flex-shrink-0 mt-0.5" />
                        <div>
                          <strong>Tầm quan trọng của giờ sinh:</strong> Giờ sinh ảnh hưởng trực tiếp đến việc an cung Mệnh, Thân và 12 cung hoàng đạo. Nếu không chắc chắn, bạn có thể chọn giờ gần đúng nhất ghi trên giấy khai sinh.
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-3">
                  {/* Dropdown Giờ (0 - 23) */}
                  <div className="relative">
                    <select
                      {...register('gio_sinh')}
                      className={`w-full px-3.5 py-2.5 bg-surface rounded-btn border text-sm text-text-primary focus:outline-none transition-all ${
                        errors.gio_sinh
                          ? 'border-[#E6C2BC] bg-[#FAF0EE]/30 focus:border-primary'
                          : 'border-surface-border focus:border-accent focus:ring-1 focus:ring-accent/30'
                      }`}
                    >
                      {Array.from({ length: 24 }, (_, i) => (
                        <option key={i} value={i}>
                          {String(i).padStart(2, '0')} Giờ
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Dropdown Phút (0 - 59) */}
                  <div className="relative">
                    <select
                      {...register('phut_sinh')}
                      className={`w-full px-3.5 py-2.5 bg-surface rounded-btn border text-sm text-text-primary focus:outline-none transition-all ${
                        errors.phut_sinh
                          ? 'border-[#E6C2BC] bg-[#FAF0EE]/30 focus:border-primary'
                          : 'border-surface-border focus:border-accent focus:ring-1 focus:ring-accent/30'
                      }`}
                    >
                      {Array.from({ length: 60 }, (_, i) => (
                        <option key={i} value={i}>
                          {String(i).padStart(2, '0')} Phút
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                {(errors.gio_sinh || errors.phut_sinh) && (
                  <p className="text-xs text-primary font-body mt-1.5 pl-1 leading-normal">
                    {errors.gio_sinh?.message || errors.phut_sinh?.message}
                  </p>
                )}
              </div>

              {/* Nút Submit */}
              <div className="pt-3">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="btn-primary w-full py-3 text-base shadow-subtle disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <LoadingSpinner size="sm" color="white" text="Đang tính toán Âm Lịch & Can Chi..." />
                  ) : (
                    <>
                      <IconSparkles size={18} className="text-accent" />
                      <span>Xác Nhận & Tính Toán Âm Lịch</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}
