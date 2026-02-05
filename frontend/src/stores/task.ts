/**
 * 生成任务状态管理
 */

import { create } from 'zustand'
import type { GenerationTask, ExportTask } from '@/types'

interface TaskState {
  // 生成任务
  generationTasks: Map<string, GenerationTask>
  // 导出任务
  exportTasks: Map<string, ExportTask>
  
  // Actions
  setGenerationTask: (taskId: string, task: GenerationTask) => void
  setExportTask: (taskId: string, task: ExportTask) => void
  removeGenerationTask: (taskId: string) => void
  removeExportTask: (taskId: string) => void
}

export const useTaskStore = create<TaskState>()((set, get) => ({
  generationTasks: new Map(),
  exportTasks: new Map(),
  
  setGenerationTask: (taskId, task) => {
    const { generationTasks } = get()
    const newTasks = new Map(generationTasks)
    newTasks.set(taskId, task)
    set({ generationTasks: newTasks })
  },
  
  setExportTask: (taskId, task) => {
    const { exportTasks } = get()
    const newTasks = new Map(exportTasks)
    newTasks.set(taskId, task)
    set({ exportTasks: newTasks })
  },
  
  removeGenerationTask: (taskId) => {
    const { generationTasks } = get()
    const newTasks = new Map(generationTasks)
    newTasks.delete(taskId)
    set({ generationTasks: newTasks })
  },
  
  removeExportTask: (taskId) => {
    const { exportTasks } = get()
    const newTasks = new Map(exportTasks)
    newTasks.delete(taskId)
    set({ exportTasks: newTasks })
  },
}))

export default useTaskStore
