'use client'

import React, { useState } from 'react'
import { ThumbsUp, ThumbsDown, X } from 'lucide-react'
import { FeedbackModal } from './FeedbackModal'

export function FeedbackWidget() {
  const [showPopover, setShowPopover] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [feedbackType, setFeedbackType] = useState<'like' | 'dislike' | null>(null)

  const handleFeedback = (type: 'like' | 'dislike') => {
    setFeedbackType(type)
    setShowPopover(true)
    
    // Optional: Send simple analytics event here
    // fetch('/api/feedback/analytics', { ... })

    // Auto-hide popover after 5 seconds if no interaction
    setTimeout(() => {
      setShowPopover(false)
    }, 5000)
  }

  const openModal = () => {
    setShowPopover(false)
    setIsModalOpen(true)
  }

  return (
    <>
      <div className="fixed bottom-6 right-6 z-40 flex flex-col items-end gap-4">
        
        {/* Popover */}
        {showPopover && (
          <div className="bg-card border border-border rounded-2xl shadow-xl p-5 max-w-xs animate-in slide-in-from-bottom-2 fade-in duration-300 mb-2">
            <div className="flex justify-between items-start mb-2">
              <h4 className="font-bold text-foreground text-lg">감사합니다</h4>
              <button onClick={() => setShowPopover(false)} className="text-muted-foreground hover:text-foreground">
                <X className="w-4 h-4" />
              </button>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed mb-4">
              보내 주신 의견은 서비스 개선에 활용됩니다.
            </p>
            <div className="flex gap-4 text-sm">
              <button 
                onClick={openModal}
                className="text-primary font-semibold hover:underline"
              >
                추가 의견 공유
              </button>
              <button 
                onClick={() => setShowPopover(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                닫기
              </button>
            </div>
          </div>
        )}

        {/* Thumbs Buttons */}
        <div className="flex items-center gap-2 bg-card border border-border rounded-full p-2 shadow-lg">
          <span className="text-xs font-medium text-muted-foreground px-2">이 정보가 도움이 되었나요?</span>
          <div className="h-4 w-[1px] bg-border mx-1"></div>
          <button
            onClick={() => handleFeedback('like')}
            className={`p-2 rounded-full transition-colors ${
              feedbackType === 'like' 
                ? 'bg-primary text-primary-foreground' 
                : 'hover:bg-secondary text-muted-foreground hover:text-primary'
            }`}
            aria-label="좋아요"
          >
            <ThumbsUp className="w-5 h-5" fill={feedbackType === 'like' ? "currentColor" : "none"} />
          </button>
          <button
            onClick={() => handleFeedback('dislike')}
            className={`p-2 rounded-full transition-colors ${
              feedbackType === 'dislike' 
                ? 'bg-destructive text-destructive-foreground' 
                : 'hover:bg-secondary text-muted-foreground hover:text-destructive'
            }`}
            aria-label="싫어요"
          >
            <ThumbsDown className="w-5 h-5" fill={feedbackType === 'dislike' ? "currentColor" : "none"} />
          </button>
        </div>
      </div>

      {/* Detailed Feedback Modal */}
      <FeedbackModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        initialType={feedbackType === 'dislike' ? 'suggestion' : 'suggestion'}
      />
    </>
  )
}
