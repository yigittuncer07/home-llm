import { create } from 'zustand';

type Theme = 'light' | 'dark' | 'system';

interface UIState {
  sidebarOpen: boolean;
  theme: Theme;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setTheme: (theme: Theme) => void;
  initTheme: () => void;
}

function applyTheme(theme: Theme): void {
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const shouldBeDark = theme === 'dark' || (theme === 'system' && prefersDark);
  document.documentElement.classList.toggle('dark', shouldBeDark);
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: window.innerWidth >= 768,
  theme: 'system',

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  setTheme: (theme) => {
    localStorage.setItem('theme', theme);
    applyTheme(theme);
    set({ theme });
  },

  initTheme: () => {
    const stored = (localStorage.getItem('theme') as Theme | null) ?? 'system';
    applyTheme(stored);
    set({ theme: stored });

    // Keep 'system' theme in sync with OS preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      const current = (localStorage.getItem('theme') as Theme | null) ?? 'system';
      if (current === 'system') applyTheme('system');
    });
  },
}));
