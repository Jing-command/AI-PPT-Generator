"use client";

import { useState, useEffect, useCallback } from 'react';
import { exportAPI } from '@/lib/api';

// 导出任务 Hook
export function useExport(pptId: string | null) {
  const [exportTask, setExportTask] = useState<{
    export_task_id: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    download_url: string | null;
    expires_at: string | null;
  } | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  // 轮询导出状态
  useEffect(() => {
    if (!exportTask?.export_task_id || exportTask.status === 'completed' || exportTask.status === 'failed') {
      return;
    }

    const interval = setInterval(async () => {
      try {
        if (!pptId || !exportTask) return;
        const status = await exportAPI.getStatus(pptId, exportTask.export_task_id);
        setExportTask(status);
        
        // 模拟进度
        if (status.status === 'processing') {
          setProgress(prev => Math.min(prev + 10, 90));
        } else if (status.status === 'completed') {
          setProgress(100);
        }
        
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(interval);
          setIsExporting(false);
        }
      } catch (err) {
        console.error('查询导出状态失败:', err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [exportTask?.export_task_id, exportTask?.status, pptId]);

  // 开始导出
  const startExport = useCallback(async (format: 'pptx' | 'pdf' | 'png' | 'jpg', quality?: 'high' | 'medium' | 'low') => {
    if (!pptId) return;
    setIsExporting(true);
    setError(null);
    setProgress(0);
    
    try {
      const response = await exportAPI.export(pptId, { format, quality });
      setExportTask(response);
      return response;
    } catch (err: any) {
      setError(err.message || '导出失败');
      setIsExporting(false);
      throw err;
    }
  }, [pptId]);

  // 下载文件
  const downloadFile = useCallback(() => {
    if (exportTask?.download_url) {
      window.open(exportTask.download_url, '_blank');
    }
  }, [exportTask?.download_url]);

  return {
    exportTask,
    isExporting,
    error,
    progress,
    startExport,
    downloadFile,
  };
}
