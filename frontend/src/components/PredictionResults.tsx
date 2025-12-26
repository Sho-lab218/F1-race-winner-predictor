import { PredictionResult } from '../types'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface PredictionResultsProps {
  predictions: PredictionResult[]
  loading: boolean
}

export default function PredictionResults({ predictions, loading }: PredictionResultsProps) {
  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg shadow-xl p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-f1-red"></div>
        </div>
      </div>
    )
  }

  if (predictions.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg shadow-xl p-6">
        <h2 className="text-2xl font-bold text-white mb-4">Prediction Results</h2>
        <div className="text-gray-400 text-center py-12">
          <p>Configure a race and click "Predict Race Winner" to see results</p>
        </div>
      </div>
    )
  }

  // Prepare data for chart
  const chartData = predictions.map((pred) => ({
    driver: pred.driver,
    probability: pred.win_probability,
  }))

  // Color gradient based on probability
  const getColor = (probability: number) => {
    if (probability > 30) return '#E10600' // F1 Red
    if (probability > 20) return '#FF6B35' // Orange
    if (probability > 10) return '#FFA500' // Yellow
    return '#4A5568' // Gray
  }

  return (
    <div className="bg-gray-800 rounded-lg shadow-xl p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Prediction Results</h2>

      {/* Top 3 Podium */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {predictions.slice(0, 3).map((pred, index) => (
          <div
            key={pred.driver}
            className={`bg-gradient-to-b ${
              index === 0
                ? 'from-yellow-600 to-yellow-800'
                : index === 1
                ? 'from-gray-400 to-gray-600'
                : 'from-orange-700 to-orange-900'
            } rounded-lg p-4 text-center`}
          >
            <div className="text-3xl mb-2">
              {index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}
            </div>
            <div className="text-white font-bold text-xl">{pred.driver}</div>
            <div className="text-white/90 text-sm mt-1">
              {pred.win_probability.toFixed(1)}%
            </div>
            <div className="text-white/70 text-xs mt-1">
              Q{pred.qualifying_position}
            </div>
          </div>
        ))}
      </div>

      {/* Chart */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-300 mb-4">
          Win Probability Distribution
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <XAxis
              dataKey="driver"
              tick={{ fill: '#9CA3AF' }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis
              tick={{ fill: '#9CA3AF' }}
              label={{
                value: 'Win Probability (%)',
                angle: -90,
                position: 'insideLeft',
                style: { fill: '#9CA3AF' },
              }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#F3F4F6',
              }}
              formatter={(value: number) => [`${value.toFixed(2)}%`, 'Win Probability']}
            />
            <Bar dataKey="probability" radius={[8, 8, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(entry.probability)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Full Results Table */}
      <div>
        <h3 className="text-lg font-semibold text-gray-300 mb-4">All Driver Probabilities</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left text-gray-400 font-medium py-2 px-3">Rank</th>
                <th className="text-left text-gray-400 font-medium py-2 px-3">Driver</th>
                <th className="text-left text-gray-400 font-medium py-2 px-3">Qualifying</th>
                <th className="text-right text-gray-400 font-medium py-2 px-3">
                  Win Probability
                </th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((pred, index) => (
                <tr
                  key={pred.driver}
                  className="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors"
                >
                  <td className="text-gray-300 py-2 px-3">#{index + 1}</td>
                  <td className="text-white font-medium py-2 px-3">{pred.driver}</td>
                  <td className="text-gray-400 py-2 px-3">P{pred.qualifying_position}</td>
                  <td className="text-right py-2 px-3">
                    <span className="font-semibold text-white">
                      {pred.win_probability.toFixed(2)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Note */}
      <div className="mt-6 p-4 bg-gray-900/50 rounded-lg border border-gray-700">
        <p className="text-sm text-gray-400">
          ⚠️ These are probabilistic estimates based on historical patterns, track-specific
          performance, and documented assumptions. Predictions update as new race data becomes
          available.
        </p>
      </div>
    </div>
  )
}

