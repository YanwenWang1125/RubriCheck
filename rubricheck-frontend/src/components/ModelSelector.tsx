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
    name: 'GPT-5 Mini',
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
  const selectedModelData = AVAILABLE_MODELS.find(model => model.id === selectedModel)

  const getSpeedColor = (speed: string) => {
    switch (speed) {
      case 'fast': return 'text-green-600 bg-green-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'slow': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'high': return 'text-blue-600 bg-blue-100'
      case 'medium': return 'text-purple-600 bg-purple-100'
      case 'standard': return 'text-gray-600 bg-gray-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getCostColor = (cost: string) => {
    switch (cost) {
      case 'low': return 'text-green-600 bg-green-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'high': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-gray-700">
          AI Model
        </label>
        {selectedModelData?.recommended && (
          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
            Recommended
          </span>
        )}
      </div>
      
      <div className="grid grid-cols-1 gap-2">
        {AVAILABLE_MODELS.map((model) => (
          <div
            key={model.id}
            className={`relative p-3 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
              selectedModel === model.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
            onClick={() => !disabled && onModelChange(model.id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <input
                    type="radio"
                    name="model"
                    value={model.id}
                    checked={selectedModel === model.id}
                    onChange={() => !disabled && onModelChange(model.id)}
                    className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                    disabled={disabled}
                  />
                  <h4 className="font-medium text-gray-900">{model.name}</h4>
                  {model.recommended && (
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                      Recommended
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mb-2">{model.description}</p>
                
                <div className="flex gap-2">
                  <span className={`text-xs px-2 py-1 rounded-full ${getSpeedColor(model.speed)}`}>
                    {model.speed} speed
                  </span>
                  <span className={`text-xs px-2 py-1 rounded-full ${getQualityColor(model.quality)}`}>
                    {model.quality} quality
                  </span>
                  <span className={`text-xs px-2 py-1 rounded-full ${getCostColor(model.cost)}`}>
                    {model.cost} cost
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="text-xs text-gray-500 mt-2">
        💡 Tip: GPT-5 Mini is recommended for most essays. Use GPT-5 Nano for ultra-fast evaluations.
      </div>
    </div>
  )
}
