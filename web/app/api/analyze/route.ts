import { NextResponse } from 'next/server'
import db from '@/lib/db'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const query = searchParams.get('query') || searchParams.get('ticker')

  if (!query) {
    return NextResponse.json({ error: 'Query is required' }, { status: 400 })
  }

  try {
    // 1. Fetch Company Info (Search by Ticker OR Name)
    // Check if query is all digits (likely ticker)
    const isTicker = /^\d+$/.test(query)
    
    let company;
    if (isTicker) {
      company = db.prepare('SELECT * FROM companies WHERE ticker = ?').get(query)
    } else {
      // Search by name (case-insensitive LIKE)
      company = db.prepare('SELECT * FROM companies WHERE name LIKE ?').get(`%${query}%`)
    }

    if (!company) {
      return NextResponse.json({ error: 'Company not found' }, { status: 404 })
    }
    
    const ticker = company.ticker; // Use the found company's ticker for subsequent queries

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
