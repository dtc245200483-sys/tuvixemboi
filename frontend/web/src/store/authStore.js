import { create } from 'zustand';

const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

// Khởi tạo state ban đầu từ localStorage nếu có
const initialAccessToken = typeof window !== 'undefined' ? localStorage.getItem(ACCESS_TOKEN_KEY) : null;
const initialRefreshToken = typeof window !== 'undefined' ? localStorage.getItem(REFRESH_TOKEN_KEY) : null;

export const useAuthStore = create((set, get) => ({
  user: null,
  accessToken: initialAccessToken,
  refreshToken: initialRefreshToken,
  isAuthenticated: Boolean(initialAccessToken),

  /**
   * Đăng nhập thành công: lưu trữ token vào localStorage và cập nhật Zustand store
   */
  login: (tokens, user = null) => {
    const access = tokens.access_token || tokens.accessToken;
    const refresh = tokens.refresh_token || tokens.refreshToken;

    if (typeof window !== 'undefined') {
      if (access) localStorage.setItem(ACCESS_TOKEN_KEY, access);
      if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
    }

    set({
      accessToken: access,
      refreshToken: refresh,
      user: user,
      isAuthenticated: Boolean(access),
    });
  },

  /**
   * Cập nhật access token mới (dùng sau khi tự động refresh thành công)
   */
  setAccessToken: (newAccessToken) => {
    if (typeof window !== 'undefined' && newAccessToken) {
      localStorage.setItem(ACCESS_TOKEN_KEY, newAccessToken);
    }
    set({ accessToken: newAccessToken, isAuthenticated: Boolean(newAccessToken) });
  },

  /**
   * Cập nhật thông tin người dùng
   */
  setUser: (user) => {
    set({ user });
  },

  /**
   * Đăng xuất: Xóa sạch token khỏi localStorage và đưa state về mặc định
   */
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
    }
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    });
  },
}));