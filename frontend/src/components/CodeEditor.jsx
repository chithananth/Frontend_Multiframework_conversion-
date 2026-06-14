import { useRef, useEffect } from 'react'
import { Copy, Trash2 } from 'lucide-react'
import { useToast } from './ToastProvider'
import './CodeEditor.css'

const PLACEHOLDERS = {
    html_to_react: `<!-- Paste your HTML here -->
<div class="container">
  <header>
    <h1>Hello World</h1>
    <p class="subtitle">Welcome to my page</p>
  </header>
  <main>
    <button class="btn" onclick="handleClick()">Click Me</button>
    <img src="logo.png" alt="Logo" />
  </main>
</div>`,
    css_to_tailwind: `/* Paste your CSS here */
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  margin: 0 auto;
  max-width: 800px;
}

.btn {
  background-color: blue;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 700;
  cursor: pointer;
}`,
}

export default function CodeEditor({ value, onChange, convType }) {
    const toast = useToast()
    const textareaRef = useRef(null)

    // Handle tabs inside textarea
    const handleKeyDown = (e) => {
        if (e.key === 'Tab') {
            e.preventDefault()
            const s = e.target.selectionStart
            const e2 = e.target.selectionEnd
            const newVal = value.substring(0, s) + '  ' + value.substring(e2)
            onChange(newVal)
            setTimeout(() => {
                textareaRef.current.selectionStart = s + 2
                textareaRef.current.selectionEnd = s + 2
            }, 0)
        }
    }

    const handleCopy = () => {
        if (!value.trim()) return
        navigator.clipboard.writeText(value)
        toast('Code copied to clipboard!', 'success')
    }

    const handleClear = () => {
        onChange('')
        textareaRef.current?.focus()
    }

    useEffect(() => {
        // Auto-resize
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto'
            textareaRef.current.style.height = Math.max(300, textareaRef.current.scrollHeight) + 'px'
        }
    }, [value])

    const lineCount = value ? value.split('\n').length : 1

    return (
        <div className="code-editor glass-card">
            {/* Header */}
            <div className="editor-header">
                <div className="editor-title">
                    <span className="editor-dot red" />
                    <span className="editor-dot yellow" />
                    <span className="editor-dot green" />
                    <span className="editor-lang-badge">
                        {convType === 'html_to_react' ? 'HTML' : 'CSS'}
                    </span>
                </div>
                <div className="editor-actions">
                    <button className="btn-secondary tooltip-wrapper" data-tip="Copy" onClick={handleCopy}>
                        <Copy size={14} />
                    </button>
                    <button className="btn-secondary tooltip-wrapper" data-tip="Clear" onClick={handleClear}>
                        <Trash2 size={14} />
                    </button>
                </div>
            </div>

            {/* Body: line numbers + textarea */}
            <div className="editor-body">
                <div className="line-numbers" aria-hidden>
                    {Array.from({ length: Math.max(lineCount, 12) }, (_, i) => (
                        <span key={i}>{i + 1}</span>
                    ))}
                </div>
                <textarea
                    ref={textareaRef}
                    className="code-textarea code-font"
                    value={value}
                    onChange={e => onChange(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={PLACEHOLDERS[convType]}
                    spellCheck={false}
                    autoCapitalize="off"
                    autoCorrect="off"
                />
            </div>

            <div className="editor-footer">
                <span>{value.split('\n').length} lines</span>
                <span>{value.length} chars</span>
            </div>
        </div>
    )
}
