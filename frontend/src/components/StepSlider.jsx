import { motion } from 'framer-motion'

export default function StepSlider({ field, value, onChange }) {
  const { label, icon, min, max, step, format, hint, hintColor, helpText } = field
  const pct = ((value - min) / (max - min)) * 100
  const hintText = hint ? hint(value) : null
  const hintClr = hintColor ? hintColor(value) : '#8FB78F'

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1.25rem' }}>{icon}</span>
          <span style={{ fontWeight: 600, color: '#2F556B', fontSize: '0.95rem' }}>{label}</span>
        </div>
        <div style={{ textAlign: 'right' }}>
          <span style={{ fontWeight: 700, fontSize: '1.15rem', color: '#2F556B' }}>
            {format ? format(value) : value}
          </span>
          {hintText && (
            <div style={{ fontSize: '0.72rem', color: hintClr, fontWeight: 600, marginTop: '1px' }}>
              {hintText}
            </div>
          )}
        </div>
      </div>

      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={e => onChange(parseFloat(e.target.value))}
        style={{
          background: `linear-gradient(90deg, #8FB78F ${pct}%, #D6E8D6 ${pct}%)`,
        }}
      />

      {helpText && (
        <p style={{ fontSize: '0.75rem', color: '#B0C8D4', margin: '0.4rem 0 0', lineHeight: 1.4 }}>
          {helpText}
        </p>
      )}
    </div>
  )
}
