import { useEffect, useState } from 'react'
import { Key, Plus, Trash2, Check, AlertCircle } from 'lucide-react'
import { apiKeyService } from '@/services'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common/Card'
import type { ApiKey } from '@/types'

const PROVIDERS = [
  { value: 'openai', label: 'OpenAI', prefix: 'sk-' },
  { value: 'anthropic', label: 'Anthropic', prefix: 'sk-ant-' },
  { value: 'kimi', label: 'Kimi', prefix: '' },
  { value: 'aliyun', label: '阿里云', prefix: 'AK-' },
  { value: 'tencent', label: '腾讯云', prefix: '' },
]

export default function SettingsPage() {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newKey, setNewKey] = useState({ name: '', api_key: '', provider: 'openai', is_default: false })
  const [error, setError] = useState('')

  useEffect(() => {
    loadApiKeys()
  }, [])

  const loadApiKeys = async () => {
    try {
      const data = await apiKeyService.getApiKeys()
      setApiKeys(data || [])
    } catch (err) {
      console.error('Failed to load API keys:', err)
    }
  }

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await apiKeyService.createApiKey(newKey)
      setShowAddForm(false)
      setNewKey({ name: '', api_key: '', provider: 'openai', is_default: false })
      await loadApiKeys()
    } catch (err) {
      setError(err instanceof Error ? err.message : '添加失败')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除这个 API Key 吗？')) return
    
    try {
      await apiKeyService.deleteApiKey(id)
      await loadApiKeys()
    } catch (err) {
      console.error('Failed to delete:', err)
    }
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">设置</h1>
        <p className="text-gray-500 mt-1">管理您的 API Key 和偏好设置</p>
      </div>

      {/* API Keys */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Key className="w-5 h-5" />
              API Key 管理
            </CardTitle>
          </div>
          <Button variant="secondary" size="sm" onClick={() => setShowAddForm(!showAddForm)}>
            <Plus className="w-4 h-4 mr-1" />
            添加
          </Button>
        </CardHeader>

        <CardContent>
          {/* 添加表单 */}
          {showAddForm && (
            <form onSubmit={handleAdd} className="mb-6 p-4 bg-gray-50 rounded-lg space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="名称"
                  value={newKey.name}
                  onChange={(e) => setNewKey({ ...newKey, name: e.target.value })}
                  placeholder="例如：我的 OpenAI Key"
                  required
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">提供商</label>
                  <select
                    value={newKey.provider}
                    onChange={(e) => setNewKey({ ...newKey, provider: e.target.value })}
                    className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  >
                    {PROVIDERS.map((p) => (
                      <option key={p.value} value={p.value}>{p.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <Input
                label="API Key"
                type="password"
                value={newKey.api_key}
                onChange={(e) => setNewKey({ ...newKey, api_key: e.target.value })}
                placeholder="sk-..."
                required
              />

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_default"
                  checked={newKey.is_default}
                  onChange={(e) => setNewKey({ ...newKey, is_default: e.target.checked })}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <label htmlFor="is_default" className="text-sm text-gray-700">设为默认</label>
              </div>

              {error && (
                <div className="flex items-center gap-2 text-sm text-red-600">
                  <AlertCircle className="w-4 h-4" />
                  {error}
                </div>
              )}

              <div className="flex gap-2">
                <Button type="submit" isLoading={isLoading}>保存</Button>
                <Button type="button" variant="ghost" onClick={() => setShowAddForm(false)}>取消</Button>
              </div>
            </form>
          )}

          {/* API Key 列表 */}
          <div className="space-y-3">
            {apiKeys.length === 0 ? (
              <p className="text-gray-500 text-center py-8">还没有 API Key，请先添加</p>
            ) : (
              apiKeys.map((key) => (
                <div
                  key={key.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                      <Key className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{key.name}</p>
                      <p className="text-sm text-gray-500">
                        {PROVIDERS.find((p) => p.value === key.provider)?.label || key.provider}
                        {key.is_default && (
                          <span className="ml-2 inline-flex items-center px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded-full">
                            <Check className="w-3 h-3 mr-1" />默认
                          </span>
                        )}
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => handleDelete(key.id)}
                    className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
