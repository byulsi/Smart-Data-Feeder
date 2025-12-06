'use client'

import React from 'react'
import { Home, Search, Settings } from 'lucide-react'
import { usePathname, useRouter } from 'next/navigation'

export function MobileNav() {
  const pathname = usePathname()
  const router = useRouter()

  // Only show on mobile (hidden on md+)
  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 bg-background/95 backdrop-blur border-t border-border z-50 pb-safe">
      <div className="flex justify-around items-center h-16">
        <button 
          onClick={() => router.push('/')}
          className={`flex flex-col items-center justify-center w-full h-full space-y-1 ${pathname === '/' ? 'text-primary' : 'text-muted-foreground'}`}
        >
          <Home className="w-5 h-5" />
          <span className="text-[10px] font-medium">Home</span>
        </button>
        
        <button 
          onClick={() => router.push('/')} // Search is on Home for now
          className={`flex flex-col items-center justify-center w-full h-full space-y-1 ${pathname === '/' ? 'text-primary' : 'text-muted-foreground'}`}
        >
          <Search className="w-5 h-5" />
          <span className="text-[10px] font-medium">Search</span>
        </button>

        <button 
          className="flex flex-col items-center justify-center w-full h-full space-y-1 text-muted-foreground opacity-50 cursor-not-allowed"
        >
          <Settings className="w-5 h-5" />
          <span className="text-[10px] font-medium">Settings</span>
        </button>
      </div>
    </div>
  )
}
