import React, { useState } from 'react'
import { useApp } from '../store'
import HighlightedEssay from '../components/HighlightedEssay'

interface ResultsProps {
  onViewChange: (view: 'main' | 'student-results') => void
}

export default function Results({ onViewChange }: ResultsProps) {
  const { result, essayText } = useApp()
  const [selectedCriterion, setSelectedCriterion] = useState<number | null>(null)
  const [showAllEvidence, setShowAllEvidence] = useState(true)
  const [showEssayHighlighting, setShowEssayHighlighting] = useState(true)

  // Helper functions

  const getLevelColor = (level: string) => {
    const levelColors: { [key: string]: string } = {
      'Excellent': 'bg-green-100 text-green-800 border-green-300',
      'Good': 'bg-blue-100 text-blue-800 border-blue-300',
      'Fair': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'Poor': 'bg-red-100 text-red-800 border-red-300',
      'A+': 'bg-green-100 text-green-800 border-green-300',
      'A': 'bg-green-100 text-green-800 border-green-300',
      'B': 'bg-blue-100 text-blue-800 border-blue-300',
      'C': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'D': 'bg-red-100 text-red-800 border-red-300'
    }
    return levelColors[level] || 'bg-gray-100 text-gray-800 border-gray-300'
  }

  // Add error boundary and null checks
  if (!result) {
    return (
      <section id="results" className="card p-6">
        <h2 className="text-lg font-semibold mb-4">4) Results</h2>
        <p className="text-gray-600 text-sm">Run an evaluation to see per-criterion scores, evidence spans, and suggestions.</p>
      </section>
    )
  }

  // Validate result structure
  if (!result.overall || !result.items || !Array.isArray(result.items)) {
    return (
      <section id="results" className="card p-6">
        <h2 className="text-lg font-semibold mb-4">4) Results</h2>
        <div className="text-red-600 bg-red-50 p-3 rounded">
          ❌ Error: Invalid result format received from backend
        </div>
        <details className="mt-2">
          <summary className="cursor-pointer text-sm text-gray-600">Debug Info</summary>
          <pre className="text-xs bg-gray-100 p-2 mt-1 rounded overflow-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        </details>
      </section>
    )
  }

  return (
    <section id="results" className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold">Results</h2>
        <div className="flex items-center gap-4">
          <button
            onClick={() => onViewChange('student-results')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            Student View
          </button>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showEssayHighlighting}
              onChange={(e) => setShowEssayHighlighting(e.target.checked)}
              className="rounded"
            />
            Show essay highlighting
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showAllEvidence}
              onChange={(e) => setShowAllEvidence(e.target.checked)}
              className="rounded"
            />
            Show all evidence
          </label>
        </div>
      </div>

      {/* Overall Score Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="card p-4 text-center">
          <div className="text-sm text-gray-600 mb-1">Overall Score</div>
          <div className="text-3xl font-bold text-blue-600">
            {typeof result.overall?.numeric === 'number' ? 
              (result.overall.numeric > 1 ? `${result.overall.numeric.toFixed(1)}%` : `${(result.overall.numeric * 100).toFixed(1)}%`) 
              : '--'}
          </div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-sm text-gray-600 mb-1">Letter Grade</div>
          <div className={`text-3xl font-bold px-3 py-1 rounded-full inline-block ${getLevelColor(result.overall?.letter || '')}`}>
            {result.overall?.letter || '--'}
          </div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-sm text-gray-600 mb-1">Confidence</div>
          <div className="text-3xl font-bold text-green-600">
            {typeof result.overall?.confidence === 'number' ? `${(result.overall.confidence*100).toFixed(0)}%` : '--'}
          </div>
        </div>
      </div>

      {/* Essay Highlighting Section */}
      {essayText && showEssayHighlighting && (
        <div className="mb-6">
          <HighlightedEssay 
            essayText={essayText}
            result={result}
            selectedCriterion={selectedCriterion}
            showAllEvidence={showAllEvidence}
            onHighlightClick={(criterionId) => {
              console.log('🔍 Navigating to Student View for criterion:', criterionId)
              // Add criterion ID to URL for Student View to pick up
              const currentUrl = new URL(window.location.href)
              currentUrl.searchParams.set('criterion', criterionId)
              window.history.pushState({}, '', currentUrl.toString())
              onViewChange('student-results')
            }}
          />
        </div>
      )}


      {/* Summary Actions */}
      <div className="mt-6 pt-4 border-t flex justify-between items-center">
        <div className="text-sm text-gray-600">
          {result.items.length} criteria evaluated • 
          {result.items.filter(item => item.level === 'Excellent' || item.level === 'A' || item.level === 'A+').length} excellent • 
          {result.items.filter(item => item.level === 'Poor' || item.level === 'D').length} needs improvement
        </div>
        <div className="flex gap-2">
          <button className="text-sm px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded">
            Export Full Report
          </button>
          <button className="text-sm px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded">
            Save Session
          </button>
        </div>
      </div>
    </section>
  )
}
