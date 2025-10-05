import { create } from 'zustand'
import type { Rubric, EvaluationResult } from './types'

type AppState = {
  rubric: Rubric | null
  essayText: string
  result: EvaluationResult | null
  setRubric: (r: Rubric | null) => void
  setEssayText: (t: string) => void
  setResult: (r: EvaluationResult | null) => void
  reset: () => void
}

export const useApp = create<AppState>((set) => ({
  rubric: null,
  essayText: '',
  result: null,
  setRubric: (rubric) => set({ rubric }),
  setEssayText: (essayText) => set({ essayText }),
  setResult: (result) => set({ result }),
  reset: () => set({ rubric: null, essayText: '', result: null })
}))
