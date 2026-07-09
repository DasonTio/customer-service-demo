import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import type { DocumentResponse } from '../api/types'

export const API = 'http://localhost:8000'

export const sampleDocuments: DocumentResponse[] = [
  {
    id: '11111111-1111-1111-1111-111111111111',
    filename: 'faq.md',
    content_type: 'text/markdown',
    created_at: '2026-07-09T10:00:00Z',
    chunk_count: 3,
  },
]

export const server = setupServer(
  http.get(`${API}/documents`, () => HttpResponse.json(sampleDocuments)),
)
