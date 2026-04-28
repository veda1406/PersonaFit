import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const performanceData = [
  { name: 'Logistic Regression', accuracy: 82, precision: 81, recall: 81, f1: 81, roc: 0.94 },
  { name: 'SVM (RBF)', accuracy: 85, precision: 84, recall: 84, f1: 84, roc: 0.95 },
  { name: 'Random Forest', accuracy: 91, precision: 90, recall: 90, f1: 90, roc: 0.98 },
  { name: 'Naive Bayes', accuracy: 74, precision: 73, recall: 73, f1: 73, roc: 0.89 },
]

export default function ModelComparisonScreen() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
      style={{
        padding: '3rem 2rem',
        maxWidth: 1000,
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '2.5rem'
      }}
    >
      <div style={{ textAlign: 'center' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, color: '#2F556B', marginBottom: '0.5rem' }}>
          Model Performance Comparison
        </h1>
        <p style={{ fontSize: '1.1rem', color: '#5A8A9F' }}>
          Evaluate how different machine learning algorithms performed on our health risk dataset.
        </p>
      </div>

      {/* Model Selection Explanation */}
      <div style={{
        background: 'linear-gradient(135deg, #F0F9F0, #E8F4F8)',
        border: '1px solid #D6E8D6',
        borderRadius: 16,
        padding: '1.5rem 2rem',
        boxShadow: '0 4px 20px rgba(143,183,143,0.1)',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '1rem'
      }}>
        <div style={{ fontSize: '2rem' }}>🏆</div>
        <div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#2F556B', margin: '0 0 0.5rem' }}>
            Selected Model: Random Forest
          </h3>
          <p style={{ color: '#5A8A9F', margin: 0, lineHeight: 1.5 }}>
            Random Forest was selected as the final model due to having the highest overall metrics,
            including a 91% accuracy and a 0.98 ROC-AUC score. It provides the most reliable and
            balanced predictions for health risk assessment.
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem' }}>
        
        {/* Table Container */}
        <div style={{
          background: 'white',
          borderRadius: 24,
          padding: '2rem',
          boxShadow: '0 4px 32px rgba(47,85,107,0.08)'
        }}>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#2F556B', marginBottom: '1.5rem' }}>
            Metrics Overview
          </h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #E8F0E8', color: '#8AAAB8', fontSize: '0.9rem' }}>
                  <th style={{ padding: '1rem 0.5rem' }}>Model</th>
                  <th style={{ padding: '1rem 0.5rem' }}>Accuracy</th>
                  <th style={{ padding: '1rem 0.5rem' }}>F1 Score</th>
                  <th style={{ padding: '1rem 0.5rem' }}>ROC-AUC</th>
                </tr>
              </thead>
              <tbody>
                {performanceData.map((model, idx) => (
                  <tr key={idx} style={{ 
                    borderBottom: '1px solid #F0F5F0',
                    fontWeight: model.name === 'Random Forest' ? 700 : 500,
                    color: model.name === 'Random Forest' ? '#2F556B' : '#5A8A9F',
                    backgroundColor: model.name === 'Random Forest' ? '#F5F9F6' : 'transparent'
                  }}>
                    <td style={{ padding: '1rem 0.5rem' }}>{model.name}</td>
                    <td style={{ padding: '1rem 0.5rem' }}>{model.accuracy}%</td>
                    <td style={{ padding: '1rem 0.5rem' }}>{model.f1}%</td>
                    <td style={{ padding: '1rem 0.5rem' }}>{model.roc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Chart Container */}
        <div style={{
          background: 'white',
          borderRadius: 24,
          padding: '2rem',
          boxShadow: '0 4px 32px rgba(47,85,107,0.08)',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#2F556B', marginBottom: '1.5rem' }}>
            ROC-AUC Comparison
          </h2>
          <div style={{ flex: 1, minHeight: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={performanceData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#8AAAB8', fontSize: 12 }} />
                <YAxis domain={[0.8, 1]} axisLine={false} tickLine={false} tick={{ fill: '#8AAAB8' }} />
                <Tooltip 
                  cursor={{ fill: '#F5F9F6' }}
                  contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 20px rgba(47,85,107,0.1)' }}
                />
                <Bar dataKey="roc" radius={[6, 6, 0, 0]}>
                  {performanceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.name === 'Random Forest' ? '#8FB78F' : '#84C0CF'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </motion.div>
  )
}
