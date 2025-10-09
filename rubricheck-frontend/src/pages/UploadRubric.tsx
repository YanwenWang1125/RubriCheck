import React, { useState } from 'react'
import { useApp } from '../store'
import type { Rubric } from '../types'
import { parseRubricFile } from '../lib/api'

export default function UploadRubric() {
  const { rubric, setRubric } = useApp()
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)

  const onFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    setUploadError(null)

    try {
      // Check if it's a JSON file
      if (file.type === 'application/json' || file.name.endsWith('.json')) {
        const text = await file.text()
        const parsed = JSON.parse(text) as Rubric
        setRubric(parsed)
      } else {
        // For DOCX/TXT files, send to backend for parsing
        const parsedRubric = await parseRubricFile(file)
        setRubric(parsedRubric)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to process file'
      setUploadError(errorMessage)
      console.error('File processing error:', err)
    } finally {
      setIsUploading(false)
    }
  }

  const onPaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
    // no-op, user pastes JSON manually
  }

  return (
    <section id="rubric" className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">1) Upload Rubric</h2>
        <label className="btn cursor-pointer">
          <input 
            type="file" 
            accept=".json,.docx,.txt,application/json,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain" 
            className="hidden" 
            onChange={onFile}
            disabled={isUploading}
          />
          {isUploading ? 'Processing...' : 'Choose file'}
        </label>
      </div>
      <p className="text-sm text-gray-600 mb-3">
        Upload a rubric file (JSON, DOCX, or TXT) or paste JSON directly. 
        Supported formats: <code>.json</code>, <code>.docx</code>, <code>.txt</code>
      </p>
      <textarea
        className="input min-h-[140px] font-mono"
        placeholder='Paste rubric JSON here...'
        defaultValue={rubric ? JSON.stringify(rubric, null, 2) : ''}
        onChange={(e) => {
          try {
            const parsed = JSON.parse(e.target.value) as Rubric
            setRubric(parsed)
          } catch { /* ignore while typing */ }
        }}
        onPaste={onPaste}
      />
      {uploadError && (
        <div className="mt-3 text-sm text-red-700 bg-red-50 p-2 rounded">
          ❌ Error: {uploadError}
        </div>
      )}
      {rubric && (
        <div className="mt-3 text-sm text-green-700">
          ✅ Loaded rubric: <span className="font-medium">{rubric.title}</span> ({rubric.criteria.length} criteria)
        </div>
      )}
    </section>
  )
}
