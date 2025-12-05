import React from 'react'
import { Search, FileText, TrendingUp, AlertTriangle } from 'lucide-react'

export function UsageGuide() {
  return (
    <div className="max-w-4xl mx-auto mt-12 md:mt-16 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Step 1: Search */}
        <div className="bg-card border border-border rounded-xl p-6 text-center hover:shadow-md transition-all">
          <div className="w-12 h-12 bg-secondary rounded-full flex items-center justify-center mx-auto mb-4 text-foreground">
            <Search className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-2">1. 기업 검색</h3>
          <p className="text-muted-foreground text-sm leading-relaxed">
            검색창에 <strong>종목코드(005930)</strong> 또는 <br/>
            <strong>기업명(삼성전자)</strong>을 입력하세요.
          </p>
        </div>

        {/* Step 2: Analyze */}
        <div className="bg-card border border-border rounded-xl p-6 text-center hover:shadow-md transition-all">
          <div className="w-12 h-12 bg-secondary rounded-full flex items-center justify-center mx-auto mb-4 text-foreground">
            <FileText className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-2">2. 데이터 분석</h3>
          <p className="text-muted-foreground text-sm leading-relaxed">
            AI가 분석한 <strong>기업 개요, 재무제표,</strong> <br/>
            그리고 <strong>스마트 차트</strong>를 확인하세요.
          </p>
        </div>

        {/* Step 3: Insights */}
        <div className="bg-card border border-border rounded-xl p-6 text-center hover:shadow-md transition-all">
          <div className="w-12 h-12 bg-secondary rounded-full flex items-center justify-center mx-auto mb-4 text-foreground">
            <TrendingUp className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-2">3. 인사이트 발견</h3>
          <p className="text-muted-foreground text-sm leading-relaxed">
            <strong>매출 비중</strong>과 <strong>지지/저항선</strong> 등 <br/>
            투자 판단에 도움이 되는 정보를 얻으세요.
          </p>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="mt-8 md:mt-12 p-4 bg-secondary/50 border border-border rounded-lg flex items-start gap-3 max-w-2xl mx-auto">
        <AlertTriangle className="w-5 h-5 text-muted-foreground shrink-0 mt-0.5" />
        <div className="text-xs text-muted-foreground text-left">
          <p className="font-semibold text-foreground mb-1">서비스 이용 시 주의사항</p>
          본 서비스에서 제공하는 모든 금융 데이터와 분석 정보는 투자 참고용이며, 정보의 정확성이나 완전성을 보장하지 않습니다. 
          실제 투자 결정에 대한 최종 책임은 이용자 본인에게 있습니다.
        </div>
      </div>
    </div>
  )
}
