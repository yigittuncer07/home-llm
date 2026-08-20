import { useNavigate } from 'react-router-dom';
import { Plus, MessageSquare } from 'lucide-react';
import { toast } from 'sonner';
import { createChat } from '../../api/chats';
import { useChatStore } from '../../store/chatStore';

const SUGGESTIONS = [
  'Explain quantum computing in simple terms',
  'Write a Python function to reverse a linked list',
  'What are some best practices for REST API design?',
  'Help me debug this: TypeError: Cannot read property of undefined',
];

interface EmptyStateProps {
  onSuggestionClick?: (text: string) => void;
}

export default function EmptyState({ onSuggestionClick }: EmptyStateProps) {
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
    <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
      <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mb-4">
        <MessageSquare size={22} className="text-blue-600 dark:text-blue-400" />
      </div>
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
        How can I help you?
      </h2>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-8 max-w-xs">
        Start a new chat or choose a suggestion below.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg mb-6">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => onSuggestionClick?.(s)}
            className="text-left px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600 transition-colors"
          >
            {s}
          </button>
        ))}
      </div>

      <button
        onClick={handleNewChat}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors"
      >
        <Plus size={16} />
        New chat
      </button>
    </div>
  );
}
