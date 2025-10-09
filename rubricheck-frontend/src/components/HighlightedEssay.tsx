import React, { useState } from 'react'
import type { EvaluationResult } from '../types'

interface HighlightedEssayProps {
  essayText: string
  result: EvaluationResult
  selectedCriterion?: number | null
  showAllEvidence?: boolean
}

export default function HighlightedEssay({ 
  essayText, 
  result, 
  selectedCriterion = null, 
  showAllEvidence = true 
}: HighlightedEssayProps) {
  const [hoveredEvidence, setHoveredEvidence] = useState<{criterionIndex: number, evidenceIndex: number} | null>(null)

  // Split essay into paragraphs
  const paragraphs = essayText.split('\n').filter(p => p.trim().length > 0)

  // Get all evidence spans for highlighting
  const getAllEvidenceSpans = () => {
    const allSpans: Array<{
      text: string
      criterionIndex: number
      evidenceIndex: number
      paraIndex?: number
      criterionId: string
      level: string
    }> = []

    result.items.forEach((item, criterionIndex) => {
      if (item.evidenceSpans && Array.isArray(item.evidenceSpans)) {
        item.evidenceSpans.forEach((evidence, evidenceIndex) => {
          if (evidence.text && evidence.text.trim().length > 0) {
            allSpans.push({
              text: evidence.text,
              criterionIndex,
              evidenceIndex,
              paraIndex: evidence.paraIndex,
              criterionId: item.criterionId,
              level: item.level
            })
          }
        })
      }
    })

    return allSpans
  }

  const getCriterionColor = (index: number) => {
    const colors = [
      'bg-blue-200 text-blue-900',
      'bg-green-200 text-green-900', 
      'bg-purple-200 text-purple-900',
      'bg-orange-200 text-orange-900',
      'bg-pink-200 text-pink-900',
      'bg-indigo-200 text-indigo-900'
    ]
    return colors[index % colors.length]
  }

  const highlightTextInParagraph = (paragraph: string, paragraphIndex: number) => {
    const allSpans = getAllEvidenceSpans()
    const relevantSpans = allSpans.filter(span => 
      span.paraIndex === paragraphIndex && 
      (showAllEvidence || selectedCriterion === null || span.criterionIndex === selectedCriterion)
    )

    if (relevantSpans.length === 0) {
      return <span>{paragraph}</span>
    }

    // Sort spans by position in text (longest first to avoid conflicts)
    relevantSpans.sort((a, b) => b.text.length - a.text.length)

    let highlightedText = paragraph
    const highlights: Array<{
      start: number
      end: number
      span: typeof relevantSpans[0]
    }> = []

    // Find all highlight positions
    relevantSpans.forEach(span => {
      const index = highlightedText.toLowerCase().indexOf(span.text.toLowerCase())
      if (index !== -1) {
        highlights.push({
          start: index,
          end: index + span.text.length,
          span
        })
      }
    })

    // Sort highlights by start position
    highlights.sort((a, b) => a.start - b.start)

    // Build highlighted text
    let result = []
    let lastIndex = 0

    highlights.forEach((highlight, index) => {
      // Add text before highlight
      if (highlight.start > lastIndex) {
        result.push(highlightedText.slice(lastIndex, highlight.start))
      }

      // Add highlighted text
      const isHovered = hoveredEvidence?.criterionIndex === highlight.span.criterionIndex && 
                       hoveredEvidence?.evidenceIndex === highlight.span.evidenceIndex

      result.push(
        <span
          key={index}
          className={`px-1 rounded cursor-pointer transition-all duration-200 ${getCriterionColor(highlight.span.criterionIndex)} ${
            isHovered ? 'ring-2 ring-blue-400 shadow-md' : 'hover:shadow-sm'
          }`}
          title={`${highlight.span.criterionId}: ${highlight.span.level}`}
          onMouseEnter={() => setHoveredEvidence({
            criterionIndex: highlight.span.criterionIndex,
            evidenceIndex: highlight.span.evidenceIndex
          })}
          onMouseLeave={() => setHoveredEvidence(null)}
        >
          {highlightedText.slice(highlight.start, highlight.end)}
        </span>
      )

      lastIndex = highlight.end
    })

    // Add remaining text
    if (lastIndex < highlightedText.length) {
      result.push(highlightedText.slice(lastIndex))
    }

    return <span>{result}</span>
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Essay with Evidence Highlights</h3>
        <div className="text-sm text-gray-600">
          {getAllEvidenceSpans().length} evidence spans found
        </div>
      </div>

      <div className="bg-white border rounded-lg p-4 max-h-96 overflow-y-auto">
        {paragraphs.map((paragraph, index) => (
          <div key={index} className="mb-3">
            <div className="text-xs text-gray-500 mb-1">Paragraph {index + 1}</div>
            <div className="text-gray-800 leading-relaxed">
              {highlightTextInParagraph(paragraph, index)}
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="bg-gray-50 p-3 rounded-lg">
        <h4 className="text-sm font-medium mb-2">Evidence Legend</h4>
        <div className="flex flex-wrap gap-2">
          {result.items.map((item, index) => (
            <div key={index} className="flex items-center gap-1 text-xs">
              <span className={`px-2 py-1 rounded ${getCriterionColor(index)}`}>
                {item.criterionId?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || `Criterion ${index + 1}`}
              </span>
              <span className="text-gray-600">({item.level})</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
