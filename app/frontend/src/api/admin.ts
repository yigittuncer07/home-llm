import { apiClient } from './client';
import type { AdminUser, UpdateTokensRequest, TokenBalanceResponse } from '../types';

export async function getAdminUsers(): Promise<AdminUser[]> {
  const res = await apiClient.get<AdminUser[]>('/admin/users');
  return res.data;
}

export async function createAdminUser(data: { email: string; password: string }): Promise<AdminUser> {
  const res = await apiClient.post<AdminUser>('/admin/users', data);
  return res.data;
}

export async function deleteAdminUser(userId: number): Promise<void> {
  await apiClient.delete(`/admin/users/${userId}`);
}

export async function updateUserTokens(
  userId: number,
  data: UpdateTokensRequest,
): Promise<TokenBalanceResponse> {
  const res = await apiClient.patch<TokenBalanceResponse>(`/admin/users/${userId}/tokens`, data);
  return res.data;
}
