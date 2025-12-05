import React from 'react'
import { Search } from 'lucide-react'
import { DataCollectionPrompt } from './DataCollectionPrompt'

interface SearchSectionProps {
  query: string
  setQuery: (query: string) => void
  handleSearch: (e: React.FormEvent) => void
  loading: boolean
  error: string
  collecting: boolean
  handleCollect: (ticker: string) => void
}

export function SearchSection({
  query,
  setQuery,
  handleSearch,
  loading,
  error,
  collecting,
  handleCollect
}: SearchSectionProps) {
  return (
    <section className="mb-8 md:mb-12 text-center max-w-2xl mx-auto px-4">
      <h2 className="text-3xl md:text-4xl font-extrabold text-foreground mb-3 md:mb-4 tracking-tight">
        금융 데이터를 더 쉽고 똑똑하게.
      </h2>
      <p className="text-muted-foreground mb-8 md:mb-10 text-base md:text-lg">
        AI 기반 분석으로 한국 주식 시장의 인사이트를 발견하세요.
      </p>
      
      <form onSubmit={handleSearch} className="relative group max-w-xl mx-auto">
        <div className="relative flex bg-card rounded-2xl p-2 shadow-sm border border-border focus-within:ring-2 focus-within:ring-ring transition-all">
          <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-muted-foreground w-5 h-5" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="종목코드(005930) 또는 기업명(삼성전자) 입력..."
            className="w-full bg-transparent text-foreground placeholder-muted-foreground px-12 py-3 outline-none text-lg"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-primary hover:opacity-90 text-primary-foreground px-6 py-2 rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
          >
            {loading ? '분석 중...' : '검색'}
          </button>
        </div>
      </form>

      {error && error.includes('not found') && (
        <DataCollectionPrompt 
          query={query}
          collecting={collecting}
          handleCollect={handleCollect}
        />
      )}
      
      {error && !error.includes('not found') && (
        <div className="mt-6 p-4 bg-destructive/10 border border-destructive/20 text-destructive rounded-xl text-sm">
          <p className="font-medium">{error}</p>
        </div>
      )}
    </section>
  )
}

