import axios from 'axios';
import { useAuthStore } from '../stores/authStore';

export const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // required for HttpOnly refresh cookie
});

// Request interceptor to attach tokens and workspace ID
apiClient.interceptors.request.use((config) => {
  const { accessToken, activeWorkspaceId } = useAuthStore.getState();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  if (activeWorkspaceId) {
    config.headers['X-Workspace-ID'] = activeWorkspaceId;
  }
  return config;
});

// Response interceptor to handle 401s
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const { data } = await axios.post(
          'http://localhost:8000/api/v1/auth/refresh',
          {},
          { withCredentials: true }
        );
        useAuthStore.getState().setToken(data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    if (error.response?.status === 422) {
      const details = error.response.data?.detail;
      const isWorkspaceError = Array.isArray(details) && details.some((d: any) => 
        d.loc?.includes('x-workspace-id') || d.loc?.includes('X-Workspace-ID')
      );
      if (isWorkspaceError) {
        return Promise.reject(new Error('Missing X-Workspace-ID header. Please select a workspace.'));
      }
    }
    
    return Promise.reject(error);
  }
);
