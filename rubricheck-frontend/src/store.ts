import { create } from 'zustand'
import type { Rubric, EvaluationResult } from './types'

type AppState = {
  rubric: Rubric | null
  essayText: string
  result: EvaluationResult | null
  selectedModel: string
  setRubric: (r: Rubric | null) => void
  setEssayText: (t: string) => void
  setResult: (r: EvaluationResult | null) => void
  setSelectedModel: (model: string) => void
  reset: () => void
}

export const useApp = create<AppState>((set) => ({
  rubric: null,
  essayText: '',
  result: null,
  selectedModel: 'gpt-5-mini', // Default to recommended model
  setRubric: (rubric) => set({ rubric }),
  setEssayText: (essayText) => set({ essayText }),
  setResult: (result) => set({ result }),
  setSelectedModel: (selectedModel) => set({ selectedModel }),
  reset: () => set({ rubric: null, essayText: '', result: null, selectedModel: 'gpt-5-mini' })
}))
