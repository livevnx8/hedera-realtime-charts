import { useEffect, useRef } from 'react'
import { useChartStore } from '../stores/chartStore'

const WS_URL = 'ws://localhost:8010/ws/vnx'
const RECONNECT_DELAY = 3000

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>()

  const {
    addCandle,
    updateLatestPrice,
    addPrediction,
    setAgentWeights,
    setAccuracy,
    setConnected,
    setReconnecting,
  } = useChartStore()

  useEffect(() => {
    const connect = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) return

      setReconnecting(true)
      const ws = new WebSocket(WS_URL)
      wsRef.current = ws

      ws.onopen = () => {
        setConnected(true)
        setReconnecting(false)
        console.log('[WS] Connected')
      }

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)

          if (msg.type === 'price_tick') {
            updateLatestPrice({
              symbol: msg.symbol,
              price: msg.price,
              timestamp: msg.timestamp,
              latency_ms: msg.latency_ms,
            })
          }

          if (msg.type === 'init' && msg.candles) {
            const hbarCandles = msg.candles['HBARUSDT'] || []
            hbarCandles.forEach((c: any) => addCandle(c))
            if (msg.agent_weights) {
              setAgentWeights(msg.agent_weights)
            }
          }

          if (msg.type === 'prediction') {
            addPrediction({
              symbol: msg.symbol,
              direction: msg.direction,
              confidence: msg.confidence,
              up_probability: msg.up_probability,
              price_at_predict: msg.price_at_predict,
              timestamp: msg.timestamp,
              iso_time: msg.iso_time,
              pattern: msg.pattern,
              pattern_confidence: msg.pattern_confidence,
              agents: msg.agents || {},
              prediction_id: msg.prediction_id,
            })
          }

          if (msg.type === 'agent_weights') {
            setAgentWeights(msg.weights)
          }

          if (msg.type === 'accuracy') {
            setAccuracy({
              overall: msg.overall,
              last_10: msg.last_10,
              last_50: msg.last_50,
              total_scored: msg.total_scored,
              total_correct: msg.total_correct,
              timestamp: msg.timestamp,
            })
          }
        } catch (e) {
          // ignore parse errors
        }
      }

      ws.onclose = () => {
        setConnected(false)
        wsRef.current = null
        reconnectTimeoutRef.current = setTimeout(connect, RECONNECT_DELAY)
      }

      ws.onerror = () => {
        ws.close()
      }
    }

    connect()

    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current)
      wsRef.current?.close()
    }
  }, [addCandle, updateLatestPrice, addPrediction, setAgentWeights, setAccuracy, setConnected, setReconnecting])
}
