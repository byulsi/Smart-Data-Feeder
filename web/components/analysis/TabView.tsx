'use client'

import React from 'react'
import { LayoutDashboard, TrendingUp, FileText, Bot } from 'lucide-react'

interface TabViewProps {
  activeTab: string
  setActiveTab: (tab: string) => void
}

export function TabView({ activeTab, setActiveTab }: TabViewProps) {
  const tabs = [
    { id: 'overview', label: '개요', icon: LayoutDashboard },
    { id: 'financials', label: '재무', icon: TrendingUp },
    { id: 'narratives', label: '텍스트', icon: FileText },
    { id: 'ai', label: 'AI 도구', icon: Bot },
  ]

  return (
    <div className="flex overflow-x-auto border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-14 z-40 no-scrollbar">
      {tabs.map((tab) => {
        const Icon = tab.icon
        const isActive = activeTab === tab.id
        
        return (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors border-b-2
              ${isActive 
                ? 'border-primary text-primary' 
                : 'border-transparent text-muted-foreground hover:text-foreground hover:border-muted'}
            `}
          >
            <Icon className="w-4 h-4" />
            {tab.label}
          </button>
        )
      })}
    </div>
  )
}
