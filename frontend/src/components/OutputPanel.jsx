import { Copy, Download, FileCode } from 'lucide-react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useToast } from './ToastProvider'
import './OutputPanel.css'

export default function OutputPanel({ result, onDownload }) {
    const toast = useToast()

    if (!result) {
        return (
            <div className="output-panel glass-card output-empty anim-fade-in">
                <div className="empty-icon">
                    <FileCode size={48} strokeWidth={1} />
                </div>
                <p className="empty-title">Your output will appear here</p>
                <p className="empty-sub">Paste code on the left and click Convert</p>
            </div>
        )
    }

    const handleCopy = () => {
        navigator.clipboard.writeText(result.output_code)
        toast('Output copied to clipboard!', 'success')
    }

    const lang = result.type === 'html_to_react' ? 'jsx' : 'plaintext'

    return (
        <div className="output-panel glass-card anim-fade-up">
            {/* Header */}
            <div className="output-header">
                <div className="output-meta">
                    <span className={`badge ${result.type === 'html_to_react' ? 'badge-react' : 'badge-tailwind'}`}>
                        {result.type === 'html_to_react' ? 'React JSX' : 'Tailwind CSS'}
                    </span>
                    <span className="output-filename code-font">{result.filename}</span>
                </div>
                <div className="output-actions">
                    <button className="btn-secondary" onClick={handleCopy}>
                        <Copy size={13} />
                        Copy
                    </button>
                    <button className="btn-primary" onClick={onDownload} style={{ padding: '8px 16px', fontSize: '13px' }}>
                        <Download size={13} />
                        Download
                    </button>
                </div>
            </div>

            {/* Stats row */}
            <div className="output-stats">
                <span>📄 {result.output_code.split('\n').length} lines</span>
                <span>💾 {(result.output_code.length / 1024).toFixed(1)} KB</span>
                <span>🗂 {result.output_format}</span>
                <span>🕒 {new Date(result.created_at).toLocaleTimeString()}</span>
            </div>

            {/* Highlighted code */}
            <div className="output-code">
                <SyntaxHighlighter
                    language={lang}
                    style={vscDarkPlus}
                    customStyle={{
                        margin: 0,
                        background: 'transparent',
                        fontSize: '12.5px',
                        lineHeight: '1.65',
                        fontFamily: "'JetBrains Mono', monospace",
                    }}
                    showLineNumbers
                    lineNumberStyle={{
                        color: 'rgba(148,163,184,0.3)',
                        fontSize: '11px',
                        minWidth: '36px',
                        paddingRight: '12px',
                    }}
                >
                    {result.output_code}
                </SyntaxHighlighter>
            </div>
        </div>
    )
}
