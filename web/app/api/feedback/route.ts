import { NextResponse } from 'next/server'
import db from '@/lib/db'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { type, content, contact } = body

    if (!type || !content) {
      return NextResponse.json(
        { error: 'Type and content are required' },
        { status: 400 }
      )
    }

    const stmt = db.prepare(`
      INSERT INTO feedbacks (type, content, contact)
      VALUES (?, ?, ?)
    `)

    const info = stmt.run(type, content, contact || null)

    return NextResponse.json({ 
      success: true, 
      id: info.lastInsertRowid 
    })
  } catch (error: any) {
    console.error('Feedback error:', error)
    return NextResponse.json(
      { error: 'Failed to submit feedback' },
      { status: 500 }
    )
  }
}
