import os
import re
import OpenDartReader
import pandas as pd
from datetime import datetime
from utils import upsert_data, get_db_connection
from dotenv import load_dotenv

load_dotenv()

class ReportContentCollector:
    def __init__(self):
        self.api_key = os.getenv("DART_API_KEY")
        if self.api_key:
            self.dart = OpenDartReader(self.api_key)
        else:
            print("Warning: DART_API_KEY not found")
            self.dart = None
        self.conn = get_db_connection()

    def fetch_latest_report(self, ticker):
        """Finds the latest Quarterly/Half-year/Annual report."""
        if not self.dart:
            return None

        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - pd.Timedelta(days=365)).strftime("%Y%m%d")
        
        try:
            # kind='A' includes Annual, Semi-Annual, Quarterly
            df = self.dart.list(ticker, start=start_date, end=end_date, kind='A')
            if df is None or df.empty:
                return None
            
            # Sort by date desc
            df = df.sort_values('rcept_dt', ascending=False)
            
            # Filter for main reports
            target_reports = ["사업보고서", "반기보고서", "분기보고서"]
            for _, row in df.iterrows():
                if any(report in row['report_nm'] for report in target_reports):
                    return row
            
            return None
        except Exception as e:
            print(f"Error fetching report list: {e}")
            return None

    def fetch_report_xml(self, rcept_no):
        """Downloads the full XML content."""
        try:
            return self.dart.document(rcept_no)
        except Exception as e:
            print(f"Error fetching document {rcept_no}: {e}")
            return None

    def parse_sections(self, xml_text):
        """
        Extracts "II. 사업의 내용" and "IV. 이사의 경영진단 및 분석의견".
        Simple regex-based extraction for MVP.
        """
        sections = {}
        
        # Regex patterns for section headers
        # Note: DART XML structure varies, but often sections are in <TITLE> or plain text.
        # This is a simplified approach. A proper XML parser would be better but DART XML is often malformed or complex.
        
        # 1. Business Overview
        # Look for "II. 사업의 내용" or similar
        business_pattern = re.compile(r'(II\.\s*사업의\s*내용.*?)(?=III\.|IV\.|V\.)', re.DOTALL | re.IGNORECASE)
        match = business_pattern.search(xml_text)
        if match:
            sections['Business Overview'] = match.group(1)
            
        # 2. MD&A
        # Look for "IV. 이사의 경영진단" or similar (sometimes it's different number)
        mda_pattern = re.compile(r'(IV\.\s*이사의\s*경영진단.*?)(?=V\.|VI\.)', re.DOTALL | re.IGNORECASE)
        match = mda_pattern.search(xml_text)
        if match:
            sections['MD&A'] = match.group(1)
            
        return sections

    def clean_text(self, text):
        """Removes HTML/XML tags and excessive whitespace."""
        # Remove tags
        clean = re.sub(r'<[^>]+>', '', text)
        # Remove entities
        clean = re.sub(r'&[a-z]+;', ' ', clean)
        # Collapse whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    def extract_narratives(self, sections):
        """Prepares narrative data."""
        narratives = []
        
        if 'Business Overview' in sections:
            content = self.clean_text(sections['Business Overview'])
            # Truncate for MVP if too long, or summarize (future)
            # Just taking first 1000 chars for now as a summary
            narratives.append({
                "section_type": "Business Overview",
                "title": "Summary",
                "content": content[:2000] + "..." if len(content) > 2000 else content
            })
            
        if 'MD&A' in sections:
            content = self.clean_text(sections['MD&A'])
            narratives.append({
                "section_type": "MD&A",
                "title": "Analysis",
                "content": content[:2000] + "..." if len(content) > 2000 else content
            })
            
        return narratives

    def run(self, ticker):
        print(f"Running collector for {ticker}...")
        report = self.fetch_latest_report(ticker)
        if report is None:
            print("No report found.")
            return

        print(f"Found report: {report['report_nm']} ({report['rcept_dt']})")
        
        # Determine period string (e.g., 2025.09)
        # report_nm usually contains date like "분기보고서 (2025.09)"
        period_match = re.search(r'\((\d{4}\.\d{2})\)', report['report_nm'])
        period = period_match.group(1) if period_match else report['rcept_dt'][:6] # Fallback to YYYYMM
        
        xml_text = self.fetch_report_xml(report['rcept_no'])
        if not xml_text:
            return

        sections = self.parse_sections(xml_text)
        narratives = self.extract_narratives(sections)
        
        # Save to DB
        cursor = self.conn.cursor()
        for n in narratives:
            try:
                # Delete existing for this period/section to avoid dupes/stale data
                cursor.execute("DELETE FROM company_narratives WHERE ticker=? AND period=? AND section_type=?", 
                               (ticker, period, n['section_type']))
                
                cursor.execute("""
                    INSERT INTO company_narratives (ticker, period, section_type, title, content)
                    VALUES (?, ?, ?, ?, ?)
                """, (ticker, period, n['section_type'], n['title'], n['content']))
            except Exception as e:
                print(f"Error saving narrative: {e}")
        
        self.conn.commit()
        print(f"Saved {len(narratives)} narratives for {ticker} ({period})")

if __name__ == "__main__":
    collector = ReportContentCollector()
    collector.run("005930")
