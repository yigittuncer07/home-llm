import { useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { getChats } from '../../api/chats';
import { useChatStore } from '../../store/chatStore';
import { useUIStore } from '../../store/uiStore';
import Sidebar from '../sidebar/Sidebar';

export default function MainLayout() {
  const navigate = useNavigate();
  const { setChats } = useChatStore();
  const { sidebarOpen, toggleSidebar, setSidebarOpen } = useUIStore();

  // Load chats once on mount
  useEffect(() => {
    getChats()
      .then(({ chats }) => setChats(chats))
      .catch(() => {
        // 401 is handled by the Axios interceptor (redirect to /login).
        // Other errors are silent here — the sidebar will show an empty state.
      });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Close sidebar on mobile when navigating
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) setSidebarOpen(false);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [setSidebarOpen]);

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-20 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } fixed md:relative md:translate-x-0 z-30 md:z-auto h-full w-64 transition-transform duration-200 ease-in-out shrink-0`}
      >
        <Sidebar />
      </div>

      {/* Main content */}
      <div className="flex flex-col flex-1 min-w-0 min-h-0">
        {/* Mobile top bar */}
        <div className="flex items-center h-12 px-3 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 md:hidden shrink-0">
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>

        <Outlet />
      </div>
    </div>
  );
}
