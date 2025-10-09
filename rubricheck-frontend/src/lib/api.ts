import axios from 'axios'
import type { Rubric, EvaluationResult } from '../types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 1200000
})

export async function evaluateEssay(rubric: Rubric, essayText: string, model: string = 'gpt-5-mini') {
  const { data } = await api.post<EvaluationResult>('/evaluate', {
    rubric,
    essayText,
    model
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