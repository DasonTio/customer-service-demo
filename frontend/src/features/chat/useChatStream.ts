import { useCallback } from 'react'
import { streamChat } from '../../api/client'
import type { ApiChatMessage } from '../../api/types'
import { useChatStore } from '../../stores/chatStore'

export function useChatStream() {
  const isStreaming = useChatStore((s) => s.isStreaming)

  const sendMessage = useCallback(async (content: string) => {
    const state = useChatStore.getState()
    const history: ApiChatMessage[] = state.messages
      .filter((m) => !m.error && m.content)
      .map((m) => ({ role: m.role, content: m.content }))

    state.addUserMessage(content)
    const assistantId = state.startAssistantMessage()
    const store = useChatStore.getState()

    try {
      await streamChat(content, history, {
        onSources: (sources) => store.setSources(assistantId, sources),
        onToken: (text) => store.appendToken(assistantId, text),
        onDone: () => store.finishMessage(assistantId),
        onError: (detail) => store.failMessage(assistantId, detail),
      })
    } catch (error) {
      store.failMessage(
        assistantId,
        error instanceof Error ? error.message : 'Something went wrong.',
      )
    }
  }, [])

  return { sendMessage, isStreaming }
}
