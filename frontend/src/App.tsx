import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AdminPage } from './features/admin/AdminPage'
import { ChatPage } from './features/chat/ChatPage'
import styles from './App.module.css'

const queryClient = new QueryClient()

type Page = 'chat' | 'admin'

export function App() {
  const [page, setPage] = useState<Page>('chat')

  return (
    <QueryClientProvider client={queryClient}>
      <header className={styles.header}>
        <h1 className={styles.brand}>Acme Support</h1>
        <nav className={styles.nav} aria-label="Main">
          <button
            className={page === 'chat' ? styles.tabActive : styles.tab}
            onClick={() => setPage('chat')}
          >
            Chat
          </button>
          <button
            className={page === 'admin' ? styles.tabActive : styles.tab}
            onClick={() => setPage('admin')}
          >
            Knowledge base
          </button>
        </nav>
      </header>
      {page === 'chat' ? <ChatPage /> : <AdminPage />}
    </QueryClientProvider>
  )
}
