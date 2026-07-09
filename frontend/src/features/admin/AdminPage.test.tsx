import { screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { describe, expect, it } from 'vitest'
import { renderWithQuery } from '../../test/helpers'
import { API, server } from '../../test/server'
import { AdminPage } from './AdminPage'

describe('AdminPage', () => {
  it('lists ingested documents', async () => {
    renderWithQuery(<AdminPage />)
    expect(await screen.findByText('faq.md')).toBeInTheDocument()
    expect(screen.getByText(/3 chunks/)).toBeInTheDocument()
  })

  it('shows the empty state when there are no documents', async () => {
    server.use(http.get(`${API}/documents`, () => HttpResponse.json([])))
    renderWithQuery(<AdminPage />)
    expect(await screen.findByText(/No documents yet/)).toBeInTheDocument()
  })
})
