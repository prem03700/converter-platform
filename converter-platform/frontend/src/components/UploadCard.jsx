import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X, FileText, Loader2, CheckCircle2, AlertCircle, Download } from 'lucide-react'
import { filesApi, convertApi } from '../api/client'

const MAX_MB = parseInt(import.meta.env.VITE_MAX_UPLOAD_MB || '200')

export default function UploadCard({ onConversionComplete }) {
  const [uploadedFile, setUploadedFile] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [targets, setTargets] = useState([])
  const [selectedTarget, setSelectedTarget] = useState('')
  const [conversion, setConversion] = useState(null)
  const [error, setError] = useState(null)
  const [phase, setPhase] = useState('idle') // idle | uploading | selecting | converting | done | error

  const reset = () => {
    setUploadedFile(null)
    setUploadProgress(0)
    setTargets([])
    setSelectedTarget('')
    setConversion(null)
    setError(null)
    setPhase('idle')
  }

  const onDrop = useCallback(async (accepted) => {
    if (!accepted.length) return
    const file = accepted[0]

    if (file.size > MAX_MB * 1024 * 1024) {
      setError(`File exceeds the ${MAX_MB} MB limit`)
      setPhase('error')
      return
    }

    setError(null)
    setPhase('uploading')
    setUploadProgress(0)

    try {
      const { data: record } = await filesApi.upload(file, (pct) => setUploadProgress(pct))
      setUploadedFile(record)

      const { data: targetData } = await convertApi.supportedTargets(record.id)
      setTargets(targetData.targets)
      setSelectedTarget(targetData.targets[0] || '')
      setPhase('selecting')
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed — please try again')
      setPhase('error')
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    disabled: phase === 'uploading' || phase === 'converting',
  })

  const handleConvert = async () => {
    if (!uploadedFile || !selectedTarget) return
    setPhase('converting')
    setError(null)

    try {
      const { data: conv } = await convertApi.convert(uploadedFile.id, selectedTarget)

      // Poll for completion when running with background Celery
      if (conv.status === 'pending' || conv.status === 'processing') {
        const pollId = setInterval(async () => {
          const { data: fresh } = await convertApi.status(conv.id)
          setConversion(fresh)
          if (fresh.status === 'completed' || fresh.status === 'failed') {
            clearInterval(pollId)
            setPhase(fresh.status === 'completed' ? 'done' : 'error')
            if (fresh.status === 'failed') setError(fresh.error_message || 'Conversion failed')
            if (fresh.status === 'completed') onConversionComplete?.()
          }
        }, 2000)
        setConversion(conv)
      } else {
        setConversion(conv)
        setPhase(conv.status === 'completed' ? 'done' : 'error')
        if (conv.status === 'failed') setError(conv.error_message || 'Conversion failed')
        if (conv.status === 'completed') onConversionComplete?.()
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Conversion request failed')
      setPhase('error')
    }
  }

  const downloadUrl = conversion?.id
    ? `${import.meta.env.VITE_API_URL || '/api/v1'}/convert/${conversion.id}/download`
    : null

  return (
    <div className="dark:glass-card glass-card-light p-8 w-full max-w-2xl mx-auto space-y-6">
      {/* Drop zone */}
      {(phase === 'idle' || phase === 'error') && (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-200
            ${isDragActive
              ? 'border-brand-500 bg-brand-500/10'
              : 'dark:border-white/20 border-slate-300 hover:border-brand-500/60 hover:bg-brand-500/5'
            }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-10 h-10 mx-auto mb-4 dark:text-slate-400 text-slate-400" />
          <p className="font-semibold dark:text-white text-slate-800 mb-1">
            {isDragActive ? 'Drop it here…' : 'Drag & drop your file here'}
          </p>
          <p className="text-sm dark:text-slate-400 text-slate-500">
            or click to browse · up to {MAX_MB} MB
          </p>
          <p className="text-xs dark:text-slate-500 text-slate-400 mt-2">
            PDF, DOCX, PNG, MP3, MP4, ZIP, EPUB, JSON and more
          </p>
        </div>
      )}

      {/* Uploading */}
      {phase === 'uploading' && (
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <Loader2 className="w-5 h-5 text-brand-500 animate-spin" />
            <span className="dark:text-slate-300 text-slate-700 text-sm">Uploading…</span>
            <span className="ml-auto text-sm font-mono dark:text-slate-400 text-slate-500">{uploadProgress}%</span>
          </div>
          <div className="h-2 dark:bg-white/10 bg-slate-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-brand-gradient rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Format selection + convert */}
      {phase === 'selecting' && uploadedFile && (
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-4 dark:bg-white/5 bg-slate-100 rounded-xl">
            <FileText className="w-5 h-5 text-brand-400 shrink-0" />
            <div className="min-w-0">
              <p className="text-sm font-medium dark:text-white text-slate-900 truncate">{uploadedFile.original_filename}</p>
              <p className="text-xs dark:text-slate-400 text-slate-500">
                {(uploadedFile.size_bytes / 1024).toFixed(1)} KB · .{uploadedFile.extension}
              </p>
            </div>
            <button onClick={reset} className="ml-auto p-1 dark:hover:bg-white/10 hover:bg-slate-200 rounded-lg transition-colors">
              <X className="w-4 h-4 dark:text-slate-400 text-slate-500" />
            </button>
          </div>

          <div className="flex gap-3">
            <div className="flex-1">
              <label className="block text-xs font-medium dark:text-slate-400 text-slate-600 mb-1.5">
                Convert to
              </label>
              <select
                value={selectedTarget}
                onChange={(e) => setSelectedTarget(e.target.value)}
                className="w-full dark:bg-surface-card bg-white dark:border-white/15 border-slate-300 border
                  rounded-xl px-3 py-2.5 text-sm dark:text-slate-200 text-slate-900
                  focus:outline-none focus:ring-2 focus:ring-brand-500/50"
              >
                {targets.map((t) => (
                  <option key={t} value={t}>.{t.toUpperCase()}</option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <button onClick={handleConvert} className="btn-primary">
                Convert
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Converting */}
      {phase === 'converting' && (
        <div className="flex items-center gap-3 py-4">
          <Loader2 className="w-5 h-5 text-brand-500 animate-spin" />
          <span className="dark:text-slate-300 text-slate-700">Converting to .{selectedTarget}…</span>
        </div>
      )}

      {/* Success */}
      {phase === 'done' && conversion && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-6 h-6 text-green-400" />
            <div>
              <p className="font-semibold dark:text-white text-slate-900">Conversion complete!</p>
              <p className="text-xs dark:text-slate-400 text-slate-500">
                {conversion.output_size_bytes
                  ? `${(conversion.output_size_bytes / 1024).toFixed(1)} KB`
                  : ''} ·  .{conversion.target_format}
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={async () => {
              const token = localStorage.getItem('access_token')
              const res = await fetch(downloadUrl, {
                headers: { Authorization: `Bearer ${token}` }
              })
              const blob = await res.blob()
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              const originalName = uploadedFile.original_filename.replace(/\.[^/.]+$/, '')
              a.href = url
              a.download = `${originalName}.${conversion.target_format}`
              a.click()
              URL.revokeObjectURL(url)
            }}
            className="btn-primary flex items-center gap-2 text-sm"
          >
            <Download className="w-4 h-4" />
            Download .{conversion.target_format.toUpperCase()}
          </button>
            <button onClick={reset} className="btn-ghost text-sm dark:text-slate-300">
              Convert another
            </button>
          </div>
        </div>
      )}

      {/* Error */}
      {(phase === 'error') && (
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
            <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 shrink-0" />
            <p className="text-sm text-red-300">{error}</p>
          </div>
          <button onClick={reset} className="btn-ghost text-sm dark:text-slate-300">
            Try again
          </button>
        </div>
      )}
    </div>
  )
}
