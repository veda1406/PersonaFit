import { motion } from 'framer-motion'

const IMPACT_COLOR = (impact) =>
  impact > 0.65 ? '#D98CA1' : impact > 0.35 ? '#E9B18A' : '#84C0CF'

const IMPACT_LABEL = (impact) =>
  impact > 0.65 ? 'High influence' : impact > 0.35 ? 'Moderate influence' : 'Some influence'

export default function FactorBar({ factor, index }) {
  const color = IMPACT_COLOR(factor.impact)
  const label = IMPACT_LABEL(factor.impact)

  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <span className="font-semibold text-[#2F556B] dark:text-gray-100 text-base">{factor.name}</span>
        <span className="text-xs font-bold px-3 py-1 rounded-full tracking-wide" style={{ color, background: color + '22' }}>
          {label}
        </span>
      </div>
      <div className="h-4 bg-[#F0F5F0] dark:bg-slate-700 rounded-full overflow-hidden shadow-inner">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${Math.round(factor.impact * 100)}%` }}
          transition={{ delay: 0.3 + index * 0.1, duration: 0.7, ease: 'easeOut' }}
          className="h-full rounded-full"
          style={{ background: color }}
        />
      </div>
      <p className="text-sm text-[#AABFC8] dark:text-slate-400 mt-2 leading-relaxed">
        {factor.description}
      </p>
    </div>
  )
}
