"use client";

import { useState, useCallback, useEffect } from 'react';
import { generationAPI } from '@/lib/api';

interface GenerationTask {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  estimated_time: number;
  message: string;
  result?: {
    ppt_id: string;
    title: string;
  };
  error?: string;
}

// AI 生成 Hook
export function useGeneration() {
  const [task, setTask] = useState<GenerationTask | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 轮询任务状态
  useEffect(() => {
    if (!task?.task_id || task.status === 'completed' || task.status === 'failed' || task.status === 'cancelled') {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const status = await generationAPI.getStatus(task.task_id);
        setTask(status);
        
        if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
          clearInterval(interval);
          setIsGenerating(false);
        }
      } catch (err) {
        console.error('查询状态失败:', err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [task?.task_id, task?.status]);

  // 开始生成
  const generate = useCallback(async (data: {
    title: string;
    description?: string;
    template_id?: string;
    slides_count?: number;
  }) => {
    setIsGenerating(true);
    setError(null);
    try {
      const response = await generationAPI.generate(data);
      setTask(response);
      return response;
    } catch (err: any) {
      setError(err.message || '生成失败');
      setIsGenerating(false);
      throw err;
    }
  }, []);

  // 取消生成
  const cancel = useCallback(async () => {
    if (!task?.task_id) return;
    try {
      await generationAPI.cancel(task.task_id);
      setTask((prev) => prev ? { ...prev, status: 'cancelled' } : null);
      setIsGenerating(false);
    } catch (err: any) {
      setError(err.message || '取消失败');
    }
  }, [task?.task_id]);

  return {
    task,
    isGenerating,
    error,
    generate,
    cancel,
  };
}
