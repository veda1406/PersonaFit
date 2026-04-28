import { useState } from 'react'
import { motion } from 'framer-motion'

const ALL_RECS = [
  {
    id: 'walk',
    icon: '🚶',
    title: 'Walk daily',
    desc: 'A 30-minute walk each day can significantly lower your risk of heart disease.',
    color: '#8FB78F',
    goal: 'improve_fitness',
    condition: (inp) => inp.activity_level < 6,
  },
  {
    id: 'diet',
    icon: '🥦',
    title: 'Improve your diet',
    desc: 'Add more vegetables, fruits, and whole grains. Small swaps make a big difference.',
    color: '#84C0CF',
    goal: 'reduce_risk',
    condition: (inp) => inp.diet_score < 7,
  },
  {
    id: 'sleep',
    icon: '🌙',
    title: 'Sleep better',
    desc: 'Aim for 7–8 hours each night. A consistent bedtime routine helps a lot.',
    color: '#B4A8D8',
    goal: 'sleep_better',
    condition: (inp) => inp.sleep_hours < 7 || inp.sleep_hours > 9,
  },
  {
    id: 'smoking',
    icon: '🚭',
    title: 'Quit smoking',
    desc: 'Quitting smoking is the single biggest improvement you can make for your health.',
    color: '#D98CA1',
    goal: 'reduce_risk',
    condition: (inp) => inp.smoking_status === 1,
  },
  {
    id: 'bmi',
    icon: '⚖️',
    title: 'Manage your weight',
    desc: 'Even a 5% reduction in body weight can significantly lower chronic disease risk.',
    color: '#E9B18A',
    goal: 'improve_fitness',
    condition: (inp) => inp.bmi > 25,
  },
  {
    id: 'hydrate',
    icon: '💧',
    title: 'Stay hydrated',
    desc: 'Drink 8 glasses of water a day — it improves energy, focus, and metabolism.',
    color: '#84C0CF',
    goal: 'improve_fitness',
    condition: () => true,
  },
  {
    id: 'stress',
    icon: '🧘',
    title: 'Reduce stress',
    desc: 'High stress impacts your heart and sleep. Try 5 minutes of daily mindfulness.',
    color: '#B4A8D8',
    goal: 'sleep_better',
    condition: () => true,
  },
]

export default function RecommendationCards({ inputs }) {
  const [goal, setGoal] = useState('reduce_risk')

  let recs = ALL_RECS.filter(r => {
    if (goal === 'reduce_risk') return r.condition(inputs)
    if (goal === 'improve_fitness') return r.goal === 'improve_fitness' || r.condition(inputs)
    if (goal === 'sleep_better') return r.goal === 'sleep_better' || r.condition(inputs)
    return r.condition(inputs)
  })

  // Prioritize goal-specific recs
  recs.sort((a, b) => (a.goal === goal ? -1 : 1))
  
  // Unique top 4
  recs = Array.from(new Set(recs)).slice(0, 4)

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-lg transition-transform duration-300 hover:scale-[1.01] border border-transparent dark:border-slate-700 mb-5">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h3 className="text-2xl font-semibold text-[#2F556B] dark:text-gray-100 mb-2 tracking-wide">
            Personalized Recommendations
          </h3>
          <p className="text-base text-[#8AAAB8] dark:text-slate-400">
            Based on your results, here's where to start
          </p>
        </div>

        <div className="flex flex-col gap-1.5 w-full md:w-auto">
          <label className="text-xs text-[#5A7A8A] dark:text-slate-400 font-bold uppercase tracking-widest">
            What's your main goal?
          </label>
          <select 
            value={goal} 
            onChange={(e) => setGoal(e.target.value)}
            className="text-sm bg-[#F5F9F6] dark:bg-slate-700 text-[#2F556B] dark:text-gray-100 border border-[#D6E8D6] dark:border-slate-600 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-[#8FB78F] font-medium shadow-sm w-full md:w-auto cursor-pointer"
          >
            <option value="reduce_risk">📉 Reduce health risk</option>
            <option value="improve_fitness">🏃 Improve fitness</option>
            <option value="sleep_better">🌙 Sleep better</option>
          </select>
        </div>
      </div>

      <div className={`grid gap-5 ${recs.length > 2 ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1'}`}>
        {recs.map((rec, i) => (
          <motion.div
            key={rec.id}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 * i, duration: 0.4 }}
            className="rounded-xl p-5 flex flex-col gap-3 border"
            style={{ 
              backgroundColor: `${rec.color}10`, 
              borderColor: `${rec.color}30` 
            }}
          >
            <div className="flex items-center gap-3 mb-1">
              <div className="text-3xl bg-white dark:bg-slate-800 rounded-full p-2 shadow-sm border border-black/5 dark:border-white/5">
                {rec.icon}
              </div>
              <span className="font-semibold text-[#2F556B] dark:text-gray-100 text-lg">
                {rec.title}
              </span>
            </div>
            <p className="text-base text-[#5A7A8A] dark:text-slate-300 leading-relaxed m-0">
              {rec.desc}
            </p>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
