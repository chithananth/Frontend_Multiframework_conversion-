import { NavLink } from 'react-router-dom'
import { Code2, History, Zap } from 'lucide-react'
import './Navbar.css'

export default function Navbar() {
    return (
        <header className="navbar">
            <div className="page-container navbar-inner">
                {/* Logo */}
                <NavLink to="/" className="navbar-logo">
                    <div className="logo-icon">
                        <Zap size={18} strokeWidth={2.5} />
                    </div>
                    <div className="logo-text">
                        <span className="gradient-text">FFC</span>
                        <span className="logo-sub">Framework Converter</span>
                    </div>
                </NavLink>

                {/* Center tag */}
                <div className="navbar-center">
                    <span className="badge badge-react">HTML → React</span>
                    <span className="badge badge-tailwind">CSS → Tailwind</span>
                </div>

                {/* Nav links */}
                <nav className="navbar-links">
                    <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                        <Code2 size={15} />
                        Converter
                    </NavLink>
                    <NavLink to="/history" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                        <History size={15} />
                        History
                    </NavLink>
                </nav>
            </div>
        </header>
    )
}
