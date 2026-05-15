import { useEffect, useRef } from 'react'
import { useChartStore, type Candle, type PriceTick, type Prediction, type AccuracyStats } from '../stores/chartStore'

const WS_URL = 'ws://localhost:8010/ws/vnx'
const RECONNECT_DELAY = 3000

// ── Type Guards ─────────────────────────────────────────────
function isPriceTick(msg: unknown): msg is { symbol: string; price: number; timestamp: number; latency_ms: number } {
  const m = msg as Record<string, unknown>
  return m.type === 'price_tick' && typeof m.symbol === 'string' && typeof m.price === 'number'
}

function isInit(msg: unknown): msg is { candles: Record<string, Candle[]>; agent_weights?: Record<string, unknown> } {
  const m = msg as Record<string, unknown>
  return m.type === 'init' && m.candles !== null && typeof m.candles === 'object'
}

function isPredictionMsg(msg: unknown): msg is Prediction & { type: string } {
  const m = msg as Record<string, unknown>
  return m.type === 'prediction' && typeof m.symbol === 'string' && typeof m.direction === 'string'
}

function isAgentWeights(msg: unknown): msg is { weights: Record<string, unknown> } {
  const m = msg as Record<string, unknown>
  return m.type === 'agent_weights' && m.weights !== null && typeof m.weights === 'object'
}

function isAccuracyMsg(msg: unknown): msg is AccuracyStats & { type: string } {
  const m = msg as Record<string, unknown>
  return m.type === 'accuracy' && typeof m.overall === 'number'
}

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

          if (isPriceTick(msg)) {
            const tick: PriceTick = {
              symbol: msg.symbol,
              price: msg.price,
              timestamp: msg.timestamp,
              latency_ms: msg.latency_ms,
            }
            updateLatestPrice(tick)
            return
          }

          if (isInit(msg)) {
            const hbarCandles = msg.candles['HBARUSDT'] || []
            hbarCandles.forEach((c: Candle) => addCandle(c))
            if (msg.agent_weights) {
              setAgentWeights(msg.agent_weights as Record<string, { weight: number; total_votes: number; correct_votes: number; accuracy: number }>)
            }
            return
          }

          if (isPredictionMsg(msg)) {
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
            return
          }

          if (isAgentWeights(msg)) {
            setAgentWeights(msg.weights as Record<string, { weight: number; total_votes: number; correct_votes: number; accuracy: number }>)
            return
          }

          if (isAccuracyMsg(msg)) {
            setAccuracy({
              overall: msg.overall,
              last_10: msg.last_10,
              last_50: msg.last_50,
              total_scored: msg.total_scored,
              total_correct: msg.total_correct,
              timestamp: msg.timestamp,
            })
            return
          }
        } catch (e) {
          // Silently ignore malformed messages
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
