import { apiClient } from './client';
import type { ChatHistoryResponse, SendMessageRequest } from '../types';

export async function getChatHistory(chatId: number): Promise<ChatHistoryResponse> {
  const res = await apiClient.get<ChatHistoryResponse>(`/chats/${chatId}/messages`);
  return res.data;
}

// Returns 202 Accepted; the assistant reply arrives via SSE, not in this response.
export async function sendMessage(
  chatId: number,
  data: SendMessageRequest,
): Promise<{ message: string }> {
  const res = await apiClient.post<{ message: string }>(`/chats/${chatId}/messages`, data);
  return res.data;
}
