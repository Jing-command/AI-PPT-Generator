import { describe, it, expect, beforeEach } from 'vitest'
import { usePPTStore } from './ppt'
import type { Presentation, Slide } from '@/types'

describe('PPT Store', () => {
  beforeEach(() => {
    usePPTStore.setState({
      currentPPT: null,
      currentSlide: null,
      slides: [],
      presentations: [],
      total: 0,
      history: [],
      canUndo: false,
      canRedo: false,
      isLoading: false,
      isSaving: false,
      selectedSlideId: null,
    })
  })

  it('should have initial state', () => {
    const state = usePPTStore.getState()
    expect(state.currentPPT).toBeNull()
    expect(state.slides).toEqual([])
    expect(state.presentations).toEqual([])
    expect(state.canUndo).toBe(false)
    expect(state.canRedo).toBe(false)
  })

  it('should set current PPT', () => {
    const mockPPT: Presentation = {
      id: '1',
      user_id: 'user1',
      title: 'Test Presentation',
      slides: [],
      status: 'draft',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    
    usePPTStore.getState().setCurrentPPT(mockPPT)
    expect(usePPTStore.getState().currentPPT).toEqual(mockPPT)
  })

  it('should add slide', () => {
    const newSlide: Slide = {
      id: 'slide1',
      type: 'content',
      content: { title: 'New Slide', text: '' },
    }
    
    usePPTStore.getState().addSlide(newSlide)
    const slides = usePPTStore.getState().slides
    
    expect(slides).toHaveLength(1)
    expect(slides[0].id).toBe('slide1')
  })

  it('should delete slide', () => {
    const slide1: Slide = {
      id: 'slide1',
      type: 'content',
      content: { title: 'Slide 1', text: '' },
    }
    const slide2: Slide = {
      id: 'slide2',
      type: 'content',
      content: { title: 'Slide 2', text: '' },
    }
    
    usePPTStore.getState().addSlide(slide1)
    usePPTStore.getState().addSlide(slide2)
    usePPTStore.getState().deleteSlide('slide1')
    
    const slides = usePPTStore.getState().slides
    expect(slides).toHaveLength(1)
    expect(slides[0].id).toBe('slide2')
  })

  it('should update slide', () => {
    const slide: Slide = {
      id: 'slide1',
      type: 'content',
      content: { title: 'Old Title', text: '' },
    }
    
    usePPTStore.getState().addSlide(slide)
    usePPTStore.getState().updateSlide('slide1', {
      content: { title: 'New Title', text: 'Updated' },
    })
    
    const updatedSlide = usePPTStore.getState().slides[0]
    expect(updatedSlide.content?.title).toBe('New Title')
    expect(updatedSlide.content?.text).toBe('Updated')
  })

  it('should set presentations', () => {
    const presentations: Presentation[] = [
      {
        id: '1',
        user_id: 'user1',
        title: 'PPT 1',
        slides: [],
        status: 'draft',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ]
    
    usePPTStore.getState().setPresentations(presentations, 1)
    const state = usePPTStore.getState()
    
    expect(state.presentations).toEqual(presentations)
    expect(state.total).toBe(1)
  })

  it('should set undo/redo state', () => {
    usePPTStore.getState().setCanUndo(true)
    expect(usePPTStore.getState().canUndo).toBe(true)
    
    usePPTStore.getState().setCanRedo(true)
    expect(usePPTStore.getState().canRedo).toBe(true)
  })
})
