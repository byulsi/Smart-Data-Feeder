import { NextResponse } from 'next/server'
import db from '@/lib/db'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const ticker = searchParams.get('ticker')
  const type = searchParams.get('type') // 'overview', 'narratives', 'chart'

  if (!ticker || !type) {
    return NextResponse.json({ error: 'Ticker and type are required' }, { status: 400 })
  }

  try {
    if (type === 'overview') {
      // Fetch Data
      const company = db.prepare('SELECT * FROM companies WHERE ticker = ?').get(ticker)
      const financials = db.prepare('SELECT * FROM financials WHERE ticker = ? ORDER BY year DESC LIMIT 4').all(ticker)
      const disclosures = db.prepare('SELECT * FROM disclosures WHERE ticker = ? ORDER BY rcept_dt DESC LIMIT 10').all(ticker)

      if (!company) return NextResponse.json({ error: 'Data not found' }, { status: 404 })

      // Generate Markdown
      let md = `# ${company.name} (${ticker}) - Corporate Overview\n\n`
      md += `**Sector:** ${company.sector || '-'} | **Market:** ${company.market_type || '-'}\n`
      md += `**Summary:** ${company.desc_summary || '-'}\n\n`
      
      md += "## 1. Financial Highlights (Recent)\n"
      if (financials && financials.length > 0) {
        md += "| Year | Quarter | Revenue | Op Profit | Net Income | Assets | Liabilities | Equity |\n"
        md += "|---|---|---|---|---|---|---|---|\n"
        financials.forEach((f: any) => {
          const q = f.quarter === 0 ? 'Yearly' : `${f.quarter}Q`
          md += `| ${f.year} | ${q} | ${f.revenue?.toLocaleString()} | ${f.op_profit?.toLocaleString()} | ${f.net_income?.toLocaleString()} | ${f.assets?.toLocaleString()} | ${f.liabilities?.toLocaleString()} | ${f.equity?.toLocaleString()} |\n`
        })
      } else {
        md += "No financial data available.\n"
      }

      md += "\n\n## 2. Recent Disclosures\n"
      if (disclosures && disclosures.length > 0) {
        disclosures.forEach((d: any) => {
          md += `- **${d.rcept_dt}** [${d.report_nm}](${d.url})\n`
        })
      } else {
        md += "No disclosures found.\n"
      }

      return new NextResponse(md, {
        headers: {
          'Content-Type': 'text/markdown; charset=utf-8',
          'Content-Disposition': `attachment; filename="${encodeURIComponent(company.name)}_Overview.md"`
        }
      })

    } else if (type === 'narratives') {
      // Placeholder for Narratives
      const company = db.prepare('SELECT name FROM companies WHERE ticker = ?').get(ticker)
      const disclosures = db.prepare('SELECT * FROM disclosures WHERE ticker = ? ORDER BY rcept_dt DESC LIMIT 10').all(ticker)
      
      if (!company) return NextResponse.json({ error: 'Data not found' }, { status: 404 })

      let md = `# ${company.name} (${ticker}) - Deep Dive Narratives\n\n`
      md += "> [!NOTE]\n> Detailed text analysis will be available in the next update.\n\n"
      
      if (disclosures && disclosures.length > 0) {
          disclosures.forEach((d: any) => {
              md += `## ${d.report_nm} (${d.rcept_dt})\n`
              md += `**Link:** [View on DART](${d.url})\n\n`
              md += "---\n\n"
          })
      }

      return new NextResponse(md, {
        headers: {
          'Content-Type': 'text/markdown; charset=utf-8',
          'Content-Disposition': `attachment; filename="${encodeURIComponent(company.name)}_Narratives.md"`
        }
      })

    } else if (type === 'chart') {
      // Generate CSV
      const market = db.prepare('SELECT date, open, high, low, close, volume, ma5, ma20, ma60 FROM market_daily WHERE ticker = ? ORDER BY date ASC').all(ticker)

      if (!market || market.length === 0) return NextResponse.json({ error: 'Data not found' }, { status: 404 })

      const header = "date,open,high,low,close,volume,ma5,ma20,ma60\n"
      const rows = market.map((m: any) => 
          `${m.date},${m.open},${m.high},${m.low},${m.close},${m.volume},${m.ma5||''},${m.ma20||''},${m.ma60||''}`
      ).join("\n")

      return new NextResponse(header + rows, {
        headers: {
          'Content-Type': 'text/csv; charset=utf-8',
          'Content-Disposition': `attachment; filename="${encodeURIComponent(ticker)}_Chart.csv"`
        }
      })
    }

    return NextResponse.json({ error: 'Invalid type' }, { status: 400 })
  } catch (error: any) {
    console.error('Database error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
