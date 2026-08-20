import { useNavigate } from 'react-router-dom';
import { Plus } from 'lucide-react';
import { toast } from 'sonner';
import { createChat } from '../../api/chats';
import { useChatStore } from '../../store/chatStore';
import ChatList from './ChatList';
import UserMenu from './UserMenu';

export default function Sidebar() {
  const navigate = useNavigate();
  const prependChat = useChatStore((s) => s.prependChat);

  async function handleNewChat() {
    try {
      const chat = await createChat();
      prependChat(chat);
      navigate(`/chat/${chat.chat_id}`);
    } catch {
      toast.error('Failed to create chat.');
    }
  }

  return (
    <aside className="flex flex-col h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800">
      {/* Header */}
      <div className="px-3 pt-4 pb-2 shrink-0">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          <Plus size={16} />
          New chat
        </button>
      </div>

      {/* Chat list */}
      <ChatList />

      {/* User menu */}
      <UserMenu />
    </aside>
  );
}
