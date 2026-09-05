import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { IconLock, IconEye, IconEyeOff, IconCheck, IconAlertCircle } from '@tabler/icons-react';
import { authService } from '../../services/api';

const changePasswordSchema = z
  .object({
    mat_khau_cu: z.string().min(1, 'Vui lòng nhập mật khẩu hiện tại'),
    mat_khau_moi: z.string().min(8, 'Mật khẩu mới phải có tối thiểu 8 ký tự'),
    xac_nhan_mat_khau: z.string().min(1, 'Vui lòng xác nhận lại mật khẩu mới'),
  })
  .refine((data) => data.mat_khau_moi === data.xac_nhan_mat_khau, {
    message: 'Mật khẩu xác nhận không trùng khớp',
    path: ['xac_nhan_mat_khau'],
  })
  .refine((data) => data.mat_khau_cu !== data.mat_khau_moi, {
    message: 'Mật khẩu mới không được trùng với mật khẩu hiện tại',
    path: ['mat_khau_moi'],
  });

export default function ChangePasswordForm({ onSuccess, onCancel }) {
  const [showOldPass, setShowOldPass] = useState(false);
  const [showNewPass, setShowNewPass] = useState(false);
  const [showConfirmPass, setShowConfirmPass] = useState(false);
  const [serverError, setServerError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      mat_khau_cu: '',
      mat_khau_moi: '',
      xac_nhan_mat_khau: '',
    },
  });

  const onSubmit = async (data) => {
    setServerError(null);
    setSuccessMessage(null);
    try {
      await authService.changePassword(data);
      setSuccessMessage('Đổi mật khẩu thành công! Vui lòng ghi nhớ mật khẩu mới.');
      reset();
      if (onSuccess) {
        setTimeout(() => {
          onSuccess();
        }, 1500);
      }
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.loi ||
        'Không thể đổi mật khẩu. Vui lòng kiểm tra lại mật khẩu cũ.';
      setServerError(msg);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 font-body">
      {serverError && (
        <div className="p-3 rounded-lg bg-[#FAF0EE] border border-[#E6C2BC] text-primary text-xs flex items-center gap-2">
          <IconAlertCircle size={16} className="flex-shrink-0" />
          <span>{serverError}</span>
        </div>
      )}

      {successMessage && (
        <div className="p-3 rounded-lg bg-[#FAF5EE] border border-accent/60 text-primary text-xs flex items-center gap-2">
          <IconCheck size={16} className="text-accent flex-shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Mật khẩu cũ */}
      <div className="space-y-1">
        <label className="block text-xs font-semibold text-text-primary">
          Mật khẩu hiện tại <span className="text-primary">*</span>
        </label>
        <div className="relative">
          <input
            type={showOldPass ? 'text' : 'password'}
            {...register('mat_khau_cu')}
            placeholder="••••••••"
            className="input-field pr-10 text-sm"
          />
          <button
            type="button"
            onClick={() => setShowOldPass(!showOldPass)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary hover:text-text-primary focus:outline-none"
            tabIndex={-1}
          >
            {showOldPass ? <IconEyeOff size={16} /> : <IconEye size={16} />}
          </button>
        </div>
        {errors.mat_khau_cu && (
          <p className="text-[11px] text-primary mt-0.5">{errors.mat_khau_cu.message}</p>
        )}
      </div>

      {/* Mật khẩu mới */}
      <div className="space-y-1">
        <label className="block text-xs font-semibold text-text-primary">
          Mật khẩu mới (tối thiểu 8 ký tự) <span className="text-primary">*</span>
        </label>
        <div className="relative">
          <input
            type={showNewPass ? 'text' : 'password'}
            {...register('mat_khau_moi')}
            placeholder="••••••••"
            className="input-field pr-10 text-sm"
          />
          <button
            type="button"
            onClick={() => setShowNewPass(!showNewPass)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary hover:text-text-primary focus:outline-none"
            tabIndex={-1}
          >
            {showNewPass ? <IconEyeOff size={16} /> : <IconEye size={16} />}
          </button>
        </div>
        {errors.mat_khau_moi && (
          <p className="text-[11px] text-primary mt-0.5">{errors.mat_khau_moi.message}</p>
        )}
      </div>

      {/* Xác nhận mật khẩu mới */}
      <div className="space-y-1">
        <label className="block text-xs font-semibold text-text-primary">
          Xác nhận mật khẩu mới <span className="text-primary">*</span>
        </label>
        <div className="relative">
          <input
            type={showConfirmPass ? 'text' : 'password'}
            {...register('xac_nhan_mat_khau')}
            placeholder="••••••••"
            className="input-field pr-10 text-sm"
          />
          <button
            type="button"
            onClick={() => setShowConfirmPass(!showConfirmPass)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary hover:text-text-primary focus:outline-none"
            tabIndex={-1}
          >
            {showConfirmPass ? <IconEyeOff size={16} /> : <IconEye size={16} />}
          </button>
        </div>
        {errors.xac_nhan_mat_khau && (
          <p className="text-[11px] text-primary mt-0.5">{errors.xac_nhan_mat_khau.message}</p>
        )}
      </div>

      {/* Hành động */}
      <div className="flex items-center justify-end gap-2.5 pt-2">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="btn-outline text-xs px-4 py-2"
          >
            Hủy
          </button>
        )}
        <button
          type="submit"
          disabled={isSubmitting}
          className="btn-primary text-xs px-5 py-2 inline-flex items-center gap-1.5"
        >
          {isSubmitting ? (
            <>
              <div className="w-3.5 h-3.5 border-2 border-text-on-primary border-t-transparent rounded-full animate-spin" />
              <span>Đang lưu...</span>
            </>
          ) : (
            <>
              <IconLock size={15} />
              <span>Cập Nhật Mật Khẩu</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
}
