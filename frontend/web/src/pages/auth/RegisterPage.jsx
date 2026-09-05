import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import {
  IconYinYang,
  IconLock,
  IconMail,
  IconArrowRight,
  IconEye,
  IconEyeOff,
  IconCheck
} from '@tabler/icons-react';
import { authService } from '../../services/api';
import ErrorMessage from '../../components/ErrorMessage';
import LoadingSpinner from '../../components/LoadingSpinner';

// Schema xác thực dữ liệu qua Zod
const registerSchema = z
  .object({
    email: z
      .string()
      .min(1, 'Vui lòng nhập địa chỉ email')
      .email('Địa chỉ email không đúng định dạng (VD: example@email.com)'),
    password: z
      .string()
      .min(8, 'Mật khẩu phải có tối thiểu 8 ký tự để đảm bảo an toàn'),
    confirm_password: z
      .string()
      .min(1, 'Vui lòng nhập lại mật khẩu xác nhận'),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: 'Mật khẩu xác nhận không khớp với mật khẩu đã nhập',
    path: ['confirm_password'],
  });

export default function RegisterPage() {
  const navigate = useNavigate();
  const [serverError, setServerError] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(registerSchema),
    mode: 'onBlur', // Kiểm tra validate ngay khi người dùng rời khỏi ô nhập
  });

  const onSubmit = async (data) => {
    setServerError(null);
    try {
      await authService.register(data.email, data.password, data.confirm_password);
      // Chuyển sang LoginPage kèm state thông báo thành công
      navigate('/login', {
        state: { successMessage: 'Đăng ký tài khoản thành công! Vui lòng đăng nhập để bắt đầu.' },
      });
    } catch (err) {
      if (err.response) {
        if (err.response.status === 409) {
          setServerError('Email này đã được đăng ký trên hệ thống. Vui lòng đăng nhập hoặc dùng email khác.');
        } else {
          const detail = err.response.data?.detail || err.response.data?.loi;
          setServerError(typeof detail === 'string' ? detail : 'Đăng ký không thành công. Vui lòng thử lại.');
        }
      } else {
        setServerError('Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại kết nối mạng của bạn.');
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
          Khởi Tạo Tài Khoản
        </h1>
        <p className="font-body text-sm text-text-secondary mt-1">
          Bắt đầu hành trình khám phá mệnh lý Tử Vi, Bát Tự & Kinh Dịch
        </p>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="card-base p-6 sm:p-8">
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
                Địa Chỉ Email <span className="text-primary">*</span>
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
                  placeholder="Tối thiểu 8 ký tự"
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

            {/* Trường Xác Nhận Mật Khẩu */}
            <div>
              <label className="block font-body text-xs font-semibold text-text-primary uppercase tracking-wider mb-1.5">
                Xác Nhận Mật Khẩu <span className="text-primary">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-text-secondary">
                  <IconLock size={18} />
                </div>
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="Nhập lại mật khẩu phía trên"
                  {...register('confirm_password')}
                  className={`w-full pl-10 pr-10 py-2.5 bg-surface rounded-btn border text-sm text-text-primary placeholder:text-text-secondary/60 focus:outline-none transition-all ${
                    errors.confirm_password
                      ? 'border-[#E6C2BC] bg-[#FAF0EE]/30 focus:border-primary'
                      : 'border-surface-border focus:border-accent focus:ring-1 focus:ring-accent/30'
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-text-secondary hover:text-text-primary"
                  tabIndex={-1}
                >
                  {showConfirmPassword ? <IconEyeOff size={18} /> : <IconEye size={18} />}
                </button>
              </div>
              {errors.confirm_password && (
                <p className="text-xs text-primary font-body mt-1.5 pl-1 leading-normal">
                  {errors.confirm_password.message}
                </p>
              )}
            </div>

            {/* Nút Đăng Ký */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn-primary w-full py-3 text-base shadow-subtle disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <LoadingSpinner size="sm" color="white" text="Đang tạo tài khoản..." />
                ) : (
                  <>
                    <span>Đăng Ký Tài Khoản</span>
                    <IconArrowRight size={18} />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Điều hướng sang Đăng Nhập */}
          <div className="mt-6 pt-5 border-t border-surface-border text-center text-sm font-body text-text-secondary">
            <span>Đã có tài khoản? </span>
            <Link
              to="/login"
              className="text-primary font-medium hover:underline hover:text-[#552218] transition-colors"
            >
              Đăng nhập ngay
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}