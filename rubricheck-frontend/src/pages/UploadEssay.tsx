import React, { useState } from 'react'
import { useApp } from '../store'
import { uploadEssayFile } from '../lib/api'

export default function UploadEssay() {
  const { essayFilePath, setEssayFilePath } = useApp()
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null)

  const onFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    setUploadError(null)

    try {
      // Just upload the file and get the file path
      const uploadResult = await uploadEssayFile(file)
      setEssayFilePath(uploadResult.file_path)
      setUploadedFileName(uploadResult.filename)
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
          {isUploading ? 'Uploading...' : 'Choose file'}
        </label>
      </div>
      <p className="text-sm text-gray-600 mb-3">
        Upload an essay file. The file will be processed by the backend.
        Supported formats: <code>.txt</code>, <code>.docx</code>, <code>.pdf</code>, <code>.png</code>, <code>.jpg</code>, <code>.jpeg</code>, <code>.webp</code>, <code>.tif</code>, <code>.tiff</code>, <code>.bmp</code>
      </p>
      
      {uploadError && (
        <div className="mt-2 text-sm text-red-700 bg-red-50 p-2 rounded">
          ❌ Error: {uploadError}
        </div>
      )}
      
      {uploadedFileName && (
        <div className="mt-3 text-sm text-green-700 bg-green-50 p-3 rounded">
          ✅ File uploaded successfully: <span className="font-medium">{uploadedFileName}</span>
          <br />
          <span className="text-xs text-gray-600">File path: {essayFilePath}</span>
        </div>
      )}
      
      {!uploadedFileName && !isUploading && (
        <div className="mt-3 text-sm text-gray-500 bg-gray-50 p-3 rounded">
          📁 No file selected. Please choose an essay file to upload.
        </div>
      )}
    </section>
  )
}
