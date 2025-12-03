'use client'

import { useState } from 'react'
import { Search, Download, FileText, BarChart2, BookOpen } from 'lucide-react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs))
}

export default function Home() {
  const [ticker, setTicker] = useState('')
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!ticker) return

    setLoading(true)
    setError('')
    setData(null)

    try {
      const res = await fetch(`/api/analyze?ticker=${ticker}`)
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

  const handleDownload = (type: string) => {
    window.location.href = `/api/download?ticker=${ticker}&type=${type}`
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">S</div>
            <h1 className="text-xl font-bold tracking-tight">Smart Data Feeder</h1>
          </div>
          <div className="text-sm text-slate-500">v0.1.0 MVP</div>
        </div>
      </header>

      {/* Hero / Search */}
      <section className="py-20 px-4 text-center">
        <h2 className="text-4xl font-extrabold text-slate-900 mb-4">
          Investment Data for <span className="text-blue-600">Gemini</span>
        </h2>
        <p className="text-lg text-slate-600 mb-8 max-w-2xl mx-auto">
          Convert complex financial data into AI-ready formats (Markdown, CSV) instantly.
        </p>

        <form onSubmit={handleSearch} className="max-w-md mx-auto relative">
          <input
            type="text"
            placeholder="Enter Ticker (e.g., 005930)"
            className="w-full h-14 pl-12 pr-4 rounded-full border border-slate-300 shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-lg transition-all"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
          />
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-6 h-6" />
          <button 
            type="submit"
            disabled={loading}
            className="absolute right-2 top-2 bottom-2 bg-blue-600 hover:bg-blue-700 text-white px-6 rounded-full font-medium transition-colors disabled:opacity-50"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>
        
        {error && (
          <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-lg max-w-md mx-auto text-sm">
            {error}
          </div>
        )}
      </section>

      {/* Dashboard */}
      {data && (
        <section className="max-w-5xl mx-auto px-4 pb-20 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* Company Card */}
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 mb-8">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-2xl font-bold text-slate-900">{data.company.name}</h3>
                <div className="flex items-center gap-2 text-slate-500 mt-1">
                  <span className="px-2 py-0.5 bg-slate-100 rounded text-xs font-medium">{data.company.ticker}</span>
                  <span>•</span>
                  <span>{data.company.market_type}</span>
                  <span>•</span>
                  <span>{data.company.sector}</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-slate-500">Last Update</div>
                <div className="font-medium">{new Date(data.company.updated_at).toLocaleDateString()}</div>
              </div>
            </div>
            <p className="text-slate-600 leading-relaxed">
              {data.company.desc_summary}
            </p>
          </div>

          {/* Action Cards */}
          <div className="grid md:grid-cols-3 gap-6">
            {/* Card 1: Overview */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center text-blue-600 mb-4">
                <FileText className="w-6 h-6" />
              </div>
              <h4 className="text-lg font-bold mb-2">Corporate Overview</h4>
              <p className="text-sm text-slate-500 mb-6 h-10">
                Financial highlights, key metrics, and business summary.
              </p>
              <button 
                onClick={() => handleDownload('overview')}
                className="w-full py-2.5 border border-slate-300 rounded-lg font-medium text-slate-700 hover:bg-slate-50 flex items-center justify-center gap-2 transition-colors"
              >
                <Download className="w-4 h-4" /> Download .md
              </button>
            </div>

            {/* Card 2: Narratives */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-purple-50 rounded-lg flex items-center justify-center text-purple-600 mb-4">
                <BookOpen className="w-6 h-6" />
              </div>
              <h4 className="text-lg font-bold mb-2">Deep Dive Narratives</h4>
              <p className="text-sm text-slate-500 mb-6 h-10">
                Extracted text from recent disclosures and reports.
              </p>
              <button 
                onClick={() => handleDownload('narratives')}
                className="w-full py-2.5 border border-slate-300 rounded-lg font-medium text-slate-700 hover:bg-slate-50 flex items-center justify-center gap-2 transition-colors"
              >
                <Download className="w-4 h-4" /> Download .md
              </button>
            </div>

            {/* Card 3: Chart Data */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center text-green-600 mb-4">
                <BarChart2 className="w-6 h-6" />
              </div>
              <h4 className="text-lg font-bold mb-2">Market Data</h4>
              <p className="text-sm text-slate-500 mb-6 h-10">
                Daily OHLCV data with Moving Averages for analysis.
              </p>
              <button 
                onClick={() => handleDownload('chart')}
                className="w-full py-2.5 border border-slate-300 rounded-lg font-medium text-slate-700 hover:bg-slate-50 flex items-center justify-center gap-2 transition-colors"
              >
                <Download className="w-4 h-4" /> Download .csv
              </button>
            </div>
          </div>
        </section>
      )}
    </main>
  )
}
