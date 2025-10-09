import React, { useState } from 'react'
import { useApp } from '../store'
import HighlightedEssay from '../components/HighlightedEssay'

export default function Results() {
  const { result, essayText } = useApp()
  const [selectedCriterion, setSelectedCriterion] = useState<number | null>(null)
  const [showAllEvidence, setShowAllEvidence] = useState(true)
  const [showEssayHighlighting, setShowEssayHighlighting] = useState(true)
  const [expandedCriteria, setExpandedCriteria] = useState<Set<number>>(new Set())

  // Helper functions
  const toggleCriterionExpansion = (index: number) => {
    const newExpanded = new Set(expandedCriteria)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedCriteria(newExpanded)
  }

  const getCriterionColor = (index: number) => {
    const colors = [
      'bg-blue-100 border-blue-300 text-blue-800',
      'bg-green-100 border-green-300 text-green-800', 
      'bg-purple-100 border-purple-300 text-purple-800',
      'bg-orange-100 border-orange-300 text-orange-800',
      'bg-pink-100 border-pink-300 text-pink-800',
      'bg-indigo-100 border-indigo-300 text-indigo-800'
    ]
    return colors[index % colors.length]
  }

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
        <h2 className="text-lg font-semibold">4) Interactive Results</h2>
        <div className="flex items-center gap-4">
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
          <button
            onClick={() => setExpandedCriteria(new Set(result.items.map((_, i) => i)))}
            className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded"
          >
            Expand All
          </button>
          <button
            onClick={() => setExpandedCriteria(new Set())}
            className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded"
          >
            Collapse All
          </button>
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
          />
        </div>
      )}

      {/* Interactive Criteria List */}
      <div className="space-y-3">
        {result.items.map((it, idx) => {
          const isExpanded = expandedCriteria.has(idx)
          const isSelected = selectedCriterion === idx
          
          return (
            <div 
              key={idx} 
              className={`card p-4 border-2 transition-all duration-200 cursor-pointer ${
                isSelected ? 'border-blue-400 shadow-lg' : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedCriterion(isSelected ? null : idx)}
            >
              {/* Criterion Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${getCriterionColor(idx)}`}>
                    {idx + 1}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">
                      {it.criterionId?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || `Criterion ${idx + 1}`}
                    </div>
                    <div className="text-xs text-gray-500">
                      Click to {isExpanded ? 'collapse' : 'expand'} details
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${getLevelColor(it.level || '')}`}>
                    {it.level || 'N/A'}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleCriterionExpansion(idx)
                    }}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {isExpanded ? '▼' : '▶'}
                  </button>
                </div>
              </div>

              {/* Expanded Content */}
              {isExpanded && (
                <div className="mt-4 space-y-4 border-t pt-4">
                  {/* Justification */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                      📝 Justification
                    </h4>
                    <div className="text-gray-700 bg-gray-50 p-3 rounded-lg">
                      {it.justification || 'No justification provided'}
                    </div>
                  </div>

                  {/* Evidence Spans */}
                  {it.evidenceSpans && Array.isArray(it.evidenceSpans) && it.evidenceSpans.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                        🔍 Evidence ({it.evidenceSpans.length} spans)
                      </h4>
                      <div className="space-y-2">
                        {it.evidenceSpans
                          .filter(ev => ev && ev.text && ev.text.trim().length > 0)
                          .map((ev, i) => (
                            <div key={i} className="bg-blue-50 border border-blue-200 p-3 rounded-lg">
                              <div className="text-sm text-gray-700 mb-1">
                                <span className="font-medium">Quote:</span> "{ev.text}"
                              </div>
                              {typeof ev.paraIndex === 'number' && (
                                <div className="text-xs text-blue-600">
                                  📍 Paragraph {ev.paraIndex}
                                </div>
                              )}
                            </div>
                          ))}
                      </div>
                    </div>
                  )}

                  {/* Suggestion */}
                  {it.suggestion && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                        💡 Improvement Suggestion
                      </h4>
                      <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-lg">
                        <div className="text-gray-700">{it.suggestion}</div>
                      </div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-2 pt-2">
                    <button className="text-xs px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded">
                      Regrade This Criterion
                    </button>
                    <button className="text-xs px-3 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded">
                      Add Teacher Note
                    </button>
                    <button className="text-xs px-3 py-1 bg-purple-100 hover:bg-purple-200 text-purple-700 rounded">
                      Export Details
                    </button>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

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
