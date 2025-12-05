import React from 'react'
import { BarChart2, Activity, Users } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts'

interface FinancialChartsProps {
  financials: any[]
  shareholders: any[]
}

export function FinancialCharts({ financials, shareholders }: FinancialChartsProps) {
  // Helper to format large numbers (Trillions/Billions)
  const formatMoney = (val: number) => {
    if (!val) return '-'
    if (val >= 1_000_000_000_000) return `${(val / 1_000_000_000_000).toFixed(1)}조`
    if (val >= 100_000_000) return `${(val / 100_000_000).toFixed(0)}억`
    return val.toLocaleString()
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">
      {/* Financial Performance Chart */}
      <div className="lg:col-span-2 bg-card border border-border rounded-2xl p-4 md:p-6 shadow-sm">
        <h3 className="text-base md:text-lg font-bold text-foreground mb-4 md:mb-6 flex items-center gap-2">
          <BarChart2 className="w-4 h-4 md:w-5 md:h-5 text-muted-foreground" />
          재무 성과
        </h3>
        <div className="h-64 md:h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={[...financials].reverse()}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="year" stroke="var(--muted-foreground)" tick={{fontSize: 12}} />
              <YAxis stroke="var(--muted-foreground)" tick={{fontSize: 12}} tickFormatter={(val) => `${val/100000000}억`} width={60} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'var(--card)', borderColor: 'var(--border)', color: 'var(--foreground)' }}
                formatter={(val: number) => formatMoney(val)}
              />
              <Legend wrapperStyle={{ paddingTop: '10px' }} />
              <Bar dataKey="revenue" name="매출액" fill="var(--foreground)" radius={[4, 4, 0, 0]} opacity={0.8} />
              <Bar dataKey="op_profit" name="영업이익" fill="var(--muted-foreground)" radius={[4, 4, 0, 0]} opacity={0.6} />
              <Bar dataKey="net_income" name="순이익" fill="var(--muted-foreground)" radius={[4, 4, 0, 0]} opacity={0.3} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* R&D & Shareholders */}
      <div className="space-y-4">
         {/* R&D Card */}
         <div className="bg-card border border-border rounded-2xl p-4 md:p-6 shadow-sm">
            <h3 className="text-base md:text-lg font-bold text-foreground mb-3 md:mb-4 flex items-center gap-2">
              <Activity className="w-4 h-4 md:w-5 md:h-5 text-muted-foreground" />
              연구개발비 (R&D)
            </h3>
            <div className="text-2xl md:text-3xl font-bold text-foreground mb-1">
              {formatMoney(financials[0]?.rnd_expenses)}
            </div>
            <div className="text-xs md:text-sm text-muted-foreground">최근 연간/분기 지출</div>
         </div>

         {/* Shareholders Card */}
         <div className="bg-card border border-border rounded-2xl p-4 md:p-6 flex-1 shadow-sm">
            <h3 className="text-base md:text-lg font-bold text-foreground mb-3 md:mb-4 flex items-center gap-2">
              <Users className="w-4 h-4 md:w-5 md:h-5 text-muted-foreground" />
              주요 주주
            </h3>
            <div className="space-y-3">
              {shareholders.map((holder: any, i: number) => (
                <div key={i} className="flex justify-between items-center text-xs md:text-sm">
                  <span className="text-foreground truncate max-w-[150px]">{holder.holder_name}</span>
                  <span className="font-mono font-medium text-muted-foreground">{holder.share_ratio}%</span>
                </div>
              ))}
              {shareholders.length === 0 && (
                <div className="text-muted-foreground text-sm">주주 데이터가 없습니다.</div>
              )}
            </div>
         </div>
      </div>
    </div>
  )
}
