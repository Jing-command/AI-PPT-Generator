"use client";

import { useState, useEffect, useCallback } from 'react';
import { pptAPI } from '@/lib/api';

interface PPT {
  id: string;
  title: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
  slide_count: number;
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
      const data = await pptAPI.list({ limit: '50' });
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
    const newPPT = await pptAPI.create(data);
    setPpts((prev) => [newPPT, ...prev]);
    return newPPT;
  }, []);

  const deletePPT = useCallback(async (id: string) => {
    await pptAPI.delete(id);
    setPpts((prev) => prev.filter((p) => p.id !== id));
  }, []);

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
        const data = await pptAPI.getById(pptId);
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
    const updated = await pptAPI.update(pptId, data);
    setPpt(updated);
    return updated;
  }, [pptId]);

  return {
    ppt,
    isLoading,
    error,
    updatePPT,
    refetch: () => pptId && pptAPI.getById(pptId).then(setPpt),
  };
}
