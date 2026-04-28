import { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import logoUrl from '../assets/logo.png'

export default function NavBar() {
  const [isDark, setIsDark] = useState(() => localStorage.getItem('theme') === 'dark')

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }, [isDark])

  const activeClass = "font-bold text-[#8FB78F] border-b-2 border-[#8FB78F] pb-1 no-underline"
  const inactiveClass = "font-medium text-[#2F556B] dark:text-gray-300 pb-1 no-underline transition-colors hover:text-[#8FB78F] dark:hover:text-[#8FB78F]"

  return (
    <nav className="flex items-center justify-between px-8 py-4 bg-white dark:bg-slate-900 shadow-sm sticky top-0 z-50 transition-colors duration-300">
      <div className="flex items-center gap-3">
        <img src={logoUrl} alt="PersonaFit Logo" className="h-[36px] dark:brightness-125 dark:contrast-125 transition-all" />
        <span className="font-extrabold text-xl text-[#2F556B] dark:text-gray-100">
          PersonaFit
        </span>
      </div>
      <div className="flex items-center gap-8">
        <NavLink to="/" className={({ isActive }) => isActive ? activeClass : inactiveClass}>Home</NavLink>
        <NavLink to="/analysis" className={({ isActive }) => isActive ? activeClass : inactiveClass}>Analysis</NavLink>
        <NavLink to="/insights" className={({ isActive }) => isActive ? activeClass : inactiveClass}>Insights</NavLink>
        <NavLink to="/models" className={({ isActive }) => isActive ? activeClass : inactiveClass}>Model Comparison</NavLink>
        <NavLink to="/about" className={({ isActive }) => isActive ? activeClass : inactiveClass}>About</NavLink>
        
        <button 
          onClick={() => setIsDark(!isDark)}
          className="ml-2 p-2 rounded-full bg-[#F5F9F6] dark:bg-slate-800 text-[#2F556B] dark:text-yellow-400 transition-colors hover:bg-[#EBF5EB] dark:hover:bg-slate-700 focus:outline-none flex items-center justify-center shadow-sm"
          title="Toggle Dark Mode"
        >
          {isDark ? '☀️' : '🌙'}
        </button>
      </div>
    </nav>
  )
}
