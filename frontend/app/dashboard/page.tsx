"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { 
  Plus, 
  FileText, 
  MoreVertical, 
  Trash2, 
  Download, 
  Loader2,
  Wand2,
  Layout
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { usePPTList } from "@/hooks/usePPT";
import { useAuth } from "@/hooks/useAuth";
import Navbar from "@/components/Navbar";
import FloatingShapes from "@/components/FloatingShapes";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const { ppts, isLoading, createPPT, deletePPT } = usePPTList();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  // 未登录跳转到登录页
  if (!authLoading && !isAuthenticated) {
    router.push("/login");
    return null;
  }

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    setIsCreating(true);
    try {
      const ppt = await createPPT({ title: newTitle });
      setShowCreateModal(false);
      setNewTitle("");
      router.push(`/editor/${ppt.id}`);
    } finally {
      setIsCreating(false);
    }
  };

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
          <div className="max-w-6xl mx-auto">
            {/* 头部 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-between mb-8"
            >
              <div>
                <h1 className="text-3xl font-bold text-gradient mb-2">
                  我的 PPT
                </h1>
                <p className="text-white/70">
                  共 {ppts.length} 个演示文稿
                </p>
              </div>

              <div className="flex gap-3">
                <Link
                  href="/generate"
                  className="hidden sm:flex items-center gap-2 glass px-5 py-2.5 rounded-full hover:bg-white/20 transition-colors"
                >
                  <Wand2 className="w-4 h-4" />
                  AI 生成
                </Link>
                
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setShowCreateModal(true)}
                  className="flex items-center gap-2 bg-white text-purple-600 px-5 py-2.5 rounded-full font-medium shadow-lg"
                >
                  <Plus className="w-4 h-4" />
                  新建
                </motion.button>
              </div>
            </motion.div>

            {/* PPT 列表 */}
            {isLoading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="w-8 h-8 animate-spin text-white/50" />
              </div>
            ) : ppts.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-20"
              >
                <div className="w-20 h-20 mx-auto mb-6 rounded-2xl glass flex items-center justify-center"
003e
                  <FileText className="w-10 h-10 text-white/50" />
                </div>
                <p className="text-white/70 text-lg mb-4">还没有 PPT</p>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  onClick={() => setShowCreateModal(true)}
                  className="inline-flex items-center gap-2 bg-white text-purple-600 px-6 py-3 rounded-full font-medium"
                >
                  <Plus className="w-4 h-4" />
                  创建第一个 PPT
                </motion.button>
              </motion.div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {ppts.map((ppt, index) => (
                  <motion.div
                    key={ppt.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="group glass-card rounded-2xl p-5 hover:bg-white/15 transition-all cursor-pointer"
                  >
                    <Link href={`/editor/${ppt.id}`}>
                      <div className="aspect-video rounded-xl bg-gradient-to-br from-white/10 to-white/5 mb-4 flex items-center justify-center">
                        <Layout className="w-12 h-12 text-white/30" />
                      </div>
                      
                      <h3 className="font-semibold text-lg mb-1 truncate">{ppt.title}</h3>
                      <p className="text-white/50 text-sm mb-3">
                        {ppt.slide_count || 0} 页 · {new Date(ppt.updated_at).toLocaleDateString('zh-CN')}
                      </p>
                    </Link>
                    
                    <div className="flex items-center justify-between pt-3 border-t border-white/10">
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        ppt.status === 'completed' ? 'bg-green-500/20 text-green-300' :
                        ppt.status === 'generating' ? 'bg-yellow-500/20 text-yellow-300' :
                        'bg-white/10 text-white/70'
                      }`}>
                        {ppt.status === 'completed' ? '已完成' :
                         ppt.status === 'generating' ? '生成中' : '草稿'}
                      </span>
                      
                      <div className="flex gap-1">
                        <button 
                          onClick={() => {/* TODO: 导出 */}}
                          className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                        >
                          <Download className="w-4 h-4 text-white/70" />
                        </button>
                        <button 
                          onClick={() => deletePPT(ppt.id)}
                          className="p-2 hover:bg-red-500/20 rounded-lg transition-colors group"
                        >
                          <Trash2 className="w-4 h-4 text-white/70 group-hover:text-red-400" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 创建弹窗 */}
      {showCreateModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="glass rounded-2xl p-6 w-full max-w-md"
          >
            <h2 className="text-xl font-semibold mb-4">创建新 PPT</h2>
            
            <input
              type="text"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="输入 PPT 标题"
              className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:border-white/40 mb-4"
              onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
              autoFocus
            />
            
            <div className="flex gap-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 py-2.5 rounded-xl glass hover:bg-white/20 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleCreate}
                disabled={!newTitle.trim() || isCreating}
                className="flex-1 py-2.5 rounded-xl bg-white text-purple-600 font-medium disabled:opacity-50"
              >
                {isCreating ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : '创建'}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </main>
  );
}
