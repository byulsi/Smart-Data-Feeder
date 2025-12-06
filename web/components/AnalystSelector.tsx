'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, Check } from 'lucide-react'

type Persona = {
  id: string
  name: string
  description: string
  emoji: string
  color: string
}

const PERSONAS: Persona[] = [
  {
    id: 'value_hunter',
    name: '가치투자 사냥꾼',
    description: '저평가된 우량주를 찾아내는 헌터',
    emoji: '/value_hunter_pixel_1764997370904.png',
    color: 'bg-emerald-100 border-emerald-500 text-emerald-900'
  },
  {
    id: 'growth_scout',
    name: '성장주 탐험가',
    description: '폭발적인 성장 잠재력을 가진 기업 발굴',
    emoji: '/growth_scout_pixel_1764997385535.png',
    color: 'bg-violet-100 border-violet-500 text-violet-900'
  },
  {
    id: 'safety_inspector',
    name: '안전 제일 감독관',
    description: '재무 안정성과 리스크 관리를 최우선',
    emoji: '/safety_inspector_pixel_1764997404649.png',
    color: 'bg-slate-100 border-slate-500 text-slate-900'
  },
  {
    id: 'momentum_surfer',
    name: '모멘텀 서퍼',
    description: '시장 추세와 수급을 타는 트레이더',
    emoji: '/momentum_surfer_pixel_1764997419691.png',
    color: 'bg-amber-100 border-amber-500 text-amber-900'
  },
  {
    id: 'day_trader',
    name: '단타 승부사',
    description: '변동성과 거래량을 이용한 단기 매매',
    emoji: '/day_trader_pixel_1764997437296.png',
    color: 'bg-red-100 border-red-500 text-red-900'
  },
  {
    id: 'dividend_investor',
    name: '배당금 수집가',
    description: '안정적인 현금 흐름과 배당 수익 추구',
    emoji: '/dividend_investor_pixel_1764997454226.png',
    color: 'bg-yellow-100 border-yellow-500 text-yellow-900'
  }
]

interface AnalystSelectorProps {
  ticker: string
  onAnalysisComplete: (result: string) => void
  result?: string
}

export function AnalystSelector({ ticker, onAnalysisComplete }: AnalystSelectorProps) {
  const [selected, setSelected] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleAnalyze = async () => {
    if (!selected) return
    setLoading(true)
    try {
      const res = await fetch('/api/persona_analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker, persona: selected })
      })
      
      const data = await res.json()
      if (data.result) {
        onAnalysisComplete(data.result)
      }
    } catch (e) {
      console.error(e)
      alert('Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  return (

    <div className="w-full py-8 bg-card/50 rounded-3xl border border-border p-6 md:p-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl md:text-3xl font-bold mb-3">데이터 활용 가이드 선택</h2>
        <p className="text-muted-foreground">
          다운로드한 데이터를 어떻게 분석할지 막막하신가요?<br/>
          원하는 <strong>투자 성향(페르소나)</strong>을 선택하면, 딱 맞는 <strong>AI 질문 가이드</strong>를 만들어드립니다.
        </p>
      </div>

      <div className="max-w-xl mx-auto">
        {/* Dropdown Selection */}
        <div className="relative mb-8">
          <label className="block text-sm font-medium text-muted-foreground mb-2 ml-1">
            어떤 관점으로 분석할까요?
          </label>
          <div className="relative">
            <select
              value={selected || ''}
              onChange={(e) => setSelected(e.target.value)}
              className="w-full appearance-none bg-background border border-input hover:border-primary rounded-xl py-4 pl-4 pr-10 text-lg font-medium shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="" disabled>캐릭터를 선택해주세요</option>
              {PERSONAS.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
          </div>
        </div>

        {/* Selected Persona Preview */}
        <AnimatePresence mode="wait">
          {selected && (
            <motion.div
              key={selected}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-background border border-border rounded-2xl p-6 mb-8 flex items-center gap-6 shadow-sm"
            >
              <div className="shrink-0 bg-secondary/30 p-4 rounded-xl">
                <img 
                  src={PERSONAS.find(p => p.id === selected)?.emoji} 
                  alt="Persona" 
                  className="w-16 h-16 pixelated"
                  style={{ imageRendering: 'pixelated' }}
                />
              </div>
              <div>
                <h3 className="font-bold text-lg text-foreground mb-1">
                  {PERSONAS.find(p => p.id === selected)?.name}
                </h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {PERSONAS.find(p => p.id === selected)?.description}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Action Button */}
        <button
          onClick={handleAnalyze}
          disabled={!selected || loading}
          className={`w-full py-4 rounded-xl font-bold text-lg transition-all shadow-lg flex items-center justify-center gap-2 ${
            !selected || loading
              ? 'bg-muted text-muted-foreground cursor-not-allowed'
              : 'bg-primary text-primary-foreground hover:opacity-90 hover:scale-[1.02]'
          }`}
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              가이드 생성 중...
            </>
          ) : (
            <>
              ✨ AI 질문 가이드 생성하기
            </>
          )}
        </button>
      </div>
    </div>
  )
}
