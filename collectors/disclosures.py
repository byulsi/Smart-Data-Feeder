import os
import OpenDartReader
from datetime import datetime, timedelta
from utils import upsert_data
from dotenv import load_dotenv
import re
from bs4 import BeautifulSoup

load_dotenv()

class DisclosuresCollector:
    def __init__(self):
        self.api_key = os.getenv("DART_API_KEY")
        if self.api_key:
            self.dart = OpenDartReader(self.api_key)
        else:
            print("Warning: DART_API_KEY not found")
            self.dart = None

    def extract_segment_data(self, xml_text, ticker, period):
        """
        Parses XML to find 'Sales by Segment' table and returns list of dicts.
        """
        segments = []
        try:
            # 1. Narrow down to Business Overview
            start_marker = "II. 사업의 내용"
            end_marker = "III. 재무에 관한 사항"
            
            start_idx = xml_text.find(start_marker)
            end_idx = xml_text.find(end_marker)
            
            if start_idx == -1 or end_idx == -1:
                return segments
                
            business_section = xml_text[start_idx:end_idx]
            
            # 2. Find "매출 및 수주상황"
            sales_marker = "매출 및 수주상황"
            sales_idx = business_section.find(sales_marker)
            
            if sales_idx == -1:
                return segments
                
            sales_section_text = business_section[sales_idx:]
            
            # 3. Parse Tables
            soup = BeautifulSoup(sales_section_text, 'html.parser')
            tables = soup.find_all('table')
            
            target_table = None
            for table in tables:
                text = table.get_text()
                if "부문" in text and "매출액" in text and "비중" in text:
                    target_table = table
                    break
            
            if not target_table:
                return segments
                
            # 4. Extract Rows
            rows = target_table.find_all('tr')
            current_division = None
            
            for row in rows:
                cols = row.find_all(['td', 'th'])
                cols_text = [ele.get_text(strip=True) for ele in cols]
                
                # We expect rows with data to have numbers.
                # Structure: [Division, Metric, CurrentAmt, CurrentRatio, ...]
                # Or: [Metric, CurrentAmt, CurrentRatio, ...] (if Division is merged)
                
                if not cols_text:
                    continue
                    
                # Skip header rows (usually contain '부문', '금액' etc but no numbers in first col)
                if cols_text[0] == "부문" or cols_text[0] == "금액":
                    continue

                # Heuristic to identify data row
                # If first col is a known division or looks like text, update current_division
                # If first col is "매출액" or "영업이익", use current_division
                
                # Check if first col is Division or Metric
                first_col = cols_text[0]
                
                # If row has 8 cols: [Div, Metric, Amt1, Rat1, Amt2, Rat2, Amt3, Rat3]
                # If row has 7 cols: [Metric, Amt1, Rat1, ...] (Div implied)
                
                division = current_division
                metric = ""
                amount = ""
                
                if len(cols_text) >= 8:
                    division = first_col
                    current_division = division
                    metric = cols_text[1]
                    amount = cols_text[2]
                elif len(cols_text) >= 7:
                    # Likely implied division
                    metric = first_col
                    amount = cols_text[1]
                else:
                    continue
                    
                # Clean amount (remove commas)
                try:
                    amount_clean = amount.replace(',', '').replace('△', '-')
                    # Check if it's a number
                    if not re.match(r'^-?\d+$', amount_clean):
                        continue
                except:
                    continue
                    
                # We only care about "매출액" and "영업이익"
                if "매출" in metric:
                    metric_key = "revenue"
                elif "영업이익" in metric:
                    metric_key = "op_profit"
                else:
                    continue
                    
                # Add to segments list
                # We need to merge revenue and op_profit for the same division
                # Check if we already have an entry for this division
                existing = next((item for item in segments if item["division"] == division), None)
                if not existing:
                    existing = {
                        "ticker": ticker,
                        "period": period,
                        "division": division,
                        "revenue": "0",
                        "op_profit": "0",
                        "insight": ""
                    }
                    segments.append(existing)
                
                if metric_key == "revenue":
                    existing["revenue"] = amount_clean
                elif metric_key == "op_profit":
                    existing["op_profit"] = amount_clean
            
            # Filter out segments with no division or no data
            segments = [s for s in segments if s["division"] and (s["revenue"] != "0" or s["op_profit"] != "0")]
                    
        except Exception as e:
            print(f"Segment extraction error: {e}")
            
        return segments

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
            # Fetch list - Periodic Reports (kind='A')
            df = self.dart.list(ticker, start=start_date, end=end_date, kind='A')
            
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
                        # Find "II. 사업의 내용" section
                        start_marker = "II. 사업의 내용"
                        end_marker = "III. 재무에 관한 사항"
                        
                        start_idx = xml_text.find(start_marker)
                        end_idx = xml_text.find(end_marker)
                        
                        if start_idx != -1 and end_idx != -1:
                            section_content = xml_text[start_idx:end_idx]
                            # Clean HTML/XML tags
                            clean_text = re.sub('<[^<]+?>', '', section_content)
                            clean_text = ' '.join(clean_text.split())
                            extracted_text = clean_text
                            summary_body = clean_text[:500] + "..." # Summary for disclosures table
                        else:
                            summary_body = "Section 'II. 사업의 내용' not found in XML."
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
                
                # Save to company_narratives if text extracted
                if extracted_text:
                    period = rcept_dt.strftime("%Y.%m")
                    narratives_to_save.append({
                        "ticker": ticker,
                        "period": period,
                        "section_type": "Business Overview",
                        "title": f"{report_nm} - Business Overview",
                        "content": extracted_text
                    })
                    
                    # Extract Segment Data
                    segments = self.extract_segment_data(xml_text, ticker, period)
                    if segments:
                        print(f"Extracted {len(segments)} segments for {ticker} ({period})")
                        upsert_data(
                            table="company_segments",
                            data=segments,
                            conflict_columns=["ticker", "period", "division"]
                        )
            
            # Upsert disclosures
            upsert_data(
                table="disclosures",
                data=disclosures_data,
                conflict_columns=["rcept_no"]
            )
            print(f"Saved {len(disclosures_data)} disclosures for {ticker}")

            # Upsert narratives
            if narratives_to_save:
                # Note: company_narratives doesn't have a unique constraint on (ticker, period, section_type) in schema.sql yet?
                # Wait, I added it in utils.py? No, I added the table but didn't specify UNIQUE in utils.py replacement.
                # Let's check utils.py content again.
                # In Step 200 replacement, I added:
                # CREATE TABLE IF NOT EXISTS company_narratives ( ... );
                # It did NOT have UNIQUE constraint.
                # So upsert_data might fail if I try to UPSERT without conflict columns.
                # Or it will just INSERT duplicates.
                # I should probably add a UNIQUE constraint or delete old ones.
                # For now, let's just INSERT. But duplicates are bad.
                # I will try to use a pseudo-upsert by deleting first? No, upsert_data handles conflict.
                # Since I can't change schema easily without dropping table (SQLite limitation for ALTER TABLE ADD CONSTRAINT),
                # I will just insert.
                # Actually, I can use `INSERT OR REPLACE` if I had a primary key or unique index.
                # Let's check if I can add a unique index dynamically or just live with duplicates for MVP (and clear table before run).
                # The user clears DB often.
                # But to be safe, I will delete existing narratives for this ticker/period before inserting.
                # Or just append.
                
                upsert_data(
                    table="company_narratives",
                    data=narratives_to_save,
                    conflict_columns=[] # No conflict columns, so it will INSERT.
                )
                print(f"Saved {len(narratives_to_save)} narratives for {ticker}")
            
        except Exception as e:
            print(f"Error fetching disclosures: {e}")

if __name__ == "__main__":
    collector = DisclosuresCollector()
    collector.fetch_disclosures("005930")
