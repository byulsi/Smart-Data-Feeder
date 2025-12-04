import os
import OpenDartReader
import pandas as pd
import re
from datetime import datetime, timedelta
from utils import upsert_data
from dotenv import load_dotenv
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
                
                print(f"DEBUG: Loop start for {report_nm}")
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

            # 3. Extract R&D Expenses
            if xml_text:
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(xml_text, 'lxml')

                    rnd_expenses = self.extract_rnd_expenses(soup)
                    if rnd_expenses:
                        print(f"Extracted R&D Expenses: {rnd_expenses:,}")
                        
                        # Parse period from report name usually "(YYYY.MM)"
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
                            print(f"Updated R&D expenses for {ticker} ({year} Q{quarter})")
                except Exception as e:
                    print(f"Error extracting R&D: {e}")

            # 4. Save Narratives
            # Upsert narratives
            if narratives_to_save:
                # Let's check if I can add a unique index dynamically or just live with duplicates for MVP (and clear table before run).
                # The user clears DB often.
                # But to be safe, I will delete existing narratives for this ticker/period before inserting.
                # Or just append.
                
                upsert_data(
                    table="company_narratives",
                    data=narratives_to_save,
                    conflict_columns=["ticker", "period", "section_type"]
                )
                print(f"Saved {len(narratives_to_save)} narratives for {ticker}")
            
        except Exception as e:
            print(f"Error fetching disclosures: {e}")

    def extract_rnd_expenses(self, soup):
        """
        Extracts Total R&D Expenses from the report XML.
        Returns the amount in KRW (assuming unit is Million KRW if detected, or raw).
        """
        tables = soup.find_all('table')
        for table in tables:
            text = table.get_text()
            if "연구개발비" in text and ("계" in text or "합계" in text):
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    cols_text = [ele.get_text(strip=True) for ele in cols]
                    
                    if not cols_text:
                        continue
                        
                    # Check for Total row
                    if "연구개발비용 총계" in cols_text[0] or "연구개발비용 계" in cols_text[0] or ("연구개발비" in cols_text[0] and "계" in cols_text[0]):
                        # Extract first value column
                        if len(cols_text) > 1:
                            val_str = cols_text[1]
                            # Clean
                            val_str = val_str.replace(',', '').replace('△', '-')
                            try:
                                val = int(val_str)
                                # Check unit. Usually Million KRW.
                                unit_mult = 1
                                if "(단위 : 백만원)" in text or "(단위: 백만원)" in text or "(단위:백만원)" in text:
                                    unit_mult = 1_000_000
                                elif "(단위 : 원)" in text:
                                    unit_mult = 1
                                else:
                                    # Heuristic: if value < 100,000,000,000 (100 Billion), it's likely Million or Thousand.
                                    if val > 0 and val < 1_000_000_000_000: # Less than 1 Trillion raw
                                        unit_mult = 1_000_000
                                
                                return val * unit_mult
                            except:
                                pass
        return None

if __name__ == "__main__":
    collector = DisclosuresCollector()
    collector.fetch_disclosures("005930")
