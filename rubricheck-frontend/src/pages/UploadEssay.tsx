import React, { useState } from 'react'
import { useApp } from '../store'
import { parseEssayFile, uploadEssayFile } from '../lib/api'

export default function UploadEssay() {
  const { essayText, setEssayText, essayFilePath, setEssayFilePath } = useApp()
  const [chars, setChars] = useState(essayText.length)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)

  const onFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    setUploadError(null)

    try {
      // Upload file to get file path
      const uploadResult = await uploadEssayFile(file)
      setEssayFilePath(uploadResult.file_path)
      
      // Also parse to show text in UI
      const result = await parseEssayFile(file)
      setEssayText(result.text)
      setChars(result.text.length)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to process file'
      setUploadError(errorMessage)
      console.error('File processing error:', err)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <section id="essay" className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">2) Upload Essay</h2>
        <label className="btn cursor-pointer">
          <input 
            type="file" 
            accept=".txt,.docx,.pdf,.png,.jpg,.jpeg,.webp,.tif,.tiff,.bmp,text/plain,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/pdf,image/*" 
            className="hidden" 
            onChange={onFile}
            disabled={isUploading}
          />
          {isUploading ? 'Processing...' : 'Choose file'}
        </label>
      </div>
      <p className="text-sm text-gray-600 mb-3">
        Upload an essay file or paste text directly. 
        Supported formats: <code>.txt</code>, <code>.docx</code>, <code>.pdf</code>, <code>.png</code>, <code>.jpg</code>, <code>.jpeg</code>, <code>.webp</code>, <code>.tif</code>, <code>.tiff</code>, <code>.bmp</code>
      </p>
      <textarea
        className="input min-h-[240px]"
        placeholder="Paste or type the student's essay here..."
        value={essayText}
        onChange={(e) => { setEssayText(e.target.value); setChars(e.target.value.length) }}
      />
      {uploadError && (
        <div className="mt-2 text-sm text-red-700 bg-red-50 p-2 rounded">
          ❌ Error: {uploadError}
        </div>
      )}
      <div className="mt-2 text-xs text-gray-500">{chars} characters</div>
    </section>
  )
}
