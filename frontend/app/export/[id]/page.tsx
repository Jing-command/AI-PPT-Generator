"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { 
  ArrowLeft, 
  FileType, 
  Download, 
  Loader2, 
  CheckCircle2,
  XCircle,
  FileText,
  Image,
  FileOutput,
  Clock
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { usePPTDetail } from "@/hooks/usePPT";
import { useExport } from "@/hooks/useExport";
import { useAuthGuard } from "@/components/AuthGuard";
import FloatingShapes from "@/components/FloatingShapes";

const EXPORT_OPTIONS = [
  {
    id: "pptx",
    name: "PowerPoint",
    description: "PPTX 格式，可在 PowerPoint 中编辑",
    icon: FileText,
    color: "from-orange-500 to-red-500",
    extension: ".pptx",
  },
  {
    id: "pdf",
    name: "PDF 文档",
    description: "适合打印和分享的通用格式",
    icon: FileOutput,
    color: "from-red-500 to-pink-500",
    extension: ".pdf",
  },
  {
    id: "png",
    name: "PNG 图片",
    description: "高质量图片，每页一张",
    icon: Image,
    color: "from-blue-500 to-cyan-500",
    extension: ".png",
  },
  {
    id: "jpg",
    name: "JPG 图片",
    description: "压缩图片，适合网页使用",
    icon: Image,
    color: "from-green-500 to-emerald-500",
    extension: ".jpg",
  },
];

const QUALITY_OPTIONS = [
  { id: "high", name: "高质量", description: "最佳清晰度，文件较大" },
  { id: "medium", name: "标准", description: "平衡质量和文件大小" },
  { id: "low", name: "快速", description: "较小文件，适合预览" },
];

