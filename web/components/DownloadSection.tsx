import React from 'react'
import { FileText, BookOpen, Download } from 'lucide-react'

interface DownloadSectionProps {
  handleDownload: (type: string) => void
}

export function DownloadSection({ handleDownload }: DownloadSectionProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4 pt-4">
      <button onClick={() => handleDownload('overview')} className="flex items-center justify-center gap-2 bg-card hover:bg-secondary border border-border text-foreground px-6 py-3 md:py-4 rounded-xl font-medium transition-all group shadow-sm">
        <FileText className="w-4 h-4 md:w-5 md:h-5 text-muted-foreground group-hover:text-foreground transition-colors" />
        <span className="text-sm md:text-base">기업 개요 및 재무 데이터 (.md)</span>
      </button>
      <button onClick={() => handleDownload('narratives')} className="flex items-center justify-center gap-2 bg-card hover:bg-secondary border border-border text-foreground px-6 py-3 md:py-4 rounded-xl font-medium transition-all group shadow-sm">
        <BookOpen className="w-4 h-4 md:w-5 md:h-5 text-muted-foreground group-hover:text-foreground transition-colors" />
        <span className="text-sm md:text-base">사업 보고서 심층 분석 (.md)</span>
      </button>
      <button onClick={() => handleDownload('chart')} className="flex items-center justify-center gap-2 bg-card hover:bg-secondary border border-border text-foreground px-6 py-3 md:py-4 rounded-xl font-medium transition-all group shadow-sm">
        <Download className="w-4 h-4 md:w-5 md:h-5 text-muted-foreground group-hover:text-foreground transition-colors" />
        <span className="text-sm md:text-base">주가 및 거래량 데이터 (.csv)</span>
      </button>
    </div>
  )
}
