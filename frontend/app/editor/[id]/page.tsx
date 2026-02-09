"use client";

import { useCallback, useEffect, useRef, useState } from "react";
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
import { useAuthGuard } from "@/components/AuthGuard";
import FloatingShapes from "@/components/FloatingShapes";

// 幻灯片缩略图组件 - 显示完整的 PPT 页面预览
function SlideThumbnail({ 
  slide, 
  index, 
  isActive, 
  onClick,
  editingContent,
}: { 
  slide: any; 
  index: number; 
  isActive: boolean; 
  onClick: () => void;
  editingContent?: { title?: string; text?: string; second_column?: string; subtitle?: string };
}) {
  // 合并编辑中的内容和原始内容
  const content = {
    ...slide.content,
    ...editingContent,
  };
  const layoutType = slide.layout?.type || 'title-content';
  
  // 根据实际布局和内容渲染完整预览
  const renderSlidePreview = () => {
    const title = content.title || '无标题';
    const text = content.text || '';
    const secondColumn = content.second_column || '';
    const subtitle = content.subtitle || '';
    
    switch (layoutType) {
      case 'title':
        return (
          <div className="h-full flex flex-col items-center justify-center p-2 text-center overflow-hidden">
            <p className="text-[8px] font-bold text-white/90 line-clamp-2 leading-tight">{title}</p>
            {subtitle && (
              <p className="text-[6px] text-white/60 mt-1 line-clamp-1">{subtitle}</p>
            )}
          </div>
        );
      
      case 'two-column':
        return (
          <div className="h-full flex flex-col p-2 overflow-hidden">
            <p className="text-[8px] font-bold text-white/90 mb-1 line-clamp-1">{title}</p>
            <div className="flex-1 flex gap-1 min-h-0">
              <div className="flex-1 bg-white/5 rounded p-1 overflow-hidden">
                <p className="text-[5px] text-white/70 line-clamp-3 leading-tight">{text || '...'}</p>
              </div>
              <div className="flex-1 bg-white/5 rounded p-1 overflow-hidden">
                <p className="text-[5px] text-white/70 line-clamp-3 leading-tight">{secondColumn || '...'}</p>
              </div>
            </div>
          </div>
        );
      
      case 'image-text':
        return (
          <div className="h-full flex flex-col p-2 overflow-hidden">
            <p className="text-[8px] font-bold text-white/90 mb-1 line-clamp-1">{title}</p>
            <div className="flex-1 flex gap-1 min-h-0">
              <div className="flex-1 bg-white/10 rounded flex items-center justify-center overflow-hidden">
                {content.image_url ? (
                  <div className="w-full h-full bg-white/20" />
                ) : (
                  <span className="text-[6px] text-white/30">图</span>
                )}
              </div>
              <div className="flex-1 bg-white/5 rounded p-1 overflow-hidden">
                <p className="text-[5px] text-white/70 line-clamp-3 leading-tight">{text || '...'}</p>
              </div>
            </div>
          </div>
        );
      
      default: // title-content
        return (
          <div className="h-full flex flex-col p-2 overflow-hidden">
            <p className="text-[8px] font-bold text-white/90 mb-1 line-clamp-1">{title}</p>
            <div className="flex-1 bg-white/5 rounded p-1 overflow-hidden">
              <p className="text-[5px] text-white/70 line-clamp-4 leading-tight">{text || '...'}</p>
            </div>
          </div>
        );
    }
  };
  
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
      <div className="aspect-video bg-gradient-to-br from-white/10 to-white/5 overflow-hidden relative">
        <div className="absolute top-1 left-1 z-10">
          <span className="text-[10px] text-white/60">{index + 1}</span>
        </div>
        {renderSlidePreview()}
      </div>
    </motion.div>
  );
}

