// src/store/authStore.ts
import { create } from 'zustand';
import { setClientToken } from '../api/client';

interface AuthState {
  token: string | null;
  userEmail: string | null;
  isAdmin: boolean;
  setAuth: (token: string, email?: string) => void;
  clearAuth: () => void;
}

// JWT payload carries role:'admin' for admin users
function isAdminFromToken(token: string | null): boolean {
  if (!token) return false;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.role === 'admin';
  } catch {
    return false;
  }
}

// Rehydrate synchronously so ProtectedRoute sees the token on first render
const _storedToken = localStorage.getItem('auth_token');
const _storedEmail = localStorage.getItem('user_email');
if (_storedToken) setClientToken(_storedToken);

export const useAuthStore = create<AuthState>((set) => ({
  token: _storedToken,
  userEmail: _storedEmail,
  isAdmin: isAdminFromToken(_storedToken),

  setAuth: (token, email) => {
    localStorage.setItem('auth_token', token);
    if (email) localStorage.setItem('user_email', email);
    setClientToken(token);
    set({ token, userEmail: email ?? null, isAdmin: isAdminFromToken(token) });
  },

  clearAuth: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_email');
    setClientToken(null);
    set({ token: null, userEmail: null, isAdmin: false });
  },
}));
