import { useChatStore } from '../../stores/chatStore'
import { MessageInput } from './MessageInput'
import { MessageList } from './MessageList'
import { useChatStream } from './useChatStream'
import styles from './ChatPage.module.css'

export function ChatPage() {
  const messages = useChatStore((s) => s.messages)
  const { sendMessage, isStreaming } = useChatStream()

  return (
    <section className={styles.page} aria-label="Customer support chat">
      <MessageList messages={messages} />
      <MessageInput onSend={(m) => void sendMessage(m)} disabled={isStreaming} />
    </section>
  )
}
