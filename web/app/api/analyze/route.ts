import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabaseClient'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const ticker = searchParams.get('ticker')

  if (!ticker) {
    return NextResponse.json({ error: 'Ticker is required' }, { status: 400 })
  }

  // 1. Fetch Company Info
  const { data: company, error: companyError } = await supabase
    .from('companies')
    .select('*')
    .eq('ticker', ticker)
    .single()

  if (companyError || !company) {
    return NextResponse.json({ error: 'Company not found' }, { status: 404 })
  }

  // 2. Fetch Financials (Summary)
  const { data: financials } = await supabase
    .from('financials')
    .select('*')
    .eq('ticker', ticker)
    .order('year', { ascending: false })
    .limit(1)

  // 3. Fetch Market Data (Latest)
  const { data: market } = await supabase
    .from('market_daily')
    .select('*')
    .eq('ticker', ticker)
    .order('date', { ascending: false })
    .limit(1)

  return NextResponse.json({
    company,
    financials: financials?.[0] || null,
    market: market?.[0] || null
  })
}
