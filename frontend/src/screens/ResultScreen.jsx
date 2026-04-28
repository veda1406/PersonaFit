import { motion } from 'framer-motion'
import ImprovementSection from '../components/ImprovementSection'
import RecommendationCards from '../components/RecommendationCards'
import FactorBar from '../components/FactorBar'

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12 } },
}
const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.45 } },
}

export default function ResultScreen({ result, onRestart }) {
  const { risk_level, risk_friendly, risk_description, risk_color, confidence, top_factors, inputs, probabilities } = result

  // Health Score derived from probability of low risk (0-100)
  const healthScore = Math.round(probabilities.low)

  return (
    <motion.div
      key="result"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
      className="min-h-screen bg-[#F5F9F6] dark:bg-[#0F172A] py-12 transition-colors duration-300"
    >
      <div className="max-w-4xl mx-auto px-6 space-y-12">
        
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="space-y-12"
        >
          {/* ── Risk Hero ── */}
          <motion.div variants={item} className="text-center pt-8 pb-4 flex flex-col items-center">
            
            <div className="relative mb-8">
              <motion.div
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                className="w-44 h-44 rounded-full flex flex-col items-center justify-center relative z-10"
                style={{
                  background: `${risk_color}1A`,
                  border: `4px solid ${risk_color}4D`,
                  boxShadow: `0 0 40px ${risk_color}26`,
                }}
              >
                <div className="flex items-baseline gap-1 mt-3">
                  <span className="text-6xl font-bold text-[#2F556B] dark:text-gray-100">{healthScore}</span>
                  <span className="text-xl font-semibold text-[#5A7A8A] dark:text-slate-400">/100</span>
                </div>
                <span className="text-xs font-bold uppercase tracking-widest text-[#5A7A8A] dark:text-slate-400 mt-1">Your Health Score</span>
              </motion.div>
            </div>

            <h2 className="text-4xl font-semibold text-[#2F556B] dark:text-gray-100 mb-4 tracking-tight">
              {risk_friendly}
            </h2>
            <p className="text-lg text-[#8AAAB8] dark:text-slate-400 mb-8 max-w-2xl mx-auto leading-relaxed">
              {risk_description}
            </p>

            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.4, type: 'spring', stiffness: 200 }}
              className="inline-block rounded-full px-8 py-3 text-sm font-bold text-white shadow-lg tracking-wide"
              style={{ background: risk_color, boxShadow: `0 4px 16px ${risk_color}55` }}
            >
              {risk_level === 0 ? 'Low Risk' : risk_level === 1 ? 'Medium Risk' : 'High Risk'} ({confidence}% Confidence)
            </motion.div>
          </motion.div>

          {/* ── Probability bars ── */}
          <motion.div variants={item} className="bg-white dark:bg-slate-800 rounded-2xl p-10 shadow-lg transition-transform duration-300 hover:scale-[1.01] border border-transparent dark:border-slate-700">
            <h3 className="text-2xl font-semibold text-[#2F556B] dark:text-gray-100 mb-8 tracking-wide">
              Risk Breakdown
            </h3>
            <div className="space-y-6">
              {[
                { label: 'Low Risk', value: probabilities.low, color: '#8FB78F' },
                { label: 'Medium Risk', value: probabilities.medium, color: '#D98CA1' },
                { label: 'High Risk', value: probabilities.high, color: '#E9B18A' },
              ].map(({ label, value, color }) => (
                <div key={label}>
                  <div className="flex justify-between mb-2">
                    <span className="text-base text-[#5A7A8A] dark:text-slate-400 font-medium">{label}</span>
                    <span className="text-base font-bold" style={{ color }}>{value}%</span>
                  </div>
                  <div className="h-4 bg-[#F0F5F0] dark:bg-slate-700 rounded-full overflow-hidden shadow-inner">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${value}%` }}
                      transition={{ delay: 0.5, duration: 0.8, ease: 'easeOut' }}
                      className="h-full rounded-full"
                      style={{ background: color }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* ── Top Factors ── */}
          <motion.div variants={item} className="bg-white dark:bg-slate-800 rounded-2xl p-10 shadow-lg transition-transform duration-300 hover:scale-[1.01] border border-transparent dark:border-slate-700">
            <h3 className="text-2xl font-semibold text-[#2F556B] dark:text-gray-100 mb-3 tracking-wide">
              Why this result?
            </h3>
            <p className="text-base text-[#8AAAB8] dark:text-slate-400 mb-8">
              These factors had the biggest influence on your health score.
            </p>
            <div className="space-y-8">
              {top_factors.map((f, i) => (
                <FactorBar key={f.name} factor={f} index={i} />
              ))}
            </div>
          </motion.div>

          {/* ── Improvement Simulator ── */}
          <motion.div variants={item}>
            <ImprovementSection inputs={inputs} currentResult={result} />
          </motion.div>

          {/* ── Recommendations ── */}
          <motion.div variants={item}>
            <RecommendationCards inputs={inputs} />
          </motion.div>

          {/* ── Restart ── */}
          <motion.div variants={item} className="text-center pt-8 pb-16">
            <button
              onClick={onRestart}
              className="bg-transparent border-2 border-[#D6E8D6] dark:border-slate-600 rounded-full px-10 py-3.5 text-[#8AAAB8] dark:text-slate-300 text-base font-bold cursor-pointer hover:bg-white dark:hover:bg-slate-800 transition-colors shadow-sm"
            >
              ← Start Over
            </button>
            <p className="text-xs text-[#AABFC8] dark:text-slate-500 mt-6 font-medium tracking-wide uppercase">
              For educational purposes only · Not medical advice
            </p>
          </motion.div>
        </motion.div>
      </div>
    </motion.div>
  )
}
