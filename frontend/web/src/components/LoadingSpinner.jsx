import React from 'react';

/**
 * LoadingSpinner - Biểu tượng tải trang chuẩn theo Design System:
 * - Sử dụng màu accent #C9962C (hoặc primary #6B2B1F)
 * - Hiệu ứng xoay tròn mượt mà
 */
export default function LoadingSpinner({ size = 'md', text = '', color = 'accent', className = '' }) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-2',
    lg: 'w-10 h-10 border-3',
  };

  const colorClasses = {
    accent: 'border-accent/30 border-t-accent',
    primary: 'border-primary/30 border-t-primary',
    white: 'border-white/30 border-t-white',
  };

  return (
    <div className={`inline-flex items-center justify-center gap-2.5 ${className}`}>
      <div
        className={`${sizeClasses[size] || sizeClasses.md} ${colorClasses[color] || colorClasses.accent} rounded-full animate-spin`}
        role="status"
        aria-label="Đang tải..."
      />
      {text && <span className="text-sm font-body text-text-secondary">{text}</span>}
    </div>
  );
}