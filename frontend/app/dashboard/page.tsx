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
  Layout,
  Image
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { usePPTList } from "@/hooks/usePPT";
import { useAuthGuard } from "@/components/AuthGuard";
import Navbar from "@/components/Navbar";
import FloatingShapes from "@/components/FloatingShapes";

// PPT 缩略图组件 - 显示完整首页预览
function PPTThumbnail({ slide }: { slide: any }) {
  if (!slide) {
    return (
      <div className="aspect-video rounded-xl bg-gradient-to-br from-white/10 to-white/5 mb-4 flex items-center justify-center">
        <Layout className="w-12 h-12 text-white/30" />
      </div>
    );
  }

  const content = slide.content || {};
  const layoutType = slide.layout?.type || 'title-content';
  const title = content.title || '无标题';
  const text = content.text || '';
  const secondColumn = content.second_column || '';
  const subtitle = content.subtitle || '';

  // 根据布局渲染不同的预览
  switch (layoutType) {
    case 'title': {
      const titleBgStyle = content.image_url ? {
        backgroundImage: `linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url(${content.image_url})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      } : {};
      return (
        <div 
          className="aspect-video rounded-xl bg-gradient-to-br from-white/10 to-white/5 mb-4 flex flex-col items-center justify-center p-4 overflow-hidden"
          style={titleBgStyle}
        >
          <p className="text-sm font-bold text-white/90 text-center line-clamp-2">{title}</p>
          {subtitle && <p className="text-xs text-white/60 mt-1 line-clamp-1">{subtitle}</p>}
        </div>
      );
    }

    case 'two-column':
      return (
        <div className="aspect-video rounded-xl bg-gradient-to-br from-white/10 to-white/5 mb-4 flex flex-col p-3 overflow-hidden">
          <p className="text-xs font-bold text-white/90 mb-1 line-clamp-1">{title}</p>
          <div className="flex-1 flex gap-2 min-h-0">
            <div className="flex-1 bg-white/5 rounded p-2 overflow-hidden">
              <p className="text-[10px] text-white/70 line-clamp-4 leading-tight">{text || '...'}</p>
            </div>
            <div className="flex-1 bg-white/5 rounded p-2 overflow-hidden">
              <p className="text-[10px] text-white/70 line-clamp-4 leading-tight">{secondColumn || '...'}</p>
            </div>
          </div>
        </div>
      );

    case 'image-text':
      return (
        <div className="aspect-video rounded-xl bg-gradient-to-br from-white/10 to-white/5 mb-4 flex flex-col p-3 overflow-hidden">
          <p className="text-xs font-bold text-white/90 mb-1 line-clamp-1">{title}</p>
          <div className="flex-1 flex gap-2 min-h-0">
            <div className="flex-1 bg-white/10 rounded flex items-center justify-center overflow-hidden">
              {content.image_url ? (
                <img 
                  src={content.image_url} 
                  alt="Slide image"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    // If image fails to load, show placeholder
                    (e.target as HTMLImageElement).style.display = 'none';
                    (e.target as HTMLImageElement).parentElement?.classList.add('flex', 'items-center', 'justify-center');
                    const icon = document.createElement('div');
                    icon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-white/30"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>';
                    (e.target as HTMLImageElement).parentElement?.appendChild(icon.firstChild!);
                  }}
                />
              ) : (
                <Image className="w-6 h-6 text-white/30" />
              )}
            </div>
            <div className="flex-1 bg-white/5 rounded p-2 overflow-hidden">
              <p className="text-[10px] text-white/70 line-clamp-4 leading-tight">{text || '...'}</p>
            </div>
          </div>
        </div>
      );

    default: // title-content
      return (
        <div className="aspect-video rounded-xl bg-gradient-to-br from-white/10 to-white/5 mb-4 flex flex-col p-3 overflow-hidden">
          <p className="text-xs font-bold text-white/90 mb-1 line-clamp-1">{title}</p>
          <div className="flex-1 bg-white/5 rounded p-2 overflow-hidden">
            <p className="text-[10px] text-white/70 line-clamp-5 leading-tight">{text || '...'}</p>
          </div>
        </div>
      );
  }
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuthGuard(true);
  const { ppts, isLoading, createPPT, deletePPT } = usePPTList();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-white/50" />
      </div>
    );
  }

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    setIsCreating(true);
    try {
      const ppt = await createPPT({ title: newTitle }) as { id: string };
      setShowCreateModal(false);
      setNewTitle("");
      router.push(`/editor/${ppt.id}`);
    } finally {
      setIsCreating(false);
    }
  };

  const handleDelete = async (id: string) => {
    setDeletingId(id);
    try {
      await deletePPT(id);
    } catch (err: any) {
      alert('删除失败: ' + err.message);
    } finally {
      setDeletingId(null);
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
                <div className="w-20 h-20 mx-auto mb-6 rounded-2xl glass flex items-center justify-center">
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
                {ppts.map((ppt, index) => {
                  // 计算页数：优先使用 slide_count，否则使用 slides 数组长度
                  const slideCount = ppt.slide_count ?? (ppt.slides?.length || 0);
                  // 获取首页
                  const firstSlide = ppt.slides?.[0];
                  
                  return (
                  <motion.div
                    key={ppt.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="group glass-card rounded-2xl p-5 cursor-pointer will-change-transform"
                    style={{ transform: 'translateZ(0)' }}
                    whileHover={{ y: -4 }}
                  >
                    <Link href={`/editor/${ppt.id}`}>
                      {/* 缩略图 - 显示完整首页预览 */}
                      <PPTThumbnail slide={firstSlide} />
                      
                      <h3 className="font-semibold text-lg mb-1 truncate">{ppt.title}</h3>
                      <p className="text-white/50 text-sm mb-3">
                        {slideCount} 页 · {new Date(ppt.updated_at).toLocaleDateString('zh-CN')}
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
                          onClick={() => handleDelete(ppt.id)}
                          disabled={deletingId === ppt.id}
                          className="p-2 hover:bg-red-500/20 rounded-lg transition-colors group disabled:opacity-50"
                        >
                          {deletingId === ppt.id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Trash2 className="w-4 h-4 text-white/70 group-hover:text-red-400" />
                          )}
                        </button>
                      </div>
                    </div>
                  </motion.div>
                  );
                })}
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
