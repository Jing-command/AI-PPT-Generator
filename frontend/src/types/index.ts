/**
 * TypeScript 类型定义
 * 前后端数据接口对齐
 */

// 用户相关
export interface User {
  id: string
  email: string
  name: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name?: string
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

// API Key
export interface ApiKey {
  id: string
  name: string
  provider: string
  is_default: boolean
  status: string
  created_at: string
}

export interface CreateApiKeyRequest {
  name: string
  api_key: string
  provider: string
  is_default?: boolean
}

// PPT
export interface Presentation {
  id: string
  user_id: string
  title: string
  slides: Slide[]
  status: 'draft' | 'published' | 'archived'
  version: number
  created_at: string
  updated_at: string
}

export interface Slide {
  id: string
  type: 'title' | 'content' | 'split' | 'image' | 'chart'
  content: SlideContent
  layout?: SlideLayout
  style?: SlideStyle
  notes?: string
}

export interface SlideContent {
  title?: string
  subtitle?: string
  text?: string
  bullets?: string[]
  image_url?: string
  chart_data?: Record<string, unknown>
}

export interface SlideLayout {
  type: string
  background?: string
  theme?: string
}

export interface SlideStyle {
  font_family?: string
  font_size?: number
  color?: string
  alignment?: string
}

export interface CreatePresentationRequest {
  title: string
  template_id?: string
}

export interface UpdatePresentationRequest {
  title?: string
  slides?: Slide[]
  status?: 'draft' | 'published' | 'archived'
}

// AI 生成
export interface GenerateRequest {
  prompt: string
  template_id?: string
  num_slides?: number
  language?: 'zh' | 'en'
  style?: string
  provider?: string
}

export interface GenerationTask {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  progress: number
  estimated_time: number
  message: string
}

// 导出
export interface ExportRequest {
  format: 'pptx' | 'pdf' | 'png' | 'jpg'
  quality?: 'standard' | 'high'
  slide_range?: string
}

export interface ExportTask {
  export_task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  download_url?: string
  expires_at?: string
}

// 模板
export interface Template {
  id: string
  name: string
  description?: string
  category: string
  thumbnail_url?: string
  usage_count: number
  is_premium: boolean
}

export interface TemplateCategory {
  id: string
  name: string
  icon: string
}

// 操作历史
export interface OperationHistory {
  id: string
  operation_type: string
  description: string
  slide_id?: string
  before_state?: Record<string, unknown>
  after_state?: Record<string, unknown>
  created_at: string
}

// API 响应
export interface ApiResponse<T> {
  code: string
  message: string
  data?: T
  details?: Record<string, unknown>
}
