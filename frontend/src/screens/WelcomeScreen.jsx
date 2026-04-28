import { motion } from 'framer-motion'
import logoUrl from '../assets/logo.png'

const leaves = [
  { top: '10%', left: '8%', size: 80, rotate: -20, delay: 0 },
  { top: '20%', right: '6%', size: 60, rotate: 15, delay: 0.2 },
  { bottom: '18%', left: '5%', size: 70, rotate: 30, delay: 0.4 },
  { bottom: '10%', right: '10%', size: 50, rotate: -10, delay: 0.1 },
  { top: '50%', right: '3%', size: 40, rotate: 45, delay: 0.3 },
]

function Leaf({ top, left, right, bottom, size, rotate, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.4 }}
      animate={{ opacity: 0.18, scale: 1 }}
      transition={{ delay, duration: 1.2, ease: 'easeOut' }}
      style={{ position: 'absolute', top, left, right, bottom }}
    >
      <svg width={size} height={size} viewBox="0 0 80 80" fill="none" style={{ transform: `rotate(${rotate}deg)` }}>
        <path d="M40 4C20 4 4 20 4 40C4 60 20 76 40 76C60 76 76 60 76 40C76 20 60 4 40 4Z"
          fill="#8FB78F" />
        <path d="M40 4C40 4 60 30 40 76" stroke="#F5F9F6" strokeWidth="2" strokeLinecap="round" />
      </svg>
    </motion.div>
  )
}

export default function WelcomeScreen({ onStart }) {
  return (
    <motion.div
      key="welcome"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5 }}
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        overflow: 'hidden',
        padding: '2rem',
      }}
      className="bg-[#F5F9F6] dark:bg-[#0F172A] transition-colors duration-300"
    >
      {/* Decorative leaves */}
      {leaves.map((l, i) => <Leaf key={i} {...l} />)}

      {/* Content */}
      <motion.div
        initial={{ opacity: 0, y: 32 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.8, ease: 'easeOut' }}
        style={{ textAlign: 'center', maxWidth: 480, zIndex: 1 }}
      >
        {/* Icon */}
        <motion.div
          animate={{ y: [0, -8, 0] }}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
          style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'center' }}
        >
          <img src={logoUrl} alt="PersonaFit Logo" className="h-[100px] dark:brightness-125 dark:contrast-125 transition-all" />
        </motion.div>

        <h1 style={{
          fontSize: 'clamp(2.8rem, 8vw, 4rem)',
          fontWeight: 800,
          color: '#2F556B',
          margin: '0 0 0.75rem',
          letterSpacing: '-0.02em',
          lineHeight: 1.1,
        }}>
          PersonaFit
        </h1>

        <p style={{
          fontSize: '1.15rem',
          color: '#5A8A9F',
          marginBottom: '2.5rem',
          lineHeight: 1.6,
          fontWeight: 400,
        }}>
          Understand your lifestyle<br />and improve your health
        </p>

        {/* Stats pills */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '0.75rem', marginBottom: '2.5rem', flexWrap: 'wrap' }}>
          {[['🔬', '4 ML Models'], ['⚡', 'Instant Analysis'], ['🎯', 'Personalised Tips']].map(([icon, label]) => (
            <span key={label} style={{
              background: 'white',
              border: '1px solid #D6E8D6',
              borderRadius: '999px',
              padding: '0.4rem 1rem',
              fontSize: '0.82rem',
              color: '#5A8A9F',
              fontWeight: 500,
              boxShadow: '0 2px 8px rgba(143,183,143,0.12)',
            }}>
              {icon} {label}
            </span>
          ))}
        </div>

        <motion.button
          whileHover={{ scale: 1.04, boxShadow: '0 8px 30px rgba(143,183,143,0.45)' }}
          whileTap={{ scale: 0.97 }}
          onClick={onStart}
          style={{
            background: 'linear-gradient(135deg, #8FB78F, #6FA86F)',
            color: 'white',
            border: 'none',
            borderRadius: '999px',
            padding: '1rem 2.8rem',
            fontSize: '1.1rem',
            fontWeight: 700,
            cursor: 'pointer',
            boxShadow: '0 4px 20px rgba(143,183,143,0.35)',
            letterSpacing: '0.01em',
          }}
        >
          Start My Analysis →
        </motion.button>

        <p style={{ marginTop: '1.2rem', fontSize: '0.78rem', color: '#9BBAC6' }}>
          Takes less than 60 seconds · For educational purposes only
        </p>
      </motion.div>
    </motion.div>
  )
}
