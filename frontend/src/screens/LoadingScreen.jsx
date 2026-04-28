import { motion } from 'framer-motion'
import logoUrl from '../assets/logo.png'

const dots = [0, 1, 2]

export default function LoadingScreen() {
  return (
    <motion.div
      key="loading"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '2rem',
      }}
      className="bg-[#F5F9F6] dark:bg-[#0F172A] transition-colors duration-300"
    >
      {/* Pulsing icon */}
      <motion.div
        animate={{ scale: [1, 1.15, 1] }}
        transition={{ duration: 1.6, repeat: Infinity, ease: 'easeInOut' }}
      >
        <img src={logoUrl} alt="Loading" className="h-[80px] dark:brightness-125 dark:contrast-125 transition-all" />
      </motion.div>

      {/* Dots */}
      <div style={{ display: 'flex', gap: '0.6rem' }}>
        {dots.map(i => (
          <motion.div
            key={i}
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 0.7, repeat: Infinity, delay: i * 0.15 }}
            style={{
              width: 10,
              height: 10,
              borderRadius: '50%',
              background: '#8FB78F',
            }}
          />
        ))}
      </div>

      <p style={{ color: '#8AAAB8', fontSize: '1rem', fontWeight: 500 }}>
        Analysing your lifestyle…
      </p>
    </motion.div>
  )
}
