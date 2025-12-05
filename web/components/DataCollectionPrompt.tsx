import React from 'react'
import { Database, ArrowRight } from 'lucide-react'

interface DataCollectionPromptProps {
  query: string
  collecting: boolean
  handleCollect: (ticker: string) => void
}

export function DataCollectionPrompt({ query, collecting, handleCollect }: DataCollectionPromptProps) {
  return (
    <div className="max-w-md mx-auto mt-8 p-8 bg-card border border-border rounded-2xl shadow-sm text-center animate-in fade-in slide-in-from-bottom-2">
      <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center mx-auto mb-6">
        <Database className="w-8 h-8 text-primary" />
      </div>
      
      <h3 className="text-xl font-bold text-foreground mb-3">
        데이터 수집 필요
      </h3>
      <p className="text-muted-foreground mb-8 leading-relaxed">
        아직 데이터베이스에 없는 기업입니다.<br/>
        실시간으로 데이터를 수집하고 분석하시겠습니까?
      </p>

      <button
        onClick={() => handleCollect(query)}
        disabled={collecting}
        className="w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground hover:opacity-90 px-6 py-4 rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {collecting ? (
          <>
            <div className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
            <span>수집 및 분석 중...</span>
          </>
        ) : (
          <>
            <span>수집 및 분석 시작</span>
            <ArrowRight className="w-4 h-4" />
          </>
        )}
      </button>
    </div>
  )
}
