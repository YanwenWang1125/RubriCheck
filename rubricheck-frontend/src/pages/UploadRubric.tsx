import React from 'react'
import { useApp } from '../store'
import type { Rubric } from '../types'

export default function UploadRubric() {
  const { rubric, setRubric } = useApp()

  const onFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const text = await file.text()
    try {
      const parsed = JSON.parse(text) as Rubric
      setRubric(parsed)
    } catch (err) {
      alert('Invalid JSON rubric.')
    }
  }

  const onPaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
    // no-op, user pastes JSON manually
  }

  return (
    <section id="rubric" className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">1) Upload Rubric (JSON)</h2>
        <label className="btn cursor-pointer">
          <input type="file" accept="application/json" className="hidden" onChange={onFile} />
          Choose file
        </label>
      </div>
      <p className="text-sm text-gray-600 mb-3">
        Provide a rubric JSON with <code>title</code>, <code>criteria[]</code> (each with <code>name</code>, <code>levels[]</code>).
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
      {rubric && (
        <div className="mt-3 text-sm text-green-700">
          ✅ Loaded rubric: <span className="font-medium">{rubric.title}</span> ({rubric.criteria.length} criteria)
        </div>
      )}
    </section>
  )
}
