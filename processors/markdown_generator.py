import os
import pandas as pd
from utils import get_db_connection
from datetime import datetime

class MarkdownGenerator:
    def __init__(self, ticker):
        self.ticker = ticker
        self.conn = get_db_connection()

    def _fetch_company_info(self):
        query = "SELECT * FROM companies WHERE ticker = ?"
        return pd.read_sql(query, self.conn, params=(self.ticker,))

    def _fetch_financials(self):
        query = """
            SELECT year, quarter, revenue, op_profit, net_income, assets, liabilities, equity
            FROM financials 
            WHERE ticker = ? 
            ORDER BY year DESC, quarter DESC
            LIMIT 4
        """
        return pd.read_sql(query, self.conn, params=(self.ticker,))

    def _fetch_disclosures(self):
        query = """
            SELECT rcept_dt, report_nm, flr_nm, url
            FROM disclosures 
            WHERE ticker = ? 
            ORDER BY rcept_dt DESC
            LIMIT 10
        """
        return pd.read_sql(query, self.conn, params=(self.ticker,))

    def generate_overview(self):
        """Generates [Ticker]_Overview.md"""
        company_df = self._fetch_company_info()
        financials_df = self._fetch_financials()
        disclosures_df = self._fetch_disclosures()

        if company_df.empty:
            return f"No data found for {self.ticker}"

        info = company_df.iloc[0]
        
        md = f"# {info['name']} ({self.ticker}) - Corporate Overview\n\n"
        md += f"**Sector:** {info['sector']} | **Market:** {info['market_type']}\n"
        if info.get('est_dt'):
            md += f"**Established:** {info['est_dt']} | "
        if info.get('listing_dt'):
            md += f"**Listed:** {info['listing_dt']}\n"
        else:
            md += "\n"
            
        md += f"**Summary:** {info['desc_summary']}\n\n"
        
        md += "## 1. Financial Highlights (Recent)\n"
        if not financials_df.empty:
            # Format numbers
            financials_df['revenue'] = financials_df['revenue'].apply(lambda x: f"{x:,}")
            financials_df['op_profit'] = financials_df['op_profit'].apply(lambda x: f"{x:,}")
            financials_df['net_income'] = financials_df['net_income'].apply(lambda x: f"{x:,}")
            
            md += financials_df.to_markdown(index=False)
        else:
            md += "No financial data available.\n"
        
        # Dynamic Segment Performance
        query = "SELECT * FROM company_segments WHERE ticker = ? ORDER BY period DESC, division ASC"
        segments_df = pd.read_sql(query, self.conn, params=(self.ticker,))
        
        md += "\n\n## 2. Segment Performance (Recent)\n"
        if not segments_df.empty:
            md += "| Period | Division | Revenue (KRW) | Op. Profit (KRW) |\n"
            md += "| :--- | :--- | :--- | :--- |\n"
            for _, row in segments_df.iterrows():
                # Format numbers
                rev = row['revenue']
                op = row['op_profit']
                try:
                    rev = f"{int(rev):,}"
                except: pass
                try:
                    op = f"{int(op):,}"
                except: pass
                
                md += f"| {row['period']} | {row['division']} | {rev} | {op} |\n"
        else:
            md += "No segment data available.\n"
        
        md += "\n\n## 3. Recent Disclosures\n"
        if not disclosures_df.empty:
            for _, row in disclosures_df.iterrows():
                rcept_dt = row['rcept_dt']
                if isinstance(rcept_dt, str):
                    date_str = rcept_dt
                else:
                    date_str = rcept_dt.strftime('%Y-%m-%d')
                md += f"- **{date_str}** [{row['report_nm']}]({row['url']})\n"
        else:
            md += "No disclosures found.\n"
            
        return md

    def generate_narratives(self):
        """Generates [Ticker]_Narratives.md"""
        # For MVP, this might just be a placeholder or list of links if we haven't parsed text yet.
        # The user plan says "Deep Dive Narratives... extracted text".
        # Since we haven't implemented text parsing in collector yet, we'll provide a structure.
        
        md = f"# {self.ticker} - Deep Dive Narratives\n\n"
        
        # Dynamic Narratives
        query = "SELECT * FROM company_narratives WHERE ticker = ? ORDER BY period DESC, section_type"
        narratives_df = pd.read_sql(query, self.conn, params=(self.ticker,))
        
        if not narratives_df.empty:
            # Group by period (taking the latest one for now)
            latest_period = narratives_df.iloc[0]['period']
            md += f"## 분기보고서 ({latest_period}) Key Takeaways\n"
            
            # Filter for latest period
            current_narratives = narratives_df[narratives_df['period'] == latest_period]
            
            # Group by Section Type
            # Order: Key Takeaways -> Business Overview -> MD&A -> News
            section_order = ["Key Takeaways", "Business Overview", "MD&A", "News"]
            
            for section in section_order:
                section_data = current_narratives[current_narratives['section_type'] == section]
                if not section_data.empty:
                    # Map section type to display header
                    display_header = section
                    if section == "Business Overview":
                        display_header = "1. Business Overview (사업의 내용)"
                    elif section == "MD&A":
                        display_header = "2. MD&A (이사의 경영진단 및 분석의견)"
                    elif section == "News":
                        display_header = "3. News & Conference Call Summary"
                    elif section == "Key Takeaways":
                        display_header = "Key Takeaways" # Already in title if we want, or subsection
                        
                    if section != "Key Takeaways": # Key Takeaways handled differently or just as a section
                        md += f"## {display_header}\n"
                    
                    for _, row in section_data.iterrows():
                        if row['title']:
                            md += f"### {row['title']}\n"
                        md += f"{row['content']}\n\n"
            
            return md

        md += "> [!NOTE]\n"
        md += "> Detailed text analysis will be available in the next update. Below are the direct links to recent reports.\n\n"
        
        disclosures_df = self._fetch_disclosures()
        if not disclosures_df.empty:
            for _, row in disclosures_df.iterrows():
                rcept_dt = row['rcept_dt']
                if isinstance(rcept_dt, str):
                    date_str = rcept_dt
                else:
                    date_str = rcept_dt.strftime('%Y-%m-%d')
                md += f"## {row['report_nm']} ({date_str})\n"
                md += f"**Link:** [View on DART]({row['url']})\n\n"
                # Placeholder for parsed text
                md += "*Content extraction pending...*\n\n"
                md += "---\n\n"
                
        return md

    def save_files(self, output_dir="output"):
        os.makedirs(output_dir, exist_ok=True)
        
        overview_md = self.generate_overview()
        with open(f"{output_dir}/{self.ticker}_Overview.md", "w", encoding="utf-8") as f:
            f.write(overview_md)
            
        narratives_md = self.generate_narratives()
        with open(f"{output_dir}/{self.ticker}_Narratives.md", "w", encoding="utf-8") as f:
            f.write(narratives_md)
            
        print(f"Generated Markdown files for {self.ticker} in {output_dir}/")

if __name__ == "__main__":
    generator = MarkdownGenerator("005930")
    generator.save_files()
