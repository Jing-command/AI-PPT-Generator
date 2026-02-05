import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Input } from './Input'

describe('Input', () => {
  it('renders with label', () => {
    render(<Input label="Email" />)
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
  })

  it('renders with placeholder', () => {
    render(<Input placeholder="Enter email" />)
    expect(screen.getByPlaceholderText('Enter email')).toBeInTheDocument()
  })

  it('handles value changes', async () => {
    const handleChange = vi.fn()
    render(<Input onChange={handleChange} />)
    
    const input = screen.getByRole('textbox')
    await userEvent.type(input, 'test@example.com')
    
    expect(handleChange).toHaveBeenCalled()
  })

  it('displays error message', () => {
    render(<Input error="Email is required" />)
    expect(screen.getByText('Email is required')).toBeInTheDocument()
  })

  it('can be disabled', () => {
    render(<Input disabled />)
    expect(screen.getByRole('textbox')).toBeDisabled()
  })

  it('supports different types', () => {
    const { rerender } = render(<Input label="Field" type="text" />)
    expect(screen.getByLabelText('Field')).toHaveAttribute('type', 'text')

    rerender(<Input label="Field" type="password" />)
    expect(screen.getByLabelText('Field')).toHaveAttribute('type', 'password')

    rerender(<Input label="Field" type="email" />)
    expect(screen.getByLabelText('Field')).toHaveAttribute('type', 'email')
  })
})
