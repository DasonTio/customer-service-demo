import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { MessageInput } from './MessageInput'

describe('MessageInput', () => {
  it('sends the trimmed message and clears the input', async () => {
    const onSend = vi.fn()
    render(<MessageInput onSend={onSend} disabled={false} />)

    const input = screen.getByRole('textbox', { name: 'Message' })
    await userEvent.type(input, '  Where is my order?  ')
    await userEvent.click(screen.getByRole('button', { name: 'Send' }))

    expect(onSend).toHaveBeenCalledWith('Where is my order?')
    expect(input).toHaveValue('')
  })

  it('does not send empty messages', async () => {
    const onSend = vi.fn()
    render(<MessageInput onSend={onSend} disabled={false} />)
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled()
  })

  it('disables sending while streaming', async () => {
    const onSend = vi.fn()
    render(<MessageInput onSend={onSend} disabled />)
    await userEvent.type(
      screen.getByRole('textbox', { name: 'Message' }),
      'hello',
    )
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled()
  })
})
