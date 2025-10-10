import React, { useState } from 'react'
import type { EvaluationResult } from '../types'

interface HighlightedEssayProps {
  essayText: string
  result: EvaluationResult
  selectedCriterion?: number | null
  showAllEvidence?: boolean
  onHighlightClick?: (criterionId: string) => void
}

export default function HighlightedEssay({ 
  essayText, 
  result, 
  selectedCriterion = null, 
  showAllEvidence = true,
  onHighlightClick
}: HighlightedEssayProps) {
  const [hoveredEvidence, setHoveredEvidence] = useState<{criterionIndex: number, evidenceIndex: number} | null>(null)

  // Debug logging for actual evaluation data
  console.log('🔍 HighlightedEssay - essayText length:', essayText?.length)
  console.log('🔍 HighlightedEssay - result:', result)
  console.log('🔍 HighlightedEssay - result.items:', result?.items)

  // Split essay into paragraphs - improved splitting
  const paragraphs = essayText
    .split(/\n\s*\n/) // Split on double newlines (paragraph breaks)
    .map(p => p.replace(/\n/g, ' ').trim()) // Replace single newlines with spaces
    .filter(p => p.length > 0)
  
  console.log('🔍 Essay split into', paragraphs.length, 'paragraphs')
  paragraphs.forEach((para, idx) => {
    console.log(`🔍 Paragraph ${idx}: "${para.substring(0, 50)}..." (${para.length} chars)`)
  })

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

    console.log('🔍 getAllEvidenceSpans - Processing result.items:', result?.items?.length || 0, 'items')

    result.items.forEach((item, criterionIndex) => {
      console.log(`🔍 Criterion ${criterionIndex}:`, {
        criterionId: item.criterionId,
        level: item.level,
        evidenceSpansCount: item.evidenceSpans?.length || 0
      })
      
      if (item.evidenceSpans && Array.isArray(item.evidenceSpans)) {
        item.evidenceSpans.forEach((evidence, evidenceIndex) => {
          if (evidence.text && evidence.text.trim().length > 0) {
            console.log(`🔍 Evidence ${evidenceIndex}:`, {
              text: evidence.text.substring(0, 50) + '...',
              paraIndex: evidence.paraIndex
            })
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

    console.log('🔍 Total evidence spans found:', allSpans.length)
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
    
    // First try exact paragraph index match
    let relevantSpans = allSpans.filter(span => 
      span.paraIndex === paragraphIndex && 
      (showAllEvidence || selectedCriterion === null || span.criterionIndex === selectedCriterion)
    )
    
    // If no exact matches, try to find spans that contain text from this paragraph
    if (relevantSpans.length === 0) {
      relevantSpans = allSpans.filter(span => {
        const spanText = span.text.toLowerCase().trim()
        const paraText = paragraph.toLowerCase().trim()
        return paraText.includes(spanText) && 
               (showAllEvidence || selectedCriterion === null || span.criterionIndex === selectedCriterion)
      })
      console.log(`🔍 Paragraph ${paragraphIndex}: No exact paraIndex matches, found ${relevantSpans.length} text-based matches`)
    }

    console.log(`🔍 Paragraph ${paragraphIndex}: Found ${relevantSpans.length} relevant spans out of ${allSpans.length} total`)
    relevantSpans.forEach((span, idx) => {
      console.log(`🔍   Span ${idx}: "${span.text.substring(0, 30)}..." (criterion ${span.criterionIndex})`)
    })

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

    // Find all highlight positions - improved algorithm
    relevantSpans.forEach(span => {
      const searchText = span.text.toLowerCase()
      const paragraphText = highlightedText.toLowerCase()
      let searchIndex = 0
      
      // Find all occurrences of the evidence text
      while (true) {
        const index = paragraphText.indexOf(searchText, searchIndex)
        if (index === -1) break
        
        // Check if this position is already covered by another highlight
        const isOverlapping = highlights.some(existing => 
          (index >= existing.start && index < existing.end) ||
          (index + span.text.length > existing.start && index + span.text.length <= existing.end)
        )
        
        if (!isOverlapping) {
          highlights.push({
            start: index,
            end: index + span.text.length,
            span
          })
        }
        
        searchIndex = index + 1
      }
    })

    // Sort highlights by start position
    highlights.sort((a, b) => a.start - b.start)
    
    console.log(`🔍 Paragraph ${paragraphIndex}: Created ${highlights.length} highlights from ${relevantSpans.length} spans`)

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
           title={`${highlight.span.criterionId}: ${highlight.span.level} - Click to view details`}
           onMouseEnter={() => setHoveredEvidence({
             criterionIndex: highlight.span.criterionIndex,
             evidenceIndex: highlight.span.evidenceIndex
           })}
           onMouseLeave={() => setHoveredEvidence(null)}
           onClick={() => {
             console.log('🔍 Highlight clicked:', highlight.span.criterionId)
             if (onHighlightClick) {
               onHighlightClick(highlight.span.criterionId)
             }
           }}
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

  // Early return if no data
  if (!essayText || !result || !result.items) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Essay with Evidence Highlights</h3>
          <div className="text-sm text-gray-600">No data available</div>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
          <p className="text-yellow-800">No essay text or evaluation results available for highlighting.</p>
        </div>
      </div>
    )
  }

  const evidenceSpans = getAllEvidenceSpans()

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Essay with Evidence Highlights</h3>
        <div className="text-sm text-gray-600">
          {evidenceSpans.length} evidence spans found
        </div>
      </div>

      <div className="bg-white border rounded-lg p-4 max-h-96 overflow-y-auto">
        {evidenceSpans.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No evidence spans found in the evaluation results.</p>
            <p className="text-sm mt-2">The essay will be displayed without highlighting.</p>
          </div>
        ) : (
          paragraphs.map((paragraph, index) => (
            <div key={index} className="mb-3">
              <div className="text-xs text-gray-500 mb-1">Paragraph {index + 1}</div>
              <div className="text-gray-800 leading-relaxed">
                {highlightTextInParagraph(paragraph, index)}
              </div>
            </div>
          ))
        )}
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
