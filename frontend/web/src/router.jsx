import React from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import BirthProfileForm from './pages/birth-profile/BirthProfileForm';
import DashboardPage from './pages/dashboard/DashboardPage';
import TuViPage from './pages/tu-vi/TuViPage';
import BatTuPage from './pages/bat-tu/BatTuPage';
import KinhDichPage from './pages/kinh-dich/KinhDichPage';
import NhanTuongPage from './pages/nhan-tuong/NhanTuongPage';
import ChatPage from './pages/chat/ChatPage';
import SettingsPage from './pages/settings/SettingsPage';
import DesignPreview from './pages/DesignPreview';

/**
 * Component bọc bảo vệ Route:
 * - Yêu cầu đã đăng nhập (isAuthenticated = true).
 * - Nếu chưa đăng nhập, tự động chuyển hướng về /login và lưu lại location hiện tại.
 */
export function ProtectedRoute({ children }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

/**
 * Route công khai (Public only):
 * - Nếu đã đăng nhập, chuyển thẳng vào /dashboard
 */
export function PublicRoute({ children }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

export default function AppRoutes() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <Routes>
      {/* Route gốc */}
      <Route
        path="/"
        element={
          isAuthenticated ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />

      {/* Xác thực người dùng */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <RegisterPage />
          </PublicRoute>
        }
      />

      {/* Dashboard Chính (Yêu cầu đăng nhập) */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />

      {/* Hồ sơ ngày sinh (Yêu cầu đăng nhập) */}
      <Route
        path="/birth-profile"
        element={
          <ProtectedRoute>
            <BirthProfileForm />
          </ProtectedRoute>
        }
      />

      {/* 4 Hệ Thống Huyền Học */}
      <Route
        path="/tu-vi"
        element={
          <ProtectedRoute>
            <TuViPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/bat-tu"
        element={
          <ProtectedRoute>
            <BatTuPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/kinh-dich"
        element={
          <ProtectedRoute>
            <KinhDichPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/nhan-tuong"
        element={
          <ProtectedRoute>
            <NhanTuongPage />
          </ProtectedRoute>
        }
      />

            {/* Trò chuyện Huyền Học (Chat AI) */}
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <ChatPage />
          </ProtectedRoute>
        }
      />

            {/* Cài đặt & Quyền riêng tư (Prompt 8.4) */}
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        }
      />

      {/* Trang xem thử Design Tokens (Prompt 8.0) */}
      <Route path="/design-preview" element={<DesignPreview />} />

      {/* Mặc định chuyển về trang chủ */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
