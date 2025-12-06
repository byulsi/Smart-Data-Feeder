import React from 'react'
import { TrendingUp } from 'lucide-react'
import { ThemeToggle } from './ThemeToggle'

export function Header() {
  return (
    <header className="border-b border-border bg-background/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 md:px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2 md:gap-3">
          <div className="bg-primary p-2 rounded-lg">
            <TrendingUp className="w-5 h-5 md:w-6 md:h-6 text-primary-foreground" />
          </div>
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-foreground">
            Antz (앤츠) 🐜
          </h1>
          <span className="hidden md:inline-block px-2 py-0.5 bg-secondary text-secondary-foreground text-xs font-medium rounded-full border border-border">
            v2.0 엔터프라이즈
          </span>
        </div>
        
        <ThemeToggle />
      </div>
    </header>
  )
}
