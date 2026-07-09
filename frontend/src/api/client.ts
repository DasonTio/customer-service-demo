import type {
  ApiChatMessage,
  ChatSource,
  ChatStreamHandlers,
  DocumentResponse,
} from './types'

export const API_BASE_URL: string =
  import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function assertOk(response: Response): Promise<void> {
  if (response.ok) return
  let detail = `Request failed with status ${response.status}`
  try {
    const body: unknown = await response.json()
    if (
      typeof body === 'object' &&
      body !== null &&
      'detail' in body &&
      typeof body.detail === 'string'
    ) {
      detail = body.detail
    }
  } catch {
    // non-JSON error body; keep the status message
  }
  throw new Error(detail)
}

export async function fetchDocuments(): Promise<DocumentResponse[]> {
  const response = await fetch(`${API_BASE_URL}/documents`)
  await assertOk(response)
  return (await response.json()) as DocumentResponse[]
}

export async function uploadDocument(file: File): Promise<DocumentResponse> {
  const form = new FormData()
  form.append('file', file)
  const response = await fetch(`${API_BASE_URL}/documents`, {
    method: 'POST',
    body: form,
  })
  await assertOk(response)
  return (await response.json()) as DocumentResponse
}

export async function deleteDocument(documentId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    method: 'DELETE',
  })
  await assertOk(response)
}

interface SseFrame {
  event: string
  data: string
}

function parseSseFrames(buffer: string): { frames: SseFrame[]; rest: string } {
  const parts = buffer.split('\n\n')
  const rest = parts.pop() ?? ''
  const frames: SseFrame[] = []
  for (const part of parts) {
    let event = 'message'
    let data = ''
    for (const line of part.split('\n')) {
      if (line.startsWith('event: ')) event = line.slice(7)
      if (line.startsWith('data: ')) data = line.slice(6)
    }
    frames.push({ event, data })
  }
  return { frames, rest }
}

export async function streamChat(
  message: string,
  history: ApiChatMessage[],
  handlers: ChatStreamHandlers,
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  })
  await assertOk(response)
  if (!response.body) {
    handlers.onError('The server returned an empty response.')
    return
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const { frames, rest } = parseSseFrames(buffer)
    buffer = rest
    for (const frame of frames) {
      switch (frame.event) {
        case 'sources':
          handlers.onSources(
            (JSON.parse(frame.data) as { sources: ChatSource[] }).sources,
          )
          break
        case 'token':
          handlers.onToken((JSON.parse(frame.data) as { text: string }).text)
          break
        case 'done':
          handlers.onDone()
          return
        case 'error':
          handlers.onError(
            (JSON.parse(frame.data) as { detail: string }).detail,
          )
          return
      }
    }
  }
}
