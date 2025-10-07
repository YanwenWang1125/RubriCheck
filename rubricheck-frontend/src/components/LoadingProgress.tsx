import React, { useState, useEffect } from 'react'

interface ProgressStep {
  id: string
  title: string
  description: string
  icon: string
  duration: number
}

interface LoadingProgressProps {
  isVisible: boolean
  onComplete?: () => void
}

const PROGRESS_STEPS: ProgressStep[] = [
  {
    id: 'preprocessing',
    title: 'Processing Essay',
    description: 'Analyzing structure, detecting language, and extracting metadata...',
    icon: '📝',
    duration: 2000
  },
  {
    id: 'rubric_conversion',
    title: 'Converting Rubric',
    description: 'Transforming rubric format for AI evaluation...',
    icon: '🔄',
    duration: 1000
  },
  {
    id: 'ai_grading',
    title: 'AI Evaluation',
    description: 'AI is analyzing your essay against each criterion...',
    icon: '🤖',
    duration: 12000
  },
  {
    id: 'finalizing',
    title: 'Finalizing Results',
    description: 'Converting result to frontend format...',
    icon: '✨',
    duration: 1000
  }
]

// Dynamic descriptions for AI grading step - based on backend logs
const AI_GRADING_DESCRIPTIONS = [
  'Evaluating criterion 1...',
  'Evaluating criterion 2...',
  'Evaluating criterion 3...',
  'Evaluating criterion 4...',
  'Evaluating criterion 5...',
  'Evaluating criterion 6...',
  'Running consistency checks...',
  'Finalizing scores...'
]

export default function LoadingProgress({ isVisible }: LoadingProgressProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)
  const [aiGradingDescription, setAiGradingDescription] = useState(0)

  useEffect(() => {
    if (!isVisible) {
      setCurrentStep(0)
      setProgress(0)
      setAiGradingDescription(0)
      return
    }

    const startTime = Date.now()
    let animationId: number
    
    // Update progress based on elapsed time - more realistic progression
    const updateProgress = () => {
      const elapsed = Date.now() - startTime
      
      // More realistic progress curve that starts fast and slows down
      let progressPercent = 0
      if (elapsed < 2000) {
        // First 2 seconds: 0-20%
        progressPercent = (elapsed / 2000) * 20
        setCurrentStep(0) // Processing Essay
      } else if (elapsed < 3000) {
        // Next 1 second: 20-30%
        progressPercent = 20 + ((elapsed - 2000) / 1000) * 10
        setCurrentStep(1) // Converting Rubric
      } else if (elapsed < 15000) {
        // Next 12 seconds: 30-80% (AI grading takes longest)
        progressPercent = 30 + ((elapsed - 3000) / 12000) * 50
        setCurrentStep(2) // AI Evaluation
      } else {
        // After 15 seconds: 80-95% (waiting for API)
        progressPercent = Math.min(80 + ((elapsed - 15000) / 10000) * 15, 95)
        setCurrentStep(3) // Finalizing
      }
      
      setProgress(progressPercent)
      
      // Continue animation
      animationId = requestAnimationFrame(updateProgress)
    }
    
    // Start progress updates
    animationId = requestAnimationFrame(updateProgress)
    
    // Handle AI grading descriptions
    const descriptionInterval = setInterval(() => {
      setAiGradingDescription(prev => (prev + 1) % AI_GRADING_DESCRIPTIONS.length)
    }, 2000) // Change description every 2 seconds
    
    return () => {
      clearInterval(descriptionInterval)
      if (animationId) {
        cancelAnimationFrame(animationId)
      }
    }
  }, [isVisible])

  if (!isVisible) return null

  return (
    <div className="mt-6 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
      {/* Header */}
      <div className="text-center mb-4">
        <div className="text-3xl mb-2">
          {PROGRESS_STEPS[currentStep]?.icon || '🚀'}
        </div>
        <h3 className="text-lg font-semibold text-gray-800">
          {PROGRESS_STEPS[currentStep]?.title || 'Processing...'}
        </h3>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Progress</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Current Step Description */}
      <div className="text-center mb-4">
        <p className="text-gray-600 text-sm leading-relaxed transition-all duration-500">
          {PROGRESS_STEPS[currentStep]?.id === 'ai_grading' 
            ? AI_GRADING_DESCRIPTIONS[aiGradingDescription]
            : PROGRESS_STEPS[currentStep]?.description || 'Please wait...'
          }
        </p>
      </div>

      {/* Step Indicators */}
      <div className="flex justify-center space-x-2 mb-3">
        {PROGRESS_STEPS.map((step, index) => (
          <div
            key={step.id}
            className={`w-2 h-2 rounded-full transition-all duration-300 ${
              index < currentStep
                ? 'bg-green-500'
                : index === currentStep
                ? 'bg-blue-500'
                : 'bg-gray-300'
            }`}
          />
        ))}
      </div>

      {/* Simple Loading Dots */}
      <div className="flex justify-center space-x-1">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"
            style={{
              animationDelay: `${i * 0.2}s`,
              animationDuration: '1.4s'
            }}
          />
        ))}
      </div>
    </div>
  )
}
