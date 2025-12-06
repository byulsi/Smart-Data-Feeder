'use client'

import React, { useState } from 'react'
import { Copy, Check, Bot, ChevronDown, ChevronUp, Download, FileText, TrendingUp, AlertTriangle, Sparkles, PieChart, Activity, ShieldCheck, Target, DollarSign } from 'lucide-react'

interface AIToolsProps {
  data: any
}

type Step = {
  id: string
  title: string
  icon: React.ElementType
  description: string
  promptType: string
  downloadType?: string
  downloadLabel?: string
}

const STEPS: Step[] = [
  {
    id: 'step1',
    title: '1단계: 기본 정보 및 개요',
    icon: PieChart,
    description: '기업의 주요 사업 부문, 경쟁력, 공급망 구조를 파악합니다.',
    promptType: 'overview',
    downloadType: 'overview',
    downloadLabel: '기업 개요 데이터 (.md)'
  },
  {
    id: 'step1_5',
    title: '1.5단계: 데이터 품질 검증',
    icon: ShieldCheck,
    description: '재무 데이터의 신뢰성을 검증하고 왜곡 요인을 조정합니다.',
    promptType: 'quality_check',
    downloadType: 'overview',
    downloadLabel: '재무 데이터 (.md)'
  },
  {
    id: 'step2',
    title: '2단계: 재무 및 팩터 분석',
    icon: Activity,
    description: '실적 추이, 수익성, 성장성 및 팩터 노출도를 분석합니다.',
    promptType: 'financials'
  },
  {
    id: 'step3',
    title: '3단계: 정성적 분석 (SWOT/ESG)',
    icon: FileText,
    description: '사업보고서 텍스트를 기반으로 강점/약점 및 리스크를 분석합니다.',
    promptType: 'qualitative',
    downloadType: 'narratives',
    downloadLabel: '사업보고서 텍스트 (.md)'
  },
  {
    id: 'step4',
    title: '4단계: 밸류에이션 (다중 방식)',
    icon: DollarSign,
    description: 'PER, PBR, DCF 등 다양한 방식으로 적정 주가를 산출합니다.',
    promptType: 'valuation'
  },
  {
    id: 'step5',
    title: '5단계: 투자 매력도 평가',
    icon: Sparkles,
    description: '종합적인 투자 매력도를 별점으로 평가하고 편향을 점검합니다.',
    promptType: 'rating'
  },
  {
    id: 'step6',
    title: '6단계: 기술적 분석',
    icon: TrendingUp,
    description: '차트 데이터를 기반으로 추세와 매매 타이밍을 분석합니다.',
    promptType: 'technical',
    downloadType: 'chart',
    downloadLabel: '시장 데이터 (.csv)'
  },
  {
    id: 'step7',
    title: '7단계: 투자 전략 수립',
    icon: Target,
    description: '성향(안정형/공격형)에 따른 구체적인 진입/청산 전략을 수립합니다.',
    promptType: 'strategy'
  },
  {
    id: 'step8',
    title: '8단계: 자금 관리 및 실행',
    icon: Bot,
    description: '분할 매수 계획과 리스크 관리를 위한 자금 운용안을 짭니다.',
    promptType: 'execution'
  }
]

