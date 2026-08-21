// src/store/chatStore.ts
import { create } from 'zustand';
import type { Chat, Message } from '../types';

interface StreamingMessage {
  content: string;
  interrupted: boolean;
}

interface ChatState {
  chats: Chat[];
  isLoadingChats: boolean;
  messagesByChat: Record<number, Message[]>;
  streamingMessage: StreamingMessage | null;
  isStreaming: boolean;

  setChats: (chats: Chat[]) => void;
  prependChat: (chat: Chat) => void;
  removeChat: (chatId: number) => void;
  updateChatTitle: (chatId: number, title: string) => void;
  setLoadingChats: (loading: boolean) => void;

  setMessages: (chatId: number, messages: Message[]) => void;
  appendMessage: (chatId: number, message: Message) => void;

  startStreaming: () => void;
  appendStreamToken: (token: string) => void;
  finalizeStream: (chatId: number) => void;
  interruptStream: () => void;
  clearStreamingMessage: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  chats: [],
  isLoadingChats: true,
  messagesByChat: {},
  streamingMessage: null,
  isStreaming: false,

  setChats: (chats) => set({ chats, isLoadingChats: false }),
  prependChat: (chat) => set((s) => ({ chats: [chat, ...s.chats] })),
  removeChat: (chatId) =>
    set((s) => ({ chats: s.chats.filter((c) => c.chat_id !== chatId) })),
  updateChatTitle: (chatId, title) =>
    set((s) => ({
      chats: s.chats.map((c) => (c.chat_id === chatId ? { ...c, title } : c)),
    })),
  setLoadingChats: (loading) => set({ isLoadingChats: loading }),

  setMessages: (chatId, messages) =>
    set((s) => ({ messagesByChat: { ...s.messagesByChat, [chatId]: messages } })),
  appendMessage: (chatId, message) =>
    set((s) => ({
      messagesByChat: {
        ...s.messagesByChat,
        [chatId]: [...(s.messagesByChat[chatId] ?? []), message],
      },
    })),

  startStreaming: () =>
    set({ isStreaming: true, streamingMessage: { content: '', interrupted: false } }),

  appendStreamToken: (token) =>
    set((s) => ({
      streamingMessage: s.streamingMessage
        ? { ...s.streamingMessage, content: s.streamingMessage.content + token }
        : { content: token, interrupted: false },
    })),

  finalizeStream: (chatId) => {
    const { streamingMessage, messagesByChat } = get();
    if (!streamingMessage) return;

    // Synthetic ID — real ID will appear in the next GET /chats/{id}/messages
    const assistantMessage: Message = {
      message_id: Date.now(),
      chat_id: chatId,
      model: '',
      tokens: null,
      role: 'assistant',
      content: streamingMessage.content,
      timestamp: new Date().toISOString(),
    };

    set({
      isStreaming: false,
      streamingMessage: null,
      messagesByChat: {
        ...messagesByChat,
        [chatId]: [...(messagesByChat[chatId] ?? []), assistantMessage],
      },
    });
  },

  interruptStream: () =>
    set((s) => ({
      isStreaming: false,
      streamingMessage: s.streamingMessage
        ? { ...s.streamingMessage, interrupted: true }
        : null,
    })),

  clearStreamingMessage: () => set({ streamingMessage: null, isStreaming: false }),
}));
