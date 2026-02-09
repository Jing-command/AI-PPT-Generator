"use client";

import { useState, useEffect, useCallback } from 'react';
import { templateAPI } from '@/lib/api';

interface Template {
  id: string;
  name: string;
  description?: string;
  thumbnail_url?: string;
  category: string;
  is_premium: boolean;
}

// 模板 Hook
export function useTemplates() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [categories, setCategories] = useState<Array<{ id: string; name: string; icon: string }>>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTemplates = useCallback(async (category?: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const [templatesData, categoriesData] = await Promise.all([
        templateAPI.list({ category, limit: 50 }),
        templateAPI.getCategories(),
      ]);
      setTemplates(templatesData.templates);
      setCategories(categoriesData);
    } catch (err: any) {
      setError(err.message || '加载失败');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  return {
    templates,
    categories,
    isLoading,
    error,
    refetch: fetchTemplates,
  };
}
