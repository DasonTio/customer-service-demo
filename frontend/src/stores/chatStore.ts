import { create } from 'zustand'
import type { ChatSource, Role } from '../api/types'

export interface ChatUiMessage {
  id: string
  role: Role
  content: string
  sources: ChatSource[]
  streaming: boolean
  error?: string
}

interface ChatState {
  messages: ChatUiMessage[]
  isStreaming: boolean
  addUserMessage: (content: string) => void
  startAssistantMessage: () => string
  appendToken: (id: string, text: string) => void
  setSources: (id: string, sources: ChatSource[]) => void
  finishMessage: (id: string) => void
  failMessage: (id: string, error: string) => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isStreaming: false,

  addUserMessage: (content) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: crypto.randomUUID(),
          role: 'user',
          content,
          sources: [],
          streaming: false,
        },
      ],
    })),

  startAssistantMessage: () => {
    const id = crypto.randomUUID()
    set((state) => ({
      isStreaming: true,
      messages: [
        ...state.messages,
        { id, role: 'assistant', content: '', sources: [], streaming: true },
      ],
    }))
    return id
  },

  appendToken: (id, text) =>
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, content: m.content + text } : m,
      ),
    })),

  setSources: (id, sources) =>
    set((state) => ({
      messages: state.messages.map((m) => (m.id === id ? { ...m, sources } : m)),
    })),

  finishMessage: (id) =>
    set((state) => ({
      isStreaming: false,
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, streaming: false } : m,
      ),
    })),

  failMessage: (id, error) =>
    set((state) => ({
      isStreaming: false,
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, streaming: false, error } : m,
      ),
    })),
}))
