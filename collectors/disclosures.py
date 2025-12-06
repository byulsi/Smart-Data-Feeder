import os
import OpenDartReader
import pandas as pd
import re
from datetime import datetime, timedelta
from utils import upsert_data
from dotenv import load_dotenv
from processors.text_parser import TextParser

load_dotenv()

class DisclosuresCollector:
    def __init__(self):
        self.api_key = os.getenv("DART_API_KEY")
        if self.api_key:
            self.dart = OpenDartReader(self.api_key)
        else:
            print("Warning: DART_API_KEY not found")
            self.dart = None
        self.parser = TextParser()

    def fetch_disclosures(self, ticker, days=1095):
        """
        Fetches disclosure list for the past 'days' and extracts key text.
        """
        if not self.dart:
            return

        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        
        print(f"Fetching disclosures for {ticker} from {start_date} to {end_date}...")
        
        try:
            # Find corp_code
            corp_code = self.dart.find_corp_code(ticker)
            if not corp_code:
                print(f"Could not find corp_code for {ticker}")
                return

            # Fetch list - All disclosures (filter locally)
            df = self.dart.list(corp_code, start=start_date, end=end_date)
            
            if df is None or df.empty:
                print(f"No periodic disclosures found for {ticker}")
                return

            disclosures_data = []
            narratives_to_save = []
            cutoff_1yr = datetime.now().date() - timedelta(days=365)

            for _, row in df.iterrows():
                report_nm = row['report_nm']
                rcept_dt_str = row['rcept_dt'] # YYYYMMDD
                rcept_dt = datetime.strptime(rcept_dt_str, "%Y%m%d").date()
                rcept_no = row['rcept_no']
                
                # print(f"DEBUG: Loop start for {report_nm}")
                xml_text = None
                
                is_annual = "사업보고서" in report_nm
                is_quarterly = "분기보고서" in report_nm or "반기보고서" in report_nm
                
                if is_quarterly and rcept_dt < cutoff_1yr:
                    continue
                
                if not (is_annual or is_quarterly):
                    continue

                # Extract Text Content
                summary_body = ""
                extracted_text = None
                
                try:
                    # Fetch full XML
                    xml_text = self.dart.document(rcept_no)
                    
                    if xml_text:
                        # 1. R&D Expenses
                        rnd_expenses = self.parser.parse_rnd_expenses(xml_text)
                        if rnd_expenses:
                            print(f"Extracted R&D Expenses for {report_nm}: {rnd_expenses:,}")
                            
                            # Parse period
                            match = re.search(r'\((\d{4})\.(\d{2})\)', report_nm)
                            if match:
                                year = int(match.group(1))
                                month = int(match.group(2))
                                quarter = (month - 1) // 3 + 1
                                if "사업보고서" in report_nm:
                                    quarter = 0
                                
                                upsert_data(
                                    table="financials",
                                    data=[{
                                        "ticker": ticker,
                                        "year": year,
                                        "quarter": quarter,
                                        "rnd_expenses": rnd_expenses
                                    }],
                                    conflict_columns=["ticker", "year", "quarter"],
                                    update_columns=["rnd_expenses"]
                                )

                        # 2. Segments (Placeholder for now, keeping existing logic if any, but simplified)
                        # The previous implementation had complex segment logic inside. 
                        # We should move that to TextParser later, but for now let's keep it simple or use the parser if implemented.
                        # Since TextParser.parse_segments is placeholder, we skip for now or migrate logic.
                        # Let's migrate the logic to TextParser in next step or just keep it here?
                        # The plan said "processors/text_parser.py" will handle it.
                        # So I should move the logic to TextParser.
                        
                        # 3. Narratives
                        narratives = self.parser.parse_narratives(xml_text)
                        if narratives:
                            print(f"Extracted {len(narratives)} narrative sections for {report_nm}")
                            
                            # Determine period for narratives
                            period = f"{year}.{quarter}Q" if quarter > 0 else f"{year}"
                            
                            narratives_data = []
                            for n in narratives:
                                narratives_data.append({
                                    "ticker": ticker,
                                    "period": period,
                                    "section_type": n['section_type'],
                                    "title": n['title'],
                                    "content": n['content']
                                })
                                
                            # Upsert narratives
                            upsert_data(
                                table="company_narratives",
                                data=narratives_data,
                                conflict_columns=["ticker", "period", "section_type", "title"]
                            )
                            
                            # Use the first narrative as summary_body for disclosures table
                            summary_body = narratives[0]['content'][:500] + "..."
                        else:
                            # Fallback if parser returns empty
                            start_marker = "II. 사업의 내용"
                            end_marker = "III. 재무에 관한 사항"
                            start_idx = xml_text.find(start_marker)
                            end_idx = xml_text.find(end_marker)
                            
                            if start_idx != -1 and end_idx != -1:
                                section_content = xml_text[start_idx:end_idx]
                                clean_text = re.sub('<[^<]+?>', '', section_content)
                                clean_text = ' '.join(clean_text.split())
                                summary_body = clean_text[:500] + "..."
                            else:
                                summary_body = "Section 'II. 사업의 내용' not found."

                    else:
                        summary_body = "Failed to fetch document XML."
                        
                except Exception as e:
                    print(f"Text extraction failed for {rcept_no}: {e}")
                    summary_body = f"Extraction error: {e}"

                disclosures_data.append({
                    "rcept_no": rcept_no,
                    "ticker": ticker,
                    "report_nm": report_nm,
                    "rcept_dt": rcept_dt,
                    "flr_nm": row['flr_nm'],
                    "url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}",
                    "summary_body": summary_body
                })
            
            # Upsert disclosures
            if disclosures_data:
                upsert_data(
                    table="disclosures",
                    data=disclosures_data,
                    conflict_columns=["rcept_no"]
                )
                print(f"Saved {len(disclosures_data)} disclosures for {ticker}")
            
        except Exception as e:
            print(f"Error fetching disclosures: {e}")

if __name__ == "__main__":
    collector = DisclosuresCollector()
    collector.fetch_disclosures("005930")
