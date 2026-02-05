import { useEffect, useState } from 'react'
import { Layout } from 'lucide-react'
import { templateService, pptService } from '@/services'
import { Button } from '@/components/common/Button'
import { Card } from '@/components/common/Card'
import type { Template, TemplateCategory } from '@/types'

const CATEGORIES = [
  { id: 'all', name: '全部', icon: '✨' },
  { id: 'business', name: '商务', icon: '💼' },
  { id: 'education', name: '教育', icon: '📚' },
  { id: 'creative', name: '创意', icon: '🎨' },
  { id: 'minimal', name: '极简', icon: '⚪' },
]

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [, setCategories] = useState<TemplateCategory[]>([])
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [isLoading, setIsLoading] = useState(false)
  const [creatingId, setCreatingId] = useState<string | null>(null)

  useEffect(() => {
    loadTemplates()
    loadCategories()
  }, [selectedCategory])

  const loadTemplates = async () => {
    setIsLoading(true)
    try {
      const params = selectedCategory === 'all' ? {} : { category: selectedCategory }
      const data = await templateService.getTemplates(params)
      setTemplates(data?.templates || [])
    } catch (err) {
      console.error('Failed to load templates:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const loadCategories = async () => {
    try {
      const data = await templateService.getCategories()
      setCategories(data || [])
    } catch (err) {
      console.error('Failed to load categories:', err)
    }
  }

  const handleUseTemplate = async (template: Template) => {
    setCreatingId(template.id)
    try {
      const newPPT = await pptService.createPresentation({
        title: `${template.name} - 我的PPT`,
        template_id: template.id,
      })
      window.location.href = `/ppt/${newPPT.id}`
    } catch (err) {
      console.error('Failed to create from template:', err)
      setCreatingId(null)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">选择模板</h1>
        <p className="text-gray-500 mt-1">从预设模板快速创建专业 PPT</p>
      </div>

      {/* 分类筛选 */}
      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`
              px-4 py-2 rounded-lg text-sm font-medium transition-colors
              ${selectedCategory === cat.id
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'}
            `}
          >
            <span className="mr-1">{cat.icon}</span>
            {cat.name}
          </button>
        ))}
      </div>

      {/* 模板列表 */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {templates.map((template) => (
            <Card key={template.id} className="overflow-hidden group">
              {/* 缩略图 */}
              <div className="aspect-video bg-gradient-to-br from-primary-100 to-primary-50 flex items-center justify-center relative">
                <Layout className="w-12 h-12 text-primary-300" />
                
                {template.is_premium && (
                  <span className="absolute top-2 right-2 px-2 py-1 text-xs bg-yellow-400 text-yellow-900 rounded-full font-medium">
                    VIP
                  </span>
                )}
              </div>

              <div className="p-4">
                <h3 className="font-semibold text-gray-900">{template.name}</h3>
                <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                  {template.description || '暂无描述'}
                </p>
                
                <p className="text-xs text-gray-400 mt-2">
                  {template.usage_count} 次使用
                </p>

                <Button
                  className="w-full mt-4"
                  size="sm"
                  isLoading={creatingId === template.id}
                  onClick={() => handleUseTemplate(template)}
                >
                  {creatingId === template.id ? '创建中...' : '使用模板'}
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {!isLoading && templates.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">该分类下暂无模板</p>
        </div>
      )}
    </div>
  )
}
