import { describe, it, expect } from 'vitest'
import { cn, formatDate, formatFileSize, debounce, generateId } from './index'

describe('cn utility', () => {
  it('merges class names', () => {
    expect(cn('class1', 'class2')).toBe('class1 class2')
  })

  it('handles conditional classes', () => {
    expect(cn('base', true && 'conditional')).toBe('base conditional')
    expect(cn('base', false && 'conditional')).toBe('base')
  })

  it('handles object syntax', () => {
    expect(cn({ active: true, disabled: false })).toBe('active')
  })

  it('merges tailwind classes correctly', () => {
    expect(cn('px-2 py-1', 'px-4')).toBe('py-1 px-4')
  })
})

describe('formatDate utility', () => {
  it('formats date string', () => {
    const date = '2024-01-15T10:30:00Z'
    const formatted = formatDate(date)
    expect(typeof formatted).toBe('string')
    expect(formatted.length).toBeGreaterThan(0)
  })

  it('handles invalid date', () => {
    expect(formatDate('invalid')).toBe('Invalid Date')
  })

  it('handles Date object', () => {
    const date = new Date('2024-01-15')
    const formatted = formatDate(date)
    expect(typeof formatted).toBe('string')
    expect(formatted.length).toBeGreaterThan(0)
  })
})

describe('formatFileSize utility', () => {
  it('formats bytes', () => {
    expect(formatFileSize(500)).toBe('500 B')
  })

  it('formats kilobytes', () => {
    expect(formatFileSize(1024)).toBe('1.0 KB')
    expect(formatFileSize(1536)).toBe('1.5 KB')
  })

  it('formats megabytes', () => {
    expect(formatFileSize(1024 * 1024)).toBe('1.0 MB')
    expect(formatFileSize(2.5 * 1024 * 1024)).toBe('2.5 MB')
  })

  it('formats gigabytes', () => {
    expect(formatFileSize(1024 * 1024 * 1024)).toBe('1.0 GB')
  })

  it('handles zero', () => {
    expect(formatFileSize(0)).toBe('0 B')
  })
})

describe('debounce utility', () => {
  it('delays function execution', () => {
    vi.useFakeTimers()
    const fn = vi.fn()
    const debouncedFn = debounce(fn, 100)

    debouncedFn()
    expect(fn).not.toHaveBeenCalled()

    vi.advanceTimersByTime(100)
    expect(fn).toHaveBeenCalledTimes(1)

    vi.useRealTimers()
  })

  it('cancels previous call', () => {
    vi.useFakeTimers()
    const fn = vi.fn()
    const debouncedFn = debounce(fn, 100)

    debouncedFn()
    debouncedFn()
    debouncedFn()

    vi.advanceTimersByTime(100)
    expect(fn).toHaveBeenCalledTimes(1)

    vi.useRealTimers()
  })

  it('passes arguments correctly', () => {
    vi.useFakeTimers()
    const fn = vi.fn()
    const debouncedFn = debounce(fn, 100)

    debouncedFn('arg1', 'arg2')
    vi.advanceTimersByTime(100)

    expect(fn).toHaveBeenCalledWith('arg1', 'arg2')
    vi.useRealTimers()
  })
})

describe('generateId utility', () => {
  it('generates unique ids', () => {
    const id1 = generateId()
    const id2 = generateId()
    expect(id1).not.toBe(id2)
  })

  it('generates string ids', () => {
    const id = generateId()
    expect(typeof id).toBe('string')
  })

  it('generates ids with correct length', () => {
    const id = generateId()
    expect(id.length).toBeGreaterThanOrEqual(8)
  })
})
