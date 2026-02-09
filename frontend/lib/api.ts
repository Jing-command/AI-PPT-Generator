// API 配置
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// 获取 Token
function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token');
  }
  return null;
}

// 通用请求函数
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers as Record<string, string>,
  };
  
  // 添加认证头
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: '请求失败' }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }
  
  return response.json();
}

// ==================== 认证 API ====================
export const authAPI = {
  // 注册
  register: (data: { email: string; password: string; username?: string }) =>
    fetchAPI('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 登录
  login: (data: { email: string; password: string }) =>
    fetchAPI<{ access_token: string; refresh_token: string; token_type: string; expires_in: number }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 刷新 Token
  refresh: (refresh_token: string) =>
    fetchAPI<{ access_token: string; refresh_token: string; token_type: string; expires_in: number }>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token }),
    }),
  
  // 获取当前用户
  getCurrentUser: () =>
    fetchAPI('/users/me'),
};

// ==================== PPT API ====================
export const pptAPI = {
  // 创建 PPT
  create: (data: { title: string; description?: string; template_id?: string }) =>
    fetchAPI('/ppt', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 获取 PPT 列表
  list: (params?: { skip?: number; limit?: number; status?: string }) => {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return fetchAPI(`/ppt?${query}`);
  },
  
  // 获取 PPT 详情
  getById: (ppt_id: string) =>
    fetchAPI(`/ppt/${ppt_id}`),
  
  // 更新 PPT
  update: (ppt_id: string, data: Partial<{ title: string; description: string; status: string }>) =>
    fetchAPI(`/ppt/${ppt_id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  
  // 删除 PPT
  delete: (ppt_id: string) =>
    fetchAPI(`/ppt/${ppt_id}`, {
      method: 'DELETE',
    }),
  
  // 获取单页幻灯片
  getSlide: (ppt_id: string, slide_id: string) =>
    fetchAPI(`/ppt/${ppt_id}/slides/${slide_id}`),
  
  // 更新单页幻灯片
  updateSlide: (ppt_id: string, slide_id: string, data: Partial<{ title: string; content: any; layout: string; notes: string }>) =>
    fetchAPI(`/ppt/${ppt_id}/slides/${slide_id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  
  // 添加幻灯片
  addSlide: (ppt_id: string, data: { title?: string; content?: any; layout?: string; position?: number }) =>
    fetchAPI(`/ppt/${ppt_id}/slides`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 删除幻灯片
  deleteSlide: (ppt_id: string, slide_id: string) =>
    fetchAPI(`/ppt/${ppt_id}/slides/${slide_id}`, {
      method: 'DELETE',
    }),
  
  // 撤销操作
  undo: (ppt_id: string) =>
    fetchAPI(`/ppt/${ppt_id}/undo`, {
      method: 'POST',
    }),
  
  // 重做操作
  redo: (ppt_id: string) =>
    fetchAPI(`/ppt/${ppt_id}/redo`, {
      method: 'POST',
    }),
  
  // 获取操作历史
  getHistory: (ppt_id: string, limit?: number) =>
    fetchAPI(`/ppt/${ppt_id}/history?limit=${limit || 50}`),
};

// ==================== AI 生成 API ====================
export const generationAPI = {
  // 提交生成任务
  generate: (data: { 
    title: string; 
    description?: string; 
    template_id?: string; 
    slides_count?: number;
    content_outline?: string[];
  }) =>
    fetchAPI<{ task_id: string; status: string; estimated_time: number; message: string }>('/ppt/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 查询生成状态
  getStatus: (task_id: string) =>
    fetchAPI(`/ppt/generate/${task_id}/status`),
  
  // 取消生成任务
  cancel: (task_id: string) =>
    fetchAPI(`/ppt/generate/${task_id}/cancel`, {
      method: 'POST',
    }),
};

// ==================== 导出 API ====================
export const exportAPI = {
  // 提交导出任务
  export: (ppt_id: string, data: { format: 'pptx' | 'pdf' | 'png' | 'jpg'; quality?: 'high' | 'medium' | 'low' }) =>
    fetchAPI<{ export_task_id: string; status: string; download_url: string | null; expires_at: string | null }>(`/ppt/${ppt_id}/export`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 查询导出状态
  getStatus: (ppt_id: string, task_id: string) =>
    fetchAPI(`/ppt/${ppt_id}/export/${task_id}/status`),
};

// ==================== 模板 API ====================
export const templateAPI = {
  // 获取模板列表
  list: (params?: { category?: string; is_premium?: boolean; limit?: number }) => {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return fetchAPI<{ templates: any[]; total: number }>(`/templates?${query}`);
  },
  
  // 获取模板分类
  getCategories: () =>
    fetchAPI<Array<{ id: string; name: string; icon: string }>>('/templates/categories'),
  
  // 获取模板详情
  getById: (template_id: string) =>
    fetchAPI(`/templates/${template_id}`),
  
  // 使用模板
  use: (template_id: string) =>
    fetchAPI(`/templates/${template_id}/use`, {
      method: 'POST',
    }),
};

// ==================== API Key API ====================
export const apiKeyAPI = {
  // 获取 API Key 列表
  list: () =>
    fetchAPI<Array<any>>('/api-keys'),
  
  // 创建 API Key
  create: (data: { name: string; provider: string; api_key: string }) =>
    fetchAPI('/api-keys', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 获取 API Key 详情
  getById: (key_id: string) =>
    fetchAPI(`/api-keys/${key_id}`),
  
  // 更新 API Key
  update: (key_id: string, data: Partial<{ name: string; is_active: boolean; is_default: boolean }>) =>
    fetchAPI(`/api-keys/${key_id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  
  // 删除 API Key
  delete: (key_id: string) =>
    fetchAPI(`/api-keys/${key_id}`, {
      method: 'DELETE',
    }),
  
  // 验证 API Key
  verify: (key_id: string) =>
    fetchAPI<{ valid: boolean; provider: string; message: string }>(`/api-keys/${key_id}/verify`, {
      method: 'POST',
    }),
};

export default {
  auth: authAPI,
  ppt: pptAPI,
  generation: generationAPI,
  export: exportAPI,
  template: templateAPI,
  apiKey: apiKeyAPI,
};
