import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, FileText, Trash2 } from 'lucide-react'
import { pptService } from '@/services'
import { usePPTStore } from '@/stores'
import { Button } from '@/components/common/Button'
import { Card } from '@/components/common/Card'
import { formatDate } from '@/utils'
import type { Presentation } from '@/types'

export default function DashboardPage() {
  const { presentations, setPresentations, isLoading, setLoading } = usePPTStore()
  const [deleteId, setDeleteId] = useState<string | null>(null)

  useEffect(() => {
    loadPresentations()
  }, [])

  const loadPresentations = async () => {
    setLoading(true)
    try {
      const data = await pptService.getPresentations()
      setPresentations(data.presentations || [], data.total || 0)
    } catch (err) {
      console.error('Failed to load presentations:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    try {
      const newPPT = await pptService.createPresentation({
        title: '未命名演示文稿',
      })
      window.location.href = `/ppt/${newPPT.id}`
    } catch (err) {
      console.error('Failed to create presentation:', err)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除这个 PPT 吗？')) return
    
    setDeleteId(id)
    try {
      await pptService.deletePresentation(id)
      await loadPresentations()
    } catch (err) {
      console.error('Failed to delete:', err)
    } finally {
      setDeleteId(null)
    }
  }

  return (
    <div className="space-y-6">
      {/* 头部 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">我的 PPT</h1>
          <p className="text-gray-500 mt-1">管理和编辑您的演示文稿</p>
        </div>
        
        <Button onClick={handleCreate}>
          <Plus className="w-4 h-4 mr-2" />
          新建 PPT
        </Button>
      </div>

      {/* 列表 */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : presentations.length === 0 ? (
        <Card className="p-12 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <FileText className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">还没有 PPT</h3>
          <p className="text-gray-500 mb-4">创建您的第一个演示文稿开始使用</p>
          <Button onClick={handleCreate}>
            <Plus className="w-4 h-4 mr-2" />
            创建 PPT
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {presentations.map((ppt: Presentation) => (
            <Card key={ppt.id} className="group relative">
              <Link to={`/ppt/${ppt.id}`} className="block p-6">
                {/* 缩略图占位 */}
                <div className="aspect-video bg-gray-100 rounded-lg mb-4 flex items-center justify-center">
                  <FileText className="w-12 h-12 text-gray-300" />
                </div>
                
                <h3 className="font-semibold text-gray-900 truncate">{ppt.title}</h3>
                <p className="text-sm text-gray-500 mt-1">
                  {ppt.slides?.length || 0} 页 · {formatDate(ppt.updated_at)}
                </p>
                
                <div className="mt-3 flex items-center gap-2">
                  <span className={`
                    px-2 py-1 text-xs rounded-full
                    ${ppt.status === 'published' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}
                  `}>
                    {ppt.status === 'published' ? '已发布' : '草稿'}
                  </span>
                </div>
              </Link>
              
              {/* 操作按钮 */}
              <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="relative">
                  <button
                    onClick={() => handleDelete(ppt.id)}
                    disabled={deleteId === ppt.id}
                    className="p-2 bg-white rounded-lg shadow-sm text-red-600 hover:bg-red-50"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
