import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { clearAccessToken, getAccessToken, setAccessToken } from '../lib/tokenStore'

const BASE_URL = import.meta.env.VITE_API_BASE_URL
const REFRESH_PATH = '/api/v1/auth/refresh'

export const httpClient = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
})

httpClient.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

interface RetriableConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

let isRefreshing = false
let refreshQueue: Array<(token: string | null) => void> = []

function queueRequest(): Promise<string | null> {
  return new Promise((resolve) => {
    refreshQueue.push(resolve)
  })
}

function flushQueue(token: string | null) {
  refreshQueue.forEach((resolve) => resolve(token))
  refreshQueue = []
}

function goToLogin() {
  clearAccessToken()
  window.location.href = '/login'
}

httpClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriableConfig | undefined

    if (error.response?.status !== 401 || !originalRequest) {
      return Promise.reject(error)
    }

    // The refresh call itself failed, or this request was already retried once — stop here.
    if (originalRequest.url?.includes(REFRESH_PATH) || originalRequest._retry) {
      goToLogin()
      return Promise.reject(error)
    }

    originalRequest._retry = true

    if (isRefreshing) {
      const token = await queueRequest()
      if (!token) return Promise.reject(error)
      originalRequest.headers.Authorization = `Bearer ${token}`
      return httpClient(originalRequest)
    }

    isRefreshing = true

    try {
      const { data } = await axios.post<{ accessToken: string }>(
        `${BASE_URL}${REFRESH_PATH}`,
        {},
        { withCredentials: true },
      )
      setAccessToken(data.accessToken)
      flushQueue(data.accessToken)
      originalRequest.headers.Authorization = `Bearer ${data.accessToken}`
      return httpClient(originalRequest)
    } catch (refreshError) {
      flushQueue(null)
      goToLogin()
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  },
)
