import { create } from 'zustand'

export interface Candle {
  time: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface PriceTick {
  symbol: string
  price: number
  timestamp: number
  latency_ms: number
}

export interface AgentVote {
  score: number
  vote: string
  correct: number | null
}

export interface Prediction {
  symbol: string
  direction: string
  confidence: number
  up_probability: number
  price_at_predict: number
  timestamp: number
  iso_time: string
  pattern: string | null
  pattern_confidence: number | null
  agents: Record<string, AgentVote>
  prediction_id: number
  agreement?: string
}

export interface AgentWeight {
  weight: number
  total_votes: number
  correct_votes: number
  accuracy: number
}

export interface AccuracyStats {
  overall: number
  last_10: number
  last_50: number
  total_scored: number
  total_correct: number
  timestamp: number
}

interface ChartState {
  candles: Candle[]
  predictions: Prediction[]
  agentWeights: Record<string, AgentWeight>
  accuracy: AccuracyStats | null
  latestPrice: PriceTick | null
  connected: boolean
  reconnecting: boolean
  // Actions
  addCandle: (c: Candle) => void
  updateLatestPrice: (p: PriceTick) => void
  addPrediction: (p: Prediction) => void
  setAgentWeights: (w: Record<string, AgentWeight>) => void
  setAccuracy: (a: AccuracyStats) => void
  setConnected: (v: boolean) => void
  setReconnecting: (v: boolean) => void
}

export const useChartStore = create<ChartState>((set) => ({
  candles: [],
  predictions: [],
  agentWeights: {},
  accuracy: null,
  latestPrice: null,
  connected: false,
  reconnecting: false,

  addCandle: (c) => set((s) => {
    const existing = s.candles.findIndex((x) => x.time === c.time)
    let next = [...s.candles]
    if (existing >= 0) {
      next[existing] = c
    } else {
      next.push(c)
      if (next.length > 500) next = next.slice(-500)
    }
    return { candles: next }
  }),

  updateLatestPrice: (p) => set({ latestPrice: p }),

  addPrediction: (p) => set((s) => {
    const next = [p, ...s.predictions]
    if (next.length > 100) next.pop()
    return { predictions: next }
  }),

  setAgentWeights: (w) => set({ agentWeights: w }),

  setAccuracy: (a) => set({ accuracy: a }),

  setConnected: (v) => set({ connected: v }),

  setReconnecting: (v) => set({ reconnecting: v }),
}))
