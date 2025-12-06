'use client'

import { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import { Header } from '@/components/Header'
import { SearchSection } from '@/components/SearchSection'
import { CompanySnapshot } from '@/components/CompanySnapshot'
import { MetricsGrid } from '@/components/MetricsGrid'
import { FinancialCharts } from '@/components/FinancialCharts'
import { DownloadSection } from '@/components/DownloadSection'
import { UsageGuide } from '@/components/UsageGuide'
import { AnalystSelector } from '@/components/AnalystSelector'
import ReactMarkdown from 'react-markdown'

export default function Home() {
  const [query, setQuery] = useState('')
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [collecting, setCollecting] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    if (analysisResult) {
      navigator.clipboard.writeText(analysisResult)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query) return

    setLoading(true)
    setError('')
    setData(null)
    setAnalysisResult(null)

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

  return (
    <main className="min-h-screen bg-background text-foreground font-sans selection:bg-primary selection:text-primary-foreground">
      <Header />

      <div className="max-w-7xl mx-auto px-4 md:px-6 py-8 md:py-12">
        <SearchSection 
          query={query}
          setQuery={setQuery}
          handleSearch={handleSearch}
          loading={loading}
          error={error}
          collecting={collecting}
          handleCollect={handleCollect}
        />

        {/* Results Section */}
        {data ? (
          <div className="space-y-6 md:space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <CompanySnapshot 
              company={data.company}
              market={data.market}
              segments={data.segments}
            />

            <MetricsGrid 
              company={data.company}
              financials={data.financials}
            />

            <FinancialCharts 
              financials={data.financials}
              shareholders={data.shareholders}
            />

            {/* 1. Data Download Section (Emphasized) */}
            <div className="bg-secondary/30 border border-border rounded-3xl p-6 md:p-8">
              <div className="text-center mb-6">
                <h3 className="text-xl md:text-2xl font-bold mb-2">📥 데이터 다운로드</h3>
                <p className="text-muted-foreground">
                  분석에 필요한 모든 데이터를 파일로 다운로드하세요.
                </p>
              </div>
              <DownloadSection handleDownload={handleDownload} />
            </div>

            {/* 2. Analyst Selector (Guide) */}
            <div className="border-t pt-8">
              <AnalystSelector 
                ticker={data.company.ticker} 
                onAnalysisComplete={setAnalysisResult} 
              />
            </div>

            {/* 3. Result Display */}
            {analysisResult && (
              <div className="bg-white dark:bg-slate-900 p-8 rounded-3xl shadow-lg border border-slate-200 dark:border-slate-800 animate-in fade-in zoom-in duration-300 relative group">
                <div className="absolute top-6 right-6">
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary/10 hover:bg-primary/20 text-primary font-bold transition-colors"
                  >
                    {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    {copied ? '복사완료!' : '가이드 복사'}
                  </button>
                </div>
                <div className="mb-6 pb-6 border-b border-border">
                  <h4 className="text-lg font-bold text-primary mb-1">💡 AI 질문 가이드</h4>
                  <p className="text-sm text-muted-foreground">
                    이 내용을 복사해서 ChatGPT나 Claude에게 붙여넣으세요.
                  </p>
                </div>
                <div className="prose dark:prose-invert max-w-none">
                  <ReactMarkdown>{analysisResult}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        ) : (
          <UsageGuide />
        )}
      </div>
    </main>
  )
}
