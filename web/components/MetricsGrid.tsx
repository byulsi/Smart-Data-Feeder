import React from 'react'
import { DollarSign, TrendingUp, BarChart2, Activity } from 'lucide-react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs))
}

interface MetricsGridProps {
  company: any
  financials: any[]
}

export function MetricsGrid({ company, financials }: MetricsGridProps) {
  // Helper to format large numbers (Trillions/Billions)
  const formatMoney = (val: number) => {
    if (!val) return '-'
    if (val >= 1_000_000_000_000) return `${(val / 1_000_000_000_000).toFixed(1)}조`
    if (val >= 100_000_000) return `${(val / 100_000_000).toFixed(0)}억`
    return val.toLocaleString()
  }

  // Fallback Calculation for PER/PBR if DB value is missing
  const latestFinancial = financials[0] || {}
  
  let per = latestFinancial.per
  let pbr = latestFinancial.pbr
  
  // If PER is missing but we have Net Income and Market Cap
  if (!per && latestFinancial.net_income && company.market_cap) {
    // Annualize Net Income if it looks like a quarterly figure (simple heuristic)
    // Or just use as is if it's yearly. 
    // For safety, let's just use the raw value if it's reasonable, or skip.
    // Better heuristic: If net_income is < 1/10th of market cap, it might be quarterly? 
    // Let's just try to calculate Price / EPS if we have EPS.
    if (latestFinancial.eps) {
       // We need price. We don't have price here, only market cap.
       // Price = Market Cap / Shares. 
       // Let's use Market Cap / Net Income directly.
       // Assuming Net Income is for the period. If it's quarterly, we should multiply by 4.
       // But `latestFinancial` might be yearly (quarter=0).
       const factor = latestFinancial.quarter === 0 ? 1 : 4
       per = (company.market_cap / (latestFinancial.net_income * factor)).toFixed(2)
    }
  }

  // If PBR is missing
  if (!pbr && latestFinancial.equity && company.market_cap) {
    pbr = (company.market_cap / latestFinancial.equity).toFixed(2)
  }

  const metrics = [
    { label: '시가총액', value: formatMoney(company.market_cap), icon: DollarSign, color: 'text-foreground' },
    { label: '주가수익비율(PER)', value: per ? `${per}배` : '-', icon: TrendingUp, color: 'text-foreground' },
    { label: '주가순자산비율(PBR)', value: pbr ? `${pbr}배` : '-', icon: BarChart2, color: 'text-foreground' },
    { label: '자기자본이익률(ROE)', value: latestFinancial.roe ? `${latestFinancial.roe}%` : '-', icon: Activity, color: 'text-foreground' },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 mb-8">
      {metrics.map((metric, i) => (
        <div key={i} className="bg-card border border-border p-4 md:p-6 rounded-2xl shadow-sm hover:shadow-md transition-all group">
          <div className="flex items-center gap-2 mb-2 md:mb-3">
            <div className={`p-1.5 md:p-2 rounded-lg bg-secondary text-foreground group-hover:bg-primary group-hover:text-primary-foreground transition-colors`}>
              <metric.icon className="w-4 h-4 md:w-5 md:h-5" />
            </div>
            <span className="text-xs md:text-sm text-muted-foreground font-medium">{metric.label}</span>
          </div>
          <div className={`text-xl md:text-2xl font-bold tracking-tight ${metric.color}`}>
            {metric.value}
          </div>
        </div>
      ))}
    </div>
  )
}
