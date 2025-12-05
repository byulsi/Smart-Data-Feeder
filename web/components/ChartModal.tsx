'use client'

import React from 'react'
import { X } from 'lucide-react'
import { SmartChart } from './SmartChart'

interface ChartModalProps {
  isOpen: boolean
  onClose: () => void
  market: any[]
  title: string
}

export function ChartModal({ isOpen, onClose, market, title }: ChartModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-5xl h-[80vh] bg-card border border-border rounded-2xl shadow-2xl p-6 flex flex-col animate-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-foreground">{title}</h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-secondary rounded-full text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Chart Content */}
        <div className="flex-1 min-h-0">
          <SmartChart market={market} height="100%" />
        </div>
      </div>
    </div>
  )
}
