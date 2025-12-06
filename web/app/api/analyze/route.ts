import { NextResponse } from 'next/server'
import db from '@/lib/db'

export const dynamic = 'force-dynamic'

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

    // 2. Fetch Financials (History - last 4 quarters/years)
    const financials = db.prepare('SELECT * FROM financials WHERE ticker = ? ORDER BY year DESC, quarter DESC LIMIT 4').all(ticker)

    // 3. Fetch Market Data (History - last 365 days)
    const market = db.prepare('SELECT * FROM market_daily WHERE ticker = ? ORDER BY date ASC LIMIT 365').all(ticker)

    // 4. Fetch Shareholders (Top 5)
    const shareholders = db.prepare('SELECT * FROM shareholders WHERE ticker = ? ORDER BY share_ratio DESC LIMIT 5').all(ticker)

    // 5. Fetch Segments (Latest period)
    const segments = db.prepare('SELECT * FROM company_segments WHERE ticker = ? ORDER BY period DESC LIMIT 10').all(ticker)

    // 6. Fetch Narratives (Latest 10)
    const narratives = db.prepare('SELECT * FROM company_narratives WHERE ticker = ? ORDER BY period DESC, id ASC LIMIT 10').all(ticker)

    return NextResponse.json({
      company,
      financials: financials || [],
      market: market || [],
      shareholders: shareholders || [],
      segments: segments || [],
      narratives: narratives || []
    })
  } catch (error: any) {
    console.error('Database error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
