import { useEffect } from 'react';
import { useChatStore } from '../../store/chatStore';
import { useAutoScroll } from '../../hooks/useAutoScroll';
import { MessageBubbleFromMessage } from './MessageBubble';
import MessageBubble from './MessageBubble';

interface MessageListProps {
  chatId: number;
}

export default function MessageList({ chatId }: MessageListProps) {
  const messages = useChatStore((s) => s.messagesByChat[chatId] ?? []);
  const streamingMessage = useChatStore((s) => s.streamingMessage);
  const isStreaming = useChatStore((s) => s.isStreaming);

  // Track both message array and streaming content for scroll triggers
  const scrollDependency = `${messages.length}-${streamingMessage?.content?.length ?? 0}`;
  const { containerRef, scrollToBottom } = useAutoScroll(scrollDependency);

  // Jump to bottom instantly on initial load
  useEffect(() => {
    scrollToBottom();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chatId]);

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto py-4 space-y-1 scroll-smooth"
    >
      {messages.map((msg) => (
        <MessageBubbleFromMessage key={msg.message_id} message={msg} />
      ))}

      {/* In-flight streaming message */}
      {(isStreaming || streamingMessage) && (
        <MessageBubble
          role="assistant"
          content={streamingMessage?.content ?? ''}
          isStreaming={isStreaming}
          interrupted={streamingMessage?.interrupted}
        />
      )}

      {/* Interrupted state with finished content */}
      {streamingMessage?.interrupted && !isStreaming && (
        <MessageBubble
          role="assistant"
          content={streamingMessage.content}
          interrupted
        />
      )}
    </div>
  );
}
