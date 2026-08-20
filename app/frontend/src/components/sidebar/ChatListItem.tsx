import { useState, useRef, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Pencil, Trash2, Check, X } from 'lucide-react';
import { toast } from 'sonner';
import { deleteChat, updateChat } from '../../api/chats';
import { useChatStore } from '../../store/chatStore';
import type { Chat } from '../../types';

interface ChatListItemProps {
  chat: Chat;
  isActive: boolean;
}

export default function ChatListItem({ chat, isActive }: ChatListItemProps) {
  const navigate = useNavigate();
  const { chatId } = useParams();
  const { removeChat, updateChatTitle, chats } = useChatStore();

  const [isRenaming, setIsRenaming] = useState(false);
  const [renameValue, setRenameValue] = useState(chat.title ?? 'New Chat');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const renameInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isRenaming) renameInputRef.current?.select();
  }, [isRenaming]);

  async function handleRenameConfirm() {
    const trimmed = renameValue.trim();
    if (!trimmed || trimmed === (chat.title ?? 'New Chat')) {
      setIsRenaming(false);
      return;
    }
    try {
      await updateChat(chat.chat_id, trimmed);
      updateChatTitle(chat.chat_id, trimmed);
    } catch {
      toast.error('Failed to rename chat.');
    } finally {
      setIsRenaming(false);
    }
  }

  async function handleDelete() {
    setIsDeleting(true);
    const previousChats = [...chats];
    removeChat(chat.chat_id);

    try {
      await deleteChat(chat.chat_id);
      if (Number(chatId) === chat.chat_id) {
        const remaining = previousChats.filter((c) => c.chat_id !== chat.chat_id);
        navigate(remaining.length ? `/chat/${remaining[0].chat_id}` : '/', { replace: true });
      }
    } catch {
      // Rollback optimistic delete
      useChatStore.setState({ chats: previousChats });
      toast.error('Failed to delete chat.');
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  }

  const displayTitle = chat.title ?? 'New Chat';

  return (
    <div
      className={`group relative flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
        isActive
          ? 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700/50'
      }`}
      onClick={() => !isRenaming && navigate(`/chat/${chat.chat_id}`)}
    >
      {isRenaming ? (
        <input
          ref={renameInputRef}
          value={renameValue}
          onChange={(e) => setRenameValue(e.target.value)}
          onBlur={handleRenameConfirm}
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleRenameConfirm();
            if (e.key === 'Escape') setIsRenaming(false);
          }}
          onClick={(e) => e.stopPropagation()}
          className="flex-1 min-w-0 bg-transparent text-sm outline-none border-b border-blue-500"
        />
      ) : (
        <span className="flex-1 min-w-0 text-sm truncate">{displayTitle}</span>
      )}

      {/* Action buttons — visible on hover or when active */}
      {!isRenaming && !showDeleteConfirm && (
        <div
          className={`flex items-center gap-1 shrink-0 ${
            isActive ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
          } transition-opacity`}
          onClick={(e) => e.stopPropagation()}
        >
          <button
            title="Rename"
            onClick={() => { setIsRenaming(true); setRenameValue(displayTitle); }}
            className="p-1 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            <Pencil size={13} />
          </button>
          <button
            title="Delete"
            onClick={() => setShowDeleteConfirm(true)}
            className="p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/40 text-gray-500 hover:text-red-600 dark:hover:text-red-400 transition-colors"
          >
            <Trash2 size={13} />
          </button>
        </div>
      )}

      {/* Inline delete confirmation */}
      {showDeleteConfirm && (
        <div
          className="flex items-center gap-1 shrink-0"
          onClick={(e) => e.stopPropagation()}
        >
          <span className="text-xs text-gray-500 dark:text-gray-400">Delete?</span>
          <button
            title="Confirm"
            disabled={isDeleting}
            onClick={handleDelete}
            className="p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/40 text-red-600 dark:text-red-400 transition-colors disabled:opacity-50"
          >
            <Check size={13} />
          </button>
          <button
            title="Cancel"
            onClick={() => setShowDeleteConfirm(false)}
            className="p-1 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            <X size={13} />
          </button>
        </div>
      )}
    </div>
  );
}
