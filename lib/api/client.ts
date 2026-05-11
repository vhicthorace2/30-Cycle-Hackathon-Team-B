import axios from 'axios';
import type { AxiosError, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '../auth/store';
import { API_ENDPOINTS } from './endpoints';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000',
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue: Array<{ resolve: (token: string) => void; reject: (error: unknown) => void }> = [];

type RetryableAxiosConfig = InternalAxiosRequestConfig & { _retry?: boolean };
type SkipRedirectAxiosConfig = AxiosRequestConfig & { headers?: Record<string, string> };

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((item) => {
    if (token) item.resolve(token);
    else item.reject(error);
  });
  failedQueue = [];
};

api.interceptors.request.use((config) => {
  const { accessToken, currentTenant } = useAuthStore.getState();
  if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`;
  if (currentTenant) config.headers['X-Tenant-ID'] = currentTenant.id;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableAxiosConfig | undefined;
    if (!originalRequest) return Promise.reject(error);
    const skipRedirect = originalRequest.headers?.['X-Skip-Auth-Redirect'] === 'true';

    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/auth/')) {
      if (skipRedirect) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        }).catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const { refreshToken } = useAuthStore.getState();
        if (!refreshToken) throw new Error('No refresh token available');
        
        const refreshUrl = `${process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '') || 'http://localhost:3000'}${API_ENDPOINTS.auth.refresh}`;
        const { data } = await axios.post<{ accessToken: string; refreshToken: string }>(refreshUrl, { refreshToken }, { withCredentials: true });
        const newToken = data.accessToken;
        const newRefreshToken = data.refreshToken;
        useAuthStore.getState().updateToken(newToken, newRefreshToken);

        processQueue(null, newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

export const skipAuthRedirectConfig: SkipRedirectAxiosConfig = {
  withCredentials: true,
  headers: { 'X-Skip-Auth-Redirect': 'true' },
};

export default api;
