import { useState } from 'react'
import API_URL from './config/api'
import { BrowserRouter, Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import NavBar from './components/NavBar'
import WelcomeScreen from './screens/WelcomeScreen'
import InputScreen from './screens/InputScreen'
import LoadingScreen from './screens/LoadingScreen'
import ResultScreen from './screens/ResultScreen'
import ModelComparisonScreen from './screens/ModelComparisonScreen'
import AboutScreen from './screens/AboutScreen'

const DEFAULT_INPUTS = {
  age: 35,
  bmi: 24.0,
  activity_level: 5,
  diet_score: 5,
  sleep_hours: 7,
  smoking_status: 0,
}

function AnimatedRoutes({ isLoading, inputs, result, handleAnalyse, handleRestart }) {
  const location = useLocation()
  const navigate = useNavigate()

  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<WelcomeScreen onStart={() => navigate('/analysis')} />} />
        <Route path="/analysis" element={<InputScreen defaults={inputs} onAnalyse={handleAnalyse} onBack={() => navigate('/')} />} />
        <Route path="/insights" element={
          result ? <ResultScreen result={result} onRestart={handleRestart} /> : 
          <div className="p-16 text-center text-[#5A8A9F] dark:text-slate-400 text-lg transition-colors duration-300">
            No analysis results yet. Please complete the <button onClick={() => navigate('/analysis')} className="text-[#8FB78F] font-bold underline bg-transparent border-none cursor-pointer text-inherit p-0">analysis</button> first.
          </div>
        } />
        <Route path="/models" element={<ModelComparisonScreen />} />
        <Route path="/about" element={<AboutScreen />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  )
}

function MainApp() {
  const [inputs, setInputs] = useState(DEFAULT_INPUTS)
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  async function handleAnalyse(finalInputs) {
    setInputs(finalInputs)
    setIsLoading(true)
    try {
      const res = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(finalInputs),
      })
      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`)
      }
      const data = await res.json()
      setResult({ ...data, inputs: finalInputs })
      setIsLoading(false)
      navigate('/insights')
    } catch {
      alert('Unable to fetch prediction. Please try again.')
      setIsLoading(false)
    }
  }

  function handleRestart() {
    setResult(null)
    setInputs(DEFAULT_INPUTS)
    navigate('/analysis')
  }

  return (
    <div className="min-h-screen bg-[#F5F9F6] dark:bg-[#0F172A] flex flex-col transition-colors duration-300 text-[#2F556B] dark:text-gray-100">
      <NavBar />
      <div className="flex-1 relative">
        <AnimatedRoutes 
          isLoading={isLoading} 
          inputs={inputs} 
          result={result} 
          handleAnalyse={handleAnalyse} 
          handleRestart={handleRestart} 
        />
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <MainApp />
    </BrowserRouter>
  )
}
