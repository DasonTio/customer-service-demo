import { beforeEach, describe, expect, it } from 'vitest'
import { useChatStore } from './chatStore'

describe('chatStore', () => {
  beforeEach(() => {
    useChatStore.setState({ messages: [], isStreaming: false })
  })

  it('appends streamed tokens to the assistant message', () => {
    const store = useChatStore.getState()
    store.addUserMessage('Refund policy?')
    const id = useChatStore.getState().startAssistantMessage()

    useChatStore.getState().appendToken(id, 'Refunds ')
    useChatStore.getState().appendToken(id, 'in 30 days.')
    useChatStore.getState().finishMessage(id)

    const { messages, isStreaming } = useChatStore.getState()
    expect(messages).toHaveLength(2)
    expect(messages[1].content).toBe('Refunds in 30 days.')
    expect(messages[1].streaming).toBe(false)
    expect(isStreaming).toBe(false)
  })

  it('records an error on the failed message and stops streaming', () => {
    const id = useChatStore.getState().startAssistantMessage()
    useChatStore.getState().failMessage(id, 'Model unavailable')

    const { messages, isStreaming } = useChatStore.getState()
    expect(messages[0].error).toBe('Model unavailable')
    expect(isStreaming).toBe(false)
  })
})
