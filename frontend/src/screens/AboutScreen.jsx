import { motion } from 'framer-motion'
import logoUrl from '../assets/logo.png'

export default function AboutScreen() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
      className="px-8 py-16 max-w-[800px] mx-auto transition-colors duration-300"
    >
      <div className="bg-white dark:bg-slate-800 rounded-3xl p-10 md:p-12 shadow-[0_4px_32px_rgba(47,85,107,0.08)] dark:shadow-none border border-transparent dark:border-slate-700">
        
        <div className="flex flex-col items-center mb-6">
          <img 
            src={logoUrl} 
            alt="PersonaFit Logo" 
            className="h-[60px] md:h-[80px] dark:brightness-125 dark:contrast-125 transition-all" 
          />
        </div>

        <h1 className="text-[2.5rem] font-extrabold text-[#2F556B] dark:text-gray-100 mb-6 text-center">
          About PersonaFit
        </h1>
        
        <div className="text-[#5A8A9F] dark:text-slate-300 text-[1.1rem] leading-[1.8]">
          <p className="mb-6">
            PersonaFit is an advanced machine learning application designed to help individuals understand their lifestyle habits and how they contribute to long-term health risks.
          </p>
          <p className="mb-6">
            Our system uses multiple health metrics, including Body Mass Index (BMI), physical activity levels, dietary quality, and sleep patterns, to provide a holistic risk assessment. It breaks down complex medical concepts into easy-to-understand language.
          </p>
          
          <h2 className="text-[1.5rem] font-bold text-[#2F556B] dark:text-gray-100 mt-8 mb-4">
            Disclaimer
          </h2>
          <div className="bg-[#FDF0F4] dark:bg-rose-950/30 border border-[#FAD1DA] dark:border-rose-900/50 rounded-xl p-5 text-[#C0607A] dark:text-rose-300 text-[1rem]">
            <strong className="font-bold text-[#A0405A] dark:text-rose-200">Important:</strong> PersonaFit is developed for educational and portfolio purposes only. 
            The assessments and recommendations provided do not constitute professional medical advice. 
            Always consult a qualified healthcare professional before making significant changes to your diet, 
            exercise routine, or lifestyle.
          </div>
        </div>
      </div>
    </motion.div>
  )
}
