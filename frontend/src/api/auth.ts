import { apiRequest } from './client'
import type { AuthResponse, LoginRequest, RegisterRequest } from '../types/auth'

export function login(request: LoginRequest): Promise<AuthResponse> {
  return apiRequest<AuthResponse>('/api/v1/auth/login', {
    method: 'POST',
    body: request,
  })
}

export function register(request: RegisterRequest): Promise<AuthResponse> {
  return apiRequest<AuthResponse>('/api/v1/auth/register', {
    method: 'POST',
    body: request,
  })
}

export function refreshToken(): Promise<{ accessToken: string }> {
  return apiRequest<{ accessToken: string }>('/api/v1/auth/refresh', {
    method: 'POST',
  })
}
