"use client";

import { useState, useCallback } from 'react';
import { pptAPI } from '@/lib/api';

interface Slide {
  id: string;
  title: string;
  type: string;
  content: any;
  layout: { type: string; theme?: string | null; background?: string | null };
  notes?: string;
}

// PPT 幻灯片 Hook
export function useSlides(pptId: string | null) {
  const [slides, setSlides] = useState<Slide[]>([]);
  const [currentSlide, setCurrentSlide] = useState<Slide | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);

  // 加载幻灯片列表
  const loadSlides = useCallback(async () => {
    if (!pptId) return;
    setIsLoading(true);
    try {
      const ppt = await pptAPI.getById(pptId) as { slides?: Slide[] };
      setSlides(ppt.slides || []);
      if (ppt.slides && ppt.slides.length > 0) {
        setCurrentSlide(ppt.slides[0]);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [pptId]);

  // 选择幻灯片
  const selectSlide = useCallback((slideId: string) => {
    setCurrentSlide(prev => {
      const slide = slides.find(s => s.id === slideId);
      return slide || prev;
    });
  }, [slides]);

  // 添加幻灯片
  const addSlide = useCallback(async (position?: number) => {
    if (!pptId) return;
    const newSlide = await pptAPI.addSlide(pptId, {
      type: "content",
      content: {
        title: "新页面",
        text: "",
        bullets: []
      },
      layout: {
        type: "title-content"
      },
      position,
    }) as Slide;
    await loadSlides();
    return newSlide;
  }, [pptId, loadSlides]);

  // 更新幻灯片
  const updateSlide = useCallback(async (slideId: string, data: Partial<Slide>) => {
    if (!pptId) return;
    setIsLoading(true);
    setError(null);
    try {
      const updated = await pptAPI.updateSlide(pptId, slideId, data) as Slide;
      setSlides(prev => prev.map(s => s.id === slideId ? { ...s, ...updated } : s));
      setCurrentSlide(prev => {
        if (prev?.id === slideId) {
          return { ...prev, ...updated };
        }
        return prev;
      });
      return updated;
    } catch (err: any) {
      console.error('Update slide error:', err);
      setError(err.message || '更新失败');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [pptId]);

  // 删除幻灯片
  const deleteSlide = useCallback(async (slideId: string) => {
    if (!pptId) return;
    await pptAPI.deleteSlide(pptId, slideId);
    setSlides(prev => {
      const filtered = prev.filter(s => s.id !== slideId);
      if (currentSlide?.id === slideId) {
        setCurrentSlide(filtered[0] || null);
      }
      return filtered;
    });
  }, [pptId, currentSlide]);

  // 撤销
  const undo = useCallback(async () => {
    if (!pptId) return;
    const result = await pptAPI.undo(pptId) as { success: boolean };
    if (result.success) {
      await loadSlides();
      setCanUndo(false);
    }
  }, [pptId, loadSlides]);

  // 重做
  const redo = useCallback(async () => {
    if (!pptId) return;
    const result = await pptAPI.redo(pptId) as { success: boolean };
    if (result.success) {
      await loadSlides();
      setCanRedo(false);
    }
  }, [pptId, loadSlides]);

  // 移动幻灯片
  const moveSlide = useCallback(async (fromIndex: number, toIndex: number) => {
    if (!pptId) return;
    const newSlides = [...slides];
    const [moved] = newSlides.splice(fromIndex, 1);
    newSlides.splice(toIndex, 0, moved);
    setSlides(newSlides);
    
    // TODO: 调用后端 API 更新顺序
  }, [pptId, slides]);

  return {
    slides,
    currentSlide,
    isLoading,
    error,
    canUndo,
    canRedo,
    loadSlides,
    selectSlide,
    addSlide,
    updateSlide,
    deleteSlide,
    undo,
    redo,
    moveSlide,
  };
}
