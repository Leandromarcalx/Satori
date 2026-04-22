import React, { useState, useRef } from 'react'
import { UploadCloud, CheckCircle, FileText, AlertCircle } from 'lucide-react'

export default function ReceiptUploader() {
  const [file, setFile] = useState(null)
  const [previewSize, setPreviewSize] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploadState, setUploadState] = useState('idle') // idle, uploading, success, error
  const [extractedItems, setExtractedItems] = useState([])
  const [errorMsg, setErrorMsg] = useState('')
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (selectedFile) => {
    if (!selectedFile.type.startsWith('image/')) {
        setErrorMsg('Please upload an image file (PNG, JPG).')
        setUploadState('error')
        return
    }
    setFile(selectedFile)
    setPreviewSize((selectedFile.size / 1024 / 1024).toFixed(2)) // MB
    setUploadState('idle')
    setErrorMsg('')
    setExtractedItems([])
  }

  const uploadFile = async () => {
    if (!file) return

    setUploadState('uploading')
    const formData = new FormData()
    formData.append('receipt', file)

    try {
      const response = await fetch('/api/upload-receipt', {
        method: 'POST',
        body: formData
      })

      const result = await response.json()
      
      if (!response.ok) {
        throw new Error(result.detail || 'Failed to analyze receipt')
      }

      setExtractedItems(result.items || [])
      setUploadState('success')
    } catch (err) {
      console.error(err)
      setErrorMsg(err.message)
      setUploadState('error')
    }
  }

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="header">
        <h1>Upload Receipt</h1>
      </div>
      
      <div 
        className={`glass-panel dropzone ${isDragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleChange} 
          accept="image/*" 
          style={{ display: 'none' }} 
        />
        <UploadCloud size={48} className="upload-icon" />
        <h3>Drag & drop your receipt here</h3>
        <p>or click to select file</p>
      </div>

      {file && (
        <div className="glass-panel" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <FileText size={24} color="var(--primary-color)" />
            <div>
              <div style={{ fontWeight: 600 }}>{file.name}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{previewSize} MB</div>
            </div>
          </div>
          
          <button 
            className="btn-primary" 
            onClick={uploadFile} 
            disabled={uploadState === 'uploading'}
          >
            {uploadState === 'uploading' ? 'Analyzing...' : 'Process Receipt'}
          </button>
        </div>
      )}

      {uploadState === 'error' && (
        <div className="glass-panel error-panel">
            <AlertCircle size={24} color="var(--error)" />
            <span>{errorMsg}</span>
        </div>
      )}

      {uploadState === 'success' && (
        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', color: 'var(--success)' }}>
            <CheckCircle size={24} />
            <h2 style={{ margin: 0, color: 'var(--success)' }}>Extracted Items</h2>
          </div>
          
          {extractedItems.length === 0 ? (
            <p>No items found.</p>
          ) : (
            <ul className="item-list">
              {extractedItems.map((item, idx) => (
                <li key={idx} className="item-row">
                  <span className="item-name">{item.name}</span>
                  <span className="item-qty">{item.quantity}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
