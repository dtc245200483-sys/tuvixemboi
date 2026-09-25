import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import {
  IconLayoutDashboard,
  IconCompass,
  IconChartBar,
  IconCoins,
  IconEye,
  IconMessageCircle,
} from '@tabler/icons-react';
import { useAuthStore } from '../store/authStore';

export default function MobileBottomNav() {
  const location = useLocation();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  // Ẩn thanh điều hướng nếu chưa đăng nhập hoặc đang ở các trang không phù hợp (login, register, chat)
  const hiddenRoutes = ['/login', '/register', '/chat'];
  if (!isAuthenticated || hiddenRoutes.includes(location.pathname)) {
    return null;
  }

  const navItems = [
    { path: '/dashboard', label: 'Tổng quan', icon: IconLayoutDashboard },
    { path: '/tu-vi', label: 'Tử Vi', icon: IconCompass },
    { path: '/bat-tu', label: 'Bát Tự', icon: IconChartBar },
    { path: '/kinh-dich', label: 'Kinh Dịch', icon: IconCoins },
    { path: '/nhan-tuong', label: 'Tướng Học', icon: IconEye },
    { path: '/chat', label: 'AI Chat', icon: IconMessageCircle, isSpecial: true },
  ];

  return (
    <nav
      className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-[#FAF6EE]/95 backdrop-blur-md border-t border-[#D5C9B8]/70 shadow-[0_-2px_10px_rgba(0,0,0,0.06)]"
      style={{ paddingBottom: 'max(0.4rem, env(safe-area-inset-bottom))' }}
      aria-label="Thanh điều hướng di động"
    >
      <div className="flex items-center justify-around px-1 py-1.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center justify-center flex-1 py-1 px-0.5 rounded-lg transition-all duration-150 active:scale-95 ${
                item.isSpecial
                  ? isActive
                    ? 'text-[#8B1C13] font-bold'
                    : 'text-[#8B1C13]/85 hover:text-[#8B1C13]'
                  : isActive
                  ? 'text-[#8B1C13] font-bold'
                  : 'text-[#6B5A4D] hover:text-[#2C2420]'
              }`}
            >
              <div
                className={`relative flex items-center justify-center w-7 h-7 rounded-full transition-all ${
                  isActive
                    ? 'bg-[#8B1C13]/10 text-[#8B1C13]'
                    : item.isSpecial
                    ? 'bg-[#D4AF37]/20 text-[#8B1C13]'
                    : 'text-current'
                }`}
              >
                <Icon size={19} stroke={isActive ? 2.2 : 1.75} />
                {isActive && (
                  <span className="absolute -bottom-0.5 w-1 h-1 rounded-full bg-[#8B1C13]" />
                )}
              </div>
              <span
                className={`text-[10px] font-body mt-0.5 tracking-tight ${
                  isActive ? 'font-bold text-[#8B1C13]' : 'font-medium'
                }`}
              >
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
