import { apiClient } from './client';
import type { UserConfig } from '../types';

export async function getUserConfig(): Promise<UserConfig> {
  const res = await apiClient.get<UserConfig>('/user/config');
  return res.data;
}

export async function updateUserConfig(data: Partial<UserConfig>): Promise<UserConfig> {
  const res = await apiClient.patch<UserConfig>('/user/config', data);
  return res.data;
}
