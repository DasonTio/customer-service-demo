export type Role = 'user' | 'assistant'

export interface ApiChatMessage {
  role: Role
  content: string
}

export interface ChatSource {
  document_id: string
  filename: string
  chunk_index: number
}

export interface DocumentResponse {
  id: string
  filename: string
  content_type: string
  created_at: string
  chunk_count: number
}

export interface ChatStreamHandlers {
  onSources: (sources: ChatSource[]) => void
  onToken: (text: string) => void
  onDone: () => void
  onError: (detail: string) => void
}
