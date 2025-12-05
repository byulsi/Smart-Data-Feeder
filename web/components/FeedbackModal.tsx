'use client'

import React, { useState, useEffect } from 'react'
import { X, Send, CheckCircle, Loader2 } from 'lucide-react'

interface FeedbackModalProps {
  isOpen: boolean
  onClose: () => void
  initialType?: string
}

export function FeedbackModal({ isOpen, onClose, initialType = 'suggestion' }: FeedbackModalProps) {
  const [type, setType] = useState(initialType)
  const [content, setContent] = useState('')
  const [contact, setContact] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setType(initialType)
      setSuccess(false)
      setContent('')
    }
  }, [isOpen, initialType])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!content.trim()) return

    setLoading(true)
    try {
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, content, contact }),
      })

      if (res.ok) {
        setSuccess(true)
        setContent('')
        setContact('')
        setTimeout(() => {
          onClose()
        }, 2000)
      } else {
        alert('피드백 전송에 실패했습니다. 다시 시도해주세요.')
      }
    } catch (error) {
      console.error(error)
      alert('오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in duration-200">
      {/* Modal Content */}
      <div className="relative w-full max-w-md bg-card border border-border rounded-2xl shadow-2xl p-6 animate-in zoom-in-95 duration-200">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-muted-foreground hover:text-foreground transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {success ? (
          <div className="flex flex-col items-center justify-center py-10 text-center animate-in fade-in slide-in-from-bottom-2">
            <div className="w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center mb-4">
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
            <h3 className="text-xl font-bold text-foreground mb-2">소중한 의견 감사합니다!</h3>
            <p className="text-muted-foreground">보내주신 피드백은 서비스 개선에 큰 도움이 됩니다.</p>
          </div>
        ) : (
          <>
            <h3 className="text-xl font-bold text-foreground mb-1">피드백 보내기</h3>
            <p className="text-sm text-muted-foreground mb-6">
              서비스 이용 중 불편한 점이나 개선 아이디어를 자유롭게 남겨주세요.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Type Selection */}
              <div className="flex gap-2 p-1 bg-secondary rounded-lg">
                {['suggestion', 'bug', 'other'].map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setType(t)}
                    className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${
                      type === t
                        ? 'bg-background text-foreground shadow-sm'
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    {t === 'suggestion' && '제안'}
                    {t === 'bug' && '버그 신고'}
                    {t === 'other' && '기타'}
                  </button>
                ))}
              </div>

              {/* Content */}
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="내용을 입력해주세요..."
                className="w-full min-h-[120px] p-3 rounded-xl bg-secondary/50 border border-border focus:ring-2 focus:ring-ring outline-none resize-none text-foreground placeholder:text-muted-foreground"
                required
              />

              {/* Contact (Optional) */}
              <input
                type="text"
                value={contact}
                onChange={(e) => setContact(e.target.value)}
                placeholder="연락처 (이메일 등, 선택사항)"
                className="w-full p-3 rounded-xl bg-secondary/50 border border-border focus:ring-2 focus:ring-ring outline-none text-foreground placeholder:text-muted-foreground text-sm"
              />

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || !content.trim()}
                className="w-full py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <span>보내기</span>
                    <Send className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  )
}
