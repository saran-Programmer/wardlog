import { httpClient } from './httpClient'

export async function synthesizeSpeech(text: string): Promise<Blob> {
  const response = await httpClient.request<Blob>({
    url: '/api/v1/conversations/speech',
    method: 'POST',
    data: { text },
    responseType: 'blob',
  })
  return response.data
}
