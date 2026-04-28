import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import StepSlider from '../components/StepSlider'

const STEPS = [
  {
    id: 1,
    title: 'Let\'s start with the basics',
    subtitle: 'No personal data is stored',
    fields: [
      {
        key: 'age', label: 'Your Age', icon: '🎂',
        min: 15, max: 75, step: 1, unit: 'years',
        format: v => `${v} yrs`,
        hint: v => v < 25 ? 'Young adult' : v < 45 ? 'Adult' : v < 60 ? 'Middle-aged' : 'Senior',
      },
      {
        key: 'bmi', label: 'Your BMI', icon: '⚖️',
        min: 15, max: 50, step: 0.5, unit: '',
        format: v => v.toFixed(1),
        hint: v => v < 18.5 ? 'Underweight' : v < 25 ? 'Healthy weight' : v < 30 ? 'Overweight' : 'Obese',
        hintColor: v => v < 18.5 ? '#84C0CF' : v < 25 ? '#8FB78F' : v < 30 ? '#E9B18A' : '#D98CA1',
        helpText: 'BMI = weight(kg) ÷ height(m)²',
      },
    ],
  },
  {
    id: 2,
    title: 'How active is your lifestyle?',
    subtitle: 'Honest answers give better results',
    fields: [
      {
        key: 'activity_level', label: 'Physical Activity', icon: '🏃',
        min: 0, max: 10, step: 0.5,
        format: v => v.toFixed(1),
        hint: v => v <= 2 ? 'Sedentary' : v <= 4 ? 'Lightly active' : v <= 7 ? 'Moderately active' : 'Very active',
        helpText: '0 = No exercise · 10 = Daily intense workouts',
      },
      {
        key: 'diet_score', label: 'Diet Quality', icon: '🥗',
        min: 0, max: 10, step: 0.5,
        format: v => v.toFixed(1),
        hint: v => v <= 3 ? 'Mostly processed food' : v <= 6 ? 'Mixed diet' : v <= 8 ? 'Mostly healthy' : 'Excellent',
        helpText: '0 = Fast food daily · 10 = Balanced whole foods',
      },
    ],
  },
  {
    id: 3,
    title: 'Sleep & habits',
    subtitle: 'Almost there!',
    fields: [
      {
        key: 'sleep_hours', label: 'Sleep Hours', icon: '😴',
        min: 3, max: 12, step: 0.5,
        format: v => `${v}h`,
        hint: v => v < 6 ? 'Too little' : v <= 9 ? 'Good range' : 'Too much',
        hintColor: v => v < 6 ? '#D98CA1' : v <= 9 ? '#8FB78F' : '#E9B18A',
        helpText: 'Adults need 7–9 hours of sleep per night',
      },
    ],
    hasSmokingField: true,
  },
]

