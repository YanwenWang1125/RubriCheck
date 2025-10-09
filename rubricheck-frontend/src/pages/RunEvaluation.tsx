import React, { useState } from 'react'
import { useApp } from '../store'
import { evaluateEssay, evaluateEssayWithFiles } from '../lib/api'
import LoadingProgress from '../components/LoadingProgress'
import ModelSelector from '../components/ModelSelector'

export default function RunEvaluation() {
  const { rubric, essayText, setResult, selectedModel, setSelectedModel, rubricFilePath, essayFilePath } = useApp()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fastMode, setFastMode] = useState(true)

  const run = async () => {
    if (!rubric) { setError('Please upload a rubric first.'); return }
    if (!essayText.trim()) { setError('Please paste an essay.'); return }
    
    // Check if we have file paths for the new approach
    if (rubricFilePath && essayFilePath) {
      setError(null)
      setLoading(true)
      try {
        const data = await evaluateEssayWithFiles(rubricFilePath, essayFilePath, selectedModel, fastMode)
        setResult(data)
        setLoading(false)
      } catch (e: any) {
        setError(e?.response?.data?.message || e?.message || 'Request failed.')
        setLoading(false)
      }
    } else {
      // Fallback to old approach if file paths not available
      setError(null)
      setLoading(true)
      try {
        const data = await evaluateEssay(rubric, essayText, selectedModel, fastMode)
        setResult(data)
        setLoading(false)
      } catch (e: any) {
        setError(e?.response?.data?.message || e?.message || 'Request failed.')
        setLoading(false)
      }
    }
  }

  return (
    <section className="card p-6">
      <h2 className="text-lg font-semibold mb-4">3) Evaluate</h2>
      
      {/* Model Selection */}
      <div className="mb-6">
        <ModelSelector 
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
          disabled={loading}
        />
      </div>
      
      {/* Fast Mode Toggle */}
      <div className="mb-6">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={fastMode}
            onChange={(e) => setFastMode(e.target.checked)}
            disabled={loading}
            className="rounded"
          />
          <span className="text-sm">
            <strong>Fast Mode</strong> 
            <span className="text-gray-600 ml-1">
              ({fastMode ? '~1-2 minutes' : '~4-6 minutes'})
            </span>
          </span>
        </label>
        <p className="text-xs text-gray-500 mt-1">
          {fastMode 
            ? 'Single API call per criterion for faster evaluation' 
            : 'Multiple API calls per criterion for higher accuracy and consistency checking'
          }
        </p>
      </div>
      
      <div className="flex items-center gap-3">
        <button className="btn btn-primary disabled:opacity-60" onClick={run} disabled={loading}>
          {loading ? 'Evaluating…' : 'Run Evaluation'}
        </button>
      </div>
      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      
      <LoadingProgress 
        isVisible={loading}
      />
    </section>
  )
}
