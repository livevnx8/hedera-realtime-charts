import { useChartStore } from '../stores/chartStore'
import { Target, Zap, BarChart3 } from 'lucide-react'

export default function AccuracyTicker() {
  const { accuracy, predictions } = useChartStore()

  const stats = [
    {
      label: 'Overall',
      value: accuracy ? `${(accuracy.overall * 100).toFixed(1)}%` : '—',
      icon: BarChart3,
      color: 'text-blue-400',
    },
    {
      label: 'Last 10',
      value: accuracy ? `${(accuracy.last_10 * 100).toFixed(1)}%` : '—',
      icon: Zap,
      color: accuracy && accuracy.last_10 >= 0.55 ? 'text-vnx-green' : 'text-vnx-red',
    },
    {
      label: 'Last 50',
      value: accuracy ? `${(accuracy.last_50 * 100).toFixed(1)}%` : '—',
      icon: Target,
      color: accuracy && accuracy.last_50 >= 0.55 ? 'text-vnx-green' : 'text-yellow-400',
    },
  ]

  const totalPredictions = predictions.length
  const correctPredictions = predictions.filter(
    (p) => p.direction === (p.agents?.onnx?.correct === 1 ? 'UP' : 'DOWN')
  ).length

  return (
    <div className="vnx-card">
      <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
        <Target size={16} className="text-vnx-gold" />
        Swarm Accuracy
      </h3>

      <div className="grid grid-cols-3 gap-3">
        {stats.map((s) => (
          <div key={s.label} className="bg-gray-800/50 rounded p-2 text-center">
            <div className={`text-xs text-gray-500 mb-1`}>{s.label}</div>
            <div className={`text-lg font-mono font-bold ${s.color}`}>{s.value}</div>
          </div>
        ))}
      </div>

      <div className="mt-3 pt-3 border-t border-gray-800">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Predictions</span>
          <span className="text-gray-300 font-mono">{totalPredictions}</span>
        </div>
        {accuracy && (
          <>
            <div className="flex items-center justify-between text-xs text-gray-500 mt-1">
              <span>Scored</span>
              <span className="text-gray-300 font-mono">{accuracy.total_scored}</span>
            </div>
            <div className="flex items-center justify-between text-xs text-gray-500 mt-1">
              <span>Correct</span>
              <span className="text-vnx-green font-mono">{accuracy.total_correct}</span>
            </div>
          </>
        )}
      </div>

      {/* Mini sparkline of last 10 outcomes */}
      {predictions.length > 0 && (
        <div className="mt-3 flex gap-0.5 items-end h-6">
          {predictions.slice(0, 20).reverse().map((p, i) => {
            const isCorrect = p.agents?.onnx?.correct === 1
            return (
              <div
                key={i}
                className={`flex-1 rounded-sm ${isCorrect ? 'bg-vnx-green' : 'bg-vnx-red'} opacity-80`}
                style={{ height: `${Math.max(20, p.confidence * 100)}%` }}
                title={`${p.direction} @ ${p.iso_time || ''}`}
              />
            )
          })}
        </div>
      )}
    </div>
  )
}
