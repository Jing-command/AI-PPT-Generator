"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { 
  ChevronLeft, 
  Plus, 
  Trash2, 
  Undo2, 
  Redo2, 
  Layout,
  Type,
  Image,
  Download,
  Save,
  MoreVertical,
  Play
} from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { usePPTDetail } from "@/hooks/usePPT";
import { useSlides } from "@/hooks/useSlides";
import FloatingShapes from "@/components/FloatingShapes";

// 幻灯片缩略图组件
function SlideThumbnail({ 
  slide, 
  index, 
  isActive, 
  onClick 
}: { 
  slide: any; 
  index: number; 
  isActive: boolean; 
  onClick: () => void;
}) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      onClick={onClick}
      className={`relative cursor-pointer rounded-lg overflow-hidden border-2 transition-all ${
        isActive 
          ? 'border-white shadow-lg' 
          : 'border-white/20 hover:border-white/40'
      }`}
    >
      <div className="aspect-video bg-gradient-to-br from-white/10 to-white/5 p-3">
        <p className="text-xs text-white/60 mb-1">{index + 1}</p>
        <p className="text-sm font-medium truncate">{slide.title || "无标题"}</p>
        <div className="mt-2 space-y-1">
          <div className="h-2 bg-white/20 rounded w-3/4" />
          <div className="h-2 bg-white/10 rounded w-1/2" />
        </div>
      </div>
    </motion.div>
  );
}

