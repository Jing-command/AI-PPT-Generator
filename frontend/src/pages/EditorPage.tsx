import { useEffect, useState, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ChevronLeft, Undo, Redo, Download, Plus, Trash2, Wand2, X, Loader2 } from 'lucide-react'
import { pptService, generationService, exportService } from '@/services'
import { usePPTStore } from '@/stores'
import { Button } from '@/components/common/Button'
import { Card } from '@/components/common/Card'
import type { Slide, GenerationTask } from '@/types'

// 防抖函数
function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export default function EditorPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const {
    currentPPT,
    slides,
    selectedSlideId,
    setCurrentPPT,
    setSlides,
    setSelectedSlideId,
    addSlide,
    deleteSlide,
    updateSlide,
    canUndo,
    canRedo,
    setCanUndo,
    setCanRedo,
    isSaving,
    setSaving,
  } = usePPTStore()

  const [isLoading, setIsLoading] = useState(true)
  const [showAiDialog, setShowAiDialog] = useState(false)
  const [aiPrompt, setAiPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  
  // AI生成任务状态
  const [generationTask, setGenerationTask] = useState<GenerationTask | null>(null)
  const [showGenerationProgress, setShowGenerationProgress] = useState(false)
  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // 幻灯片编辑防抖保存
  const saveSlide = useCallback(
    debounce(async (slideId: string, slideData: Partial<Slide>) => {
      if (!id) return
      setSaving(true)
      try {
        await pptService.updateSlide(id, slideId, slideData)
      } catch (err) {
        console.error('Failed to save slide:', err)
      } finally {
        setSaving(false)
      }
    }, 1500),
    [id, setSaving]
  )

  // 清理轮询
  const clearPollInterval = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current)
      pollIntervalRef.current = null
    }
  }

  useEffect(() => {
    if (id) {
      loadPPT(id)
    }
    // 组件卸载时清理轮询
    return () => {
      clearPollInterval()
    }
  }, [id])

  const loadPPT = async (pptId: string) => {
    setIsLoading(true)
    try {
      const data = await pptService.getPresentation(pptId)
      setCurrentPPT(data)
      setCanUndo(true)
      setCanRedo(false)
    } catch (err) {
      console.error('Failed to load PPT:', err)
      navigate('/')
    } finally {
      setIsLoading(false)
    }
  }

  // 轮询生成任务状态
  const pollGenerationStatus = (taskId: string) => {
    clearPollInterval()
    setShowGenerationProgress(true)
    
    pollIntervalRef.current = setInterval(async () => {
      try {
        const status = await generationService.getStatus(taskId)
        setGenerationTask(status)
        
        if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
          clearPollInterval()
          if (status.status === 'completed') {
            // 刷新PPT内容
            if (id) loadPPT(id)
            setTimeout(() => {
              setShowGenerationProgress(false)
              setGenerationTask(null)
            }, 3000)
          }
        }
      } catch (err) {
        console.error('Failed to poll generation status:', err)
      }
    }, 2000)
  }

  // 取消生成任务
  const handleCancelGeneration = async () => {
    if (!generationTask?.task_id) return
    try {
      await generationService.cancel(generationTask.task_id)
      clearPollInterval()
      setShowGenerationProgress(false)
      setGenerationTask(null)
    } catch (err) {
      console.error('Failed to cancel generation:', err)
    }
  }

  const handleAddSlide = async () => {
    if (!id) return
    
    const newSlide: Slide = {
      id: `slide-${Date.now()}`,
      type: 'content',
      content: { title: '新页面', text: '' },
    }
    
    try {
      await pptService.addSlide(id, newSlide)
      addSlide(newSlide)
    } catch (err) {
      console.error('Failed to add slide:', err)
    }
  }

  const handleDeleteSlide = async (slideId: string) => {
    if (!id) return
    if (!confirm('确定要删除这页吗？')) return
    
    try {
      await pptService.deleteSlide(id, slideId)
      deleteSlide(slideId)
    } catch (err) {
      console.error('Failed to delete slide:', err)
    }
  }

  const handleUndo = async () => {
    if (!id) return
    try {
      const result = await pptService.undo(id)
      if (result.state) {
        setSlides(result.state.slides || [])
      }
    } catch (err) {
      console.error('Undo failed:', err)
    }
  }

  const handleRedo = async () => {
    if (!id) return
    try {
      const result = await pptService.redo(id)
      if (result.state) {
        setSlides(result.state.slides || [])
      }
    } catch (err) {
      console.error('Redo failed:', err)
    }
  }

  const handleExport = async (format: 'pptx' | 'pdf') => {
    if (!id) return
    try {
      const result = await exportService.export(id, format)
      alert(`导出任务已创建，任务ID: ${result.export_task_id}`)
    } catch (err) {
      console.error('Export failed:', err)
    }
  }

  const handleAiGenerate = async () => {
    if (!aiPrompt.trim()) return
    
    setIsGenerating(true)
    try {
      const result = await generationService.generate({
        prompt: aiPrompt,
        num_slides: 5,
        language: 'zh',
      })
      
      setShowAiDialog(false)
      setAiPrompt('')
      
      // 开始轮询任务状态
      const initialTask: GenerationTask = {
        task_id: result.task_id,
        status: 'pending',
        progress: 0,
        estimated_time: 60,
        message: '任务已提交，正在生成中...',
      }
      setGenerationTask(initialTask)
      pollGenerationStatus(result.task_id)
      
    } catch (err) {
      console.error('AI generation failed:', err)
      alert('生成任务创建失败')
    } finally {
      setIsGenerating(false)
    }
  }

  const selectedSlide = slides.find((s) => s.id === selectedSlideId)

  // 处理标题变化（本地更新 + 自动保存）
  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!selectedSlide) return
    const newContent = { ...selectedSlide.content, title: e.target.value }
    updateSlide(selectedSlide.id, { content: newContent })
    saveSlide(selectedSlide.id, { content: newContent })
  }

  // 处理内容变化（本地更新 + 自动保存）
  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (!selectedSlide) return
    const newContent = { ...selectedSlide.content, text: e.target.value }
    updateSlide(selectedSlide.id, { content: newContent })
    saveSlide(selectedSlide.id, { content: newContent })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      {/* 工具栏 */}
      <div className="flex items-center justify-between px-4 py-2 bg-white border-b border-gray-200">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={() => navigate('/')}>
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <span className="font-medium">{currentPPT?.title}</span>
          {isSaving && <span className="text-xs text-gray-400">保存中...</span>}
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={handleUndo} disabled={!canUndo}>
            <Undo className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={handleRedo} disabled={!canRedo}>
            <Redo className="w-4 h-4" />
          </Button>
          <Button variant="secondary" size="sm" onClick={() => setShowAiDialog(true)}>
            <Wand2 className="w-4 h-4 mr-1" />
            AI 生成
          </Button>
          <Button variant="secondary" size="sm" onClick={() => handleExport('pptx')}>
            <Download className="w-4 h-4 mr-1" />
            导出
          </Button>
        </div>
      </div>

      {/* 生成进度条 */}
      {showGenerationProgress && generationTask && (
        <div className="bg-blue-50 border-b border-blue-200 px-4 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
              <span className="text-sm text-blue-800">{generationTask.message}</span>
              <span className="text-xs text-blue-600">
                {generationTask.status === 'pending' && '等待中...'}
                {generationTask.status === 'processing' && `生成中 ${generationTask.progress}%`}
                {generationTask.status === 'completed' && '✅ 生成完成'}
                {generationTask.status === 'failed' && '❌ 生成失败'}
                {generationTask.status === 'cancelled' && '已取消'}
              </span>
            </div>
            {(generationTask.status === 'pending' || generationTask.status === 'processing') && (
              <button
                onClick={handleCancelGeneration}
                className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
              >
                <X className="w-3 h-3" />
                取消
              </button>
            )}
          </div>
          {(generationTask.status === 'pending' || generationTask.status === 'processing') && (
            <div className="mt-2 h-1 bg-blue-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 transition-all duration-300"
                style={{ width: `${generationTask.progress}%` }}
              />
            </div>
          )}
        </div>
      )}

      {/* 主编辑区 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 左侧缩略图 */}
        <div className="w-64 bg-gray-50 border-r border-gray-200 overflow-y-auto p-4">
          <div className="space-y-2">
            {slides.map((slide, index) => (
              <div
                key={slide.id}
                onClick={() => setSelectedSlideId(slide.id)}
                className={`
                  relative p-3 rounded-lg cursor-pointer transition-colors
                  ${selectedSlideId === slide.id ? 'bg-white shadow-sm ring-2 ring-primary-500' : 'hover:bg-white'}
                `}
              >
                <div className="aspect-video bg-gray-100 rounded border border-gray-200 mb-2 flex items-center justify-center">
                  <span className="text-gray-400 text-sm">{index + 1}</span>
                </div>
                <p className="text-xs text-gray-600 truncate">{slide.content?.title || '无标题'}</p>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteSlide(slide.id)
                  }}
                  className="absolute top-2 right-2 p-1 opacity-0 hover:opacity-100 text-red-500"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>

          <Button variant="ghost" className="w-full mt-4" onClick={handleAddSlide}>
            <Plus className="w-4 h-4 mr-1" />
            添加页面
          </Button>
        </div>

        {/* 编辑画布 */}
        <div className="flex-1 bg-gray-100 p-8 overflow-auto">
          {selectedSlide ? (
            <div className="max-w-4xl mx-auto">
              <Card className="aspect-video bg-white p-8">
                <input
                  type="text"
                  value={selectedSlide.content?.title || ''}
                  onChange={handleTitleChange}
                  className="w-full text-3xl font-bold border-none focus:ring-0 p-0 placeholder-gray-300"
                  placeholder="输入标题"
                />
                <textarea
                  value={selectedSlide.content?.text || ''}
                  onChange={handleContentChange}
                  className="w-full h-64 mt-4 resize-none border-none focus:ring-0 p-0 placeholder-gray-300"
                  placeholder="输入内容..."
                />
              </Card>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              选择一个页面开始编辑
            </div>
          )}
        </div>
      </div>

      {/* AI 生成对话框 */}
      {showAiDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md p-6">
            <h3 className="text-lg font-semibold mb-4">AI 生成 PPT</h3>
            <textarea
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              className="w-full h-32 p-3 border border-gray-300 rounded-lg resize-none focus:border-primary-500 focus:ring-primary-500"
              placeholder="描述您想要的 PPT 内容，例如：制作一个关于人工智能发展历程的演示文稿..."
            />
            <div className="flex justify-end gap-2 mt-4">
              <Button variant="ghost" onClick={() => setShowAiDialog(false)}>取消</Button>
              <Button onClick={handleAiGenerate} isLoading={isGenerating}>开始生成</Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