export function AITools({ data }: AIToolsProps) {
  const [openStep, setOpenStep] = useState<string | null>('step1')
  const [copied, setCopied] = useState('')

  const toggleStep = (id: string) => {
    setOpenStep(openStep === id ? null : id)
  }

  const generatePrompt = (type: string) => {
    const { company, financials, segments } = data
    
    // Base Context
    let context = `[Target Company]\nName: ${company.name} (${company.ticker})\nSector: ${company.sector}\nSummary: ${company.desc_summary}\n\n`
    
    // Financial Context (Common)
    let finContext = `[Financial Highlights (Recent)]\n`
    financials.slice(0, 4).forEach((f: any) => {
      finContext += `Year: ${f.year}, Quarter: ${f.quarter}, Revenue: ${f.revenue}, Op Profit: ${f.op_profit}, Net Income: ${f.net_income}, R&D: ${f.rnd_expenses || 0}\n`
    })
    finContext += `\n`

    // Segment Context
    let segContext = ""
    if (segments && segments.length > 0) {
      segContext += `[Segment Performance]\n`
      segments.forEach((s: any) => {
        segContext += `Period: ${s.period}, Division: ${s.division}, Revenue: ${s.revenue}, Op Profit: ${s.op_profit}\n`
      })
      segContext += `\n`
    }

    let prompt = `Act as a professional financial analyst. Analyze the following company: ${company.name} (${company.ticker}).\n\n`

    switch (type) {
      case 'overview':
        prompt += context + segContext
        prompt += `Task: Analyze the business overview.\n`
        prompt += `- Analyze revenue mix by major business segments (recent 3 years trend).\n`
        prompt += `- Identify key product/service portfolio and market share.\n`
        prompt += `- Analyze major competitors and competitive advantages.\n`
        prompt += `- Check supply chain structure and dependency on key clients.\n`
        prompt += `Output Format: Markdown table + 3-line key summary.`
        break

      case 'quality_check':
        prompt += context + finContext
        prompt += `Task: Verify financial data quality and adjust for corporate events.\n`
        prompt += `1) Check for adjusted stock price reflection (dividend, split, bonus issue).\n`
        prompt += `2) Verify quarterly data connectivity (audit opinion, base date).\n`
        prompt += `3) Analyze cash flow persistence (operating cash flow anomalies).\n`
        prompt += `4) Identify non-financial issues (litigation, regulation, environment).\n`
        prompt += `Output Format: Verification results + Adjusted metrics table + Notes.`
        break

      case 'financials':
        prompt += context + finContext + segContext
        prompt += `Task: Analyze financials and factor exposure.\n`
        prompt += `Financial Analysis (Recent 5 years/quarters):\n`
        prompt += `1) Performance Trend: Revenue, Op Profit, Net Income (YoY Growth)\n`
        prompt += `2) Profitability: OPM, ROE, ROA, EBITDA Margin\n`
        prompt += `3) Stability: Debt Ratio, Current Ratio, Net Debt Ratio\n`
        prompt += `4) Growth: Revenue Growth, CAPEX/Revenue, R&D/Revenue\n`
        prompt += `Factor Analysis: Exposure to SMB, HML, RMW, CMA, UMD.\n`
        prompt += `Output Format: Metrics table + 1-sentence summary vs industry peers.`
        break

      case 'qualitative':
        prompt += context
        prompt += `Task: Perform qualitative analysis (SWOT + News + ESG).\n`
        prompt += `1) SWOT Analysis: Strengths, Weaknesses, Opportunities, Threats (with quantitative basis).\n`
        prompt += `2) Recent News/Policy: Gov policy impact, regulation changes, competitor trends.\n`
        prompt += `3) ESG Risk: Environmental costs, Social issues, Governance risks.\n`
        prompt += `4) Alternative Data: Social sentiment, Analyst report tone changes.\n`
        prompt += `Note: Use the provided 'Narratives.md' content for deep analysis.\n`
        prompt += `Output Format: Markdown table per section + Comprehensive Risk Score (1-10).`
        break

      case 'valuation':
        prompt += context + finContext
        prompt += `Task: Perform multi-valuation and reflect policy scenarios.\n`
        prompt += `Methods (6 types): PER, PBR, PSR, PEG, EV/EBITDA, DCF.\n`
        prompt += `Scenarios:\n- Base: Current policy\n- Enhanced: Policy support expanded (Rev +15%)\n- Strong: Super strong policy (Rev +30%)\n`
        prompt += `Assumptions: WACC, Terminal Growth, Risk Premium.\n`
        prompt += `Output Format: Fair value table by method + Range by scenario + Consensus Fair Value.`
        break

      case 'rating':
        prompt += context + finContext
        prompt += `Task: Rate investment attractiveness (5 stars) and check behavioral biases.\n`
        prompt += `Ratings:\n1) Competitiveness & Growth\n2) Stability & Profitability\n3) Valuation Appeal\n4) Policy Momentum\n5) Overall Score\n`
        prompt += `Bias Check: Confirmation bias, Loss aversion, Overconfidence.\n`
        prompt += `Output Format: Star rating table + Summary + Bias checklist + Improvement plan.`
        break

      case 'technical':
        prompt += `Task: Cross-validate technical analysis with traditional indicators and ML models.\n`
        prompt += `I have the market data (CSV). Based on the recent price trends:\n`
        prompt += `1) Traditional: MA (20/60/120), RSI, MACD, Bollinger Bands, Support/Resistance.\n`
        prompt += `2) ML Enhancement: Random Forest feature importance, LSTM prediction, Pattern recognition.\n`
        prompt += `3) Comprehensive Signal: Buy/Sell/Neutral signal consistency, Trend strength (ADX).\n`
        prompt += `Output Format: Signal table + ML results + Comprehensive Signal (Confidence %).`
        break

      case 'strategy':
        prompt += context
        prompt += `Task: Propose investment strategies (Stable vs Aggressive) and analyze portfolio risk.\n`
        prompt += `1) Stable Strategy: High win rate, strict entry/exit rules.\n`
        prompt += `2) Aggressive Strategy: High return, momentum based.\n`
        prompt += `3) Portfolio Risk: Volatility, Beta, Correlation, VaR contribution.\n`
        prompt += `Output Format: Detailed plan table by strategy + Risk analysis table + Target investor profile.`
        break

      case 'execution':
        prompt += context
        prompt += `Task: Concretize investment strategy for [Amount] KRW capital and propose automation.\n`
        prompt += `1) Weight Decision: Conservative/Neutral/Aggressive scenarios.\n`
        prompt += `2) Split Buy Plan: 1st/2nd/3rd entry prices and amounts.\n`
        prompt += `3) Stop/Profit Rules: Specific price levels and expected return.\n`
        prompt += `4) Automation: Next.js + Supabase system design, Telegram alerts.\n`
        prompt += `Output Format: Execution plan + System architecture diagram + Monitoring checklist.`
        break
        
      default:
        prompt += "Analyze this company."
    }

    return prompt
  }

  const handleCopy = (type: string) => {
    const prompt = generatePrompt(type)
    navigator.clipboard.writeText(prompt)
    setCopied(type)
    setTimeout(() => setCopied(''), 2000)
  }

  const handleDownload = (type: string) => {
    window.location.href = `/api/download?ticker=${data.company.ticker}&type=${type}`
  }

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-primary/10 to-secondary/10 border border-primary/20 rounded-xl p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-primary/10 rounded-lg">
            <Bot className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h3 className="text-lg font-bold mb-2">AI Investment Analyst (8-Step Workflow)</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              전문가 수준의 8단계 분석 프로세스를 따라가세요. 각 단계별로 최적화된 프롬프트와 데이터를 제공합니다.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {STEPS.map((step, index) => {
          const isOpen = openStep === step.id
          const Icon = step.icon

          return (
            <div key={step.id} className={`bg-card border ${isOpen ? 'border-primary' : 'border-border'} rounded-xl transition-all duration-200 overflow-hidden`}>
              <button 
                onClick={() => toggleStep(step.id)}
                className="w-full flex items-center justify-between p-4 hover:bg-secondary/50 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className={`p-2 rounded-lg ${isOpen ? 'bg-primary/10 text-primary' : 'bg-secondary text-muted-foreground'}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="text-left">
                    <h4 className={`font-semibold ${isOpen ? 'text-primary' : 'text-foreground'}`}>{step.title}</h4>
                    {!isOpen && <p className="text-xs text-muted-foreground truncate max-w-[200px] md:max-w-md">{step.description}</p>}
                  </div>
                </div>
                {isOpen ? <ChevronUp className="w-5 h-5 text-muted-foreground" /> : <ChevronDown className="w-5 h-5 text-muted-foreground" />}
              </button>

              {isOpen && (
                <div className="p-4 pt-0 border-t border-border/50 animate-in slide-in-from-top-2">
                  <p className="text-sm text-muted-foreground mb-4 mt-4">
                    {step.description}
                  </p>

                  <div className="flex flex-col md:flex-row gap-3">
                    <button
                      onClick={() => handleCopy(step.promptType)}
                      className="flex-1 flex items-center justify-center gap-2 py-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 font-medium transition-colors"
                    >
                      {copied === step.promptType ? (
                        <>
                          <Check className="w-4 h-4" />
                          <span>프롬프트 복사 완료!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4" />
                          <span>프롬프트 복사</span>
                        </>
                      )}
                    </button>

                    {step.downloadType && (
                      <button
                        onClick={() => handleDownload(step.downloadType!)}
                        className="flex-1 flex items-center justify-center gap-2 py-3 rounded-lg bg-secondary hover:bg-secondary/80 border border-border font-medium transition-colors"
                      >
                        <Download className="w-4 h-4" />
                        <span>{step.downloadLabel || '데이터 다운로드'}</span>
                      </button>
                    )}
                  </div>
                  
                  <div className="mt-4 p-3 bg-secondary/30 rounded-lg border border-border/50">
                    <p className="text-xs text-muted-foreground">
                      <strong>Tip:</strong> 복사한 프롬프트를 ChatGPT나 Claude에 붙여넣으세요. 
                      {step.downloadType && " 다운로드한 파일도 함께 업로드하면 더 정확한 분석이 가능합니다."}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
