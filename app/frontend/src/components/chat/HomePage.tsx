import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../../store/chatStore';
import EmptyState from './EmptyState';

export default function HomePage() {
  const navigate = useNavigate();
  const chats = useChatStore((s) => s.chats);
  const isLoadingChats = useChatStore((s) => s.isLoadingChats);

  useEffect(() => {
    if (!isLoadingChats && chats.length > 0) {
      navigate(`/chat/${chats[0].chat_id}`, { replace: true });
    }
  }, [isLoadingChats, chats, navigate]);

  if (isLoadingChats) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-950">
        <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-50 dark:bg-gray-950">
      <EmptyState />
    </div>
  );
}
