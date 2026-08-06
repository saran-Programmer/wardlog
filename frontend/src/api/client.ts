import { AxiosError } from 'axios'
import { httpClient } from './httpClient'

export class ApiError extends Error {
  status: number
  details?: Record<string, string>

  constructor(status: number, message: string, details?: Record<string, string>) {
    super(message)
    this.status = status
    this.details = details
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  body?: unknown
}

interface ErrorBody {
  error?: string
  details?: Record<string, string>
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body } = options

  try {
    const response = await httpClient.request<T>({ url: path, method, data: body })
    return response.data
  } catch (err) {
    const axiosError = err as AxiosError<ErrorBody>
    if (axiosError.response) {
      const data = axiosError.response.data
      throw new ApiError(axiosError.response.status, data?.error ?? 'Something went wrong', data?.details)
    }
    throw err
  }
}
