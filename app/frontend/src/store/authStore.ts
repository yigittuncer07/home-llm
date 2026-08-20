import { create } from 'zustand';
import { setClientToken } from '../api/client';

interface AuthState {
  token: string | null;
  userEmail: string | null;
  setAuth: (token: string, email?: string) => void;
  clearAuth: () => void;
  initFromStorage: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  userEmail: null,

  setAuth: (token, email) => {
    localStorage.setItem('auth_token', token);
    if (email) localStorage.setItem('user_email', email);
    setClientToken(token);
    set({ token, userEmail: email ?? null });
  },

  clearAuth: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_email');
    setClientToken(null);
    set({ token: null, userEmail: null });
  },

  initFromStorage: () => {
    const token = localStorage.getItem('auth_token');
    const email = localStorage.getItem('user_email');
    if (token) {
      setClientToken(token);
      set({ token, userEmail: email });
    }
  },
}));
