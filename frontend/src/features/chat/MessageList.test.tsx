import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { ChatUiMessage } from '../../stores/chatStore'
import { MessageList } from './MessageList'

function message(overrides: Partial<ChatUiMessage>): ChatUiMessage {
  return {
    id: crypto.randomUUID(),
    role: 'user',
    content: 'hello',
    sources: [],
    streaming: false,
    ...overrides,
  }
}

describe('MessageList', () => {
  it('shows the empty state before any messages', () => {
    render(<MessageList messages={[]} />)
    expect(screen.getByText(/Hi, I'm Aria/)).toBeInTheDocument()
  })

  it('renders user and assistant messages', () => {
    render(
      <MessageList
        messages={[
          message({ content: 'Where is my order?' }),
          message({ role: 'assistant', content: 'It ships tomorrow.' }),
        ]}
      />,
    )
    expect(screen.getByText('Where is my order?')).toBeInTheDocument()
    expect(screen.getByText('It ships tomorrow.')).toBeInTheDocument()
  })

  it('shows deduplicated source filenames after streaming ends', () => {
    const sources = [
      { document_id: 'a', filename: 'faq.md', chunk_index: 0 },
      { document_id: 'a', filename: 'faq.md', chunk_index: 2 },
    ]
    render(
      <MessageList
        messages={[message({ role: 'assistant', content: 'Answer.', sources })]}
      />,
    )
    expect(screen.getByText(/Sources:\s*faq\.md$/)).toBeInTheDocument()
  })
})
