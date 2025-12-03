import os
import pandas as pd
from utils import get_db_connection
from datetime import datetime

class MarkdownGenerator:
    def __init__(self, ticker):
        self.ticker = ticker
        self.conn = get_db_connection()

    def _fetch_company_info(self):
        query = "SELECT * FROM companies WHERE ticker = %s"
        return pd.read_sql(query, self.conn, params=(self.ticker,))

    def _fetch_financials(self):
        query = """
            SELECT year, quarter, revenue, op_profit, net_income, assets, liabilities, equity
            FROM financials 
            WHERE ticker = %s 
            ORDER BY year DESC, quarter DESC
            LIMIT 4
        """
        return pd.read_sql(query, self.conn, params=(self.ticker,))

    def _fetch_disclosures(self):
        query = """
            SELECT rcept_dt, report_nm, flr_nm, url
            FROM disclosures 
            WHERE ticker = %s 
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
        
        md += "\n\n## 2. Recent Disclosures\n"
        if not disclosures_df.empty:
            for _, row in disclosures_df.iterrows():
                date_str = row['rcept_dt'].strftime('%Y-%m-%d')
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
        md += "> [!NOTE]\n"
        md += "> Detailed text analysis will be available in the next update. Below are the direct links to recent reports.\n\n"
        
        disclosures_df = self._fetch_disclosures()
        if not disclosures_df.empty:
            for _, row in disclosures_df.iterrows():
                date_str = row['rcept_dt'].strftime('%Y-%m-%d')
                md += f"## {row['report_nm']} ({date_str})\n"
                md += f"**Link:** [View on DART]({row['url']})\n\n"
                # Placeholder for parsed text
                md += "*Content extraction pending...*\n\n"
                md += "---\n\n"
                
        return md

    def save_files(self, output_dir="output"):
        os.makedirs(output_dir, exist_ok=True)
        
        overview_md = self.generate_overview()
        with open(f"{output_dir}/{self.ticker}_Overview.md", "w") as f:
            f.write(overview_md)
            
        narratives_md = self.generate_narratives()
        with open(f"{output_dir}/{self.ticker}_Narratives.md", "w") as f:
            f.write(narratives_md)
            
        print(f"Generated Markdown files for {self.ticker} in {output_dir}/")

if __name__ == "__main__":
    generator = MarkdownGenerator("005930")
    generator.save_files()
