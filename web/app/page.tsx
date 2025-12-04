'use client'

import { useState } from 'react'
import { Search, Download, FileText, BarChart2, BookOpen, TrendingUp, Users, PieChart, Activity, DollarSign } from 'lucide-react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts'

export function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs))
}

export default function Home() {
  const [query, setQuery] = useState('')
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [collecting, setCollecting] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query) return

    setLoading(true)
    setError('')
    setData(null)

    try {
      const res = await fetch(`/api/analyze?query=${encodeURIComponent(query)}`)
      if (!res.ok) {
        if (res.status === 404) throw new Error('Data not found. Please run the collector first.')
        throw new Error('Failed to fetch data')
      }
      const json = await res.json()
      setData(json)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCollect = async (ticker: string) => {
    if (!ticker) return
    setCollecting(true)
    try {
      const res = await fetch('/api/collect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker })
      })
      
      if (!res.ok) {
        const json = await res.json()
        throw new Error(json.error || 'Collection failed')
      }
      
      // Success! Retry search
      handleSearch(new Event('submit') as any)
      
    } catch (err: any) {
      setError(err.message)
    } finally {
      setCollecting(false)
    }
  }

  const handleDownload = (type: string) => {
    if (!data) return
    window.location.href = `/api/download?ticker=${data.company.ticker}&type=${type}`
  }

  // Helper to format large numbers (Trillions/Billions)
  const formatMoney = (val: number) => {
    if (!val) return '-'
    if (val >= 1_000_000_000_000) return `${(val / 1_000_000_000_000).toFixed(1)}조`
    if (val >= 100_000_000) return `${(val / 100_000_000).toFixed(0)}억`
    return val.toLocaleString()
  }

  return (
    <main className="min-h-screen bg-slate-900 text-slate-100 font-sans selection:bg-blue-500 selection:text-white">
      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/20">S</div>
            <h1 className="text-xl font-bold tracking-tight text-slate-100">Smart Data Feeder</h1>
          </div>
          <div className="flex items-center gap-4">
             <span className="px-2 py-1 rounded bg-blue-500/10 text-blue-400 text-xs font-medium border border-blue-500/20">v2.0 Enterprise</span>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Search Section */}
        <section className="mb-12 text-center max-w-2xl mx-auto">
          <h2 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400 mb-4">
            Financial Intelligence, Simplified.
          </h2>
          <p className="text-slate-400 mb-8 text-lg">
            Deep dive into Korean market data with AI-powered insights.
          </p>
          
          <form onSubmit={handleSearch} className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-200"></div>
            <div className="relative flex bg-slate-800 rounded-xl p-2 shadow-2xl border border-slate-700">
              <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500 w-5 h-5" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search Ticker (005930) or Name (삼성전자)..."
                className="w-full bg-transparent text-slate-100 placeholder-slate-500 px-12 py-3 outline-none text-lg"
              />
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-2 rounded-lg font-medium transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Analyzing...' : 'Search'}
              </button>
            </div>
          </form>

          {error && (
            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm animate-in fade-in slide-in-from-top-2">
              <p className="font-medium mb-2">{error}</p>
              {error.includes('not found') && (
                <button
                  onClick={() => handleCollect(query)}
                  disabled={collecting}
                  className="bg-red-500/20 hover:bg-red-500/30 text-red-300 px-4 py-2 rounded-lg text-xs transition-colors flex items-center justify-center gap-2 mx-auto"
                >
                  {collecting ? 'Collecting Data...' : 'Start Data Collection'}
                </button>
              )}
            </div>
          )}
        </section>

        {/* Results Section */}
        {data && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            {/* 1. Company Header */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-8 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none"></div>
              
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <h2 className="text-3xl font-bold text-white">{data.company.name}</h2>
                    <span className="text-slate-400 text-xl font-light">{data.company.ticker}</span>
                    <span className="bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded text-xs font-medium border border-blue-500/30">{data.company.market_type}</span>
                  </div>
                  <div className="flex gap-4 text-sm text-slate-400">
                    <span>{data.company.sector}</span>
                    <span className="w-px h-4 bg-slate-700"></span>
                    <span>Est. {data.company.est_dt}</span>
                  </div>
                </div>
                
                <div className="flex gap-3">
                   <button
                    onClick={() => handleCollect(data.company.ticker)}
                    disabled={collecting}
                    className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-slate-300 px-4 py-2 rounded-lg text-sm transition-colors"
                  >
                    <Activity className={cn("w-4 h-4", collecting && "animate-spin")} />
                    {collecting ? 'Updating...' : 'Update Data'}
                  </button>
                </div>
              </div>
              
              <p className="mt-6 text-slate-300 leading-relaxed max-w-4xl">
                {data.company.desc_summary}
              </p>
            </div>

            {/* 2. Key Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Market Cap', value: formatMoney(data.company.market_cap), icon: DollarSign, color: 'text-emerald-400' },
                { label: 'PER', value: data.financials[0]?.per ? `${data.financials[0].per}x` : '-', icon: TrendingUp, color: 'text-blue-400' },
                { label: 'PBR', value: data.financials[0]?.pbr ? `${data.financials[0].pbr}x` : '-', icon: BarChart2, color: 'text-purple-400' },
                { label: 'ROE', value: data.financials[0]?.roe ? `${data.financials[0].roe}%` : '-', icon: Activity, color: 'text-orange-400' },
              ].map((metric, i) => (
                <div key={i} className="bg-slate-800/50 border border-slate-700 p-5 rounded-xl hover:bg-slate-800 transition-colors">
                  <div className="flex items-center gap-2 mb-2">
                    <metric.icon className={cn("w-4 h-4", metric.color)} />
                    <span className="text-slate-400 text-sm font-medium">{metric.label}</span>
                  </div>
                  <div className="text-2xl font-bold text-slate-100">{metric.value}</div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* 3. Financial Charts */}
              <div className="lg:col-span-2 bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
                  <BarChart2 className="w-5 h-5 text-blue-400" />
                  Financial Performance
                </h3>
                <div className="h-80 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={[...data.financials].reverse()}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                      <XAxis dataKey="year" stroke="#94a3b8" tick={{fontSize: 12}} />
                      <YAxis stroke="#94a3b8" tick={{fontSize: 12}} tickFormatter={(val) => `${val/100000000}억`} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f1f5f9' }}
                        formatter={(val: number) => formatMoney(val)}
                      />
                      <Legend />
                      <Bar dataKey="revenue" name="Revenue" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="op_profit" name="Op. Profit" fill="#10b981" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="net_income" name="Net Income" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* 4. R&D & Shareholders */}
              <div className="space-y-4">
                 {/* R&D Card */}
                 <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
                    <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                      <Activity className="w-5 h-5 text-pink-400" />
                      R&D Investment
                    </h3>
                    <div className="text-3xl font-bold text-white mb-1">
                      {formatMoney(data.financials[0]?.rnd_expenses)}
                    </div>
                    <div className="text-sm text-slate-400">Latest Annual/Quarterly Spending</div>
                 </div>

                 {/* Shareholders Card */}
                 <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 flex-1">
                    <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                      <Users className="w-5 h-5 text-yellow-400" />
                      Major Shareholders
                    </h3>
                    <div className="space-y-3">
                      {data.shareholders.map((holder: any, i: number) => (
                        <div key={i} className="flex justify-between items-center text-sm">
                          <span className="text-slate-300">{holder.holder_name}</span>
                          <span className="font-mono font-medium text-blue-300">{holder.share_ratio}%</span>
                        </div>
                      ))}
                      {data.shareholders.length === 0 && (
                        <div className="text-slate-500 text-sm">No shareholder data available.</div>
                      )}
                    </div>
                 </div>
              </div>
            </div>

            {/* 5. Download Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
              <button onClick={() => handleDownload('overview')} className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 px-6 py-4 rounded-xl font-medium transition-all group">
                <FileText className="w-5 h-5 text-blue-400 group-hover:scale-110 transition-transform" />
                <span>Overview Report (.md)</span>
              </button>
              <button onClick={() => handleDownload('narratives')} className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 px-6 py-4 rounded-xl font-medium transition-all group">
                <BookOpen className="w-5 h-5 text-purple-400 group-hover:scale-110 transition-transform" />
                <span>Deep Dive Report (.md)</span>
              </button>
              <button onClick={() => handleDownload('chart')} className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 px-6 py-4 rounded-xl font-medium transition-all group">
                <Download className="w-5 h-5 text-emerald-400 group-hover:scale-110 transition-transform" />
                <span>Market Data (.csv)</span>
              </button>
            </div>

          </div>
        )}
      </div>
    </main>
  )
}
