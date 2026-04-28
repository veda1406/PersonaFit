import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const RISK_LABELS_FRIENDLY = {
  0: "You're in great shape!",
  1: "You may have some areas to improve",
  2: "You may be at higher health risk",
}
const RISK_COLORS = { 0: '#8FB78F', 1: '#D98CA1', 2: '#E9B18A' }
const RISK_EMOJI = { 0: '💚', 1: '🌼', 2: '🔆' }

export default function ImprovementSection({ inputs, currentResult }) {
  const [activity, setActivity] = useState(inputs.activity_level)
  const [diet, setDiet] = useState(inputs.diet_score)
  const [sleep, setSleep] = useState(inputs.sleep_hours)
  const [simResult, setSimResult] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const hasChange =
      activity !== inputs.activity_level ||
      diet !== inputs.diet_score ||
      sleep !== inputs.sleep_hours

    if (!hasChange) { setSimResult(null); return }

    const timer = setTimeout(async () => {
      setLoading(true)
      try {
        const res = await fetch('/api/simulate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...inputs,
            new_activity: activity,
            new_diet: diet,
            new_sleep: sleep,
          }),
        })
        const data = await res.json()
        setSimResult(data)
      } catch {
        /* fail silently */
      } finally {
        setLoading(false)
      }
    }, 400)
    return () => clearTimeout(timer)
  }, [activity, diet, sleep])

  const improved = simResult && simResult.risk_level < currentResult.risk_level
  const worse = simResult && simResult.risk_level > currentResult.risk_level
  const same = simResult && simResult.risk_level === currentResult.risk_level

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl p-10 shadow-lg transition-transform duration-300 hover:scale-[1.01] border border-transparent dark:border-slate-700 mb-5">
      <h3 className="text-2xl font-semibold text-[#2F556B] dark:text-gray-100 mb-2 tracking-wide">
        What if you improve?
      </h3>
      <p className="text-base text-[#8AAAB8] dark:text-slate-400 mb-8 leading-relaxed">
        Small changes can improve your health. Try adjusting the sliders below.
      </p>

      {/* Sliders */}
      <div className="flex flex-col gap-8 mb-10">
        <SimSlider icon="🏃" label="Physical Activity" value={activity} min={0} max={10} step={0.5}
          onChange={setActivity} format={v => v.toFixed(1)} />
        <SimSlider icon="🥗" label="Diet Quality" value={diet} min={0} max={10} step={0.5}
          onChange={setDiet} format={v => v.toFixed(1)} />
        <SimSlider icon="😴" label="Sleep Hours" value={sleep} min={3} max={12} step={0.5}
          onChange={setSleep} format={v => `${v}h`} />
      </div>

      {/* Before vs After */}
      <div className="grid grid-cols-2 gap-6">
        <BeforeAfterCard
          label="Now"
          emoji={RISK_EMOJI[currentResult.risk_level]}
          text={RISK_LABELS_FRIENDLY[currentResult.risk_level]}
          color={RISK_COLORS[currentResult.risk_level]}
          conf={currentResult.confidence}
          healthScore={Math.round(currentResult.probabilities.low)}
        />
        <BeforeAfterCard
          label="After changes"
          emoji={simResult ? RISK_EMOJI[simResult.risk_level] : '⋯'}
          text={simResult ? RISK_LABELS_FRIENDLY[simResult.risk_level] : 'Adjust sliders'}
          color={simResult ? RISK_COLORS[simResult.risk_level] : '#D6E8D6'}
          conf={simResult ? simResult.confidence : null}
          healthScore={simResult ? simResult.health_score : null}
          loading={loading}
          isProjection
        />
      </div>

      {/* Outcome message */}
      <AnimatePresence>
        {simResult && (
          <motion.p
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className={`mt-8 px-6 py-4 rounded-xl text-sm font-bold text-center shadow-sm ${
              improved ? 'bg-[#F0F9F0] dark:bg-green-900/30 text-[#5A8A5A] dark:text-green-400' :
              worse ? 'bg-[#FDF5EE] dark:bg-orange-900/30 text-[#B07040] dark:text-orange-400' :
              'bg-[#F0F5FF] dark:bg-slate-700/50 text-[#5A7A9A] dark:text-slate-300'
            }`}
          >
            {improved && '🎉 These changes could lower your risk level!'}
            {same && '➡️ Your risk level stays the same — try bigger changes.'}
            {worse && '⚠️ This combination raises risk — try different values.'}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  )
}

function SimSlider({ icon, label, value, min, max, step, onChange, format }) {
  const pct = ((value - min) / (max - min)) * 100
  return (
    <div>
      <div className="flex justify-between items-center mb-3">
        <span className="text-base font-semibold text-[#2F556B] dark:text-gray-100 flex items-center gap-2">
          <span className="text-xl">{icon}</span> {label}
        </span>
        <span className="text-base font-bold text-[#8FB78F] bg-[#8FB78F]/10 dark:bg-[#8FB78F]/20 px-3 py-1 rounded-full shadow-sm">
          {format ? format(value) : value}
        </span>
      </div>
      <input
        type="range"
        min={min} max={max} step={step} value={value}
        onChange={e => onChange(parseFloat(e.target.value))}
        className="w-full h-3 rounded-full appearance-none cursor-pointer shadow-inner"
        style={{ background: `linear-gradient(90deg, #84C0CF ${pct}%, #D6E8D6 ${pct}%)` }}
      />
    </div>
  )
}

function BeforeAfterCard({ label, emoji, text, color, conf, loading, isProjection }) {
  return (
    <div 
      className="rounded-2xl p-6 text-center min-h-[140px] flex flex-col items-center justify-center gap-2 border shadow-sm"
      style={{
        background: color + '15',
        borderColor: color + '35',
      }}
    >
      <span className="text-xs font-bold text-[#8AAAB8] dark:text-slate-400 uppercase tracking-widest">{label}</span>
      <span className="text-5xl leading-none my-1">
        {loading ? <motion.span animate={{ opacity: [1, 0.3, 1] }} transition={{ duration: 0.8, repeat: Infinity }}>⋯</motion.span> : emoji}
      </span>
      <span className="text-sm text-[#5A7A8A] dark:text-slate-300 font-semibold leading-relaxed">{text}</span>
      {conf && <span className="text-xs font-bold mt-2 px-3 py-1 rounded-full bg-white/50 dark:bg-black/20" style={{ color }}>{conf}% Confidence</span>}
    </div>
  )
}
