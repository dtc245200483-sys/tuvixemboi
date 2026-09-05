import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  IconYinYang,
  IconLock,
  IconMail,
  IconArrowRight,
  IconEye,
  IconEyeOff,
  IconCheck
} from '@tabler/icons-react';
import { authService, birthProfileService } from '../../services/api';
import { useAuthStore } from '../../store/authStore';
import ErrorMessage from '../../components/ErrorMessage';
import LoadingSpinner from '../../components/LoadingSpinner';

const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Vui lòng nhập email đăng nhập')
    .email('Định dạng email không hợp lệ'),
  password: z
    .string()
    .min(1, 'Vui lòng nhập mật khẩu'),
});

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const login = useAuthStore((state) => state.login);

  const [serverError, setServerError] = useState(null);
  const [successNotice, setSuccessNotice] = useState(null);
  const [showPassword, setShowPassword] = useState(false);

  // Hiển thị thông báo nếu có chuyển hướng từ RegisterPage
  useEffect(() => {
    if (location.state?.successMessage) {
      setSuccessNotice(location.state.successMessage);
      // Xóa state của location để không lặp lại khi refresh
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(loginSchema),
    mode: 'onBlur',
  });

  const onSubmit = async (data) => {
    setServerError(null);
    try {
      const res = await authService.login(data.email, data.password);
      const tokens = res.data;

      // Nạp thông tin user hiện tại
      login(tokens);

      try {
        const meRes = await authService.getMe();
        login(tokens, meRes.data);
      } catch (meErr) {
        // Vẫn tiếp tục nếu lấy me thất bại tạm thời
      }

      // Chuyển hướng sang trang hồ sơ sinh hoặc dashboard
      let targetPath = location.state?.from?.pathname;
      if (!targetPath || targetPath === '/login' || targetPath === '/register') {
        try {
          const profRes = await birthProfileService.getAll();
          const list = profRes.data?.du_lieu || profRes.data || [];
          targetPath = list.length > 0 ? '/dashboard' : '/birth-profile';
        } catch {
          targetPath = '/dashboard';
        }
      }
      navigate(targetPath, { replace: true });
    } catch (err) {
      if (err.response) {
        if (err.response.status === 401 || err.response.status === 400) {
          // Nguyên tắc bảo mật: Không tiết lộ email có tồn tại hay không
          setServerError('Sai email hoặc mật khẩu. Vui lòng kiểm tra lại.');
        } else {
          const detail = err.response.data?.detail || err.response.data?.loi;
          setServerError(typeof detail === 'string' ? detail : 'Đăng nhập không thành công.');
        }
      } else {
        setServerError('Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng của bạn.');
      }
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center mb-6">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-card bg-surface border border-surface-border text-accent shadow-subtle mb-3">
          <IconYinYang size={32} stroke={1.75} />
        </div>
        <h1 className="font-heading text-3xl font-bold text-primary tracking-wide">
          Đăng Nhập Hệ Thống
        </h1>
        <p className="font-body text-sm text-text-secondary mt-1">
          Nền Tảng Luận Giải Tử Vi & Huyền Học Trí Tuệ Nhân Tạo
        </p>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="card-base p-6 sm:p-8">
          {/* Thông báo đăng ký thành công nếu có (dùng đúng token accent và subtle surface) */}
          {successNotice && (
            <div className="bg-[#FAF5EE] border border-accent/40 rounded-btn p-3.5 flex items-center gap-2.5 text-sm text-text-primary mb-5 font-body shadow-subtle">
              <IconCheck size={20} className="flex-shrink-0 text-accent" />
              <span>{successNotice}</span>
            </div>
          )}

          {serverError && (
            <ErrorMessage
              message={serverError}
              onClose={() => setServerError(null)}
              className="mb-5"
            />
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
            {/* Trường Email */}
            <div>
              <label className="block font-body text-xs font-semibold text-text-primary uppercase tracking-wider mb-1.5">
                Email Đăng Nhập <span className="text-primary">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-text-secondary">
                  <IconMail size={18} />
                </div>
                <input
                  type="email"
                  placeholder="name@example.com"
                  {...register('email')}
                  className={`w-full pl-10 pr-3.5 py-2.5 bg-surface rounded-btn border text-sm text-text-primary placeholder:text-text-secondary/60 focus:outline-none transition-all ${
                    errors.email
                      ? 'border-[#E6C2BC] bg-[#FAF0EE]/30 focus:border-primary'
                      : 'border-surface-border focus:border-accent focus:ring-1 focus:ring-accent/30'
                  }`}
                />
              </div>
              {errors.email && (
                <p className="text-xs text-primary font-body mt-1.5 pl-1 leading-normal">
                  {errors.email.message}
                </p>
              )}
            </div>

            {/* Trường Mật Khẩu */}
            <div>
              <label className="block font-body text-xs font-semibold text-text-primary uppercase tracking-wider mb-1.5">
                Mật Khẩu <span className="text-primary">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-text-secondary">
                  <IconLock size={18} />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Nhập mật khẩu"
                  {...register('password')}
                  className={`w-full pl-10 pr-10 py-2.5 bg-surface rounded-btn border text-sm text-text-primary placeholder:text-text-secondary/60 focus:outline-none transition-all ${
                    errors.password
                      ? 'border-[#E6C2BC] bg-[#FAF0EE]/30 focus:border-primary'
                      : 'border-surface-border focus:border-accent focus:ring-1 focus:ring-accent/30'
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-text-secondary hover:text-text-primary"
                  tabIndex={-1}
                >
                  {showPassword ? <IconEyeOff size={18} /> : <IconEye size={18} />}
                </button>
              </div>
              {errors.password && (
                <p className="text-xs text-primary font-body mt-1.5 pl-1 leading-normal">
                  {errors.password.message}
                </p>
              )}
            </div>

            {/* Nút Đăng Nhập */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn-primary w-full py-3 text-base shadow-subtle disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <LoadingSpinner size="sm" color="white" text="Đang đăng nhập..." />
                ) : (
                  <>
                    <span>Đăng Nhập</span>
                    <IconArrowRight size={18} />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Điều hướng sang Đăng Ký */}
          <div className="mt-6 pt-5 border-t border-surface-border text-center text-sm font-body text-text-secondary">
            <span>Chưa có tài khoản? </span>
            <Link
              to="/register"
              className="text-primary font-medium hover:underline hover:text-[#552218] transition-colors"
            >
              Đăng ký tài khoản mới
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}