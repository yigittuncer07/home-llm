import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { getChatHistory } from '../../api/messages';
import { sendMessage } from '../../api/messages';
import { useChatStore } from '../../store/chatStore';
import { useStream } from '../../hooks/useStream';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import EmptyState from './EmptyState';
import type { Message } from '../../types';

export default function ChatWindow() {
  const { chatId: chatIdStr } = useParams<{ chatId: string }>();
  const chatId = Number(chatIdStr);
  const navigate = useNavigate();

  const { setMessages, appendMessage, clearStreamingMessage, isStreaming } = useChatStore();
  const messages = useChatStore((s) => s.messagesByChat[chatId]);
  const { startStream, stopStream } = useStream(chatId);

  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [suggestionPrefill, setSuggestionPrefill] = useState('');

  useEffect(() => {
    if (!chatId) return;

    let cancelled = false;
    clearStreamingMessage();
    setIsLoadingMessages(true);

    getChatHistory(chatId)
      .then(({ messages: msgs }) => {
        if (!cancelled) setMessages(chatId, msgs);
      })
      .catch(() => {
        if (!cancelled) toast.error('Failed to load messages.');
      })
      .finally(() => {
        if (!cancelled) setIsLoadingMessages(false);
      });

    return () => {
      cancelled = true;
      stopStream();
      clearStreamingMessage();
    };
  }, [chatId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleSend(prompt: string, model: string) {
    const optimisticMsg: Message = {
      message_id: Date.now(),
      chat_id: chatId,
      model,
      tokens: null,
      role: 'user',
      content: prompt,
      timestamp: new Date().toISOString(),
    };
    appendMessage(chatId, optimisticMsg);

    try {
      await sendMessage(chatId, { prompt, model });
      // 202 accepted — open SSE stream to receive the assistant reply
      startStream();
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } }).response?.status;
      if (status !== 401) {
        toast.error('Failed to send message.');
      }
    }
  }

  if (!chatId || isNaN(chatId)) {
    navigate('/', { replace: true });
    return null;
  }

  if (isLoadingMessages) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  const hasMessages = (messages?.length ?? 0) > 0;

  return (
    <div className="flex-1 flex flex-col min-h-0 bg-gray-50 dark:bg-gray-950">
      {hasMessages || isStreaming ? (
        <MessageList chatId={chatId} />
      ) : (
        <EmptyState onSuggestionClick={setSuggestionPrefill} />
      )}

      <MessageInput
        onSend={handleSend}
        onStop={stopStream}
        isStreaming={isStreaming}
        initialValue={suggestionPrefill}
        onInitialValueConsumed={() => setSuggestionPrefill('')}
      />
    </div>
  );
}
