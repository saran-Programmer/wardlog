import { apiRequest } from './client'
import type { UpdateProfileRequest, UserResponse } from '../types/auth'

export function getMe(): Promise<UserResponse> {
  return apiRequest<UserResponse>('/api/v1/users/me')
}

export function updateProfile(request: UpdateProfileRequest): Promise<UserResponse> {
  return apiRequest<UserResponse>('/api/v1/users/me', {
    method: 'PUT',
    body: request,
  })
}
