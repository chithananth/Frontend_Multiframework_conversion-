import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import ConverterPage from './components/ConverterPage'
import HistoryPage from './components/HistoryPage'
import ToastProvider from './components/ToastProvider'

function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <div style={{ minHeight: '100vh', position: 'relative', zIndex: 1 }}>
          <Navbar />
          <Routes>
            <Route path="/" element={<ConverterPage />} />
            <Route path="/history" element={<HistoryPage />} />
          </Routes>
        </div>
      </ToastProvider>
    </BrowserRouter>
  )
}

export default App
