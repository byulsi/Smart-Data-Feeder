import React from 'react'
import { Activity } from 'lucide-react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs))
}

interface CompanyHeaderProps {
  company: any
  collecting: boolean
  handleCollect: (ticker: string) => void
}

export function CompanyHeader({ company, collecting, handleCollect }: CompanyHeaderProps) {
  return (
    <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-6 md:p-8 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none"></div>
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10">
        <div className="w-full md:w-auto">
          <div className="flex flex-wrap items-center gap-3 mb-2">
            <h2 className="text-2xl md:text-3xl font-bold text-white">{company.name}</h2>
            <span className="text-slate-400 text-lg md:text-xl font-light">{company.ticker}</span>
            <span className="bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded text-xs font-medium border border-blue-500/30">{company.market_type}</span>
          </div>
          <div className="flex gap-4 text-sm text-slate-400">
            <span>{company.sector}</span>
            <span className="w-px h-4 bg-slate-700"></span>
            <span>Est. {company.est_dt}</span>
          </div>
        </div>
        
        <div className="flex gap-3 w-full md:w-auto">
           <button
            onClick={() => handleCollect(company.ticker)}
            disabled={collecting}
            className="flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 text-slate-300 px-4 py-2 rounded-lg text-sm transition-colors w-full md:w-auto"
          >
            <Activity className={cn("w-4 h-4", collecting && "animate-spin")} />
            {collecting ? 'Updating...' : 'Update Data'}
          </button>
        </div>
      </div>
      
      <p className="mt-6 text-slate-300 leading-relaxed max-w-4xl text-sm md:text-base">
        {company.desc_summary}
      </p>
    </div>
  )
}
