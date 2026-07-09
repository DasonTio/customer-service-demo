import { useEffect, useRef } from 'react'
import type { ChatUiMessage } from '../../stores/chatStore'
import styles from './MessageList.module.css'

export interface MessageListProps {
  messages: ChatUiMessage[]
}

export function MessageList({ messages }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (messages.length === 0) {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyTitle}>Hi, I'm Aria 👋</p>
        <p className={styles.emptySubtitle}>
          Ask me anything about our products and policies.
        </p>
      </div>
    )
  }

  return (
    <div className={styles.list} role="log" aria-label="Conversation">
      {messages.map((message) => (
        <div
          key={message.id}
          className={
            message.role === 'user' ? styles.userRow : styles.assistantRow
          }
        >
          <div
            className={
              message.role === 'user' ? styles.userBubble : styles.assistantBubble
            }
          >
            {message.content}
            {message.streaming && !message.content && (
              <span className={styles.typing} aria-label="Agent is typing">
                ●●●
              </span>
            )}
            {message.error && (
              <p className={styles.error}>⚠ {message.error}</p>
            )}
            {!message.streaming && message.sources.length > 0 && (
              <p className={styles.sources}>
                Sources:{' '}
                {[...new Set(message.sources.map((s) => s.filename))].join(', ')}
              </p>
            )}
          </div>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
