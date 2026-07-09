import { useRef, useState } from 'react'
import { Button } from '../../components/Button'
import { useDeleteDocument, useDocuments, useUploadDocument } from './hooks'
import styles from './AdminPage.module.css'

export function AdminPage() {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const documents = useDocuments()
  const upload = useUploadDocument()
  const remove = useDeleteDocument()

  function handleFileChange(files: FileList | null) {
    const file = files?.[0]
    if (!file) return
    setUploadError(null)
    upload.mutate(file, {
      onError: (error) => setUploadError(error.message),
      onSettled: () => {
        if (fileInputRef.current) fileInputRef.current.value = ''
      },
    })
  }

  return (
    <section className={styles.page} aria-label="Knowledge base admin">
      <header className={styles.header}>
        <div>
          <h2 className={styles.title}>Knowledge base</h2>
          <p className={styles.subtitle}>
            Documents the agent uses to answer customers (.txt, .md, .pdf).
          </p>
        </div>
        <input
          ref={fileInputRef}
          className={styles.hiddenInput}
          type="file"
          accept=".txt,.md,.pdf"
          aria-label="Upload document"
          onChange={(e) => handleFileChange(e.target.files)}
        />
        <Button
          onClick={() => fileInputRef.current?.click()}
          disabled={upload.isPending}
        >
          {upload.isPending ? 'Ingesting…' : 'Upload document'}
        </Button>
      </header>

      {uploadError && <p className={styles.error}>⚠ {uploadError}</p>}

      {documents.isLoading && <p className={styles.muted}>Loading documents…</p>}
      {documents.isError && (
        <p className={styles.error}>⚠ Could not load documents.</p>
      )}
      {documents.data?.length === 0 && (
        <p className={styles.muted}>
          No documents yet. Upload one so the agent has something to work with.
        </p>
      )}

      {documents.data && documents.data.length > 0 && (
        <ul className={styles.list}>
          {documents.data.map((doc) => (
            <li key={doc.id} className={styles.item}>
              <div>
                <p className={styles.filename}>{doc.filename}</p>
                <p className={styles.meta}>
                  {doc.chunk_count} chunks ·{' '}
                  {new Date(doc.created_at).toLocaleString()}
                </p>
              </div>
              <Button
                variant="danger"
                onClick={() => remove.mutate(doc.id)}
                disabled={remove.isPending}
              >
                Delete
              </Button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
