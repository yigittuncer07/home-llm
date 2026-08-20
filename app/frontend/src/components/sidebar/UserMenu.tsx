import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Settings, LogOut, Sun, Moon, Monitor } from 'lucide-react';
import { toast } from 'sonner';
import { logout } from '../../api/auth';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';

export default function UserMenu() {
  const navigate = useNavigate();
  const userEmail = useAuthStore((s) => s.userEmail);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const { theme, setTheme } = useUIStore();

  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  async function handleLogout() {
    setOpen(false);
    try {
      await logout();
    } catch {
      // Ignore errors — we clear local state regardless
    }
    clearAuth();
    navigate('/login', { replace: true });
  }

  const initial = (userEmail ?? '?')[0].toUpperCase();
  const themeIcons = { light: Sun, dark: Moon, system: Monitor } as const;
  const cycleTheme = () => {
    const next = theme === 'system' ? 'light' : theme === 'light' ? 'dark' : 'system';
    setTheme(next);
  };

  const ThemeIcon = themeIcons[theme];

  return (
    <div ref={menuRef} className="relative px-2 py-2 border-t border-gray-200 dark:border-gray-700">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors text-left"
      >
        <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-semibold shrink-0">
          {initial}
        </div>
        <span className="flex-1 min-w-0 text-sm text-gray-700 dark:text-gray-300 truncate">
          {userEmail ?? 'User'}
        </span>
      </button>

      {open && (
        <div className="absolute bottom-full left-2 right-2 mb-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg py-1 z-50">
          <button
            onClick={() => { setOpen(false); navigate('/settings'); }}
            className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <Settings size={15} />
            Settings
          </button>

          <button
            onClick={cycleTheme}
            className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <ThemeIcon size={15} />
            Theme: {theme.charAt(0).toUpperCase() + theme.slice(1)}
          </button>

          <hr className="my-1 border-gray-200 dark:border-gray-700" />

          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
          >
            <LogOut size={15} />
            Log out
          </button>
        </div>
      )}
    </div>
  );
}
