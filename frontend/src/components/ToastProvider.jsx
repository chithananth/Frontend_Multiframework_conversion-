import { createContext, useContext, useState, useCallback } from 'react'
import { CheckCircle, XCircle, Info, X } from 'lucide-react'

const ToastContext = createContext(null)

export function useToast() {
    return useContext(ToastContext)
}

export default function ToastProvider({ children }) {
    const [toasts, setToasts] = useState([])

    const addToast = useCallback((message, type = 'info') => {
        const id = Date.now()
        setToasts(prev => [...prev, { id, message, type }])
        setTimeout(() => {
            setToasts(prev => prev.filter(t => t.id !== id))
        }, 3500)
    }, [])

    const removeToast = (id) => setToasts(prev => prev.filter(t => t.id !== id))

    const ICONS = {
        success: <CheckCircle size={16} />,
        error: <XCircle size={16} />,
        info: <Info size={16} />,
    }

    return (
        <ToastContext.Provider value={addToast}>
            {children}
            <div className="toast-container">
                {toasts.map(t => (
                    <div key={t.id} className={`toast toast-${t.type} anim-slide-in`}>
                        {ICONS[t.type]}
                        <span>{t.message}</span>
                        <button
                            onClick={() => removeToast(t.id)}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', marginLeft: 'auto', padding: 0 }}
                        >
                            <X size={14} />
                        </button>
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    )
}
