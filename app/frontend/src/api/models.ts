import { apiClient } from './client';
import type { ModelBalance } from '../types';

export async function getModels(): Promise<ModelBalance[]> {
  const res = await apiClient.get<ModelBalance[]>('/models');
  return res.data;
}