// 幻灯片编辑器组件 - 根据布局类型渲染不同界面
function SlideEditor({
  slide,
  slideTitle,
  slideContent,
  setSlideTitle,
  setSlideContent,
  handleSaveSlideTitle,
  handleSaveSlide,
  updateSlide,
  onContentChange,
  setEditingContent,
}: {
  slide: any;
  slideTitle: string;
  slideContent: string;
  setSlideTitle: (v: string) => void;
  setSlideContent: (v: string) => void;
  handleSaveSlideTitle: () => void;
  handleSaveSlide: () => void;
  updateSlide: (id: string, data: any) => Promise<any>;
  onContentChange?: (content: any) => void;
  setEditingContent?: React.Dispatch<React.SetStateAction<{[slideId: string]: any}>>;
}) {
  const layoutType = slide.layout?.type || 'title-content';
  
  const [secondColumn, setSecondColumn] = useState(slide.content?.second_column || '');
  const [subtitle, setSubtitle] = useState(slide.content?.subtitle || '');
  const [imageUrl, setImageUrl] = useState(slide.content?.image_url || '');

  // 同步外部状态变化（用于切换幻灯片时）
  useEffect(() => {
    setSecondColumn(slide.content?.second_column || '');
    setSubtitle(slide.content?.subtitle || '');
    setImageUrl(slide.content?.image_url || '');
  }, [slide.id]);

  // 通知父组件内容变化（用于实时预览）
  // 使用 ref 避免循环依赖
  const onContentChangeRef = useRef(onContentChange);
  onContentChangeRef.current = onContentChange;
  
  useEffect(() => {
    onContentChangeRef.current?.({
      title: slideTitle,
      text: slideContent,
      second_column: secondColumn,
      subtitle: subtitle,
    });
  }, [slideTitle, slideContent, secondColumn, subtitle]);

  // 标题布局 - 仅大标题和副标题
  if (layoutType === 'title') {
    // 保存副标题
    const handleSaveSubtitle = async () => {
      if (subtitle === slide.content?.subtitle) return;
      try {
        await updateSlide(slide.id, {
          content: { ...slide.content, subtitle: subtitle },
        });
        // 保存成功后清除编辑缓存
        setEditingContent?.(prev => {
          const next = { ...prev };
          if (next[slide.id]) {
            delete next[slide.id];
          }
          return next;
        });
      } catch (err) {
        console.error('保存副标题失败:', err);
      }
    };

    return (
      <div className="h-full flex flex-col items-center justify-center text-center">
        <input
          type="text"
          value={slideTitle}
          onChange={(e) => setSlideTitle(e.target.value)}
          onBlur={handleSaveSlideTitle}
          placeholder="输入标题"
          className="text-4xl font-bold bg-transparent border-b-2 border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-2 mb-4 transition-colors text-center w-full"
        />
        <input
          type="text"
          value={subtitle}
          onChange={(e) => setSubtitle(e.target.value)}
          onBlur={handleSaveSubtitle}
          placeholder="输入副标题"
          className="text-xl text-white/70 bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-1 transition-colors text-center w-3/4"
        />
      </div>
    );
  }

  // 双栏布局
  if (layoutType === 'two-column') {
    // 保存右栏内容
    const handleSaveSecondColumn = async () => {
      if (secondColumn === slide.content?.second_column) return;
      try {
        await updateSlide(slide.id, {
          content: { ...slide.content, second_column: secondColumn },
        });
        // 保存成功后清除编辑缓存
        setEditingContent?.(prev => {
          const next = { ...prev };
          if (next[slide.id]) {
            delete next[slide.id];
          }
          return next;
        });
      } catch (err) {
        console.error('保存右栏内容失败:', err);
      }
    };

    return (
      <div className="h-full flex flex-col">
        <input
          type="text"
          value={slideTitle}
          onChange={(e) => setSlideTitle(e.target.value)}
          onBlur={handleSaveSlideTitle}
          placeholder="标题"
          className="text-2xl font-bold bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-2 mb-4 transition-colors"
        />
        <div className="flex-1 grid grid-cols-2 gap-6">
          <textarea
            value={slideContent}
            onChange={(e) => setSlideContent(e.target.value)}
            onBlur={handleSaveSlide}
            placeholder="左栏内容..."
            className="bg-white/5 rounded-lg p-4 resize-none focus:outline-none focus:ring-2 focus:ring-white/20"
          />
          <textarea
            value={secondColumn}
            onChange={(e) => setSecondColumn(e.target.value)}
            onBlur={handleSaveSecondColumn}
            placeholder="右栏内容..."
            className="bg-white/5 rounded-lg p-4 resize-none focus:outline-none focus:ring-2 focus:ring-white/20"
          />
        </div>
      </div>
    );
  }

  // 图文混排布局
  if (layoutType === 'image-text') {
    // 保存图片 URL
    const handleSaveImageUrl = async () => {
      if (imageUrl === slide.content?.image_url) return;
      try {
        await updateSlide(slide.id, {
          content: { ...slide.content, image_url: imageUrl },
        });
        // 保存成功后清除编辑缓存
        setEditingContent?.(prev => {
          const next = { ...prev };
          if (next[slide.id]) {
            delete next[slide.id];
          }
          return next;
        });
      } catch (err) {
        console.error('保存图片URL失败:', err);
      }
    };

    return (
      <div className="h-full flex flex-col">
        <input
          type="text"
          value={slideTitle}
          onChange={(e) => setSlideTitle(e.target.value)}
          onBlur={handleSaveSlideTitle}
          placeholder="标题"
          className="text-2xl font-bold bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-2 mb-4 transition-colors"
        />
        <div className="flex-1 grid grid-cols-2 gap-6">
          <div className="bg-white/5 rounded-lg flex flex-col">
            <div className="flex-1 flex items-center justify-center text-white/30">
              <div className="text-center">
                <Image className="w-12 h-12 mx-auto mb-2" />
                <span className="text-sm">图片区域</span>
              </div>
            </div>
            <input
              type="text"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              onBlur={handleSaveImageUrl}
              placeholder="图片 URL"
              className="px-3 py-2 bg-white/10 text-sm focus:outline-none border-t border-white/10"
            />
          </div>
          <textarea
            value={slideContent}
            onChange={(e) => setSlideContent(e.target.value)}
            onBlur={handleSaveSlide}
            placeholder="文字内容..."
            className="bg-white/5 rounded-lg p-4 resize-none focus:outline-none focus:ring-2 focus:ring-white/20"
          />
        </div>
      </div>
    );
  }

  // 默认 title-content 布局
  return (
    <div className="h-full flex flex-col">
      <input
        type="text"
        value={slideTitle}
        onChange={(e) => setSlideTitle(e.target.value)}
        onBlur={handleSaveSlideTitle}
        placeholder="幻灯片标题"
        className="text-3xl font-bold bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-2 mb-4 transition-colors"
      />
      <textarea
        value={slideContent}
        onChange={(e) => setSlideContent(e.target.value)}
        onBlur={handleSaveSlide}
        placeholder="在此输入内容..."
        className="flex-1 bg-transparent resize-none focus:outline-none text-lg leading-relaxed"
      />
    </div>
  );
}

