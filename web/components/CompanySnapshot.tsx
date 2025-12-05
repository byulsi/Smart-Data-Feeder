import React, { useMemo, useState } from 'react'
import { ZoomIn, ZoomOut } from 'lucide-react'
import { SmartChart } from './SmartChart'

interface CompanySnapshotProps {
  company: any
  market: any[]
  segments: any[]
}

export function CompanySnapshot({ company, market, segments }: CompanySnapshotProps) {
  // Default to showing last 90 days (approx 3 months)
  const [visibleCount, setVisibleCount] = useState(90)

  // Filter market data based on visibleCount
  const visibleMarketData = useMemo(() => {
    if (!market || market.length === 0) return []
    // Sort by date ascending
    const sorted = [...market].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    // Take the last N items
    return sorted.slice(-visibleCount)
  }, [market, visibleCount])

  const handleZoomIn = () => {
    // Decrease visible count (show fewer days -> zoom in)
    setVisibleCount(prev => Math.max(30, prev - 30))
  }

  const handleZoomOut = () => {
    // Increase visible count (show more days -> zoom out)
    setVisibleCount(prev => Math.min(market.length, prev + 30))
  }

  // Process Segments for Business Mix
  const segmentData = useMemo(() => {
    if (!segments || segments.length === 0) return []
    // Filter for latest period
    const latestPeriod = segments[0].period
    const currentSegments = segments.filter(s => s.period === latestPeriod)
    
    // Calculate total revenue for percentage
    const totalRevenue = currentSegments.reduce((sum, s) => sum + Number(s.revenue), 0)
    
    return currentSegments.map(s => ({
      name: s.division,
      value: Number(s.revenue),
      percent: (Number(s.revenue) / totalRevenue) * 100
    })).sort((a, b) => b.value - a.value) // Sort largest first
  }, [segments])

  return (
    <div className="bg-card border border-border rounded-2xl p-6 md:p-8 mb-8 shadow-sm">
      
      {/* 1. Header & Business Mix */}
      <div className="flex flex-col lg:flex-row gap-8 mb-8">
        {/* Identity */}
        <div className="flex-1">
          <div className="flex items-baseline gap-3 mb-2">
            <h2 className="text-3xl font-bold text-foreground">{company.name}</h2>
            <span className="text-muted-foreground text-xl font-light">{company.ticker}</span>
          </div>
          <div className="flex gap-3 text-sm text-muted-foreground mb-4">
            <span className="bg-secondary px-2 py-0.5 rounded text-secondary-foreground border border-border">{company.market_type}</span>
            <span className="bg-secondary px-2 py-0.5 rounded text-secondary-foreground border border-border">{company.sector}</span>
          </div>
          <p className="text-foreground leading-relaxed text-sm md:text-base max-w-2xl">
            {company.desc_summary}
          </p>
        </div>

        {/* Business Mix */}
        <div className="lg:w-1/3">
          <h3 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider">사업 부문별 매출 비중</h3>
          <div className="space-y-3">
            {segmentData.slice(0, 4).map((seg, i) => (
              <div key={i} className="group">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-foreground">{seg.name}</span>
                  <span className="text-muted-foreground">{seg.percent.toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-secondary rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-foreground rounded-full transition-all duration-500"
                    style={{ width: `${seg.percent}%` }}
                  />
                </div>
              </div>
            ))}
            {segmentData.length > 4 && (
              <p className="text-xs text-muted-foreground text-right">+ {segmentData.length - 4}개 더보기</p>
            )}
          </div>
        </div>
      </div>

      {/* 2. Smart Chart */}
      <div className="w-full relative">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">스마트 차트 (일봉)</h3>
          
          {/* Zoom Controls */}
          <div className="flex items-center gap-1 bg-secondary/50 rounded-lg p-1">
            <button 
              onClick={handleZoomOut}
              disabled={visibleCount >= market.length}
              className="p-1.5 hover:bg-background rounded-md text-muted-foreground hover:text-foreground transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              aria-label="축소 (기간 확대)"
              title="축소 (기간 확대)"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <div className="w-[1px] h-4 bg-border mx-1"></div>
            <button 
              onClick={handleZoomIn}
              disabled={visibleCount <= 30}
              className="p-1.5 hover:bg-background rounded-md text-muted-foreground hover:text-foreground transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              aria-label="확대 (기간 축소)"
              title="확대 (기간 축소)"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        <SmartChart market={visibleMarketData} height={400} />
      </div>
    </div>
  )
}
