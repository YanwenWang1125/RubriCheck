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
    duration: 1500
  },
  {
    id: 'ai_grading',
    title: 'AI Evaluation',
    description: 'AI is analyzing your essay against each criterion...',
    icon: '🤖',
    duration: 80000
  },
  {
    id: 'evidence_extraction',
    title: 'Extracting Evidence',
    description: 'Finding supporting quotes and evidence spans...',
    icon: '🔍',
    duration: 20000
  },
  {
    id: 'finalizing',
    title: 'Finalizing Results',
    description: 'Compiling scores and generating feedback...',
    icon: '✨',
    duration: 15000
  }
]

// Dynamic descriptions for AI grading step
const AI_GRADING_DESCRIPTIONS = [
  'Evaluating clarity and organization...',
  'Analyzing grammar and mechanics...',
  'Assessing evidence and support...',
  'Reviewing critical thinking...',
  'Checking argument structure...',
  'Finalizing criterion scores...'
]

export default function LoadingProgress({ isVisible, onComplete }: LoadingProgressProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)
  const [isAnimating, setIsAnimating] = useState(false)
  const [aiGradingDescription, setAiGradingDescription] = useState(0)

  useEffect(() => {
    if (!isVisible) {
      setCurrentStep(0)
      setProgress(0)
      setIsAnimating(false)
      setAiGradingDescription(0)
      return
    }

    setIsAnimating(true)
    let stepIndex = 0
    let aiDescriptionIndex = 0

    const runSteps = () => {
      if (stepIndex >= PROGRESS_STEPS.length) {
        setProgress(100)
        setTimeout(() => {
          setIsAnimating(false)
          onComplete?.()
        }, 500)
        return
      }

      const step = PROGRESS_STEPS[stepIndex]
      setCurrentStep(stepIndex)
      
      // Special handling for AI grading step
      if (step.id === 'ai_grading') {
        const descriptionInterval = setInterval(() => {
          setAiGradingDescription(prev => (prev + 1) % AI_GRADING_DESCRIPTIONS.length)
        }, step.duration / AI_GRADING_DESCRIPTIONS.length)
        
        setTimeout(() => {
          clearInterval(descriptionInterval)
        }, step.duration)
      }
      
      // Animate progress for this step
      const stepProgress = (stepIndex + 1) / PROGRESS_STEPS.length * 100
      const startProgress = (stepIndex / PROGRESS_STEPS.length) * 100
      
      // Smooth progress animation
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          const increment = (stepProgress - startProgress) / (step.duration / 50)
          const newProgress = Math.min(prev + increment, stepProgress)
          if (newProgress >= stepProgress) {
            clearInterval(progressInterval)
          }
          return newProgress
        })
      }, 50)

      setTimeout(() => {
        stepIndex++
        runSteps()
      }, step.duration)
    }

    runSteps()
  }, [isVisible, onComplete])

  if (!isVisible) return null

  return (
    <div className="mt-6 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
      {/* Header */}
      <div className="text-center mb-4">
        <div className="text-3xl mb-2 animate-float">
          {PROGRESS_STEPS[currentStep]?.icon || '🚀'}
        </div>
        <h3 className="text-lg font-semibold text-gray-800 animate-pulse-glow">
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
            className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-300 ease-out relative"
            style={{ width: `${progress}%` }}
          >
            {/* Enhanced shimmer effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-40 animate-shimmer"></div>
          </div>
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
                ? 'bg-green-500 scale-110'
                : index === currentStep
                ? 'bg-blue-500 scale-125 animate-pulse'
                : 'bg-gray-300'
            }`}
          />
        ))}
      </div>

      {/* Animated Dots */}
      <div className="flex justify-center space-x-1">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"
            style={{
              animationDelay: `${i * 0.1}s`,
              animationDuration: '1s'
            }}
          />
        ))}
      </div>
    </div>
  )
}
