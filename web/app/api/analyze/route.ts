import { NextResponse } from 'next/server'
import db from '@/lib/db'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const ticker = searchParams.get('ticker')

  if (!ticker) {
    return NextResponse.json({ error: 'Ticker is required' }, { status: 400 })
  }

  try {
    // 1. Fetch Company Info
    const company = db.prepare('SELECT * FROM companies WHERE ticker = ?').get(ticker)

    if (!company) {
      return NextResponse.json({ error: 'Company not found' }, { status: 404 })
    }

    // 2. Fetch Financials (Summary) - Latest year
    const financials = db.prepare('SELECT * FROM financials WHERE ticker = ? ORDER BY year DESC, quarter DESC LIMIT 1').get(ticker)

    // 3. Fetch Market Data (Latest)
    const market = db.prepare('SELECT * FROM market_daily WHERE ticker = ? ORDER BY date DESC LIMIT 1').get(ticker)

    return NextResponse.json({
      company,
      financials: financials || null,
      market: market || null
    })
  } catch (error: any) {
    console.error('Database error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
