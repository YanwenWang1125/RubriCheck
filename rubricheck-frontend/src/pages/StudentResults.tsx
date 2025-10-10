import React, { useState, useEffect, useRef } from 'react'
import { useApp } from '../store'

interface EvidenceSpan {
  start: number
  end: number
  paragraph: number
  text: string
  relevance_score: number
}

interface Criterion {
  id: string
  name: string
  weight: number
  score: number
  level: 'Excellent' | 'Proficient' | 'Meets expectations' | 'Developing' | 'Poor'
  confidence: number
  evidence_spans: EvidenceSpan[]
  feedback: {
    why: string
    suggestion: string
    strengths?: string[]
    areas_for_improvement?: string[]
  }
}

interface StudentResult {
  id: string
  essay_text: string
  overall_score: number
  letter_grade: string
  timestamp: string
  criteria: Criterion[]
  metadata: {
    word_count: number
    paragraph_count: number
    reading_time: string
  }
}

interface StudentResultsProps {
  onViewChange: (view: 'main' | 'student-results') => void
}

export default function StudentResults({ onViewChange }: StudentResultsProps) {
  const { result, essayText } = useApp()
  const [viewMode, setViewMode] = useState<'annotated' | 'original'>('annotated')
  const [selectedCriterion, setSelectedCriterion] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentCriterionIndex, setCurrentCriterionIndex] = useState(-1)
  const [showConfidenceIndicators, setShowConfidenceIndicators] = useState(true)
  const [expandedCriteria, setExpandedCriteria] = useState<Set<string>>(new Set())
  const [isFeedbackPanelCollapsed, setIsFeedbackPanelCollapsed] = useState(false)
  
  const criteriaRefs = useRef<(HTMLDivElement | null)[]>([])
  const essayRef = useRef<HTMLDivElement>(null)
  const rightPanelRef = useRef<HTMLDivElement>(null)

  // Convert backend result to student result format
  console.log('🔍 Debug - Raw result:', result)
  console.log('🔍 Debug - Essay text from store:', essayText)
  console.log('🔍 Debug - Essay text length:', essayText?.length)
  
  // Try to reconstruct essay text from evidence spans if main essay text is not available
  const getEssayTextFromEvidence = () => {
    if (essayText) return essayText
    
    if (result?.items) {
      // Collect all evidence spans and try to reconstruct the essay
      const allEvidence = result.items.flatMap(item => item.evidenceSpans || [])
      if (allEvidence.length > 0) {
        // Sort by paragraph index and join the text
        const sortedEvidence = allEvidence
          .filter(ev => ev.text && ev.text.trim().length > 0)
          .sort((a, b) => (a.paraIndex || 0) - (b.paraIndex || 0))
        
        if (sortedEvidence.length > 0) {
          console.log('📝 Reconstructing essay from evidence spans:', sortedEvidence.length, 'spans')
          
          // Group by paragraph and join with proper spacing
          const paragraphs: string[] = []
          let currentPara = 0
          let currentParaText = ''
          
          sortedEvidence.forEach(ev => {
            const paraIndex = ev.paraIndex || 0
            if (paraIndex !== currentPara) {
              if (currentParaText.trim()) {
                paragraphs.push(currentParaText.trim())
              }
              currentPara = paraIndex
              currentParaText = ev.text
            } else {
              currentParaText += ' ' + ev.text
            }
          })
          
          if (currentParaText.trim()) {
            paragraphs.push(currentParaText.trim())
          }
          
          return paragraphs.join('\n\n')
        }
      }
    }
    
    return ''
  }

  const studentResult: StudentResult | null = result ? {
    id: 'student_result_001',
    essay_text: getEssayTextFromEvidence(),
    overall_score: typeof result.overall?.numeric === 'number' ? 
      (result.overall.numeric > 1 ? result.overall.numeric : result.overall.numeric * 100) : 0,
    letter_grade: result.overall?.letter || 'N/A',
    timestamp: new Date().toISOString(),
    criteria: result.items?.map((item: any, index: number) => {
      // Handle different data structures - check for actual field names
      const criterionId = item.criterionId || item.id || `criterion_${index}`
      const criterionName = item.name || getCriterionNameFromId(criterionId) || `Criterion ${index + 1}`
      console.log(`🏷️ Criterion ${index}: id="${criterionId}", name="${criterionName}"`)
      const level = item.level || getLevelFromScore(item.score || 0)
      const score = item.score || (level === 'Excellent' ? 5 : level === 'Good' ? 4 : level === 'Fair' ? 3 : level === 'Developing' ? 2 : 1)
      const evidenceSpans = item.evidenceSpans || item.evidence_spans || []
      
      return {
        id: criterionId,
        name: criterionName,
        weight: item.weight || 20,
        score: score,
        level: level,
        confidence: item.confidence || 0.8,
        evidence_spans: evidenceSpans,
        feedback: {
          why: item.justification || item.feedback?.why || 'No feedback available.',
          suggestion: item.suggestion || item.feedback?.suggestion || 'No suggestions available.',
          strengths: item.feedback?.strengths || [],
          areas_for_improvement: item.feedback?.areas_for_improvement || []
        }
      }
    }) || [],
    metadata: {
      word_count: (() => {
        const text = getEssayTextFromEvidence()
        const count = text ? text.split(/\s+/).filter(word => word.trim().length > 0).length : 0
        console.log('📊 Word count calculated:', count, 'from text length:', text?.length || 0)
        return count
      })(),
      paragraph_count: (() => {
        const text = getEssayTextFromEvidence()
        const count = text ? text.split(/\n\s*\n/).filter(para => para.trim().length > 0).length : 0
        console.log('📊 Paragraph count calculated:', count)
        return count
      })(),
      reading_time: (() => {
        const text = getEssayTextFromEvidence()
        if (!text) return '0 minutes'
        const wordCount = text.split(/\s+/).filter(word => word.trim().length > 0).length
        const slowReading = Math.ceil(wordCount / 150) // 150 words per minute (slow)
        const fastReading = Math.ceil(wordCount / 250) // 250 words per minute (fast)
        const readingTime = wordCount > 0 ? `${fastReading}-${slowReading} minutes` : '0 minutes'
        console.log('📊 Reading time calculated:', readingTime, 'from', wordCount, 'words')
        return readingTime
      })()
    }
  } : null

  console.log('🔍 Debug - Final studentResult:', studentResult)

  function getLevelFromScore(score: number): 'Excellent' | 'Proficient' | 'Meets expectations' | 'Developing' | 'Poor' {
    if (score >= 4.5) return 'Excellent'
    if (score >= 3.5) return 'Proficient'
    if (score >= 2.5) return 'Meets expectations'
    if (score >= 1.5) return 'Developing'
    return 'Poor'
  }

  function getCriterionNameFromId(criterionId: string): string {
    const nameMap: { [key: string]: string } = {
      'focus_and_thesis': 'Focus & Thesis',
      'organization_and_flow': 'Organization & Flow',
      'evidence_and_support': 'Evidence & Support',
      'analysis_and_insight': 'Analysis & Insight',
      'style_and_clarity': 'Style & Clarity',
      'grammar_and_mechanics': 'Grammar & Mechanics',
      'criterion_0': 'Focus & Thesis',
      'criterion_1': 'Organization & Flow',
      'criterion_2': 'Evidence & Support',
      'criterion_3': 'Analysis & Insight',
      'criterion_4': 'Style & Clarity',
      'criterion_5': 'Grammar & Mechanics'
    }
    return nameMap[criterionId] || criterionId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  const getLevelColor = (level: string) => {
    const levelColors: { [key: string]: string } = {
      'Excellent': 'bg-emerald-100 text-emerald-800 border-2 border-emerald-500',
      'Proficient': 'bg-sky-100 text-sky-800 border-2 border-sky-500',
      'Meets expectations': 'bg-amber-100 text-amber-800 border-2 border-amber-500',
      'Developing': 'bg-rose-100 text-rose-800 border-2 border-rose-500',
      'Poor': 'bg-red-100 text-red-800 border-2 border-red-500',
      'Good': 'bg-blue-100 text-blue-800 border-2 border-blue-500',
      'Fair': 'bg-yellow-100 text-yellow-800 border-2 border-yellow-500'
    }
    const color = levelColors[level] || 'bg-gray-100 text-gray-800 border-2 border-gray-500'
    console.log(`🎨 Level color for "${level}": ${color}`)
    return color
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence > 0.8) return 'text-green-600'
    if (confidence > 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getCriterionBorderColor = (index: number) => {
    // Use the same colors as the evidence highlights
    const colors = ['#fef3c7', '#dbeafe', '#d1fae5', '#fce7f3', '#e9d5ff', '#fed7aa']
    const color = colors[index % colors.length]
    return `border-4 rounded-lg`
  }

  const getCriterionBorderStyle = (index: number) => {
    // Use the same colors as the evidence highlights
    const colors = ['#fef3c7', '#dbeafe', '#d1fae5', '#fce7f3', '#e9d5ff', '#fed7aa']
    const color = colors[index % colors.length]
    return { borderColor: color }
  }

  const highlightEvidence = (criterionId: string) => {
    console.log(`🎯 Highlighting evidence for criterion: ${criterionId}`)
    setSelectedCriterion(criterionId)
    
    // Auto-expand the criterion when evidence is clicked
    setExpandedCriteria(prev => new Set([...prev, criterionId]))
    
    // Scroll to evidence in essay
    if (essayRef.current) {
      const evidenceElements = essayRef.current.querySelectorAll(`[data-criterion="${criterionId}"]`)
      if (evidenceElements.length > 0) {
        evidenceElements[0].scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }
    
    // Scroll to corresponding criterion in right panel
    setTimeout(() => {
      const criterionElement = document.getElementById(`criterion-${criterionId}`)
      console.log(`🎯 Looking for criterion element: criterion-${criterionId}`, criterionElement)
      
      if (criterionElement) {
        console.log(`🎯 Found criterion element, scrolling to it`)
        
        // Ensure the right panel is visible and focused
        if (rightPanelRef.current) {
          console.log(`🎯 Ensuring right panel is visible`)
          rightPanelRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
        }
        
        // Scroll to the specific criterion within the right panel
        criterionElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
        
        // Add a temporary highlight effect
        criterionElement.classList.add('criterion-highlighted')
        console.log(`🎯 Added highlight effect to criterion`)
        
        setTimeout(() => {
          criterionElement.classList.remove('criterion-highlighted')
          console.log(`🎯 Removed highlight effect from criterion`)
        }, 2000)
      } else {
        console.log(`🚨 Criterion element not found: criterion-${criterionId}`)
      }
    }, 100) // Small delay to ensure expansion animation completes
  }

  const toggleCriterionExpansion = (criterionId: string) => {
    setExpandedCriteria(prev => {
      const newSet = new Set(prev)
      if (newSet.has(criterionId)) {
        newSet.delete(criterionId)
      } else {
        newSet.add(criterionId)
      }
      return newSet
    })
  }

  const toggleFeedbackPanel = () => {
    setIsFeedbackPanelCollapsed(!isFeedbackPanelCollapsed)
  }

  const renderEssayWithHighlights = () => {
    console.log('🔍 Debug - renderEssayWithHighlights called')
    console.log('🔍 Debug - studentResult:', studentResult)
    console.log('🔍 Debug - essay_text:', studentResult?.essay_text)
    
    if (!studentResult || !studentResult.essay_text) {
      console.log('🚨 Debug - renderEssayWithHighlights: studentResult or essay_text is missing')
      return null
    }

    // Always start with the original essay text
    let essayHTML = studentResult.essay_text
      .replace(/\n\n/g, '</p><p class="mb-4">')
      .replace(/\n/g, '<br>')
    
    if (viewMode === 'annotated') {
      // Add evidence highlights only in annotated mode
      studentResult.criteria.forEach((criterion, criterionIndex) => {
        criterion.evidence_spans.forEach((span, spanIndex) => {
          const highlightId = `highlight-${criterionIndex}-${spanIndex}`
          const highlightedText = `<span class="evidence-highlight ${selectedCriterion === criterion.id ? 'active' : ''}" 
            id="${highlightId}" 
            data-criterion="${criterion.id}" 
            data-criterion-name="${criterion.name}"
            style="background-color: ${getHighlightColor(criterionIndex)}; cursor: pointer; padding: 2px 4px; border-radius: 4px; transition: all 0.2s ease;"
            onmouseover="this.style.backgroundColor='${getHighlightHoverColor(criterionIndex)}'"
            onmouseout="this.style.backgroundColor='${getHighlightColor(criterionIndex)}'"
            onclick="window.openCriterionFromEvidence && window.openCriterionFromEvidence('${criterion.id}')"
          >${span.text}</span>`
          essayHTML = essayHTML.replace(span.text, highlightedText)
        })
      })
    }
    // In original mode, essayHTML remains clean without any highlights

    return `<p class="mb-4">${essayHTML}</p>`
  }

  const getHighlightColor = (index: number) => {
    const colors = ['#fef3c7', '#dbeafe', '#d1fae5', '#fce7f3', '#e9d5ff', '#fed7aa']
    return colors[index % colors.length]
  }

  const getHighlightHoverColor = (index: number) => {
    const colors = ['#fde68a', '#bfdbfe', '#a7f3d0', '#f9a8d4', '#ddd6fe', '#fdba74']
    return colors[index % colors.length]
  }

  const filteredCriteria = studentResult?.criteria.filter(criterion =>
    criterion.name.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  // Set up global function for evidence clicks
  useEffect(() => {
    (window as any).openCriterionFromEvidence = (criterionId: string) => {
      highlightEvidence(criterionId)
    }
    
    return () => {
      delete (window as any).openCriterionFromEvidence
    }
  }, [])

  // Check for criterion ID in URL parameters when component mounts
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const criterionId = urlParams.get('criterion')
    if (criterionId && studentResult) {
      console.log('🔍 Found criterion ID in URL:', criterionId)
      // Small delay to ensure component is fully rendered
      setTimeout(() => {
        highlightEvidence(criterionId)
        // Clear the URL parameter after processing
        const currentUrl = new URL(window.location.href)
        currentUrl.searchParams.delete('criterion')
        window.history.replaceState({}, '', currentUrl.toString())
      }, 500)
    }
  }, [studentResult])

  // Debug: Watch for store changes
  useEffect(() => {
    console.log('🔄 StudentResults useEffect - store changed')
    console.log('🔄 result:', result)
    console.log('🔄 essayText:', essayText)
    console.log('🔄 essayText length:', essayText?.length)
  }, [result, essayText])

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setCurrentCriterionIndex(prev => {
          if (prev === -1) return 0 // Start from first item if none selected
          return Math.min(prev + 1, filteredCriteria.length - 1)
        })
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setCurrentCriterionIndex(prev => {
          if (prev === -1) return filteredCriteria.length - 1 // Start from last item if none selected
          return Math.max(prev - 1, 0)
        })
      } else if (e.key === 'Enter') {
        e.preventDefault()
        if (currentCriterionIndex >= 0 && filteredCriteria[currentCriterionIndex]) {
          highlightEvidence(filteredCriteria[currentCriterionIndex].id)
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [currentCriterionIndex, filteredCriteria])

  // Focus management
  useEffect(() => {
    if (currentCriterionIndex >= 0 && criteriaRefs.current[currentCriterionIndex]) {
      criteriaRefs.current[currentCriterionIndex]?.focus()
      criteriaRefs.current[currentCriterionIndex]?.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      })
    }
  }, [currentCriterionIndex])

  if (!studentResult) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">RubriCheck Results — Student View</h2>
            <div className="text-gray-600 space-y-4">
              <p>No results available yet. To see your evaluation results:</p>
              <ol className="list-decimal list-inside space-y-2 ml-4">
                <li>Upload a rubric file (PDF, DOCX, or TXT)</li>
                <li>Upload an essay file (PDF, DOCX, or TXT)</li>
                <li>Click "Run Evaluation" to analyze your essay</li>
                <li>Return here to view your results in student-friendly format</li>
              </ol>
              <div className="mt-6">
                <button 
                  onClick={() => onViewChange('main')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Go to Main View
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">RubriCheck Results — Student View</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button 
                onClick={() => {/* Export PDF functionality */}}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Export PDF
              </button>
              <button 
                onClick={() => {/* Export CSV functionality */}}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                Export CSV
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overall Score Summary */}
        <div className="bg-white rounded-lg shadow-sm border-2 border-gray-300 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Overall Score</h2>
            <div className="text-right">
              <div className="text-4xl font-bold text-blue-600">{studentResult.overall_score.toFixed(1)}</div>
              <div className="text-lg text-gray-600">{studentResult.letter_grade}</div>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-700">Word Count:</span>
              <span className="ml-2">{studentResult.metadata.word_count}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Paragraphs:</span>
              <span className="ml-2">{studentResult.metadata.paragraph_count}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Reading Time:</span>
              <span className="ml-2">{studentResult.metadata.reading_time}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Submitted:</span>
              <span className="ml-2">{new Date(studentResult.timestamp).toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Split View Container */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel: Essay Viewer */}
          <div className="bg-white rounded-lg shadow-sm border-2 border-gray-300">
            <div className="p-4 border-b bg-gray-50">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Your Essay (Annotated)</h3>
                <div className="flex items-center space-x-2">
                  <button 
                    onClick={() => setViewMode('annotated')}
                    className={`px-3 py-1 text-sm rounded-md focus:outline-none focus:ring-2 ${
                      viewMode === 'annotated' 
                        ? 'bg-blue-600 text-white focus:ring-blue-500' 
                        : 'bg-gray-300 text-gray-700 hover:bg-gray-400 focus:ring-gray-500'
                    }`}
                  >
                    Annotated
                  </button>
                  <button 
                    onClick={() => setViewMode('original')}
                    className={`px-3 py-1 text-sm rounded-md focus:outline-none focus:ring-2 ${
                      viewMode === 'original' 
                        ? 'bg-blue-600 text-white focus:ring-blue-500' 
                        : 'bg-gray-300 text-gray-700 hover:bg-gray-400 focus:ring-gray-500'
                    }`}
                  >
                    Original
                  </button>
                </div>
              </div>
            </div>
            <div className="p-6">
              {studentResult?.essay_text ? (
                <div 
                  ref={essayRef}
                  className={`prose max-w-none ${viewMode === 'original' ? 'original-view' : ''}`}
                  dangerouslySetInnerHTML={{ __html: renderEssayWithHighlights() || studentResult.essay_text }}
                />
              ) : (
                <div className="text-gray-500 italic space-y-2">
                  <div>No essay content available. Please load test data or run an evaluation.</div>
                  <div className="text-xs">
                    Debug info: studentResult = {studentResult ? 'exists' : 'null'}, 
                    essay_text = {studentResult?.essay_text ? `${studentResult.essay_text.length} chars` : 'empty'}
                  </div>
                  <div className="text-xs">
                    Raw essayText from store: {essayText ? `${essayText.length} chars` : 'empty'}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel: Rubric & Feedback */}
          <div ref={rightPanelRef} className="bg-white rounded-lg shadow-sm border-2 border-gray-300 sticky top-24 self-start max-h-[calc(100vh-8rem)] overflow-y-auto sticky-panel">
            <div className="p-4 border-b bg-gray-50">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold text-gray-900">Rubric & Feedback</h3>
                <button
                  onClick={toggleFeedbackPanel}
                  className="p-2 text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
                  title={isFeedbackPanelCollapsed ? "Expand feedback panel" : "Collapse feedback panel"}
                >
                  {isFeedbackPanelCollapsed ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                    </svg>
                  )}
                </button>
              </div>
              {!isFeedbackPanelCollapsed && (
                <input 
                  type="text" 
                  placeholder="Search criteria..." 
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              )}
            </div>
            <div className="p-4 flex-1 overflow-y-auto">
              <div className="space-y-3">
                {filteredCriteria.map((criterion, index) => {
                  const isExpanded = expandedCriteria.has(criterion.id)
                  return (
                    <div
                      key={criterion.id}
                      id={`criterion-${criterion.id}`}
                      ref={el => criteriaRefs.current[index] = el}
                      className={`${getCriterionBorderColor(index)} focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        currentCriterionIndex === index ? 'ring-2 ring-blue-500' : ''
                      }`}
                      style={getCriterionBorderStyle(index)}
                      tabIndex={0}
                      data-criterion-id={criterion.id}
                    >
                      {/* Top Status - Always Visible */}
                      <div 
                        className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                        onClick={() => toggleCriterionExpansion(criterion.id)}
                      >
                        <div className="flex items-center justify-between">
                          <h4 className="font-semibold text-gray-900">{criterion.name}</h4>
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getLevelColor(criterion.level)}`}>
                              {criterion.level}
                            </span>
                            <span className="text-sm text-gray-500">{criterion.score.toFixed(1)}/5.0</span>
                            <button
                              className="p-1 text-gray-400 hover:text-gray-600 focus:outline-none"
                              onClick={(e) => {
                                e.stopPropagation()
                                toggleCriterionExpansion(criterion.id)
                              }}
                            >
                              {isExpanded ? (
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                                </svg>
                              ) : (
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                </svg>
                              )}
                            </button>
                          </div>
                        </div>
                        
                        <div className="mt-2">
                          <div className="flex items-center justify-between text-sm mb-1">
                            <span>Score</span>
                            {showConfidenceIndicators && (
                              <span className={`text-xs ${getConfidenceColor(criterion.confidence)}`}>
                                {criterion.confidence > 0.8 ? 'High' : criterion.confidence > 0.6 ? 'Medium' : 'Low'} Confidence
                              </span>
                            )}
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                              style={{ width: `${(criterion.score / 5) * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>

                      {/* Expandable Content - Hidden by Default */}
                      {isExpanded && (
                        <div className="px-4 pb-4 border-t bg-gray-50">
                          <div className="pt-4 space-y-3">
                            <div>
                              <h5 className="font-medium text-gray-700 mb-1">Why this level?</h5>
                              <p className="text-sm text-gray-600">{criterion.feedback.why}</p>
                            </div>
                            
                            <div>
                              <h5 className="font-medium text-gray-700 mb-1">Try this next:</h5>
                              <p className="text-sm text-gray-600">{criterion.feedback.suggestion}</p>
                            </div>

                            {criterion.evidence_spans.length > 0 && (
                              <button 
                                className="text-sm text-blue-600 hover:text-blue-800 focus:outline-none focus:underline"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  highlightEvidence(criterion.id)
                                }}
                              >
                                Show evidence ({criterion.evidence_spans.length} span{criterion.evidence_spans.length > 1 ? 's' : ''})
                              </button>
                            )}

                            {criterion.feedback.strengths && criterion.feedback.strengths.length > 0 && (
                              <div>
                                <h5 className="font-medium text-green-700 mb-1">Strengths:</h5>
                                <ul className="text-sm text-green-600 list-disc list-inside">
                                  {criterion.feedback.strengths.map((strength, idx) => (
                                    <li key={idx}>{strength}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {criterion.feedback.areas_for_improvement && criterion.feedback.areas_for_improvement.length > 0 && (
                              <div>
                                <h5 className="font-medium text-orange-700 mb-1">Areas for improvement:</h5>
                                <ul className="text-sm text-orange-600 list-disc list-inside">
                                  {criterion.feedback.areas_for_improvement.map((area, idx) => (
                                    <li key={idx}>{area}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Help Section */}
        <div className="mt-8 bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">How to read your results</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-blue-800">
            <div>
              <h4 className="font-semibold mb-2">Left panel: "Your Essay (Annotated)"</h4>
              <ul className="space-y-1">
                <li>• Yellow highlights show text the AI used as evidence</li>
                <li>• Hover or tap a criterion to spotlight matching highlights</li>
                <li>• Use the Annotated / Original toggle to switch views</li>
                <li>• Use ↑/↓ arrows to navigate criteria, Enter to show evidence</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Right panel: "Rubric & Feedback"</h4>
              <ul className="space-y-1">
                <li>• Level badge shows your current performance</li>
                <li>• Score bar shows 1–5 scale for quick scanning</li>
                <li>• "Why?" explains the score with specific evidence</li>
                <li>• "Try this next" gives actionable improvement tips</li>
                <li>• Confidence indicators show system certainty</li>
              </ul>
            </div>
          </div>
        </div>
      </main>

      <style>{`
        .evidence-highlight {
          transition: all 0.2s ease;
        }
        .evidence-highlight:hover {
          transform: scale(1.02);
        }
        .evidence-highlight.active {
          border: 2px solid #f59e0b;
          box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.2);
        }
        .original-view .evidence-highlight {
          background-color: transparent !important;
          border: none !important;
          cursor: default !important;
          padding: 0 !important;
        }
        .sticky-panel {
          scroll-behavior: smooth;
        }
        .sticky-panel::-webkit-scrollbar {
          width: 6px;
        }
        .sticky-panel::-webkit-scrollbar-track {
          background: #f1f5f9;
          border-radius: 3px;
        }
        .sticky-panel::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 3px;
        }
        .sticky-panel::-webkit-scrollbar-thumb:hover {
          background: #94a3b8;
        }
        .criterion-highlighted {
          animation: highlightPulse 2s ease-in-out;
          border-color: #3b82f6 !important;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3) !important;
        }
        @keyframes highlightPulse {
          0% { 
            transform: scale(1);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5);
          }
          50% { 
            transform: scale(1.02);
            box-shadow: 0 0 0 6px rgba(59, 130, 246, 0.3);
          }
          100% { 
            transform: scale(1);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }
        }
      `}</style>
    </div>
  )
}
