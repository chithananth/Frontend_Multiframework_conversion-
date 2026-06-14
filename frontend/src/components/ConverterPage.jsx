import { useState, useRef } from 'react'
import { ArrowRight, Sparkles, Code2, Palette, FileArchive, Upload, X, File } from 'lucide-react'
import CodeEditor from './CodeEditor'
import OutputPanel from './OutputPanel'
import { convertCode } from '../api/client'
import { useToast } from './ToastProvider'
import './ConverterPage.css'
import axios from 'axios'

const CONV_TYPES = [
    { id: 'html_to_react', label: 'HTML → React', icon: <Code2 size={15} />, color: 'cyan' },
    { id: 'css_to_tailwind', label: 'CSS → Tailwind', icon: <Palette size={15} />, color: 'green' },
]

const OUTPUT_FORMATS = [
    { id: 'single', label: 'Single File', desc: 'One clean component file' },
    { id: 'merged', label: 'Merged File', desc: 'All code in one file' },
    { id: 'zip', label: 'ZIP Archive', desc: 'Upload & convert multiple files' },
]

export default function ConverterPage() {
    const toast = useToast()
    const [convType, setConvType] = useState('html_to_react')
    const [outputFormat, setOutputFormat] = useState('single')
    const [inputCode, setInputCode] = useState('')
    const [componentName, setComponentName] = useState('MyComponent')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)

    // ZIP multi-file upload state
    const [uploadedFiles, setUploadedFiles] = useState([])
    const [dragOver, setDragOver] = useState(false)
    const fileInputRef = useRef(null)

    const isZipMode = outputFormat === 'zip'

    // ── File upload handlers ──────────────────────────────────────────────
    const handleFileSelect = (e) => {
        const newFiles = Array.from(e.target.files)
        setUploadedFiles(prev => [...prev, ...newFiles])
        e.target.value = '' // Reset so same file can be selected again
    }

    const handleDrop = (e) => {
        e.preventDefault()
        setDragOver(false)
        const newFiles = Array.from(e.dataTransfer.files)
        setUploadedFiles(prev => [...prev, ...newFiles])
    }

    const handleDragOver = (e) => {
        e.preventDefault()
        setDragOver(true)
    }

    const handleDragLeave = (e) => {
        e.preventDefault()
        setDragOver(false)
    }

    const removeFile = (index) => {
        setUploadedFiles(prev => prev.filter((_, i) => i !== index))
    }

    const clearAllFiles = () => {
        setUploadedFiles([])
    }

    const getFileIcon = (name) => {
        const ext = name.split('.').pop().toLowerCase()
        if (ext === 'html' || ext === 'htm') return '🌐'
        if (ext === 'css') return '🎨'
        if (ext === 'js' || ext === 'jsx') return '⚡'
        if (ext === 'zip') return '📦'
        return '📄'
    }

    const formatFileSize = (bytes) => {
        if (bytes < 1024) return bytes + ' B'
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    }

    // ── Convert handler ────────────────────────────────────────────────────
    const handleConvert = async () => {
        if (isZipMode) {
            // ZIP mode: multi-file upload
            if (uploadedFiles.length === 0) {
                toast('Please upload files to convert!', 'error')
                return
            }
            setLoading(true)
            try {
                const formData = new FormData()
                formData.append('type', convType)
                uploadedFiles.forEach(f => formData.append('files', f))

                const response = await axios.post('/api/convert-zip', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' },
                    responseType: 'blob',
                })

                const contentDisposition = response.headers['content-disposition'] || ''
                const match = contentDisposition.match(/filename="?([^"]+)"?/)
                const filename = match ? match[1] : 'converted_files.zip'
                const url = URL.createObjectURL(new Blob([response.data], { type: 'application/zip' }))
                const a = document.createElement('a')
                a.href = url; a.download = filename; a.click()
                URL.revokeObjectURL(url)
                toast(`ZIP downloaded with ${uploadedFiles.length} converted file(s)! 🎉`, 'success')
                setResult(null)
            } catch (err) {
                let msg = 'Conversion failed. Is the backend running?'
                if (err.response?.data) {
                    try {
                        const text = await err.response.data.text()
                        const parsed = JSON.parse(text)
                        msg = parsed.error || msg
                    } catch { }
                }
                toast(msg, 'error')
            } finally {
                setLoading(false)
            }
        } else {
            // Single / Merged mode: text input (unchanged)
            if (!inputCode.trim()) {
                toast('Please enter some code to convert!', 'error')
                return
            }
            setLoading(true)
            try {
                const response = await convertCode({
                    type: convType,
                    input_code: inputCode,
                    output_format: outputFormat,
                    component_name: componentName,
                })
                setResult(response.data)
                toast('Conversion successful! 🎉', 'success')
            } catch (err) {
                const msg = err.response?.data?.error || 'Conversion failed. Is the backend running?'
                toast(msg, 'error')
            } finally {
                setLoading(false)
            }
        }
    }

    const handleDownload = () => {
        if (!result) return
        const blob = new Blob([result.output_code], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = result.filename || 'output.txt'
        a.click()
        URL.revokeObjectURL(url)
        toast(`Downloaded ${result.filename}`, 'success')
    }

    return (
        <div className="converter-page page-container">
            {/* Hero */}
            <div className="hero anim-fade-up">
                <div className="hero-badge">
                    <Sparkles size={12} />
                    Powered by AI-grade transformations
                </div>
                <h1 className="hero-title">
                    <span className="gradient-text">Frontend Framework</span>
                    <br />Converter
                </h1>
                <p className="hero-sub">
                    Transform your HTML & CSS into modern React components
                    and Tailwind CSS utility classes — instantly.
                </p>
            </div>

            {/* Options Panel */}
            <div className="options-card glass-card anim-fade-up" style={{ animationDelay: '0.1s' }}>
                {/* Conversion type */}
                <div className="options-row">
                    <div>
                        <p className="section-label">Conversion Type</p>
                        <div className="tab-group">
                            {CONV_TYPES.map(ct => (
                                <button
                                    key={ct.id}
                                    className={`tab-btn ${convType === ct.id ? 'active' : ''}`}
                                    onClick={() => { setConvType(ct.id); setResult(null) }}
                                >
                                    {ct.icon}
                                    {ct.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Output format */}
                    <div>
                        <p className="section-label">Output Format</p>
                        <div className="format-cards">
                            {OUTPUT_FORMATS.map(f => (
                                <button
                                    key={f.id}
                                    className={`format-card ${outputFormat === f.id ? 'active' : ''}`}
                                    onClick={() => { setOutputFormat(f.id); setResult(null) }}
                                >
                                    {f.id === 'zip' && <FileArchive size={14} />}
                                    <div>
                                        <div className="format-label">{f.label}</div>
                                        <div className="format-desc">{f.desc}</div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Component name (only for HTML→React in single/merged mode) */}
                    {convType === 'html_to_react' && !isZipMode && (
                        <div>
                            <p className="section-label">Component Name</p>
                            <input
                                className="comp-name-input code-font"
                                value={componentName}
                                onChange={e => setComponentName(e.target.value)}
                                placeholder="MyComponent"
                                spellCheck={false}
                            />
                        </div>
                    )}
                </div>

                {/* Convert button */}
                <button
                    className="btn-primary convert-btn anim-pulse"
                    onClick={handleConvert}
                    disabled={loading}
                >
                    {loading ? (
                        <><span className="spinner" /> Converting…</>
                    ) : (
                        <><ArrowRight size={16} /> Convert Now</>
                    )}
                </button>
            </div>

            {/* Editor + Output Panes */}
            <div className="editor-grid">
                <div className="editor-col anim-slide-in" style={{ animationDelay: '0.2s' }}>
                    <div className="col-label">{isZipMode ? 'Upload Files' : 'Input'}</div>

                    {isZipMode ? (
                        /* ── ZIP Upload Zone ────────────────────────────── */
                        <div className="glass-card upload-zone-wrapper">
                            {/* Drop zone */}
                            <div
                                className={`upload-dropzone ${dragOver ? 'drag-over' : ''}`}
                                onDrop={handleDrop}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    multiple
                                    accept=".html,.htm,.css,.js,.jsx,.zip"
                                    onChange={handleFileSelect}
                                    style={{ display: 'none' }}
                                />
                                <div className="upload-icon">
                                    <Upload size={32} strokeWidth={1.5} />
                                </div>
                                <p className="upload-title">
                                    Drag & drop files here, or <span className="upload-link">browse</span>
                                </p>
                                <p className="upload-sub">
                                    Supports .html, .css, .js, .jsx, and .zip files
                                </p>
                            </div>

                            {/* File list */}
                            {uploadedFiles.length > 0 && (
                                <div className="upload-file-list">
                                    <div className="upload-list-header">
                                        <span className="upload-count">
                                            {uploadedFiles.length} file{uploadedFiles.length > 1 ? 's' : ''} selected
                                        </span>
                                        <button className="btn-secondary" onClick={clearAllFiles} style={{ fontSize: 11, padding: '4px 10px' }}>
                                            <X size={12} /> Clear All
                                        </button>
                                    </div>
                                    <div className="upload-files">
                                        {uploadedFiles.map((f, i) => (
                                            <div key={i} className="upload-file-item anim-fade-up" style={{ animationDelay: `${i * 0.04}s` }}>
                                                <span className="file-icon">{getFileIcon(f.name)}</span>
                                                <div className="file-info">
                                                    <span className="file-name code-font">{f.name}</span>
                                                    <span className="file-size">{formatFileSize(f.size)}</span>
                                                </div>
                                                <button className="file-remove" onClick={() => removeFile(i)} title="Remove">
                                                    <X size={14} />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        /* ── Normal Code Editor (single / merged) ──────── */
                        <CodeEditor
                            value={inputCode}
                            onChange={setInputCode}
                            convType={convType}
                        />
                    )}
                </div>

                <div className="editor-divider">
                    <div className="divider-arrow">
                        <ArrowRight size={20} color="var(--accent-primary)" />
                    </div>
                </div>

                <div className="editor-col anim-fade-up" style={{ animationDelay: '0.25s' }}>
                    <div className="col-label">Output</div>
                    {isZipMode ? (
                        <div className="output-panel glass-card output-empty anim-fade-in">
                            <div className="empty-icon">
                                <FileArchive size={48} strokeWidth={1} />
                            </div>
                            <p className="empty-title">ZIP output will auto-download</p>
                            <p className="empty-sub">
                                Upload files on the left, click Convert Now, and your converted ZIP will download automatically.
                            </p>
                            {uploadedFiles.length > 0 && (
                                <p style={{ color: 'var(--accent-primary)', fontSize: 13, marginTop: 8, fontWeight: 600 }}>
                                    ✅ {uploadedFiles.length} file{uploadedFiles.length > 1 ? 's' : ''} ready to convert
                                </p>
                            )}
                        </div>
                    ) : (
                        <OutputPanel result={result} onDownload={handleDownload} />
                    )}
                </div>
            </div>
        </div>
    )
}
