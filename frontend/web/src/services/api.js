import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const BASE_URL = (import.meta.env.VITE_API_URL !== undefined && import.meta.env.VITE_API_URL !== '')
  ? import.meta.env.VITE_API_URL
  : (import.meta.env.PROD ? '' : 'http://localhost:8000');

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Flag và queue để tránh gọi refresh token trùng lặp khi nhiều request đồng thời bị 401
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

/**
 * 1. Request Interceptor: Tự động gắn Bearer Token vào mọi request nếu đã đăng nhập
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * 2. Response Interceptor: Xử lý lỗi 401 & Tự động gọi Refresh Token
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Nếu không có response (lỗi mạng hoặc server offline)
    if (!error.response) {
      return Promise.reject(new Error('Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại mạng.'));
    }

    const isAuthRoute =
      originalRequest.url.includes('/auth/login') ||
      originalRequest.url.includes('/auth/register') ||
      originalRequest.url.includes('/auth/refresh');

    // Nếu lỗi 401 và không phải là route login/register/refresh
    if (error.response.status === 401 && !originalRequest._retry && !isAuthRoute) {
      if (isRefreshing) {
        // Nếu đang trong tiến trình refresh, đẩy request này vào hàng đợi chờ
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = useAuthStore.getState().refreshToken;

      if (!refreshToken) {
        isRefreshing = false;
        useAuthStore.getState().logout();
        if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }

      try {
        // Gọi endpoint POST /auth/refresh
        const res = await axios.post(`${BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const newAccessToken = res.data.access_token;
        useAuthStore.getState().setAccessToken(newAccessToken);

        apiClient.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`;
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

        processQueue(null, newAccessToken);
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        useAuthStore.getState().logout();
        if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// Các hàm gọi API tiện ích
export const authService = {
  register: (email, password, confirm_password) =>
    apiClient.post('/auth/register', { email, password, confirm_password }),

  login: (email, password) => {
    // Backend yêu cầu FormData cho OAuth2 password flow: username & password
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    return apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },

  getMe: () => apiClient.get('/auth/me'),
  changePassword: (data) => apiClient.put('/auth/change-password', data),
  deleteAccount: (data) => apiClient.delete('/auth/me', { data }),
};

export const birthProfileService = {
  create: (data) => apiClient.post('/birth-profile', data),
  anSao: (data) => apiClient.post('/birth-profile/an-sao', data),
  setDefault: (id) => apiClient.put(`/birth-profile/${id}/set-default`),
  getAll: () => apiClient.get('/birth-profile'),
  getById: (id) => apiClient.get(`/birth-profile/${id}`),
  update: (id, data) => apiClient.put(`/birth-profile/${id}`, data),
  delete: (id) => apiClient.delete(`/birth-profile/${id}`),
};

export const tuViService = {
  getLaSo: (birthProfileId, onlyChart = false) =>
    apiClient.get(`/tu-vi/${birthProfileId}`, { params: { only_chart: onlyChart } }),
  getChartOnly: (birthProfileId) =>
    apiClient.get(`/tu-vi/${birthProfileId}/chart`),
  getTopicInterpretation: (birthProfileId, topic) =>
    apiClient.get(`/tu-vi/${birthProfileId}/topic`, { params: { topic } }),
  chatWithChart: (birthProfileId, cauHoi) =>
    apiClient.post(`/tu-vi/${birthProfileId}/chat`, { cau_hoi: cauHoi }),
};

export const batTuService = {
  getTuTru: (birthProfileId) => apiClient.get(`/bat-tu/${birthProfileId}`),
};

export const kinhDichService = {
  gieoQue: (data) => apiClient.post('/gieo-que', data),
};

export const nhanTuongService = {
  xemTay: (formData) =>
    apiClient.post('/xem-tuong/tay', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  xemMat: (formData) =>
    apiClient.post('/xem-tuong/mat', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

export const visionService = {
  getConsent: () => apiClient.get('/vision/consent'),
  postConsent: () => apiClient.post('/vision/consent'),
  uploadMat: (formData) =>
    apiClient.post('/vision/upload-mat', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  uploadTay: (formData) =>
    apiClient.post('/vision/upload-tay', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  deleteAnh: (id) => apiClient.delete(`/vision/anh/${id}`),
  getMyPhotos: () => apiClient.get('/vision/anh-cua-toi'),
};

export const quotaService = {
  getQuota: () => apiClient.get('/quota'),
  upgradePremium: () => apiClient.post('/quota/upgrade-premium'),
};

export const chatService = {
  sendMessage: (data) => apiClient.post('/chat', data),
  getHistory: (params) => apiClient.get('/chat/history', { params }),

  // --- Quản lý phiên trò chuyện (Chat Sessions) ---
  getSessions: () => apiClient.get('/chat/sessions'),
  createSession: (data) => apiClient.post('/chat/sessions', data),
  deleteSession: (sessionId) => apiClient.delete(`/chat/sessions/${sessionId}`),
  getSessionMessages: (sessionId, params) =>
    apiClient.get(`/chat/sessions/${sessionId}/messages`, { params }),
};

export const forumService = {
  getPosts: (params) => apiClient.get('/forum/posts', { params }),
  createPost: (data) => apiClient.post('/forum/posts', data),
  getPost: (id) => apiClient.get(`/forum/posts/${id}`),
  deletePost: (id) => apiClient.delete(`/forum/posts/${id}`),
  createComment: (postId, data) => apiClient.post(`/forum/posts/${postId}/comments`, data),
  deleteComment: (commentId) => apiClient.delete(`/forum/comments/${commentId}`),
};

export default apiClient;