const slideVariants = {
  enter: (dir) => ({ x: dir > 0 ? 80 : -80, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit: (dir) => ({ x: dir > 0 ? -80 : 80, opacity: 0 }),
}

export default function InputScreen({ defaults, onAnalyse, onBack }) {
  const [step, setStep] = useState(0)
  const [values, setValues] = useState(defaults)
  const [direction, setDirection] = useState(1)

  const currentStep = STEPS[step]
  const isLast = step === STEPS.length - 1

  function go(delta) {
    setDirection(delta)
    setStep(s => Math.max(0, Math.min(STEPS.length - 1, s + delta)))
  }

  function handleNext() {
    if (isLast) onAnalyse(values)
    else go(1)
  }

  function setValue(key, val) {
    setValues(v => ({ ...v, [key]: val }))
  }

  return (
    <motion.div
      key="input"
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -24 }}
      transition={{ duration: 0.45 }}
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem',
      }}
    >
      <div style={{ width: '100%', maxWidth: 520 }}>

        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '2rem', gap: '0.75rem' }}>
          <button
            onClick={step === 0 ? onBack : () => go(-1)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.2rem', color: '#8AAAB8', padding: '0.25rem' }}
          >
            ←
          </button>
          <div style={{ flex: 1 }}>
            {/* Progress bar */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '0.78rem', color: '#8AAAB8', fontWeight: 500, whiteSpace: 'nowrap' }}>
                Step {step + 1} of {STEPS.length}
              </span>
              <div style={{ flex: 1, height: 6, background: '#D6E8D6', borderRadius: 999, overflow: 'hidden' }}>
                <motion.div
                  animate={{ width: `${((step + 1) / STEPS.length) * 100}%` }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                  style={{ height: '100%', background: 'linear-gradient(90deg, #8FB78F, #84C0CF)', borderRadius: 999 }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Step card */}
        <AnimatePresence mode="wait" custom={direction}>
          <motion.div
            key={step}
            custom={direction}
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.35, ease: 'easeInOut' }}
            style={{
              background: 'white',
              borderRadius: 24,
              padding: '2rem',
              boxShadow: '0 4px 32px rgba(47,85,107,0.08)',
              marginBottom: '1.5rem',
            }}
          >
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#2F556B', margin: '0 0 0.3rem' }}>
              {currentStep.title}
            </h2>
            <p style={{ fontSize: '0.88rem', color: '#8AAAB8', margin: '0 0 2rem' }}>
              {currentStep.subtitle}
            </p>

            {/* Slider fields */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              {currentStep.fields.map(field => (
                <StepSlider
                  key={field.key}
                  field={field}
                  value={values[field.key]}
                  onChange={val => setValue(field.key, val)}
                />
              ))}

              {/* Smoking toggle (step 3 only) */}
              {currentStep.hasSmokingField && (
                <SmokingToggle
                  value={values.smoking_status}
                  onChange={val => setValue('smoking_status', val)}
                />
              )}
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Dots */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
          {STEPS.map((_, i) => (
            <div key={i} style={{
              width: i === step ? 20 : 8,
              height: 8,
              borderRadius: 999,
              background: i === step ? '#8FB78F' : '#D6E8D6',
              transition: 'all 0.3s ease',
            }} />
          ))}
        </div>

        {/* Next button */}
        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          onClick={handleNext}
          style={{
            width: '100%',
            background: isLast ? 'linear-gradient(135deg, #8FB78F, #6FA86F)' : 'linear-gradient(135deg, #84C0CF, #5FAABF)',
            color: 'white',
            border: 'none',
            borderRadius: 999,
            padding: '1rem',
            fontSize: '1.05rem',
            fontWeight: 700,
            cursor: 'pointer',
            boxShadow: isLast
              ? '0 4px 20px rgba(143,183,143,0.4)'
              : '0 4px 20px rgba(132,192,207,0.35)',
            letterSpacing: '0.01em',
          }}
        >
          {isLast ? '🔍 Analyse My Health' : 'Continue →'}
        </motion.button>
      </div>
    </motion.div>
  )
}

function SmokingToggle({ value, onChange }) {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
        <span style={{ fontSize: '1.3rem' }}>🚬</span>
        <span style={{ fontWeight: 600, color: '#2F556B', fontSize: '0.95rem' }}>Do you smoke?</span>
      </div>
      <div style={{ display: 'flex', gap: '0.75rem' }}>
        {[{ label: 'No, I don\'t', val: 0 }, { label: 'Yes, I do', val: 1 }].map(opt => (
          <motion.button
            key={opt.val}
            whileTap={{ scale: 0.96 }}
            onClick={() => onChange(opt.val)}
            style={{
              flex: 1,
              padding: '0.85rem',
              borderRadius: 14,
              border: '2px solid',
              borderColor: value === opt.val ? (opt.val === 0 ? '#8FB78F' : '#D98CA1') : '#E8F0E8',
              background: value === opt.val ? (opt.val === 0 ? '#F0F9F0' : '#FDF0F4') : 'white',
              color: value === opt.val ? (opt.val === 0 ? '#5A8A5A' : '#C0607A') : '#8AAAB8',
              fontWeight: 600,
              fontSize: '0.9rem',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            {opt.label}
          </motion.button>
        ))}
      </div>
    </div>
  )
}
