import { useChartStore } from '../stores/chartStore'
import { Wifi, WifiOff, Activity, Server } from 'lucide-react'

export default function SwarmStatus() {
  const { connected, reconnecting, latestPrice } = useChartStore()

  return (
    <div className="vnx-card">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
          <Server size={16} className="text-blue-400" />
          VNX Swarm Status
        </h3>
        <div className="flex items-center gap-2">
          {connected ? (
            <span className="flex items-center gap-1 text-xs text-vnx-green">
              <Wifi size={14} />
              Live
            </span>
          ) : reconnecting ? (
            <span className="flex items-center gap-1 text-xs text-yellow-400">
              <Activity size={14} className="animate-spin" />
              Reconnecting...
            </span>
          ) : (
            <span className="flex items-center gap-1 text-xs text-vnx-red">
              <WifiOff size={14} />
              Disconnected
            </span>
          )}
        </div>
      </div>

      <div className="space-y-2 text-xs">
        <div className="flex items-center justify-between">
          <span className="text-gray-500">Data Source</span>
          <span className="text-gray-300">Binance WS + VNX DB</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-500">Model</span>
          <span className="text-gray-300">BitLattice-ONNX-v3.1</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-500">Timeframe</span>
          <span className="text-gray-300">5 min</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-500">Agents</span>
          <span className="text-gray-300">7 swarm agents</span>
        </div>
        {latestPrice && (
          <div className="flex items-center justify-between">
            <span className="text-gray-500">Latency</span>
            <span className="text-gray-300 font-mono">
              {latestPrice.latency_ms.toFixed(0)}ms
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
