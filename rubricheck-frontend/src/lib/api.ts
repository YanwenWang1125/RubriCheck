import axios from 'axios'
import type { Rubric, EvaluationResult } from '../types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 120000
})

export async function evaluateEssay(rubric: Rubric, essayText: string) {
  const { data } = await api.post<EvaluationResult>('/evaluate', {
    rubric,
    essayText
  })
  return data
}
