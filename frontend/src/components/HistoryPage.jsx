import { useState, useEffect } from 'react'
import { History, Trash2, Download, Search, RefreshCw, Code2, Palette } from 'lucide-react'
import { fetchHistory, deleteHistory, downloadFile } from '../api/client'
import { useToast } from './ToastProvider'
import './HistoryPage.css'

const TYPE_LABELS = {
    html_to_react: { label: 'HTML → React', cls: 'badge-react' },
    css_to_tailwind: { label: 'CSS → Tailwind', cls: 'badge-tailwind' },
}

const FORMAT_LABELS = {
    single: 'Single',
    merged: 'Merged',
    zip: 'ZIP',
}

export default function HistoryPage() {
    const toast = useToast()
    const [records, setRecords] = useState([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')
    const [deleting, setDeleting] = useState(null)
    const [expanded, setExpanded] = useState(null)

    const load = async () => {
        setLoading(true)
        try {
            const res = await fetchHistory()
            setRecords(res.data)
        } catch {
            toast('Failed to load history. Is the backend running?', 'error')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { load() }, [])

    const handleDelete = async (id) => {
        setDeleting(id)
        try {
            await deleteHistory(id)
            setRecords(prev => prev.filter(r => r.id !== id))
            toast('Record deleted', 'success')
        } catch {
            toast('Delete failed', 'error')
        } finally {
            setDeleting(null)
        }
    }

    const handleDownload = (record) => {
        const blob = new Blob([record.output_code], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = record.filename || `output_${record.id}.txt`
        a.click()
        URL.revokeObjectURL(url)
        toast(`Downloaded ${record.filename}`, 'success')
    }

    const filtered = records.filter(r =>
        r.filename?.toLowerCase().includes(search.toLowerCase()) ||
        r.type?.includes(search.toLowerCase()) ||
        r.input_code?.toLowerCase().includes(search.toLowerCase())
    )

    const formatDate = (iso) => {
        const d = new Date(iso)
        return d.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
    }

    return (
        <div className="history-page page-container">
            {/* Header */}
            <div className="history-header anim-fade-up">
                <div className="history-title-row">
                    <div className="history-icon"><History size={22} /></div>
                    <div>
                        <h1 className="history-title">Conversion <span className="gradient-text">History</span></h1>
                        <p className="history-sub">{records.length} conversions stored in the database</p>
                    </div>
                </div>
                <div className="history-controls">
                    <div className="search-box">
                        <Search size={14} />
                        <input
                            placeholder="Search by name or type…"
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                        />
                    </div>
                    <button className="btn-secondary" onClick={load} disabled={loading}>
                        <RefreshCw size={13} className={loading ? 'spinning' : ''} />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Table / Grid */}
            {loading ? (
                <div className="history-loading anim-fade-in">
                    <div className="spinner" style={{ width: 32, height: 32, borderWidth: 3 }} />
                    <span>Loading history…</span>
                </div>
            ) : filtered.length === 0 ? (
                <div className="history-empty glass-card anim-fade-up">
                    <History size={48} strokeWidth={1} style={{ color: 'var(--text-muted)', opacity: 0.4 }} />
                    <p style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>
                        {records.length === 0 ? 'No conversions yet' : 'No results match your search'}
                    </p>
                    <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
                        {records.length === 0 ? 'Run your first conversion to see it here.' : 'Try a different search term.'}
                    </p>
                </div>
            ) : (
                <div className="history-list anim-fade-up">
                    {filtered.map((r, idx) => (
                        <div
                            key={r.id}
                            className={`history-card glass-card ${expanded === r.id ? 'expanded' : ''}`}
                            style={{ animationDelay: `${idx * 0.03}s` }}
                        >
                            <div className="history-card-main" onClick={() => setExpanded(expanded === r.id ? null : r.id)}>
                                {/* Type icon */}
                                <div className={`history-type-icon ${r.type === 'html_to_react' ? 'icon-react' : 'icon-tailwind'}`}>
                                    {r.type === 'html_to_react' ? <Code2 size={16} /> : <Palette size={16} />}
                                </div>

                                {/* Info */}
                                <div className="history-info">
                                    <div className="history-name code-font">{r.filename || `output_${r.id}`}</div>
                                    <div className="history-meta">
                                        <span className={`badge ${TYPE_LABELS[r.type]?.cls}`}>{TYPE_LABELS[r.type]?.label}</span>
                                        <span className={`badge badge-zip`}>{FORMAT_LABELS[r.output_format]}</span>
                                        <span className="history-date">{formatDate(r.created_at)}</span>
                                    </div>
                                </div>

                                {/* Stats */}
                                <div className="history-stats">
                                    <span>{r.input_code?.split('\n').length} lines in</span>
                                    <span>{r.output_code?.split('\n').length} lines out</span>
                                </div>

                                {/* Actions */}
                                <div className="history-actions" onClick={e => e.stopPropagation()}>
                                    <button
                                        className="btn-secondary tooltip-wrapper"
                                        data-tip="Download"
                                        onClick={() => handleDownload(r)}
                                    >
                                        <Download size={13} />
                                    </button>
                                    <button
                                        className="btn-secondary danger tooltip-wrapper"
                                        data-tip="Delete"
                                        onClick={() => handleDelete(r.id)}
                                        disabled={deleting === r.id}
                                    >
                                        {deleting === r.id ? <span className="spinner" style={{ width: 13, height: 13 }} /> : <Trash2 size={13} />}
                                    </button>
                                </div>
                            </div>

                            {/* Expanded preview */}
                            {expanded === r.id && (
                                <div className="history-preview anim-fade-in">
                                    <div className="preview-row">
                                        <div className="preview-pane">
                                            <div className="preview-label">Input</div>
                                            <pre className="preview-code code-font">{r.input_code?.slice(0, 800)}{r.input_code?.length > 800 ? '\n…' : ''}</pre>
                                        </div>
                                        <div className="preview-pane">
                                            <div className="preview-label">Output</div>
                                            <pre className="preview-code code-font">{r.output_code?.slice(0, 800)}{r.output_code?.length > 800 ? '\n…' : ''}</pre>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
