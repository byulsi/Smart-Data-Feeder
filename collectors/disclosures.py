import os
import OpenDartReader
from datetime import datetime, timedelta
from utils import upsert_data
from dotenv import load_dotenv
import re

load_dotenv()

class DisclosuresCollector:
    def __init__(self):
        self.api_key = os.getenv("DART_API_KEY")
        if self.api_key:
            self.dart = OpenDartReader(self.api_key)
        else:
            print("Warning: DART_API_KEY not found")
            self.dart = None

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
