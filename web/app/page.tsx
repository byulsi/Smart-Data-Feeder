'use client'

import { useState } from 'react'
import { Search, Download, FileText, BarChart2, BookOpen } from 'lucide-react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs))
}

export default function Home() {
  const [query, setQuery] = useState('')
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

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

  const [collecting, setCollecting] = useState(false)

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


        {/* Search Section */}
        <section className="bg-white rounded-xl shadow-sm p-8 mb-8">
          <form onSubmit={handleSearch} className="flex gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="종목코드 (예: 005930) 또는 기업명 (예: 삼성전자)"
              className="flex-1 rounded-lg border-gray-300 border px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {loading ? '검색 중...' : '검색'}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-lg max-w-md mx-auto text-sm">
              {error}
              {error.includes('not found') && (
                 <div className="mt-3">
                   <button
                     onClick={() => handleCollect(query)}
                     disabled={collecting}
                     className="bg-red-100 hover:bg-red-200 text-red-700 px-4 py-2 rounded-md font-medium text-xs transition-colors disabled:opacity-50 flex items-center justify-center gap-2 mx-auto"
                   >
                     {collecting ? (
                       <>
                         <span className="w-3 h-3 border-2 border-red-700 border-t-transparent rounded-full animate-spin"></span>
                         데이터 수집 중 (약 20초 소요)...
                       </>
                     ) : (
                       '지금 데이터 수집하기'
                     )}
                   </button>
                 </div>
              )}
            </div>
          )}
        </section>

        {/* Results Section */}
        {data && (
          <div className="space-y-6">
            {/* Company Card */}
            <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-blue-500">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    {data.company.name} <span className="text-gray-500 text-lg">({data.company.ticker})</span>
                  </h2>
                  <div className="flex gap-3 text-sm text-gray-600 mb-4">
                    <span className="bg-gray-100 px-2 py-1 rounded">{data.company.market_type}</span>
                    <span className="bg-gray-100 px-2 py-1 rounded">{data.company.sector}</span>
                    {data.company.est_dt && <span className="bg-gray-100 px-2 py-1 rounded">설립일: {data.company.est_dt}</span>}
                    {data.company.listing_dt && <span className="bg-gray-100 px-2 py-1 rounded">상장일: {data.company.listing_dt}</span>}
                  </div>
                  <p className="text-gray-700 leading-relaxed">
                    {data.company.desc_summary}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-500 mb-1">최근 업데이트</div>
                  <div className="font-medium mb-2">{new Date(data.company.updated_at).toLocaleDateString()}</div>
                  <button
                    onClick={() => handleCollect(data.company.ticker)}
                    disabled={collecting}
                    className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded transition-colors disabled:opacity-50 flex items-center gap-1 ml-auto"
                  >
                    {collecting ? (
                      <>
                        <span className="w-3 h-3 border-2 border-gray-500 border-t-transparent rounded-full animate-spin"></span>
                        업데이트 중...
                      </>
                    ) : (
                      <>
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        데이터 업데이트
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Financial Highlights */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-gray-500 text-sm font-medium mb-2">매출액 (최근 연간)</h3>
                <p className="text-2xl font-bold text-gray-900">
                  {data.financials[0]?.revenue ? Number(data.financials[0].revenue).toLocaleString() : '-'} <span className="text-sm font-normal text-gray-500">KRW</span>
                </p>
              </div>
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-gray-500 text-sm font-medium mb-2">영업이익 (최근 연간)</h3>
                <p className="text-2xl font-bold text-gray-900">
                  {data.financials[0]?.op_profit ? Number(data.financials[0].op_profit).toLocaleString() : '-'} <span className="text-sm font-normal text-gray-500">KRW</span>
                </p>
              </div>
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-gray-500 text-sm font-medium mb-2">순이익 (최근 연간)</h3>
                <p className="text-2xl font-bold text-gray-900">
                  {data.financials[0]?.net_income ? Number(data.financials[0].net_income).toLocaleString() : '-'} <span className="text-sm font-normal text-gray-500">KRW</span>
                </p>
              </div>
            </div>

            {/* Market Data */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">주가 정보 (최근 1년)</h3>
              <div className="h-64 flex items-end justify-between gap-1 px-4 border-b border-gray-200 pb-4">
                {data.market.slice(-30).map((m: any, i: number) => (
                  <div 
                    key={i} 
                    className="bg-blue-500 w-full hover:bg-blue-600 transition-colors relative group"
                    style={{ height: `${(m.close / Math.max(...data.market.slice(-30).map((x:any) => x.close))) * 100}%` }}
                  >
                    <div className="opacity-0 group-hover:opacity-100 absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-gray-900 text-white text-xs py-1 px-2 rounded whitespace-nowrap z-10">
                      {m.date}: {m.close.toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 flex justify-between text-sm text-gray-500">
                <span>30일 전</span>
                <span>오늘</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4 justify-center pt-8">
              <button 
                onClick={() => handleDownload('overview')}
                className="flex items-center gap-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 px-6 py-3 rounded-lg font-medium transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                기업 개요 다운로드 (.md)
              </button>
              <button 
                onClick={() => handleDownload('narratives')}
                className="flex items-center gap-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 px-6 py-3 rounded-lg font-medium transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                심층 분석 리포트 다운로드 (.md)
              </button>
              <button 
                onClick={() => handleDownload('chart')}
                className="flex items-center gap-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 px-6 py-3 rounded-lg font-medium transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                주가 데이터 다운로드 (.csv)
              </button>
            </div>
          </div>
        )}

    </main>
  )
}