export default function ExportPage() {
  const params = useParams();
  const pptId = params.id as string;
  
  const { isLoading: authLoading } = useAuthGuard(true);
  const { ppt, isLoading: pptLoading } = usePPTDetail(pptId);
  const { exportTask, isExporting, error, progress, startExport, downloadFile } = useExport(pptId);
  
  const [selectedFormat, setSelectedFormat] = useState<string>("pptx");
  const [selectedQuality, setSelectedQuality] = useState<string>("high");

  const handleExport = async () => {
    try {
      await startExport(
        selectedFormat as 'pptx' | 'pdf' | 'png' | 'jpg',
        selectedQuality as 'high' | 'medium' | 'low'
      );
    } catch (err) {
      console.error('导出失败:', err);
    }
  };

  if (pptLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-white/20 border-t-white rounded-full" />
      </div>
    );
  }

  const selectedOption = EXPORT_OPTIONS.find(o => o.id === selectedFormat);

  return (
    <main className="min-h-screen relative overflow-hidden">
      {/* 背景 */}
      <div 
        className="fixed inset-0 animate-gradient"
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 25%, #8b5cf6 50%, #ec4899 75%, #f43f5e 100%)',
          backgroundSize: '400% 400%',
        }}
      />
      <FloatingShapes />

      <div className="relative z-10 min-h-screen flex flex-col">
        {/* 头部 */}
        <header className="glass border-b border-white/10">
          <div className="flex items-center gap-4 px-4 h-14">
            <Link
              href={`/editor/${pptId}`}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            
            <div>
              <h1 className="font-medium">导出 PPT</h1>
              {ppt && (
                <p className="text-sm text-white/60">{ppt.title}</p>
              )}
            </div>
          </div>
        </header>

        {/* 主体 */}
        <div className="flex-1 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-2xl glass rounded-3xl p-6 sm:p-8"
          >
            <div className="text-center mb-8">
              <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${selectedOption?.color} flex items-center justify-center`}>
                {selectedOption && <selectedOption.icon className="w-8 h-8 text-white" />}
              </div>
              <h2 className="text-2xl font-bold text-gradient mb-2">导出设置</h2>
              <p className="text-white/60">选择你想要的导出格式</p>
            </div>

            {/* 错误提示 */}
            {error && (
              <div className="mb-6 p-4 rounded-xl bg-red-500/20 border border-red-500/30 text-red-200 flex items-center gap-2">
                <XCircle className="w-5 h-5" />
                {error}
              </div>
            )}

            {/* 格式选择 */}
            <div className="mb-8">
              <h3 className="text-sm font-medium text-white/80 mb-4">选择格式</h3>
              
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {EXPORT_OPTIONS.map((option) => {
                  const Icon = option.icon;
                  return (
                    <button
                      key={option.id}
                      onClick={() => setSelectedFormat(option.id)}
                      disabled={isExporting}
                      className={`p-4 rounded-xl border-2 text-left ${
                        selectedFormat === option.id
                          ? 'border-white bg-white/20'
                          : 'border-white/20 hover:border-white/40'
                      } ${isExporting ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${option.color} flex items-center justify-center mb-3`}>
                        <Icon className="w-5 h-5 text-white" />
                      </div>
                      <p className="font-medium text-sm">{option.name}</p>
                      <p className="text-xs text-white/50 mt-1">{option.extension}</p>
                    </button>
                  );
                })}
              </div>
              
              <p className="text-sm text-white/60 mt-3">
                {EXPORT_OPTIONS.find(o => o.id === selectedFormat)?.description}
              </p>
            </div>

            {/* 质量选择（仅图片格式） */}
            {(selectedFormat === 'png' || selectedFormat === 'jpg') && (
              <div className="mb-8">
                <h3 className="text-sm font-medium text-white/80 mb-4">图片质量</h3>
                
                <div className="space-y-2">
                  {QUALITY_OPTIONS.map((quality) => (
                    <button
                      key={quality.id}
                      onClick={() => setSelectedQuality(quality.id)}
                      disabled={isExporting}
                      className={`w-full p-4 rounded-xl border-2 flex items-center justify-between ${
                        selectedQuality === quality.id
                          ? 'border-white bg-white/20'
                          : 'border-white/20 hover:border-white/40'
                      } ${isExporting ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      <div className="text-left">
                        <p className="font-medium">{quality.name}</p>
                        <p className="text-sm text-white/50">{quality.description}</p>
                      </div>
                      
                      {selectedQuality === quality.id && (
                        <div className="w-5 h-5 rounded-full bg-white flex items-center justify-center">
                          <div className="w-2 h-2 rounded-full bg-purple-600" />
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* 导出进度 */}
            {exportTask && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-6 p-4 rounded-xl glass"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    exportTask.status === 'completed' ? 'bg-green-500/20' :
                    exportTask.status === 'failed' ? 'bg-red-500/20' :
                    'bg-yellow-500/20'
                  }`}>
                    {exportTask.status === 'completed' ? (
                      <CheckCircle2 className="w-6 h-6 text-green-400" />
                    ) : exportTask.status === 'failed' ? (
                      <XCircle className="w-6 h-6 text-red-400" />
                    ) : (
                      <Loader2 className="w-6 h-6 text-yellow-400 animate-spin" />
                    )}
                  </div>
                  
                  <div className="flex-1">
                    <p className="font-medium">
                      {exportTask.status === 'completed' ? '导出完成！' :
                       exportTask.status === 'failed' ? '导出失败' :
                       '正在导出...'}
                    </p>
                    
                    {exportTask.status === 'processing' && (
                      <>
                        <div className="mt-2 h-2 bg-white/10 rounded-full overflow-hidden">
                          <motion.div
                            className="h-full bg-gradient-to-r from-yellow-400 to-pink-400"
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                          />
                        </div>
                        <p className="text-sm text-white/60 mt-1">{progress}%</p>
                      </>
                    )}
                  </div>
                  
                  {exportTask.status === 'completed' && exportTask.download_url && (
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={downloadFile}
                      className="flex items-center gap-2 px-4 py-2 bg-white text-purple-600 rounded-full font-medium text-sm"
                    >
                      <Download className="w-4 h-4" />
                      下载
                    </motion.button>
                  )}
                </div>
              </motion.div>
            )}

            {/* 导出按钮 */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleExport}
              disabled={isExporting}
              className="w-full flex items-center justify-center gap-2 bg-white text-purple-600 px-6 py-4 rounded-xl font-semibold text-lg shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isExporting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  导出中...
                </>
              ) : (
                <>
                  <FileType className="w-5 h-5" />
                  开始导出
                </>
              )}
            </motion.button>

            {/* 提示 */}
            <div className="mt-6 flex items-start gap-3 text-sm text-white/50">
              <Clock className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <p>
                导出可能需要一些时间，请耐心等待。导出完成后文件将在 24 小时内可下载。
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </main>
  );
}
