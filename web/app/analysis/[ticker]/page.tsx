'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Header } from '@/components/Header'
import { TabView } from '@/components/analysis/TabView'
import { CompanySnapshot } from '@/components/CompanySnapshot'
import { MetricsGrid } from '@/components/MetricsGrid'
import { FinancialCharts } from '@/components/FinancialCharts'
import { DownloadSection } from '@/components/DownloadSection'
import { AITools } from '@/components/analysis/AITools'
import { Narratives } from '@/components/analysis/Narratives'
import { ArrowLeft } from 'lucide-react'

export default function AnalysisPage() {
  const params = useParams()
  const router = useRouter()
  const ticker = params.ticker as string
  
  const [activeTab, setActiveTab] = useState('overview')
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!ticker) return

    const fetchData = async () => {
      setLoading(true)
      try {
        // Reuse the existing analyze API
        // In a real app, we might want a dedicated endpoint by ticker, but search works if ticker is exact
        const res = await fetch(`/api/analyze?query=${ticker}`)
        if (!res.ok) {
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

    fetchData()
  }, [ticker])

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-background p-8 text-center">
        <h1 className="text-xl font-bold mb-4">Error loading data</h1>
        <p className="text-muted-foreground mb-4">{error}</p>
        <button onClick={() => router.push('/')} className="text-primary hover:underline">
          Go back home
        </button>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-background text-foreground pb-20">
      <Header />
      
      {/* Sticky Sub-header for Mobile Context */}
      <div className="sticky top-0 z-30 bg-background/95 backdrop-blur border-b border-border px-4 py-3 flex items-center gap-3">
        <button onClick={() => router.push('/')} className="p-1 hover:bg-accent rounded-full">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="font-bold text-sm leading-tight">{data.company.name}</h1>
          <span className="text-xs text-muted-foreground">{data.company.ticker}</span>
        </div>
      </div>

      <TabView activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'overview' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2">
            <CompanySnapshot 
              company={data.company}
              market={data.market}
              segments={data.segments}
            />
            <MetricsGrid 
              company={data.company}
              financials={data.financials}
            />
            
            <div className="pt-4 border-t border-border">
              <h3 className="text-lg font-bold mb-4">데이터 다운로드</h3>
              <DownloadSection handleDownload={(type) => window.location.href = `/api/download?ticker=${data.company.ticker}&type=${type}`} />
            </div>
          </div>
        )}

        {activeTab === 'financials' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2">
            <FinancialCharts 
              financials={data.financials}
              shareholders={data.shareholders}
            />
          </div>
        )}



        {activeTab === 'narratives' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2">
             <Narratives narratives={data.narratives} />
          </div>
        )}

        {activeTab === 'ai' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2">
            <AITools data={data} />
          </div>
        )}
      </div>
      
      {/* Mobile Download/Action Bar (Optional, maybe later) */}
    </main>
  )
}