export default function EditorPage() {
  const router = useRouter();
  const params = useParams();
  const pptId = params.id as string;
  
  const { ppt, isLoading: pptLoading, updatePPT } = usePPTDetail(pptId);
  const { 
    slides, 
    currentSlide, 
    isLoading: slidesLoading,
    loadSlides,
    selectSlide,
    addSlide,
    updateSlide,
    deleteSlide,
    undo,
    redo,
  } = useSlides(pptId);
  
  const [title, setTitle] = useState("");
  const [slideContent, setSlideContent] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  // 加载数据
  useEffect(() => {
    if (pptId) {
      loadSlides();
    }
  }, [pptId, loadSlides]);

  // 同步标题
  useEffect(() => {
    if (ppt) {
      setTitle(ppt.title || "");
    }
  }, [ppt]);

  // 同步当前幻灯片内容
  useEffect(() => {
    if (currentSlide) {
      setSlideContent(currentSlide.content?.text || "");
    }
  }, [currentSlide]);

  // 保存 PPT 标题
  const handleSaveTitle = async () => {
    if (!pptId || title === ppt?.title) return;
    setIsSaving(true);
    try {
      await updatePPT({ title });
    } finally {
      setIsSaving(false);
    }
  };

  // 保存幻灯片内容
  const handleSaveSlide = async () => {
    if (!currentSlide) return;
    setIsSaving(true);
    try {
      await updateSlide(currentSlide.id, {
        content: { text: slideContent },
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (pptLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-white/20 border-t-white rounded-full" />
      </div>
    );
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
      <FloatingShapes />

      <div className="relative z-10 flex flex-col h-screen">
        {/* 顶部工具栏 */}
        <header className="glass border-b border-white/10">
          <div className="flex items-center justify-between px-4 h-14">
            <div className="flex items-center gap-4">
              <Link href="/dashboard"
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </Link>
              
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                onBlur={handleSaveTitle}
                placeholder="PPT 标题"
                className="bg-transparent font-medium text-lg focus:outline-none min-w-[200px]"
              />
              
              {isSaving && (
                <span className="text-xs text-white/50">保存中...</span>
              )}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => undo()}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                title="撤销"
              >
                <Undo2 className="w-5 h-5" />
              </button>
              
              <button
                onClick={() => redo()}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                title="重做"
              >
                <Redo2 className="w-5 h-5" />
              </button>
              
              <div className="w-px h-6 bg-white/20 mx-2" />
              
              <button
                onClick={handleSaveSlide}
                disabled={isSaving}
                className="flex items-center gap-2 px-4 py-2 bg-white text-purple-600 rounded-full font-medium text-sm hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                <Save className="w-4 h-4" />
                保存
              </button>
              
              <Link
                href={`/export/${pptId}`}
                className="flex items-center gap-2 px-4 py-2 glass rounded-full font-medium text-sm hover:bg-white/20 transition-colors"
              >
                <Download className="w-4 h-4" />
                导出
              </Link>
            </div>
          </div>
        </header>

        {/* 主体内容 */}
        <div className="flex-1 flex overflow-hidden">
          {/* 左侧幻灯片列表 */}
          <aside className="w-64 glass border-r border-white/10 flex flex-col">
            <div className="p-4 border-b border-white/10 flex items-center justify-between">
              <span className="text-sm font-medium">幻灯片 ({slides.length})</span>
              
              <button
                onClick={() => addSlide()}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-3 space-y-3">
              {slidesLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin w-6 h-6 border-2 border-white/20 border-t-white rounded-full" />
                </div>
              ) : (
                slides.map((slide, index) => (
                  <SlideThumbnail
                    key={slide.id}
                    slide={slide}
                    index={index}
                    isActive={currentSlide?.id === slide.id}
                    onClick={() => selectSlide(slide.id)}
                  />
                ))
              )}
            </div>
          </aside>

          {/* 中间编辑区 */}
          <main className="flex-1 flex flex-col">
            <div className="flex-1 p-8 flex items-center justify-center">
              <div className="w-full max-w-4xl aspect-video glass rounded-2xl p-8 overflow-auto">
                {currentSlide ? (
                  <div className="h-full flex flex-col">
                    <input
                      type="text"
                      value={currentSlide.title || ""}
                      onChange={(e) => updateSlide(currentSlide.id, { title: e.target.value })}
                      placeholder="幻灯片标题"
                      className="text-3xl font-bold bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-2 mb-4 transition-colors"
                    />
                    
                    <textarea
                      value={slideContent}
                      onChange={(e) => setSlideContent(e.target.value)}
                      placeholder="在此输入内容..."
                      className="flex-1 bg-transparent resize-none focus:outline-none text-lg leading-relaxed"
                    />
                  </div>
                ) : (
                  <div className="h-full flex items-center justify-center text-white/40">
                    <p>选择一个幻灯片开始编辑</p>
                  </div>
                )}
              </div>
            </div>
          </main>

          {/* 右侧属性面板 */}
          <aside className="w-72 glass border-l border-white/10">
            <div className="p-4 border-b border-white/10">
              <span className="text-sm font-medium">属性</span>
            </div>
            
            <div className="p-4 space-y-6">
              {currentSlide ? (
                <>
                  <div>
                    <label className="text-sm text-white/60 mb-2 block">布局</label>
                    <div className="grid grid-cols-2 gap-2">
                      {['title', 'title-content', 'two-column', 'image-text'].map((layout) => (
                        <button
                          key={layout}
                          onClick={() => updateSlide(currentSlide.id, { layout })}
                          className={`p-3 rounded-lg border transition-all ${
                            currentSlide.layout === layout
                              ? 'border-white bg-white/20'
                              : 'border-white/20 hover:border-white/40'
                          }`}
                        >
                          <Layout className="w-5 h-5 mx-auto mb-1" />
                          <span className="text-xs">{layout}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="text-sm text-white/60 mb-2 block">备注</label>
                    <textarea
                      value={currentSlide.notes || ""}
                      onChange={(e) => updateSlide(currentSlide.id, { notes: e.target.value })}
                      placeholder="演讲者备注..."
                      rows={4}
                      className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-sm focus:outline-none focus:border-white/40 resize-none"
                    />
                  </div>

                  <button
                    onClick={() => deleteSlide(currentSlide.id)}
                    className="w-full flex items-center justify-center gap-2 p-3 rounded-lg bg-red-500/20 text-red-300 hover:bg-red-500/30 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                    删除幻灯片
                  </button>
                </>
              ) : (
                <p className="text-white/40 text-center py-8">选择幻灯片查看属性</p>
              )}
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}
