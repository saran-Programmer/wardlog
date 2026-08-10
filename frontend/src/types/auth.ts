export type ToneType = 'WARM' | 'FUNNY' | 'PROFESSIONAL'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name: string
  age?: number
  sex?: string
  speciality?: string
  tone: ToneType
  assistantName?: string
}

export interface UserResponse {
  id: string
  email: string
  name: string
  age?: number
  sex?: string
  speciality?: string
  tone: string
  assistantName?: string
}

export interface UpdateProfileRequest {
  name?: string
  age?: number
  sex?: string
  speciality?: string
  tone?: ToneType
  assistantName?: string
}

export interface AuthResponse {
  accessToken: string
  user: UserResponse
}
