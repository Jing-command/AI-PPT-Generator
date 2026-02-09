"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Wand2, Loader2, Sparkles, Check, ArrowRight, FileText } from "lucide-react";
import { useRouter } from "next/navigation";
import { useGeneration } from "@/hooks/useGeneration";
import { useTemplates } from "@/hooks/useTemplates";
import Navbar from "@/components/Navbar";
import FloatingShapes from "@/components/FloatingShapes";

export default function GeneratePage() {
  const router = useRouter();
  const { generate, cancel, task, isGenerating, error } = useGeneration();
  const { templates, categories, isLoading: templatesLoading } = useTemplates();
  
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [slideCount, setSlideCount] = useState(10);

  const handleGenerate = async () => {
    if (!title.trim()) return;
    
    try {
      await generate({
        title: title.trim(),
        description: description.trim(),
        template_id: selectedTemplate || undefined,
        slides_count: slideCount,
      });
    } catch (err) {
      console.error("生成失败:", err);
    }
  };

  // 生成完成后跳转到编辑器
  if (task?.status === 'completed' && task.result?.ppt_id) {
    setTimeout(() => {
      router.push(`/editor/${task.result.ppt_id}`);
    }, 1500);
  }

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
      <div className="fixed inset-0 bg-gradient-to-b from-transparent via-transparent to-black/20" />
      <FloatingShapes />

      <div className="relative z-10">
        <Navbar />

        <div className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center mb-10"
            >
              <div className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full mb-4">
                <Wand2 className="w-4 h-4 text-yellow-300" />
                <span className="text-sm">AI 智能生成</span>
              </div>
              <h1 className="text-4xl font-bold text-gradient mb-3">
                一句话生成 PPT
              </h1>
              <p className="text-white/70">
                描述你的想法，AI 帮你完成剩下的工作
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass rounded-3xl p-6 sm:p-8"
            >
              {/* 标题输入 */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">PPT 主题 *</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="例如：2024年人工智能发展趋势报告"
                  className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-white/40"
                />
              </div>

              {/* 描述输入 */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">详细描述（可选）</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="补充说明：目标受众、关键要点、风格偏好..."
                  rows={3}
                  className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-white/40 resize-none"
                />
              </div>

              {/* 页数选择 */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">页数: {slideCount} 页</label>
                <input
                  type="range"
                  min={5}
                  max={30}
                  value={slideCount}
                  onChange={(e) => setSlideCount(Number(e.target.value))}
                  className="w-full accent-white"
                />
                <div className="flex justify-between text-xs text-white/50 mt-1">
                  <span>5 页</span>
                  <span>30 页</span>
                </div>
              </div>

              {/* 模板选择 */}
              <div className="mb-8">
                <label className="block text-sm font-medium mb-3">选择模板</label>
                
                {templatesLoading ? (
                  <div className="flex items-center gap-2 text-white/50">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    加载中...
                  </div>
                ) : (
                  <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
                    <button
                      onClick={() => setSelectedTemplate(null)}
                      className={`p-3 rounded-xl border-2 transition-all ${
                        selectedTemplate === null 
                          ? 'border-white bg-white/20' 
                          : 'border-white/20 hover:border-white/40'
                      }`}
                    >
                      <Sparkles className="w-6 h-6 mx-auto mb-2" />
                      <span className="text-xs">AI 推荐</span>
                    </button>
                    
                    {templates.slice(0, 7).map((template) => (
                      <button
                        key={template.id}
                        onClick={() => setSelectedTemplate(template.id)}
                        className={`p-3 rounded-xl border-2 transition-all ${
                          selectedTemplate === template.id 
                            ? 'border-white bg-white/20' 
                            : 'border-white/20 hover:border-white/40'
                        }`}
                      >
                        <div className="aspect-video rounded bg-gradient-to-br from-white/20 to-white/5 mb-2" />
                        <span className="text-xs truncate block">{template.name}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* 错误提示 */}
              {error && (
                <div className="mb-4 p-3 rounded-xl bg-red-500/20 border border-red-500/30 text-red-200 text-sm">
                  {error}
                </div>
              )}

              {/* 生成按钮 */}
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleGenerate}
                disabled={!title.trim() || isGenerating}
                className="w-full flex items-center justify-center gap-2 bg-white text-purple-600 px-6 py-4 rounded-xl font-semibold text-lg shadow-lg disabled:opacity-50"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    生成中...
                  </>
                ) : (
                  <>
                    <Wand2 className="w-5 h-5" />
                    开始生成
                  </>
                )}
              </motion.button>
            </motion.div>

            {/* 生成状态 */}
            {task && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="mt-6 glass rounded-2xl p-6"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    task.status === 'completed' ? 'bg-green-500/20' :
                    task.status === 'failed' ? 'bg-red-500/20' :
                    'bg-yellow-500/20'
                  }`}>
                    {task.status === 'completed' ? (
                      <Check className="w-6 h-6 text-green-400" />
                    ) : task.status === 'failed' ? (
                      <span className="text-red-400">!</span>
                    ) : (
                      <Loader2 className="w-6 h-6 text-yellow-400 animate-spin" />
                    )}
                  </div>
                  
                  <div className="flex-1">
                    <h3 className="font-semibold">
                      {task.status === 'completed' ? '生成完成！' :
                       task.status === 'failed' ? '生成失败' :
                       task.status === 'cancelled' ? '已取消' :
                       '正在生成...'}
                    </h3>
                    <p className="text-white/60 text-sm">{task.message}</p>
                    
                    {task.status === 'processing' && (
                      <div className="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-gradient-to-r from-yellow-400 to-pink-400"
                          initial={{ width: 0 }}
                          animate={{ width: '60%' }}
                          transition={{ duration: task.estimated_time || 60, ease: 'linear' }}
                        />
                      </div>
                    )}
                  </div>
                  
                  {task.status === 'processing' && (
                    <button
                      onClick={cancel}
                      className="px-4 py-2 rounded-lg glass hover:bg-white/20 text-sm"
                    >
                      取消
                    </button>
                  )}
                  
                  {task.status === 'completed' && task.result && (
                    <button
                      onClick={() => router.push(`/editor/${task.result.ppt_id}`)}
                      className="flex items-center gap-1 px-4 py-2 rounded-lg bg-white text-purple-600 text-sm font-medium"
                    >
                      编辑
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
