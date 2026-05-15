import { useChartStore } from '../stores/chartStore'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

const AGENT_NAMES: Record<string, string> = {
  onnx: 'ONNX BitLattice',
  rsi_revert: 'RSI Mean-Revert',
  momentum: 'Momentum',
  bb_bounce: 'Bollinger Bounce',
  sma_cross: 'SMA Cross',
  vol_price: 'Volume-Price',
  pattern_recog: 'Pattern Recog',
}

const AGENT_COLORS: Record<string, string> = {
  onnx: '#3b82f6',
  rsi_revert: '#8b5cf6',
  momentum: '#f59e0b',
  bb_bounce: '#10b981',
  sma_cross: '#06b6d4',
  vol_price: '#ec4899',
  pattern_recog: '#f97316',
}

export default function AgentVotePanel() {
  const { agentWeights, predictions } = useChartStore()

  const latestPrediction = predictions[0]
  const agentVotes = latestPrediction?.agents || {}

  const agents = Object.keys(AGENT_NAMES).map((key) => ({
    key,
    name: AGENT_NAMES[key],
    color: AGENT_COLORS[key],
    weight: agentWeights[key]?.weight || 1.0,
    accuracy: agentWeights[key]?.accuracy || 0,
    totalVotes: agentWeights[key]?.total_votes || 0,
    vote: agentVotes[key],
  }))

  return (
    <div className="vnx-card h-full flex flex-col">
      <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
        <TrendingUp size={16} className="text-vnx-green" />
        Agent Votes
      </h3>

      <div className="flex-1 overflow-y-auto space-y-2">
        {agents.map((a) => {
          const score = a.vote?.score ?? 0
          const isUp = score > 0
          const isDown = score < 0
          const isNeutral = score === 0
          const absScore = Math.abs(score)
          const barWidth = Math.min(100, absScore * 200)

          return (
            <div key={a.key} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400 flex items-center gap-1.5">
                  <span
                    className="inline-block w-2 h-2 rounded-full"
                    style={{ backgroundColor: a.color }}
                  />
                  {a.name}
                </span>
                <span className="text-gray-500">
                  w={a.weight.toFixed(2)} acc={((a.accuracy || 0) * 100).toFixed(0)}%
                </span>
              </div>

              <div className="flex items-center gap-2">
                <div className="flex-1 h-5 bg-gray-800 rounded overflow-hidden relative">
                  {isUp && (
                    <div
                      className="h-full rounded transition-all duration-300"
                      style={{
                        width: `${barWidth}%`,
                        backgroundColor: '#00bfa5',
                        marginLeft: 'auto',
                      }}
                    />
                  )}
                  {isDown && (
                    <div
                      className="h-full rounded transition-all duration-300"
                      style={{
                        width: `${barWidth}%`,
                        backgroundColor: '#ff6b6b',
                      }}
                    />
                  )}
                  {isNeutral && (
                    <div className="h-full flex items-center justify-center">
                      <Minus size={12} className="text-gray-600" />
                    </div>
                  )}
                </div>

                <div className="w-6 flex justify-center">
                  {isUp && <TrendingUp size={14} className="text-vnx-green" />}
                  {isDown && <TrendingDown size={14} className="text-vnx-red" />}
                  {isNeutral && <Minus size={14} className="text-gray-600" />}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {latestPrediction && (
        <div className="mt-3 pt-3 border-t border-gray-800">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Consensus</span>
            <span className="text-gray-400">
              {latestPrediction.agreement || 'N/A'}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
