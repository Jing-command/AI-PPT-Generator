/**
 * PPT 状态管理
 */

import { create } from 'zustand'
import type { Presentation, Slide, OperationHistory } from '@/types'

interface PPTState {
  // 当前 PPT
  currentPPT: Presentation | null
  currentSlide: Slide | null
  slides: Slide[]
  
  // 列表
  presentations: Presentation[]
  total: number
  
  // 操作历史
  history: OperationHistory[]
  canUndo: boolean
  canRedo: boolean
  
  // UI 状态
  isLoading: boolean
  isSaving: boolean
  selectedSlideId: string | null
  
  // Actions
  setCurrentPPT: (ppt: Presentation | null) => void
  setCurrentSlide: (slide: Slide | null) => void
  setSlides: (slides: Slide[]) => void
  updateSlide: (slideId: string, data: Partial<Slide>) => void
  addSlide: (slide: Slide, position?: number) => void
  deleteSlide: (slideId: string) => void
  reorderSlides: (slideIds: string[]) => void
  
  setPresentations: (presentations: Presentation[], total: number) => void
  setHistory: (history: OperationHistory[]) => void
  setCanUndo: (value: boolean) => void
  setCanRedo: (value: boolean) => void
  setLoading: (value: boolean) => void
  setSaving: (value: boolean) => void
  setSelectedSlideId: (id: string | null) => void
}

export const usePPTStore = create<PPTState>()((set, get) => ({
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
  
  setCurrentPPT: (ppt) => set({ 
    currentPPT: ppt, 
    slides: ppt?.slides || [],
    selectedSlideId: ppt?.slides?.[0]?.id || null 
  }),
  
  setCurrentSlide: (slide) => set({ currentSlide: slide }),
  setSlides: (slides) => set({ slides }),
  
  updateSlide: (slideId, data) => {
    const { slides } = get()
    const newSlides = slides.map((s) =>
      s.id === slideId ? { ...s, ...data } : s
    )
    set({ slides: newSlides })
  },
  
  addSlide: (slide, position) => {
    const { slides } = get()
    const newSlides = [...slides]
    if (position !== undefined && position <= newSlides.length) {
      newSlides.splice(position, 0, slide)
    } else {
      newSlides.push(slide)
    }
    set({ slides: newSlides, selectedSlideId: slide.id })
  },
  
  deleteSlide: (slideId) => {
    const { slides, selectedSlideId } = get()
    const newSlides = slides.filter((s) => s.id !== slideId)
    
    // 如果删除的是当前选中的，选择第一个
    let newSelectedId = selectedSlideId
    if (selectedSlideId === slideId) {
      newSelectedId = newSlides[0]?.id || null
    }
    
    set({ slides: newSlides, selectedSlideId: newSelectedId })
  },
  
  reorderSlides: (slideIds) => {
    const { slides } = get()
    const slideMap = new Map(slides.map((s) => [s.id, s]))
    const newSlides = slideIds.map((id) => slideMap.get(id)!).filter(Boolean)
    set({ slides: newSlides })
  },
  
  setPresentations: (presentations, total) => set({ presentations, total }),
  setHistory: (history) => set({ history }),
  setCanUndo: (value) => set({ canUndo: value }),
  setCanRedo: (value) => set({ canRedo: value }),
  setLoading: (value) => set({ isLoading: value }),
  setSaving: (value) => set({ isSaving: value }),
  setSelectedSlideId: (id) => set({ selectedSlideId: id }),
}))

export default usePPTStore
