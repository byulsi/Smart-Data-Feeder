'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Header } from '@/components/Header'
import { SearchSection } from '@/components/SearchSection'
import { UsageGuide } from '@/components/UsageGuide'

export default function Home() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [collecting, setCollecting] = useState(false)
  const router = useRouter()

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query) return

    setLoading(true)
    setError('')

    try {
      // Check if data exists first
      const res = await fetch(`/api/analyze?query=${encodeURIComponent(query)}`)
      if (!res.ok) {
        if (res.status === 404) throw new Error('Data not found. Please run the collector first.')
        throw new Error('Failed to fetch data')
      }
      const json = await res.json()
      
      // Redirect to analysis page
      router.push(`/analysis/${json.company.ticker}`)
      
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
      
      // Success! Redirect to analysis
      // We assume the ticker is what we searched for. 
      // Ideally the API returns the ticker, but we can use the input for now.
      // Wait a bit for DB to settle? usually fast enough.
      router.push(`/analysis/${ticker}`)
      
    } catch (err: any) {
      setError(err.message)
    } finally {
      setCollecting(false)
    }
  }

  return (
    <main className="min-h-screen bg-background text-foreground font-sans selection:bg-primary selection:text-primary-foreground flex flex-col">
      <Header />

      <div className="flex-1 flex flex-col items-center justify-center p-4 md:p-6 -mt-20">
        <div className="w-full max-w-2xl space-y-8">
          <div className="text-center space-y-4">
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
              Smart Investment Analysis
            </h1>
            <p className="text-muted-foreground text-lg">
              AI-powered insights for smarter decisions.
            </p>
          </div>

          <SearchSection 
            query={query}
            setQuery={setQuery}
            handleSearch={handleSearch}
            loading={loading}
            error={error}
            collecting={collecting}
            handleCollect={handleCollect}
          />
          
          <div className="pt-8">
             <UsageGuide />
          </div>
        </div>
      </div>
    </main>
  )
}
