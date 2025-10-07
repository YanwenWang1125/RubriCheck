import React, { useState } from 'react'
import { useApp } from '../store'
import { evaluateEssay } from '../lib/api'

export default function RunEvaluation() {
  const { rubric, essayText, setResult } = useApp()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const run = async () => {
    if (!rubric) { setError('Please upload a rubric first.'); return }
    if (!essayText.trim()) { setError('Please paste an essay.'); return }
    setError(null)
    setLoading(true)
    try {
      const data = await evaluateEssay(rubric, essayText)
      setResult(data)
    } catch (e: any) {
      setError(e?.response?.data?.message || e?.message || 'Request failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="card p-6">
      <h2 className="text-lg font-semibold mb-2">3) Evaluate</h2>
      <div className="flex items-center gap-3">
        <button className="btn btn-primary disabled:opacity-60" onClick={run} disabled={loading}>
          {loading ? 'Evaluating…' : 'Run Evaluation'}
        </button>
      </div>
      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
    </section>
  )
}
