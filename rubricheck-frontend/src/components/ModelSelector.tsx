import React from 'react'

export interface AIModel {
  id: string
  name: string
  description: string
  speed: 'fast' | 'medium' | 'slow'
  quality: 'high' | 'medium' | 'standard'
  cost: 'low' | 'medium' | 'high'
  recommended?: boolean
}

export const AVAILABLE_MODELS: AIModel[] = [
  {
    id: 'gpt-5-mini',
    name: 'GPT-5 Mini (Recommended)',
    description: 'Latest generation model with enhanced reasoning capabilities',
    speed: 'fast',
    quality: 'high',
    cost: 'low',
    recommended: true
  },
  {
    id: 'gpt-5-nano',
    name: 'GPT-5 Nano',
    description: 'Ultra-fast and efficient for quick evaluations',
    speed: 'fast',
    quality: 'high',
    cost: 'low'
  },
  {
    id: 'gpt-4.1-mini',
    name: 'GPT-4.1 Mini',
    description: 'Improved version with better accuracy and speed',
    speed: 'fast',
    quality: 'high',
    cost: 'low'
  }
]

interface ModelSelectorProps {
  selectedModel: string
  onModelChange: (modelId: string) => void
  disabled?: boolean
}

export default function ModelSelector({ selectedModel, onModelChange, disabled = false }: ModelSelectorProps) {
  return (
    <div>
      <label htmlFor="ai-model-select" className="block text-sm font-medium text-gray-700 mb-1">
        AI Model
      </label>
      <select
        id="ai-model-select"
        className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        value={selectedModel}
        onChange={(e) => onModelChange(e.target.value)}
        disabled={disabled}
      >
        {AVAILABLE_MODELS.map((model) => (
          <option key={model.id} value={model.id}>
            {model.name}
          </option>
        ))}
      </select>
    </div>
  )
}
