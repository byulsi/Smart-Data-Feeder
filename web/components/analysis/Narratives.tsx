'use client'

import React from 'react'
import { FileText, Calendar, Tag } from 'lucide-react'

interface NarrativesProps {
  narratives: any[]
}

export function Narratives({ narratives }: NarrativesProps) {
  if (!narratives || narratives.length === 0) {
    return (
      <div className="text-center py-12 bg-card border border-border rounded-xl">
        <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <h3 className="text-lg font-semibold mb-2">데이터가 없습니다</h3>
        <p className="text-muted-foreground">
          아직 수집된 텍스트 분석 데이터가 없습니다.<br />
          최신 공시 데이터를 수집해주세요.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {narratives.map((item, index) => (
        <div key={index} className="bg-card border border-border rounded-xl p-6 hover:border-primary/30 transition-colors">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-primary/10 rounded-lg">
              <FileText className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h4 className="font-bold text-lg">{item.title || item.section_type}</h4>
              <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {item.period}
                </span>
                <span className="flex items-center gap-1">
                  <Tag className="w-3 h-3" />
                  {item.section_type}
                </span>
              </div>
            </div>
          </div>
          
          <div className="prose prose-sm dark:prose-invert max-w-none bg-secondary/30 p-4 rounded-lg">
            <p className="whitespace-pre-wrap leading-relaxed text-foreground/90">
              {item.content}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}
