'use client'

import React, { useMemo } from 'react'
import { 
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  ReferenceLine, Cell
} from 'recharts'

interface SmartChartProps {
  market: any[]
  height?: number | string
}

export function SmartChart({ market, height = 400 }: SmartChartProps) {
  
  // 1. Process Market Data for Chart
  const chartData = useMemo(() => {
    if (!market || market.length === 0) return []
    
    // Sort by date ascending just in case
    const sorted = [...market].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    
    return sorted.map(d => ({
      ...d,
      // Ensure numbers
      open: Number(d.open),
      high: Number(d.high),
      low: Number(d.low),
      close: Number(d.close),
      volume: Number(d.volume),
      ma5: Number(d.ma5),
      ma20: Number(d.ma20),
      ma60: Number(d.ma60),
      // For candle color
      isUp: Number(d.close) >= Number(d.open)
    }))
  }, [market])

  // 2. Calculate Support/Resistance (Volume Profile)
  const supportResistanceLines = useMemo(() => {
    if (chartData.length === 0) return []

    const prices = chartData.map(d => d.close)
    const minPrice = Math.min(...prices)
    const maxPrice = Math.max(...prices)
    const range = maxPrice - minPrice
    const buckets = 20
    const bucketSize = range / buckets
    
    const volumeProfile = new Array(buckets).fill(0)
    
    chartData.forEach(d => {
      const bucketIndex = Math.min(
        Math.floor((d.close - minPrice) / bucketSize), 
        buckets - 1
      )
      volumeProfile[bucketIndex] += d.volume
    })

    // Find peaks (simple local maxima)
    const peaks = []
    for (let i = 1; i < buckets - 1; i++) {
      if (volumeProfile[i] > volumeProfile[i-1] && volumeProfile[i] > volumeProfile[i+1]) {
        peaks.push({
          price: minPrice + (i + 0.5) * bucketSize,
          volume: volumeProfile[i]
        })
      }
    }

    // Sort by volume and take top 3
    return peaks.sort((a, b) => b.volume - a.volume).slice(0, 3).map(p => p.price)
  }, [chartData])

  // Prepare data for Floating Bar (Candle Body)
  const candleData = chartData.map(d => ({
    ...d,
    body: [Math.min(d.open, d.close), Math.max(d.open, d.close)],
    color: d.close >= d.open ? '#ef4444' : '#3b82f6' // Keep Red/Blue for market standard
  }))

  return (
    <div style={{ height, width: '100%' }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={candleData} margin={{ top: 20, right: 0, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="currentColor" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="currentColor" stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} opacity={0.5} />
          <XAxis 
            dataKey="date" 
            stroke="var(--muted-foreground)" 
            tick={{fontSize: 11}} 
            tickFormatter={(val) => new Date(val).toLocaleDateString(undefined, {month:'short', day:'numeric'})}
            minTickGap={30}
          />
          <YAxis 
            yAxisId="price"
            domain={['auto', 'auto']} 
            stroke="var(--muted-foreground)" 
            tick={{fontSize: 11}} 
            tickFormatter={(val) => val.toLocaleString()}
            orientation="right"
          />
          <YAxis 
            yAxisId="volume"
            orientation="left"
            stroke="var(--muted-foreground)"
            tick={false}
            axisLine={false}
            domain={[0, 'dataMax * 4']} // Push volume down
          />
          <Tooltip 
            contentStyle={{ backgroundColor: 'var(--card)', borderColor: 'var(--border)', color: 'var(--foreground)' }}
            labelFormatter={(label) => new Date(label).toLocaleDateString()}
            formatter={(value: any, name: string) => [
              typeof value === 'number' ? value.toLocaleString() : value,
              name === 'body' ? 'Price' : name.toUpperCase()
            ]}
          />
          
          {/* Volume */}
          <Bar dataKey="volume" yAxisId="volume" fill="var(--muted-foreground)" barSize={4} radius={[2, 2, 0, 0]} opacity={0.3} />

          {/* Moving Averages */}
          <Line type="monotone" dataKey="ma5" yAxisId="price" stroke="#fbbf24" dot={false} strokeWidth={1} name="MA5" />
          <Line type="monotone" dataKey="ma20" yAxisId="price" stroke="#f87171" dot={false} strokeWidth={1} name="MA20" />
          <Line type="monotone" dataKey="ma60" yAxisId="price" stroke="#34d399" dot={false} strokeWidth={1} name="MA60" />

          {/* Candle Body (Floating Bar) */}
          <Bar dataKey="body" yAxisId="price" barSize={8}>
            {candleData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>

          {/* Support/Resistance Lines */}
          {supportResistanceLines.map((price, i) => (
            <ReferenceLine 
              key={i} 
              y={price} 
              yAxisId="price" 
              stroke="var(--foreground)" 
              strokeDasharray="3 3" 
              strokeOpacity={0.3}
              label={{ 
                value: 'S/R', 
                position: 'insideLeft', 
                fill: 'var(--muted-foreground)', 
                fontSize: 10 
              }} 
            />
          ))}

        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
