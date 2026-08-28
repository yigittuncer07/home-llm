// src/api/admin.ts

import { apiClient } from './client';
import type { AdminUser, UpdateTokensRequest, TokenBalanceResponse } from '../types';

export async function getAdminUsers(params?: { skip?: number; limit?: number }): Promise<AdminUser[]> {
  const res = await apiClient.get<AdminUser[]>('/admin/users', { params });
  return res.data;
}

export async function createAdminUser(data: { email: string; password: string; is_admin?: boolean }): Promise<AdminUser> {
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

export async function massUpdateTokens(payload: { model_name: string; balance: number }) {
  const response = await apiClient.patch('/admin/users/tokens', payload);
  return response.data;
}