export default function EditorPage() {
  const router = useRouter();
  const params = useParams();
  const pptId = params.id as string;
  
  const { isLoading: authLoading } = useAuthGuard(true);
  const { ppt, isLoading: pptLoading, updatePPT } = usePPTDetail(pptId);
  const { 
    slides, 
    currentSlide, 
    isLoading: slidesLoading,
    error: slidesError,
    loadSlides,
    selectSlide,
    addSlide,
    updateSlide,
    deleteSlide,
    undo,
    redo,
  } = useSlides(pptId);
  
  const [title, setTitle] = useState("");
  const [slideTitle, setSlideTitle] = useState("");
  const [slideContent, setSlideContent] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  
  // 当前编辑中的内容（用于实时预览缩略图）
  const [editingContent, setEditingContent] = useState<{[slideId: string]: any}>({});

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
      setSlideTitle(currentSlide.content?.title || "");
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

  // 保存幻灯片标题
  const handleSaveSlideTitle = async () => {
    if (!currentSlide) return;
    const editedTitle = editingContent[currentSlide.id]?.title ?? slideTitle;
    if (editedTitle === currentSlide.content?.title) return;
    setIsSaving(true);
    try {
      await updateSlide(currentSlide.id, {
        content: { ...currentSlide.content, title: editedTitle },
      });
      // 清除已保存的标题缓存
      setEditingContent(prev => {
        const next = { ...prev };
        if (next[currentSlide.id]) {
          next[currentSlide.id] = { ...next[currentSlide.id], title: undefined };
        }
        return next;
      });
    } finally {
      setIsSaving(false);
    }
  };

  // 保存幻灯片内容
  const handleSaveSlide = async () => {
    if (!currentSlide) return;
    const editedText = editingContent[currentSlide.id]?.text ?? slideContent;
    if (editedText === currentSlide.content?.text) return;
    setIsSaving(true);
    try {
      await updateSlide(currentSlide.id, {
        content: { ...currentSlide.content, text: editedText },
      });
      // 清除已保存的内容缓存
      setEditingContent(prev => {
        const next = { ...prev };
        if (next[currentSlide.id]) {
          next[currentSlide.id] = { ...next[currentSlide.id], text: undefined };
        }
        return next;
      });
    } finally {
      setIsSaving(false);
    }
  };

  // 切换幻灯片时自动保存
  const handleSelectSlide = async (slideId: string) => {
    if (currentSlide && editingContent[currentSlide.id]) {
      const edited = editingContent[currentSlide.id];
      const current = currentSlide.content || {};
      
      // 检查是否有变更
      const hasChanges = 
        edited.title !== current.title ||
        edited.text !== current.text ||
        edited.second_column !== current.second_column ||
        edited.subtitle !== current.subtitle;
      
      if (hasChanges) {
        await updateSlide(currentSlide.id, {
          content: { 
            ...current, 
            title: edited.title ?? current.title,
            text: edited.text ?? current.text,
            second_column: edited.second_column ?? current.second_column,
            subtitle: edited.subtitle ?? current.subtitle,
          },
        });
        // 清除已保存的编辑缓存
        setEditingContent(prev => {
          const next = { ...prev };
          delete next[currentSlide.id];
          return next;
        });
      }
    }
    selectSlide(slideId);
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
                    onClick={() => handleSelectSlide(slide.id)}
                    editingContent={editingContent[slide.id]}
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
                  <SlideEditor 
                    slide={currentSlide}
                    slideTitle={slideTitle}
                    slideContent={slideContent}
                    setSlideTitle={setSlideTitle}
                    setSlideContent={setSlideContent}
                    handleSaveSlideTitle={handleSaveSlideTitle}
                    handleSaveSlide={handleSaveSlide}
                    updateSlide={updateSlide}
                    onContentChange={(content) => {
                      setEditingContent(prev => ({
                        ...prev,
                        [currentSlide.id]: content
                      }));
                    }}
                    setEditingContent={setEditingContent}
                  />
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
              {slidesError && (
                <div className="p-3 rounded-lg bg-red-500/20 text-red-300 text-sm">
                  {slidesError}
                </div>
              )}
              {currentSlide ? (
                <>
                  <div>
                    <label className="text-sm text-white/60 mb-2 block">布局</label>
                    <div className="grid grid-cols-2 gap-2">
                      {['title', 'title-content', 'two-column', 'image-text'].map((layout) => (
                        <button
                          key={layout}
                          onClick={async () => {
                            console.log('Changing layout to:', layout);
                            try {
                              await updateSlide(currentSlide.id, { layout: { type: layout } });
                              console.log('Layout updated successfully');
                            } catch (err) {
                              console.error('Layout update failed:', err);
                            }
                          }}
                          className={`p-3 rounded-lg border transition-all ${
                            currentSlide.layout?.type === layout
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
