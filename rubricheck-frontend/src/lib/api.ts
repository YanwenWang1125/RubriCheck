import axios from 'axios'
import type { Rubric, EvaluationResult } from '../types'

const api = axios.create({
  baseURL: (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 1200000
})

export async function evaluateEssayWithFiles(rubricPath: string, essayPath: string, model: string = 'gpt-5-mini', fastMode: boolean = true) {
  const { data } = await api.post<EvaluationResult>('/evaluate', {
    rubricPath,
    essayPath,
    model,
    fastMode
  })
  return data
}

export async function evaluateEssay(rubric: Rubric, essayText: string, model: string = 'gpt-5-mini', fastMode: boolean = true) {
  const { data } = await api.post<EvaluationResult>('/evaluate', {
    rubric,
    essayText,
    model,
    fastMode
  })
  return data
}

export async function uploadRubricFile(file: File): Promise<{ success: boolean; file_path: string; filename: string; file_type: string }> {
  const formData = new FormData()
  formData.append('file', file)
  
  const { data } = await api.post<{ success: boolean; file_path: string; filename: string; file_type: string }>('/rubric/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return data
}

export async function parseRubricFile(file: File): Promise<Rubric> {
  const formData = new FormData()
  formData.append('file', file)
  
  const { data } = await api.post<Rubric>('/rubric/parse', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return data
}

export async function uploadEssayFile(file: File): Promise<{ success: boolean; file_path: string; filename: string; file_type: string }> {
  const formData = new FormData()
  formData.append('file', file)
  
  const { data } = await api.post<{ success: boolean; file_path: string; filename: string; file_type: string }>('/essay/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return data
}

export async function parseEssayFile(file: File): Promise<{ text: string; filename: string; file_type: string }> {
  const formData = new FormData()
  formData.append('file', file)
  
  const { data } = await api.post<{ success: boolean; text: string; filename: string; file_type: string }>('/essay/parse', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return data
}
