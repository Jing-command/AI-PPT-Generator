/**
 * API 服务统一导出
 */

import apiClient from './api'
import type { ApiResponse, Presentation, Slide, Template, TemplateCategory, ApiKey, ExportTask, GenerationTask } from '@/types'

export { default as apiClient } from './api'
export { default as authService } from './auth'

// PPT 服务
export const pptService = {
  async getPresentations(params?: { skip?: number; limit?: number; status?: string }): Promise<{ presentations: Presentation[]; total: number }> {
    const response = await apiClient.get<ApiResponse<{ presentations: Presentation[]; total: number }>>('/ppt', { params })
    return response.data.data!
  },

  async getPresentation(id: string): Promise<Presentation> {
    const response = await apiClient.get<ApiResponse<Presentation>>(`/ppt/${id}`)
    return response.data.data!
  },

  async createPresentation(data: { title: string; template_id?: string }): Promise<Presentation> {
    const response = await apiClient.post<ApiResponse<Presentation> | Presentation>('/ppt', data)
    const payload = response.data
    const pptData = 'id' in payload ? payload : payload.data
    if (!pptData) {
      throw new Error('创建 PPT 返回缺少数据')
    }
    return pptData
  },

  async updatePresentation(id: string, data: Partial<{ title: string; slides: Slide[]; status: string }>): Promise<Presentation> {
    const response = await apiClient.patch<ApiResponse<Presentation>>(`/ppt/${id}`, data)
    return response.data.data!
  },

  async deletePresentation(id: string): Promise<void> {
    await apiClient.delete<ApiResponse<void>>(`/ppt/${id}`)
  },

  // 幻灯片操作
  async getSlide(pptId: string, slideId: string): Promise<Slide> {
    const response = await apiClient.get<ApiResponse<Slide>>(`/ppt/${pptId}/slides/${slideId}`)
    return response.data.data!
  },

  async updateSlide(pptId: string, slideId: string, slideData: Partial<Slide>): Promise<Slide> {
    const response = await apiClient.patch<ApiResponse<Slide>>(`/ppt/${pptId}/slides/${slideId}`, slideData)
    return response.data.data!
  },

  async addSlide(pptId: string, slideData: Slide): Promise<Slide> {
    const response = await apiClient.post<ApiResponse<Slide>>(`/ppt/${pptId}/slides`, slideData)
    return response.data.data!
  },

  async deleteSlide(pptId: string, slideId: string): Promise<void> {
    await apiClient.delete<ApiResponse<void>>(`/ppt/${pptId}/slides/${slideId}`)
  },

  // 撤销/重做
  async undo(pptId: string): Promise<{ state: { slides: Slide[] } }> {
    const response = await apiClient.post<ApiResponse<{ state: { slides: Slide[] } }>>(`/ppt/${pptId}/undo`)
    return response.data.data!
  },

  async redo(pptId: string): Promise<{ state: { slides: Slide[] } }> {
    const response = await apiClient.post<ApiResponse<{ state: { slides: Slide[] } }>>(`/ppt/${pptId}/redo`)
    return response.data.data!
  },

  async getHistory(pptId: string, limit?: number): Promise<unknown[]> {
    const response = await apiClient.get<ApiResponse<unknown[]>>(`/ppt/${pptId}/history`, { params: { limit } })
    return response.data.data || []
  },
}

// AI 生成服务
export const generationService = {
  async generate(data: { prompt: string; num_slides?: number; language?: string; style?: string }): Promise<{ task_id: string }> {
    const response = await apiClient.post<ApiResponse<{ task_id: string }>>('/ppt/generate', data)
    return response.data.data!
  },

  async getStatus(taskId: string): Promise<GenerationTask> {
    const response = await apiClient.get<ApiResponse<GenerationTask>>(`/ppt/generate/${taskId}/status`)
    return response.data.data!
  },

  async cancel(taskId: string): Promise<void> {
    await apiClient.post<ApiResponse<void>>(`/ppt/generate/${taskId}/cancel`)
  },
}

// 导出服务
export const exportService = {
  async export(pptId: string, format: 'pptx' | 'pdf' | 'png' | 'jpg'): Promise<{ export_task_id: string }> {
    const response = await apiClient.post<ApiResponse<{ export_task_id: string }>>(`/ppt/${pptId}/export`, { format })
    return response.data.data!
  },

  async getStatus(pptId: string, taskId: string): Promise<ExportTask> {
    const response = await apiClient.get<ApiResponse<ExportTask>>(`/ppt/${pptId}/export/${taskId}/status`)
    return response.data.data!
  },
}

// 模板服务
export const templateService = {
  async getTemplates(params?: { category?: string; is_premium?: boolean }): Promise<{ templates: Template[]; total: number }> {
    const response = await apiClient.get<ApiResponse<{ templates: Template[]; total: number }>>('/templates', { params })
    return response.data.data!
  },

  async getTemplate(id: string): Promise<Template> {
    const response = await apiClient.get<ApiResponse<Template>>(`/templates/${id}`)
    return response.data.data!
  },

  async getCategories(): Promise<TemplateCategory[]> {
    const response = await apiClient.get<ApiResponse<TemplateCategory[]>>('/templates/categories')
    return response.data.data || []
  },

  async useTemplate(id: string): Promise<void> {
    await apiClient.post<ApiResponse<void>>(`/templates/${id}/use`)
  },
}

// API Key 服务
export const apiKeyService = {
  async getApiKeys(): Promise<ApiKey[]> {
    const response = await apiClient.get<ApiResponse<ApiKey[]>>('/api-keys')
    return response.data.data || []
  },

  async createApiKey(data: { name: string; api_key: string; provider: string; is_default?: boolean }): Promise<ApiKey> {
    const response = await apiClient.post<ApiResponse<ApiKey>>('/api-keys', data)
    return response.data.data!
  },

  async updateApiKey(id: string, data: Partial<{ name: string; is_default: boolean }>): Promise<ApiKey> {
    const response = await apiClient.patch<ApiResponse<ApiKey>>(`/api-keys/${id}`, data)
    return response.data.data!
  },

  async deleteApiKey(id: string): Promise<void> {
    await apiClient.delete<ApiResponse<void>>(`/api-keys/${id}`)
  },

  async verify(id: string): Promise<{ valid: boolean; message?: string }> {
    const response = await apiClient.post<ApiResponse<{ valid: boolean; message?: string }>>(`/api-keys/${id}/verify`)
    return response.data.data!
  },
}
