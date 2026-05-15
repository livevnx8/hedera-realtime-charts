import { useWebSocket } from './hooks/useWebSocket'
import ChartPanel from './components/ChartPanel'
import AgentVotePanel from './components/AgentVotePanel'
import AccuracyTicker from './components/AccuracyTicker'
import SwarmStatus from './components/SwarmStatus'

export default function App() {
  useWebSocket()

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-4">
      {/* Header */}
      <header className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-vnx-green to-blue-500 flex items-center justify-center">
            <span className="text-white font-bold text-sm">V</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">VNX Swarm Dashboard</h1>
            <p className="text-xs text-gray-500">Real-time prediction swarm + price tracking</p>
          </div>
        </div>
        <div className="text-xs text-gray-500">
          BitLattice-ONNX-v3.1 | 5-min | 7 agents
        </div>
      </header>

      {/* Main layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Chart - takes 3 columns */}
        <div className="lg:col-span-3">
          <ChartPanel />
        </div>

        {/* Side panel */}
        <div className="space-y-4">
          <SwarmStatus />
          <AccuracyTicker />
          <AgentVotePanel />
        </div>
      </div>
    </div>
  )
}
