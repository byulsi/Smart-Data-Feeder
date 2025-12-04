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

      // Segment Data
      const segments = db.prepare('SELECT * FROM company_segments WHERE ticker = ? ORDER BY period DESC, division ASC').all(ticker)
      
      md += "\n\n## 2. Segment Performance (Recent)\n"
      if (segments && segments.length > 0) {
        md += "| Period | Division | Revenue (KRW) | Op. Profit (KRW) |\n"
        md += "| :--- | :--- | :--- | :--- |\n"
        segments.forEach((s: any) => {
           // Simple formatting
           const rev = s.revenue ? Number(s.revenue).toLocaleString() : '-'
           const op = s.op_profit ? Number(s.op_profit).toLocaleString() : '-'
           md += `| ${s.period} | ${s.division} | ${rev} | ${op} |\n`
        })
      } else {
        md += "No segment data available.\n"
      }

      md += "\n\n## 3. Recent Disclosures\n"
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
      const company = db.prepare('SELECT name FROM companies WHERE ticker = ?').get(ticker)
      const narratives = db.prepare('SELECT * FROM company_narratives WHERE ticker = ? ORDER BY period DESC, section_type').all(ticker)
      const disclosures = db.prepare('SELECT * FROM disclosures WHERE ticker = ? ORDER BY rcept_dt DESC LIMIT 10').all(ticker)
      
      if (!company) return NextResponse.json({ error: 'Data not found' }, { status: 404 })

      let md = `# ${company.name} (${ticker}) - Deep Dive Narratives\n\n`
      
      if (narratives && narratives.length > 0) {
          // Group by period (taking the latest one for now)
          const latestPeriod = narratives[0].period
          md += `## 분기보고서 (${latestPeriod}) Key Takeaways\n`
          
          const currentNarratives = narratives.filter((n: any) => n.period === latestPeriod)
          const sectionOrder = ["Key Takeaways", "Business Overview", "MD&A", "News"]
          
          sectionOrder.forEach(section => {
              const sectionData = currentNarratives.filter((n: any) => n.section_type === section)
              if (sectionData.length > 0) {
                  let displayHeader = section
                  if (section === "Business Overview") displayHeader = "1. Business Overview (사업의 내용)"
                  else if (section === "MD&A") displayHeader = "2. MD&A (이사의 경영진단 및 분석의견)"
                  else if (section === "News") displayHeader = "3. News & Conference Call Summary"
                  
                  if (section !== "Key Takeaways") {
                      md += `## ${displayHeader}\n`
                  }
                  
                  sectionData.forEach((row: any) => {
                      if (row.title) md += `### ${row.title}\n`
                      md += `${row.content}\n\n`
                  })
              }
          })
      } else {
          md += "> [!NOTE]\n> Detailed text analysis will be available in the next update.\n\n"
      }
      
      // Append links
      if (disclosures && disclosures.length > 0) {
          md += "---\n## Reference Links\n"
          disclosures.forEach((d: any) => {
              md += `- **${d.rcept_dt}** [${d.report_nm}](${d.url})\n`
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
