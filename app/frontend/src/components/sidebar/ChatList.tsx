import { useParams } from 'react-router-dom';
import { useChatStore } from '../../store/chatStore';
import ChatListItem from './ChatListItem';

function SkeletonItem() {
  return (
    <div className="px-3 py-2 rounded-lg">
      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-3/4" />
    </div>
  );
}

export default function ChatList() {
  const chats = useChatStore((s) => s.chats);
  const isLoadingChats = useChatStore((s) => s.isLoadingChats);
  const { chatId } = useParams();

  if (isLoadingChats) {
    return (
      <div className="flex-1 overflow-y-auto px-2 py-1 space-y-1">
        {Array.from({ length: 5 }).map((_, i) => (
          <SkeletonItem key={i} />
        ))}
      </div>
    );
  }

  if (!chats.length) {
    return (
      <div className="flex-1 flex items-center justify-center px-4">
        <p className="text-xs text-gray-400 dark:text-gray-500 text-center">
          No chats yet. Click "New chat" to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-2 py-1 space-y-0.5">
      {chats.map((chat) => (
        <ChatListItem
          key={chat.chat_id}
          chat={chat}
          isActive={Number(chatId) === chat.chat_id}
        />
      ))}
    </div>
  );
}
