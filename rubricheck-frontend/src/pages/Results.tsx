import React from 'react'
import { useApp } from '../store'

export default function Results() {
  const { result } = useApp()

  return (
    <section id="results" className="card p-6">
      <h2 className="text-lg font-semibold mb-4">4) Results</h2>
      {!result && (
        <p className="text-gray-600 text-sm">Run an evaluation to see per-criterion scores, evidence spans, and suggestions.</p>
      )}
      {result && (
        <div className="space-y-4">
          <div className="card p-4">
            <div className="text-sm text-gray-600">Overall</div>
            <div className="text-2xl font-semibold">
              {typeof result.overall.numeric === 'number' ? 
                (result.overall.numeric > 1 ? `${result.overall.numeric.toFixed(1)}%` : `${(result.overall.numeric * 100).toFixed(1)}%`) 
                : '--'}
            </div>
            <div className="text-sm text-gray-600">
              {result.overall.letter ? `Letter: ${result.overall.letter}` : ''}
              {typeof result.overall.confidence === 'number' ? ` · Confidence: ${(result.overall.confidence*100).toFixed(0)}%` : ''}
            </div>
          </div>

          <div className="space-y-3">
            {result.items.map((it, idx) => (
              <div key={idx} className="card p-4">
                <div className="flex items-center justify-between">
                  <div className="font-medium">Criterion: {it.criterionId}</div>
                  <div className="text-primary-700 text-sm font-semibold">{it.level}</div>
                </div>
                <div className="mt-2 text-sm">
                  <div className="text-gray-700 whitespace-pre-wrap"><span className="font-medium">Justification: </span>{it.justification}</div>
                  {it.suggestion && <div className="mt-1 text-gray-700"><span className="font-medium">Suggestion: </span>{it.suggestion}</div>}
                  {!!it.evidenceSpans?.length && (
                    <ul className="mt-2 text-gray-600 list-disc pl-5">
                      {it.evidenceSpans
                        .filter(ev => ev.text && ev.text.trim().length > 0)
                        .map((ev, i) => <li key={i} className="text-xs">"{ev.text}" {typeof ev.paraIndex==='number' ? `(para ${ev.paraIndex})` : ''}</li>)}
                    </ul>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}
