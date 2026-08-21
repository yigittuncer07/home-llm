import axios from 'axios';

export const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Holds the current token in module scope so interceptors can access it without
// importing the Zustand store (which would create a circular dependency).
let currentToken: string | null = null;

export function setClientToken(token: string | null): void {
  currentToken = token;
}

apiClient.interceptors.request.use((config) => {
  if (currentToken) {
    config.headers.Authorization = `Bearer ${currentToken}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only force-logout on 401s from authenticated requests, not from the login endpoint itself
    if (error.response?.status === 401 && currentToken) {
      setClientToken(null);
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_email');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);
