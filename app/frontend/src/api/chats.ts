import { apiClient } from './client';
import type { Chat, ChatsResponse, ChatDeleteResponse } from '../types';

export async function getChats(): Promise<ChatsResponse> {
  const res = await apiClient.get<ChatsResponse>('/chats');
  return res.data;
}

export async function createChat(): Promise<Chat> {
  const res = await apiClient.post<Chat>('/chats');
  return res.data;
}

export async function deleteChat(chatId: number): Promise<ChatDeleteResponse> {
  const res = await apiClient.delete<ChatDeleteResponse>(`/chats/${chatId}`);
  return res.data;
}

export async function updateChat(chatId: number, title: string): Promise<Chat> {
  const res = await apiClient.patch<Chat>(`/chats/${chatId}`, { title });
  return res.data;
}
