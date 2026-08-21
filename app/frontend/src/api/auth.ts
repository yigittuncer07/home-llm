// src/api/auth.ts
import { apiClient } from './client';
import type { LoginRequest, LoginResponse } from '../types';

export async function login(data: LoginRequest): Promise<LoginResponse> {
  const res = await apiClient.post<LoginResponse>('/auth/login', data);
  return res.data;
}

export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout');
}