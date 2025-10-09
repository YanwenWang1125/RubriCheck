import { create } from 'zustand'
import type { Rubric, EvaluationResult } from './types'

type AppState = {
  rubric: Rubric | null
  essayText: string
  result: EvaluationResult | null
  selectedModel: string
  rubricFilePath: string | null
  essayFilePath: string | null
  setRubric: (r: Rubric | null) => void
  setEssayText: (t: string) => void
  setResult: (r: EvaluationResult | null) => void
  setSelectedModel: (model: string) => void
  setRubricFilePath: (path: string | null) => void
  setEssayFilePath: (path: string | null) => void
  reset: () => void
}

export const useApp = create<AppState>((set) => ({
  rubric: null,
  essayText: '',
  result: null,
  selectedModel: 'gpt-5-mini', // Default to recommended model
  rubricFilePath: null,
  essayFilePath: null,
  setRubric: (rubric) => set({ rubric }),
  setEssayText: (essayText) => set({ essayText }),
  setResult: (result) => set({ result }),
  setSelectedModel: (selectedModel) => set({ selectedModel }),
  setRubricFilePath: (rubricFilePath) => set({ rubricFilePath }),
  setEssayFilePath: (essayFilePath) => set({ essayFilePath }),
  reset: () => set({ rubric: null, essayText: '', result: null, selectedModel: 'gpt-5-mini', rubricFilePath: null, essayFilePath: null })
}))
