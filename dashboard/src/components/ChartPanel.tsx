import { useEffect, useRef } from 'react'
import { createChart, IChartApi, ISeriesApi, CandlestickData, HistogramData } from 'lightweight-charts'
import { useChartStore } from '../stores/chartStore'

export default function ChartPanel() {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const volSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null)
  const markersRef = useRef<any[]>([])

  const { candles, predictions, latestPrice } = useChartStore()

  useEffect(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#0f172a' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: '#1e293b' },
        horzLines: { color: '#1e293b' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#1e293b',
      },
      timeScale: {
        borderColor: '#1e293b',
        timeVisible: true,
        secondsVisible: false,
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
    })

    const candleSeries = chart.addCandlestickSeries({
      upColor: '#00bfa5',
      downColor: '#ff6b6b',
      borderUpColor: '#00bfa5',
      borderDownColor: '#ff6b6b',
      wickUpColor: '#00bfa5',
      wickDownColor: '#ff6b6b',
    })

    const volSeries = chart.addHistogramSeries({
      color: '#3b82f6',
      priceFormat: { type: 'volume' },
      priceScaleId: '',
    })
    volSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    })

    chartRef.current = chart
    candleSeriesRef.current = candleSeries
    volSeriesRef.current = volSeries

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth })
      }
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [])

  // Update candles
  useEffect(() => {
    if (!candleSeriesRef.current || candles.length === 0) return

    const data: CandlestickData[] = candles.map((c) => ({
      time: (c.time / 1000) as any,
      open: c.open,
      high: c.high,
      low: c.low,
      close: c.close,
    }))

    candleSeriesRef.current.setData(data)
    chartRef.current?.timeScale().fitContent()

    const volData: HistogramData[] = candles.map((c) => ({
      time: (c.time / 1000) as any,
      value: c.volume,
      color: c.close >= c.open ? '#00bfa5' : '#ff6b6b',
    }))
    volSeriesRef.current?.setData(volData)
  }, [candles])

  // Add prediction markers
  useEffect(() => {
    if (!candleSeriesRef.current || predictions.length === 0) return

    // Remove old markers
    if (markersRef.current.length > 0) {
      candleSeriesRef.current.setMarkers([])
      markersRef.current = []
    }

    const markers = predictions.slice(0, 20).map((p) => ({
      time: (p.timestamp / 1000) as any,
      position: (p.direction === 'UP' ? 'belowBar' : 'aboveBar') as any,
      color: p.direction === 'UP' ? '#00bfa5' : '#ff6b6b',
      shape: (p.direction === 'UP' ? 'arrowUp' : 'arrowDown') as any,
      text: `${p.direction} ${(p.confidence * 100).toFixed(0)}%`,
      size: Math.max(1, Math.min(3, Math.round(p.confidence * 3))) as any,
    }))

    candleSeriesRef.current.setMarkers(markers)
    markersRef.current = markers
  }, [predictions])

  // Live tick updates the latest candle
  useEffect(() => {
    if (!candleSeriesRef.current || !latestPrice || candles.length === 0) return

    const lastCandle = candles[candles.length - 1]
    const minuteTs = Math.floor(latestPrice.timestamp / 60000) * 60000

    if (lastCandle.time === minuteTs) {
      candleSeriesRef.current.update({
        time: (minuteTs / 1000) as any,
        open: lastCandle.open,
        high: Math.max(lastCandle.high, latestPrice.price),
        low: Math.min(lastCandle.low, latestPrice.price),
        close: latestPrice.price,
      })
      volSeriesRef.current?.update({
        time: (minuteTs / 1000) as any,
        value: lastCandle.volume,
        color: latestPrice.price >= lastCandle.open ? '#00bfa5' : '#ff6b6b',
      })
    }
  }, [latestPrice, candles])

  return (
    <div className="vnx-card flex flex-col h-full">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-lg font-semibold text-white">HBAR / USDT</h2>
        {latestPrice && (
          <div className="flex items-center gap-4">
            <span className="text-xl font-mono font-bold text-white">
              ${latestPrice.price.toFixed(5)}
            </span>
            <span className="text-xs text-gray-400">
              Latency: {latestPrice.latency_ms.toFixed(0)}ms
            </span>
          </div>
        )}
      </div>
      <div ref={chartContainerRef} className="flex-1 w-full" />
    </div>
  )
}
