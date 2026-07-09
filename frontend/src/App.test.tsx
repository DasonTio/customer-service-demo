import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { App } from './App'

describe('App', () => {
  it('renders the chat page by default', () => {
    render(<App />)
    expect(screen.getByText('Acme Support')).toBeInTheDocument()
    expect(screen.getByText(/Hi, I'm Aria/)).toBeInTheDocument()
  })

  it('switches to the knowledge base page', async () => {
    render(<App />)
    await userEvent.click(
      screen.getByRole('button', { name: 'Knowledge base' }),
    )
    expect(await screen.findByText('faq.md')).toBeInTheDocument()
  })
})
