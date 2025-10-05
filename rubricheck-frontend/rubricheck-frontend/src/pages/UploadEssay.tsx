import React, { useState } from 'react'
import { useApp } from '../store'

export default function UploadEssay() {
  const { essayText, setEssayText } = useApp()
  const [chars, setChars] = useState(essayText.length)

  return (
    <section id="essay" className="card p-6">
      <h2 className="text-lg font-semibold mb-4">2) Paste Essay</h2>
      <textarea
        className="input min-h-[240px]"
        placeholder="Paste or type the student's essay here..."
        value={essayText}
        onChange={(e) => { setEssayText(e.target.value); setChars(e.target.value.length) }}
      />
      <div className="mt-2 text-xs text-gray-500">{chars} characters</div>
    </section>
  )
}
