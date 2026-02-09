"use client";

import { useState, useEffect, useCallback } from 'react';
import { apiKeyAPI } from '@/lib/api';

interface APIKey {
  id: string;
  name: string;
  provider: string;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  last_used_at?: string;
}

// API Key 管理 Hook
export function useAPIKeys() {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAPIKeys = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiKeyAPI.list();
      setApiKeys(data);
    } catch (err: any) {
      setError(err.message || '加载失败');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAPIKeys();
  }, [fetchAPIKeys]);

  const createAPIKey = useCallback(async (data: { name: string; provider: string; api_key: string }) => {
    const newKey = await apiKeyAPI.create(data);
    setApiKeys((prev) => [...prev, newKey]);
    return newKey;
  }, []);

  const updateAPIKey = useCallback(async (id: string, data: Partial<{ name: string; is_active: boolean; is_default: boolean }>) => {
    const updated = await apiKeyAPI.update(id, data);
    setApiKeys((prev) => prev.map((k) => (k.id === id ? updated : k)));
    return updated;
  }, []);

  const deleteAPIKey = useCallback(async (id: string) => {
    await apiKeyAPI.delete(id);
    setApiKeys((prev) => prev.filter((k) => k.id !== id));
  }, []);

  const verifyAPIKey = useCallback(async (id: string) => {
    return apiKeyAPI.verify(id);
  }, []);

  return {
    apiKeys,
    isLoading,
    error,
    refetch: fetchAPIKeys,
    createAPIKey,
    updateAPIKey,
    deleteAPIKey,
    verifyAPIKey,
  };
}
