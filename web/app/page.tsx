'use client'

import { useState } from 'react'
import { Header } from '@/components/Header'
import { SearchSection } from '@/components/SearchSection'
import { CompanySnapshot } from '@/components/CompanySnapshot'
import { MetricsGrid } from '@/components/MetricsGrid'
import { FinancialCharts } from '@/components/FinancialCharts'
import { DownloadSection } from '@/components/DownloadSection'
import { UsageGuide } from '@/components/UsageGuide'

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

            <DownloadSection handleDownload={handleDownload} />
          </div>
        ) : (
          <UsageGuide />
        )}
      </div>
    </main>
  )
}
