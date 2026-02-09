"use client";

import { useState, useEffect, useCallback } from 'react';
import { pptAPI } from '@/lib/api';

interface Slide {
  id: string;
  type: string;
  content: {
    title?: string;
    text?: string;
    subtitle?: string;
    bullets?: string[];
    image_url?: string;
  };
  layout?: {
    type: string;
    background?: string;
    theme?: string;
  };
}

interface PPT {
  id: string;
  title: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
  slide_count: number;
  slides?: Slide[];
}

// PPT 列表 Hook
export function usePPTList() {
  const [ppts, setPpts] = useState<PPT[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPPTs = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await pptAPI.list({ limit: 50 }) as PPT[];
      setPpts(data);
    } catch (err: any) {
      setError(err.message || '加载失败');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPPTs();
  }, [fetchPPTs]);

  const createPPT = useCallback(async (data: { title: string; description?: string }) => {
    const newPPT = await pptAPI.create(data) as PPT;
    setPpts((prev) => [newPPT, ...prev]);
    return newPPT;
  }, []);

  const deletePPT = useCallback(async (id: string) => {
    try {
      await pptAPI.delete(id);
      // 乐观更新：立即从列表中移除
      setPpts((prev) => prev.filter((p) => p.id !== id));
    } catch (err: any) {
      // 删除失败时重新获取列表，确保状态同步
      await fetchPPTs();
      throw err;
    }
  }, [fetchPPTs]);

  return {
    ppts,
    isLoading,
    error,
    refetch: fetchPPTs,
    createPPT,
    deletePPT,
  };
}

// PPT 详情 Hook
export function usePPTDetail(pptId: string | null) {
  const [ppt, setPpt] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!pptId) return;

    const fetchPPT = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await pptAPI.getById(pptId) as PPT;
        setPpt(data);
      } catch (err: any) {
        setError(err.message || '加载失败');
      } finally {
        setIsLoading(false);
      }
    };

    fetchPPT();
  }, [pptId]);

  const updatePPT = useCallback(async (data: Partial<{ title: string; description: string }>) => {
    if (!pptId) return;
    const updated = await pptAPI.update(pptId, data) as PPT;
    setPpt(updated);
    return updated;
  }, [pptId]);

  return {
    ppt,
    isLoading,
    error,
    updatePPT,
    refetch: () => pptId && pptAPI.getById(pptId).then(data => setPpt(data as PPT)),
  };
}
